import discord
from discord.ext import commands
import asyncio
from discord import app_commands





# Initialize bot with application command support
intents = discord.Intents.default()

intents.message_content = True
intents.presences = True 
intents.members = True 

bot = commands.Bot(command_prefix="!", intents=intents)


APP_KEY = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI1IiwianRpIjoiZjU4NmU5ZWZkZWRjZDQyZDNiMzZjYzk0MmE5YzRmNGQ0Yjg2ODI0ZGQzNWFmZDQ2OWRlY2RjMDc4YjQ1ZmJhMDZiMmQ4ZDNlMTA2MTlhZTciLCJpYXQiOjE3Mjc0Mzk0MTguNTkzMjk3LCJuYmYiOjE3Mjc0Mzk0MTguNTkzMywiZXhwIjoxNzU4OTc1NDE4LjU4NTk5NCwic3ViIjoiMzQ5MTk3Iiwic2NvcGVzIjpbXX0.W0cnFbQX3Lqfr6SA3Sm7JRqrLvtX5mz46lFseOVbgEHxVLkUDYCIn48GduJwNzTXEL_xjysvTzOw9cYhn47uLiGXV8egyxciKBOF1wVonzsN7wfDIGwzJnrrO041lL-KUsMNcaENo2zpeMWHRnsI5Jl66EkNfWDA-fIn6MFAPU3hbFp1_Z-9oa8La-lleF4gJjrOnlmVbuc6cdiZmn_dA4o__nHuzK-S8Wca3N72z1-Z2SDUhEdXutZGMiJ18Oo8_ehSfa756OMMY7IKCdObY4kdzXyJW3angZKFkRlewl366Wco6MSNckJ7jJRUsja5Y_K8uDSMC5XL_YQHiTGa0D6oqPOPW1WOeEY7T065BQwmR_Dz7ZdiBA81BmiG5AdyODZ-hUzCWDHXtHvxrHo1MkJUySCjEspDfCDqtXIzWlDgMBWUWUqUbcolgjxmvmYQdauo3tMao3Bx2_K7EFa5eqxLKJDoo8r4D-70Ssqcdb0Wc5QvgUDlNRR_0dO1hwp83Z4LwLRPD09BxsNQvosIRJR35o6Cjf9B1iObUZcdQYfAL1J1RHAePRb56F0lLgv_ObvjgmOEiDql-KGZdCjtwcR_nI8zqIipNHsUJvxwf1HdAR0rJdgVKfIuXnz6XrWR2_oBSEzNjZl6P69L4ORY5q4SU0qUFIYGoeto2ySru34'
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


from commands.presence_tracker import register_presence_tracker
from commands.speak import register_speak_commands

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
    register_presence_tracker(bot)
    register_loop_commands(bot)
    register_key_management(bot)
    
    
    
    print("Syncing commands with Discord...")
    await bot.tree.sync()
    print("Commands synced!")
    
    

@bot.event
async def on_disconnect():
    from commands.presence_tracker import save_current_activities
    save_current_activities()  # Save any ongoing activities
    print("Bot disconnected, saved ongoing activities")

# Run bot
bot.run("MTE2NjA2NTMyNzgxMDAzMTY2Ng.GtT7qS.pGDI5uJg-JCbQwvCJnuFecxdSHeM-n-ihEqb5g")