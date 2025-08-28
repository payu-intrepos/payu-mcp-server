import json
from typing import Optional, List
from utils.network import API_BASE, make_request_with_direct_token
from urllib.parse import urlencode


async def get_transactions_list(
    date_from: str,
    date_to: str,
    page_offset: int = 0,
    page_limit: int = 10,
    status: List[str] = None,
    mode: List[str] = None,
    payment_source: List[str] = None,
    pa: List[str] = None,
    more_filters: List[str] = None,
    transaction_currency: List[str] = None,
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
        status (List[str]): Status filter list (optional). Valid values: captured, failed, failure, blocked, cancelled, bounced, refundPending, refundSuccess, autoRefund, Auto Refund Initiated, Auto Refunded, in progress, auth, pending, initiated, in-progress, in_progress, Authorized, userCancelled, dropped, refundFailed, Cancelled
        mode (List[str]): Payment mode filter list (optional). Valid values: CC, EMI, UPI, enach, SBQR, ADHR, DBT, UPICC, UPICLI, UPIOTM, DC, CASH, CHALLANPAYMENTS, PAYPAL, ISBQR, QR, NEFTRTGS, UPIPPI, CLW, OLW, UPICL, SPLITPAY, OFUPI, DBQR, LAZYPAY, payViaApp, COD, CN, NB
        payment_source (List[str]): Payment source filter list (optional). Valid values: pg, button, paymentLink, apiIntInvoice, excelPlugin, appPaymentLink, payHandle, appPayHandle, slashPayHandle, webstore, sist, sinst, si_invoice, event, storefront, pos, appItemizedInvoice, itemizedInvoice, sirecurring
        pa (List[str]): Payment aggregator filter list (optional). Valid values: PayU, AxisCyber, RazorPay
        more_filters (List[str]): Additional filters (optional). Valid values: ivr, remReattempts, interTxn, mobile, txnOffer, emailInvoice, uniqTxn, domTxn, web, siInvoice, subEMI, chargebackTxn, tpv
        transaction_currency (List[str]): Currency filter list (optional). Valid values: USD, AED, AUD, CAD, GBP, OTH
        min_amount (float): Minimum amount filter (optional, must be provided together with max_amount due to PayU API requirement)
        max_amount (float): Maximum amount filter (optional, must be provided together with min_amount due to PayU API requirement)
        offer_applied (bool): Filter by offer applied status (optional)
    
    Returns:
        str: Formatted transactions list
    """
    # Validate status parameter
    if status:
        valid_statuses = [
            "captured", "failed", "failure", "blocked", "cancelled", "bounced", 
            "refundPending", "refundSuccess", "autoRefund", "Auto Refund Initiated", 
            "Auto Refunded", "in progress", "auth", "pending", "initiated", 
            "in-progress", "in_progress", "Authorized", "userCancelled", "dropped", 
            "refundFailed", "Cancelled"
        ]
        for s in status:
            if s not in valid_statuses:
                return json.dumps({
                    "error": f"Invalid status '{s}'. Valid statuses are: {', '.join(valid_statuses)}"
                }, indent=2)
    
    # Validate mode parameter
    if mode:
        valid_modes = [
            "CC", "EMI", "UPI", "enach", "SBQR", "ADHR", "DBT", "UPICC", "UPICLI", 
            "UPIOTM", "DC", "CASH", "CHALLANPAYMENTS", "PAYPAL", "ISBQR", "QR", 
            "NEFTRTGS", "UPIPPI", "CLW", "OLW", "UPICL", "SPLITPAY", "OFUPI", 
            "DBQR", "LAZYPAY", "payViaApp", "COD", "CN", "NB"
        ]
        for m in mode:
            if m not in valid_modes:
                return json.dumps({
                    "error": f"Invalid mode '{m}'. Valid modes are: {', '.join(valid_modes)}"
                }, indent=2)
    
    # Validate payment_source parameter
    if payment_source:
        valid_payment_sources = [
            "pg", "button", "paymentLink", "apiIntInvoice", "excelPlugin", 
            "appPaymentLink", "payHandle", "appPayHandle", "slashPayHandle", 
            "webstore", "sist", "sinst", "si_invoice", "event", "storefront", 
            "pos", "appItemizedInvoice", "itemizedInvoice", "sirecurring"
        ]
        for ps in payment_source:
            if ps not in valid_payment_sources:
                return json.dumps({
                    "error": f"Invalid payment_source '{ps}'. Valid sources are: {', '.join(valid_payment_sources)}"
                }, indent=2)
    
    # Validate pa parameter
    if pa:
        valid_pas = ["PayU", "AxisCyber", "RazorPay"]
        for p in pa:
            if p not in valid_pas:
                return json.dumps({
                    "error": f"Invalid pa '{p}'. Valid payment aggregators are: {', '.join(valid_pas)}"
                }, indent=2)
    
    # Validate more_filters parameter
    if more_filters:
        valid_more_filters = [
            "ivr", "remReattempts", "interTxn", "mobile", "txnOffer", "emailInvoice", 
            "uniqTxn", "domTxn", "web", "siInvoice", "subEMI", "chargebackTxn", "tpv"
        ]
        for mf in more_filters:
            if mf not in valid_more_filters:
                return json.dumps({
                    "error": f"Invalid more_filter '{mf}'. Valid filters are: {', '.join(valid_more_filters)}"
                }, indent=2)
    
    # Validate transaction_currency parameter
    if transaction_currency:
        valid_currencies = ["USD", "AED", "AUD", "CAD", "GBP", "OTH"]
        for tc in transaction_currency:
            if tc not in valid_currencies:
                return json.dumps({
                    "error": f"Invalid currency '{tc}'. Valid currencies are: {', '.join(valid_currencies)}"
                }, indent=2)
    
    # Validate amount parameters - PayU API requires both or neither
    if min_amount is not None or max_amount is not None:
        if min_amount is None or max_amount is None:
            return json.dumps({
                "error": "Both minAmount and maxAmount must be provided together (PayU API requirement)"
            }, indent=2)
        if min_amount >= max_amount:
            return json.dumps({
                "error": f"minAmount ({min_amount}) must be less than maxAmount ({max_amount})"
            }, indent=2)
    
    # Build base parameters (mandatory and defaults)
    params = {
        'dateFrom': date_from,
        'dateTo': date_to,
        'all-flag': 1,  # Always 1 as per specification
        'pageOffset': page_offset,
        'pageLimit': page_limit
    }
    
    # Always add mandatory additional fields
    mandatory_additional_fields = ["transactionAmount", "transactionCurrency", "exchangeRate", "exchangeDate"]
    
    # Optional amount parameters
    if min_amount is not None:
        params['minAmount'] = min_amount
    if max_amount is not None:
        params['maxAmount'] = max_amount
    if offer_applied is not None:
        params['offerApplied'] = 'true' if offer_applied else 'false'
    
    # Build URL with array parameters
    base_params = urlencode(params)
    array_params = []
    
    # Add array parameters manually for proper formatting
    if status:
        array_params.extend([f'status[]={s}' for s in status])
    if mode:
        array_params.extend([f'mode[]={m}' for m in mode])
    if payment_source:
        array_params.extend([f'paymentSource[]={ps}' for ps in payment_source])
    if pa:
        array_params.extend([f'pa[]={p}' for p in pa])
    if more_filters:
        array_params.extend([f'moreFilters[]={mf}' for mf in more_filters])
    if transaction_currency:
        array_params.extend([f'transactionCurrency[]={tc}' for tc in transaction_currency])
    
    # Always add mandatory additional fields
    array_params.extend([f'additionalFields[]={af}' for af in mandatory_additional_fields])
    
    # Combine all parameters
    if array_params:
        url = f"{API_BASE}/transactions/?{base_params}&{'&'.join(array_params)}"
    else:
        url = f"{API_BASE}/transactions/?{base_params}&{'&'.join([f'additionalFields[]={af}' for af in mandatory_additional_fields])}"
    data = await make_request_with_direct_token(url)
    
    if not data:
        return "Failed to retrieve transactions list."
    
    return json.dumps(data, indent=2)


async def get_transactions_summary(
    date_from: str,
    date_to: str,
    status: List[str] = None,
    mode: List[str] = None,
    payment_source: List[str] = None,
    transaction_currency: List[str] = None,
    more_filters: List[str] = None,
    pa: List[str] = None,
    offer_applied: Optional[bool] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None
) -> str:
    """
    Get transactions summary from PayU.
    
    Args:
        date_from (str): Start date (YYYY-MM-DD HH:MM:SS format) - MANDATORY
        date_to (str): End date (YYYY-MM-DD HH:MM:SS format) - MANDATORY
        status (List[str]): Status filter list (optional). Valid values: captured, in progress, auth, pending, initiated, in-progress, in_progress, Authorized, userCancelled, failed, failure, blocked, cancelled, autoRefund, Auto Refund Initiated, Auto Refunded, dropped, bounced, refundSuccess, refundFailed, refundPending, Cancelled
        mode (List[str]): Payment mode filter list (optional). Valid values: CC, DC, NB, EMI, CASH, COD, CN, UPI, CHALLANPAYMENTS, payViaApp, enach, PAYPAL, LAZYPAY, SBQR, ISBQR, DBQR, ADHR, QR, OFUPI, DBT, NEFTRTGS, SPLITPAY, UPICC, UPIPPI, UPICL, UPICLI, CLW, OLW, UPIOTM
        payment_source (List[str]): Payment source filter list (optional). Valid values: pg, button, paymentLink, apiIntInvoice, excelPlugin, appPaymentLink, sirecurring, sist, sinst, si_invoice, payHandle, appPayHandle, slashPayHandle, appItemizedInvoice, itemizedInvoice, event, webstore, pos, storefront
        transaction_currency (List[str]): Currency filter list (optional). Valid values: USD, CAD, GBP, AED, AUD, OTH
        more_filters (List[str]): Additional filters (optional). Valid values: ivr, emailInvoice, uniqTxn, remReattempts, txnOffer, domTxn, interTxn, mobile, web, chargebackTxn, subEMI, siInvoice, tpv
        pa (List[str]): Payment aggregator filter list (optional). Valid values: RazorPay, AxisCyber, PayU
        offer_applied (bool): Filter by offer applied status (optional)
        min_amount (float): Minimum amount filter (optional, must be provided together with max_amount due to PayU API requirement)
        max_amount (float): Maximum amount filter (optional, must be provided together with min_amount due to PayU API requirement)
    
    Returns:
        str: Formatted transactions summary
    """
    # Validate status parameter
    if status:
        valid_statuses = [
            "captured", "in progress", "auth", "pending", "initiated", "in-progress", 
            "in_progress", "Authorized", "userCancelled", "failed", "failure", "blocked", 
            "cancelled", "autoRefund", "Auto Refund Initiated", "Auto Refunded", 
            "dropped", "bounced", "refundSuccess", "refundFailed", "refundPending", "Cancelled"
        ]
        for s in status:
            if s not in valid_statuses:
                return json.dumps({
                    "error": f"Invalid status '{s}'. Valid statuses are: {', '.join(valid_statuses)}"
                }, indent=2)
    
    # Validate mode parameter
    if mode:
        valid_modes = [
            "CC", "DC", "NB", "EMI", "CASH", "COD", "CN", "UPI", "CHALLANPAYMENTS", 
            "payViaApp", "enach", "PAYPAL", "LAZYPAY", "SBQR", "ISBQR", "DBQR", 
            "ADHR", "QR", "OFUPI", "DBT", "NEFTRTGS", "SPLITPAY", "UPICC", "UPIPPI", 
            "UPICL", "UPICLI", "CLW", "OLW", "UPIOTM"
        ]
        for m in mode:
            if m not in valid_modes:
                return json.dumps({
                    "error": f"Invalid mode '{m}'. Valid modes are: {', '.join(valid_modes)}"
                }, indent=2)
    
    # Validate payment_source parameter
    if payment_source:
        valid_payment_sources = [
            "pg", "button", "paymentLink", "apiIntInvoice", "excelPlugin", 
            "appPaymentLink", "sirecurring", "sist", "sinst", "si_invoice", 
            "payHandle", "appPayHandle", "slashPayHandle", "appItemizedInvoice", 
            "itemizedInvoice", "event", "webstore", "pos", "storefront"
        ]
        for ps in payment_source:
            if ps not in valid_payment_sources:
                return json.dumps({
                    "error": f"Invalid payment_source '{ps}'. Valid sources are: {', '.join(valid_payment_sources)}"
                }, indent=2)
    
    # Validate transaction_currency parameter
    if transaction_currency:
        valid_currencies = ["USD", "CAD", "GBP", "AED", "AUD", "OTH"]
        for tc in transaction_currency:
            if tc not in valid_currencies:
                return json.dumps({
                    "error": f"Invalid currency '{tc}'. Valid currencies are: {', '.join(valid_currencies)}"
                }, indent=2)
    
    # Validate more_filters parameter
    if more_filters:
        valid_more_filters = [
            "ivr", "emailInvoice", "uniqTxn", "remReattempts", "txnOffer", "domTxn", 
            "interTxn", "mobile", "web", "chargebackTxn", "subEMI", "siInvoice", "tpv"
        ]
        for mf in more_filters:
            if mf not in valid_more_filters:
                return json.dumps({
                    "error": f"Invalid more_filter '{mf}'. Valid filters are: {', '.join(valid_more_filters)}"
                }, indent=2)
    
    # Validate pa parameter
    if pa:
        valid_pas = ["RazorPay", "AxisCyber", "PayU"]
        for p in pa:
            if p not in valid_pas:
                return json.dumps({
                    "error": f"Invalid pa '{p}'. Valid payment aggregators are: {', '.join(valid_pas)}"
                }, indent=2)
    
    # Validate amount parameters - PayU API requires both or neither
    if min_amount is not None or max_amount is not None:
        if min_amount is None or max_amount is None:
            return json.dumps({
                "error": "Both minAmount and maxAmount must be provided together (PayU API requirement)"
            }, indent=2)
        if min_amount >= max_amount:
            return json.dumps({
                "error": f"minAmount ({min_amount}) must be less than maxAmount ({max_amount})"
            }, indent=2)
    
    # Build base parameters (mandatory and defaults)
    params = {
        'dateFrom': date_from,
        'dateTo': date_to,
        'all-flag': 1,  # Always 1 as per specification
        'read_refund': 'false'  # Always false as per specification
    }
    
    # Optional amount parameters
    if min_amount is not None:
        params['minAmount'] = min_amount
    if max_amount is not None:
        params['maxAmount'] = max_amount
    if offer_applied is not None:
        params['offerApplied'] = 'true' if offer_applied else 'false'
    
    # Build URL with array parameters
    base_params = urlencode(params)
    array_params = []
    
    # Add array parameters manually for proper formatting
    if status:
        array_params.extend([f'status={s}' for s in status])
    if mode:
        array_params.extend([f'mode={m}' for m in mode])
    if payment_source:
        array_params.extend([f'paymentSource={ps}' for ps in payment_source])
    if transaction_currency:
        array_params.extend([f'transactionCurrency={tc}' for tc in transaction_currency])
    if more_filters:
        array_params.extend([f'moreFilters={mf}' for mf in more_filters])
    if pa:
        array_params.extend([f'pa={p}' for p in pa])
    
    # Combine all parameters
    if array_params:
        url = f"{API_BASE}/transactions/summary/?{base_params}&{'&'.join(array_params)}"
    else:
        url = f"{API_BASE}/transactions/summary/?{base_params}"
    
    data = await make_request_with_direct_token(url)
    
    if not data:
        return "Failed to retrieve transactions summary."
    
    return json.dumps(data, indent=2)
