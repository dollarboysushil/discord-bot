import discord
import asyncio
from discord import app_commands

def drag_loop(bot):
    # Ensure the bot is ready before defining commands
    @bot.event
    async def on_ready():
        print(f'Logged in as {bot.user}')

    @bot.tree.command(name="drag", description="Move a user between two voice channels a given number of times.")
    async def drag(interaction: discord.Interaction, member: discord.Member, vc1: discord.VoiceChannel, vc2: discord.VoiceChannel, times: int):
        # Check if the user has permission to move members
        if not interaction.user.guild_permissions.move_members:
            await interaction.response.send_message("You don't have permission to move members.", ephemeral=True)
            return

        # Ensure the bot has permission to move members in both channels
        if not interaction.guild.me.guild_permissions.move_members:
            await interaction.response.send_message("I don't have permission to move members.", ephemeral=True)
            return

        # Check if the member is in a voice channel
        if not member.voice:
            await interaction.response.send_message(f"{member.mention} is not in a voice channel.", ephemeral=True)
            return

        # Limit the number of times the drag command can be used
        if times < 1 or times > 99999:
            await interaction.response.send_message("Please provide a valid number of times (between 1 and 10).", ephemeral=True)
            return

        # Send an initial response
        await interaction.response.send_message(f"Dragging {member.mention} between {vc1.name} and {vc2.name} {times} times...")

        for _ in range(times):
            try:
                # Move member between the voice channels
                await member.move_to(vc1)
                await asyncio.sleep(0.1)  # Adjust delay as needed
                await member.move_to(vc2)
                await asyncio.sleep(0.1)  # Adjust delay as needed
            except Exception as e:
                await interaction.followup.send(f"An error occurred while dragging {member.mention}: {str(e)}")
                return

        # Send a follow-up message once finished
        await interaction.followup.send(f"Finished dragging {member.mention}!")
