import tkinter as tk
from customtkinter import *
import pandas as pd
import SupportFunctions
import threading
from datetime import datetime
import os
from collections import defaultdict

company_name='Capgemini SE'
scraper='scraper_capgemini'

class MyRow(CTkFrame):
    def __init__(self, master, label):
        super().__init__(master)

        # add widgets onto the frame, for example:
        self.label = CTkLabel(self, text=label)
        self.label.grid(row=0, column=0, padx=20)
        self.time_label = CTkLabel(self, text='0s')
        self.label.grid(row=0, column=1, padx=20)

class MyFrame(CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master)

        # add widgets onto the frame...
        self.row_count=0

    def add_row(self, label):
        new_row = MyRow(self, label=company_name)
        new_row.label.grid(row=self.row_count, column=0, padx=20)
        new_row.time_label.grid(row=self.row_count, column=1, padx=20)
        self.row_count += 1
        print(new_row.label)

    def update_row(self, row_value):
        self.time[0] +=1
        print(row_value)
        print(self.time[row_value])
        self.time_labels[self.row_count].configure(text=f'{self.time[row_value]}s')
        self.after(1000, self.update_row, row_value)




class App(CTk):
    def __init__(self):
        super().__init__()
        self.geometry("400x200")
        self.grid_rowconfigure(0, weight=1)  # configure grid system
        self.grid_columnconfigure(0, weight=1)

        self.scrape_frame = MyFrame(self)
        self.scrape_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.row_button = CTkButton(self, text="Add row", command=lambda: self.scrape_frame.add_row(company_name))
        self.row_button.grid(row=1, column=0, padx=20, pady=20, sticky="ew")

app2 = App()
app2.mainloop()