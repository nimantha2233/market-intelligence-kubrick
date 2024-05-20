import yfinance as yf
import json

def get_company_status(symbol):
    # Provides information on whether the company is private or public
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        if info['quoteType'] == 'EQUITY':
            return "Public"
        else:
            return "Private"
    except KeyError:
        return 'Private'
    except Exception as e:
        return str(e)

def get_company_details(symbol):
    status = get_company_status(symbol)
    if status == "Private":
        return json.dumps({"Public/Private": "Private"})
    elif status == "Public":
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            company_details = {
                "Public/Private": "Public",
                "Previous Close": info.get("previousClose", "N/A"),
                "52 Week Range": info.get("fiftyTwoWeekRange", "N/A"),
                "Sector": info.get("sector", "N/A"),
                "Industry": info.get("industry", "N/A"),
                "Full Time Employees": info.get("fullTimeEmployees", "N/A"),
                "Market Cap": info.get("marketCap", "N/A"),
                "Fiscal Year Ends": info.get("fiscalYearEnd", "N/A"),
                "Revenue": info.get("totalRevenue", "N/A"),
                "EBITDA": info.get("ebitda", "N/A"),
                "Revenue Trends": "N/A",  # This might require additional data source
                "Profitability": "N/A",   # This might require additional data source
                "Growth Rate": "N/A"      # This might require additional data source
            }
            return json.dumps(company_details)
        except Exception as e:
            return json.dumps({"error": str(e)})
    else:
        return json.dumps({"error": status})

# Example usage
symbol = 'AAPL'  # Example symbol for Apple Inc.
company_details_json = get_company_details(symbol)
print(company_details_json)