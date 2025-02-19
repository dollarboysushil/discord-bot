import discord
from discord import app_commands
import asyncio


def tag_loop(bot):


    @bot.tree.command(name="tag_loop", description="Tag a user multiple times with a key")
    @app_commands.describe(
        username="The username of the person you want to tag",
        count="Number of times to tag the user",
        key="Static key for command authorization"
    )
    async def tag_loop(
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
        count = min(count, 9999)

        # Defer response to allow time for multiple tags
        await interaction.response.defer()

        # Tag in a loop with 0.5 second delay
        for _ in range(count):
            await interaction.followup.send(username.mention)
            await asyncio.sleep(0.5)
