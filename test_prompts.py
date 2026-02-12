import yaml
import os
import sys

# Load Config
def load_config():
    if os.path.exists("config.yaml"):
        with open("config.yaml", "r") as f:
            return yaml.safe_load(f)
    return {}

# Mock the rewriter logic
def get_sys_prompt(config, app_name, window_title):
    # Check for App-specific config
    app_config = config.get("apps", {}).get(app_name)
    
    if app_config:
        # Check for conditional rules (e.g. Chrome tab titles)
        if "rules" in app_config:
            for rule in app_config["rules"]:
                if "if_title_contains" in rule and rule["if_title_contains"].lower() in window_title.lower():
                    return rule["instructions"], f"Matched Rule: {rule['if_title_contains']}"
        
        # Fallback to general app instructions
        if "instructions" in app_config:
            return app_config["instructions"], "Matched App Default"

    # Global fallback
    return config.get("global_instructions", "Default"), "Global Fallback"

def main():
    print("--- 🧪 Shortcut Copywriter Prompt Tester ---")
    config = load_config()
    if not config:
        print("Error: Could not load config.yaml")
        return

    # Test Cases
    tests = [
        ("Slack", "", "Slack Message"),
        ("WhatsApp", "", "WhatsApp Message"),
        ("Microsoft Teams", "", "Teams Message"),
        ("Mail", "", "Professional Email"),
        ("Google Chrome", "Inbox (1) - Gmail", "Gmail via Chrome"),
        ("Google Chrome", "WhatsApp Web", "WhatsApp via Chrome"),
        ("Google Chrome", "Twitter / X", "Twitter Post"),
        ("TextEdit", "Untitled", "Generic App (Should use Global)")
    ]

    for app, title, desc in tests:
        print(f"\nExample: {desc}")
        print(f"Context: App='{app}', Title='{title}'")
        
        prompt, source = get_sys_prompt(config, app, title)
        
        print(f"Source:  {source}")
        print("-" * 40)
        # Print first 3 lines of prompt to verify
        lines = prompt.strip().split('\n')
        for i in range(min(5, len(lines))):
            print(f"  > {lines[i]}")
        print("-" * 40)

if __name__ == "__main__":
    main()
