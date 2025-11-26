# Auto-Commit to GitHub Setup

This project includes an automatic commit and push system that watches for file changes and automatically commits them to GitHub.

## Quick Start

### Option 1: Run in Background (Recommended)

Double-click or run:
```powershell
.\scripts\start-auto-commit.ps1
```

This will start the file watcher in a separate window that runs in the background.

### Option 2: Run Directly

```powershell
.\scripts\auto-commit-github.ps1
```

## How It Works

1. **File Watcher**: Monitors all files in the project directory
2. **Debounce**: Waits 30 seconds after the last file change before committing (prevents too many commits)
3. **Auto-Commit**: Automatically stages all changes and commits with a timestamp message
4. **Auto-Push**: Pushes the commit to GitHub automatically

## Configuration

You can customize the commit delay (default: 30 seconds):

```powershell
.\scripts\auto-commit-github.ps1 -CommitDelay 60
```

## Ignored Files

The script automatically ignores:
- `.git/` directory
- `node_modules/`
- `__pycache__/`
- Build artifacts (`build/`, `dist/`, `target/`)
- IDE files (`.idea/`, `.vscode/`)
- Log files (`.log`)
- Temporary files (`.tmp`, `.swp`)

These are already configured in `.gitignore`.

## Stopping the Watcher

- Press `Ctrl+C` in the PowerShell window running the watcher
- Or close the PowerShell window

## Manual Commit (Alternative)

If you prefer to commit manually instead:

```powershell
cd C:\Users\ACHARYS\Desktop\AISOC
git add -A
git commit -m "Your commit message"
git push origin main
```

## Troubleshooting

### Push Fails with Authentication Error

If you see authentication errors, you may need to:
1. Set up a Personal Access Token (PAT) in GitHub
2. Use it as your password when Git prompts

### Too Many Commits

If commits are too frequent, increase the delay:
```powershell
.\scripts\auto-commit-github.ps1 -CommitDelay 120  # 2 minutes
```

### Script Not Detecting Changes

Make sure:
- You're saving files (not just typing)
- Files are not in ignored directories
- The script is running in the correct directory

