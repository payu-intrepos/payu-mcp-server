import json
from typing import Optional
from utils.network import API_BASE, make_request_with_direct_token
from urllib.parse import urlencode


async def search_refunds(
    date_from: str,
    date_to: str,
    page_offset: int = 0,
    page_size: int = 10,
    status: str = ""
) -> str:
    """
    Search refunds in PayU system.
    
    Args:
        date_from (str): Start date (YYYY-MM-DD format)
        date_to (str): End date (YYYY-MM-DD format)
        page_offset (int): Page offset for pagination (default: 0)
        page_size (int): Number of records per page (default: 10)
        status (str): Refund status filter (optional). Valid values: requested, success, failure, queued, pending, user_cancelled
    
    Returns:
        str: Formatted search results
    """
    # Validate status parameter if provided
    if status:
        valid_statuses = ["requested", "success", "failure", "queued", "pending", "user_cancelled"]
        if status not in valid_statuses:
            return json.dumps({
                "error": f"Invalid status '{status}'. Valid statuses are: {', '.join(valid_statuses)}"
            }, indent=2)
    
    params = {
        'dateFrom': date_from,
        'dateTo': date_to,
        'pageOffset': page_offset,
        'pageSize': page_size
    }
    
    if status:
        params['status'] = status
    
    url = f"{API_BASE}/refund/v1/onepayu/search?{urlencode(params)}"
    data = await make_request_with_direct_token(url)
    
    if not data:
        return "Failed to search refunds."
    
    return json.dumps(data, indent=2)


async def get_refunds_summary(
    date_from: str,
    date_to: str,
    status: str = ""
) -> str:
    """
    Get refunds summary from PayU.
    
    Args:
        date_from (str): Start date (YYYY-MM-DD format)
        date_to (str): End date (YYYY-MM-DD format)
        status (str): Status filter (optional). Valid values: requested, success, failure, queued, pending, user_cancelled
    
    Returns:
        str: Formatted refunds summary
    """
    # Validate status parameter if provided
    if status:
        valid_statuses = ["requested", "success", "failure", "queued", "pending", "user_cancelled"]
        if status not in valid_statuses:
            return json.dumps({
                "error": f"Invalid status '{status}'. Valid statuses are: {', '.join(valid_statuses)}"
            }, indent=2)
    
    params = {
        'dateFrom': date_from,
        'dateTo': date_to
    }
    
    if status:
        params['status'] = status
    
    url = f"{API_BASE}/refunds/summary/?{urlencode(params)}"
    data = await make_request_with_direct_token(url)
    
    if not data:
        return "Failed to retrieve refunds summary."
    
    return json.dumps(data, indent=2)
