import os
import sys
import time
import asyncio
from dotenv import load_dotenv

# Add the project directory to python path to ensure imports work correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config
from utils.logger import Logger
from utils.excel_writer import write_opportunities_to_excel
from agents.sponsored import run_sponsored_agent
from agents.ugc import run_ugc_agent
from agents.speaker_hackathon import run_speaker_hackathon_agent

async def safe_run_agent(agent_fn, agent_name: str) -> list:
    """
    Runs an agent function safely catching any exceptions to prevent halting other agents.
    """
    Logger.info(f"Launching {agent_name}...")
    start_time = time.time()
    try:
        results = await agent_fn()
        elapsed = time.time() - start_time
        Logger.success(f"{agent_name} completed in {elapsed:.2f}s. Found {len(results)} opportunities.")
        return results
    except Exception as e:
        elapsed = time.time() - start_time
        Logger.error(f"Error in {agent_name} after {elapsed:.2f}s: {str(e)}")
        return []

async def main_async():
    Logger.info("=" * 60)
    Logger.info("          STARTING OPPORTUNITY HUNTER AI AGENT          ")
    Logger.info("=" * 60)
    
    # 1. API Keys Validation
    missing_keys = []
    if not config.TAVILY_API_KEY and not config.SERPER_API_KEY:
        missing_keys.append("TAVILY_API_KEY or SERPER_API_KEY (at least one is required)")
        
    if missing_keys:
        Logger.error("CRITICAL ERROR: Missing configuration keys!")
        for key in missing_keys:
            Logger.error(f" - Please configure '{key}' in your .env file.")
        Logger.warning("Please edit the '.env' file inside the 'opportunity-agent' directory, add your API keys, and run again.")
        sys.exit(1)
        
    Logger.info(f"Target Profile: {config.USER_PROFILE['name']} | Location: {config.USER_PROFILE['location']}")
    Logger.info(f"Interests Biased: {', '.join(config.USER_PROFILE['interests'])}")
    Logger.info("Using 100% free, unlimited keyless GPT-4o engine.")
    Logger.info("Initiating search & extraction agents in parallel...")
    
    start_time = time.time()
    
    # 2. Run all three agents concurrently using safe wrapper
    sponsored_task = safe_run_agent(run_sponsored_agent, "Sponsored Trips Agent")
    ugc_task = safe_run_agent(run_ugc_agent, "UGC Brand Deals Agent")
    speaker_hackathon_task = safe_run_agent(run_speaker_hackathon_agent, "Speaker & Hackathon Agent")
    
    results = await asyncio.gather(sponsored_task, ugc_task, speaker_hackathon_task)
    
    sponsored_trips, ugc_deals, speaker_hackathons = results
    
    total_found = len(sponsored_trips) + len(ugc_deals) + len(speaker_hackathons)
    Logger.info("-" * 60)
    Logger.success(f"All agents completed execution. Total unique opportunities extracted: {total_found}")
    
    # 3. Write results to Excel
    Logger.info("Generating beautiful styled Excel workbook...")
    try:
        excel_path = write_opportunities_to_excel(
            sponsored_trips=sponsored_trips,
            ugc_deals=ugc_deals,
            speaker_hackathons=speaker_hackathons,
            output_dir="output"
        )
        Logger.success("=" * 60)
        Logger.success(f"SUCCESS: Excel output generated at:")
        Logger.success(f" -> {excel_path}")
        Logger.success("=" * 60)
    except Exception as e:
        Logger.error(f"Failed to generate Excel sheet: {str(e)}")
        Logger.error("Dumping results to JSON files instead as fallback...")
        try:
            import json
            fallback_path = "output/fallback_opportunities.json"
            os.makedirs("output", exist_ok=True)
            with open(fallback_path, "w", encoding="utf-8") as f:
                json.dump({
                    "sponsored_trips": sponsored_trips,
                    "ugc_deals": ugc_deals,
                    "speaker_hackathons": speaker_hackathons
                }, f, indent=2)
            Logger.success(f"Successfully dumped opportunities to backup JSON: {fallback_path}")
        except Exception as je:
            Logger.error(f"Fallback JSON dump failed: {str(je)}")
            
    total_elapsed = time.time() - start_time
    Logger.info(f"Total time elapsed: {total_elapsed:.2f} seconds.")

def main():
    # Setup for Windows loop policy to avoid issues with subprocesses or socket limits
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
