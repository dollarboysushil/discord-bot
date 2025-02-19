import discord


# Slash command to respond with "Pong!"
def register_ping_command(bot):
    @bot.tree.command(name="ping", description="Check bot's response time")
    async def ping(interaction: discord.Interaction):
        await interaction.response.send_message('Pong!')