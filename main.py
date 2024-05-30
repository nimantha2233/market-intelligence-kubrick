import tkinter
import customtkinter
import pandas as pd
import SupportFunctions

company_dict = {'company_name':['Capgemini SE', 'AND Digital', 'Dufrain', 'FDM Group (Holdings) Ltd', 'Slalom', 'Tata Consultancy Services Limited', 'Wipro Limited', 'Infosys Limited', 'Credera', 'Infinite Lambda', 'Mesh AI', 'Sparta Global', 'Ten10', 'Fjord Consulting Group', 'BetterGov', 'Cambridge Consultants Limited', 'Capco Limited', 'Cognizant Technology Solutions Corporation', 'IQVIA Holdings Inc', 'Kubrick Group Limited'],
        'company_url':['https://www.capgemini.com/','https://www.and.digital/','https://www.dufrain.co.uk/','https://www.fdmgroup.com/','https://www.slalom.com/','https://www.tcs.com','https://www.wipro.com/', 'https://www.infosys.com/', 'https://www.credera.com/en-gb', 'https://infinitelambda.com', 'https://www.mesh-ai.com/', 'https://www.spartaglobal.com', 'https://ten10.com', 'https://fjordconsultinggroup.com', 'https://www.bettergov.co.uk/', 'https://www.cambridgeconsultants.com/', 'https://www.capco.com', 'https://www.cognizant.com', 'https://jobs.iqvia.com/en', 'https://www.kubrickgroup.com'],
        'status':['Public','Private','Private','Public','Private','Public','Public', 'Public', 'Private', 'Private', 'Private', 'Private', 'Private', 'Private', 'Private', 'Private', 'Private', 'Public', 'Public', 'Private'],
        'ticker':['CAP.PA', '', '', 'FDM.L', '','TCS.BO','WIT', 'INFY', '', '', '', '', '', '', '', '', '', 'CTSH', 'IQV', ''],
        'scraper':['scraper_capgemini','scraper_digital','scraper_dufrain','scraper_fdmgroup','scraper_slalom','scraper_tcs','scraper_wipro', 'scraper_infosys', 'scraper_credera', 'scraper_infinitelambda', 'scraper_meshai', 'scraper_spartaglobal', 'scraper_ten10', 'scraper_fjord', 'scraper_bettergov', 'scraper_cambridge', 'scraper_capco', 'scraper_cognizant', 'scraper_iqvia', 'scraper_kubrick']}

company_df = pd.DataFrame(company_dict)

def create_app():
    # System Settings
    customtkinter.set_appearance_mode("dark")
    customtkinter.set_default_color_theme("blue")

    # App frame
    app = customtkinter.CTk()
    app.geometry("320x250")
    app.title("Kubrick MI Webscrape")

    # UI elements
    title = customtkinter.CTkLabel(app, text="Select an option and click Start.")
    title.pack(padx=10, pady=10)
    # Option buttons
    webscrape_var = customtkinter.BooleanVar()
    price_report_var = customtkinter.BooleanVar()

    webscrape_button = customtkinter.CTkCheckBox(app, text="Webscrape", variable=webscrape_var)
    webscrape_button.pack(pady=5)

    price_report_button = customtkinter.CTkCheckBox(app, text="Price Report", variable=price_report_var)
    price_report_button.pack(pady=5)

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
    play_button = customtkinter.CTkButton(app, text="Start", command=lambda: main_scrape(app, title, currentCompanyLabel, pPercentage, progressBar, 
                                                                                         finishLabel, play_button, progressFrame, webscrape_var, 
                                                                                         price_report_var, webscrape_button, price_report_button))
    play_button.pack(pady=10)

    # Finished Downloading
    finishLabel = customtkinter.CTkLabel(app, text="")
    finishLabel.pack(pady=10)

    return app

def main_scrape(app, title, currentCompanyLabel, pPercentage, progressBar, 
                finishLabel, play_button, progressFrame, webscrape_var, 
                price_report_var, webscrape_button, price_report_button):

    if not webscrape_var.get() and not price_report_var.get():
        tkinter.messagebox.showwarning("No Option Selected", "Please select at least one option before starting.")
        return
    
    title.pack_forget()
    webscrape_button.pack_forget()
    price_report_button.pack_forget()
    app.geometry("320x130")

    app.update()
    total_companies = len(company_dict['company_name'])
    price_error_count = 0  # Initialize error counter
    scrape_error_count = 0

    file_path = r'C:\Users\Jack\Documents\VS Code\market-intelligence-kubrick\Kubrick MI Data.xlsx'
    excel_file_path = r'C:\Users\Jack\Documents\VS Code\market-intelligence-kubrick\Kubrick MI Diff.xlsx'
    template_file_path = r'C:\Users\Jack\Documents\VS Code\market-intelligence-kubrick\Template.xlsx'

    #if not webscrape_var.get() and price_report_var.get():
    #    i=0
    #    for company_name in company_dict['company_name']:
    #        company_url, scraper, status, ticker = get_company_metadata(company_name, company_df)
    #        i+=1
    #        currentCompanyLabel.configure(text=f"Current Company: {company_name}")
    #        temp_data = get_company_info_pricereport2(company_name, ticker, file_path=r'C:\Users\Jack\Documents\VS Code\market-intelligence-kubrick\Kubrick MI Data.xlsx')
    #        if temp_data["Error"]:
    #            error_count += 1
    #        # Remove the 'Error' field before updating the excel
    #        temp_data.pop("Error", None)    
    #        update_excel(temp_data, file_path=r'C:\Users\Jack\Documents\VS Code\market-intelligence-kubrick\Kubrick MI Data.xlsx')
    #        progress = i / total_companies
    #        progressBar.set(progress)
    #        pPercentage.configure(text=f'{int(progress*100)}%')
    #        app.update_idletasks()
    if webscrape_var.get():
        i=0
        for company_name in company_dict['company_name']:
            i+=1
            currentCompanyLabel.configure(text=f"Current Company: {company_name}")
            company_url, scraper, status, ticker = SupportFunctions.get_company_metadata(company_name, company_df)
            try:
                scraped_data = SupportFunctions.get_scraped_company_data(scraper)
                yahoo_json = SupportFunctions.get_company_details2(status, ticker)
                final_df = SupportFunctions.create_final_df2(company_name, company_url, status, yahoo_json, scraped_data, template_file_path)

                old_df = SupportFunctions.read_from_excel(file_path, company_name, template_file_path)

                SupportFunctions.log_new_and_modified_rows2(final_df, old_df, company_name, excel_file_path)
                SupportFunctions.write_to_excel(final_df, file_path, company_name)
            except:
                scrape_error_count += 1
            progress = i / total_companies
            progressBar.set(progress)
            pPercentage.configure(text=f'{int(progress*100)}%')
            app.update_idletasks()

    if price_report_var.get():
        i=0
        for company_name in company_dict['company_name']:
            i+=1
            currentCompanyLabel.configure(text=f"Current Company: {company_name}")
            temp_data = SupportFunctions.get_company_info_pricereport2(company_name, ticker, file_path)
            if temp_data["Error"]:
                price_error_count += 1
            # Remove the 'Error' field before updating the excel
            temp_data.pop("Error", None)    
            SupportFunctions.update_excel(temp_data, file_path)
            progress = i / total_companies
            progressBar.set(progress)
            pPercentage.configure(text=f'{int(progress*100)}%')
            app.update_idletasks()

    if not price_report_var.get() and webscrape_var.get():
        # WEB SCRAPING FUNCTION
        # ---------------------
        #for i, (company, ticker) in enumerate(temp_dict.items(), start =1):
        #    currentCompanyLabel.configure(text=f"Current Company: {company}")
        #    
        pass
    if price_report_var.get() and webscrape_var.get():
        # WEB SCRAPING FUNCTION
        # ---------------------
        #for i, (company, ticker) in enumerate(temp_dict.items(), start =1):
        #    currentCompanyLabel.configure(text=f"Current Company: {company}")
        #    
        pass

    # Update UI to show completion message and exit button
    if scrape_error_count + price_error_count > 0:
        # Resize the window to half its height
        app.geometry("280x110")
        finishLabel.configure(text=f"Scraping finished with {scrape_error_count} company data error(s) and {price_error_count} price report error(s).\nPlease look at log file for more information.")
    else:
        app.geometry("220x100")
        finishLabel.configure(text="Scraping finished!")

    pPercentage.pack_forget()
    progressBar.pack_forget()
    progressFrame.pack_forget()
    play_button.pack_forget()
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