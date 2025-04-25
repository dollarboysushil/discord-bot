import discord
import requests
from discord.ext import tasks, commands
from discord import app_commands

class HTBProfile:
    def __init__(self, app_key, user_id):
        self.app_key = app_key
        self.user_id = user_id
        self.headers = {
            'Authorization': f'Bearer {self.app_key}',
            'User-Agent': 'Mozilla/5.0'
        }
        self.nepali_rank = None
        self.htb_rank = None
        self.user_owns = None
        self.system_owns = None
        self.global_rank = None
        self.presence_index = 0
        self.presence_messages = []

    def fetch_all_data(self):
        """Fetch all HTB profile data"""
        try:
            # Get Nepal country rankings
            np_data = self._get_country_rankings('NP')
            if np_data:
                self.nepali_rank = self._find_user_rank(np_data)
            
            # Get general profile data
            profile_data = self._get_profile_data()
            if profile_data:
                self.htb_rank = profile_data.get('rank')
                self.user_owns = profile_data.get('user_owns')
                self.system_owns = profile_data.get('system_owns')
                self.global_rank = profile_data.get('ranking')
            
            # Update presence messages
            self._update_presence_messages()
            return True
        except Exception as e:
            print(f"Error fetching HTB profile data: {e}")
            return False

    def _get_country_rankings(self, country_code):
        """Get rankings for a specific country"""
        url = f'https://labs.hackthebox.com/api/v4/rankings/country/{country_code}/members'
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to retrieve country data. Status code: {response.status_code}")
            return None

    def _get_profile_data(self):
        """Get basic profile data for the user"""
        url = f'https://labs.hackthebox.com/api/v4/user/profile/basic/{self.user_id}'
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json().get('profile', {})
        else:
            print(f"Failed to retrieve profile data. Status code: {response.status_code}")
            return None

    def _find_user_rank(self, data):
        """Find user's rank in the rankings data"""
        rankings = data.get('data', {}).get('rankings', [])
        for user in rankings:
            if user['id'] == self.user_id:
                return user['rank']
        return None

    def _update_presence_messages(self):
        """Update the list of presence messages"""
        messages = []
        
        if self.nepali_rank:
            messages.append(f'#{self.nepali_rank} Nepali Rank on HTB')
        
        if self.htb_rank:
            messages.append(f'{self.htb_rank} Rank on HTB')
        
        if self.user_owns is not None:
            messages.append(f'Owned {self.user_owns} Users on HTB')
        
        if self.system_owns is not None:
            messages.append(f'Owned {self.system_owns} Roots on HTB')
        
        if self.global_rank:
            messages.append(f'#{self.global_rank} Global Rank on HTB')
            
        self.presence_messages = messages

    def get_next_presence(self):
        """Get the next presence message in rotation"""
        if not self.presence_messages:
            return None
            
        message = self.presence_messages[self.presence_index]
        self.presence_index = (self.presence_index + 1) % len(self.presence_messages)
        return message

def register_htb_presence(bot, app_key, user_id):
    """Register HTB presence functionality with the bot"""
    htb_profile = HTBProfile(app_key, user_id)
    
    @tasks.loop(hours=1)
    async def fetch_profile_data():
        """Fetch HTB profile data every hour"""
        try:
            htb_profile.fetch_all_data()
            print("HTB profile data updated successfully")
        except Exception as e:
            print(f"Error in fetch_profile_data task: {e}")

    @tasks.loop(seconds=10)
    async def update_presence():
        """Rotate through different presence messages"""
        try:
            message = htb_profile.get_next_presence()
            if message:
                await bot.change_presence(activity=discord.CustomActivity(name=message))
        except Exception as e:
            print(f"Error updating presence: {e}")

    @update_presence.before_loop
    async def before_update_presence():
        await bot.wait_until_ready()
        # Initial fetch of profile data
        await fetch_profile_data()

    # Start the tasks
    fetch_profile_data.start()
    update_presence.start()
    
    return fetch_profile_data, update_presence