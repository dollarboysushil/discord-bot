import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import yt_dlp  # Using yt-dlp instead of youtube_dl
import os

# YT-DLP options
ytdlp_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  # Bind to IPv4 since IPv6 addresses cause issues sometimes
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

ffmpeg_options = {
    'options': '-vn',
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
}

ytdlp = yt_dlp.YoutubeDL(ytdlp_format_options)

class YTDLPSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        
        try:
            data = await loop.run_in_executor(None, lambda: ytdlp.extract_info(url, download=not stream))
            
            if 'entries' in data:
                # Take first item from a playlist
                data = data['entries'][0]

            # Get direct audio URL for streaming
            if stream:
                return cls(discord.FFmpegPCMAudio(data['url'], **ffmpeg_options), data=data)
            else:
                filename = ytdlp.prepare_filename(data)
                # Convert filename to mp3 if it's been extracted as audio
                if filename.endswith('.webm') or filename.endswith('.m4a'):
                    base_filename = os.path.splitext(filename)[0]
                    filename = f"{base_filename}.mp3"
                return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)
                
        except Exception as e:
            print(f"Error extracting info: {e}")
            raise e

class MusicPlayer:
    def __init__(self, bot):
        self.bot = bot
        self.voice_clients = {}  # {guild_id: voice_client}
        
    async def play(self, interaction, url):
        """Play music from YouTube URL"""
        if not interaction.user.voice:
            await interaction.response.send_message("You need to be in a voice channel to use this command!", ephemeral=True)
            return
        
        voice_channel = interaction.user.voice.channel
        guild_id = interaction.guild_id
        
        # Create downloads directory if it doesn't exist
        if not os.path.exists('downloads'):
            os.makedirs('downloads')
        
        # Join the user's voice channel if not already connected
        if guild_id not in self.voice_clients or not self.voice_clients[guild_id].is_connected():
            try:
                await interaction.response.defer(ephemeral=True)
                self.voice_clients[guild_id] = await voice_channel.connect()
                await interaction.followup.send(f"Connected to {voice_channel.name}", ephemeral=True)
            except discord.ClientException:
                # Already connected, move to the new channel
                await interaction.response.defer(ephemeral=True)
                await self.voice_clients[guild_id].move_to(voice_channel)
                await interaction.followup.send(f"Moved to {voice_channel.name}", ephemeral=True)
        else:
            await interaction.response.defer(ephemeral=True)
            await interaction.followup.send(f"Already connected to {voice_channel.name}", ephemeral=True)
        
        # Process and play the URL
        try:
            await interaction.followup.send(f"Processing: {url}", ephemeral=True)
            
            # If already playing, stop current audio
            if self.voice_clients[guild_id].is_playing():
                self.voice_clients[guild_id].stop()
            
            # Get the source and play the audio (using stream=True)
            player = await YTDLPSource.from_url(url, loop=self.bot.loop, stream=True)
            self.voice_clients[guild_id].play(player, after=lambda e: print(f'Player error: {e}') if e else None)
            
            await interaction.followup.send(f"Now playing: **{player.title}**")
        except Exception as e:
            error_message = str(e)
            print(f"Error playing URL: {error_message}")
            await interaction.followup.send(f"An error occurred while trying to play the audio: {error_message}")
    
    async def stop(self, interaction):
        """Stop the currently playing music and disconnect"""
        guild_id = interaction.guild_id
        
        if guild_id in self.voice_clients and self.voice_clients[guild_id].is_connected():
            self.voice_clients[guild_id].stop()
            await self.voice_clients[guild_id].disconnect()
            del self.voice_clients[guild_id]
            await interaction.response.send_message("Disconnected from voice channel", ephemeral=True)
        else:
            await interaction.response.send_message("Not connected to any voice channel", ephemeral=True)

def register_music_commands(bot):
    music_player = MusicPlayer(bot)
    
    @bot.tree.command(name="play", description="Play music from a YouTube URL")
    @app_commands.describe(url="The YouTube URL to play")
    async def play(interaction, url: str):
        await music_player.play(interaction, url)
    
    @bot.tree.command(name="stop", description="Stop the currently playing music and disconnect")
    async def stop(interaction):
        await music_player.stop(interaction)
    
    print("Music commands registered!")