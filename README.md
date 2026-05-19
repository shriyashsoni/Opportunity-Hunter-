# 🎯 Opportunity Hunter — Local Python AI Agent

An autonomous, concurrent multi-agent system that intelligently crawls the web, extracts high-quality opportunities (Fully Funded Trips, UGC Brand Deals, Speaker CFPs & Hackathons) tailored to your personal developer profile, and compiles them into a premium-styled Excel spreadsheet with a summary metrics dashboard.

---

## 🏗️ Architecture & Project Structure

The project has been initialized with the following structure:

```text
opportunity-agent/
├── main.py                     # Entry Point: Orchestrates parallel multi-agent executions
├── config.py                   # Configuration: Profile customization, targeted queries, model configurations
├── requirements.txt            # Python Dependencies
├── .gitignore                  # Git Ignores (hides environment keys & Excel outputs)
├── .env.example                # Environment configuration template for API credentials
├── run_agent.bat               # Windows automation launcher (one-click start)
├── run_agent.sh                # macOS / Linux automation launcher (with venv auto-setup)
├── agents/
│   ├── sponsored.py            # Sponsored Trips Agent prompt & execution
│   ├── ugc.py                  # UGC Brand Deals Agent prompt & execution
│   └── speaker_hackathon.py    # Hackathons & Speaker CFPs Agent prompt & execution
├── utils/
│   ├── base_agent.py           # Core: Parallel Tavily/Serper search, LLM extraction pipeline, deduplication
│   ├── excel_writer.py         # Premium OpenPyXL Excel spreadsheet template generator
│   └── logger.py               # Colorized, timestamped command-line logging
└── output/                     # Auto-created directory where generated Excel reports are saved
```

---

## 🚀 Key Features

* **Parallel Search Execution**: Employs Python `asyncio` to search up to **30+ highly-targeted queries** concurrently in batched throttles of 3 to prevent network choke and API rate limits.
* **Dual-Layer Search Architecture**: Features primary search using **Tavily AI** (the industry standard search built specifically for agents) with an automatic failover to **Serper.dev** (Google Search API) if limits are reached.
* **No-Config Out-of-the-Box LLM Extraction**: Out-of-the-box support for **Pollinations AI's keyless GPT-4o** engine (100% free and unlimited). You can also configure **Groq (Llama-3.3-70b-versatile)** or **Google Gemini API** for high-speed, enterprise-grade extraction.
* **Token-Aware Chunked Processing**: Automates the packaging of raw search snippets into small chunks (max 15 items) to prevent token overflow on LLM context windows.
* **Clean Data Extraction**: Programmatically filters out expired deadlines, general travel blogs, and exposure-only deals using dynamic system constraints.
* **Rigorous Post-Deduplication**: Filters duplicate results via a two-way validation pipeline:
  1. Normalized URL matching (stripping UTM coordinates and parameters).
  2. Slugified Title matching (stripping casing and whitespaces to identify duplicate listings with minor title variants).
* **Premium-Styled Excel Output**: Automatically generates highly customized spreadsheets containing:
  * **Summary Dashboard**: Interactive metrics summary, category counts, and high-value highlights.
  * **Top Picks**: Featured high-value rows with direct clickable links.
  * **Data Sheets**: Dedicated tabs for Sponsored Trips, UGC Deals, and CFPs.
  * **Theme**: Modern Deep Slate / Steel Blue (`#1F385C`) aesthetics, auto-fitting column widths, freeze-panes, alternating row fills (`#F4F7FA`), and Soft Sage Green (`#E2F0D9`) row highlights for travel-covered items.

---

## 🔑 A-to-Z API Setup Guide

To perform its autonomous sweeps, the agent leverages specialized search and extraction APIs. Below is a comprehensive breakdown of the APIs required, their functions, free tiers, and links to get keys.

### Search APIs (At least one is REQUIRED)

| API Provider | Purpose | Free Tier Allowance | Key Link | Required / Optional |
| :--- | :--- | :--- | :--- | :--- |
| **Tavily AI** | **Primary Search**: Highly optimized search engine engineered specifically for AI agents. Delivers structured developer and event snippets. | **1,000 Free Searches** / month | [Get Tavily Key](https://tavily.com) | **Required** (Highly Recommended) |
| **Serper.dev** | **Fallback Backup**: Google Search API wrapper. Acts as an automatic fallback if Tavily's limits are exceeded. | **2,500 Free Queries** upon signup | [Get Serper Key](https://serper.dev) | **Optional** (Recommended for redundancy) |

### LLM & Extraction APIs (Optional)

| API Provider | Purpose | Free Tier Allowance | Key Link | Required / Optional |
| :--- | :--- | :--- | :--- | :--- |
| **Groq API** | **Primary Extraction Engine**: Extremely high-speed, structured JSON generation utilizing `llama-3.3-70b-versatile`. | Generous free developer rate-limits | [Get Groq Key](https://console.groq.com) | **Optional** (Highly Recommended for speed) |
| **Google Gemini API** | **Backup Extraction Engine**: Powerful failover engine with native JSON mode capability. | **1,500 Queries** / day (Free tier) | [Get Gemini Key](https://aistudio.google.com/apikey) | **Optional** (Configured for failover) |
| **Pollinations AI** | **Zero-Config Default Engine**: Keyless, unlimited free GPT-4o engine. **Used automatically if no Groq/Gemini key is configured!** | 100% Free / Unlimited | None (Works out of the box) | **Fallback** (Requires no configuration) |

---

## ⚙️ Installation & Configuration

Follow these step-by-step instructions to install and configure the Opportunity Hunter on your system.

### Step 1: System Prerequisites
Ensure you have **Python 3.9** or higher installed on your system.
* Check your version by running:
  ```bash
  python --version  # or python3 --version
  ```
* If Python is not installed, download it from the [Official Python Website](https://python.org). Make sure to check the box **"Add Python to PATH"** during installation.

### Step 2: Clone or Download the Repository
If you downloaded this project as a zip, extract it. If cloning via Git:
```bash
git clone https://github.com/yourusername/opportunity-agent.git
cd opportunity-agent
```

### Step 3: Configure Environment Variables
1. Find the `.env.example` file in the root directory.
2. Duplicate or copy the file, renaming the duplicate to `.env`:
   ```bash
   # On macOS / Linux
   cp .env.example .env

   # On Windows (Command Prompt)
   copy .env.example .env

   # On Windows (PowerShell)
   Copy-Item .env.example .env
   ```
3. Open the newly created `.env` file in your favorite text editor (VS Code, Notepad, etc.) and paste your API keys:
   ```env
   # Add your Groq API Key (Highly Recommended)
   GROQ_API_KEY=gsk_your_groq_key_here

   # Add your Gemini API Key (Optional)
   GEMINI_API_KEY=AIzaSy_your_gemini_key_here

   # Add your Tavily API Key (Primary Search - Highly Recommended)
   TAVILY_API_KEY=tvly-your_tavily_key_here

   # Add your Serper API Key (Fallback Search)
   SERPER_API_KEY=your_serper_key_here
   ```

> [!TIP]
> **Zero-Config Run**: If you do not have Groq or Gemini API keys yet, you can leave those fields blank in your `.env`. The agent will automatically fallback to the integrated **Pollinations GPT-4o** engine, requiring only a search key (`TAVILY_API_KEY` or `SERPER_API_KEY`) to run successfully!

### Step 4: Set up Virtual Environment & Install Dependencies
Setting up a virtual environment isolates the agent's dependencies from your global system.

#### On Windows (PowerShell / CMD)
```powershell
# 1. Create a virtual environment inside .venv
python -m venv .venv

# 2. Activate the virtual environment
.venv\Scripts\activate

# 3. Install required libraries
pip install --upgrade pip
pip install -r requirements.txt
```

#### On macOS / Linux (Terminal)
```bash
# 1. Create a virtual environment inside .venv
python3 -m venv .venv

# 2. Activate the virtual environment
source .venv/bin/activate

# 3. Install required libraries
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🎨 Profile Personalization

The agent doesn't just search generic terms; it biases all queries, prompts, and search filters toward **your specific profile**.

### Customize `config.py`
Open `config.py` in your text editor. Locate the `USER_PROFILE` dictionary at line 45:

```python
USER_PROFILE = {
    "name": "Your Name",
    "skills": ["Web3", "Blockchain", "Full-Stack Dev", "AI", "EdTech", "Content Creation"],
    "location": "India",
    "role": "Entrepreneur, Developer, Speaker, Builder",
    "social": "@yourhandle",
    "interests": ["tech", "AI", "Web3", "blockchain", "developer events", "startup ecosystem"]
}
```

* **Customize this profile** with your own skills, location, name, and interests! All sub-agents will dynamically inject this background into search terms and LLM evaluation criteria.
* If you want to customize search targets, you can also modify the **queries lists** (`SPONSORED_TRIPS_QUERIES`, `UGC_BRAND_DEALS_QUERIES`, and `SPEAKER_HACKATHON_QUERIES`) directly below the profile block.

---

## 🚀 How to Start the Agent

You can start the agent's parallel sweep using the automated platform launchers or the command line.

### Method A: Automated Platform Launchers (Recommended)
We have included automated one-click launcher scripts that handle launching the process cleanly:

* **Windows**: Double-click the `run_agent.bat` file in your explorer window, or run:
  ```cmd
  run_agent.bat
  ```
* **macOS / Linux**: Open your terminal, grant execution permissions, and run the automated bash script (it will automatically detect or set up a virtual environment `.venv` and install dependencies for you!):
  ```bash
  chmod +x run_agent.sh
  ./run_agent.sh
  ```

### Method B: Manual Command Line
If your virtual environment is active, simply run the Python entry orchestrator:
```bash
python main.py
```

---

## 📊 Understanding the Output

Once the agent completes its sweep, it automatically outputs highly-styled spreadsheets in the `output/` folder, structured as `opportunities_YYYYMMDD_HHMM.xlsx`.

```text
output/
├── opportunities_20260519_1400.xlsx        # Master Workbook (Contains Dashboard + 3 Tabs)
├── sponsored_trips_20260519_1400.xlsx      # Isolated Excel file for Sponsored Trips
├── ugc_brand_deals_20260519_1400.xlsx      # Isolated Excel file for UGC Brand Deals
└── speaker_hackathons_20260519_1400.xlsx   # Isolated Excel file for Speaker Calls & Hackathons
```

### Visual Indicators & Formatting Rules
1. **Summary Dashboard**: Provides metric scorecards detailing the total number of items identified in each category, followed by a curated **Top Picks** section.
2. **Interactive Filters**: Multi-column sorting is turned on by default in all sheets, enabling you to sort by deadlines or hosting brands.
3. **Frozen Panes**: Header rows are frozen. Scroll down as much as you like; the headers stay pinned to the top.
4. **Soft Alternating Rows**: Soft blue-gray (`#F4F7FA`) alternating row backgrounds maintain layout readability.
5. **High-Value Highlights**: Any opportunity where flights and accommodations are confirmed to be **fully covered** is automatically styled with a soft **Sage Green background (`#E2F0D9`)** and **Dark Olive text (`#385723`)**, making premium deals jump out instantly!
6. **Clickable Links**: All application URLs are styled as blue underlined hyperlinks that open directly in your web browser.

---

## 💡 Troubleshooting & Rate Limits

> [!NOTE]
> All search and extraction routines are executed within defensive `try/except` wrappers. If one specific query or API fails due to rate limits or connection hiccups, the agent will log the warning, skip that single chunk gracefully, and compile all other extracted listings without halting the program!

* **Groq 429 (Rate Limit)**: If your Groq free tier API key gets throttled, the agent instantly and automatically fails over to the Pollinations keyless GPT-4o engine for that batch query to keep execution flowing seamlessly.
* **Tavily 429 (Rate Limit)**: If Tavily hits search limits, the agent automatically fails over to your **Serper.dev** Google Search configuration on subsequent requests.

---

## 📜 Contributing & License

This project is open-source and free to use. 
* Feel free to fork the repository, open issues, or submit pull requests with improvements (such as adding new category sub-agents or expanding search engines!).
* Licensed under the **MIT License**. See the `LICENSE` file for details (or feel free to use it commercially or personally under standard open-source guidelines).
