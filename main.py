import discord
from discord.ext import commands
import asyncio
from discord import app_commands
from dotenv import load_dotenv

from dotenv import load_dotenv
import os

# Load variables from .env file
load_dotenv()

# Access the key
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")



# Initialize bot with application command support
intents = discord.Intents.default()

intents.message_content = True
intents.presences = True 
intents.members = True 

bot = commands.Bot(command_prefix="!", intents=intents)


APP_KEY = os.getenv("APP_KEY")
USER_ID = 349197



# Import and register commands
from commands.ping import register_ping_command
from commands.tag import tag_user
from commands.say_hello import say_hello
from commands.tag_vc import tag_vc

from commands.announce import announce
from commands.speak import register_speak_commands  # Import speak commands

from commands.change_nickname import change_nickname
#from commands.display_htb_stats import update_presence, fetch_profile_data


from commands.loops_commands import register_loop_commands
from commands.key_manager import register_key_management
from commands.music import register_music_commands

#from commands.presence_tracker import register_presence_tracker
from commands.speak import register_speak_commands
from commands.htb_api import register_htb_presence


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    # Register all slash commands
    register_ping_command(bot)
    tag_user(bot)
    say_hello(bot)
    tag_vc(bot)
    announce(bot)
    register_speak_commands(bot)
    
    change_nickname(bot)
    #register_presence_tracker(bot)
    register_loop_commands(bot)
    register_key_management(bot)
    
    # Start HackTheBox presence updates
    register_htb_presence(bot, APP_KEY, USER_ID)
    register_music_commands(bot) 
    print("Syncing commands with Discord...")
    await bot.tree.sync()
    print("Commands synced!")
    
    

@bot.event
async def on_disconnect():
    from commands.presence_tracker import save_current_activities
    save_current_activities()  # Save any ongoing activities
    print("Bot disconnected, saved ongoing activities")

# Run bot
bot.run(DISCORD_TOKEN)