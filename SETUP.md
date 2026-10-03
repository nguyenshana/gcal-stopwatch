# Calendar Stopwatch - setup

Made by Claude

## Set Up
1. Start the app with `python3 server.py`, or see "Alternate Option to start the app: Run it via Start.command"
2. Set up Google calendar connection by following the "One-time Google setup" section

### Alternate Option to start the app: Run it via Start.command
0. First time only: macOS blocks downloaded scripts. In Terminal run
   `xattr -dr com.apple.quarantine ~/<path-to-folder>/gcal-stopwatch` (adjust the path if needed).
1. Double-click `Start.command`.
   If macOS offers to install developer tools for `python3`, accept, then run it again.
2. A window opens (Chrome/Edge/Brave app-style if installed, otherwise your default browser).
3. Press Ctrl+C or close the Terminal window to quit.

### One-time Google setup (~5 min, free)
1. Go to https://console.cloud.google.com and create a project (any name).
2. APIs & Services > Library > search "Google Calendar API" > Enable.
3. APIs & Services > OAuth consent screen (now called "Google Auth Platform"):
   - **Branding:** enter an app name (e.g. gcal-stopwatch) and your email as the support email, then save.
   - **Audience:** choose External. Under **Test users**, click **Add users**, enter the Google
     account you'll sign in with, and save. Without this step Google shows
     "Access blocked: ... has not completed the Google verification process" (Error 403).
   - Optional: "Publish app" avoids re-signing in every 7 days, but needs a homepage and privacy
     policy URL. Staying in Testing works fine; you just sign in again about once a week.
4. Credentials > Create credentials > OAuth client ID > Application type **Desktop app**.
5. Download the JSON, rename it to `credentials.json`, and put it in this folder.
6. Start the app and press "Sign in with Google". You'll see an "unverified app" warning:
   Advanced > Go to (app) > allow.

Your login token is stored in `data.json` in this folder. Delete it to sign out everywhere.
