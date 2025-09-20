# Discord Showcase Loader

A Python bot that automatically downloads images and videos from Discord channels to your Synology NAS using Download Station.

## Features

- 🤖 **Automatic Detection**: Monitors specified Discord channels for new messages containing images and videos
- 📥 **Smart Downloads**: Automatically downloads media files to your Synology NAS via Download Station
- 🎯 **Multiple Sources**: Supports Discord attachments and common media hosting sites (YouTube, Imgur, etc.)
- 📂 **Organized Storage**: Creates organized folder structure based on channel names
- ✅ **Visual Feedback**: Reacts to messages with emojis to indicate download status
- 🔧 **Configurable**: Easy configuration via environment variables

## Requirements

- Python 3.8+
- Discord bot token
- Synology NAS with Download Station enabled
- Network access between the bot and your NAS

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/RAMOTS/discord-showcase-loader.git
   cd discord-showcase-loader
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create configuration file**:
   ```bash
   cp .env.example .env
   ```

4. **Edit the `.env` file with your settings** (see Configuration section below)

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure the following variables:

#### Discord Settings
- `DISCORD_BOT_TOKEN`: Your Discord bot token (required)
- `DISCORD_CHANNEL_IDS`: Comma-separated list of channel IDs to monitor (required)

#### Synology NAS Settings
- `SYNOLOGY_HOST`: IP address or hostname of your NAS (required)
- `SYNOLOGY_PORT`: Port for DSM (default: 5000 for HTTP, 5001 for HTTPS)
- `SYNOLOGY_USERNAME`: NAS username (required)
- `SYNOLOGY_PASSWORD`: NAS password (required)
- `SYNOLOGY_USE_HTTPS`: Use HTTPS connection (default: false)

#### Download Settings
- `DOWNLOAD_DESTINATION`: Destination folder on NAS (default: downloads/discord-media)

### Example Configuration

```env
# Discord Bot Configuration
DISCORD_BOT_TOKEN=your_discord_bot_token_here
DISCORD_CHANNEL_IDS=123456789012345678,987654321098765432

# Synology NAS Configuration
SYNOLOGY_HOST=192.168.1.100
SYNOLOGY_PORT=5000
SYNOLOGY_USERNAME=your_nas_username
SYNOLOGY_PASSWORD=your_nas_password
SYNOLOGY_USE_HTTPS=false

# Download Configuration
DOWNLOAD_DESTINATION=downloads/discord-media
```

## Setting Up Discord Bot

1. **Create a Discord Application**:
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Click "New Application" and give it a name
   - Go to the "Bot" section
   - Click "Add Bot"
   - Copy the bot token

2. **Configure Bot Permissions**:
   - In the OAuth2 → URL Generator section
   - Select "bot" scope
   - Select these permissions:
     - Read Messages/View Channels
     - Read Message History
     - Add Reactions

3. **Invite Bot to Server**:
   - Use the generated URL to invite the bot to your Discord server
   - Make sure the bot has access to the channels you want to monitor

4. **Get Channel IDs**:
   - Enable Developer Mode in Discord (User Settings → Advanced → Developer Mode)
   - Right-click on channels you want to monitor
   - Click "Copy ID"

## Setting Up Synology NAS

1. **Enable Download Station**:
   - Open DSM on your Synology NAS
   - Go to Package Center
   - Install "Download Station" if not already installed
   - Open Download Station and ensure it's running

2. **Create Download Folders**:
   - The bot will automatically create subfolders based on channel names
   - Ensure the NAS user has write permissions to the destination folder

3. **Network Access**:
   - Ensure the bot can reach your NAS on the network
   - If using Docker, make sure networking is configured properly

## Usage

### Running the Bot

```bash
python discord_showcase_loader.py
```

### Supported Media Types

The bot automatically detects and downloads:

**Images**: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.webp`, `.svg`, `.tiff`, `.ico`

**Videos**: `.mp4`, `.avi`, `.mov`, `.wmv`, `.flv`, `.webm`, `.mkv`, `.m4v`, `.3gp`, `.ogv`

**Supported Sites**:
- Discord attachments
- Direct media file URLs
- YouTube
- Vimeo
- Imgur
- Twitch
- Reddit media

### Visual Feedback

The bot will react to messages with emojis:
- ✅ Download queued successfully
- ❌ Download failed
- ⚠️ Error occurred during processing

### File Organization

Downloaded files are organized as follows:
```
downloads/discord-media/
├── channel-name-1/
│   ├── 20231201_143022_channel-name-1_username_image.jpg
│   └── 20231201_143105_channel-name-1_username_video.mp4
└── channel-name-2/
    └── 20231201_144530_channel-name-2_username_meme.gif
```

## Troubleshooting

### Common Issues

1. **Bot not responding**:
   - Check bot token is correct
   - Ensure bot has proper permissions in Discord
   - Verify channel IDs are correct

2. **NAS connection failed**:
   - Check NAS IP address and port
   - Verify username/password
   - Ensure Download Station is running
   - Check firewall settings

3. **Downloads not starting**:
   - Verify Download Station is enabled
   - Check destination folder permissions
   - Look at bot logs for error messages

### Logging

The bot creates a log file `discord_showcase_loader.log` with detailed information about:
- Bot startup and configuration
- Message processing
- Download attempts
- Errors and warnings

### Testing

To test the setup:
1. Start the bot
2. Post an image or video in a monitored channel
3. Check for emoji reaction on the message
4. Verify download appears in Download Station
5. Check log file for any errors

## Development

### Project Structure

```
discord-showcase-loader/
├── discord_showcase_loader.py  # Main bot script
├── synology_client.py         # Synology API client
├── config.py                  # Configuration management
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

### Adding New Features

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source. Feel free to modify and distribute according to your needs.

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## Support

If you encounter issues:
1. Check the troubleshooting section
2. Review the log files
3. Open an issue on GitHub with detailed information