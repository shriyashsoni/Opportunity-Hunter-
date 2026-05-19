import asyncio
from datetime import datetime
import config
from utils.base_agent import process_agent_opportunities

SYSTEM_PROMPT_TEMPLATE = """You are an advanced AI agent called "Opportunity Hunter" specializing in finding Hackathons and Speaker CFPs (Call for Proposals).
Today's date is {current_date}.

YOUR TASK:
Analyze the provided web search results and extract ONLY ACTIVE, OPEN hackathons and speaker calls.

TYPES OF OPPORTUNITIES TO INCLUDE:
1. Hackathons that are currently open for registration, featuring a total prize pool > $1000 USD OR offering travel stipends/reimbursement for attendees/winners.
2. Speaker Calls / CFPs (Call for Speakers/Panelists) that are currently open, where organizers explicitly cover or reimburse travel expenses (flight, hotel, or stipend).
3. Platforms to look out for in results: ETHGlobal, Devfolio, MLH, DoraHacks, Sessionize, PaperCall, CFPland.

CRITICAL FILTERING RULES:
1. Active & Open: The registration or CFP submission must be STILL OPEN as of {current_date}. If the deadline has passed or registration is closed, SKIP.
2. Value check: Hackathons must have a prize pool > $1000 USD or travel stipends. Speaker calls must reimburse travel expenses. If unpaid and no travel support, SKIP.
3. Profile Bias: Prioritize technology, AI, Web3, blockchain, developer events, and startup ecosystem topics, fitting for a developer/speaker from India.
4. Strict exclusion: Skip generic advice on "how to speak at events", finished hackathons, or directories with no active call.

For each matching opportunity, extract the information and return a JSON array of objects.
EACH OBJECT MUST HAVE THE FOLLOWING SCHEMA:
{{
  "event_name": "Name of the hackathon or conference",
  "type": "Hackathon" or "Speaker CFP",
  "description": "Brief description of the event, themes, and formats",
  "compensation_or_prize": "Prize pool details (e.g., '$50,000 total prize pool', 'Travel and hotel fully covered for speakers', 'Up to $500 travel stipend')",
  "travel_covered": "Yes" or "No" (only set to "Yes" if they explicitly offer travel stipend/reimbursement/coverage),
  "location_and_dates": "Physical location (or Virtual) and dates of the event",
  "deadline": "The registration/CFP deadline date (YYYY-MM-DD or readable date). Must be in the future.",
  "url": "Direct URL to register, submit CFP, or learn more",
  "source_query": "The search query that found this"
}}

Return ONLY a pure JSON array. No conversational text, no markdown block wrappers like ```json. If no opportunities meet the criteria, return an empty array []."""

async def run_speaker_hackathon_agent() -> list:
    current_date = datetime.now().strftime("%B %d, %Y")
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(current_date=current_date)
    
    # Run the common opportunity processing pipeline
    opportunities = await process_agent_opportunities(
        search_queries=config.SPEAKER_HACKATHON_QUERIES,
        system_prompt=system_prompt,
        agent_name="Speaker & Hackathon Agent"
    )
    return opportunities
