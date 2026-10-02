"""Directory and resolver for Nifty 50, Sensex, and Indian equity instruments."""

# Canonical Nifty 50 and key Indian equities catalog
INDIAN_EQUITIES_CATALOG: dict[str, dict[str, str]] = {
    # NIFTY 50 Top Weights
    "RELIANCE": {
        "name": "Reliance Industries Limited",
        "exchange": "NSE",
        "sector": "Energy & Retail Conglomerate",
        "yahoo_ticker": "RELIANCE.NS",
    },
    "TCS": {
        "name": "Tata Consultancy Services Limited",
        "exchange": "NSE",
        "sector": "Information Technology",
        "yahoo_ticker": "TCS.NS",
    },
    "HDFCBANK": {
        "name": "HDFC Bank Limited",
        "exchange": "NSE",
        "sector": "Banking & Financial Services",
        "yahoo_ticker": "HDFCBANK.NS",
    },
    "ICICIBANK": {
        "name": "ICICI Bank Limited",
        "exchange": "NSE",
        "sector": "Banking & Financial Services",
        "yahoo_ticker": "ICICIBANK.NS",
    },
    "BHARTIARTL": {
        "name": "Bharti Airtel Limited",
        "exchange": "NSE",
        "sector": "Telecommunications",
        "yahoo_ticker": "BHARTIARTL.NS",
    },
    "INFY": {
        "name": "Infosys Limited",
        "exchange": "NSE",
        "sector": "Information Technology",
        "yahoo_ticker": "INFY.NS",
    },
    "ITC": {
        "name": "ITC Limited",
        "exchange": "NSE",
        "sector": "Consumer Goods & Conglomerate",
        "yahoo_ticker": "ITC.NS",
    },
    "SBIN": {
        "name": "State Bank of India",
        "exchange": "NSE",
        "sector": "Public Sector Banking",
        "yahoo_ticker": "SBIN.NS",
    },
    "LT": {
        "name": "Larsen & Toubro Limited",
        "exchange": "NSE",
        "sector": "Engineering & Construction",
        "yahoo_ticker": "LT.NS",
    },
    "HINDUNILVR": {
        "name": "Hindustan Unilever Limited",
        "exchange": "NSE",
        "sector": "Fast Moving Consumer Goods (FMCG)",
        "yahoo_ticker": "HINDUNILVR.NS",
    },
    "AXISBANK": {
        "name": "Axis Bank Limited",
        "exchange": "NSE",
        "sector": "Banking & Financial Services",
        "yahoo_ticker": "AXISBANK.NS",
    },
    "KOTAKBANK": {
        "name": "Kotak Mahindra Bank Limited",
        "exchange": "NSE",
        "sector": "Banking & Financial Services",
        "yahoo_ticker": "KOTAKBANK.NS",
    },
    "BAJFINANCE": {
        "name": "Bajaj Finance Limited",
        "exchange": "NSE",
        "sector": "Non-Banking Financial Company (NBFC)",
        "yahoo_ticker": "BAJFINANCE.NS",
    },
    "MARUTI": {
        "name": "Maruti Suzuki India Limited",
        "exchange": "NSE",
        "sector": "Automobile Manufacturer",
        "yahoo_ticker": "MARUTI.NS",
    },
    "M&M": {
        "name": "Mahindra & Mahindra Limited",
        "exchange": "NSE",
        "sector": "Automotive & Farm Equipment",
        "yahoo_ticker": "M&M.NS",
    },
    "TITAN": {
        "name": "Titan Company Limited",
        "exchange": "NSE",
        "sector": "Consumer Discretionary & Jewellery",
        "yahoo_ticker": "TITAN.NS",
    },
    "SUNPHARMA": {
        "name": "Sun Pharmaceutical Industries Limited",
        "exchange": "NSE",
        "sector": "Pharmaceuticals & Healthcare",
        "yahoo_ticker": "SUNPHARMA.NS",
    },
    "ADANIENT": {
        "name": "Adani Enterprises Limited",
        "exchange": "NSE",
        "sector": "Integrated Resource Management",
        "yahoo_ticker": "ADANIENT.NS",
    },
    "TATAMOTORS": {
        "name": "Tata Motors Limited",
        "exchange": "NSE",
        "sector": "Automobile Manufacturer",
        "yahoo_ticker": "TMPV.NS",
    },
    "TMPV": {
        "name": "Tata Motors Passenger Vehicles Limited",
        "exchange": "NSE",
        "sector": "Automobile Manufacturer",
        "yahoo_ticker": "TMPV.NS",
    },
    "ULTRACEMCO": {
        "name": "UltraTech Cement Limited",
        "exchange": "NSE",
        "sector": "Cement & Building Materials",
        "yahoo_ticker": "ULTRACEMCO.NS",
    },
    "NTPC": {
        "name": "NTPC Limited",
        "exchange": "NSE",
        "sector": "Thermal & Renewable Power",
        "yahoo_ticker": "NTPC.NS",
    },
    "ONGC": {
        "name": "Oil and Natural Gas Corporation Limited",
        "exchange": "NSE",
        "sector": "Oil & Gas Exploration",
        "yahoo_ticker": "ONGC.NS",
    },
    "POWERGRID": {
        "name": "Power Grid Corporation of India Limited",
        "exchange": "NSE",
        "sector": "Power Transmission Utilities",
        "yahoo_ticker": "POWERGRID.NS",
    },
    "TATASTEEL": {
        "name": "Tata Steel Limited",
        "exchange": "NSE",
        "sector": "Steel & Metal Products",
        "yahoo_ticker": "TATASTEEL.NS",
    },
    "BAJAJFINSV": {
        "name": "Bajaj Finserv Limited",
        "exchange": "NSE",
        "sector": "Financial Services Holding",
        "yahoo_ticker": "BAJAJFINSV.NS",
    },
    "COALINDIA": {
        "name": "Coal India Limited",
        "exchange": "NSE",
        "sector": "Mining & Minerals",
        "yahoo_ticker": "COALINDIA.NS",
    },
    "HCLTECH": {
        "name": "HCL Technologies Limited",
        "exchange": "NSE",
        "sector": "Information Technology",
        "yahoo_ticker": "HCLTECH.NS",
    },
    "NESTLEIND": {
        "name": "Nestle India Limited",
        "exchange": "NSE",
        "sector": "FMCG - Food Products",
        "yahoo_ticker": "NESTLEIND.NS",
    },
    "ASIANPAINT": {
        "name": "Asian Paints Limited",
        "exchange": "NSE",
        "sector": "Paints & Home Decor",
        "yahoo_ticker": "ASIANPAINT.NS",
    },
    "JSWSTEEL": {
        "name": "JSW Steel Limited",
        "exchange": "NSE",
        "sector": "Steel Manufacturing",
        "yahoo_ticker": "JSWSTEEL.NS",
    },
    "GRASIM": {
        "name": "Grasim Industries Limited",
        "exchange": "NSE",
        "sector": "Chemicals, Textiles & Building",
        "yahoo_ticker": "GRASIM.NS",
    },
    "TECHM": {
        "name": "Tech Mahindra Limited",
        "exchange": "NSE",
        "sector": "IT & Consulting",
        "yahoo_ticker": "TECHM.NS",
    },
    "HINDALCO": {
        "name": "Hindalco Industries Limited",
        "exchange": "NSE",
        "sector": "Aluminium & Copper Producer",
        "yahoo_ticker": "HINDALCO.NS",
    },
    "CIPLA": {
        "name": "Cipla Limited",
        "exchange": "NSE",
        "sector": "Pharmaceuticals & Biotechnology",
        "yahoo_ticker": "CIPLA.NS",
    },
    "ADANIPORTS": {
        "name": "Adani Ports and Special Economic Zone Limited",
        "exchange": "NSE",
        "sector": "Ports & Logistics Infrastructure",
        "yahoo_ticker": "ADANIPORTS.NS",
    },
    "TRENT": {
        "name": "Trent Limited",
        "exchange": "NSE",
        "sector": "Fashion & Lifestyle Retail",
        "yahoo_ticker": "TRENT.NS",
    },
    "BEL": {
        "name": "Bharat Electronics Limited",
        "exchange": "NSE",
        "sector": "Defense Electronics & Avionics",
        "yahoo_ticker": "BEL.NS",
    },
    "SHRIRAMFIN": {
        "name": "Shriram Finance Limited",
        "exchange": "NSE",
        "sector": "Commercial Vehicle & NBFC",
        "yahoo_ticker": "SHRIRAMFIN.NS",
    },
    "DRREDDY": {
        "name": "Dr. Reddy's Laboratories Limited",
        "exchange": "NSE",
        "sector": "Global Pharmaceutical Formulations",
        "yahoo_ticker": "DRREDDY.NS",
    },
    "BPCL": {
        "name": "Bharat Petroleum Corporation Limited",
        "exchange": "NSE",
        "sector": "Oil Refining & Marketing",
        "yahoo_ticker": "BPCL.NS",
    },
    "EICHERMOT": {
        "name": "Eicher Motors Limited",
        "exchange": "NSE",
        "sector": "Commercial Vehicles & Royal Enfield",
        "yahoo_ticker": "EICHERMOT.NS",
    },
    "WIPRO": {
        "name": "Wipro Limited",
        "exchange": "NSE",
        "sector": "Global Information Technology",
        "yahoo_ticker": "WIPRO.NS",
    },
    "APOLLOHOSP": {
        "name": "Apollo Hospitals Enterprise Limited",
        "exchange": "NSE",
        "sector": "Healthcare Services & Pharmacies",
        "yahoo_ticker": "APOLLOHOSP.NS",
    },
    "HEROMOTOCO": {
        "name": "Hero MotoCorp Limited",
        "exchange": "NSE",
        "sector": "Two-Wheeler Manufacturer",
        "yahoo_ticker": "HEROMOTOCO.NS",
    },
    "TATACONSUM": {
        "name": "Tata Consumer Products Limited",
        "exchange": "NSE",
        "sector": "Beverages & Packaged Foods",
        "yahoo_ticker": "TATACONSUM.NS",
    },
    "BRITANNIA": {
        "name": "Britannia Industries Limited",
        "exchange": "NSE",
        "sector": "Packaged Food & Biscuits",
        "yahoo_ticker": "BRITANNIA.NS",
    },
    "SBILIFE": {
        "name": "SBI Life Insurance Company Limited",
        "exchange": "NSE",
        "sector": "Life Insurance",
        "yahoo_ticker": "SBILIFE.NS",
    },
    "HDFCLIFE": {
        "name": "HDFC Life Insurance Company Limited",
        "exchange": "NSE",
        "sector": "Life Insurance",
        "yahoo_ticker": "HDFCLIFE.NS",
    },
    "INDUSINDBK": {
        "name": "IndusInd Bank Limited",
        "exchange": "NSE",
        "sector": "Private Sector Banking",
        "yahoo_ticker": "INDUSINDBK.NS",
    },
    "DIVISLAB": {
        "name": "Divi's Laboratories Limited",
        "exchange": "NSE",
        "sector": "Active Pharmaceutical Ingredients (API)",
        "yahoo_ticker": "DIVISLAB.NS",
    },
    "TATAPOWER": {
        "name": "Tata Power Company Limited",
        "exchange": "NSE",
        "sector": "Integrated Power & Renewables",
        "yahoo_ticker": "TATAPOWER.NS",
    },
    "JIOFIN": {
        "name": "Jio Financial Services Limited",
        "exchange": "NSE",
        "sector": "Digital Financial Services",
        "yahoo_ticker": "JIOFIN.NS",
    },
    "ZOMATO": {
        "name": "Eternal (Zomato) Limited",
        "exchange": "NSE",
        "sector": "Online Food Delivery & Quick Commerce",
        "yahoo_ticker": "ETERNAL.NS",
    },
    "ETERNAL": {
        "name": "Eternal Limited",
        "exchange": "NSE",
        "sector": "Online Food Delivery & Quick Commerce",
        "yahoo_ticker": "ETERNAL.NS",
    },
    "VEDL": {
        "name": "Vedanta Limited",
        "exchange": "NSE",
        "sector": "Diversified Natural Resources",
        "yahoo_ticker": "VEDL.NS",
    },
    "HAL": {
        "name": "Hindustan Aeronautics Limited",
        "exchange": "NSE",
        "sector": "Defense & Aerospace Manufacturing",
        "yahoo_ticker": "HAL.NS",
    },
    # Indices
    "NIFTY": {
        "name": "NIFTY 50 Benchmark Index",
        "exchange": "NSE",
        "sector": "Indian Benchmark Equity Index",
        "yahoo_ticker": "^NSEI",
    },
    "NIFTY50": {
        "name": "NIFTY 50 Benchmark Index",
        "exchange": "NSE",
        "sector": "Indian Benchmark Equity Index",
        "yahoo_ticker": "^NSEI",
    },
    "SENSEX": {
        "name": "S&P BSE SENSEX 30 Index",
        "exchange": "BSE",
        "sector": "Indian Benchmark Equity Index",
        "yahoo_ticker": "^BSESN",
    },
    "^NSEI": {
        "name": "NIFTY 50 Benchmark Index",
        "exchange": "NSE",
        "sector": "Indian Benchmark Equity Index",
        "yahoo_ticker": "^NSEI",
    },
    "^BSESN": {
        "name": "S&P BSE SENSEX 30 Index",
        "exchange": "BSE",
        "sector": "Indian Benchmark Equity Index",
        "yahoo_ticker": "^BSESN",
    },
}


def normalize_indian_symbol(raw_symbol: str) -> tuple[str, str]:
    """
    Resolve any user input to (display_symbol, yahoo_ticker).
    Examples:
        'RELIANCE' -> ('RELIANCE.NS', 'RELIANCE.NS')
        'reliance' -> ('RELIANCE.NS', 'RELIANCE.NS')
        'TCS.NS' -> ('TCS.NS', 'TCS.NS')
        'NIFTY' -> ('^NSEI', '^NSEI')
        'SENSEX' -> ('^BSESN', '^BSESN')
        'HDFCBANK.BO' -> ('HDFCBANK.BO', 'HDFCBANK.BO')
    """
    clean = raw_symbol.upper().strip()

    # Index aliases
    if clean in ("NIFTY", "NIFTY50", "NIFTY 50", "^NSEI"):
        return ("^NSEI", "^NSEI")
    if clean in ("SENSEX", "BSESENSEX", "BSE SENSEX", "^BSESN"):
        return ("^BSESN", "^BSESN")

    # Already has exchange suffix
    if clean.endswith(".NS") or clean.endswith(".BO"):
        return (clean, clean)

    # In catalog
    base = clean.split(".")[0]
    if base in INDIAN_EQUITIES_CATALOG:
        entry = INDIAN_EQUITIES_CATALOG[base]
        return (entry["yahoo_ticker"], entry["yahoo_ticker"])

    # If already index starting with ^
    if clean.startswith("^"):
        return (clean, clean)

    # Default Indian equity convention on NSE
    return (f"{clean}.NS", f"{clean}.NS")


def get_equity_metadata(symbol: str) -> dict[str, str]:
    """Retrieve full company name, exchange, sector, and currency."""
    clean = symbol.upper().strip()
    base = clean.split(".")[0].replace("^", "")

    if clean in ("^NSEI", "NIFTY", "NIFTY50"):
        return {
            "name": "NIFTY 50 Benchmark Index",
            "exchange": "NSE",
            "sector": "Indian Equity Benchmark Index",
            "currency": "INR",
            "currency_symbol": "₹",
        }
    if clean in ("^BSESN", "SENSEX"):
        return {
            "name": "S&P BSE SENSEX 30 Index",
            "exchange": "BSE",
            "sector": "Indian Equity Benchmark Index",
            "currency": "INR",
            "currency_symbol": "₹",
        }

    if base in INDIAN_EQUITIES_CATALOG:
        entry = INDIAN_EQUITIES_CATALOG[base]
        return {
            "name": entry["name"],
            "exchange": entry["exchange"],
            "sector": entry["sector"],
            "currency": "INR",
            "currency_symbol": "₹",
        }

    # Fallback for other tickers
    is_indian = clean.endswith(".NS") or clean.endswith(".BO") or clean in INDIAN_EQUITIES_CATALOG
    return {
        "name": f"{base.capitalize()} Ltd." if is_indian else base,
        "exchange": "NSE" if clean.endswith(".NS") else ("BSE" if clean.endswith(".BO") else "US"),
        "sector": "Equity",
        "currency": "INR" if is_indian else "USD",
        "currency_symbol": "₹" if is_indian else "$",
    }
