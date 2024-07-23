# Discord Advertisement Bot

This Discord bot allows users to create and schedule advertisements within Discord servers. It provides an interactive interface for creating ads, supports image attachments, and includes role-based permissions for ad creation.

## Features

- Create advertisements with customizable titles and descriptions
- Schedule advertisements for future posting
- Support for multiple image attachments per advertisement
- Role-based permission system for ad creation
- Interactive channel selection interface
- Pastel color framing for attached images

## Prerequisites

- Python 3.8 or higher
- discord.py library
- Pillow library for image processing

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/discord-ad-bot.git
   cd discord-ad-bot
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `config.json` file in the root directory with your Discord bot token:
   ```json
   {
     "TOKEN": "your_discord_bot_token_here"
   }
   ```

## Configuration

1. Open `main.py` and locate the `AUTHORIZED_ROLE_IDS` list.
2. Add the role IDs that should have permission to create ads:
   ```python
   AUTHORIZED_ROLE_IDS = [1219669909366116463, 1234567890123456789]  # Add more role IDs as needed
   ```

## Usage

1. Start the bot:
   ```
   python main.py
   ```

2. In Discord, use the `/create_ad` command to open the ad creation interface.

3. Follow the prompts to:
   - Select a channel for the ad
   - Enter the ad title and details
   - Attach images (optional)

4. The bot will post the ad in the selected channel or schedule it for future posting.

## Commands

- `/create_ad`: Opens the interface to create a new advertisement
- `/remove_command <command_name>`: Removes a specified slash command (admin only)

## Scheduling Advertisements

To schedule an ad for future posting:

1. Use the `/create_ad` command.
2. In the scheduling form, specify the date and time for the ad to be posted.
3. The bot will automatically post the ad at the scheduled time.

## Permissions

Only users with roles specified in `AUTHORIZED_ROLE_IDS` can use the `/create_ad` command. Ensure that your bot has the necessary permissions in the Discord server, including:

- Send Messages
- Embed Links
- Attach Files
- Add Reactions
- Use External Emojis
- Manage Messages (for removing reactions)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions, please open an issue on the GitHub repository.