import discord
import asyncio
import os
from gtts import gTTS
from discord import app_commands
from dataclasses import dataclass
from collections import deque
from typing import Dict, Deque

@dataclass
class QueueItem:
    text: str
    user_id: int
    interaction: discord.Interaction

class VoiceState:
    def __init__(self):
        self.queue: Deque[QueueItem] = deque()
        self.last_activity: float = 0
        self.is_playing: bool = False
        self.current_item: QueueItem = None

# Store voice states for each guild
guild_states: Dict[int, VoiceState] = {}
TIMEOUT_SECONDS = 180  # 3 minutes

async def process_queue(guild_id: int, voice_client: discord.VoiceClient):
    """Process the speech queue for a guild."""
    state = guild_states[guild_id]

    while voice_client.is_connected():
        if state.queue and not state.is_playing:
            state.is_playing = True
            state.current_item = state.queue.popleft()

            try:
                filename = f"speech_{guild_id}.mp3"
                tts = gTTS(text=state.current_item.text, lang="hi")
                tts.save(filename)

                voice_client.play(
                    discord.FFmpegPCMAudio(filename),
                    after=lambda e: asyncio.run_coroutine_threadsafe(
                        on_playback_finished(guild_id, filename, e),
                        voice_client.loop
                    )
                )

                state.last_activity = asyncio.get_event_loop().time()

                try:
                    await state.current_item.interaction.followup.send(
                        f"Now playing your message: `{state.current_item.text}`",
                        ephemeral=True
                    )
                except discord.errors.NotFound:
                    pass  # Interaction might have expired

            except Exception as e:
                print(f"Error processing queue item: {e}")
                state.is_playing = False
                if os.path.exists(filename):
                    os.remove(filename)

        await asyncio.sleep(0.5)

async def on_playback_finished(guild_id: int, filename: str, error):
    """Callback for when audio playback finishes."""
    if guild_id in guild_states:
        state = guild_states[guild_id]
        state.is_playing = False
        state.current_item = None

    if os.path.exists(filename):
        os.remove(filename)

    if error:
        print(f"Error during playback: {error}")

async def check_activity_timeout(guild_id: int, voice_client: discord.VoiceClient):
    """Monitor voice client activity and disconnect after timeout."""
    while voice_client.is_connected():
        await asyncio.sleep(10)

        if guild_id in guild_states:
            state = guild_states[guild_id]
            time_elapsed = asyncio.get_event_loop().time() - state.last_activity

            if time_elapsed >= TIMEOUT_SECONDS and not state.queue and not state.is_playing:
                await voice_client.disconnect()
                del guild_states[guild_id]
                print(f"Disconnected from guild {guild_id} due to inactivity")
                break

def register_speak_commands(bot):
    """Register the /speak and /queue commands."""

    @bot.tree.command(name="speak", description="Make the bot join VC and speak text")
    @app_commands.describe(text="The word or sentence you want the bot to say")
    async def speak(interaction: discord.Interaction, text: str):
        if not interaction.user.voice:
            await interaction.response.send_message("You need to be in a voice channel.", ephemeral=True)
            return

        voice_channel = interaction.user.voice.channel
        guild_id = interaction.guild_id

        try:
            if guild_id not in guild_states:
                guild_states[guild_id] = VoiceState()

            state = guild_states[guild_id]
            state.last_activity = asyncio.get_event_loop().time()

            if not interaction.guild.voice_client:
                vc = await voice_channel.connect()
                asyncio.create_task(process_queue(guild_id, vc))
                asyncio.create_task(check_activity_timeout(guild_id, vc))
            else:
                vc = interaction.guild.voice_client
                if vc.channel != voice_channel:
                    await vc.move_to(voice_channel)

            queue_position = len(state.queue) + (1 if state.is_playing else 0)
            state.queue.append(QueueItem(text, interaction.user.id, interaction))

            await interaction.response.send_message(
                f"Added to queue (Position: {queue_position})" if queue_position > 0
                else "Processing your request...",
                ephemeral=True
            )

        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    @bot.tree.command(name="queue", description="Show current TTS queue")
    async def show_queue(interaction: discord.Interaction):
        guild_id = interaction.guild_id

        if guild_id not in guild_states or not guild_states[guild_id].queue:
            await interaction.response.send_message("The queue is currently empty.", ephemeral=True)
            return

        state = guild_states[guild_id]
        queue_list = []

        if state.current_item:
            queue_list.append(f"Currently playing: {state.current_item.text}")

        for i, item in enumerate(state.queue, 1):
            user = interaction.guild.get_member(item.user_id)
            username = user.display_name if user else "Unknown User"
            queue_list.append(f"{i}. {username}: {item.text}")

        await interaction.response.send_message(
            "**TTS Queue:**\n" + "\n".join(queue_list),
            ephemeral=True
        )
