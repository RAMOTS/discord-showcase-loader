"""
Discord Showcase Loader - Automatically download media from Discord to Synology NAS
"""
import os
import logging
import asyncio
import re
from typing import List, Set
from urllib.parse import urlparse

import discord
from discord.ext import commands

from synology_client import SynologyDownloadStation
from config import Config

# Initialize configuration
config = Config()

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Media file extensions to look for
MEDIA_EXTENSIONS = {
    'images': {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.tiff', '.ico'},
    'videos': {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv', '.m4v', '.3gp', '.ogv'}
}

# URL patterns for common media hosting sites
MEDIA_URL_PATTERNS = [
    r'https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)[\w-]+',
    r'https?://(?:www\.)?vimeo\.com/\d+',
    r'https?://(?:www\.)?twitch\.tv/\w+',
    r'https?://(?:i\.)?imgur\.com/\w+\.(?:jpg|jpeg|png|gif|webp)',
    r'https?://(?:www\.)?reddit\.com/\w+',
    r'https?://(?:cdn\.)?discordapp\.com/attachments/[\w/.-]+',
    r'https?://media\.discordapp\.net/attachments/[\w/.-]+',
]

class DiscordShowcaseLoader(commands.Bot):
    """Discord bot for automatically downloading media to Synology NAS."""
    
    def __init__(self):
        """Initialize the Discord bot."""
        intents = discord.Intents.default()
        intents.message_content = True
        
        super().__init__(command_prefix='!', intents=intents)
        
        self.config = config
        self.synology = SynologyDownloadStation(
            host=config.synology_host,
            port=config.synology_port,
            use_https=config.synology_use_https,
            username=config.synology_username,
            password=config.synology_password
        )
        
        self.processed_messages: Set[int] = set()
        
    async def setup_hook(self):
        """Setup hook called when the bot starts."""
        logger.info("Discord Showcase Loader starting up...")
        
        # Validate configuration
        if not self._validate_config():
            logger.error("Invalid configuration. Please check your environment variables.")
            await self.close()
            return
        
        # Login to Synology NAS
        if not await self.synology.login():
            logger.error("Failed to login to Synology NAS")
            await self.close()
            return
            
        logger.info("Successfully connected to Synology NAS")
        
    def _validate_config(self) -> bool:
        """Validate the configuration."""
        errors = self.config.validate()
        
        if errors:
            for error in errors:
                logger.error(f"Configuration error: {error}")
            return False
            
        return True
    
    async def on_ready(self):
        """Called when the bot is ready."""
        logger.info(f'{self.user} has connected to Discord!')
        logger.info(f'Monitoring channels: {self.config.channel_ids}')
        
    async def on_message(self, message: discord.Message):
        """Handle new messages."""
        # Skip if message is from bot itself
        if message.author == self.user:
            return
            
        # Skip if message is not in monitored channels
        if message.channel.id not in self.config.channel_ids:
            return
            
        # Skip if message was already processed
        if message.id in self.processed_messages:
            return
            
        logger.info(f"Processing message from {message.author} in #{message.channel.name}")
        
        # Mark message as processed
        self.processed_messages.add(message.id)
        
        # Extract media URLs from the message
        media_urls = self._extract_media_urls(message)
        
        if media_urls:
            logger.info(f"Found {len(media_urls)} media URL(s) in message")
            
            # Download each media URL
            for url in media_urls:
                await self._download_media(url, message)
        else:
            logger.debug("No media found in message")
            
    def _extract_media_urls(self, message: discord.Message) -> List[str]:
        """Extract media URLs from a Discord message."""
        media_urls = []
        
        # Check message attachments
        for attachment in message.attachments:
            if self._is_media_file(attachment.filename):
                media_urls.append(attachment.url)
                logger.info(f"Found attachment: {attachment.filename}")
        
        # Check message content for URLs
        if message.content:
            # Find URLs using regex patterns
            for pattern in MEDIA_URL_PATTERNS:
                matches = re.findall(pattern, message.content, re.IGNORECASE)
                media_urls.extend(matches)
            
            # Find direct media file URLs
            url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+\.(?:' + '|'.join(
                ext.lstrip('.') for exts in MEDIA_EXTENSIONS.values() for ext in exts
            ) + r')'
            direct_media_urls = re.findall(url_pattern, message.content, re.IGNORECASE)
            media_urls.extend(direct_media_urls)
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(media_urls))
    
    def _is_media_file(self, filename: str) -> bool:
        """Check if a filename represents a media file."""
        if not filename:
            return False
            
        # Get file extension
        file_ext = os.path.splitext(filename.lower())[1]
        
        # Check against known media extensions
        all_extensions = set()
        for extensions in MEDIA_EXTENSIONS.values():
            all_extensions.update(extensions)
            
        return file_ext in all_extensions
    
    async def _download_media(self, url: str, message: discord.Message):
        """Download media to Synology NAS."""
        try:
            # Create a descriptive filename based on the message
            timestamp = message.created_at.strftime("%Y%m%d_%H%M%S")
            channel_name = message.channel.name.replace(' ', '_')
            author_name = message.author.display_name.replace(' ', '_')
            
            # Extract filename from URL if possible
            parsed_url = urlparse(url)
            original_filename = os.path.basename(parsed_url.path)
            
            if original_filename and '.' in original_filename:
                base_name, ext = os.path.splitext(original_filename)
                filename = f"{timestamp}_{channel_name}_{author_name}_{base_name}{ext}"
            else:
                filename = f"{timestamp}_{channel_name}_{author_name}"
            
            # Create destination path
            destination = f"{self.config.download_destination}/{channel_name}"
            
            # Create download task
            success = await self.synology.create_download_task(url, destination)
            
            if success:
                logger.info(f"Successfully queued download: {url}")
                
                # React to the message to indicate success
                try:
                    await message.add_reaction('✅')
                except discord.HTTPException:
                    logger.warning("Could not add reaction to message")
                    
            else:
                logger.error(f"Failed to queue download: {url}")
                
                # React to the message to indicate failure
                try:
                    await message.add_reaction('❌')
                except discord.HTTPException:
                    logger.warning("Could not add reaction to message")
                    
        except Exception as e:
            logger.error(f"Error downloading media {url}: {str(e)}")
            
            # React to the message to indicate error
            try:
                await message.add_reaction('⚠️')
            except discord.HTTPException:
                logger.warning("Could not add reaction to message")
    
    async def close(self):
        """Clean up when bot is shutting down."""
        logger.info("Shutting down Discord Showcase Loader...")
        
        # Logout from Synology NAS
        if self.synology.session_id:
            await self.synology.logout()
            
        await super().close()


async def main():
    """Main entry point."""
    bot = DiscordShowcaseLoader()
    
    try:
        await bot.start(config.discord_token)
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
    finally:
        if not bot.is_closed():
            await bot.close()


if __name__ == "__main__":
    asyncio.run(main())
