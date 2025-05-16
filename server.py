"""
PayU MCP Server
--------------------------
This MCP Server provides integration with PayU payment gateway APIs.
It provides functionality to retrieve payment details, send payment links,
and perform inquiries on payment invoices.
"""

import re
import sys
import argparse
import logging

from mcp.server.fastmcp import FastMCP
from tools.invoice_details import get_invoice_details
from tools.payment_link import create_payment_link
from tools.transaction_details import get_transaction_details


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("payu-mcp-server")

# Initialize FastMCP server
mcp = FastMCP("payu-mcp-server")


@mcp.tool()
async def invoice_details(invoice_id: str) -> str:
    """
    Get invoice details from PayU API.

    Args:
        invoice_id (str): Invoice ID to query.

    Returns:
        str: Formatted transaction details or error message.
    """
    if not isinstance(invoice_id, str) or not re.match(r'^[a-zA-Z0-9-_]+$', invoice_id):
        return "Invalid invoice ID format."
    try:
        return await get_invoice_details(invoice_id)
    except Exception as e:
        logger.error("Error fetching invoice details")
        return "Error retrieving invoice details"


@mcp.tool()
async def transaction_details(payu_id: str) -> str:
    """
    Get transaction data for a specific PayU ID.

    Args:
        payu_id (str): PayU transaction ID.

    Returns:
        str: Formatted transaction details or error message.
    """
    if not isinstance(payu_id, str) or not re.match(r'^[a-zA-Z0-9-_]+$', payu_id):
        return "Invalid PayU ID format."
    try:
        return await get_transaction_details(payu_id)
    except Exception as e:
        logger.error("Error fetching transaction details")
        return "Error retrieving transaction details"


@mcp.tool()
async def payment_link(
    amount: float,
    description: str,
    name: str = "",
    phone: str = "",
    email: str = ""
) -> str:
    """
    Send payment link to a customer.

    Args:
        amount (float): Payment amount.
        description (str): Payment description.
        name (str, optional): Customer name.
        phone (str, optional): Customer phone number.
        email (str, optional): Customer email address.

    Returns:
        str: Formatted payment link details or error message.
    """
    # Input validation
    if not isinstance(amount, (int, float)) or amount <= 0:
        return "Invalid amount."

    if not isinstance(description, str) or not description.strip():
        return "Invalid description."

    if name and (not isinstance(name, str) or not re.match(r'^[\w\s-]+$', name)):
        return "Invalid name format."

    if phone and (not isinstance(phone, str) or not re.match(r'^\+?[1-9]\d{1,14}$', phone)):
        return "Invalid phone format."

    if email and (
        not isinstance(email, str) or
        not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email)
    ):
        return "Invalid email format."

    try:
        return await create_payment_link(amount, description, name, phone, email)
    except Exception as e:
        logger.error(f"Error creating payment link: {e}")
        return f"Error creating payment link: {str(e)}"


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='A Model Context Protocol (MCP) server for PayU integration'
    )
    parser.add_argument('--sse', action='store_true', help='Use SSE transport')
    parser.add_argument('--port', type=int, default=8888, help='Port to run the server on')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')

    return parser.parse_args()


# Define main function for running the server
def main():
    """Run the MCP server."""
    args = parse_arguments()

    # Configure debug logging if requested
    if args.debug:
        logger.debug("Debug logging enabled")

    # Set server port
    mcp.settings.port = args.port

    try:
        # Run server with appropriate transport
        if args.sse:
            mcp.run(transport='sse')
        else:
            mcp.run()
    except Exception as e:
        logger.critical(f"Failed to start server")
        sys.exit(1)


# Use main as entry point
if __name__ == "__main__":
    main()