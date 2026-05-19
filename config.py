import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"

# Support multiple Gemini API keys for rotation/failover
GEMINI_API_KEYS = []
if GEMINI_API_KEY:
    # Support comma-separated keys in GEMINI_API_KEY
    GEMINI_API_KEYS = [k.strip() for k in GEMINI_API_KEY.split(",") if k.strip()]

# Support numbered keys GEMINI_API_KEY_1, GEMINI_API_KEY_2, etc.
i = 1
while True:
    key = os.getenv(f"GEMINI_API_KEY_{i}")
    if not key:
        # Also check without underscore in case of GEMINI_API_KEY1
        key = os.getenv(f"GEMINI_API_KEY{i}")
        if not key:
            break
    key_stripped = key.strip()
    if key_stripped and key_stripped not in GEMINI_API_KEYS:
        GEMINI_API_KEYS.append(key_stripped)
    i += 1

# If no keys were found but GEMINI_API_KEY is present, populate it.
# If GEMINI_API_KEYS has keys but GEMINI_API_KEY is not set, set it to the first active key for backwards compatibility.
if GEMINI_API_KEYS and not GEMINI_API_KEY:
    GEMINI_API_KEY = GEMINI_API_KEYS[0]
elif GEMINI_API_KEY and not GEMINI_API_KEYS:
    GEMINI_API_KEYS = [GEMINI_API_KEY]

# Gemini settings
GEMINI_MODEL = "gemini-2.5-flash"  # Highly accurate and fast Flash model available in 2026

# User Profile to personalize and bias searches
USER_PROFILE = {
    "name": "Shriyash Soni",
    "skills": ["Web3", "Blockchain", "Full-Stack Dev", "AI", "EdTech", "Content Creation"],
    "location": "India",
    "role": "Entrepreneur, Developer, Speaker, Builder",
    "social": "@shriyashsoni",
    "interests": ["tech", "AI", "Web3", "blockchain", "developer events", "startup ecosystem"]
}

# 20 targeted search queries for Sheet 1: Sponsored Trips
SPONSORED_TRIPS_QUERIES = [
    "fully funded travel grant web3 blockchain developer 2026",
    "fully covered flight accommodation volunteer program 2026",
    "tech conference travel grant speaker developer 2026",
    "youth delegate slot fully funded flight accommodation 2026",
    "content creator press trip fully covered travel 2026",
    "brand ambassador program fully funded travel 2026",
    "global fellowship travel grant fully covered 2026",
    "community moderator sponsored trip travel 2026",
    "developer advocate ambassador travel grant 2026",
    "academic fellowship fully covered travel flight 2026",
    "fully funded international conference delegate 2026",
    "climate youth summit fully funded travel 2026",
    "one young world delegate scholarship fully funded 2026",
    "hacker travel stipend fully covered blockchain 2026",
    "tech summit travel sponsorship flight hotel 2026",
    "startup founder retreat sponsored travel visa 2026",
    "open call travel grant community leaders 2026",
    "emerging leaders program fully funded international travel 2026",
    "underrepresented founders travel grant conference 2026",
    "cultural exchange program fully covered travel flight stay 2026"
]

# 20 targeted search queries for Sheet 2: UGC Brand Deals
UGC_BRAND_DEALS_QUERIES = [
    "paid UGC creator campaigns tech brands software",
    "paid brand ambassador program web3 blockchain startup",
    "AI startup paid creator collaboration video reel",
    "paid brand deals tech content creators reels",
    "UGC campaigns paid free product tech gadgets",
    "paid creator collab developer tools software brand",
    "Insense Trend.io paid campaigns tech creators",
    "Billo paid UGC video campaigns tech",
    "EdTech brand sponsor paid content creator",
    "paid brand ambassador developer program 2026",
    "sponsored video integration tech review youtube paid",
    "software as a service affiliate program paid sponsor video",
    "web3 marketing campaign paid content creator promotion",
    "AI tool tiktok promotion paid campaign influencer",
    "tech gadgets product placement paid sponsorship reels",
    "dev tool startup paid micro influencer sponsorship",
    "digital product review sponsor paid collaboration",
    "coding channel paid sponsorship brand deals 2026",
    "software developer paid partnership instagram tiktok",
    "app launch paid campaign video creators needed"
]

# 20 targeted search queries for Sheet 3: Speaker Calls & Hackathons
SPEAKER_HACKATHON_QUERIES = [
    "ETHGlobal hackathon open registration travel stipend 2026",
    "Devfolio open hackathons blockchain prize pool 2026",
    "DoraHacks open hackathons Web3 prize pool 2026",
    "MLH open hackathons developer registration 2026",
    "Sessionize CFP open speaker travel reimbursed 2026",
    "PaperCall open CFP travel stipend tech 2026",
    "CFPland open call for speakers travel covered 2026",
    "open Web3 developer conference CFP travel support 2026",
    "AI developer hackathon open registration prize pool 2026",
    "blockchain conference open call for speakers travel reimbursed 2026",
    "international developer summit call for proposals speakers 2026",
    "web3 conference speaker submit CFP flight hotel covered",
    "major tech conference open CFP global speaker flight reimbursement",
    "linux foundation open speaking CFP travel support 2026",
    "rust web3 golang conference speaker travel grant 2026",
    "solana ethereum multichain hackathon open application 2026",
    "hackathon with travel reimbursement travel grant 2026",
    "artificial intelligence builder hackathon register now 2026",
    "pycon open talk proposals speaker travel grant 2026",
    "tech conference call for presentations travel expense covered 2026"
]
