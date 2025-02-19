import discord
from discord.ext import commands, tasks
from discord import app_commands
from gtts import gTTS
import asyncio
import yt_dlp
from typing import Dict, Optional, Any

from collections import deque
from dataclasses import dataclass
from typing import Dict, Deque

intents = discord.Intents.default()



import requests
import asyncio


app_key = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI1IiwianRpIjoiZjU4NmU5ZWZkZWRjZDQyZDNiMzZjYzk0MmE5YzRmNGQ0Yjg2ODI0ZGQzNWFmZDQ2OWRlY2RjMDc4YjQ1ZmJhMDZiMmQ4ZDNlMTA2MTlhZTciLCJpYXQiOjE3Mjc0Mzk0MTguNTkzMjk3LCJuYmYiOjE3Mjc0Mzk0MTguNTkzMywiZXhwIjoxNzU4OTc1NDE4LjU4NTk5NCwic3ViIjoiMzQ5MTk3Iiwic2NvcGVzIjpbXX0.W0cnFbQX3Lqfr6SA3Sm7JRqrLvtX5mz46lFseOVbgEHxVLkUDYCIn48GduJwNzTXEL_xjysvTzOw9cYhn47uLiGXV8egyxciKBOF1wVonzsN7wfDIGwzJnrrO041lL-KUsMNcaENo2zpeMWHRnsI5Jl66EkNfWDA-fIn6MFAPU3hbFp1_Z-9oa8La-lleF4gJjrOnlmVbuc6cdiZmn_dA4o__nHuzK-S8Wca3N72z1-Z2SDUhEdXutZGMiJ18Oo8_ehSfa756OMMY7IKCdObY4kdzXyJW3angZKFkRlewl366Wco6MSNckJ7jJRUsja5Y_K8uDSMC5XL_YQHiTGa0D6oqPOPW1WOeEY7T065BQwmR_Dz7ZdiBA81BmiG5AdyODZ-hUzCWDHXtHvxrHo1MkJUySCjEspDfCDqtXIzWlDgMBWUWUqUbcolgjxmvmYQdauo3tMao3Bx2_K7EFa5eqxLKJDoo8r4D-70Ssqcdb0Wc5QvgUDlNRR_0dO1hwp83Z4LwLRPD09BxsNQvosIRJR35o6Cjf9B1iObUZcdQYfAL1J1RHAePRb56F0lLgv_ObvjgmOEiDql-KGZdCjtwcR_nI8zqIipNHsUJvxwf1HdAR0rJdgVKfIuXnz6XrWR2_oBSEzNjZl6P69L4ORY5q4SU0qUFIYGoeto2ySru34'
user_id = 349197




def get_profile_data_for_NP(app_key):
    # Set up the URL and headers
    url2 = f'https://labs.hackthebox.com/api/v4/rankings/country/NP/members'
    headers = {
        'Authorization': f'Bearer {app_key}',
        'User-Agent': 'Mozilla/5.0'
    }

    # Make the GET request
    response = requests.get(url2, headers=headers)

    # Check the response status
    if response.status_code == 200:
        return response.json()  # Return the JSON response
    else:
        print("Failed to retrieve data. Status code:", response.status_code)
        print("Response:", response.text)
        return None

def get_user_rank(data, user_id):
    # Iterate through the rankings to find the user with the specific ID
    rankings = data.get('data', {}).get('rankings', [])
    for user in rankings:
        if user['id'] == user_id:
            return user['rank']  # Return the user's rank
    return None  # Return None if the user is not found

# Fetch the profile data
profile_data2 = get_profile_data_for_NP(app_key)

#print(get_user_rank(profile_data,user_id))

###############################################################################################






###############################################################################################
#for other details
###############################################################################################

def get_profile_data(app_key, user_id):
    # Set up the URL and headers
    url = f'https://labs.hackthebox.com/api/v4/user/profile/basic/{user_id}'
    headers = {
        'Authorization': f'Bearer {app_key}',
        'User-Agent': 'Mozilla/5.0'
    }

    # Make the GET request
    response = requests.get(url, headers=headers)

    # Check the response status
    if response.status_code == 200:
        return response.json().get('profile', {})
    else:
        print("Failed to retrieve data. Status code:", response.status_code)
        print("Response:", response.text)
        return None

def get_rank(profile):
    return profile.get('rank')

def get_system_owns(profile):
    return profile.get('system_owns')

def get_user_owns(profile):
    return profile.get('user_owns')

def get_ranking(profile):
    return profile.get('ranking')

profile_data = get_profile_data(app_key, user_id)


###############################################################################################








# Intents are required for most bot actions
intents = discord.Intents.default()
intents.message_content = True  # Required for reading message content
intents.voice_states = True  # Required to get voice channel members

# Define the bot
class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.profile_data2 = None
        self.profile_data = None
        self.nepali_rank = None
        self.htb_rank = None
        self.user_owns = None
        self.system_owns = None
        self.global_rank = None


    async def setup_hook(self):
        # Sync the slash commands
        await bot.tree.sync()




    async def on_ready(self):
        print(f'Bot is online as {bot.user}')

        self.update_presence.start()  # Start updating presence every 10 seconds
        self.fetch_profile_data.start()  # Start fetching profile data every 1 hour


    @tasks.loop(seconds=10)  # Update presence every 10 seconds
    async def update_presence(self):
        try:
            if not self.is_closed() and self.profile_data2 and self.profile_data:
                # Update bot's presence every 10 seconds
                await self.change_presence(activity=discord.CustomActivity(name=f'#{self.nepali_rank} Nepali Rank on HTB'))
                await asyncio.sleep(10)
                await self.change_presence(activity=discord.CustomActivity(name=f'{self.htb_rank} Rank on HTB'))
                await asyncio.sleep(10)
                await self.change_presence(activity=discord.CustomActivity(name=f'Owned {self.user_owns} Users on HTB'))
                await asyncio.sleep(10)
                await self.change_presence(activity=discord.CustomActivity(name=f'Owned {self.system_owns} Roots on HTB'))
                await asyncio.sleep(10)
                await self.change_presence(activity=discord.CustomActivity(name=f'#{self.global_rank} Global Rank on HTB'))
        except Exception as e:
            print(f"Error updating presence: {e}")

    @tasks.loop(hours=1)  # Fetch profile data every 1 hour
    async def fetch_profile_data(self):
        try:
            # Fetch profile data every 1 hour
            self.profile_data2 = get_profile_data_for_NP(app_key)
            self.profile_data = get_profile_data(app_key, user_id)

            # Update ranks and other data
            self.nepali_rank = get_user_rank(self.profile_data2, user_id)
            self.htb_rank = get_rank(self.profile_data)
            self.user_owns = get_user_owns(self.profile_data)
            self.system_owns = get_system_owns(self.profile_data)
            self.global_rank = get_ranking(self.profile_data)

            print("Profile data fetched successfully.")
        except Exception as e:
            print(f"Error fetching profile data: {e}")

# Create the bot instance
bot = MyBot()