import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox # for treeview and  mesage box
from firebase_config import db
from datetime import datetime
from datetime import datetime, timedelta

# Define colors
heavyrow = "#ADBBDA"
lightrow = "#EDE8F5"
vio = "#191970"
white = "white"
vin = "#03346E"

# Function to fetch and display sales data
def fetch_sales(tree, date_input, trn_id_input, acc_id_input, prc_loc_input, status):
    # Clear the treeview
    for row in tree.get_children():
        tree.delete(row)

    # Get filter values
    transaction_date = date_input.get().strip()
    trn_id = trn_id_input.get().strip().lower()
    acc_id = acc_id_input.get().strip().lower()
    prc_loc = prc_loc_input.get().strip()

    # Start Firestore query
    sales_ref = db.collection('sales')
    query = sales_ref
    
    # Filter by transaction_date
    if transaction_date:
        try:
            # Parse the date input
            parts = transaction_date.split("-")
            year = int(parts[0]) if len(parts) > 0 and parts[0].isdigit() else None
            month = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else None
            day = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else None

            # Determine the date range based on the input
            if year and not month and not day:  # Year-only input
                start_date = datetime(year, 1, 1, 0, 0, 0)
                end_date = datetime(year + 1, 1, 1, 0, 0, 0)
            elif year and month and not day:  # Year and month input
                start_date = datetime(year, month, 1, 0, 0, 0)
                # Handle the end of the month
                if month == 12:  # If December, go to the next year's January
                    end_date = datetime(year + 1, 1, 1, 0, 0, 0)
                else:
                    end_date = datetime(year, month + 1, 1, 0, 0, 0)
            elif year and month and day:  # Full date input
                start_date = datetime(year, month, day)
                end_date = start_date + timedelta(days=1)
            else:
                raise ValueError("Invalid date input format")
            
            query = query.where("transaction_date", ">=", start_date).where("transaction_date", "<=", end_date)
        except ValueError:
            print("Invalid date format. Use YYYY, YYYY-MM, or YYYY-MM-DD.")

    

    # Execute query and populate the treeview
    docs = query.stream()
    count = 1

    for doc in docs:
        data = doc.to_dict()
        sales_id = doc.id
        transaction_date = data.get("transaction_date", "")
        transaction_date_str = (
            transaction_date.strftime('%Y-%m-%d')
            if isinstance(transaction_date, datetime)
            else "Invalid Format"
        )
        trn_id_r = data.get("transactionID", "").lower()
        terminal = data.get("terminal", "")
        price = data.get("price", "")
        trip_id = data.get("TripID", "").lower()
        status_r = data.get("status", "")
        acc_id_r =data.get("account_id", "").lower()
        cashier_r = data.get("cashier_id", "").lower()


        if  ((prc_loc == "ALL" or terminal == prc_loc) and 
             (status == "ALL" or status_r == status) and 
             (trn_id in trn_id_r or trn_id in trip_id) and 
             (acc_id in acc_id_r or acc_id in cashier_r)):
 

            # Insert data into the treeview
            row_tags = "red" if data.get('status') == "Refunded" or  data.get('status') == "Cancelled" else "oddrow" if count % 2 == 0 else "evenrow"
            tree.insert('', 'end', values=(
                count, 
                sales_id, 
                f"  {terminal}", 
                f"₱. {price}", 
                transaction_date_str, 
                data.get("account_id", data.get("cashier_id", "")), 
                trn_id_r, 
                trip_id, 
                status_r
            ), 
            tags=(row_tags,))
            count += 1




# Main function to display the manage sales interface
def manage_sales(action, main_content_frame):
    # Clear current content
    for widget in main_content_frame.winfo_children():
        widget.destroy()

    status_var = tk.StringVar(value="ALL")
    def toggle_status():
        current_status = status_var.get()
        if current_status == "ALL":
            status_var.set("Payed")
        elif current_status == "Payed":
            status_var.set("Refunded")
        elif current_status == "Refunded":
            status_var.set("Cancelled")
        else:
            status_var.set("ALL")
        # Fetch data after toggling status
        fetch_sales(tree, date_entry, trn_id_entry, acc_id_entry, prc_loc_dropdown, status_var.get())


    # Title holder frame
    c_frame = ctk.CTkFrame(main_content_frame, corner_radius=0, fg_color=vin)
    c_frame.pack(fill="x")

    button_frame = ctk.CTkFrame(c_frame, corner_radius=0, fg_color=vin)
    button_frame.pack(fill="x")

    # Title
    title_label = ctk.CTkLabel(button_frame, text="MANAGE SALES", text_color=white, font=("Arial", 20, "bold"))
    title_label.pack(side="left",pady=(5, 10), padx=(20, 10))

    # Filter frame
    filter_frame = ctk.CTkFrame(c_frame, corner_radius=0, fg_color=vin)
    filter_frame.pack(fill="x")
    filter_frame.grid_columnconfigure(tuple(range(7)), weight=1)

    # Date filter
    date_label = ctk.CTkLabel(filter_frame, text="Transaction Date:", text_color=white)
    date_label.grid(row=0, column=0, padx=(25, 10), pady=(5, 0), sticky="w")
    date_entry = ctk.CTkEntry(filter_frame, width=150, placeholder_text="YYYY-MM-DD", text_color="#191970")
    date_entry.grid(row=1, column=0, padx=(25, 10), pady=(0, 10), sticky="w")

    # PRC Loc. filter
    prc_loc_label = ctk.CTkLabel(filter_frame, text="PRC Loc.:", text_color=white)
    prc_loc_label.grid(row=0, column=1, padx=10, pady=(5, 0), sticky="w")
    prc_loc_dropdown = ctk.CTkComboBox(filter_frame, values=["ALL", "Manila", "Legaspi", "Antipolo", "Montalban", "uiouioui"], command=lambda _: fetch_sales(tree, date_entry, trn_id_entry, acc_id_entry, prc_loc_dropdown, status_var.get()))
    prc_loc_dropdown.grid(row=1, column=1, padx=10, pady=(0, 10), sticky="w")
    prc_loc_dropdown.set("ALL")

    # TRN ID filter
    trn_id_label = ctk.CTkLabel(filter_frame, text="TRN ID:", text_color=white)
    trn_id_label.grid(row=0, column=2, padx=10, pady=(5, 0), sticky="w")
    trn_id_entry = ctk.CTkEntry(filter_frame, width=150, placeholder_text="TRN/Trip ID", text_color="#191970")
    trn_id_entry.grid(row=1, column=2, padx=10, pady=(0, 10), sticky="w")

    # Acc. ID filter
    acc_id_label = ctk.CTkLabel(filter_frame, text="Acc. ID:", text_color=white)
    acc_id_label.grid(row=0, column=3, padx=10, pady=(5, 0), sticky="w")
    acc_id_entry = ctk.CTkEntry(filter_frame, width=150, placeholder_text="Acc/Cashier ID", text_color="#191970")
    acc_id_entry.grid(row=1, column=3, padx=10, pady=(0, 10), sticky="w")

    status_button = ctk.CTkButton( filter_frame, textvariable=status_var, fg_color=white, text_color=vio, command=toggle_status,height=40, font=("Arial", 18, "bold"), hover_color="#6eacda")
    status_button.grid(row=0, rowspan=2, column=7, padx=10, pady=(20, 10), sticky="e")

    # Ensure a maximum of 7 columns and align widgets
    # Code for the Treeview Table
    columns = ("No.","Sales ID", "PRC. At", "Price", "TRN Date", "Acc. ID" , "TRN ID", "Trip ID", 'Status' )
    tree_frame = ctk.CTkFrame(main_content_frame)
    tree_frame.pack(fill="both", expand=True)

    # Scrollbar for vertical and horizontal scrolling
    vertical_scroll = tk.Scrollbar(tree_frame, orient="vertical")
    vertical_scroll.pack(side="right", fill="y")

    tree = ttk.Treeview(tree_frame, yscrollcommand=vertical_scroll.set, columns=columns, show="headings", height=10)

    # Treeview column configurations
    for col in columns:
        tree.heading(col, text=col)

        if col == "No." :
            tree.column(col, anchor="w", width=35)
        elif col == "Acc. ID" :
            tree.column(col, width=100)
        elif col == "PRC. At" or  col == "Price":
            tree.column(col,   width=60)
        elif   col == "TRN Date":
            tree.column(col,  width=50)
        elif col == "Sales ID" or col == "TRN ID" or col == "Trip ID" :
            tree.column(col,  width=100)
        else:
            tree.column(col, anchor="center", width=20)

    tree.tag_configure('oddrow', background=lightrow)
    tree.tag_configure('evenrow', background=heavyrow)
    tree.tag_configure('red', background="#cc3e40", foreground="#fff")

    tree.pack(fill="both", expand=True)
    # configure scrollbars
    vertical_scroll.config(command=tree.yview)

    tree.bind("<Double-1>", lambda e: view_full_data(tree))

    # Fetch sales data when Enter key is pressed
    for entry in [date_entry, trn_id_entry, acc_id_entry]:
        entry.bind("<Return>", lambda event:  fetch_sales(tree, date_entry, trn_id_entry, acc_id_entry, prc_loc_dropdown, status_var.get()))

    # Fetch data after toggling status
    fetch_sales(tree, date_entry, trn_id_entry, acc_id_entry, prc_loc_dropdown, status_var.get())


def view_full_data(treeview):
    # Get the selected item from the Treeview
    selected_item = treeview.focus()
    if not selected_item:
        messagebox.showwarning("Warning", "Please select a transaction to view.")
        return

    # Get the values of the selected row
    selected_values = treeview.item(selected_item, 'values')
    sales_id = selected_values[1]  # Assuming the TRN ID is the second column

    # Create a new window to display the full data
    full_data_window = ctk.CTkToplevel()
    full_data_window.title(f"Full Data for Transaction {sales_id}")
    full_data_window.geometry("405x470")
    full_data_window.configure(fg_color="#021526")
    
    # Main frame to hold the side-by-side frames
    main_frame = ctk.CTkFrame(full_data_window, corner_radius=10, fg_color="#021526")
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)
    # Left frame for transaction data
    transaction_frame = ctk.CTkFrame(main_frame, corner_radius=10, fg_color="#e0e0e0")
    transaction_frame.grid(row=0, column=0, padx=10, pady=(10,5), sticky="nsew")

    # Fetch the selected transaction document from Firebase (Transaction collection)
    transaction_doc = db.collection('sales').document(sales_id).get()

    if transaction_doc.exists:
        data = transaction_doc.to_dict()
        # Fields to fetch and their corresponding labels for transactions
        transaction_fields = {
            'ID': "Sales ID",
            'transactionID':'Transaction ID',
            'TripID':'trip ID',
            'ScheduleID':'Schedule ID',
            'account_id': "Account ID",
            'cashier_id': "Cashier ID",
            'transaction_date': "TRN Date",
            'price': "Price",
            'terminal': "Purchase At.",
            'status': "Status"
        }

        # Transaction details (in the left frame)
        transaction_title = ctk.CTkLabel(transaction_frame, text="Sales Data", font=("Arial", 16, "bold"), text_color="#191970")
        transaction_title.pack(anchor="w", padx=10, pady=5)
        
        for field, label_text in transaction_fields.items():
            value = data.get(field, 'N/A')  # Fetch field value or use 'N/A' if it doesn't exist
            label = ctk.CTkLabel(transaction_frame, text=f"   {label_text}:    {value}", text_color="#191970")
            label.pack(anchor="w", padx=10, pady=3)
    else:
        messagebox.showerror("Error", f"No transaction data found for {sales_id}")


    # Add Exit and Edit Trip Info buttons at the bottom
    button_frame = ctk.CTkFrame(full_data_window, fg_color="#021526")
    button_frame.pack(pady=5, side="top")
    # Exit Button
    exit_button = ctk.CTkButton(button_frame, text="Exit", command=full_data_window.destroy, fg_color="#6eacda",font=("Arial", 14, "bold"), text_color="#191970", hover_color="#F95454")
    exit_button.pack( padx=10, pady=(0,15))

