from utils.network import API_BASE, get_default_headers,make_request
from datetime import datetime, timedelta

"""
Generate date range for API queries.

Args:
    days_back (int): Number of days to look back from today.

Returns:
    tuple: (from_date, to_date) formatted as YYYY-MM-DD strings.
"""
def get_date_range(days_back: int = 30) -> tuple:
    today = datetime.now().strftime("%Y-%m-%d")
    past_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    return past_date, today

"""
Parse a transaction API response and return a dictionary of key transaction details.
Args:
    json_response (dict): The JSON response from the transaction API

Returns:
    dict: A dictionary containing the parsed transaction details
"""


def parse_invoice_response(json_response,invoice_id):

    # Validate overall response status
    if json_response.get("status") != 0 or not json_response.get("result"):
        return {"error": "Invalid response or error in API call"}

    # Extract result and data
    result = json_response.get("result", {})
    data = result.get("data", [])

    # Check if any transaction data exists
    if not data or len(data) == 0:
        return {"error": "No transaction data found"}

    # Format and limit to 5 transactions
    formatted_transactions = []
    for transaction in data[:5]:
        try:
            formatted_trans = {
                "transaction_id": transaction.get("transactionId", "N/A"),
                "date": transaction.get("createdOn", "N/A"),
                "amount": f"₹{transaction.get('settledAmount', 0):.2f}",
                "status": transaction.get("status", "N/A"),
                "reference_id": transaction.get("merchantReferenceId", "N/A"),
                "mode": transaction.get("mode", "N/A")
            }
            formatted_transactions.append(formatted_trans)
        except Exception as e:
            print(f"Error processing transaction")

    # Prepare response with view more link only if total transactions > 5
    response = {
        "transactions": formatted_transactions
    }

    # Add view more link if total transactions exceed 5
    total_rows = result.get("rows", 0)
    response.update({
        "instruction": "Always show the data in a tabular formate with columns - Transaction Id, Date, Amount, Status, Reference Id and Mode"
    })
    import urllib.parse
    # Sanitize invoice_id to prevent XSS vulnerability in the URL
    sanitized_invoice_id = urllib.parse.quote(str(invoice_id))
    response.update({
        "view_more_link": f"For more details, you can view at https://payu.in/business/payment-links/{sanitized_invoice_id}",
    })

    return response

"""
Get invoice details from PayU API.

Args:
    invoice_id (str): Invoice ID to query.

Returns:
    str: Formatted transaction details or error message.
"""
async def get_invoice_details(
        invoice_id: str,
        page_offset: int = 0,
        page_size: int = 10,
        order: str = "asc"
) -> dict:

    try:
        # Generate date range for the query
        from_date, to_date = get_date_range()

        # Construct API URL with date parameters
        url = f"{API_BASE}/payment-links/{invoice_id}/txns?dateFrom={from_date}&dateTo={to_date}&pageOffset={page_offset}&pageSize={page_size}&order={order}"

        # Make API request
        response_data = await make_request(url, get_default_headers())

        # Handle error case
        if not response_data:
            return {
                "status": "error",
                "message": "Unable to retrieve invoice details. Please check the invoice ID and try again."
            }

        # Extract PayU ID from response and get transaction details
        parsed_data = parse_invoice_response(response_data, invoice_id)

        if isinstance(parsed_data, dict):
            if parsed_data.get("error"):
                return {
                    "status": "error",
                    "message": parsed_data["error"]
                }

            if not parsed_data:
                return {
                    "status": "error",
                    "message": "No data found for given PayUID."
                }

            return {
                "status": "success",
                "message": "Invoice details retrieved successfully",
                "data": parsed_data
            }
        else:
            return {
                "status": "error",
                "message": "Failed to parse invoice response"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error retrieving invoice details: {str(e)}"
        }
