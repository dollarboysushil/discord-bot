import discord
from discord import app_commands


def register_hint_rules(bot):
    @bot.tree.command(name="hint_rules", description="Displays the server rules for asking hints.")
    async def hint_rules(interaction: discord.Interaction):
        # Just acknowledge the command without creating an interaction message
        await interaction.response.send_message("✅ Rules posted!", ephemeral=True)

        embed = discord.Embed(
            title="🚨 HINT REQUEST RULES",
            description=(
                "**This server is ONLY for small hints.**\n\n"
                "❗ **No full solutions are allowed.**\n"
                "❗ **Try everything first before asking.**\n"
                "❗ **Repeated hint requests or direct answer requests will result in an immediate ban.**\n\n"
                "We strictly follow **Hack The Box policies** — respect the process and learn by doing."
            ),
            color=discord.Color.red()
        )
        embed.set_footer(text="Failure to follow these rules = instant ban.")
        await interaction.channel.send(embed=embed)
