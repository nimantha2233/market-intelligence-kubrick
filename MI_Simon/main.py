import tkinter as tk
from customtkinter import *
import pandas as pd
import SupportFunctions
import threading
from datetime import datetime
import os
from collections import defaultdict

# Get the directory path of main.py
current_dir = os.path.dirname(os.path.abspath(__file__))

company_dict = {
    "company_name": [
        "EPAM Systems Inc",
        "Edge Testing Solutions",
        "DXC Technology",
        "Deloitte",
        "Cognifide",
        "CGI",
        "Canon Inc.",
        "Billigence",
        "Avanade Inc.",
        "Arthur D Little",
        "Alchemmy",
        "Adatis",
        "Grayce Group Limited",
        "Rockborne Limited",
        "Digital Futures",
        "Thoughtworks",
        "Wavestone",
        "ZS",
        "PwC",
        "Softwire",
        "Sutherland",
        "TAG Solutions",
        "Testhouse Ltd",
        "NexInfo",
        "Oliver Wyman",
        "PA Consulting",
        "Planit Testing",
        "Project One",
        "Laboratory Corp Of America Holdings",
        "LogicSource, Inc.",
        "Made Tech",
        "METRICSTREAM INC",
        "Mphasis Ltd",
        "Frontier Economics",
        "HCL Technologies Ltd",
        "Icon PLC",
        "International Business Machines Corp",
        "Kearney",
        "Credo Consulting",
        "Digital Workplace Group",
        "Eden McCallum",
        "Enfuse Group",
        "EY",
        "Blueberry Consultants Ltd",
        "Blueberry Consultants Ltd",
        "Cambridge Design Partnership",
        "Centric Consulting",
        "Clarasys",
        "Accenture PLC",
        "Airwalk Reply",
        "Apexon",
        "Atos SE",
        "Baringa",
        "Capgemini SE",
        "AND Digital",
        "Dufrain",
        "FDM Group (Holdings) Ltd",
        "Slalom",
        "Tata Consultancy Services Limited",
        "Wipro Limited",
        "Infosys Limited",
        "Credera",
        "Infinite Lambda",
        "Mesh AI",
        "Sparta Global",
        "Ten10",
        "Fjord Consulting Group",
        "BetterGov",
        "Cambridge Consultants Limited",
        "Capco Limited",
        "Cognizant Technology Solutions Corporation",
        "IQVIA Holdings Inc",
        "Kubrick Group Limited",
        "Hexaware Technologies Ltd",
        "JMAN Group",
        "KONICA MINOLTA INC",
        "LockPath, Inc.",
        "Lovelytics",
        "Mason Advisory",
        "MindTree Ltd",
        "mthree",
        "North Highland",
        "OpenCredo",
        "PPD Inc",
        "Projective",
    ],
    "company_url": [
        "https://www.epam.com/",
        "https://www.resillion.com/",
        "https://dxc.com/uk/en",
        "https://www.deloitte.com/global/en.html",
        "https://www.vml.com",
        "https://www.cgi.com/",
        "https://www.canon.co.uk",
        "https://billigence.com",
        "https://www.avanade.com",
        "https://www.adlittle.com",
        "https://alchemmy.com/",
        "https://adatis.co.uk/",
        "https://www.grayce.co.uk",
        "https://rockborne.com/",
        "https://digitalfutures.com/",
        "https://www.thoughtworks.com/en-gb",
        "https://www.wavestone.com/en/",
        "https://www.zs.com/",
        "https://www.pwc.co.uk",
        "https://www.softwire.com",
        "https://www.sutherlandglobal.com/",
        "https://tagsolutions.com/",
        "https://www.testhouse.net/",
        "https://nexinfo.com/",
        "https://www.oliverwyman.com/",
        "https://www.paconsulting.com/",
        "https://www.planit.com/au/home",
        "https://projectone.com/",
        "https://biopharma.labcorp.com/",
        "https://logicsource.com/",
        "https://www.madetech.com/",
        "https://www.metricstream.com/",
        "https://www.mphasis.com/",
        "https://www.frontier-economics.com/uk/en/home/",
        "https://www.hcltech.com/",
        "https://www.iconplc.com/",
        "https://www.ibm.com/uk-en",
        "https://www.kearney.com/",
        "https://www.credoconsultancy.co.uk/",
        "https://digitalworkplacegroup.com/",
        "https://edenmccallum.com/",
        "https://www.enfusegroup.com/",
        "https://www.ey.com/en_uk",
        "https://www.bbconsult.co.uk/",
        "https://www.bcg.com/",
        "https://www.cambridge-design.com/",
        "https://centricconsulting.com/",
        "https://www.clarasys.com/",
        "https://www.accenture.com/gb-en",
        "https://airwalkreply.com/",
        "https://www.apexon.com/",
        "https://atos.net/en/",
        "https://www.baringa.com/en/",
        "https://www.capgemini.com/",
        "https://www.and.digital/",
        "https://www.dufrain.co.uk/",
        "https://www.fdmgroup.com/",
        "https://www.slalom.com/",
        "https://www.tcs.com",
        "https://www.wipro.com/",
        "https://www.infosys.com/",
        "https://www.credera.com/en-gb",
        "https://infinitelambda.com",
        "https://www.mesh-ai.com/",
        "https://www.spartaglobal.com",
        "https://ten10.com",
        "https://fjordconsultinggroup.com",
        "https://www.bettergov.co.uk/",
        "https://www.cambridgeconsultants.com/",
        "https://www.capco.com",
        "https://www.cognizant.com",
        "https://jobs.iqvia.com/en",
        "https://www.kubrickgroup.com",
        "https://hexaware.com/",
        "https://jmangroup.com/",
        "https://www.konicaminolta.co.uk/en-gb",
        "https://www.navex.com/en-gb/",
        "https://lovelytics.com",
        "https://masonadvisory.com/services/",
        "https://www.mindtreeitsolutions.com/",
        "https://mthree.com/",
        "https://www.northhighland.com/",
        "https://opencredo.com/",
        "https://www.ppd.com/",
        "https://www.projectivegroup.com/",
    ],
    "status": [
        "Public",
        "Private",
        "Public",
        "Private",
        "Private",
        "Private",
        "Public",
        "Private",
        "Private",
        "Private",
        "Private",
        "Private",
        "Private",
        "Private",
        "Private",
        "Private",
        "Private",
        "Private",
        "Private",
        "Private",
        "Private",
        "Private",
        "Private",
        "Private",
        "Private",
        "Private",
        "Private",
        "Private",
        "Public",
        "Private",
        "Public",
        "Private",
        "Public",
        "Private",
        "Public",
        "Public",
        "Public",
        "Private",
        "Private",
        "Private",
        "Private",
        "Private",
        "Private",
        "Private",
        "Private",
        "Private",
        "Private",
        "Private",
        "Public",
        "Private",
        "Private",
        "Public",
        "Private",
        "Public",
        "Private",
        "Private",
        "Public",
        "Private",
        "Public",
        "Public",
        "Public",
        "Private",
        "Private",
        "Private",
        "Private",
        "Private",
        "Private",
        "Private",
        "Private",
        "Private",
        "Public",
        "Public",
        "Private",
        "Private",
        "Private",
        "Public",
        "Private",
        "Private",
        "Private",
        "Private",
        "Private",
        "Private",
        "Private",
        "Private",
        "Private",
    ],
    "ticker": [
        "EPAM",
        "",
        "DXC",
        "",
        "",
        "",
        "7751.T",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "LAB.F",
        "",
        "MTEC.L",
        "",
        "MPHASIS.BO",
        "",
        "HCLTECH.BO",
        "ICLR",
        "IBM",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "ACN",
        "",
        "",
        "ATO.PA",
        "",
        "CAP.PA",
        "",
        "",
        "FDM.L",
        "",
        "TCS.BO",
        "WIT",
        "INFY",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "CTSH",
        "IQV",
        "",
        "",
        "",
        "KNCAF",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
    ],
    "scraper": [
        "scraper_epam",
        "scraper_resillion",
        "scraper_dxc",
        "scraper_deloitte",
        "scraper_vml",
        "scraper_cgi",
        "scraper_canon",
        "scraper_billigence",
        "scraper_avanade",
        "scraper_adlittle",
        "scraper_alchemmy",
        "scraper_adatis",
        "scraper_grayce",
        "scraper_rockborne",
        "scraper_digitalfutures",
        "scraper_thoughtworks",
        "scraper_wavestone",
        "scraper_zs",
        "scraper_pwc",
        "scraper_softwire",
        "scraper_sutherland",
        "scraper_tagsolutions",
        "scraper_testhouse",
        "scraper_nexinfo",
        "scraper_oliverwyman",
        "scraper_paconsulting",
        "scraper_planittesting",
        "scraper_projectone",
        "scraper_labcorp",
        "scraper_logicsource",
        "scraper_madetech",
        "scraper_metricstream",
        "scraper_mphasis",
        "scraper_frontiereconomics",
        "scraper_hcltech",
        "scraper_iconplc",
        "scraper_ibm",
        "scraper_kerney",
        "scraper_credo",
        "scraper_digitalworkplace",
        "scraper_edenmccallum",
        "scraper_enfuse",
        "scraper_ey",
        "scraper_blueberry",
        "scraper_boston",
        "scraper_cambridgedesign",
        "scraper_centric",
        "scraper_clarasys",
        "scraper_accenture",
        "scraper_airwalkreply",
        "scraper_apexon",
        "scraper_atosse",
        "scraper_baringa",
        "scraper_capgemini",
        "scraper_digital",
        "scraper_dufrain",
        "scraper_fdmgroup",
        "scraper_slalom",
        "scraper_tcs",
        "scraper_wipro",
        "scraper_infosys",
        "scraper_credera",
        "scraper_infinitelambda",
        "scraper_meshai",
        "scraper_spartaglobal",
        "scraper_ten10",
        "scraper_fjord",
        "scraper_bettergov",
        "scraper_cambridge",
        "scraper_capco",
        "scraper_cognizant",
        "scraper_iqvia",
        "scraper_kubrick",
        "scraper_hexaware",
        "scraper_jman",
        "scraper_konica",
        "scraper_lockpath",
        "scraper_lovelytics",
        "scraper_mason",
        "scraper_mindtree",
        "scraper_mthree",
        "scraper_highland",
        "scraper_credo",
        "scraper_ppd",
        "scraper_projective",
    ],
}

company_df = pd.DataFrame(company_dict)

full_company_list = {
    'Capgemini SE' : 'CAP.PA',
    'AND Digital' : '',
    'Dufrain' : '',
    'FDM Group (Holdings) Ltd' : 'FDM.L',
    'Slalom' : '',
    'Tata Consultancy Services Limited' : 'TCS.BO',
    'Wipro Limited' : 'WIT',
    'Fjord Consulting Group' : '',
    'Mesh AI' : '',
    'Sparta Global' : '',
    'Ten10' : '',
    'Credera' : '',
    'Infinite Lambda' : '',
    'BetterGov' : '',
    'Cambridge Consultants Limited' : '',
    'Capco Limited' : '',
    'Cognizant Technology Solutions Corporation' : 'CTSH',
    'Infosys Limited' : 'INFY',
    'IQVIA Holdings Inc' : 'IQV',
    'Kubrick Group Limited' : '',
    '11:FS' : '',
    'a1qa' : '',
    'Accenture PLC' : 'ACN',
    'Adatis' : '',
    'Afiniti' : '',
    'Airwalk Reply' : '',
    'Alchemmy' : '',
    'Alix Partners' : '',
    'Apexon' : '',
    'Arthur D Little' : '',
    'Atos Group' : '', # Unsure on what the ticker is? Mentioned it is public in excel by Simon
    'Atos SE' : 'ATO.PA',
    'Avanade Inc.' : '',
    'Bain & Company' : '',
    'Baringa' : '',
    'Billigence' : '',
    'BJSS' : '',
    'Blueberry Consultants Ltd.' : '',
    'Booz Allen Hamilton Holding Corp' : 'BAH',
    'Boston Consulting Group' : '',
    'Broadstones Tech' : '',
    'Cambridge Design Partnership' : '',
    'Canon Inc.' : '7751.T',
    'Capita' : 'CPI.L',
    'Centric Consulting' : '',
    'CGI' : '',
    'CIGNITI Technologies Ltd' : 'CIGNITITEC.BO',
    'Clarasys' : '',
    'Cognifide' : '',
    'Contino Ltd.' : '',
    'Credo Consulting' : '',
    'Deloitte' : '',
    'Designit' : '',
    'Digital Workplace Group' : '',
    'DXC Technology' : 'DXC',
    'Eclature Technologies' : '',
    'Eden McCallum' : '',
    'Edge Testing Solutions' : '',
    'Elixirr International Plc' : 'ELIX.L',
    'EPAM Systems Inc' : 'EPAM',
    'Equal Experts' : '',
    'EY' : '',
    'Faculty AI' : '',
    'Frog Design' : '',
    'Frontier Economics' : '',
    'GeekTek' : '',
    'Genpact Ltd' : 'G',
    'HCL Technologies Ltd' : 'HCLTECH.BO',
    'Hexaware Technologies Ltd' : '',
    'HP Inc' : 'HPQ',
    'Icon PLC' : 'ICLR',
    'IDEO' : '',
    'Infostretch Corp' : '',
    'International Business Machines Corp' : 'IBM',
    'JMAN Group' : '',
    'Kainos' : 'KNOS.L',
    'Kearney' : '',
    'KONICA MINOLTA INC' : 'KNCAF',
    'KPMG' : '',
    'Laboratory Corp Of America Holdings' : 'LAB.F',
    'LockPath, Inc.' : '',
    'LogicManager' : '',
    'LogicSource, Inc.' : '',
    'Lovelytics' : '',
    'Lunar' : '',
    'Made Tech Group Plc ' : 'MTEC.L',
    'Mason Advisory' : '',
    'McKinsey' : '',
    'METRICSTREAM INC' : '',
    'MindTree Ltd' : '',
    'Mosaic Island' : '',
    'Mphasis Ltd' : 'MPHASIS.BO',
    'mthree' : '',
    'Neoris' : '',
    'NexInfo' : '',
    'North Highland' : '',
    'OC&C Strategy Consultants' : '',
    'Oliver Wyman' : '',
    'OpenCredo' : '',
    'Oracle Consulting' : '',
    'PA Consulting Group' : '',
    'Parexel International Corp' : '',
    'Peru Consulting' : '',
    'Planit Testing' : '',
    'PPD Inc' : '',
    'PRA Health Sciences Inc' : '',
    'Project One' : '',
    'Projective' : '',
    'Prolifics' : '',
    'PwC' : '',
    'RICOH CO LTD' : 'RICO.L',
    'Roland Berger' : '',
    'SEIKO EPSON CORP' : 'SEKEY',
    'Simon Kutcher & Partners' : '',
    'SkillStorm' : '',
    'Softwire' : '',
    'Spring Studios' : '',
    'Strategy & London' : '',
    'Sutherland' : '',
    'Switchfast Technologies' : '',
    'Syneos Health Inc' : '',
    'TAG Solutions' : '',
    'Tech Mahindra Ltd' : 'TECHM.BO',
    'Terillium' : '',
    'Testhouse Ltd' : '',
    'The Berkeley Partnership' : '',
    'The PSC' : '',
    'Thoughtworks' : '7W8.F',
    'Ultimus Fund Solutions' : '',
    'Verisk Analytics Inc' : 'VRSK',
    'Wavestone' : 'WAVE.PA',
    'Xerox Corp' : '',
    'Zoonou' : '',
    'ZS' : '',
    'Digital Futures' : '',
    'Rockborne Limited' : '',
    'Grayce Group Limited' : ''

}

 
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
            except:
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
        for company_name in company_dict["company_name"]:
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
        
        file_path = SupportFunctions.get_data_file_path('Kubrick MI Data.xlsx')
        midiff_file_path = SupportFunctions.get_data_file_path('Kubrick MI Diff.xlsx')
        intel_file_path = SupportFunctions.get_data_file_path('kubrick_mi_company_intel.csv')
        template_file_path = SupportFunctions.get_data_file_path('Template.xlsx')

        price_report_run = False
        temporary_df = pd.read_excel(file_path, sheet_name="Price Report")
        temporary_df['Date of Collection'] = pd.to_datetime(temporary_df['Date of Collection'], format='%Y-%m-%d')
        current_date = pd.to_datetime(datetime.now().strftime('%Y-%m-%d'), format='%Y-%m-%d')


        if min(temporary_df['Date of Collection']) < current_date:
            price_report_run = True

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