def get_webscrape(error_count, error_message, error_dict, file_path, template_file_path, total_companies, currentCompanyLabel, pPercentage, progressBar):
    i=0
    for company_name in company_dict["company_name"]:
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
        i+=1

def get_price_report(error_count, error_message, error_dict, file_path, currentCompanyLabel, pPercentage, progressBar):
    i = 0
    for full_company_name, full_company_ticker in full_company_list.items():
        i += 1
        temp_data = SupportFunctions.get_company_info_pricereport2(full_company_name, full_company_ticker, file_path)
        if temp_data["Error"]:
            error_count['Price Report'] += 1
            error_message['Price Report']='Please check yahoo finance changes for the following companies:'
            error_dict['Price Report'].append(full_company_name)
            break
        temp_data.pop("Error", None)
        SupportFunctions.update_excel(temp_data, file_path)
        progress = i / len(full_company_list)
        app.after(0, update_progress, app, currentCompanyLabel, pPercentage, progressBar, progress, full_company_name)

    return