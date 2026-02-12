from rewriter import get_active_context

print("Testing Context Detection...")
app, title = get_active_context()
print(f"Detected App: '{app}'")
print(f"Detected Window Title: '{title}'")

if app and app != "Unknown":
    print("SUCCESS: Context detection is working.")
else:
    print("WARNING: Context detection might be failing or permissions are needed.")
