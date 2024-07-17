import os
import scrapers
import numpy as np
import pandas as pd
import yfinance as yf
from io import StringIO
from collections import defaultdict
from datetime import datetime, timedelta, date
from azure.storage.blob import BlobSasPermissions, generate_blob_sas, BlobClient, BlobServiceClient
from urllib.parse import quote
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Retrieve the secrets from environment variables
account_name = os.getenv('ACCOUNT_NAME')
container_name = os.getenv('CONTAINER_NAME')
account_key = os.getenv('ACCOUNT_KEY')

# Build the connection string
connect_str = 'DefaultEndpointsProtocol=https;AccountName=' + account_name + ';AccountKey=' + account_key + ';EndpointSuffix=core.windows.net'

blob_service_client = BlobServiceClient.from_connection_string(connect_str)

def list_blobs(prefix):
    container_client = blob_service_client.get_container_client(container_name)
    return [blob.name for blob in container_client.list_blobs(name_starts_with=prefix)]

def get_scraped_company_data(scraper):
    try:
        function_name = scraper
        func = getattr(scrapers, function_name)
        return func()
    except:
        log_error(f'Issue with {scraper} in scrapers.py. Please check the log files.')

def download_blob(file_name):
    try:
        # Encode the file name to replace spaces with %20
        encoded_file_name = quote(file_name)

        sas_token = generate_blob_sas(
            account_name=account_name,
            container_name=container_name,
            blob_name=file_name,
            account_key=account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1)
        )
        sas_url = f'https://{account_name}.blob.core.windows.net/{container_name}/{encoded_file_name}?{sas_token}'
        return pd.read_csv(sas_url)
    except Exception as e:
        log_error(f'Error while accessing {file_name} in Azure : {e}')

def download_blob_as_string(file_name):
    try:
        # Encode the file name to replace spaces with %20
        encoded_file_name = quote(file_name)

        sas_token = generate_blob_sas(
            account_name=account_name,
            container_name=container_name,
            blob_name=file_name,
            account_key=account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1)
        )
        sas_url = f'https://{account_name}.blob.core.windows.net/{container_name}/{encoded_file_name}?{sas_token}'
        blob_client = BlobClient.from_blob_url(sas_url)
        stream = StringIO(blob_client.download_blob().content_as_text())
        return stream
    except Exception as e:
        log_error(f'Error while accessing {file_name} in Azure : {e}')

def delete_blob(file_name):
    try:
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)
        blob_client.delete_blob()
    except Exception as e:
        log_error(f'Error while deleting {file_name} in Azure : {e}')

def get_blob_csv_company(company_name):
    try:
        prefix = f'output/{company_name}'
        matching_files = list_blobs(prefix)
        file_name = next((file for file in matching_files if 'webscrape' in file and file.endswith('.csv')), None)
        if file_name:
            data = download_blob(file_name)
            delete_blob(file_name)
            return data
        else:
            return download_blob('Template.csv')
    except Exception as e:
        log_error(f'Unable to access csv for {company_name} in Azure : {e}')

def get_blob_path_file(path_file, sanitized_name):
    try:
        matching_files = list_blobs(path_file)
        file_name = next((file for file in matching_files if 'webscrape' in file and file.endswith('.csv')), None)

        if file_name:
            return file_name
        else:
            return f'output/{sanitized_name}/file_not_found.csv'
    except Exception as e:
        log_error(f'Unable to find path file for {sanitized_name} : {e}')

def download_blob_to_string(blob_name):
    try:
        """Download a blob to a string."""
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        blob_data = blob_client.download_blob()
        return blob_data.content_as_text()
    except Exception as e:
        log_error(f'Unable to download {blob_name} from Azure : {e}')

def upload_string_to_blob(blob_name, content):
    try:
        """Upload a string to a blob."""
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        blob_client.upload_blob(content, overwrite=True)
    except Exception as e:
        log_error(f'Unable to update {blob_name} in Azure : {e}')

def upload_blob_from_string(file_name, content):
    try:
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)
        blob_client.upload_blob(content, overwrite=True)
    except Exception as e:
        log_error(f'Unable to update {file_name} in Azure : {e}')

def blob_exists(blob_name):
    """Check if a blob exists in the specified container."""
    try:
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        try:
            blob_client.get_blob_properties()
            return True
        except:
            return False
    except Exception as e:
        log_error(f'Unable to check if {blob_name} exists in Azure : {e}')

def company_intel_table(company_name, blob_name="output/kubrick_mi_company_intel.csv"):
    # Check if the blob exists
    if not blob_exists(blob_name):
        # Create an empty DataFrame and upload it to the blob
        empty_df = pd.DataFrame(columns=['Date Collected', 'Company Name', 'URL', 'Training Program Duration',
                                         'Anecdotal Views of Quality', 'Consultant Pricing'])
        csv_content = empty_df.to_csv(index=False)
        upload_string_to_blob(blob_name, csv_content)
    
    try:
        # Download the blob content as a string
        csv_content = download_blob_to_string(blob_name)
        data = pd.read_csv(StringIO(csv_content), encoding='utf-8')
    except UnicodeDecodeError:
        # If there's a Unicode error, try a different encoding
        data = pd.read_csv(StringIO(csv_content), encoding='ISO-8859-1')
    
    data_as_dict = defaultdict(list)
    set1 = set(name for name in list(data['Company Name']))
    set2 = {company_name}
    set1.update(set2)
    names = list(set1)
    names.sort()

    for name in names:
        company_names_column = data.iloc[:, 1]
        company_exists = name in company_names_column.values

        data_as_dict["Date Collected"].append(datetime.now().strftime("%Y-%m-%d"))
        data_as_dict["Company Name"].append(name)
        
        try:
            cols = ['URL','Training Program Duration','Anecdotal Views of Quality','Consultant Pricing']
            if company_exists:
                company_index = company_names_column[company_names_column == name].index[0]
                for col in cols:
                    data_as_dict[col].append(data.at[company_index, col])
                
                for key, value in data_as_dict.items():
                    data.at[company_index, key] = value[0]
                
            else:
                for col in cols:
                    data_as_dict[col].append("To be completed manually")
        
        except Exception as e:
            log_error(f"Error obtaining intel data for {company_name}: {e}")
            return False
    new_data = pd.DataFrame(data_as_dict)
    save_dataframe_to_blob(new_data, blob_name)
    return True

def save_dataframe_to_blob(df, file_path):
    """Save a DataFrame to a blob."""
    try:
        csv_content = df.to_csv(index=False)
        upload_blob_from_string(file_path, csv_content)
    except Exception as e:
        log_error(f'Unable to save data in {file_path} : {e}')

def log_error(message):
    file_name = 'logs/log_error.txt'
    log_message = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message} \n"
    
    try:
        # Download the existing log file content
        log_stream = download_blob_as_string(file_name)
        current_log = log_stream.getvalue()
    except Exception as e:
        # If the log file does not exist, start with an empty log
        current_log = ""

    # Append the new log message
    updated_log = current_log + log_message

    # Upload the updated log content back to Azure Blob Storage
    upload_string_to_blob(file_name, updated_log)

def reallocate_old_df(old_df, file_path, sanitized_name):
    try:
        if old_df.empty:
            return
        else:
            file_name = file_path.rsplit('/', 1)[-1]
            history_file_path = f'/archives/{sanitized_name}/{file_name}'
            # Remove the directory containing the csv_file
            if blob_exists(file_path):
                delete_blob(file_path)
            else:
                pass
            save_dataframe_to_blob(old_df, history_file_path)
    except Exception as e:
        log_error(f'Unable to save old data for {sanitized_name} to {file_path} : {e}')

def log_differences(action, sheet_name, num_differences):
    """
    Log the differences found to a text file.
    
    Args:
    action (str): The action taken (e.g., "Added" or "No differences found").
    sheet_name (str): The name of the sheet.
    num_differences (int): The number of differences found.
    """
    path_file = 'logs/log_diff.txt'
    time_today = datetime.now().strftime("%Y-%m-%d")
    if num_differences == 0:
        log_message = f"{time_today}: No new data for company: '{sheet_name}' \n"
    elif num_differences == 1:
        log_message = f"{time_today}: {action} {num_differences} new data row for company: '{sheet_name}' \n"
    else:
        log_message = f"{time_today}: {action} {num_differences} new data rows for company: '{sheet_name}' \n"
        
    try:
        # Download the existing log file content
        log_stream = download_blob_as_string(path_file)
        current_log = log_stream.getvalue()
    except Exception as e:
        # If the log file does not exist, start with an empty log
        current_log = ""

    # Append the new log message
    updated_log = current_log + log_message

    # Upload the updated log content back to Azure Blob Storage
    upload_string_to_blob(path_file, updated_log)

def get_company_info_pricereport(company_name, ticker, file_path):
    """
    Produces price report for a given company
    
    Args:
    company_name (str): Full company name
    ticker (str): Company ticker. This can be an empty string if the company is private.

    Return:
    (json) : Financial Data to produce the price report
    """

    if ticker == "":
        return {
            "Date of Collection": datetime.now().strftime("%Y-%m-%d"),
            "Company Name": company_name,
            "Previous Close": "Private",
            "%-Change": "Private",
            "Sector": "Private",
            "Currency": "Private",
            "52 Week Range": "Private",
            "Error" : False
        }
    
    try:
        # Fetch company data from Yahoo Finance
        stock = yf.Ticker(ticker)
        info = stock.info
        # Check if the returned info indicates data not found
        if len(info) <= 1:
            error_message = f"Issue with ticker: {company_name} : {info}"
            log_error(error_message)
            return {
                "Date of Collection": datetime.now().strftime("%Y-%m-%d"),
                "Company Name": company_name,
                "Previous Close": "Private",
                "%-Change": "Private",
                "Sector": "Private",
                "Currency": "Private",
                "52 Week Range": "Private",
                "Error" : True
                
            }
        # Try to get historical data
        previous_close = info.get("previousClose", "N/A")
        if previous_close == "N/A":
            error_message = f"Error while retrieving financial data for: {ticker}."
            log_error(error_message)
            return {
                "Date of Collection": datetime.now().strftime("%Y-%m-%d"),
                "Company Name": company_name,
                "Previous Close": "Private",
                "%-Change": "Private",
                "Sector": "Private",
                "Currency": "Private",
                "52 Week Range": "Private",
                "Error" : True
            }
        
        try: 
            df = download_blob(file_path)
            # Check if 'company_name' and the relevant close column exist in the DataFrame
            if 'Company Name' in df.columns and 'Previous Close' in df.columns:
                # Filter the rows where the company_name matches and the close value is a number
                filtered_df = df[(df['Company Name'] == company_name) & (df['Previous Close'].apply(lambda x: x != 'Private'))]

                if not filtered_df.empty:
                    # Get the last close value
                    last_close = float(filtered_df['Previous Close'].iloc[-1])
                    # Calculate the percentage change
                    percent_change = abs(round(((previous_close - last_close) / last_close) * 100, 4))
                else:
                    percent_change = 0
            else:
                percent_change = 0
        except FileNotFoundError:
            percent_change = 0
        
        return {
            "Date of Collection": datetime.now().strftime("%Y-%m-%d"),
            "Company Name": company_name,
            "Previous Close": previous_close,
            "%-Change": percent_change,
            "Sector": info.get("sector", "No Sector Available"),
            "Currency": info.get('currency', "No Currency Available"),
            "52 Week Range": f'{info.get("fiftyTwoWeekLow", "No 52 Week Low Available")} - {info.get("fiftyTwoWeekHigh", "No 52 Week High Available")}',
            "Error" : False
        }
    except Exception as e:
        error_message = f"Error while retrieving financial data for: {company_name}. Exception: {str(e)}"
        log_error(error_message)
        return {
            "Date of Collection": datetime.now().strftime("%Y-%m-%d"),
            "Company Name": company_name,
            "Previous Close": "Private",
            "%-Change": "Private",
            "Sector": "Private",
            "Currency": "Private",
            "52 Week Range": "Private",
            "Error" : True
        }

def get_company_metadata(company_name, company_df):
    company_slice = company_df[(company_df['company_name']==company_name)]
    company_url = company_slice.iloc[0]['company_url']
    scraper = company_slice.iloc[0]['scraper']
    status = company_slice.iloc[0]['status']
    ticker = company_slice.iloc[0]['ticker']

    return company_url, scraper, status, ticker

def get_company_details(status, symbol):
    """
    Obtains yfinance data if company is public.
    
    Args:
    symbol (str) : Company symbol to obtain yfinance data. This could be blank if company doesn't have a symbol

    Returns:
    (json) : Company information
    """

    if status == "Private":
        company_details = {
                "Previous Close": "Private",
                "52 Week Range": "Private",
                "Sector": "Private",
                "Industry": "Private",
                "Full Time Employees": "Private",
                "Market Cap": "Private",
                "Fiscal Year Ends": "Private",
                "Revenue": "Private",
                "EBITDA": "Private",
        }
    elif status == "Public":
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            next_fiscal_year_end_epoch = info.get('nextFiscalYearEnd')
            if next_fiscal_year_end_epoch > 1e12:
                next_fiscal_year_end_epoch /= 1000

            company_details = {
                "Previous Close": info.get("previousClose", np.nan),
                "52 Week Range": f'{info.get("fiftyTwoWeekLow", np.nan)} - {info.get("fiftyTwoWeekHigh", np.nan)}',
                "Sector": info.get("sector", np.nan),
                "Industry": info.get("industry", np.nan),
                "Full Time Employees": info.get("fullTimeEmployees", np.nan),
                "Market Cap": info.get("marketCap", np.nan),
                "Fiscal Year Ends": datetime.fromtimestamp(next_fiscal_year_end_epoch).strftime('%d/%m/%y'),
                "Revenue": info.get("totalRevenue", np.nan),
                "EBITDA": info.get("ebitda", np.nan),
            }
        except Exception as e:
            return f'Error, check {symbol} is a valid ticker'
    return company_details

def column_cleaner(df):
    for column in df.columns:
        column_clean = column.replace('_', ' ')
        df[column] = [f'No {column_clean} Data Available' if data in ('', ' ', None, 'nan', np.nan) else data for data in df[column]]
    
    return df

def table_sorter(df):
    df_sorted = df.map(lambda x: x.strip() if isinstance(x, str) else x)
    return df_sorted.sort_values(by=df_sorted.columns.tolist()).reset_index(drop=True)

def create_final_df(company_name, url, status, json_data, df, template_file_path):
    """
    Creates the final dataframe to be stored using data from webscrape + financial data
    
    Args:
    company_name (str) : Name of company
    url (str) : URL of company
    json_data (json) : Financial data of company
    df (pd.Dataframe) : Webscrape data of comapny

    Returns:
    final_df (pd.Dataframe) : Dataframe with all data in the Template table format
    """
    # Get the current date, company name, and website url metadata
    meta_dict = {'Date of Collection':date.today(), 'Company Name':company_name, 'Website_URL':url, 'Public/Private':status}

    df_copy = df

    columns_list = download_blob(template_file_path).columns.tolist()
    for column in columns_list:
        if column in df_copy.columns:
            pass
        elif column in meta_dict.keys():
            df_copy[column] = meta_dict[column]
        elif column in json_data.keys():
            df_copy[column] = json_data[column]
        else:
            df_copy[column] = ' '

    df_clean = column_cleaner(df_copy)
    final_df = df_clean[columns_list]
    final_df_sorted = table_sorter(final_df)

    return final_df_sorted

def log_new_and_modified_rows(final_df, old_df, path_file, company_name):
    """
    Compare rows between final_df and old_df, update or remove rows accordingly, 
    and handle Excel file updates.

    Args:
    final_df (pd.DataFrame): The most up-to-date dataframe.
    old_df (pd.DataFrame): The older dataframe to compare against.
    path_file (str): Path to save the CSV file.
    company_name (str): Name of the company for logging purposes.
    """
    # Subset to relevant columns
    columns_of_interest = ['Practices', 'Practices_URL', 'Services', 'Services_URL', 'Solutions', 'Solutions_URL']
    df1 = final_df[columns_of_interest].copy()
    df2 = old_df[columns_of_interest].copy()

    # Convert columns to the same data type (string) for comparison
    for column in columns_of_interest:
        df1[column] = df1[column].astype(str)
        df2[column] = df2[column].astype(str)

    # Initialize the temporary DataFrame to store unmatched rows with their status
    temp_df = pd.DataFrame(columns=['Status'] + list(final_df.columns))

    # Keep track of original indices before dropping rows
    original_idx1 = df1.index.tolist()
    original_idx2 = df2.index.tolist()

    # Compare each row in df1 with each row in df2
    for idx1, row1 in df1.iterrows():
        matched = False
        for idx2, row2 in df2.iterrows():
            if row1.equals(row2):
                # If a match is found, remove the row from both dataframes
                df1.drop(idx1, inplace=True)
                df2.drop(idx2, inplace=True)
                matched = True
                break
        if not matched:
            # If no match is found, mark the row as 'Added' and store in temp_df
            full_row1 = final_df.loc[original_idx1[idx1]].copy()
            full_row1['Status'] = 'Added'
            temp_df = pd.concat([temp_df, pd.DataFrame([full_row1])], ignore_index=True)

    # Any remaining rows in df2 are 'Removed'
    for idx2, row2 in df2.iterrows():
        full_row2 = old_df.loc[original_idx2[idx2]].copy()
        full_row2['Status'] = 'Removed'
        temp_df = pd.concat([temp_df, pd.DataFrame([full_row2])], ignore_index=True)

    # If there are any changes, write them to the CSV file
    if not temp_df.empty:
        save_dataframe_to_blob(temp_df, path_file)
        log_differences("Changed", company_name, len(temp_df))
    else:
        # If there are no new or modified rows, delete the CSV file if it exists
        if os.path.exists(path_file):
            os.remove(path_file)
        log_differences("No differences found", company_name, 0)

def update_price_report(data, file_path):

    """
    Updates the sheet "Price Report" with the financial data from a company
    
    Args:
    data (json) : Financial Company data
    """

    try:
        # Check if the file exists
        if blob_exists(file_path):
            # Load existing CSV file
            df = download_blob(file_path)
        else:
            # If the file does not exist, create an empty DataFrame with the appropriate columns
            df = pd.DataFrame(columns=data.keys())

        # Remove the row if the company already exists
        df = df[df['Company Name'] != data["Company Name"]]

        # Append the new data
        new_data = pd.DataFrame([data])
        df = pd.concat([df, new_data], ignore_index=True)

        # Save the updated DataFrame back to the CSV file
        save_dataframe_to_blob(df, file_path)

    except Exception as e:
        log_error(f"Error updating CSV file: {e}")


