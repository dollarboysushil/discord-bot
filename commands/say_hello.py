import discord
from discord import app_commands



# Slash command to say hello to a specific user

def say_hello(bot):
    @bot.tree.command(name="hello", description="Say hello to a user")
    @app_commands.describe(username="The username of the person you want to greet")
    async def hello(interaction: discord.Interaction, username: discord.Member):
        await interaction.response.send_message(f"Hello {username.mention}!")
