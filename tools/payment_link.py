from utils.network import API_BASE, get_default_headers,make_request

from typing import List, Optional
from utils.utils import validate_email,validate_phone,mask_email,mask_phone
class CustomerDetail():
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

class CustomerResponse():
    total_customers: int
    customers: List[CustomerDetail]

async def fetch_customers(search_text):
    import urllib.parse
    # Sanitize the search_text input
    sanitized_search_text = urllib.parse.quote_plus(search_text)
    url = f"{API_BASE}/invoice/customer/customers?searchText={sanitized_search_text}"
    response_data = await make_request(url, get_default_headers())
    if not response_data:
        return []

    return parse_customer_response(response_data)


def parse_customer_response(response):
    """
    Parse customer details from the API response

    Args:
        response (dict): API response dictionary

    Returns:
        list: Parsed customer details
    """
    # Check if response is valid
    if "error" in response:
        return []

    # Extract customer details
    result = response.get("result", {})
    customers = result.get("customerDetails", [])

    # Parse and format customer details
    parsed_customers = [
        {
            "name": customer.get("name"),
            "email": customer.get("email"),
            "phone": customer.get("phone")
        }
        for customer in customers
    ]

    return parsed_customers


async def create_payment_link(
        amount: float,
        description: str,
        name: str = "",
        phone: str = "",
        email: str = ""
) -> str:
    """
    Create a payment link with customer validation

    Args:
        amount (float): Payment amount
        description (str): Payment description
        name (str, optional): Customer name
        phone (str, optional): Customer phone number
        email (str, optional): Customer email

    Returns:
        str: Formatted payment link response or error message
    """
    # Prepare customer details for API call
    customer_details = {
        "name": name,
        "phone": phone,
        "email": email
    }

    # Scenario 1: If email or phone is valid, directly create payment link
    if validate_email(email) or validate_phone(phone):
        return await create_payment_link_request(amount, description, **customer_details)

    # Scenario 2: If both email and phone are not present, but name is present
    if name and not email and not phone:
        # Fetch customers by name
        customer_response = await fetch_customers(name)

        # Handle parsing errors
        if not customer_response:
            # If no customers found, proceed with creating payment link using name
            return await create_payment_link_request(amount, description, **customer_details)

        # Handle multiple customers found
        if len(customer_response) > 1:
            customer_list = "\n".join([
                f"{i + 1}. Name: {c['name']}, "
                f"Email: {mask_email(c['email'])}, "
                f"Phone: {mask_phone(c['phone'])}"
                for i, c in enumerate(customer_response)
            ])
            return f"Multiple customers found ({len(customer_response)} total):\n{customer_list}\n\n Please specify a customer by providing their email or phone number. Instruction: Show full masked email and phone number to end user show that user can understand the relevant information"

        # If exactly one customer found, use their details
        if customer_response:
            customer = customer_response[0]
            customer_details['email'] = customer.get('email', email)
            customer_details['phone'] = customer.get('phone', phone)

    # Create payment link with updated or original customer details
    return await create_payment_link_request(amount, description, **customer_details)


async def create_payment_link_request(
        amount: float,
        description: str,
        name: str = "",
        phone: str = "",
        email: str = ""
) -> str:

    url = f"{API_BASE}/payment-links"
    # Prepare request body
    customer = {
        "email": email,
        "name": name,
        "phone": phone
    }
    request_body = {
        "viaSms": phone != "",  # Send SMS only if phone number is not empty
        "viaEmail": email != "",  # Send email only if email is not empty
        "subAmount": amount,
        "description": description,
        "source": "payment_link_onedash",
        "customer": customer
    }

    # Make API request
    data = await make_request(url, get_default_headers(), request_body)

    # Handle error case
    if not data or "result" not in data:
        return "Failed to create payment link. Please check the inputs and try again."

    # Extract result and format response
    result = data["result"]

    # Build formatted response
    response_parts = [
        f"- name: {name}",
        f"- paymentLink: {result.get('paymentLink', 'No payment link found')}",
        f"- description: {result.get('description', 'No description found')}",
        f"- phone: {mask_phone(phone)}",
        f"- email: {mask_email(email)}",
        f"- invoiceNumber: {result.get('invoiceNumber', 'No invoice number found')}"
    ]

    return "\n".join(response_parts)
