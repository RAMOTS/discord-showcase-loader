"""
Synology Download Station API client for managing downloads.
"""
import requests
import logging
from typing import Optional, Dict, Any
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class SynologyDownloadStation:
    """Client for interacting with Synology Download Station API."""
    
    def __init__(self, host: str, port: int = 5000, use_https: bool = False,
                 username: str = "", password: str = ""):
        """
        Initialize the Synology Download Station client.
        
        Args:
            host: NAS hostname or IP address
            port: NAS port (default 5000 for HTTP, 5001 for HTTPS)
            use_https: Whether to use HTTPS
            username: NAS username
            password: NAS password
        """
        self.host = host
        self.port = port
        self.use_https = use_https
        self.username = username
        self.password = password
        self.session_id: Optional[str] = None
        
        protocol = "https" if use_https else "http"
        self.base_url = f"{protocol}://{host}:{port}"
        self.api_url = urljoin(self.base_url, "/webapi/")
        
        # Disable SSL warnings if using HTTPS without proper certificates
        if use_https:
            requests.packages.urllib3.disable_warnings()
    
    async def login(self) -> bool:
        """
        Login to the Synology NAS and obtain a session ID.
        
        Returns:
            True if login successful, False otherwise
        """
        login_url = urljoin(self.api_url, "auth.cgi")
        
        params = {
            "api": "SYNO.API.Auth",
            "version": "3",
            "method": "login",
            "account": self.username,
            "passwd": self.password,
            "session": "DownloadStation",
            "format": "cookie"
        }
        
        try:
            response = requests.get(login_url, params=params, verify=False, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get("success"):
                self.session_id = response.cookies.get("id")
                logger.info("Successfully logged in to Synology NAS")
                return True
            else:
                logger.error(f"Login failed: {data.get('error', {})}")
                return False
                
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return False
    
    async def logout(self) -> bool:
        """
        Logout from the Synology NAS.
        
        Returns:
            True if logout successful, False otherwise
        """
        if not self.session_id:
            return True
            
        logout_url = urljoin(self.api_url, "auth.cgi")
        
        params = {
            "api": "SYNO.API.Auth",
            "version": "3",
            "method": "logout",
            "session": "DownloadStation"
        }
        
        try:
            response = requests.get(logout_url, params=params, verify=False, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get("success"):
                logger.info("Successfully logged out from Synology NAS")
                self.session_id = None
                return True
            else:
                logger.error(f"Logout failed: {data.get('error', {})}")
                return False
                
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return False
    
    async def create_download_task(self, url: str, destination: str = "") -> bool:
        """
        Create a download task in Download Station.
        
        Args:
            url: URL of the file to download
            destination: Destination folder (optional)
            
        Returns:
            True if task created successfully, False otherwise
        """
        if not self.session_id:
            logger.error("Not logged in to Synology NAS")
            return False
        
        download_url = urljoin(self.api_url, "DownloadStation/task.cgi")
        
        # Use POST data instead of GET parameters for task creation
        # This prevents 403 Forbidden errors that occur with GET requests
        data = {
            "api": "SYNO.DownloadStation.Task",
            "version": "1",
            "method": "create",
            "uri": url
        }
        
        if destination:
            data["destination"] = destination
        
        cookies = {"id": self.session_id}
        
        try:
            # Use POST instead of GET for task creation operations
            response = requests.post(download_url, data=data, cookies=cookies, 
                                   verify=False, timeout=10)
            response.raise_for_status()
            
            response_data = response.json()
            if response_data.get("success"):
                logger.info(f"Successfully created download task for: {url}")
                return True
            else:
                error_info = response_data.get("error", {})
                error_code = error_info.get("code")
                
                # Handle specific error codes for better debugging
                if error_code == 403:
                    logger.error(f"Access denied (403) - check permissions and session validity")
                elif error_code == 119:
                    logger.error(f"Session expired (119) - attempting to re-login")
                    # Try to re-login and retry once
                    if await self.login():
                        return await self.create_download_task(url, destination)
                else:
                    logger.error(f"Failed to create download task: {error_info}")
                return False
                
        except Exception as e:
            logger.error(f"Download task creation error: {str(e)}")
            return False
    
    async def get_task_list(self) -> Optional[Dict[str, Any]]:
        """
        Get list of download tasks.
        
        Returns:
            Task list data if successful, None otherwise
        """
        if not self.session_id:
            logger.error("Not logged in to Synology NAS")
            return None
        
        task_url = urljoin(self.api_url, "DownloadStation/task.cgi")
        
        params = {
            "api": "SYNO.DownloadStation.Task",
            "version": "1",
            "method": "list"
        }
        
        cookies = {"id": self.session_id}
        
        try:
            response = requests.get(task_url, params=params, cookies=cookies, 
                                  verify=False, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get("success"):
                return data.get("data", {})
            else:
                logger.error(f"Failed to get task list: {data.get('error', {})}")
                return None
                
        except Exception as e:
            logger.error(f"Task list retrieval error: {str(e)}")
            return None