"""
Configuration management for Discord Showcase Loader
"""
import os
import logging
from typing import List, Optional
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class Config:
    """Configuration management class."""
    
    def __init__(self, env_file: str = ".env"):
        """Initialize configuration from environment variables."""
        # Load environment variables from file
        load_dotenv(env_file)
        
        # Discord configuration
        self.discord_token = os.getenv('DISCORD_BOT_TOKEN')
        self.channel_ids = self._parse_channel_ids(os.getenv('DISCORD_CHANNEL_IDS', ''))
        
        # Synology configuration
        self.synology_host = os.getenv('SYNOLOGY_HOST')
        self.synology_port = int(os.getenv('SYNOLOGY_PORT', 5000))
        self.synology_username = os.getenv('SYNOLOGY_USERNAME')
        self.synology_password = os.getenv('SYNOLOGY_PASSWORD')
        self.synology_use_https = os.getenv('SYNOLOGY_USE_HTTPS', 'false').lower() == 'true'
        
        # Download configuration
        self.download_destination = os.getenv('DOWNLOAD_DESTINATION', 'downloads/discord-media')
        
        # Logging configuration
        self.log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        self.log_file = os.getenv('LOG_FILE', 'discord_showcase_loader.log')
    
    def _parse_channel_ids(self, channel_ids_str: str) -> List[int]:
        """Parse channel IDs from comma-separated string."""
        if not channel_ids_str:
            return []
        
        channel_ids = []
        for id_str in channel_ids_str.split(','):
            id_str = id_str.strip()
            if id_str:
                try:
                    channel_ids.append(int(id_str))
                except ValueError:
                    logger.warning(f"Invalid channel ID: {id_str}")
        
        return channel_ids
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of errors."""
        errors = []
        
        if not self.discord_token:
            errors.append("Missing DISCORD_BOT_TOKEN")
        
        if not self.channel_ids:
            errors.append("Missing or invalid DISCORD_CHANNEL_IDS")
        
        if not self.synology_host:
            errors.append("Missing SYNOLOGY_HOST")
        
        if not self.synology_username:
            errors.append("Missing SYNOLOGY_USERNAME")
        
        if not self.synology_password:
            errors.append("Missing SYNOLOGY_PASSWORD")
        
        if self.synology_port <= 0 or self.synology_port > 65535:
            errors.append("Invalid SYNOLOGY_PORT (must be 1-65535)")
        
        return errors
    
    def is_valid(self) -> bool:
        """Check if configuration is valid."""
        return len(self.validate()) == 0
    
    def __str__(self) -> str:
        """String representation of configuration (without sensitive data)."""
        return f"""Discord Showcase Loader Configuration:
  Discord Token: {'Set' if self.discord_token else 'Not set'}
  Channel IDs: {self.channel_ids}
  Synology Host: {self.synology_host}
  Synology Port: {self.synology_port}
  Synology HTTPS: {self.synology_use_https}
  Synology Username: {'Set' if self.synology_username else 'Not set'}
  Synology Password: {'Set' if self.synology_password else 'Not set'}
  Download Destination: {self.download_destination}
  Log Level: {self.log_level}
  Log File: {self.log_file}"""