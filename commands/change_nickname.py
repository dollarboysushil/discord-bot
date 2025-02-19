import discord
from discord import app_commands


def change_nickname(bot):


    @bot.tree.command(name="change_nickname", description="Change the bot's nickname on all installed servers.")
    async def change_nickname(interaction: discord.Interaction, new_name: str = None):
        # Check if the user has the 'administrator' permission to use this command
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return

        # Get the bot's user object
        bot_user = interaction.guild.get_member(bot.user.id)
        
        # Define default nickname
        default_nickname = bot.user.name

        # If no new nickname is provided, reset to default
        if new_name is None:
            new_name = default_nickname

        # Iterate over all guilds the bot is a part of
        success_count = 0
        failed_count = 0
        
        for guild in bot.guilds:
            try:
                # Try to change the bot's nickname in each guild
                await guild.me.edit(nick=new_name)
                success_count += 1
            except Exception as e:
                # If there's an error, print the error and count it as a failure
                print(f"Error changing nickname in {guild.name}: {e}")
                failed_count += 1

        # Respond with a message about the result
        await interaction.response.send_message(f"Successfully changed the nickname in {success_count} server(s). Failed in {failed_count} server(s).", ephemeral=True)