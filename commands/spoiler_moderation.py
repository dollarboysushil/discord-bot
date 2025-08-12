import discord
from discord import app_commands
from discord.ext import commands
import re

# Define privileged roles or user IDs
PRIVILEGED_ROLES = ["💲DBS", "Moderator", "Higher Administrator"]
# Role names allowed to use deletec
PRIVILEGED_USERS = [123456789012345678]    # Optional: specific user IDs


def register_spoiler_moderation(bot: commands.Bot):
    @bot.tree.command(name="deletec", description="Delete a spoiler message and warn the sender.")
    @app_commands.describe(message_link="The link to the message you want to delete")
    async def deletec(interaction: discord.Interaction, message_link: str):
        # Permission check
        if not await is_privileged(interaction):
            await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
            return

        try:
            # Extract IDs from message link
            match = re.search(r"channels/(\d+)/(\d+)/(\d+)", message_link)
            if not match:
                await interaction.response.send_message("❌ Invalid message link format.", ephemeral=True)
                return

            guild_id, channel_id, message_id = map(int, match.groups())

            # Ensure command is run in same guild
            if guild_id != interaction.guild.id:
                await interaction.response.send_message("❌ That message is not in this server.", ephemeral=True)
                return

            # Fetch channel and message
            channel = bot.get_channel(channel_id)
            if not channel:
                await interaction.response.send_message("❌ Could not find that channel.", ephemeral=True)
                return

            message = await channel.fetch_message(message_id)

            # Delete the message
            await message.delete()

            # Warn in the same channel
            await channel.send(
                f"⚠️ {message.author.mention}, your message has been removed. "
                "Please use the spoiler tag when sending spoilers.\n"
                "• For text: `||spoiler text||`\n"
                "• For images: Right-click → Mark as Spoiler"
            )

            await interaction.response.send_message("✅ Message deleted and user warned in the channel.", ephemeral=True)

        except discord.NotFound:
            await interaction.response.send_message("❌ Message not found.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to delete that message.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"⚠️ An error occurred: {e}", ephemeral=True)

    @bot.tree.command(name="spoiler_help", description="Learn how to mark messages or images as spoilers.")
    async def spoiler_help(interaction: discord.Interaction):
        help_text = (
            "**How to mark text as a spoiler:**\n"
            "• Wrap your text in `||` like this: `||This is a spoiler||`\n\n"
            "**How to mark an image as a spoiler:**\n"
            "• On desktop: Right-click the image before sending and select 'Mark as Spoiler'.\n"
            "• On mobile: Long-press the image and choose 'Mark as Spoiler'.\n\n"
            "This helps others avoid unwanted spoilers. 🚫👀"
        )
        # Send as public message
        await interaction.response.send_message(help_text, ephemeral=False)


async def is_privileged(interaction: discord.Interaction) -> bool:
    member = interaction.user

    # Allow admins with Administrator permission
    if isinstance(member, discord.Member) and member.guild_permissions.administrator:
        return True

    # Check user ID
    if member.id in PRIVILEGED_USERS:
        return True

    # Check if user has privileged roles
    if any(role.name in PRIVILEGED_ROLES for role in member.roles):
        return True

    return False
