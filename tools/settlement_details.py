import json
from typing import Optional
from utils.network import API_BASE, make_request_with_direct_token
from urllib.parse import urlencode


async def get_settlement_details(
    settlement_id: str,
    utr: str = "",
    status: str = "inprogress",
    tid: str = ""
) -> str:
    """
    Get PayU settlement details by settlement ID.
    
    Args:
        settlement_id (str): Settlement ID
        utr (str): UTR reference (optional)
        status (str): Settlement status (default: "inprogress")
        tid (str): Transaction ID (optional)
    
    Returns:
        str: Formatted settlement details
    """
    params = {
        'utr': utr,
        'settlementId': settlement_id,
        'status': status,
        'tid': tid
    }
    
    url = f"{API_BASE}/settlements/details?{urlencode(params)}"
    data = await make_request_with_direct_token(url)
    
    if not data:
        return "Failed to retrieve settlement details. Please check the settlement ID and try again."
    
    return json.dumps(data, indent=2)