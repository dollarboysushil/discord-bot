import discord
from discord import app_commands
import asyncio
from typing import Dict, Any

# Store active tasks to be able to cancel them
active_tasks = {
    "drag": {},  # Dictionary to track drag tasks by user ID
    "dm": {},    # Dictionary to track DM tasks by user ID
    "tag": {}    # Dictionary to track tag tasks by user ID
}

def register_stop_commands(bot):
    
    @bot.tree.command(name="stop_drag", description="Stop an ongoing drag command")
    async def stop_drag(interaction: discord.Interaction, member: discord.Member):
        # Check if the user has permission to move members
        if not interaction.user.guild_permissions.move_members:
            await interaction.response.send_message("You don't have permission to stop drag commands.", ephemeral=True)
            return
            
        member_id = str(member.id)
        
        if member_id in active_tasks["drag"]:
            active_tasks["drag"][member_id].cancel()
            active_tasks["drag"].pop(member_id, None)
            await interaction.response.send_message(f"Stopped dragging {member.mention}!")
        else:
            await interaction.response.send_message(f"No active drag command found for {member.mention}.", ephemeral=True)
    
    @bot.tree.command(name="stop_dm", description="Stop an ongoing DM loop")
    async def stop_dm(interaction: discord.Interaction, member: discord.Member, key: str):
        # Static key for authorization (must match the one in dm_loop.py)
        STATIC_KEY = "dbs"
        
        # Validate key
        if key != STATIC_KEY:
            await interaction.response.send_message("Invalid authorization key!", ephemeral=True)
            return
            
        member_id = str(member.id)
        
        if member_id in active_tasks["dm"]:
            active_tasks["dm"][member_id].cancel()
            active_tasks["dm"].pop(member_id, None)
            await interaction.response.send_message(f"Stopped DM loop for {member.mention}!", ephemeral=True)
        else:
            await interaction.response.send_message(f"No active DM loop found for {member.mention}.", ephemeral=True)
    
    @bot.tree.command(name="stop_tag", description="Stop an ongoing tag loop")
    async def stop_tag(interaction: discord.Interaction, member: discord.Member, key: str):
        # Static key for authorization (must match the one in tag_loop.py)
        STATIC_KEY = "dbs"
        
        # Validate key
        if key != STATIC_KEY:
            await interaction.response.send_message("Invalid authorization key!", ephemeral=True)
            return
            
        member_id = str(member.id)
        
        if member_id in active_tasks["tag"]:
            active_tasks["tag"][member_id].cancel()
            active_tasks["tag"].pop(member_id, None)
            await interaction.response.send_message(f"Stopped tag loop for {member.mention}!", ephemeral=True)
        else:
            await interaction.response.send_message(f"No active tag loop found for {member.mention}.", ephemeral=True)

# Modified versions of your original loop functions with task tracking

def drag_loop_with_tracking(bot):
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

        # Create a task for the dragging operation
        member_id = str(member.id)
        
        # Cancel any existing task for this member
        if member_id in active_tasks["drag"]:
            active_tasks["drag"][member_id].cancel()
        
        # Define the actual dragging task
        async def drag_task():
            try:
                for _ in range(times):
                    # Check if the task has been cancelled
                    if asyncio.current_task().cancelled():
                        return
                        
                    # Move member between the voice channels
                    await member.move_to(vc1)
                    await asyncio.sleep(0.1)  # Adjust delay as needed
                    
                    # Check again if cancelled
                    if asyncio.current_task().cancelled():
                        return
                        
                    await member.move_to(vc2)
                    await asyncio.sleep(0.1)  # Adjust delay as needed
                
                # Send a follow-up message once finished
                await interaction.followup.send(f"Finished dragging {member.mention}!")
                
                # Remove task from active tasks
                active_tasks["drag"].pop(member_id, None)
            except Exception as e:
                await interaction.followup.send(f"An error occurred while dragging {member.mention}: {str(e)}")
                active_tasks["drag"].pop(member_id, None)
        
        # Create and store the task
        task = asyncio.create_task(drag_task())
        active_tasks["drag"][member_id] = task

def dm_loop_with_tracking(bot):
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
        # Static key for authorization
        STATIC_KEY = "dbs"

        # Validate key
        if key != STATIC_KEY:
            await interaction.response.send_message("Invalid authorization key!", ephemeral=True)
            return

        # Limit count to prevent abuse
        count = min(count, 999)

        # Defer response to allow time for multiple DMs
        await interaction.response.defer(ephemeral=True)
        
        # Create a task for the DM operation
        member_id = str(username.id)
        
        # Cancel any existing task for this member
        if member_id in active_tasks["dm"]:
            active_tasks["dm"][member_id].cancel()
        
        # Define the DM task
        async def dm_task():
            try:
                sent_count = 0
                for _ in range(count):
                    # Check if the task has been cancelled
                    if asyncio.current_task().cancelled():
                        await interaction.followup.send(f"DM loop stopped after sending {sent_count} messages.", ephemeral=True)
                        return
                        
                    try:
                        await username.send(f"Tagged by {interaction.user.mention}")
                        sent_count += 1
                        await asyncio.sleep(0.5)
                    except discord.Forbidden:
                        await interaction.followup.send(f"Cannot send DM to {username.mention}", ephemeral=True)
                        break
                
                await interaction.followup.send(f"Sent {sent_count} DMs to {username.mention}", ephemeral=True)
                
                # Remove task from active tasks
                active_tasks["dm"].pop(member_id, None)
            except Exception as e:
                await interaction.followup.send(f"An error occurred while sending DMs to {username.mention}: {str(e)}", ephemeral=True)
                active_tasks["dm"].pop(member_id, None)
        
        # Create and store the task
        task = asyncio.create_task(dm_task())
        active_tasks["dm"][member_id] = task

def tag_loop_with_tracking(bot):
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
        # Static key for authorization
        STATIC_KEY = "dbs"

        # Validate key
        if key != STATIC_KEY:
            await interaction.response.send_message("Invalid authorization key!", ephemeral=True)
            return

        # Limit count to prevent abuse
        count = min(count, 9999)

        # Defer response to allow time for multiple tags
        await interaction.response.defer()
        
        # Create a task for the tagging operation
        member_id = str(username.id)
        
        # Cancel any existing task for this member
        if member_id in active_tasks["tag"]:
            active_tasks["tag"][member_id].cancel()
        
        # Define the tagging task
        async def tag_task():
            try:
                sent_count = 0
                for _ in range(count):
                    # Check if the task has been cancelled
                    if asyncio.current_task().cancelled():
                        await interaction.followup.send(f"Tag loop stopped after sending {sent_count} tags.")
                        return
                        
                    await interaction.followup.send(username.mention)
                    sent_count += 1
                    await asyncio.sleep(0.5)
                
                # Remove task from active tasks
                active_tasks["tag"].pop(member_id, None)
            except Exception as e:
                await interaction.followup.send(f"An error occurred while tagging {username.mention}: {str(e)}")
                active_tasks["tag"].pop(member_id, None)
        
        # Create and store the task
        task = asyncio.create_task(tag_task())
        active_tasks["tag"][member_id] = task