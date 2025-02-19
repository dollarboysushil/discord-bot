import discord
from discord import app_commands



def announce(bot):
    

    # Slash command to announce a message to a specific text channel
    @bot.tree.command(name="announce", description="Announce a message to a specific text channel")
    @app_commands.describe(channel="The text channel where you want to send the announcement", message="The announcement message")
    async def announce(interaction: discord.Interaction, channel: discord.TextChannel, message: str):
        # Send the message to the specified text channel
        await channel.send(message)
        await interaction.response.send_message(f"Announcement sent to {channel.mention}!")

