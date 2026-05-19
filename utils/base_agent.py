import os
import json
import re
import asyncio
import httpx
import google.generativeai as genai
import config
from utils.logger import Logger

import google.generativeai.client as genai_client
import random

# Build isolated _ClientManager instances for all configured keys to enable thread-safe dynamic key rotation
_client_managers = []
if hasattr(config, "GEMINI_API_KEYS") and config.GEMINI_API_KEYS:
    for key in config.GEMINI_API_KEYS:
        try:
            manager = genai_client._ClientManager()
            manager.configure(api_key=key)
            _client_managers.append((key, manager))
        except Exception as e:
            Logger.error(f"Failed to configure manager for key {key[:8]}...: {str(e)}")
else:
    # Fallback to single GEMINI_API_KEY if GEMINI_API_KEYS is not populated
    if config.GEMINI_API_KEY:
        try:
            manager = genai_client._ClientManager()
            manager.configure(api_key=config.GEMINI_API_KEY)
            _client_managers.append((config.GEMINI_API_KEY, manager))
        except Exception as e:
            Logger.error(f"Failed to configure default key manager: {str(e)}")

# Global state for key rotation and rate-limiting
_current_key_index = 0
_key_lock = asyncio.Lock()
_gemini_api_lock = asyncio.Lock()

# Also perform global default configuration for backwards compatibility / other parts of the SDK
if config.GEMINI_API_KEY:
    try:
        genai.configure(api_key=config.GEMINI_API_KEY)
    except Exception as e:
        Logger.error(f"Failed to set global default Gemini configuration: {str(e)}")

async def search_query(query: str) -> list:
    """
    Search the web using Tavily as primary, falling back to Serper if Tavily fails/not configured.
    """
    # 1. Tavily Search (Primary)
    if config.TAVILY_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                Logger.debug(f"Tavily searching: '{query}'")
                response = await client.post(
                    "https://api.tavily.com/search",
                    json={
                        "api_key": config.TAVILY_API_KEY,
                        "query": query,
                        "search_depth": "basic",
                        "max_results": 10
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    results = []
                    for r in data.get("results", []):
                        results.append({
                            "title": r.get("title", ""),
                            "url": r.get("url", ""),
                            "content": r.get("content", ""),
                            "query": query
                        })
                    return results
                else:
                    Logger.warning(f"Tavily returned code {response.status_code} for: '{query}'")
        except Exception as e:
            Logger.warning(f"Tavily search failed for: '{query}'. Error: {str(e)}")

    # 2. Serper Search (Fallback)
    if config.SERPER_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                Logger.debug(f"Serper searching (Fallback): '{query}'")
                response = await client.post(
                    "https://google.serper.dev/search",
                    headers={
                        "X-API-KEY": config.SERPER_API_KEY,
                        "Content-Type": "application/json"
                    },
                    json={
                        "q": query,
                        "num": 10
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    results = []
                    for r in data.get("organic", []):
                        results.append({
                            "title": r.get("title", ""),
                            "url": r.get("link", ""),
                            "content": r.get("snippet", ""),
                            "query": query
                        })
                    return results
                else:
                    Logger.warning(f"Serper returned code {response.status_code} for: '{query}'")
        except Exception as e:
            Logger.error(f"Serper search failed for: '{query}'. Error: {str(e)}")

    Logger.warning(f"No search API available or both failed for query: '{query}'")
    return []

async def run_searches_in_batches(queries: list) -> list:
    """
    Runs search queries in parallel batches of 3, with 0.5s sleep in between.
    """
    all_results = []
    for i in range(0, len(queries), 3):
        batch = queries[i:i+3]
        Logger.info(f"Searching batch: {batch}")
        tasks = [search_query(q) for q in batch]
        
        # Gather with return_exceptions to ensure one failure doesn't crash the whole batch
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for res in batch_results:
            if isinstance(res, list):
                all_results.extend(res)
            elif isinstance(res, Exception):
                Logger.error(f"Search task raised exception: {str(res)}")
        
        # Rate limit spacing
        if i + 3 < len(queries):
            await asyncio.sleep(0.5)
            
    return all_results

async def call_gemini_extraction(system_prompt: str, user_prompt: str) -> list:
    """
    Calls Groq (Llama-3.3-70b-versatile) as the primary engine for lightning-fast, high-accuracy extraction.
    Falls back to keyless GPT-4o on Pollinations if Groq is unavailable, rate-limited, or has no key configured.
    """
    max_retries = 5
    
    for attempt in range(max_retries):
        try:
            if config.GROQ_API_KEY:
                Logger.info(
                    f"[GROQ] Querying Llama-3.3-70b-versatile... (Attempt {attempt+1}/{max_retries})"
                )
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {config.GROQ_API_KEY}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "messages": [
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_prompt}
                            ],
                            "model": config.GROQ_MODEL,
                            "temperature": 0.1
                        },
                        timeout=30.0
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        text = data["choices"][0]["message"]["content"].strip()
                        
                        # Clean markdown wrappers (e.g. ```json ... ``` or ``` ...)
                        text = re.sub(r"^```[a-zA-Z0-9]*\n", "", text)
                        text = re.sub(r"\n```$", "", text)
                        text = text.strip()
                        
                        try:
                            parsed_data = json.loads(text)
                            if isinstance(parsed_data, list):
                                return parsed_data
                            elif isinstance(parsed_data, dict):
                                for val in parsed_data.values():
                                    if isinstance(val, list):
                                        return val
                                return [parsed_data]
                        except json.JSONDecodeError:
                            Logger.warning("Failed to decode JSON response from Groq. Retrying...")
                    elif response.status_code == 429:
                        Logger.warning(f"Groq API rate-limited (429). Falling back to keyless engine on this attempt...")
                        # Fall through to Pollinations keyless GPT-4o within the same attempt to keep speed high!
                        raise Exception("Groq 429")
                    else:
                        Logger.warning(f"Groq API returned status code {response.status_code}. Retrying...")
            
            # Fallback/Direct: Query Keyless Pollinations GPT-4o engine
            if not config.GROQ_API_KEY or attempt > 0:
                engine_name = "keyless GPT-4o fallback" if config.GROQ_API_KEY else "keyless GPT-4o"
                Logger.info(
                    f"[FREE-ENGINE] Querying {engine_name}... (Attempt {attempt+1}/{max_retries})"
                )
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "https://text.pollinations.ai/",
                        json={
                            "messages": [
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_prompt}
                            ],
                            "model": "openai"
                        },
                        timeout=60.0
                    )
                    
                    if response.status_code == 200:
                        text = response.text.strip()
                        
                        # Clean markdown wrappers
                        text = re.sub(r"^```[a-zA-Z0-9]*\n", "", text)
                        text = re.sub(r"\n```$", "", text)
                        text = text.strip()
                        
                        try:
                            parsed_data = json.loads(text)
                            if isinstance(parsed_data, list):
                                return parsed_data
                            elif isinstance(parsed_data, dict):
                                for val in parsed_data.values():
                                    if isinstance(val, list):
                                        return val
                                return [parsed_data]
                        except json.JSONDecodeError:
                            Logger.warning("Failed to decode JSON response from free GPT-4o. Retrying...")
                    else:
                        Logger.warning(f"Free GPT-4o returned status code {response.status_code}. Retrying...")
                        
        except Exception as e:
            # Handle Groq rate-limiting failover to keyless engine on the first attempt
            if "Groq 429" in str(e) or (config.GROQ_API_KEY and attempt == 0):
                Logger.warning("[FAILOVER] Groq error. Instantly switching to keyless GPT-4o fallback...")
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            "https://text.pollinations.ai/",
                            json={
                                "messages": [
                                    {"role": "system", "content": system_prompt},
                                    {"role": "user", "content": user_prompt}
                                ],
                                "model": "openai"
                            },
                            timeout=60.0
                        )
                        if response.status_code == 200:
                            text = response.text.strip()
                            text = re.sub(r"^```[a-zA-Z0-9]*\n", "", text)
                            text = re.sub(r"\n```$", "", text)
                            text = text.strip()
                            try:
                                parsed_data = json.loads(text)
                                if isinstance(parsed_data, list):
                                    return parsed_data
                                elif isinstance(parsed_data, dict):
                                    for val in parsed_data.values():
                                        if isinstance(val, list):
                                            return val
                                    return [parsed_data]
                            except json.JSONDecodeError:
                                pass
                except Exception as fe:
                    Logger.error(f"Fallback engine error: {str(fe)}")
            else:
                Logger.error(f"Extraction error: {str(e)}")
            
        # Smart jittered sleep to prevent concurrent agents from colliding on retries
        sleep_time = random.uniform(3.0, 7.0)
        await asyncio.sleep(sleep_time)
        
    return []

def deduplicate_results(opportunities: list) -> list:
    """
    Deduplicates opportunity dicts based on cleaned URL and slugified title.
    """
    seen_urls = set()
    seen_titles = set()
    unique_opps = []
    
    for opp in opportunities:
        url = opp.get("url", "").strip().lower()
        if "?" in url:
            url = url.split("?")[0]
        url = url.rstrip("/")
        
        title = opp.get("title", "").strip().lower()
        title_slug = "".join(c for c in title if c.isalnum())
        
        # If no URL, fall back to title slug deduplication only
        if not url:
            if title_slug and title_slug not in seen_titles:
                seen_titles.add(title_slug)
                unique_opps.append(opp)
            continue
            
        if url not in seen_urls:
            if not title_slug or title_slug not in seen_titles:
                seen_urls.add(url)
                if title_slug:
                    seen_titles.add(title_slug)
                unique_opps.append(opp)
            else:
                Logger.debug(f"Skipping duplicate title slug '{title_slug}' for url: {opp.get('url')}")
        else:
            Logger.debug(f"Skipping duplicate URL: {opp.get('url')}")
            
    return unique_opps

async def process_agent_opportunities(
    search_queries: list, 
    system_prompt: str, 
    agent_name: str
) -> list:
    """
    Common workflow for all agents:
    1. Runs all search queries in batches.
    2. Deduplicates raw search results by URL first.
    3. Chunks search results (max 15 at a time).
    4. Sends each chunk to Gemini for filtering & extraction.
    5. Aggregates and deduplicates final structured opportunities.
    """
    Logger.info(f"[{agent_name}] Starting search queries...")
    raw_results = await run_searches_in_batches(search_queries)
    
    if not raw_results:
        Logger.warning(f"[{agent_name}] No search results found across all queries.")
        return []
        
    # Pre-deduplicate raw results to fit within 15 and remove early noise
    deduped_raw = []
    seen_raw_urls = set()
    for item in raw_results:
        url = item.get("url", "").strip().lower().split("?")[0].rstrip("/")
        if url and url not in seen_raw_urls:
            seen_raw_urls.add(url)
            deduped_raw.append(item)
            
    Logger.info(f"[{agent_name}] Found {len(raw_results)} raw search hits ({len(deduped_raw)} unique URLs).")
    
    # Process in chunks of 15 for Gemini
    all_extracted_opportunities = []
    chunk_size = 15
    for i in range(0, len(deduped_raw), chunk_size):
        chunk = deduped_raw[i:i+chunk_size]
        Logger.info(f"[{agent_name}] Sending chunk {i//chunk_size + 1} of {(len(deduped_raw)-1)//chunk_size + 1} (size: {len(chunk)}) to Gemini...")
        
        # Structure search data for Gemini
        chunk_data = []
        for idx, item in enumerate(chunk):
            chunk_data.append({
                "index": idx,
                "title": item.get("title"),
                "url": item.get("url"),
                "snippet": item.get("content"),
                "search_query": item.get("query")
            })
            
        user_prompt = f"Here is the batch of search results to evaluate and extract opportunities from:\n\n{json.dumps(chunk_data, indent=2)}"
        
        extracted = await call_gemini_extraction(system_prompt, user_prompt)
        if extracted:
            Logger.success(f"[{agent_name}] Extracted {len(extracted)} opportunities from chunk.")
            all_extracted_opportunities.extend(extracted)
        else:
            Logger.warning(f"[{agent_name}] No opportunities extracted from this chunk.")
            
    # Deduplicate final structured results
    final_opportunities = deduplicate_results(all_extracted_opportunities)
    Logger.success(f"[{agent_name}] Finished! Extracted {len(final_opportunities)} unique active opportunities.")
    return final_opportunities
