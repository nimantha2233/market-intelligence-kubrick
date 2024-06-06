

from SupportFunctions import read_from_excel

file_path = r'MI\database\Kubrick MI Data.xlsx'
intel_file_path = r'MI\database\kubrick_mi_company_intel.csv'
template_file_path = r'Mi\Template.xlsx'


df = read_from_excel(file_path,'Dufrain', template_file_path)
print(df)

