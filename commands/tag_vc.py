
import discord
from discord import app_commands

def tag_vc(bot):
    @bot.tree.command(name="tag_vc", description="Tag everyone in a specific voice channel")
    @app_commands.describe(channel="The voice channel where you want to tag everyone")
    async def tag_vc(interaction: discord.Interaction, channel: discord.VoiceChannel):
        members = channel.members
        if not members:
            await interaction.response.send_message(f"No one is in the voice channel {channel.name}.")
        else:
            mentions = " ".join([member.mention for member in members])
            await interaction.response.send_message(f"Tagging everyone in {channel.name}: {mentions}")

# Slash command to tag everyone in a specific voice channel
