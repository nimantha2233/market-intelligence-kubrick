import tkinter as tk
from customtkinter import *
import pandas as pd
import SupportFunctions
import threading
from datetime import datetime
import os
from collections import defaultdict
import logging

logger_filepath = SupportFunctions.get_data_file_path(filename='scrape_app.log', folder='logs')
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
company_df = company_df[mask]
company_df = company_df.iloc[:3]

df_full_company_list = company_df[['company_name','ticker']].fillna('')
full_company_list = dict(zip(df_full_company_list['company_name'], df_full_company_list['ticker']))


 
class App(CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        set_appearance_mode("dark")
        self.title("Kubrick MI Webscrape")
 
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

    def get_webscrape(self, row, company_df, template_file_path, file_path):
        logger.info(f'New run starting at {datetime.now()}')

        self.currentCompanyLabel_scrape = CTkLabel(self, text="Current Company: None")
        self.currentCompanyLabel_scrape.grid(row=row, column=0, pady=5, sticky="ew")

        self.pPercentage_scrape = CTkLabel(self, text='0%')
        self.pPercentage_scrape.grid(row=row+1, column=1, pady=10, sticky="ew")
        self.progressBar_scrape = CTkProgressBar(self, width=160)
        self.progressBar_scrape.set(0)
        self.progressBar_scrape.grid(row=row+1, column=0, sticky="ew")
        self.update()
        i=0
        scraping_dict = {'error_num':0, 'company_list':[]}
        total_companies = len(company_df["company_name"])
        for company_name in company_df["company_name"]:
            i += 1
            self.currentCompanyLabel_scrape.configure(text=f"Current Company: {company_name}")
            company_url, scraper, status, ticker = SupportFunctions.get_company_metadata(company_name, company_df)
            try:
                scraped_data = SupportFunctions.get_scraped_company_data(scraper)
                yahoo_json = SupportFunctions.get_company_details2(status, ticker)
                final_df = SupportFunctions.create_final_df2(company_name, company_url, status, yahoo_json, scraped_data, template_file_path)
                old_df = SupportFunctions.read_from_excel(file_path, company_name, template_file_path)
                SupportFunctions.log_new_and_modified_rows2(final_df, old_df, company_name, file_path)
                SupportFunctions.write_to_excel(final_df, file_path, company_name)
            except Exception as e:
                logger.error(f"An error occurred: {str(e)}", exc_info=True)
                scraping_dict['error_num'] +=1
                scraping_dict['company_list'].append(company_name)

            progress = i / total_companies
            self.after(0, self.update_progress, progress, company_name, 'scrape')

        if scraping_dict['error_num'] > 0:
            text = f"Scraping finished with {scraping_dict['error_num']} error(s). Please check for changes in the company website for the following companies: {scraping_dict['company_list']}."
            self.currentCompanyLabel_scrape.configure(text=text)

        else:
            text = "Scraping completed successfully. No errors found."
            self.currentCompanyLabel_scrape.configure(text=text)
        
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
        
        self.title.grid_remove()
        self.webscrape_button.grid_remove()
        self.price_report_button.grid_remove()
        self.company_intel_button.grid_remove()
        self.play_button.grid_remove()

        row = 0
        
        file_path = os.path.join(current_dir, 'database', 'Kubrick MI Data.xlsx')
        intel_file_path = os.path.join(current_dir, 'database', 'kubrick_mi_company_intel.csv')
        template_file_path = os.path.join(current_dir, 'Template.xlsx')

        price_report_run = False
        temporary_df = pd.read_excel(file_path, sheet_name="Price Report")
        temporary_df['Date of Collection'] = pd.to_datetime(temporary_df['Date of Collection'], format='%Y-%m-%d')
        current_date = pd.to_datetime(datetime.now().strftime('%Y-%m-%d'), format='%Y-%m-%d')


        if min(temporary_df['Date of Collection']) < current_date:
            price_report_run = True

        print(price_report_run) 

        if self.price_report_var.get() and not price_report_run:
            SupportFunctions.log_error("Price Report cannot run in the same day, please try run tomorrow.")

        if self.webscrape_var.get():
            scrape_thread = threading.Thread(target=self.get_webscrape, args=(row, company_df, template_file_path, file_path))
            row += 2
            scrape_thread.start()
            
        if self.price_report_var.get():
            price_thread = threading.Thread(target=self.get_pricing, args=(row, file_path, full_company_list, price_report_run))
            row += 2
            price_thread.start()

        if self.company_intel_var.get():
            intel_thread = threading.Thread(target=self.get_intel, args=(row, company_df, intel_file_path))
            row += 2
            intel_thread.start()

        # Create Exit button
        exit_button = CTkButton(self, text="Exit", command=self.quit)
        exit_button.grid(row=row, column=0, padx=10, pady=5, sticky="ew")

 
app = App()
app.mainloop()