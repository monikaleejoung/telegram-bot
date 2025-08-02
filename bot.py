from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import sqlite3
import logging
import os

# Set up logging to see what's happening
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Configuration
PASSWORD = "123456"  # Your access password - change this to something secure!
# Replace with your actual bot token from @BotFather
BOT_TOKEN = "Your_bot_token"


# Store logged-in users (in memory - will reset when bot restarts)
logged_in_users = set()

# Database setup
def setup_database():
    """Initialize the SQLite database and create the notes table"""
    conn = sqlite3.connect("data.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            key TEXT, 
            value TEXT,
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (key, user_id)
        )
    """)
    conn.commit()
    return conn, cursor

# Initialize database
db_conn, db_cursor = setup_database()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome message when user starts the bot"""
    welcome_text = """
🤖 Welcome to the Notes Bot!

Available commands:
/login <password> - Login to access notes
/save <key> <value> - Save a note with key and value
/get <key> - Retrieve a note by key
/list - List all your saved notes
/delete <key> - Delete a specific note
/help - Show this help message
/logout - Logout from the bot

Example:
/login 123456
/save mynote This is my important note
/get mynote
/list
/delete mynote
    """
    await update.message.reply_text(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help message"""
    help_text = """
📚 **Notes Bot Help**

**Commands:**
• `/start` - Welcome message
• `/help` - Show this help
• `/login <password>` - Login with password
• `/save <key> <value>` - Save a note
• `/get <key>` - Get a note by key
• `/list` - List all your notes
• `/delete <key>` - Delete a note
• `/logout` - Logout

**Examples:**
```
/login 123456
/save todo Buy groceries
/get todo
/list
/delete todo
```

**Tips:**
• Your notes are private to you
• Keys are case-sensitive
• You can use spaces in values
• Logout to secure your notes
    """
    await update.message.reply_text(help_text)

async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user login with password"""
    # Check if password is provided
    if len(context.args) != 1:
        await update.message.reply_text("❌ Usage: /login <password>\nExample: /login 123456")
        return
    
    password = context.args[0]
    user_id = update.message.from_user.id
    
    # Check if password is correct
    if password == PASSWORD:
        logged_in_users.add(user_id)
        await update.message.reply_text("✅ Login successful! You can now use /save and /get commands.")
    else:
        await update.message.reply_text("❌ Wrong password! Please try again.")

async def save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save a note with key and value"""
    user_id = update.message.from_user.id
    
    # Check if user is logged in
    if user_id not in logged_in_users:
        await update.message.reply_text("🚫 Please login first using /login <password>")
        return
    
    # Check if key and value are provided
    if len(context.args) < 2:
        await update.message.reply_text("❌ Usage: /save <key> <value>\nExample: /save mynote This is my note")
        return
    
    key = context.args[0]
    value = " ".join(context.args[1:])  # Join all remaining words as the value
    
    # Check if key is too long
    if len(key) > 50:
        await update.message.reply_text("❌ Key is too long! Maximum 50 characters.")
        return
    
    # Check if value is too long
    if len(value) > 1000:
        await update.message.reply_text("❌ Value is too long! Maximum 1000 characters.")
        return
    
    try:
        # Save to database (user-specific)
        db_cursor.execute("REPLACE INTO notes (key, value, user_id) VALUES (?, ?, ?)", (key, value, user_id))
        db_conn.commit()
        await update.message.reply_text(f"✅ Saved: '{key}' = '{value}'")
    except Exception as e:
        await update.message.reply_text(f"❌ Error saving note: {str(e)}")

async def get(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Retrieve a note by key"""
    user_id = update.message.from_user.id
    
    # Check if user is logged in
    if user_id not in logged_in_users:
        await update.message.reply_text("🚫 Please login first using /login <password>")
        return
    
    # Check if key is provided
    if len(context.args) != 1:
        await update.message.reply_text("❌ Usage: /get <key>\nExample: /get mynote")
        return
    
    key = context.args[0]
    
    try:
        # Get from database (user-specific)
        db_cursor.execute("SELECT value FROM notes WHERE key = ? AND user_id = ?", (key, user_id))
        result = db_cursor.fetchone()
        
        if result:
            await update.message.reply_text(f"📝 {key}: {result[0]}")
        else:
            await update.message.reply_text(f"❌ No note found with key '{key}'")
    except Exception as e:
        await update.message.reply_text(f"❌ Error retrieving note: {str(e)}")

async def delete_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete a note by key"""
    user_id = update.message.from_user.id
    
    # Check if user is logged in
    if user_id not in logged_in_users:
        await update.message.reply_text("🚫 Please login first using /login <password>")
        return
    
    # Check if key is provided
    if len(context.args) != 1:
        await update.message.reply_text("❌ Usage: /delete <key>\nExample: /delete mynote")
        return
    
    key = context.args[0]
    
    try:
        # Delete from database (user-specific)
        db_cursor.execute("DELETE FROM notes WHERE key = ? AND user_id = ?", (key, user_id))
        db_conn.commit()
        
        if db_cursor.rowcount > 0:
            await update.message.reply_text(f"🗑️ Deleted note: '{key}'")
        else:
            await update.message.reply_text(f"❌ No note found with key '{key}' to delete")
    except Exception as e:
        await update.message.reply_text(f"❌ Error deleting note: {str(e)}")

async def logout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Logout user"""
    user_id = update.message.from_user.id
    logged_in_users.discard(user_id)
    await update.message.reply_text("✅ Logged out successfully!")

async def list_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all saved notes for the user"""
    user_id = update.message.from_user.id
    
    # Check if user is logged in
    if user_id not in logged_in_users:
        await update.message.reply_text("🚫 Please login first using /login <password>")
        return
    
    try:
        # Get all notes for this user
        db_cursor.execute("SELECT key, value FROM notes WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
        results = db_cursor.fetchall()
        
        if results:
            notes_list = "📋 Your saved notes:\n\n"
            for i, (key, value) in enumerate(results, 1):
                # Truncate long values for display
                display_value = value[:50] + "..." if len(value) > 50 else value
                notes_list += f"{i}. **{key}**: {display_value}\n"
            
            if len(results) == 1:
                notes_list += f"\n📊 Total: 1 note"
            else:
                notes_list += f"\n📊 Total: {len(results)} notes"
                
            await update.message.reply_text(notes_list)
        else:
            await update.message.reply_text("📝 No notes saved yet. Use /save to create your first note!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error listing notes: {str(e)}")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user statistics"""
    user_id = update.message.from_user.id
    
    # Check if user is logged in
    if user_id not in logged_in_users:
        await update.message.reply_text("🚫 Please login first using /login <password>")
        return
    
    try:
        # Get user stats
        db_cursor.execute("SELECT COUNT(*) FROM notes WHERE user_id = ?", (user_id,))
        note_count = db_cursor.fetchone()[0]
        
        stats_text = f"""
📊 **Your Statistics**

📝 Total notes: {note_count}
👤 User ID: {user_id}
🔐 Status: Logged in

Use /list to see all your notes!
        """
        await update.message.reply_text(stats_text)
    except Exception as e:
        await update.message.reply_text(f"❌ Error getting stats: {str(e)}")

def main():
    """Main function to run the bot"""
    print("🤖 Starting Telegram Notes Bot...")
    
    # Create the application
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("login", login))
    app.add_handler(CommandHandler("save", save))
    app.add_handler(CommandHandler("get", get))
    app.add_handler(CommandHandler("delete", delete_note))
    app.add_handler(CommandHandler("list", list_notes))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("logout", logout))
    
    print("✅ Bot is running! Press Ctrl+C to stop.")
    
    # Start the bot
    app.run_polling()

if __name__ == "__main__":
    main()
