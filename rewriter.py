import os
import sys
import yaml
import subprocess
import requests
import json

# --- Configuration & Constants ---
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")

def get_active_context():
    """
    Uses AppleScript to get the name of the frontmost application and its window title.
    Returns: (app_name, window_title)
    """
    scpt = """
    global frontApp, frontAppName, windowTitle
    
    set windowTitle to ""
    
    tell application "System Events"
        set frontApp to first application process whose frontmost is true
        set frontAppName to name of frontApp
        
        try
            tell process frontAppName
                set windowTitle to name of front window
            end tell
        on error
            set windowTitle to ""
        end try
    end tell
    
    return frontAppName & "|||" & windowTitle
    """
    try:
        result = subprocess.check_output(['osascript', '-e', scpt], text=True).strip()
        parts = result.split("|||")
        if len(parts) == 2:
            return parts[0], parts[1]
        return parts[0], ""
    except Exception as e:
        # Fallback if AppleScript fails
        # print(f"Error getting context: {e}", file=sys.stderr)
        return "Unknown", ""

def load_config():
    """Loads the configuration from config.yaml."""
    if not os.path.exists(CONFIG_PATH):
        print(f"Error: Config file not found at {CONFIG_PATH}", file=sys.stderr)
        sys.exit(1)
    
    with open(CONFIG_PATH, 'r') as f:
        return yaml.safe_load(f)

def get_sys_prompt(config, app_name, window_title):
    """
    Determines the system prompt based on the application and window title.
    Prioritizes specific rules, then app-specific instructions, then global instructions.
    """
    
    # Check for App-specific config
    app_config = config.get("apps", {}).get(app_name)
    
    if app_config:
        # Check for conditional rules (e.g. Chrome tab titles)
        if "rules" in app_config:
            for rule in app_config["rules"]:
                if "if_title_contains" in rule and rule["if_title_contains"].lower() in window_title.lower():
                    return rule["instructions"]
        
        # Fallback to general app instructions
        if "instructions" in app_config:
            return app_config["instructions"]

    # Global fallback
    return config.get("global_instructions", "Rewrite the text to be clear and professional.")

def call_llm(config, text, system_instruction):
    """Calls the LLM API based on configuration."""
    api_config = config.get("api", {})
    provider = api_config.get("provider", "openai")
    key = api_config.get("key")
    
    if not key or key == "YOUR_API_KEY_HERE":
        return "Error: API Key not configured in config.yaml."

    if provider == "openai":
        url = f"{api_config.get('base_url', 'https://api.openai.com/v1')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": api_config.get("model", "gpt-4o"),
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": text}
            ],
            "temperature": api_config.get("temperature", 0.7),
            "frequency_penalty": api_config.get("frequency_penalty", 0.0),
            "presence_penalty": api_config.get("presence_penalty", 0.0)
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            if response.status_code != 200:
                print(f"API Error: Status {response.status_code}", file=sys.stderr)
                print(f"Response: {response.text}", file=sys.stderr)
                print(f"Headers: {response.headers}", file=sys.stderr)
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
        except Exception as e:
            return f"Error calling OpenAI API: {str(e)}"
            
    elif provider == "anthropic":
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        data = {
            "model": api_config.get("model", "claude-3-opus-20240229"),
            "system": system_instruction,
            "messages": [
                {"role": "user", "content": text}
            ],
            "max_tokens": 1024
        }
        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            result = response.json()
            return result['content'][0]['text'].strip()
        except Exception as e:
            return f"Error calling Anthropic API: {str(e)}"
            
    else:
        return f"Error: Unsupported provider '{provider}'"

def main():
    if len(sys.argv) < 2:
        # If no input argument, check stdin (sometimes shortcuts pass via stdin)
        if not sys.stdin.isatty():
            text = sys.stdin.read().strip()
        else:
            print("Usage: python rewriter.py <text_to_rewrite>")
            sys.exit(1)
    else:
        text = sys.argv[1]

    if not text:
        print("No text provided.")
        sys.exit(0)

    # 1. Load Config
    config = load_config()

    # Debug logging
    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "debug.log")
    with open(log_path, "a") as f:
        f.write(f"\n--- New Run ---\nArgs: {sys.argv}\n")

    # Handle input (Text or File Path)
    text = ""
    # Check arguments first (Index 1)
    if len(sys.argv) > 1:
        text = sys.argv[1]
    
    # If no arg, try stdin (blindly read)
    if not text:
        try:
            # Read binary to avoid decoding errors
            stdin_bytes = sys.stdin.buffer.read()
            if stdin_bytes:
                try:
                    text = stdin_bytes.decode('utf-8').strip()
                except:
                    text = stdin_bytes.decode('latin-1').strip()
        except Exception:
             pass

    if not text:
        print("No text provided.")
        sys.exit(0)

    # Check if input is a file path
    if os.path.exists(text) and os.path.isfile(text):
        try:
            # If it's an RTF file, convert it using textutil
            if text.lower().endswith(".rtf"):
                try:
                    # Log file size
                    size = os.path.getsize(text)

                    # Convert
                    result = subprocess.run(['textutil', '-convert', 'txt', '-stdout', text], capture_output=True, text=True)
                    
                    if result.returncode != 0:
                        # Fallback
                        with open(text, 'r', errors='ignore') as f:
                            text = f.read()
                    else:
                        content = result.stdout
                        
                        if not content.strip():
                            with open(text, 'r', errors='ignore') as f:
                                text = f.read()
                        else:
                            text = content

                except Exception as e:
                    # Fallback to reading raw
                    with open(text, 'r', errors='ignore') as f:
                        text = f.read()
            else:
                # Try reading as plain text
                with open(text, 'r', errors='ignore') as f:
                    text = f.read()
        except Exception as e:
            pass

    if not text:
        print("No text provided.")
        sys.exit(0)

    # 2. Get Context
    app_name, window_title = get_active_context()

    # 3. Determine Instructions
    instructions = get_sys_prompt(config, app_name, window_title)

    # 4. Call LLM
    try:
        new_text = call_llm(config, text, instructions)
        if new_text.startswith("Error calling"):
            raise Exception(new_text)
        
        # 5. Output Result
        print(new_text)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
