import pandas as pd
import SupportFunctions
from datetime import datetime
import re
import logging
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
import os

class AzureBlobStorageHandler(logging.Handler):
    def __init__(self, account_name, container_name, account_key, blob_name):
        super().__init__()
        self.blob_service_client = BlobServiceClient(
            account_url=f"https://{account_name}.blob.core.windows.net",
            credential=account_key
        )
        self.container_name = container_name
        self.blob_name = blob_name

    def emit(self, record):
        log_entry = self.format(record)
        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name, blob=self.blob_name
        )
        try:
            # Read the existing blob content
            existing_logs = blob_client.download_blob().content_as_text()
        except:
            # If the blob doesn't exist, start with an empty string
            existing_logs = ""
        
        # Append the new log entry
        new_logs = existing_logs + log_entry + "\n"
        
        # Upload the updated log content to the blob
        blob_client.upload_blob(new_logs, overwrite=True)

def main():

    # Load the .env file
    load_dotenv()

    # Retrieve the secrets from environment variables
    account_name = os.getenv('ACCOUNT_NAME')
    container_name_log = os.getenv('CONTAINER_NAME')
    account_key = os.getenv('ACCOUNT_KEY')

    # Build the connection string
    connect_str = 'DefaultEndpointsProtocol=https;AccountName=' + account_name + ';AccountKey=' + account_key + ';EndpointSuffix=core.windows.net'
    blob_name_log = 'logs/scrape_app.log'

    # Configure logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Create and add the custom handler
    azure_handler = AzureBlobStorageHandler(account_name, container_name_log, account_key, blob_name_log)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    azure_handler.setFormatter(formatter)
    logger.addHandler(azure_handler)

    # This will need to change to Azure's Blob Storage
    metadata_filepath = f'company_metadata.csv'

    # Read in metadata file
    company_df = SupportFunctions.download_blob(metadata_filepath)
    company_df.fillna('',inplace=True)
    # Filter to exclude not yet completed companies
    mask = company_df['scraper'] != 'to complete'

    company_df = company_df[mask]

    logger.info(f'New run starting at {datetime.now()}')

    intel_file_path = f'output/kubrick_mi_company_intel.csv'
    price_report_file_path = f'output/price_report.csv'
    price_report_run = True
    intel_dict = {'error_num':0, 'company_list':[]}
    scraping_dict = {'error_num': 0, 'company_list': []}
    pricing_dict = {'error_num':0, 'company_list':[]}
    try:
        temporary_df = SupportFunctions.download_blob(price_report_file_path)
        try:
            temporary_df['Date of Collection'] = pd.to_datetime(temporary_df['Date of Collection'], format='mixed')
        except ValueError:
            temporary_df['Date of Collection'] = pd.to_datetime(temporary_df['Date of Collection'], format='%d/%m/%Y')
    
        current_date = pd.to_datetime(datetime.now().strftime('%Y-%m-%d'))

        if max(temporary_df['Date of Collection']) < current_date:
            price_report_run = True
        
    except FileNotFoundError:
        price_report_run = False
        SupportFunctions.log_error('Price Report file could not be found. Starting a price report from scratch.')

    if not price_report_run:
        SupportFunctions.log_error("Price Report cannot run in the same day, please try run tomorrow.")
        price_report_var = False

    for company_name in company_df["company_name"]:
        company_url, scraper, status, ticker = SupportFunctions.get_company_metadata(company_name, company_df)
        company_intel_success = SupportFunctions.company_intel_table(company_name, intel_file_path)
        if not company_intel_success:
            intel_dict['error_num'] +=1
            intel_dict['company_list'].append(company_name)
            logger.error(f"An error occurred for intel data for company : {str(company_name)}", exc_info=True)

        sanitized_name = re.sub(r'[<>:"/\\|?*]', '_', company_name).strip()
        file_paths = f'output/{sanitized_name}'
        file_path = SupportFunctions.get_blob_path_file(file_paths, sanitized_name)
        price_report_file_path = f'output/price_report.csv'
        midiff_file_path = f'output/{sanitized_name}/{sanitized_name} diff.csv'
        template_file_path = 'Template.csv'

        try:
            scraped_data = SupportFunctions.get_scraped_company_data(scraper)
            yahoo_json = SupportFunctions.get_company_details(status, ticker)
            final_df = SupportFunctions.create_final_df(company_name, company_url, status, yahoo_json, scraped_data, template_file_path)
            old_df = SupportFunctions.get_blob_csv_company(sanitized_name)
            SupportFunctions.reallocate_old_df(old_df, file_path, sanitized_name)
            SupportFunctions.log_new_and_modified_rows(final_df, old_df, midiff_file_path, company_name)
            date_today = datetime.now()
            formatted_date = date_today.strftime('%d_%m_%Y')
            filename = f'output/{sanitized_name}/{sanitized_name}_webscrape_{formatted_date}.csv'
            SupportFunctions.save_dataframe_to_blob(final_df, filename)
        except Exception as e:
            scraping_dict['error_num'] += 1
            scraping_dict['company_list'].append(company_name)
            SupportFunctions.log_error(f'Error webscraping for company {company_name} : {e}')
            logger.error(f"Error webscraping for company {company_name} : {e}", exc_info=True)
        if price_report_run:
            temp_data = SupportFunctions.get_company_info_pricereport(company_name, ticker, price_report_file_path)
            if temp_data["Error"]:
                pricing_dict['error_num'] +=1
                pricing_dict['company_list'].append(company_name)
            temp_data.pop("Error", None)
            SupportFunctions.update_price_report(temp_data, price_report_file_path)
    if pricing_dict['error_num'] > 0 or intel_dict['error_num'] > 0 or scraping_dict['error_num'] > 0:
        logger.info(f"{datetime.now()} : Scraping finished with {pricing_dict['error_num']} pricing error(s), {scraping_dict['error_num']} scraping error(s) and {intel_dict['error_num']} shortform error(s). Please check the log files for a list of the companies with errors.")
    else:
        logger.info(f'{datetime.now()} : Run completed without any errors')

if __name__ == "__main__":
    main()