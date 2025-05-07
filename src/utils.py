import re
from datetime import datetime
from dateutil import parser

# Enhanced date patterns to catch more formats
DATE_PATTERNS = [
    # Standard formats
    r'\b(\d{2}[/-]\d{2}[/-]\d{4})\b',  # DD/MM/YYYY or DD-MM-YYYY
    r'\b(\d{4}[/-]\d{2}[/-]\d{2})\b',  # YYYY/MM/DD or YYYY-MM-DD

    # With expiry keywords
    r'(?:exp|expiry|expiration|expires|best before|use by)[:\s]*(\d{2}[/-]\d{2}[/-]\d{4})',
    r'(?:exp|expiry|expiration|expires|best before|use by)[:\s]*(\d{4}[/-]\d{2}[/-]\d{2})',

    # Dot separated formats
    r'\b(\d{2}\.\d{2}\.\d{4})\b',  # DD.MM.YYYY
    r'\b(\d{4}\.\d{2}\.\d{2})\b',  # YYYY.MM.DD

    # Month name formats
    r'\b(\d{2}[\s-](?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[\s-]\d{4})\b',
    r'\b(\d{2}[\s-](?:January|February|March|April|May|June|July|August|September|October|November|December)[\s-]\d{4})\b',

    # Just month and year (assuming day is 1)
    r'(?:exp|expiry|expiration|expires|best before|use by)[:\s]*(\d{2}[/-]\d{4})',
    r'(?:exp|expiry|expiration|expires|best before|use by)[:\s]*(\d{4}[/-]\d{2})',

    # With weird separators
    r'\b(\d{2}[ ,.]\d{2}[ ,.]\d{4})\b',  # DD<sep>MM<sep>YYYY

    # Formats with abbreviated year
    r'\b(\d{2}[/-]\d{2}[/-]\d{2})\b',  # DD/MM/YY
]

# Keywords that often appear near expiry dates
EXPIRY_KEYWORDS = [
    "expiry", "exp", "exp date", "expiration", "expires on", "E"
    "best before", "best by", "use by", "use before",
    "bb date", "bb", "ed", "exp. date"
]


def extract_expiry_date(text):
    """
    Extract expiry date from text using multiple approaches
    """
    if not text:
        return None

    text = text.lower()

    # Try to find dates associated with expiry keywords first
    for keyword in EXPIRY_KEYWORDS:
        if keyword in text:
            # Get the line containing the keyword
            lines = text.split('\n')
            for line in lines:
                if keyword in line:
                    # Try all patterns on this specific line
                    for pattern in DATE_PATTERNS:
                        match = re.search(pattern, line, re.IGNORECASE)
                        if match:
                            date_str = match.group(1)
                            try:
                                return parse_date_string(date_str)
                            except:
                                continue

    # If no date found with keywords, try all patterns on the entire text
    for pattern in DATE_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                # Check if it's a valid date and not too far in the future (expiry dates usually within 5 years)
                date = parse_date_string(match)
                if date:
                    today = datetime.today()
                    five_years = datetime(today.year + 5, today.month, today.day)
                    if date < five_years:
                        return date
            except:
                continue

    return None


def parse_date_string(date_str):
    """Parse date string with multiple approaches"""
    try:
        # Try dateutil parser first (flexible)
        return parser.parse(date_str, dayfirst=True, fuzzy=True)
    except:
        pass

    try:
        # Handle special case: MM/YYYY or MM-YYYY (assume day 1)
        if re.match(r'^\d{2}[/-]\d{4}$', date_str):
            month, year = date_str.replace('-', '/').split('/')
            return datetime(int(year), int(month), 1)
    except:
        pass

    try:
        # Handle special case: YYYY/MM or YYYY-MM (assume day 1)
        if re.match(r'^\d{4}[/-]\d{2}$', date_str):
            year, month = date_str.replace('-', '/').split('/')
            return datetime(int(year), int(month), 1)
    except:
        pass

    try:
        # Handle special case: DD/MM/YY (2-digit year)
        if re.match(r'^\d{2}[/-]\d{2}[/-]\d{2}$', date_str):
            parts = re.split(r'[/-]', date_str)
            day, month, year = int(parts[0]), int(parts[1]), int(parts[2])

            # Convert 2-digit year to 4-digit
            current_year = datetime.now().year
            century = current_year // 100 * 100
            full_year = century + year

            # If the resulting year is more than 50 years in the future,
            # assume it's from the previous century
            if full_year > current_year + 50:
                full_year -= 100

            return datetime(full_year, month, day)
    except:
        pass

    return None


def check_if_expired(date):
    """Check if a date is in the past"""
    today = datetime.today()
    return date < today