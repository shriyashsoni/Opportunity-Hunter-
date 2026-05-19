#!/bin/bash

# ------------------------------------------------------------------------------
# 🎯 OPPORTUNITY HUNTER AI AGENT - MAC/LINUX RUNNER
# ------------------------------------------------------------------------------
# This script automates virtual environment activation and starts the agent.
# ------------------------------------------------------------------------------

# Stylized color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}          STARTING OPPORTUNITY HUNTER AI AGENT          ${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[ERROR] Python 3 is not installed or not in your PATH.${NC}"
    echo "Please install Python 3.9+ from https://python.org or your package manager and try again."
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

# Detect existing virtual environment and activate
if [ -d ".venv" ]; then
    echo -e "${GREEN}[INFO] Found virtual environment '.venv'. Activating...${NC}"
    source .venv/bin/activate
elif [ -d "venv" ]; then
    echo -e "${GREEN}[INFO] Found virtual environment 'venv'. Activating...${NC}"
    source venv/bin/activate
else
    echo -e "${YELLOW}[WARNING] No active Python virtual environment (.venv/venv) detected.${NC}"
    echo "It is highly recommended to run this agent in a virtual environment."
    read -p "Do you want to create a new virtual environment now? (y/n): " create_venv
    if [[ $create_venv == "y" || $create_venv == "Y" ]]; then
        echo -e "${GREEN}[INFO] Creating virtual environment (.venv)...${NC}"
        python3 -m venv .venv
        source .venv/bin/activate
        echo -e "${GREEN}[INFO] Installing dependencies from requirements.txt...${NC}"
        pip install --upgrade pip
        pip install -r requirements.txt
    else
        echo -e "${YELLOW}[INFO] Running with global system Python interpreter...${NC}"
    fi
fi

echo -e "${GREEN}[INFO] Executing AI Agent sweep...${NC}"
echo ""

# Execute the orchestrator
python3 main.py

echo ""
echo -e "${BLUE}============================================================${NC}"
echo -e "${GREEN}           EXECUTION COMPLETED SUCCESSFULLY          ${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

read -p "Press Enter to exit..."
