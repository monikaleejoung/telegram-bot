# Telegram Notes Bot

A simple Telegram bot that allows users to save and retrieve notes using a key-value system with password protection.

## Features

- 🔐 Password-protected access
- 💾 Save notes with custom keys
- 📖 Retrieve notes by key
- 📋 List all saved notes
- 🚪 Logout functionality
- 💾 SQLite database storage

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Your Bot Token

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the bot token (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 3. Configure Your Bot

1. Open `bot.py` in a text editor
2. Replace `YOUR_BOT_TOKEN` with your actual bot token:
   ```python
   BOT_TOKEN = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
   ```
3. (Optional) Change the password from "123456" to something more secure:
   ```python
   PASSWORD = "your_secure_password_here"
   ```

### 4. Run the Bot

```bash
python bot.py
```

You should see: `🤖 Starting Telegram Notes Bot...` and `✅ Bot is running!`

## How to Use

### 1. Start the Bot
Send `/start` to your bot to see the welcome message and available commands.

### 2. Login
```
/login 123456
```
Replace "123456" with your actual password.

### 3. Save a Note
```
/save mynote This is my important note
```
This saves "This is my important note" with the key "mynote".

### 4. Get a Note
```
/get mynote
```
This retrieves the note saved with key "mynote".

### 5. List All Notes
```
/list
```
Shows all your saved notes.

### 6. Logout
```
/logout
```
Logs you out and prevents access to notes until you login again.

## Commands Summary

| Command | Usage | Description |
|---------|-------|-------------|
| `/start` | `/start` | Shows welcome message and help |
| `/login` | `/login <password>` | Login with password |
| `/save` | `/save <key> <value>` | Save a note |
| `/get` | `/get <key>` | Retrieve a note |
| `/list` | `/list` | List all notes |
| `/logout` | `/logout` | Logout from bot |

## Examples

```
/login 123456
/save todo Buy groceries tomorrow
/save reminder Call mom at 3pm
/get todo
/list
/logout
```

## Security Notes

- The password is stored in plain text in the code - change it to something secure!
- User sessions are stored in memory and will reset when the bot restarts
- Notes are stored in a local SQLite database (`data.db`)

## Troubleshooting

### Bot not responding?
- Make sure you replaced `YOUR_BOT_TOKEN` with your actual token
- Check that the bot is running (you should see "Bot is running!" message)
- Try sending `/start` to your bot

### Database errors?
- The bot will automatically create the database file (`data.db`) when it first runs
- Make sure the bot has write permissions in the directory

### Import errors?
- Run `pip install -r requirements.txt` to install dependencies
- Make sure you're using Python 3.7 or higher 