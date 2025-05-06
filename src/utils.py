import re
from datetime import datetime
from dateutil import parser

# Match formats like 12/04/2024, 2024-04-12, Exp: 12-04-2024
DATE_PATTERNS = [
    r'\b(\d{2}[/-]\d{2}[/-]\d{4})\b',
    r'\b(\d{4}[/-]\d{2}[/-]\d{2})\b'
]

def extract_expiry_date(text):
    for pattern in DATE_PATTERNS:
        match = re.search(pattern, text)
        if match:
            date_str = match.group(1)
            try:
                return parser.parse(date_str, dayfirst=True)
            except:
                continue
    return None

def check_if_expired(date):
    today = datetime.today()
    return date < today
