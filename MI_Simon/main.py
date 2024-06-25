import tkinter as tk
from customtkinter import *
import pandas as pd
import SupportFunctions
import threading
import queue
from datetime import datetime
import os
import re
import logging
import glob

logger_filepath = SupportFunctions.get_data_file_path(filename='scrape_app.log', folder='database\logs')
logging.basicConfig(filename=logger_filepath, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get the directory path of main.py
current_dir = os.path.dirname(os.path.abspath(__file__))
metadata_filepath = SupportFunctions.get_data_file_path(filename = 'company_metadata.csv')

# Read in metadata file
company_df = pd.read_csv(filepath_or_buffer=metadata_filepath, index_col = 0)
company_df.fillna('',inplace=True)
# Filter to exclude not yet completed companies
mask = company_df['scraper'] != 'to complete'

df_full_company_list = company_df[['company_name','ticker']].fillna('')
company_df = company_df[mask]
full_company_list = dict(zip(df_full_company_list['company_name'], df_full_company_list['ticker']))

class App(CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        set_appearance_mode("dark")
        self.title("Kubrick MI Webscrape")

        # Set the window size (width x height)
        window_width = 310
        window_height = 200

        # Get the screen width and height
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Calculate the position to center the window
        position_right = int(screen_width/2 - window_width/2)
        position_down = int(screen_height/2 - window_height/2)

        # Set the geometry with the calculated position
        self.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")

        self.grid_columnconfigure(0, weight=1)

        # Login Window title
        self.title = CTkLabel(self, text="Select an option and click Start.")
        self.title.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
 
        # Username label and entry box
        self.webscrape_var = BooleanVar()
        self.webscrape_button = CTkCheckBox(self, text="Webscrape", variable=self.webscrape_var)
        self.webscrape_button.grid(row=1, column=0, padx=20, pady=5, sticky="ew")

        self.price_report_var = BooleanVar()
        self.price_report_button = CTkCheckBox(self, text="Price Report", variable=self.price_report_var)
        self.price_report_button.grid(row=2, column=0, padx=20, pady=5, sticky="ew")

        self.company_intel_var = BooleanVar()
        self.company_intel_button = CTkCheckBox(self, text="Company Intel", variable=self.company_intel_var)
        self.company_intel_button.grid(row=3, column=0, padx=20, pady=5, sticky="ew")

        # Play button
        self.play_button = CTkButton(self, text="Start", command=self.start_scraping_thread)
        self.play_button.grid(row=4, column=0, pady=10, sticky="ew")

    def update_progress(self, progress, company_name, bar):
        # Update the progress bar and label
        if bar == 'scrape':
            self.currentCompanyLabel_scrape.configure(text=f"Current Company: {company_name}")
            self.progressBar_scrape.set(progress)
            self.pPercentage_scrape.configure(text=f'{int(progress*100)}%')
            self.update_idletasks()
        
        if bar == 'intel':
            self.currentCompanyLabel_intel.configure(text=f"Current Company: {company_name}")
            self.progressBar_intel.set(progress)
            self.pPercentage_intel.configure(text=f'{int(progress*100)}%')
            self.update_idletasks()

        if bar == 'price':
            self.currentCompanyLabel_price.configure(text=f"Current Company: {company_name}")
            self.progressBar_price.set(progress)
            self.pPercentage_price.configure(text=f'{int(progress*100)}%')
            self.update_idletasks()                   

    def get_webscrape(self, row, company_df):
        # Partition the company names into chunks
        total_companies = len(company_df["company_name"])
        chunk_size = total_companies // 5  # Number of companies per chunk
        chunks = [company_df["company_name"][i:i+chunk_size] for i in range(0, total_companies, chunk_size)]

        threads = []
        self.lock = threading.Lock()  # Create a lock for thread-safe operations
        self.progress_counter = 0  # Shared progress counter
        error_queue = queue.Queue()  # Queue to collect errors from threads

        self.currentCompanyLabel_scrape = CTkLabel(self, text="Current Company: None")
        self.currentCompanyLabel_scrape.grid(row=row, column=0, pady=5, sticky="ew")

        self.pPercentage_scrape = CTkLabel(self, text='0%')
        self.pPercentage_scrape.grid(row=row+1, column=1, pady=10, sticky="ew")
        self.progressBar_scrape = CTkProgressBar(self, width=160)
        self.progressBar_scrape.set(0)
        self.progressBar_scrape.grid(row=row+1, column=0, sticky="ew")
        self.update()

        # Create and start a thread for each chunk
        for chunk in chunks:
            scrape_thread = threading.Thread(target=self.scrape_chunk, args=(row, chunk, company_df, total_companies, error_queue))
            threads.append(scrape_thread)
            scrape_thread.start()
            row += 2  # Update the row for the next thread

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Collect error information from the queue
        error_dict = {'error_num': 0, 'company_list': []}
        while not error_queue.empty():
            errors = error_queue.get()
            error_dict['error_num'] += errors['error_num']
            error_dict['company_list'].extend(errors['company_list'])

            # Display the final message
        if error_dict['error_num'] > 0:
            text = f"Scraping finished with {error_dict['error_num']} error(s). Please check the log files for a list of the companies with errors."
        else:
            text = "Scraping completed successfully. No errors found."
        self.currentCompanyLabel_scrape.configure(text=text)

    def scrape_chunk(self, row, chunk, company_df, total_companies, error_queue):
        i = 0
        scraping_dict = {'error_num': 0, 'company_list': []}
        for company_name in chunk:
            i += 1
            company_url, scraper, status, ticker = SupportFunctions.get_company_metadata(company_name, company_df)
            sanitized_name = re.sub(r'[<>:"/\\|?*]', '_', company_name).strip()
            file_paths = SupportFunctions.get_data_file_path(f'*webscrape*.csv', f'database\output\{sanitized_name}')
            file_paths = glob.glob(file_paths)
            if len(file_paths) > 0:
                file_path = file_paths[0]
            else:
                file_path = SupportFunctions.get_data_file_path(f'file_not_found.csv', f'database\output\{sanitized_name}')
            midiff_file_path = SupportFunctions.get_data_file_path(f'{sanitized_name} diff.csv', f'database\output\{sanitized_name}')
            template_file_path = SupportFunctions.get_data_file_path('Template.csv')
            try:
                scraped_data = SupportFunctions.get_scraped_company_data(scraper)
                yahoo_json = SupportFunctions.get_company_details2(status, ticker)
                final_df = SupportFunctions.create_final_df2(company_name, company_url, status, yahoo_json, scraped_data, template_file_path)
                old_df = SupportFunctions.read_from_csv(file_path, company_name, template_file_path)
                SupportFunctions.reallocate_old_df(old_df, file_path, sanitized_name)
                SupportFunctions.log_new_and_modified_rows3(final_df, old_df, midiff_file_path, company_name)
                SupportFunctions.write_to_csv(final_df, file_path, sanitized_name)
            except Exception as e:
                scraping_dict['error_num'] += 1
                scraping_dict['company_list'].append(company_name)
                SupportFunctions.log_error(f'Error webscraping for company {company_name} : {e}')
                logger.error(f"An error occurred: {str(e)}", exc_info=True)

            with self.lock:  # Use lock to update the shared progress counter safely
                self.progress_counter += 1
                progress = self.progress_counter / total_companies
                self.after(0, self.update_progress, progress, company_name, 'scrape')
        # Put the error information into the queue
        error_queue.put(scraping_dict)
        return

    def get_intel(self, row, company_df, intel_file_path):

        self.currentCompanyLabel_intel = CTkLabel(self, text="Current Company: None")
        self.currentCompanyLabel_intel.grid(row=row, column=0, pady=5, sticky="ew")

        self.pPercentage_intel = CTkLabel(self, text='0%')
        self.pPercentage_intel.grid(row=row+1, column=1, pady=10, sticky="ew")
        self.progressBar_intel = CTkProgressBar(self, width=160)
        self.progressBar_intel.set(0)
        self.progressBar_intel.grid(row=row+1, column=0, sticky="ew")
        self.update()
        i=0
        intel_dict = {'error_num':0, 'company_list':[]}
        total_companies = len(company_df["company_name"])
        for company_name in company_df["company_name"]:
            i += 1
            self.currentCompanyLabel_intel.configure(text=f"Current Company: {company_name}")
            company_url, scraper, status, ticker = SupportFunctions.get_company_metadata(company_name, company_df)
            company_intel_success = SupportFunctions.company_intel_table(company_name, intel_file_path)
            if not company_intel_success:
                intel_dict['error_num'] +=1
                intel_dict['company_list'].append(company_name)
                logger.error(f"An error occurred for intel data for company : {str(company_name)}", exc_info=True)

            progress = i / total_companies
            self.after(0, self.update_progress, progress, company_name, 'intel')

        if intel_dict['error_num'] > 0:
            text = f"Intel report finished with {intel_dict['error_num']} error(s). Please check for intel changes with the following companies: {intel_dict['company_list']}."
            self.currentCompanyLabel_intel.configure(self, text=text)

        else:
            text="Intel report completed successfully. No errors found."
            self.currentCompanyLabel_intel.configure(self, text=text)

        return

    def get_pricing(self, row, file_path, full_company_list, price_report_run):
        self.currentCompanyLabel_price = CTkLabel(self, text="Current Company: None")
        self.currentCompanyLabel_price.grid(row=row, column=0, pady=5, sticky="ew")
        self.pPercentage_price = CTkLabel(self, text='0%')
        self.pPercentage_price.grid(row=row+1, column=1, pady=10, sticky="ew")
        self.progressBar_price = CTkProgressBar(self, width=160)
        self.progressBar_price.grid(row=row+1, column=0, sticky="ew")
        self.progressBar_price.set(0)
        self.update()

        if not price_report_run:
            self.currentCompanyLabel_price.configure(self, text="Pricing report has already been run today. Please try again tomorrow or remove today's data.")

        else:
            i = 0
            pricing_dict = {'error_num':0, 'company_list':[]}
            for full_company_name, full_company_ticker in full_company_list.items():
                i += 1
                temp_data = SupportFunctions.get_company_info_pricereport2(full_company_name, full_company_ticker, file_path)
                if temp_data["Error"]:
                    pricing_dict['error_num'] +=1
                    pricing_dict['company_list'].append(full_company_name)
                    logger.error(f"An error occurred for price report for : {str(full_company_name)}", exc_info=True)
                    break
                temp_data.pop("Error", None)
                SupportFunctions.update_excel(temp_data, file_path)
                progress = i / len(full_company_list)
                self.after(0, self.update_progress, progress, full_company_name, 'price')

            if pricing_dict['error_num'] > 0:
                text = f"Price report finished with {pricing_dict['error_num']} error(s). Please check yahoo finance changes for the following companies: {pricing_dict['company_list']}."
                self.currentCompanyLabel_price.configure(self, text=text)

            else:
                text="Pricing report completed successfully. No errors found."
                self.currentCompanyLabel_price.configure(self, text=text)

        return
            
    def start_scraping_thread(self):
    # Start the long-running task in a separate thread
        threading.Thread(target=self.main_scrape).start()

    def main_scrape(self):

        if not self.webscrape_var.get() and not self.price_report_var.get() and not self.company_intel_var.get():
            tk.messagebox.showwarning("No Option Selected", "Please select at least one option before starting.")
            return
        

        logger.info(f'New run starting at {datetime.now()}')
        self.title.grid_remove()
        self.webscrape_button.grid_remove()
        self.price_report_button.grid_remove()
        self.company_intel_button.grid_remove()
        self.play_button.grid_remove()

        row = 0
        
        intel_file_path = SupportFunctions.get_data_file_path('kubrick_mi_company_intel.csv', 'database\output')
        price_report_file_path = SupportFunctions.get_data_file_path('price_report.csv', f'database\output')

        price_report_run = False

        try:
            temporary_df = pd.read_csv(price_report_file_path)
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

        # Set the geometry with the calculated position
        self.geometry(f"400x{20 + 100*((self.price_report_var.get() and price_report_run) + self.webscrape_var.get() + self.price_report_var.get())}")

        if self.price_report_var.get() and not price_report_run:
            SupportFunctions.log_error("Price Report cannot run in the same day, please try run tomorrow.")

        if self.webscrape_var.get():
            scrape_thread = threading.Thread(target=self.get_webscrape, args=(row, company_df))
            row += 2
            scrape_thread.start()  

        if self.price_report_var.get():
            price_thread = threading.Thread(target=self.get_pricing, args=(row, price_report_file_path, full_company_list, price_report_run))
            row += 2
            price_thread.start()

        if self.company_intel_var.get() and price_report_run:
            intel_thread = threading.Thread(target=self.get_intel, args=(row, company_df, intel_file_path))
            row += 2
            intel_thread.start()

        # Create Exit button
        exit_button = CTkButton(self, text="Exit", command=self.quit)
        exit_button.grid(row=row, column=0, padx=10, pady=5, sticky="ew")

app = App()
app.mainloop()