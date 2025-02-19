import discord
from discord import app_commands
import asyncio


def dm_loop(bot):

    @bot.tree.command(name="dm_loop", description="Tag a user multiple times via DM")
    @app_commands.describe(
        username="The username of the person you want to tag",
        count="Number of times to tag the user",
        key="Static key for command authorization"
    )
    async def dm_loop(
        interaction: discord.Interaction,
        username: discord.Member,
        count: int,
        key: str
    ):
        # Static key for authorization (replace with your desired key)
        STATIC_KEY = "dbs"

        # Validate key
        if key != STATIC_KEY:
            await interaction.response.send_message("Invalid authorization key!", ephemeral=True)
            return

        # Limit count to prevent abuse
        count = min(count, 999)

        # Defer response to allow time for multiple DMs
        await interaction.response.defer(ephemeral=True)

        # Send DMs in a loop with 0.5 second delay
        for _ in range(count):
            try:
                await username.send(f"Tagged by {interaction.user.mention}")
                await asyncio.sleep(0.5)
            except discord.Forbidden:
                await interaction.followup.send(f"Cannot send DM to {username.mention}", ephemeral=True)
                break

        await interaction.followup.send(f"Sent {count} DMs to {username.mention}", ephemeral=True)