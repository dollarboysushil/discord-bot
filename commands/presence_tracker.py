# commands/presence_tracker.py

import discord
from discord import app_commands
from discord.ext import commands, tasks
import sqlite3
import datetime
from collections import defaultdict
import traceback

# Database file path
DATABASE_FILE = "presence_tracker.db"

# Dictionary to store current activities: {user_id: {activity_name: start_time}}
current_activities = defaultdict(dict)

# Database setup
def setup_database():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    # Create user_activities table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_activities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        activity_name TEXT NOT NULL,
        start_time TIMESTAMP NOT NULL,
        end_time TIMESTAMP,
        duration INTEGER
    )
    ''')
    
    conn.commit()
    conn.close()
    print("Database setup completed")
    
    # Verify the database is accessible
    check_database()

def check_database():
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM user_activities")
        count = cursor.fetchone()[0]
        print(f"Database contains {count} activity records")
        
        if count > 0:
            cursor.execute("SELECT * FROM user_activities ORDER BY id DESC LIMIT 5")
            latest = cursor.fetchall()
            print("Latest records:")
            for record in latest:
                print(f"  {record}")
        
        conn.close()
    except Exception as e:
        print(f"Database check error: {e}")
        traceback.print_exc()

# Activity tracking task that runs every minute
@tasks.loop(seconds=30)  # Check more frequently for debugging
async def track_activities(bot):
    print("\n--- Tracking activities check ---")
    try:
        for guild in bot.guilds:
            print(f"Checking guild: {guild.name} (ID: {guild.id})")
            try:
                for member in guild.members:
                    if member.bot:
                        continue  # Skip bots
                    
                    print(f"Checking member: {member.name} (ID: {member.id})")
                    
                    # Debug: Check if the member object has activities attribute
                    if not hasattr(member, 'activities'):
                        print(f"WARNING: {member.name} doesn't have activities attribute!")
                        continue
                    
                    # Debug: Print all activities
                    if member.activities:
                        print(f"{member.name}'s activities: {[f'{a.type}: {a.name}' for a in member.activities]}")
                    else:
                        print(f"{member.name} has no activities")
                    
                    # Get current activities
                    current_activity_names = set()
                    if member.activities:
                        for activity in member.activities:
                            # Debug all activity types
                            print(f"Activity type: {activity.type}, name: {activity.name}, application ID: {getattr(activity, 'application_id', 'N/A')}")
                            
                            # Check all types of activities (playing, streaming, listening, watching, custom)
                            if activity.type in [
                                discord.ActivityType.playing,
                                discord.ActivityType.streaming,
                                discord.ActivityType.listening,
                                discord.ActivityType.watching,
                                discord.ActivityType.custom
                            ]:
                                activity_name = activity.name
                                current_activity_names.add(activity_name)
                                
                                # If this is a new activity, add to current_activities
                                if activity_name not in current_activities[member.id]:
                                    current_activities[member.id][activity_name] = datetime.datetime.now()
                                    print(f"NEW ACTIVITY: {member.name} - {activity_name}")
                    
                    # Check for ended activities
                    ended_activities = []
                    if member.id in current_activities:
                        for activity_name, start_time in list(current_activities[member.id].items()):
                            if activity_name not in current_activity_names:
                                ended_activities.append((activity_name, start_time))
                        
                        # Update database for ended activities
                        for activity_name, start_time in ended_activities:
                            end_time = datetime.datetime.now()
                            duration = int((end_time - start_time).total_seconds())
                            
                            try:
                                conn = sqlite3.connect(DATABASE_FILE)
                                cursor = conn.cursor()
                                cursor.execute('''
                                INSERT INTO user_activities (user_id, activity_name, start_time, end_time, duration)
                                VALUES (?, ?, ?, ?, ?)
                                ''', (str(member.id), activity_name, start_time, end_time, duration))
                                conn.commit()
                                conn.close()
                                
                                # Remove ended activity from tracking
                                del current_activities[member.id][activity_name]
                                print(f"ENDED ACTIVITY: {member.name} - {activity_name} - Duration: {duration}s")
                            except Exception as e:
                                print(f"Database insert error: {e}")
                                traceback.print_exc()
            
            except Exception as e:
                print(f"Error processing guild {guild.name}: {e}")
                traceback.print_exc()
    except Exception as e:
        print(f"Error in track_activities: {e}")
        traceback.print_exc()

# Function to get activity data from the database
def get_activity_data(user_id, days=1):
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        # Calculate the date for specified days ago
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
        
        # Query for activity data
        cursor.execute('''
        SELECT activity_name, SUM(duration) as total_duration
        FROM user_activities
        WHERE user_id = ? AND start_time >= ?
        GROUP BY activity_name
        ORDER BY total_duration DESC
        ''', (str(user_id), cutoff_date))
        
        results = cursor.fetchall()
        conn.close()
        
        print(f"Query for user {user_id}, days={days}: found {len(results)} activities")
        for activity, duration in results:
            print(f"  {activity}: {duration}s")
        
        return results
    except Exception as e:
        print(f"Error getting activity data: {e}")
        traceback.print_exc()
        return []

# Format seconds into readable time
def format_time(seconds):
    if seconds < 60:
        return f"{seconds} seconds"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''}"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        if minutes == 0:
            return f"{hours} hour{'s' if hours != 1 else ''}"
        return f"{hours} hour{'s' if hours != 1 else ''} {minutes} minute{'s' if minutes != 1 else ''}"

# Handle ongoing activities when the bot shuts down
def save_current_activities():
    current_time = datetime.datetime.now()
    
    try:
        # Save all current activities to database with end time as now
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        for user_id, activities in current_activities.items():
            for activity_name, start_time in activities.items():
                duration = int((current_time - start_time).total_seconds())
                cursor.execute('''
                INSERT INTO user_activities (user_id, activity_name, start_time, end_time, duration)
                VALUES (?, ?, ?, ?, ?)
                ''', (str(user_id), activity_name, start_time, current_time, duration))
        
        conn.commit()
        conn.close()
        print("Saved current activities on shutdown")
    except Exception as e:
        print(f"Error saving current activities: {e}")
        traceback.print_exc()

# Common function to create activity log embeds
async def create_activity_log_embed(user, activities, time_period, color):
    if not activities:
        return None
    
    # Create an embed for the response
    embed = discord.Embed(
        title=f"{time_period} Activity Log",
        description=f"Activity summary for {user.display_name}",
        color=color
    )
    
    # Display all activities
    total_time = 0
    for i, (activity_name, duration) in enumerate(activities):
        total_time += duration
        formatted_time = format_time(duration)
        if i < 3:  # Highlight top 3
            embed.add_field(
                name=f"#{i+1}: {activity_name}",
                value=f"**{formatted_time}**",
                inline=False
            )
        else:
            embed.add_field(
                name=activity_name,
                value=formatted_time,
                inline=True
            )
    
    # Add total time
    embed.set_footer(text=f"Total tracked time: {format_time(total_time)}")
    
    return embed

# Register the presence tracker commands
def register_presence_tracker(bot):
    print("Registering presence tracker...")
    setup_database()
    
    # Add commands to the bot
    @bot.tree.command(name="log_today", description="View your or another user's activity log for today")
    @app_commands.describe(user="The user to view activity log for (leave empty for yourself)")
    async def log_today(interaction: discord.Interaction, user: discord.Member = None):
        await interaction.response.defer()
        
        try:
            # If no user is specified, use the command invoker
            target_user = user if user else interaction.user
            print(f"Running log_today for user: {target_user.name} (ID: {target_user.id})")
            
            # Check permissions if viewing another user's data
            if user and user != interaction.user:
                # Check if the command invoker has appropriate permissions
                if not interaction.user.guild_permissions.administrator and not interaction.user.guild_permissions.manage_guild:
                    await interaction.followup.send("You don't have permission to view another user's activity log.")
                    return
            
            activities = get_activity_data(target_user.id, days=1)
            
            if not activities:
                print(f"No activities found for user {target_user.name}")
                await interaction.followup.send(f"No activity data recorded for {target_user.display_name} today.")
                return
            
            embed = await create_activity_log_embed(
                target_user, 
                activities, 
                "Today's", 
                discord.Color.blue()
            )
            
            if embed:
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(f"No activity data recorded for {target_user.display_name} today.")
        except Exception as e:
            print(f"Error in log_today command: {e}")
            traceback.print_exc()
            await interaction.followup.send(f"An error occurred while processing your request: {e}")

    @bot.tree.command(name="log_week", description="View your or another user's activity log for the past week")
    @app_commands.describe(user="The user to view activity log for (leave empty for yourself)")
    async def log_week(interaction: discord.Interaction, user: discord.Member = None):
        await interaction.response.defer()
        
        try:
            # If no user is specified, use the command invoker
            target_user = user if user else interaction.user
            print(f"Running log_week for user: {target_user.name} (ID: {target_user.id})")
            
            # Check permissions if viewing another user's data
            if user and user != interaction.user:
                # Check if the command invoker has appropriate permissions
                if not interaction.user.guild_permissions.administrator and not interaction.user.guild_permissions.manage_guild:
                    await interaction.followup.send("You don't have permission to view another user's activity log.")
                    return
            
            activities = get_activity_data(target_user.id, days=7)
            
            if not activities:
                print(f"No activities found for user {target_user.name}")
                await interaction.followup.send(f"No activity data recorded for {target_user.display_name} in the past week.")
                return
            
            embed = await create_activity_log_embed(
                target_user, 
                activities, 
                "Weekly", 
                discord.Color.green()
            )
            
            if embed:
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(f"No activity data recorded for {target_user.display_name} in the past week.")
        except Exception as e:
            print(f"Error in log_week command: {e}")
            traceback.print_exc()
            await interaction.followup.send(f"An error occurred while processing your request: {e}")
    
    # Add monthly log command
    @bot.tree.command(name="log_month", description="View your or another user's activity log for the past month")
    @app_commands.describe(user="The user to view activity log for (leave empty for yourself)")
    async def log_month(interaction: discord.Interaction, user: discord.Member = None):
        await interaction.response.defer()
        
        try:
            # If no user is specified, use the command invoker
            target_user = user if user else interaction.user
            print(f"Running log_month for user: {target_user.name} (ID: {target_user.id})")
            
            # Check permissions if viewing another user's data
            if user and user != interaction.user:
                # Check if the command invoker has appropriate permissions
                if not interaction.user.guild_permissions.administrator and not interaction.user.guild_permissions.manage_guild:
                    await interaction.followup.send("You don't have permission to view another user's activity log.")
                    return
            
            activities = get_activity_data(target_user.id, days=30)
            
            if not activities:
                print(f"No activities found for user {target_user.name}")
                await interaction.followup.send(f"No activity data recorded for {target_user.display_name} in the past month.")
                return
            
            embed = await create_activity_log_embed(
                target_user, 
                activities, 
                "Monthly", 
                discord.Color.purple()
            )
            
            if embed:
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(f"No activity data recorded for {target_user.display_name} in the past month.")
        except Exception as e:
            print(f"Error in log_month command: {e}")
            traceback.print_exc()
            await interaction.followup.send(f"An error occurred while processing your request: {e}")
    
    # Add a manual refresh command for debugging
    @bot.tree.command(name="debug_presence", description="Debug presence tracking")
    async def debug_presence(interaction: discord.Interaction):
        await interaction.response.defer()
        
        # Print debug info
        print("\n--- DEBUG INFO ---")
        print(f"Intents: {bot.intents}")
        print(f"Presence intent enabled: {bot.intents.presences}")
        print(f"Members intent enabled: {bot.intents.members}")
        
        # Check database
        check_database()
        
        # Check current activities
        print("Current activities tracking:")
        for user_id, activities in current_activities.items():
            user = bot.get_user(int(user_id))
            username = user.name if user else "Unknown User"
            print(f"  {username} (ID: {user_id}):")
            for activity_name, start_time in activities.items():
                duration = int((datetime.datetime.now() - start_time).total_seconds())
                print(f"    {activity_name} - {format_time(duration)}")
        
        await interaction.followup.send("Debug information has been printed to the console.")
    
    # Start tracking activities
    if not track_activities.is_running():
        track_activities.start(bot)
        print("Started tracking activities")
    else:
        print("Activity tracking is already running")
    
    # Add error handlers
    @log_today.error
    async def log_today_error(interaction: discord.Interaction, error):
        print(f"Error in log_today command: {error}")
        traceback.print_exc()
        await interaction.followup.send(f"An error occurred: {error}")

    @log_week.error
    async def log_week_error(interaction: discord.Interaction, error):
        print(f"Error in log_week command: {error}")
        traceback.print_exc()
        await interaction.followup.send(f"An error occurred: {error}")
        
    @log_month.error
    async def log_month_error(interaction: discord.Interaction, error):
        print(f"Error in log_month command: {error}")
        traceback.print_exc()
        await interaction.followup.send(f"An error occurred: {error}")
    
    print("Presence tracker commands registered")