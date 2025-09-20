#!/usr/bin/env python3
"""
Simple runner script for Discord Showcase Loader
"""

import sys
import asyncio
import logging
from pathlib import Path

# Add current directory to path to ensure local imports work
sys.path.insert(0, str(Path(__file__).parent))

from discord_showcase_loader import main

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        sys.exit(1)