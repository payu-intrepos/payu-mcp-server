import re


def validate_email(email):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return email and re.match(email_regex, email) is not None


def validate_phone(phone):
    phone_regex = r'^\+?[1-9]\d{9,14}$'
    return phone and re.match(phone_regex, phone) is not None

def mask_email(email):
    """Mask email leaving first 2 and last 2 characters visible"""
    if '@' in email:
        username, domain = email.split('@')
        if len(username) > 4:  # Need at least 5 chars to show 2 at start, 2 at end and mask at least 1
            visible_prefix = username[:2]
            visible_suffix = username[-2:]
            masked_middle = '*' * (len(username) - 4)
            masked_username = f"{visible_prefix}{masked_middle}{visible_suffix}"
            return f"{masked_username}@{domain}"
        elif len(username) > 0:  # For short usernames, mask everything except first char
            return f"{username[0]}{'*' * (len(username)-1)}@{domain}"
    return email

def mask_phone(phone):
    """Mask the middle 4 characters of a phone number"""
    if len(phone) >= 6:  # Ensure phone number is long enough to mask
        prefix = phone[:len(phone)//2 - 2]
        middle = "****"  # Mask middle 4 digits
        suffix = phone[len(phone)//2 + 2:]
        return f"{prefix}{middle}{suffix}"
    return phone
