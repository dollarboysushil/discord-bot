import discord
from discord import app_commands
from datetime import datetime, timedelta
import pytz  # pip install pytz
import asyncio

# channel_id -> { "task": asyncio.Task, "message": discord.Message, "target": datetime, "start": datetime }
channel_timers = {}


def format_remaining_time(remaining: timedelta):
    total_seconds = int(remaining.total_seconds())
    if total_seconds <= 0:
        return "0S"

    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    parts = []
    if days:
        parts.append(f"{days}D")
    if hours:
        parts.append(f"{hours}H")
    if minutes:
        parts.append(f"{minutes}M")
    parts.append(f"{seconds}S")
    return " ".join(parts)


def progress_bar(start: datetime, target: datetime, length=20):
    total = (target - start).total_seconds()
    remaining = (target - datetime.utcnow()).total_seconds()
    if remaining <= 0:
        filled = length
    else:
        filled = int(((total - remaining) / total) * length)
    empty = length - filled
    return f"{'🟩'*filled}{'⬜'*empty} {int((total-remaining)/total*100)}%"


async def countdown_task(channel_id, target, start, message):
    try:
        while True:
            now = datetime.utcnow()
            remaining = target - now
            if remaining.total_seconds() <= 0:
                embed = discord.Embed(
                    title="✅ Machine Released!",
                    description="The machine is now available.",
                    color=discord.Color.green()
                )
                await message.edit(embed=embed, content=None)
                channel_timers.pop(channel_id, None)
                break

            formatted = format_remaining_time(remaining)
            bar = progress_bar(start, target)

            embed = discord.Embed(
                title="🕒 Machine Countdown",
                description=f"# {formatted}\n{bar}",
                color=discord.Color.blurple()
            )
            await message.edit(embed=embed, content=None)
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        embed = discord.Embed(
            title="⏹ Countdown stopped",
            description="Stopped by Admin.",
            color=discord.Color.red()
        )
        await message.edit(embed=embed, content=None)


def register_box_release_timer(bot):

    @bot.tree.command(name="box_release_timer", description="Start a countdown timer until box release")
    @app_commands.describe(
        date="Optional: Release date in YYYY-MM-DD (e.g., 2025-09-07)",
        time="Release time in HH:MM format (24h)",
        timezone="Time zone (e.g., Asia/Kathmandu, UTC, America/New_York)"
    )
    async def box_release_timer(interaction: discord.Interaction, time: str, timezone: str, date: str = None):
        # Parse time
        try:
            hour, minute = map(int, time.split(":"))
        except ValueError:
            return await interaction.response.send_message("❌ Invalid time format. Use HH:MM (24h).", ephemeral=True)

        # Parse timezone
        try:
            tz = pytz.timezone(timezone)
        except pytz.UnknownTimeZoneError:
            return await interaction.response.send_message("❌ Unknown timezone.", ephemeral=True)

        now_tz = datetime.now(tz)

        # Parse date if provided
        if date:
            try:
                year, month, day = map(int, date.split("-"))
                target_tz = tz.localize(
                    datetime(year, month, day, hour, minute, 0))
            except ValueError:
                return await interaction.response.send_message("❌ Invalid date format. Use YYYY-MM-DD.", ephemeral=True)
        else:
            # Fallback to next occurrence of time (current logic)
            target_tz = now_tz.replace(
                hour=hour, minute=minute, second=0, microsecond=0)
            if target_tz <= now_tz:
                target_tz += timedelta(days=7)

        target_utc = target_tz.astimezone(pytz.UTC).replace(tzinfo=None)

        # Stop existing timer if running
        if interaction.channel.id in channel_timers:
            channel_timers[interaction.channel.id]["task"].cancel()

        await interaction.response.send_message("🕒 Machine will release in **calculating...**")
        msg = await interaction.original_response()

        task = asyncio.create_task(countdown_task(
            interaction.channel.id, target_utc, datetime.utcnow(), msg
        ))
        channel_timers[interaction.channel.id] = {
            "task": task, "message": msg, "target": target_utc, "start": datetime.utcnow()
        }

    @bot.tree.command(name="stop_timer", description="Stop the countdown timer in this channel")
    async def stop_timer(interaction: discord.Interaction):
        if interaction.channel.id not in channel_timers:
            return await interaction.response.send_message("⚠️ No active timer found in this channel.", ephemeral=True)

        channel_timers[interaction.channel.id]["task"].cancel()
        del channel_timers[interaction.channel.id]
        await interaction.response.send_message("✅ Countdown stopped for this channel.")
