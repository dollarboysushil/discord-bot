# commands/presence_tracker.py

import discord
from discord import app_commands
from discord.ext import commands, tasks
import sqlite3
import datetime
from collections import defaultdict

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

# Activity tracking task that runs every minute
@tasks.loop(minutes=1)
async def track_activities(bot):
    print("Tracking activities...")
    for guild in bot.guilds:
        try:
            for member in guild.members:
                if member.bot:
                    continue  # Skip bots
                
                # Get current activities
                current_activity_names = set()
                if hasattr(member, 'activities') and member.activities:
                    for activity in member.activities:
                        if activity.type == discord.ActivityType.playing or activity.type == discord.ActivityType.listening or activity.type == discord.ActivityType.custom:
                            activity_name = activity.name
                            current_activity_names.add(activity_name)
                            
                            # If this is a new activity, add to current_activities
                            if activity_name not in current_activities[member.id]:
                                current_activities[member.id][activity_name] = datetime.datetime.now()
                                print(f"New activity detected: {member.name} - {activity_name}")
                
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
                        print(f"Activity ended: {member.name} - {activity_name} - Duration: {duration}s")
        
        except Exception as e:
            print(f"Error tracking activities: {e}")

# Function to get activity data from the database
def get_activity_data(user_id, days=1):
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
    
    return results

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

# Register the presence tracker commands
def register_presence_tracker(bot):
    setup_database()
    
    # Define command functions
    async def log_today_cmd(interaction: discord.Interaction):
        await interaction.response.defer()  # Defer response as this might take time
        
        user_id = interaction.user.id
        activities = get_activity_data(user_id, days=1)
        
        if not activities:
            await interaction.followup.send("No activity data recorded for today.")
            return
        
        # Create an embed for the response
        embed = discord.Embed(
            title="Today's Activity Log",
            description=f"Activity summary for {interaction.user.display_name} in the last 24 hours",
            color=discord.Color.blue()
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
        
        await interaction.followup.send(embed=embed)

    async def log_week_cmd(interaction: discord.Interaction):
        await interaction.response.defer()  # Defer response as this might take time
        
        user_id = interaction.user.id
        activities = get_activity_data(user_id, days=7)
        
        if not activities:
            await interaction.followup.send("No activity data recorded for the past week.")
            return
        
        # Create an embed for the response
        embed = discord.Embed(
            title="Weekly Activity Log",
            description=f"Activity summary for {interaction.user.display_name} in the last 7 days",
            color=discord.Color.green()
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
        
        await interaction.followup.send(embed=embed)
    
    # Add commands to the bot
    @bot.tree.command(name="log_today", description="View your activity log for today")
    async def log_today(interaction: discord.Interaction):
        await log_today_cmd(interaction)
    
    @bot.tree.command(name="log_week", description="View your activity log for the past week")
    async def log_week(interaction: discord.Interaction):
        await log_week_cmd(interaction)
    
    # Start tracking activities
    if not track_activities.is_running():
        track_activities.start(bot)
        print("Started tracking activities")
    
    # Add error handlers
    @log_today.error
    async def log_today_error(interaction: discord.Interaction, error):
        print(f"Error in log_today command: {error}")
        await interaction.followup.send(f"An error occurred: {error}")

    @log_week.error
    async def log_week_error(interaction: discord.Interaction, error):
        print(f"Error in log_week command: {error}")
        await interaction.followup.send(f"An error occurred: {error}")
    
    print("Presence tracker commands registered")