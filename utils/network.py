import httpx
from typing import Dict, Any, Optional
import logging
import time
from datetime import datetime

from utils.token_manager import PayUTokenManager

# Constants
API_BASE = "https://oneapi.payu.in"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



# Create a single instance of the token manager
tm = PayUTokenManager()

"""
Return the default headers for PayU API requests.

Returns:
    Dict[str, str]: A dictionary containing the required headers for PayU API.
"""
def get_default_headers() -> Dict[str, str]:
    
    headers = {"Accept": "application/json", "mid": tm.mid}
    if tm.access_token and tm.token_type:
        headers["Authorization"] = f"{tm.token_type} {tm.access_token}"
    return headers


"""
Fetch a new token from the PayU API.
Returns True if token refresh was successful, False otherwise.
"""
async def refresh_token() -> bool:
    
    if not tm.client_id or not tm.client_secret:
        logger.error("PayU API credentials not set")
        return False

    logger.info("Refreshing PayU API token")

    token_url = "https://accounts.payu.in/oauth/token"
    payload = {
        'client_id': tm.client_id,
        'client_secret': tm.client_secret,
        'grant_type': 'client_credentials',
        'scope': 'create_payment_links read_transactions read_payment_links read_invoices'
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                token_url,
                headers=headers,
                data=payload
            )
            response.raise_for_status()
            token_data = response.json()

            # Store token data in the token manager
            tm.access_token = token_data.get('access_token')
            tm.token_type = token_data.get('token_type')
            expires_in = token_data.get('expires_in')
            tm.expires_at = int(time.time()) + expires_in

            readable_time = datetime.fromtimestamp(tm.expires_at).strftime('%Y-%m-%d %H:%M:%S')

            # Verify token was set properly
            if tm.access_token:
                # Verify the singleton is working correctly
                if tm.access_token == tm.access_token:
                    logger.info("Token verification successful")
                else:
                    logger.error("Token verification failed - token mismatch!")
            else:
                logger.error("Failed to set access token!")

            return tm.access_token is not None

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error refreshing token: {e.response.status_code} - Error communicating with PayU API")
        return False
    except Exception as e:
        logger.error("Error refreshing token")
        return False

"""
Ensures a valid token is available, refreshing if necessary.
Returns True if a valid token is available, False otherwise.
"""
async def ensure_valid_token() -> bool:
    
    current_time = int(time.time())

    # Check current token status
    if tm.expires_at > 0:
        expiry_time = datetime.fromtimestamp(tm.expires_at).strftime('%Y-%m-%d %H:%M:%S')
    else:
        expiry_time = 'Not set'

    logger.info(f"Token status: exists={tm.access_token is not None}, expires_at={expiry_time}")

    # Check if token is expired or doesn't exist (with 5-minute buffer)
    if not tm.access_token or current_time >= (tm.expires_at - 300):
        logger.info("Token needs refresh, calling refresh_token()")
        return await refresh_token()

    logger.info("Token is valid, no refresh needed")
    return True

"""
Make a request to the PayU API with proper error handling.

Args:
    url (str): API endpoint URL.
    headers (Optional[Dict[str, str]]): Request headers. If None, default headers will be used.
    body (Optional[Dict[str, Any]]): Request body for POST requests.

Returns:
    Optional[Dict[str, Any]]: JSON response from the API or None if request failed.
"""
async def make_request(
        url: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    
    # First check if we have a valid token
    is_valid_token = await ensure_valid_token()

    if is_valid_token:
        # Use provided headers or get default headers after token validation
        # This ensures we have the latest token in our headers
        request_headers = headers if headers is not None else get_default_headers()

        # Verify Authorization header has token
        auth_header = request_headers.get("Authorization", "")
        if auth_header == "":
            # Try to recreate headers with explicit token
            if tm.access_token:
                request_headers["Authorization"] = f"Bearer {tm.access_token}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                if body:
                    response = await client.post(url, headers=request_headers, json=body)
                else:
                    response = await client.get(url, headers=request_headers)

                response.raise_for_status()
                response_data = response.json()
                logger.info(f"Received response with status {response.status_code}")

                return response_data
            except httpx.TimeoutException:
                return None
            except httpx.HTTPStatusError as e:
                return None
            except Exception as e:
                return None
    else:
        logger.error("Failed to obtain valid token")
        return None


"""
Make a request to the PayU API using the AUTH_TOKEN environment variable as bearer token.
This function bypasses the token refresh mechanism and uses the direct token from environment.

Args:
    url (str): API endpoint URL.
    headers (Optional[Dict[str, str]]): Request headers. If None, default headers will be used.
    body (Optional[Dict[str, Any]]): Request body for POST requests.

Returns:
    Optional[Dict[str, Any]]: JSON response from the API or None if request failed.
"""
async def make_request_with_direct_token(
        url: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    
    # Get the direct auth token from environment variable
    if not tm.auth_token:
        logger.error("AUTH_TOKEN environment variable not set")
        return None

    # Use provided headers or create default headers
    request_headers = headers if headers is not None else {"Accept": "application/json"}
    
    # Add merchant ID if available
    if tm.mid:
        request_headers["mid"] = tm.mid
    
    # Add the bearer token from environment variable
    request_headers["Authorization"] = f"Bearer {tm.auth_token}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            if body:
                response = await client.post(url, headers=request_headers, json=body)
            else:
                response = await client.get(url, headers=request_headers)

            response.raise_for_status()
            response_data = response.json()
            logger.info(f"Received response with status {response.status_code}")

            return response_data
        except httpx.TimeoutException:
            logger.error("Request timeout")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Request error: {str(e)}")
            return None
