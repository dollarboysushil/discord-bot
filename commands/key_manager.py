import sqlite3
import os
import discord
from discord import app_commands

# Database setup
DB_PATH = 'bot_data.db'

def setup_database():
    """Initialize the database and create tables if they don't exist"""
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create table for server keys
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS server_keys (
            server_id TEXT PRIMARY KEY,
            auth_key TEXT NOT NULL
        )
        ''')
        
        conn.commit()
        conn.close()

def get_server_key(server_id):
    """Get the authorization key for a server, or return default if not set"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT auth_key FROM server_keys WHERE server_id = ?', (str(server_id),))
    result = cursor.fetchone()
    
    conn.close()
    
    # Return the key if found, otherwise return default
    if result:
        return result[0]
    else:
        # Insert the default key
        set_server_key(server_id, "dbs")
        return "dbs"

def set_server_key(server_id, new_key):
    """Set or update the authorization key for a server"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT OR REPLACE INTO server_keys (server_id, auth_key)
    VALUES (?, ?)
    ''', (str(server_id), new_key))
    
    conn.commit()
    conn.close()

def register_key_management(bot):
    """Register the key management commands"""
    
    # Make sure database is set up
    setup_database()
    
    @bot.tree.command(name="reset_key", description="Set a new authorization key for loop commands (Server Owner only)")
    @app_commands.describe(new_key="The new authorization key to use for loop commands")
    async def reset_key(interaction: discord.Interaction, new_key: str):
        # Check if the user is the server owner
        if interaction.user.id != interaction.guild.owner_id:
            await interaction.response.send_message("Only the server owner can reset the authorization key.", ephemeral=True)
            return
        
        # Check if the key meets basic requirements (not empty, no spaces)
        if not new_key or ' ' in new_key:
            await interaction.response.send_message("Invalid key. Key cannot be empty or contain spaces.", ephemeral=True)
            return
        
        # Set the new key
        set_server_key(interaction.guild.id, new_key)
        
        await interaction.response.send_message("Authorization key updated successfully!", ephemeral=True)

    @bot.tree.command(name="check_key", description="Check if you know the current authorization key (no key revealed)")
    @app_commands.describe(key="The key to check")
    async def check_key(interaction: discord.Interaction, key: str):
        # Get the stored key
        stored_key = get_server_key(interaction.guild.id)
        
        if key == stored_key:
            await interaction.response.send_message("Your key is correct!", ephemeral=True)
        else:
            await interaction.response.send_message("Invalid key.", ephemeral=True)