import tkinter
import customtkinter
import pandas as pd
import SupportFunctions
import threading
from datetime import datetime
import os
from collections import defaultdict

# Get the directory path of main.py
current_dir = os.path.dirname(os.path.abspath(__file__))
info_filepath = SupportFunctions.get_data_file_path(filename = 'company_info.csv')


company_dict = {'company_name':['Capgemini SE', 'AND Digital', 'Dufrain', 'FDM Group (Holdings) Ltd', 'Slalom', 'Tata Consultancy Services Limited', 'Wipro Limited', 'Infosys Limited', 'Credera', 'Infinite Lambda', 'Mesh AI', 'Sparta Global', 'Ten10', 'Fjord Consulting Group', 'BetterGov', 'Cambridge Consultants Limited', 'Capco Limited', 'Cognizant Technology Solutions Corporation', 'IQVIA Holdings Inc', 'Kubrick Group Limited'],
        'company_url':['https://www.capgemini.com/','https://www.and.digital/','https://www.dufrain.co.uk/','https://www.fdmgroup.com/','https://www.slalom.com/','https://www.tcs.com','https://www.wipro.com/', 'https://www.infosys.com/', 'https://www.credera.com/en-gb', 'https://infinitelambda.com', 'https://www.mesh-ai.com/', 'https://www.spartaglobal.com', 'https://ten10.com', 'https://fjordconsultinggroup.com', 'https://www.bettergov.co.uk/', 'https://www.cambridgeconsultants.com/', 'https://www.capco.com', 'https://www.cognizant.com', 'https://www.iqvia.com/', 'https://www.kubrickgroup.com'],
        'status':['Public','Private','Private','Public','Private','Public','Public', 'Public', 'Private', 'Private', 'Private', 'Private', 'Private', 'Private', 'Private', 'Private', 'Private', 'Public', 'Public', 'Private'],
        'ticker':['CAP.PA', '', '', 'FDM.L', '','TCS.BO','WIT', 'INFY', '', '', '', '', '', '', '', '', '', 'CTSH', 'IQV', ''],
        'scraper':['scraper_capgemini','scraper_digital','scraper_dufrain','scraper_fdmgroup','scraper_slalom','scraper_tcs','scraper_wipro', 'scraper_infosys', 'scraper_credera', 'scraper_infinitelambda', 'scraper_meshai', 'scraper_spartaglobal', 'scraper_ten10', 'scraper_fjord', 'scraper_bettergov', 'scraper_cambridge', 'scraper_capco', 'scraper_cognizant', 'scraper_iqvia', 'scraper_kubrick']}

company_df = pd.DataFrame(company_dict)

company_df  = pd.read_csv(info_filepath)
company_df = company_df.iloc[1:4]


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
}


# Get the directory path of main.py
current_dir = os.path.dirname(os.path.abspath(__file__))

def create_app():
    # System Settings
    customtkinter.set_appearance_mode("dark")
    customtkinter.set_default_color_theme("blue")

    # App frame
    app = customtkinter.CTk()
    app.geometry("320x280")
    app.title("Kubrick MI Webscrape")

    # UI elements
    title = customtkinter.CTkLabel(app, text="Select an option and click Start.")
    title.pack(padx=10, pady=10)
    # Option buttons
    webscrape_var = customtkinter.BooleanVar()
    price_report_var = customtkinter.BooleanVar()
    company_intel_var = customtkinter.BooleanVar()

    webscrape_button = customtkinter.CTkCheckBox(app, text="Webscrape", variable=webscrape_var)
    webscrape_button.pack(pady=5)

    price_report_button = customtkinter.CTkCheckBox(app, text="Price Report", variable=price_report_var)
    price_report_button.pack(pady=5)

    company_intel_button = customtkinter.CTkCheckBox(app, text="Company Intel", variable=company_intel_var)
    company_intel_button.pack(pady=5)

    # Current Company being scraped
    currentCompanyLabel = customtkinter.CTkLabel(app, text="Current Company: None")
    currentCompanyLabel.pack(pady=5)

    # Frame for progress bar and percentage
    progressFrame = customtkinter.CTkFrame(app)
    progressFrame.pack(pady=5)

    # Progress percentage
    pPercentage = customtkinter.CTkLabel(progressFrame, text='0%')
    pPercentage.pack(side=tkinter.LEFT, padx=5)

    # Progress bar
    progressBar = customtkinter.CTkProgressBar(progressFrame, width=160)
    progressBar.set(0)
    progressBar.pack(side=tkinter.LEFT, padx=5)
    

    # Play button
    play_button = customtkinter.CTkButton(app, text="Start", 
                                          command=lambda: start_scraping_thread(app, title, currentCompanyLabel, pPercentage, progressBar, 
                                                                                finishLabel, play_button, progressFrame, webscrape_var, 
                                                                                price_report_var,company_intel_var, webscrape_button,
                                                                                price_report_button, company_intel_button))
    play_button.pack(pady=10)

    # Finished Downloading
    finishLabel = customtkinter.CTkLabel(app, text="")
    finishLabel.pack(pady=10)

    return app

def start_scraping_thread(app, title, currentCompanyLabel, pPercentage, progressBar, 
                          finishLabel, play_button, progressFrame, webscrape_var, 
                          price_report_var, company_intel_var, webscrape_button,
                          price_report_button, company_intel_button):
    # Start the long-running task in a separate thread
    threading.Thread(target=main_scrape, args=(app, title, currentCompanyLabel, pPercentage, progressBar, 
                                               finishLabel, play_button, progressFrame, webscrape_var, 
                                               price_report_var, company_intel_var, webscrape_button,
                                               price_report_button, company_intel_button)).start()

def update_progress(app, currentCompanyLabel, pPercentage, progressBar, progress, company_name):
    # Update the progress bar and label
    currentCompanyLabel.configure(text=f"Current Company: {company_name}")
    progressBar.set(progress)
    pPercentage.configure(text=f'{int(progress*100)}%')
    app.update_idletasks()



def main_scrape(app, title, currentCompanyLabel, pPercentage, progressBar, 
                finishLabel, play_button, progressFrame, webscrape_var, 
                price_report_var,company_intel_var, webscrape_button,
                price_report_button, company_intel_button):

    if not webscrape_var.get() and not price_report_var.get() and not company_intel_var.get():
        tkinter.messagebox.showwarning("No Option Selected", "Please select at least one option before starting.")
        return
    
    title.pack_forget()
    webscrape_button.pack_forget()
    price_report_button.pack_forget()
    company_intel_button.pack_forget()
    play_button.pack_forget()
    app.geometry("320x100")

    app.update()
    total_companies = len(company_dict['company_name'])
    error_count = defaultdict(int)  # Initialize error counter
    error_message = defaultdict(str)
    error_dict = defaultdict(list)
    i = 0

    # file_path = r'C:\Users\Jack\Documents\VS Code\market-intelligence-kubrick\Kubrick MI Data.xlsx'
    # intel_file_path = r'C:\Users\Jack\Documents\VS Code\market-intelligence-kubrick\kubrick_mi_company_intel.csv'
    # template_file_path = r'C:\Users\Jack\Documents\VS Code\market-intelligence-kubrick\Template.xlsx'

    
    file_path = os.path.join(current_dir, 'database', 'Kubrick MI Data.xlsx')
    intel_file_path = os.path.join(current_dir, 'database', 'kubrick_mi_company_intel.csv')
    template_file_path = os.path.join(current_dir, 'Template.xlsx')

    price_report_run = False
    temporary_df = pd.read_excel(file_path, sheet_name="Price Report", engine= 'openpyxl')
    temporary_df['Date of Collection'] = pd.to_datetime(temporary_df['Date of Collection'], format='%Y-%m-%d')
    current_date = pd.to_datetime(datetime.now().strftime('%Y-%m-%d'), format='%Y-%m-%d')
    df_list = []

    if temporary_df['Date of Collection'].iloc[-1] < current_date:
        price_report_run = True
    if price_report_var.get() and not price_report_run:
        SupportFunctions.log_error("Price Report cannot run in the same day, please try run tomorrow.")

    if webscrape_var.get():
        i=0
        for company_name in company_dict["company_name"]:
            i += 1
            currentCompanyLabel.configure(text=f"Current Company: {company_name}")
            company_url, scraper, status, ticker = SupportFunctions.get_company_metadata(company_name, company_df)
            try:
                scraped_data = SupportFunctions.get_scraped_company_data(scraper)
                yahoo_json = SupportFunctions.get_company_details2(status, ticker)
                final_df = SupportFunctions.create_final_df2(company_name, company_url, status, yahoo_json, scraped_data, template_file_path)
                old_df = SupportFunctions.read_from_excel(file_path, company_name, template_file_path)
                SupportFunctions.log_new_and_modified_rows2(final_df, old_df, company_name, file_path)
                SupportFunctions.write_to_excel(final_df, file_path, company_name)
            except:
                error_count['Scraping'] += 1
                error_message['Scraping'] = 'Please check for changes in the company website for the following companies:'
                error_dict['Scraping'].append(company_name)

            progress = i / total_companies
            app.after(0, update_progress, app, currentCompanyLabel, pPercentage, progressBar, progress, company_name)

    if company_intel_var.get():
        i=0
        for company_name in company_dict["company_name"]:
            i += 1
            currentCompanyLabel.configure(text=f"Current Company: {company_name}")
            company_url, scraper, status, ticker = SupportFunctions.get_company_metadata(company_name, company_df)
            company_intel_success = SupportFunctions.company_intel_table(company_name, company_url, df_list, intel_file_path)
            if not company_intel_success:
                error_count['Intel report'] += 1
                error_message['Intel Report']='Please check the existing intel file for the following companies:'
                error_dict['Intel'].append(company_name)

            progress = i / total_companies
            app.after(0, update_progress, app, currentCompanyLabel, pPercentage, progressBar, progress, company_name)

    if price_report_var.get() and price_report_run:
        i = 0
        for full_company_name, full_company_ticker in full_company_list.items():
            i += 1
            temp_data = SupportFunctions.get_company_info_pricereport2(full_company_name, full_company_ticker, file_path)
            if temp_data["Error"]:
                error_count['Price Report'] += 1
                error_message['Price Report']='Please check yahoo finance changes for the following companies:'
                error_dict['Price Report'].append(company_name)
                break
            temp_data.pop("Error", None)
            SupportFunctions.update_excel(temp_data, file_path)
            progress = i / len(full_company_list)
            app.after(0, update_progress, app, currentCompanyLabel, pPercentage, progressBar, progress, full_company_name)


    text = []
    print(error_count != defaultdict(int))
    # Update UI to show completion message and exit button
    if error_count != defaultdict(int):
        # Resize the window to half its height

        for key in error_count:
            text.append(f'{key} finished with {error_count} error(s). Please check for changes with the following companies: {error_dict[key]}.')

        text_string = '\n'.join(text)
        app.geometry("280x160")
        finishLabel.configure(text=f"{text_string} \nPlease look at log file for more information.")
    else:
        app.geometry("300x100")
        finishLabel.configure(text="Task(s) completed successfully. No errors found.")

    pPercentage.pack_forget()
    progressBar.pack_forget()
    progressFrame.pack_forget()
    currentCompanyLabel.pack_forget()

    # Create Exit button
    exit_button = customtkinter.CTkButton(app, text="Exit", command=app.quit)
    exit_button.pack(pady=10)
        
def main():
    global app
    app = create_app()
    app.mainloop()

if __name__ == "__main__":
    main()