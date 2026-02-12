# Shortcut Copywriter 🤖✏️

An intelligent, context-aware AI writing assistant for macOS.

**What it does:**
Select text in *any* application (Slack, WhatsApp, Chrome, Mail, etc.), press a global hotkey, and have an LLM rewrite it perfectly for that context.

- **Universal:** Works in stubborn apps like Google Docs, WhatsApp, and VS Code.
- **Context-Aware:** Knows if you're writing a professional email or a casual Slack message.
- **Secure:** Runs locally on your Mac using your own API Key.

## Installation

### 1. Download & Setup
1.  Clone or download this repository.
2.  Open Terminal and run the installer:
    ```bash
    cd path/to/shortcut-copywriter
    bash install.sh
    ```
3.  The installer will:
    -   Set up the Python environment.
    -   Ask for your OpenAI API Key.
    -   Generate your `config.yaml`.
    -   **Give you the exact command** to use in the Shortcut.

### 2. Create the macOS Shortcut
1.  Open the **Shortcuts** app on your Mac.
2.  Create a new Shortcut named **"AI Copywriter"**.
3.  Add the following actions in order:

    1.  **Run AppleScript** (Force Copy):
        ```applescript
        on run {input, parameters}
            tell application "System Events" to keystroke "c" using command down
            delay 1.0
            return input
        end run
        ```
    2.  **Get Clipboard**
    3.  **Get Text from Input** (Input: Clipboard)
    4.  **Run Shell Script**:
        -   Shell: `/bin/zsh`
        -   Pass Input: **as arguments**
        -   Uncheck "Run as Administrator"
        -   **Command:** (Paste the command provided by `install.sh`)
    5.  **Copy to Clipboard** (Input: Shell Script Result)
    6.  **Run AppleScript** (Force Paste):
        ```applescript
        on run {input, parameters}
            tell application "System Events" to keystroke "v" using command down
            return input
        end run
        ```

4.  **Assign a Hotkey**: In the Shortcut details (sidebar), click "Add Keyboard Shortcut" and choose a key (e.g., `F6` or `Cmd+Shift+R`).

### 3. Usage
-   **Method A (Hotkey):** Select text -> Press Hotkey.
-   **Method B (Spotlight - Best for WhatsApp):** Select Text -> `Cmd+Space` -> Type "AI Copywriter" -> Enter.

## Configuration
Edit `config.yaml` to change prompts for specific apps or switch models.

```yaml
apps:
  "Slack":
    instructions: "Make it friendly and concise."
  "Mail":
    instructions: "Professional and polite."
```
