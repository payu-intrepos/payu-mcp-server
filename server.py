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
from typing import Optional

from mcp.server.fastmcp import FastMCP
from tools.invoice_details import get_invoice_details
from tools.payment_link import create_payment_link
from tools.transaction_details import get_transaction_details
from tools.enhanced_transaction_tools import get_transactions_list, get_transactions_summary
from tools.refund_tool import search_refunds, get_refunds_summary
from tools.settlement_details import get_settlement_details


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


# Enhanced Transaction Tools
@mcp.tool()
async def transactions_list(
    date_from: str,
    date_to: str,
    page_offset: int = 0,
    page_limit: int = 10,
    status: str = "",
    mode: str = "",
    payment_source: str = "",
    pa: str = "",
    more_filters: str = "",
    transaction_currency: str = "",
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    offer_applied: Optional[bool] = None
) -> str:
    """
    Get detailed transactions list from PayU.
    
    Args:
        date_from (str): Start date (YYYY-MM-DD HH:MM:SS format) - MANDATORY
        date_to (str): End date (YYYY-MM-DD HH:MM:SS format) - MANDATORY
        page_offset (int): Page offset for pagination (default: 0)
        page_limit (int): Number of records per page (default: 10)
        status (str): Status filter (comma-separated, optional). Valid values: captured, failed, failure, blocked, cancelled, bounced, refundPending, refundSuccess, autoRefund, Auto Refund Initiated, Auto Refunded, in progress, auth, pending, initiated, in-progress, in_progress, Authorized, userCancelled, dropped, refundFailed, Cancelled
        mode (str): Payment mode filter (comma-separated, optional). Valid values: CC, EMI, UPI, enach, SBQR, ADHR, DBT, UPICC, UPICLI, UPIOTM, DC, CASH, CHALLANPAYMENTS, PAYPAL, ISBQR, QR, NEFTRTGS, UPIPPI, CLW, OLW, UPICL, SPLITPAY, OFUPI, DBQR, LAZYPAY, payViaApp, COD, CN, NB
        payment_source (str): Payment source filter (comma-separated, optional). Valid values: pg, button, paymentLink, apiIntInvoice, excelPlugin, appPaymentLink, payHandle, appPayHandle, slashPayHandle, webstore, sist, sinst, si_invoice, event, storefront, pos, appItemizedInvoice, itemizedInvoice, sirecurring
        pa (str): Payment aggregator filter (comma-separated, optional). Valid values: PayU, AxisCyber, RazorPay
        more_filters (str): Additional filters (comma-separated, optional). Valid values: ivr, remReattempts, interTxn, mobile, txnOffer, emailInvoice, uniqTxn, domTxn, web, siInvoice, subEMI, chargebackTxn, tpv
        transaction_currency (str): Currency filter (comma-separated, optional). Valid values: USD, AED, AUD, CAD, GBP, OTH
        min_amount (float): Minimum amount filter (optional, must be provided together with max_amount due to PayU API requirement)
        max_amount (float): Maximum amount filter (optional, must be provided together with min_amount due to PayU API requirement)
        offer_applied (bool): Filter by offer applied status (optional)
    
    Returns:
        str: Formatted transactions list
    """
    if not isinstance(date_from, str) or not isinstance(date_to, str):
        return "Invalid date format. Use YYYY-MM-DD HH:MM:SS format."
    
    # Validate amount parameters at server level - PayU API requires both or neither
    if min_amount is not None or max_amount is not None:
        if min_amount is None or max_amount is None:
            return "Both minAmount and maxAmount must be provided together (PayU API requirement)"
        if min_amount >= max_amount:
            return f"minAmount ({min_amount}) must be less than maxAmount ({max_amount})"
    
    try:
        # Convert comma-separated strings to lists
        status_list = [s.strip() for s in status.split(",")] if status else None
        mode_list = [m.strip() for m in mode.split(",")] if mode else None
        payment_source_list = [ps.strip() for ps in payment_source.split(",")] if payment_source else None
        pa_list = [p.strip() for p in pa.split(",")] if pa else None
        more_filters_list = [mf.strip() for mf in more_filters.split(",")] if more_filters else None
        currency_list = [c.strip() for c in transaction_currency.split(",")] if transaction_currency else None
        
        return await get_transactions_list(
            date_from=date_from,
            date_to=date_to,
            page_offset=page_offset,
            page_limit=page_limit,
            status=status_list,
            mode=mode_list,
            payment_source=payment_source_list,
            pa=pa_list,
            more_filters=more_filters_list,
            transaction_currency=currency_list,
            min_amount=min_amount,
            max_amount=max_amount,
            offer_applied=offer_applied
        )
    except Exception as e:
        logger.error(f"Error fetching transactions list: {e}")
        return "Error retrieving transactions list"


@mcp.tool()
async def transactions_summary(
    date_from: str,
    date_to: str,
    status: str = "",
    mode: str = "",
    payment_source: str = "",
    transaction_currency: str = "",
    more_filters: str = "",
    pa: str = "",
    offer_applied: Optional[bool] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None
) -> str:
    """
    Get transactions summary from PayU.
    
    Args:
        date_from (str): Start date (YYYY-MM-DD HH:MM:SS format) - MANDATORY
        date_to (str): End date (YYYY-MM-DD HH:MM:SS format) - MANDATORY
        status (str): Status filter (comma-separated, optional). Valid values: captured, in progress, auth, pending, initiated, in-progress, in_progress, Authorized, userCancelled, failed, failure, blocked, cancelled, autoRefund, Auto Refund Initiated, Auto Refunded, dropped, bounced, refundSuccess, refundFailed, refundPending, Cancelled
        mode (str): Payment mode filter (comma-separated, optional). Valid values: CC, DC, NB, EMI, CASH, COD, CN, UPI, CHALLANPAYMENTS, payViaApp, enach, PAYPAL, LAZYPAY, SBQR, ISBQR, DBQR, ADHR, QR, OFUPI, DBT, NEFTRTGS, SPLITPAY, UPICC, UPIPPI, UPICL, UPICLI, CLW, OLW, UPIOTM
        payment_source (str): Payment source filter (comma-separated, optional). Valid values: pg, button, paymentLink, apiIntInvoice, excelPlugin, appPaymentLink, sirecurring, sist, sinst, si_invoice, payHandle, appPayHandle, slashPayHandle, appItemizedInvoice, itemizedInvoice, event, webstore, pos, storefront
        transaction_currency (str): Currency filter (comma-separated, optional). Valid values: USD, CAD, GBP, AED, AUD, OTH
        more_filters (str): Additional filters (comma-separated, optional). Valid values: ivr, emailInvoice, uniqTxn, remReattempts, txnOffer, domTxn, interTxn, mobile, web, chargebackTxn, subEMI, siInvoice, tpv
        pa (str): Payment aggregator filter (comma-separated, optional). Valid values: RazorPay, AxisCyber, PayU
        offer_applied (bool): Filter by offer applied status (optional)
        min_amount (float): Minimum amount filter (optional, must be provided together with max_amount due to PayU API requirement)
        max_amount (float): Maximum amount filter (optional, must be provided together with min_amount due to PayU API requirement)
    
    Returns:
        str: Formatted transactions summary
    """
    if not isinstance(date_from, str) or not isinstance(date_to, str):
        return "Invalid date format. Use YYYY-MM-DD HH:MM:SS format."
    
    # Validate amount parameters at server level - PayU API requires both or neither
    if min_amount is not None or max_amount is not None:
        if min_amount is None or max_amount is None:
            return "Both minAmount and maxAmount must be provided together (PayU API requirement)"
        if min_amount >= max_amount:
            return f"minAmount ({min_amount}) must be less than maxAmount ({max_amount})"
    
    try:
        # Convert comma-separated strings to lists
        status_list = [s.strip() for s in status.split(",")] if status else None
        mode_list = [m.strip() for m in mode.split(",")] if mode else None
        payment_source_list = [ps.strip() for ps in payment_source.split(",")] if payment_source else None
        currency_list = [c.strip() for c in transaction_currency.split(",")] if transaction_currency else None
        more_filters_list = [mf.strip() for mf in more_filters.split(",")] if more_filters else None
        pa_list = [p.strip() for p in pa.split(",")] if pa else None
        
        return await get_transactions_summary(
            date_from=date_from,
            date_to=date_to,
            status=status_list,
            mode=mode_list,
            payment_source=payment_source_list,
            transaction_currency=currency_list,
            more_filters=more_filters_list,
            pa=pa_list,
            offer_applied=offer_applied,
            min_amount=min_amount,
            max_amount=max_amount
        )
    except Exception as e:
        logger.error(f"Error fetching transactions summary: {e}")
        return "Error retrieving transactions summary"


@mcp.tool()
async def search_refunds_data(
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
    if not isinstance(date_from, str) or not isinstance(date_to, str):
        return "Invalid date format. Use YYYY-MM-DD format."
    
    # Validate status parameter
    if status:
        valid_statuses = ["requested", "success", "failure", "queued", "pending", "user_cancelled"]
        if status not in valid_statuses:
            return f"Invalid status '{status}'. Valid statuses are: {', '.join(valid_statuses)}"
    
    try:
        return await search_refunds(date_from, date_to, page_offset, page_size, status)
    except Exception as e:
        logger.error(f"Error searching refunds: {e}")
        return "Error searching refunds"


@mcp.tool()
async def refunds_summary_data(
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
    if not isinstance(date_from, str) or not isinstance(date_to, str):
        return "Invalid date format. Use YYYY-MM-DD format."
    
    # Validate status parameter
    if status:
        valid_statuses = ["requested", "success", "failure", "queued", "pending", "user_cancelled"]
        if status not in valid_statuses:
            return f"Invalid status '{status}'. Valid statuses are: {', '.join(valid_statuses)}"
    
    try:
        return await get_refunds_summary(date_from, date_to, status)
    except Exception as e:
        logger.error(f"Error fetching refunds summary: {e}")
        return "Error retrieving refunds summary"


@mcp.tool()
async def settlement_details(
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
    if not isinstance(settlement_id, str) or not re.match(r'^[a-zA-Z0-9-_]+$', settlement_id):
        return "Invalid settlement ID format."
    
    try:
        return await get_settlement_details(settlement_id, utr, status, tid)
    except Exception as e:
        logger.error(f"Error fetching settlement details: {e}")
        return "Error retrieving settlement details"


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