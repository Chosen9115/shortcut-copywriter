#!/bin/bash

# Shortcut Copywriter Installer

echo "----------------------------------------------------------------"
echo "  Shortcut Copywriter - Setup Wizard"
echo "----------------------------------------------------------------"

# 1. Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 could not be found. Please install Python 3."
    exit 1
fi

echo "[+] Found Python 3"

# 2. Create Virtual Environment
if [ ! -d "venv" ]; then
    echo "[*] Creating virtual environment (venv)..."
    python3 -m venv venv
else
    echo "[+] Virtual environment already exists."
fi

# 3. Install Dependencies
echo "[*] Installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt > /dev/null
if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies."
    exit 1
fi
echo "[+] Dependencies installed."

# 4. Configure API Key
if [ ! -f "config.yaml" ]; then
    echo "----------------------------------------------------------------"
    echo "  Configuration Setup"
    echo "----------------------------------------------------------------"
    cp config.example.yaml config.yaml
    
    echo "Please enter your OpenAI API Key (starts with sk-...):"
    read -r api_key
    
    # Use sed to replace the placeholder
    # Detect OS for sed usage (macOS requires empty string arg for -i)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/YOUR_API_KEY_HERE/$api_key/" config.yaml
    else
        sed -i "s/YOUR_API_KEY_HERE/$api_key/" config.yaml
    fi
    
    echo "[+] API Key saved to config.yaml"
else
    echo "[+] config.yaml already exists. Skipping configuration."
fi

# 5. Output Shortcut Path
current_dir=$(pwd)
python_path="$current_dir/venv/bin/python"
script_path="$current_dir/rewriter.py"
full_command="$python_path $script_path \"\$1\""

echo "----------------------------------------------------------------"
echo "  Setup Complete! "
echo "----------------------------------------------------------------"
echo ""
echo "To finish, create your macOS Shortcut with this 'Run Shell Script' command:"
echo ""
echo "----------------------------------------------------------------"
echo "$full_command"
echo "----------------------------------------------------------------"
echo ""
echo "(Details: Shell: /bin/zsh, Pass Input: as arguments, Uncheck Admin)"
echo "----------------------------------------------------------------"
