> [!Caution] > **Notice**: This bot may be susceptible to multiple security risks. It was developed exclusively for private or personal use. **Commercial use is prohibited.**

# Discord Bot

A versatile Discord bot built with Python, designed to enhance your server experience with various commands and utilities.

## Features

- **Announcements**: Send custom announcements to the server (`announce.py`).
- **Nickname Management**: Change or manage user nicknames (`change_nickname.py`).
- **Heartbeat Stats**: Display server heartbeat or uptime statistics (`display_htb_stats.py`).
- **Rank Display**: Show user ranks or levels (`display_rank.py`).
- **DM Loop**: Automate direct messages to users (`dm_loop.py`).
- **Drag Loop**: Execute a drag-related loop functionality (`drag_loop.py`).
- **HTB API**: Integrate with Hack The Box API for server stats or challenges (`htb_api.py`).
- **Key Manager**: Handle API keys or bot configuration securely (`key_manager.py`).
- **Loop Commands**: Run repetitive command sequences (`loops_commands.py`).
- **Music**: Play music or audio in voice channels (`music.py`).
- **Ping**: Check bot latency or server response time (`ping.py`).
- **Presence Tracker**: Monitor and display user presence or activity (`presence_tracker.py`).
- **Say Hello**: Send a greeting message (`say_hello.py`).
- **Speak**: Text-to-speech or voice output functionality (`speak.py`).
- **Stop**: Stop or pause bot operations (`stop.py`).
- **Tag Management**: Create, manage, or display tags (`tag.py`, `tag_loop.py`, `tag_loop.py`, `tag_vc.py`).

### Additional Features

- **Moderation**: Basic moderation tools (e.g., kick, ban, mute).
- **Custom Commands**: Allow server admins to create custom bot commands.
- **Role Management**: Assign or remove roles via commands.
- **Error Handling**: Robust error messages for failed commands.
- **Help Command**: Display available commands and their usage.

## Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/dollarboysushil/discord-bot
   cd discord-bot
   ```

2. **Install Dependencies: Ensure you have Python 3.8+ installed. Then run**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**:

   - Create a .env file in the root directory.
   - Add your Discord bot token:

   ```bash
   DISCORD_TOKEN=your_bot_token_here
   APP_KEY=you_token_from_htb_profile
   ```

   - Install python-dotenv if not included:

   ```bash
   pip install python-dotenv
   ```

4. **Run the Bot**:
   ```bash
   python main.py
   ```

## Usage

- Invite the bot to your server using the OAuth2 URL generated with your bot's client ID (found on the Discord Developer Portal).
- Use commands with slash commands support e.g /ping /drag /announce.

## Contributing

- Fork the repository.
- Create a new branch (git checkout -b feature-name).
- Make your changes and commit (git commit -m "Add feature-name").
- Push to the branch (git push origin feature-name).
- Open a pull request.

## License

- This project is licensed under the MIT License. See the [LICENSE](LICENSE.md) file for details.
