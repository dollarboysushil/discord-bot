import discord
from discord import app_commands

def tag_user(bot):
    @bot.tree.command(name="tag", description="Tag a user")
    @app_commands.describe(username="The username of the person you want to tag")
    async def tag(interaction: discord.Interaction, username: discord.Member):
        await interaction.response.send_message(f"Hello {username.mention}!")


