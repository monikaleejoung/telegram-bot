from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import sqlite3
import logging

# Set up logging to see what's happening
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Configuration
PASSWORD = "123456"  # Your access password - change this to something secure!
BOT_TOKEN = "7305836786:AAFSdqidLT4GXWJHfHKYY-XGD5zOUPAoE94"  # Replace with your actual bot token from @BotFather

# Store logged-in users (in memory - will reset when bot restarts)
logged_in_users = set()

# Database setup
def setup_database():
    """Initialize the SQLite database and create the notes table"""
    conn = sqlite3.connect("data.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            key TEXT PRIMARY KEY, 
            value TEXT
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
/logout - Logout from the bot

Example:
/login 123456
/save mynote This is my important note
/get mynote
    """
    await update.message.reply_text(welcome_text)

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
    
    try:
        # Save to database
        db_cursor.execute("REPLACE INTO notes (key, value) VALUES (?, ?)", (key, value))
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
        # Get from database
        db_cursor.execute("SELECT value FROM notes WHERE key = ?", (key,))
        result = db_cursor.fetchone()
        
        if result:
            await update.message.reply_text(f"📝 {key}: {result[0]}")
        else:
            await update.message.reply_text(f"❌ No note found with key '{key}'")
    except Exception as e:
        await update.message.reply_text(f"❌ Error retrieving note: {str(e)}")

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
        # Get all notes
        db_cursor.execute("SELECT key, value FROM notes")
        results = db_cursor.fetchall()
        
        if results:
            notes_list = "📋 Your saved notes:\n\n"
            for i, (key, value) in enumerate(results, 1):
                notes_list += f"{i}. {key}: {value}\n"
            await update.message.reply_text(notes_list)
        else:
            await update.message.reply_text("📝 No notes saved yet. Use /save to create your first note!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error listing notes: {str(e)}")

def main():
    """Main function to run the bot"""
    print("🤖 Starting Telegram Notes Bot...")
    
    # Create the application
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("login", login))
    app.add_handler(CommandHandler("save", save))
    app.add_handler(CommandHandler("get", get))
    app.add_handler(CommandHandler("logout", logout))
    app.add_handler(CommandHandler("list", list_notes))
    
    print("✅ Bot is running! Press Ctrl+C to stop.")
    
    # Start the bot
    app.run_polling()

if __name__ == "__main__":
    main()
