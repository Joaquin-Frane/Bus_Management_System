import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import firebase_admin
from firebase_admin import firestore
import pandas as pd
from fpdf import FPDF  # For generating PDFs

from firebase_config import db  # Ensure your firebase_config.py is set up correctly
from pathlib import Path
import customtkinter as ctk

from forHover import set_hover_color


# Function to export data to Excel
def export_to_excel(collection_name):
    try:
         # Get the Downloads folder path
        downloads_folder = Path.home() / "Downloads"

        current_date_time = datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
        file_name = downloads_folder /f"Ceres_{collection_name}_Records_{current_date_time}.xlsx"

        def make_timezone_naive(data):
            """Convert any timezone-aware datetime fields to naive."""
            for record in data:
                for key, value in record.items():
                    if isinstance(value, datetime) and value.tzinfo is not None:
                        record[key] = value.replace(tzinfo=None)

        if collection_name == "summary":
            # Fetch both collections
            transactions = db.collection("DailyTransactions").get()
            sales = db.collection("DailySales").get()

            transactions_data = [doc.to_dict() for doc in transactions]
            sales_data = [doc.to_dict() for doc in sales]

            if not transactions_data and not sales_data:
                messagebox.showinfo("No Data", "No data found in both 'DailyTransactions' and 'DailySales' collections!")
                return

            # Convert timezone-aware datetimes to naive
            make_timezone_naive(transactions_data)
            make_timezone_naive(sales_data)

            # Process data for both collections
            with pd.ExcelWriter(file_name, engine="xlsxwriter") as writer:
                # Transactions Sheet
                if transactions_data:
                    transactions_df = pd.DataFrame(transactions_data)
                    transactions_df.insert(0, "No.", [f"No: {i}" for i in range(1, len(transactions_df) + 1)])
                    transactions_df.columns = [col.upper() for col in transactions_df.columns]
                    transactions_df.to_excel(writer, sheet_name="DailyTransactions", index=False)

                # Sales Sheet
                if sales_data:
                    sales_df = pd.DataFrame(sales_data)
                    sales_df.insert(0, "No.", [f"No: {i}" for i in range(1, len(sales_df) + 1)])
                    sales_df.columns = [col.upper() for col in sales_df.columns]
                    sales_df.to_excel(writer, sheet_name="DailySales", index=False)

            messagebox.showinfo("Success", f"Summary data exported successfully as {file_name}.")
        else:
            # Fetch single collection
            docs = db.collection(collection_name).get()
            data = [doc.to_dict() for doc in docs]

            if not data:
                messagebox.showinfo("No Data", f"No data found in collection '{collection_name}'!")
                return

            # Convert timezone-aware datetimes to naive
            make_timezone_naive(data)

            # Process data
            df = pd.DataFrame(data)
            df.insert(0, "No.", [f"No: {i}" for i in range(1, len(df) + 1)])
            df.columns = [col.upper() for col in df.columns]

            with pd.ExcelWriter(file_name, engine="xlsxwriter") as writer:
                df.to_excel(writer, sheet_name=collection_name, index=False)

            messagebox.showinfo("Success", f"Data exported successfully as {file_name}.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        print(f"An error occurred: {e}")

# Function to export data to PDF
def export_to_pdf(collection_name):
    try:
        downloads_folder = Path.home() / "Downloads"
        current_date_time = datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
        file_name = downloads_folder /f"Ceres_{collection_name}_Records_{current_date_time}.pdf"

        if collection_name == "summary":
            # Fetch both collections
            transactions = db.collection("DailyTransactions").get()
            sales = db.collection("DailySales").get()

            transactions_data = [doc.to_dict() for doc in transactions]
            sales_data = [doc.to_dict() for doc in sales]

            if not transactions_data and not sales_data:
                messagebox.showinfo("No Data", "No data found in both 'DailyTransactions' and 'DailySales' collections!")
                return

            # Create PDF
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            pdf.set_font("Arial", size=12)

            # Add Transactions
            pdf.set_font("Arial", style="B", size=14)
            pdf.cell(200, 10, txt="Daily Transactions Records", ln=True, align="C")
            pdf.set_font("Arial", size=12)
            for idx, record in enumerate(transactions_data, start=1):
                pdf.cell(200, 10, txt=f"No: {idx}", ln=True)
                for key, value in record.items():
                    pdf.cell(200, 10, txt=f"{key}: {value}", ln=True)
                pdf.cell(200, 10, txt="", ln=True)

            # Add Sales
            pdf.add_page()
            pdf.set_font("Arial", style="B", size=14)
            pdf.cell(200, 10, txt="Daily Sales Records", ln=True, align="C")
            pdf.set_font("Arial", size=12)
            for idx, record in enumerate(sales_data, start=1):
                pdf.cell(200, 10, txt=f"No: {idx}", ln=True)
                for key, value in record.items():
                    pdf.cell(200, 10, txt=f"{key}: {value}", ln=True)
                pdf.cell(200, 10, txt="", ln=True)

            pdf.output(file_name)
            messagebox.showinfo("Success", f"Summary data exported successfully as {file_name}.")
        else:
            # Fetch single collection
            docs = db.collection(collection_name).get()
            data = [doc.to_dict() for doc in docs]

            if not data:
                messagebox.showinfo("No Data", f"No data found in collection '{collection_name}'!")
                return

            # Create PDF
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            pdf.set_font("Arial", size=12)

            # Add Title
            pdf.set_font("Arial", style="B", size=14)
            pdf.cell(200, 10, txt=f"{collection_name} Records", ln=True, align="C")
            pdf.set_font("Arial", size=12)

            # Add Data
            for idx, record in enumerate(data, start=1):
                pdf.cell(200, 10, txt=f"No: {idx}", ln=True)
                for key, value in record.items():
                    pdf.cell(200, 10, txt=f"{key}: {value}", ln=True)
                pdf.cell(200, 10, txt="", ln=True)

            pdf.output(file_name)
            messagebox.showinfo("Success", f"Data exported successfully as {file_name}.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")



# Function to handle button click
def download_report(file_type, collection_name):
    if not collection_name:
        messagebox.showwarning("Selection Error", "Please select a collection.")
        return

    if file_type == "excel":
        export_to_excel(collection_name)
    elif file_type == "pdf":
        export_to_pdf(collection_name)

# GUI Setup
def setup_gui():
    # Initialize CTk window
    root = ctk.CTk()
    root.title("Download Reports")
    root.geometry("400x220")
    
    # Center the window on the screen
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = 400
    window_height = 220
    x = int((screen_width - window_width) / 2)
    y = int((screen_height - window_height) / 2)
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

     # Set the window to always stay on top
    root.attributes("-topmost", True)
    root.resizable(False, False)  # Lock the window size


    bg_frame = ctk.CTkFrame(root, fg_color="#03346E")  # Set background color here
    bg_frame.pack(fill="both", expand=True)
    # Title Label
    title_label = ctk.CTkLabel(bg_frame, text="DOWNLOAD REPORTS", font=("Arial", 20, "bold"), text_color="white")
    title_label.pack(fill="x", pady=10)

    # Dropdown Menu for Collection Selection
    ctk.CTkLabel(bg_frame, text="Select Report Type:", font=("Arial", 18), text_color="white").pack(pady=5)
    collection_var = ctk.StringVar()
    collection_dropdown = ctk.CTkComboBox(bg_frame, values=["SALES", "TRANSACTIONS", "SUMMARY"], font=("Arial", 20), width=320, height=40, command=lambda selection: collection_var.set(selection))
    collection_dropdown.pack(pady=5)

    # Buttons for Excel and PDF Export
    button_frame = ctk.CTkFrame(bg_frame, fg_color="transparent")  # Transparent frame for buttons
    button_frame.pack(pady=15)

    excel_button = ctk.CTkButton(button_frame, text="EXCEL", width=150, height=40, font=("Arial", 20, 'bold'), fg_color="#06D001", text_color="#fff", hover_color="#fff",
                                 command=lambda: download_report("excel", collection_var.get().lower()))
    excel_button.grid(row=0, column=0, padx=10)
    set_hover_color(excel_button, "#fff", "#06D001", "#06D001", "#fff")

    pdf_button = ctk.CTkButton(button_frame, text="PDF", width=150, height=40, font=("Arial", 20, 'bold'),  fg_color="#FF3737", text_color="#fff",hover_color="#fff",
                               command=lambda: download_report("pdf", collection_var.get().lower()))
    pdf_button.grid(row=0, column=1, padx=10)
    set_hover_color(pdf_button, "#fff", "#FF3737", "#FF3737", "#fff")

    root.mainloop()

