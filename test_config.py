#!/usr/bin/env python3
"""
Configuration validator and test utility for Discord Showcase Loader
"""

import sys
import asyncio
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from synology_client import SynologyDownloadStation


async def test_synology_connection(config: Config) -> bool:
    """Test connection to Synology NAS."""
    print("Testing Synology NAS connection...")
    
    synology = SynologyDownloadStation(
        host=config.synology_host,
        port=config.synology_port,
        use_https=config.synology_use_https,
        username=config.synology_username,
        password=config.synology_password
    )
    
    try:
        # Test login
        login_success = await synology.login()
        if login_success:
            print("✅ Successfully connected to Synology NAS")
            
            # Test getting task list
            tasks = await synology.get_task_list()
            if tasks is not None:
                print("✅ Successfully retrieved download task list")
                print(f"   Current tasks: {len(tasks.get('tasks', []))}")
            else:
                print("⚠️  Could not retrieve task list")
            
            # Logout
            await synology.logout()
            return True
        else:
            print("❌ Failed to connect to Synology NAS")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False


def main():
    """Main test function."""
    print("Discord Showcase Loader - Configuration Test\n")
    
    # Load and validate configuration
    config = Config()
    
    print("Configuration validation:")
    print("=" * 40)
    
    errors = config.validate()
    if errors:
        print("❌ Configuration errors found:")
        for error in errors:
            print(f"   - {error}")
        print("\nPlease fix these issues in your .env file before running the bot.")
        return False
    else:
        print("✅ Configuration is valid")
    
    print(f"\nConfiguration summary:")
    print(f"  Discord Token: {'Set' if config.discord_token else 'Not set'}")
    print(f"  Channel IDs: {config.channel_ids}")
    print(f"  Synology Host: {config.synology_host}:{config.synology_port}")
    print(f"  Synology HTTPS: {config.synology_use_https}")
    print(f"  Download Destination: {config.download_destination}")
    
    # Test Synology connection
    print("\nTesting connections:")
    print("=" * 40)
    
    try:
        synology_success = asyncio.run(test_synology_connection(config))
        if not synology_success:
            return False
    except Exception as e:
        print(f"❌ Synology test failed: {e}")
        return False
    
    print("\n✅ All tests passed! The bot should work correctly.")
    print("\nTo start the bot, run:")
    print("  python discord_showcase_loader.py")
    print("  or")
    print("  python run.py")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)