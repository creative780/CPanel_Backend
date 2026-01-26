"""
Service for interacting with Matrix (Synapse) Admin API
"""
import requests
import logging
from typing import Optional, Dict, Any
from django.conf import settings

logger = logging.getLogger(__name__)


class MatrixService:
    """Service for Matrix/Synapse Admin API operations"""
    
    def __init__(self):
        self.base_url = getattr(settings, 'MATRIX_BASE_URL', 'http://synapse:8008')
        self.server_name = getattr(settings, 'MATRIX_SERVER_NAME', 'chat.local')
        self.admin_token = getattr(settings, 'MATRIX_ADMIN_ACCESS_TOKEN', None)
        
        if not self.admin_token:
            logger.warning("MATRIX_ADMIN_ACCESS_TOKEN not set - Matrix operations will fail")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for Admin API requests"""
        return {
            'Authorization': f'Bearer {self.admin_token}',
            'Content-Type': 'application/json',
        }
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Optional[Dict]:
        """Make a request to the Matrix Admin API"""
        if not self.admin_token:
            logger.error("Cannot make Matrix API request: MATRIX_ADMIN_ACCESS_TOKEN not configured")
            return None
        
        # Admin API v2 endpoints use /_synapse/admin/v2, v1 endpoints use /_synapse/admin/v1
        # Check if endpoint starts with /v2 or /v1 to determine the base path
        if endpoint.startswith('/v2'):
            url = f"{self.base_url}/_synapse/admin{endpoint}"
        elif endpoint.startswith('/v1'):
            url = f"{self.base_url}/_synapse/admin{endpoint}"
        else:
            # Default to v1 for backward compatibility
            url = f"{self.base_url}/_synapse/admin/v1{endpoint}"
        headers = self._get_headers()
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=10)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=headers, json=data, timeout=10)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)
            else:
                logger.error(f"Unsupported HTTP method: {method}")
                return None
            
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.RequestException as e:
            logger.error(f"Matrix API request failed: {method} {endpoint} - {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    logger.error(f"Error response: {error_data}")
                except:
                    logger.error(f"Error response text: {e.response.text}")
            return None
    
    def create_user(self, username: str, password: Optional[str] = None, display_name: Optional[str] = None, admin: bool = False) -> Optional[Dict]:
        """
        Create a Matrix user via Registration API (using shared secret)
        
        Returns:
            Dict with 'user_id' and optionally 'access_token' and 'password'
        """
        """
        Create a Matrix user via Registration API (using shared secret)
        
        Args:
            username: Username (without @ and server name)
            password: Optional password (if not provided, user will need to reset password)
            display_name: Optional display name
            admin: Whether user should be admin
        
        Returns:
            User info dict or None on error
        """
        user_id = f"@{username.lower()}:{self.server_name}"
        
        # Check if user already exists
        # Note: get_user requires Admin API which we don't have working
        # So we'll try to register and handle "already exists" error
        
        # Use registration API with shared secret (simpler than Admin API)
        from django.conf import settings
        shared_secret = getattr(settings, 'MATRIX_SHARED_SECRET', None)
        if not shared_secret:
            logger.error("MATRIX_SHARED_SECRET not configured - cannot create users")
            return None
        
        # Generate a password if not provided (store it so we can use it for login later)
        if not password:
            import secrets
            password = secrets.token_urlsafe(16)
        
        # Register user via /_matrix/client/v3/register endpoint
        # Matrix requires a two-step registration flow with shared secret
        register_url = f"{self.base_url}/_matrix/client/v3/register"
        
        # Step 1: Request registration (get session) with retry logic for rate limiting
        max_retries = 3
        retry_count = 0
        import time
        
        while retry_count < max_retries:
            try:
                step1_response = requests.post(
                    register_url,
                    json={'username': username.lower(), 'password': password},
                    timeout=10
                )
            
                # Handle rate limiting (429) - retry with backoff
                if step1_response.status_code == 429:
                    error_data = step1_response.json() if step1_response.content else {}
                    retry_after_ms = error_data.get('retry_after_ms', 2000)
                    retry_count += 1
                    if retry_count < max_retries:
                        logger.warning(f"Rate limited, waiting {retry_after_ms/1000:.1f}s before retry {retry_count}/{max_retries}")
                        time.sleep(retry_after_ms / 1000.0)
                        continue
                    else:
                        logger.error(f"Registration failed after {max_retries} retries due to rate limiting")
                        return None
                
                # If successful on first try (no auth required), we're done
                if step1_response.status_code == 200:
                    result = step1_response.json()
                    logger.info(f"Created Matrix user via registration API: {user_id}")
                    if display_name:
                        self.update_user_display_name(user_id, display_name)
                    return {
                        'user_id': user_id,
                        'access_token': result.get('access_token'),
                        'password': password  # Store password for later token creation
                    }
                
                # Check if user already exists (400 with M_USER_IN_USE)
                if step1_response.status_code == 400:
                    error_data = step1_response.json() if step1_response.content else {}
                    error_msg = error_data.get('error', '').lower()
                    if 'already' in error_msg or 'in use' in error_msg or 'taken' in error_msg:
                        logger.info(f"Matrix user {user_id} already exists")
                        # Return user info with password so caller can try to login
                        return {'user_id': user_id, 'password': password}
                    else:
                        logger.error(f"Registration failed: {step1_response.status_code} - {step1_response.text}")
                        return None
                
                # If we get a 401, we need to complete the auth flow
                if step1_response.status_code == 401:
                    session_data = step1_response.json()
                    session_id = session_data.get('session')
                    flows = session_data.get('flows', [])
                    
                    # Find available auth flow (should be m.login.dummy with shared secret enabled)
                    auth_flow = None
                    for flow in flows:
                        stages = flow.get('stages', [])
                        if 'm.login.dummy' in stages or 'm.login.shared_secret' in stages:
                            auth_flow = flow
                            break
                    
                    if session_id and auth_flow:
                        # Step 2: Complete registration
                        # Use dummy auth since that's what's available
                        step2_data = {
                            'username': username.lower(),
                            'password': password,
                            'auth': {
                                'type': 'm.login.dummy',
                                'session': session_id
                            },
                            'initial_device_display_name': 'CRM Client'
                        }
                        
                        step2_response = requests.post(register_url, json=step2_data, timeout=10)
                        if step2_response.status_code == 200:
                            result = step2_response.json()
                            logger.info(f"Created Matrix user via registration API: {user_id}")
                            if display_name:
                                self.update_user_display_name(user_id, display_name)
                            # Return user info including password so we can use it for token creation
                            return {
                                'user_id': user_id,
                                'access_token': result.get('access_token'),
                                'password': password  # Store password for later token creation
                            }
                        else:
                            logger.error(f"Step 2 registration failed: {step2_response.status_code} - {step2_response.text}")
                            return None
                    else:
                        logger.error(f"No shared secret flow found. Available flows: {flows}")
                        return None
                
                # Other status codes - no retry
                logger.error(f"Registration failed: {step1_response.status_code} - {step1_response.text}")
                return None
                
            except requests.exceptions.RequestException as e:
                retry_count += 1
                if retry_count < max_retries:
                    logger.warning(f"Request error, retrying ({retry_count}/{max_retries}): {e}")
                    time.sleep(1)
                    continue
                else:
                    logger.error(f"Error registering Matrix user {user_id} after {max_retries} retries: {e}")
                    return None
        
        return None
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """
        Get Matrix user info
        
        Args:
            user_id: Full Matrix user ID (e.g. @username:chat.local)
        
        Returns:
            User info dict or None if not found
        """
        # URL encode the user_id
        import urllib.parse
        encoded_user_id = urllib.parse.quote(user_id, safe='')
        result = self._make_request('GET', f'/v2/users/{encoded_user_id}')
        return result
    
    def create_access_token(self, user_id: str, device_id: Optional[str] = None, password: Optional[str] = None) -> Optional[str]:
        """
        Create an access token for a Matrix user via Client-Server API login
        
        Args:
            user_id: Full Matrix user ID
            device_id: Optional device ID
            password: User password (required for login)
        
        Returns:
            Access token string or None on error
        """
        # Use Client-Server API login endpoint instead of Admin API
        login_url = f"{self.base_url}/_matrix/client/v3/login"
        
        login_data = {
            'type': 'm.login.password',
            'identifier': {
                'type': 'm.id.user',
                'user': user_id
            }
        }
        
        if password:
            login_data['password'] = password
        else:
            # If no password provided, we can't login - return None
            logger.warning(f"Cannot create access token for {user_id} without password")
            return None
        
        if device_id:
            login_data['device_id'] = device_id
        else:
            login_data['initial_device_display_name'] = 'CRM Client'
        
        try:
            response = requests.post(login_url, json=login_data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                return result.get('access_token')
            else:
                logger.error(f"Failed to login user {user_id}: {response.status_code} - {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error logging in Matrix user {user_id}: {e}")
            return None
    
    def deactivate_user(self, user_id: str, erase: bool = False) -> bool:
        """
        Deactivate a Matrix user
        
        Args:
            user_id: Full Matrix user ID
            erase: Whether to erase user data
        
        Returns:
            True if successful, False otherwise
        """
        import urllib.parse
        encoded_user_id = urllib.parse.quote(user_id, safe='')
        data = {'erase': erase}
        result = self._make_request('POST', f'/v1/deactivate/{encoded_user_id}', data)
        return result is not None
    
    def update_user_display_name(self, user_id: str, display_name: str) -> bool:
        """
        Update user display name
        
        Args:
            user_id: Full Matrix user ID
            display_name: New display name
        
        Returns:
            True if successful, False otherwise
        """
        # Try to update via Admin API first, but don't fail if it doesn't work
        # (display name can be updated later by the user themselves)
        if not self.admin_token:
            logger.debug(f"Admin token not available, skipping display name update for {user_id}")
            return False
        
        try:
            import urllib.parse
            encoded_user_id = urllib.parse.quote(user_id, safe='')
            data = {'displayname': display_name}
            result = self._make_request('PUT', f'/v2/users/{encoded_user_id}', data)
            return result is not None
        except Exception as e:
            logger.warning(f"Could not update display name for {user_id}: {e} (this is non-critical)")
            return False


# Singleton instance
matrix_service = MatrixService()

