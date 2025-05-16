from utils.network import API_BASE, get_default_headers,make_request

def parse_to_string(data):
    output = []

    # Add the top-level information
    output.append(f"API Status: {data['status']}")
    output.append(f"Message: {data['message']}")
    output.append(f"Code: {data['code']}")

    # Parse the result section
    result = data['result']
    output.append("\nTRANSACTION DETAILS:")
    output.append(f"Payment ID: {result['paymentId']}")
    output.append(f"Merchant Transaction ID: {result['merchantTransactionId']}")
    output.append(f"Status: {result['status']}")
    output.append(f"Transaction Date/Time: {result['transactionDateTime']}")
    output.append(f"Transaction Source: {result['transactionSource']}")
    output.append(f"Amount: {result['amount']}")
    output.append(f"Amount Left For Refund: {result['amountLeftForRefund'] or 'None'}")
    output.append(f"Product Info: {result['productInfo']}")

    # Payment details
    payment_details = result['paymentDetails']
    output.append("\nPAYMENT DETAILS:")
    output.append(f"Mode: {payment_details['mode']}")
    output.append(f"Bank Reference Number: {payment_details['bankRefNo']}")

    # Amount breakup
    output.append(f"\nAmount Breakup: {result['amountBreakup'] or 'None'}")
    output.append(f"Settlement Details: {result['settlementDetails'] or 'None'}")

    # Customer information
    customer = result['customer']
    output.append("\nCUSTOMER INFORMATION:")
    output.append(f"Name: {customer['name']}")

    # Timeline
    output.append(f"\nTimeline: {result['timeLine'] or 'None'}")

    # Additional customer fields
    if result['customerAdditionalFields']:
        output.append("\nADDITIONAL CUSTOMER FIELDS:")
        for key, value in result['customerAdditionalFields'].items():
            output.append(f"{key}: {value}")

    # Other details
    output.append(f"\nIs POS Transaction: {result['isPosTransaction']}")
    output.append(f"Splits: {result['splits']}")
    output.append(f"Split Payments: {result['splitPayments'] or 'None'}")
    output.append(f"Offer Details: {result['offerDetails'] or 'None'}")
    output.append(f"Device Info: {result['deviceInfo']}")
    output.append(f"Rule Description: {result['ruleDescription']}")
    output.append(f"Additional Charges: {result['additionalCharges'] or 'None'}")

    # Actions taken
    actions = result['actionsTakenDetail']
    output.append("\nACTIONS TAKEN:")
    output.append(f"Transaction Update Data List: {actions['txnUpdateDataList']}")
    output.append(f"Count: {actions['count']}")

    # Remaining fields
    output.append(f"\nAmount in INR: {result['amountInInr'] or 'None'}")
    output.append(f"MCP Info: {result['mcpInfo'] or 'None'}")
    output.append(f"Offer Activity Details: {result['offerActivityDetails'] or 'None'}")
    output.append(f"Discount: {result['discount']}")
    output.append(f"EMI Conversion: {result['emiConversion'] or 'None'}")
    output.append(f"POS Transaction: {result['posTransaction']}")
    output.append(f"PA Name: {result['pa_name'] or 'None'}")

    return "\n".join(output)


# Example usage with the provided JSON data
async def get_transaction_details(payu_id: str) -> str:
    url = f"{API_BASE}/transactions/{payu_id}"
    data = await make_request(url, get_default_headers())

    if not data:
        return "Failed to retrieve transaction details. Please check the PayU ID and try again."

    # Check if result exists in the response before parsing
    if 'result' in data:
       # Parse and format transaction data
        transaction = parse_to_string(data)
        return transaction
    else:
        # Return basic information without full parsing
        return f"API Status: {data.get('status', 'N/A')}\nMessage: {data.get('message', 'N/A')}\nCode: {data.get('code', 'N/A')}\n\nNo transaction details available."
