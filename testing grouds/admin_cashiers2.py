# imports for Gui and database connection
import firebase_admin
from firebase_admin import credentials, auth, exceptions
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from firebase_config import db
from forHover import set_hover_color
import re  # Import regex for pattern matching

count = 1  # counter 

heavyrow = "#ADBBDA"
lightrow = "#EDE8F5"
vio = "#191970"
white = "white"
purplr = "#9747FF"
red = "#FF3737"
lightblue = "#4682B4"
vin = "#03346E"

global_terminal_location = "All"
global_query = ""
global_status_filter = "All"  
global_id_query = "" 
# function to update the main_content_frame from main code
def manage_cashiers(action, main_content_frame):

    status_filter = tk.StringVar(value="All")

    def toggle_status():
        current_status = status_filter.get()
        if current_status == "All":
            status_filter.set("Active")
        elif current_status == "Active":
            status_filter.set("Cancelled")
        else:
            status_filter.set("All")
        filter()
    
    def filter(*args):
        global global_terminal_location, global_query, global_status_filter, global_id_query
        global_status_filter = status_filter.get()
        global_id_query = id_entry.get()  # Fetch actual string value
        global_query = search_entry.get()  # Fetch actual string value
        global_terminal_location = terminal_var.get()  # Fetch actual string value
        filter_cashiers(db, tree)

    # Clear previous content in the frame
    for widget in main_content_frame.winfo_children():  # select individual widgets
        widget.destroy()  # destroy that widget

    # Code for button frame for managing bus schedule (serve as title holder)
    c_frame = ctk.CTkFrame(main_content_frame, corner_radius=0, fg_color=vin)
    c_frame.pack(fill="x")

    # Button frame to hold the sub top bar 
    button_frame = ctk.CTkFrame(c_frame, fg_color=vin)
    button_frame.pack(fill="x")

    # title in Button frame
    title_label = ctk.CTkLabel(button_frame, text=" CASHIER", text_color="white", font=("Arial", 23, "bold"))
    title_label.pack(side="left", padx=(20, 10), pady=(10, 5))

    # add button in button frame 
    add_button = ctk.CTkButton(button_frame, text="Add", fg_color=white, text_color=vio, font=("Arial", 16, "bold"), height=35, command=lambda: add_cashier(db, tree))
    add_button.pack(side="left", padx=10, pady=(5,5))
    
    set_hover_color(add_button, hover_bg_color=purplr, hover_text_color=white, normal_bg_color=white, normal_text_color=vio)

    # code for Search frame to hold search and filter related stuff
    search_frame = ctk.CTkFrame(c_frame, fg_color=vin)
    search_frame.pack(fill="x")
    search_frame.columnconfigure(tuple(range(6)), weight=1)

    # Add dropdown for terminal locations
    search_label = ctk.CTkLabel(search_frame, text="Status", text_color="white").grid(row=0, column=0, padx=(25, 5), pady=(5, 0), sticky="w")
    status_button = ctk.CTkButton(search_frame, textvariable=status_filter, fg_color=white, text_color=vio, font=("Arial", 16, "bold"),height=35, command=toggle_status)
    status_button.grid(row=1, column=0, padx=(20, 5), pady=(0, 10), sticky="w")
    set_hover_color(status_button, hover_bg_color=purplr, hover_text_color=white, normal_bg_color=white, normal_text_color=vio)

    # Add dropdown for terminal locations
    search_label = ctk.CTkLabel(search_frame, text="Terminal Loc.", text_color="white")
    search_label.grid(row=0, column=1, padx=(25, 5), pady=(5, 0), sticky="w")

    terminal_locations = fetch_terminal_locations(db)
    terminal_var = ctk.StringVar(value="All")  # Default value is "All"
    terminal_dropdown = ctk.CTkComboBox(search_frame, variable=terminal_var, values=["All"] + terminal_locations)
    terminal_dropdown.grid(row=1, column=1, padx=(20, 5), pady=(0, 10), sticky="w")
    

    # Update treeview when a terminal is selected
    terminal_var.trace_add("write", filter)

    # search box
    search_label = ctk.CTkLabel(search_frame, text="Name Search:", text_color="white")
    search_label.grid(row=0, column=2, padx=10, pady=(5, 0), sticky="w")

    search_entry = ctk.CTkEntry(search_frame, width=200, placeholder_text="Jaun D", placeholder_text_color="#6eacda")
    search_entry.grid(row=1, column=2, padx=5, pady=(0,10), sticky="w")

    # ID Search Box
    id_label = ctk.CTkLabel(search_frame, text="Search by ID:", text_color="white")
    id_label.grid(row=0, column=3, padx=10, pady=(5, 0), sticky="w")

    id_entry = ctk.CTkEntry(search_frame, width=200, placeholder_text="12345", placeholder_text_color="#6eacda")
    id_entry.grid(row=1, column=3, padx=5, pady=(0, 10), sticky="w")
    id_entry.bind("<KeyRelease>", filter)

    search_entry.bind("<KeyRelease>", filter)

    # Buttons for edit and delete row of data in treeview
    delete = ctk.CTkButton(search_frame, text="Delete", font=("Arial", 16, "bold"), height=35, command=lambda: delete_cashier(db, tree), fg_color=white, text_color=red)
    delete.grid(row=0, column=7, rowspan=2, padx=(5, 20), pady=(25, 10), sticky="w")
    
    edit = ctk.CTkButton(search_frame, text="Edit", font=("Arial", 16, "bold"), height=35, command=lambda: edit_cashier(db, tree), fg_color=white, text_color=vio)
    edit.grid(row=0, column=6, rowspan=2, padx=5, pady=(25, 10), sticky="w")

    set_hover_color(delete, hover_bg_color=red, hover_text_color=white, normal_bg_color=white, normal_text_color=red)
    set_hover_color(edit, hover_bg_color=lightblue, hover_text_color=white, normal_bg_color=white, normal_text_color=vio)

    # headers for columns in treeview stored in a list object
    columns = ("No.", "Cashier ID", "Cashier Name", "Email", "Address", "Phone No.", "UID", "Terminal Loc", "Wage/Hr", "Status")
    tree_frame = ctk.CTkFrame(main_content_frame)
    tree_frame.pack(fill="both", expand=True)

    tree_scroll = tk.Scrollbar(tree_frame, orient="vertical")
    tree_scroll.pack(side="right", fill="y")

    tree = ttk.Treeview(tree_frame, columns=columns, yscrollcommand=tree_scroll.set, show='headings')
    tree.tag_configure('oddrow', background=heavyrow)
    tree.tag_configure('evenrow', background=lightrow)
    tree.tag_configure('Inactive', background="#999")
    
    for col in columns:
        tree.heading(col, text=col)
        if col == 'No.':
            tree.column(col, width=35)
        elif col== "Status":
            tree.column(col, width=40, anchor="center")    
        elif col =="Cashier ID":
            tree.column(col, width=70)
        elif col =="Email" or col =="Address" or col =="UID":
            tree.column(col, width=100)
        elif col =="Cashier Name" :
            tree.column(col, width=110)
        elif col =="Terminal Loc" :
            tree.column(col, width=80)
        elif col =="Phone No."  :
            tree.column(col, width=70)
        elif col =="Wage/Hr" :
            tree.column(col, width=50)
        else:
            tree.column(col, width=100)

    tree.pack(fill=ctk.BOTH, expand=True)
    tree_scroll.config(command=tree.yview)

    # function to run when an item in treeview is double clicked
    def clicker(e):
        edit_cashier(db, tree)

    tree.bind("<Double-1>", clicker)  # event listener in treeview check if an item / row is double clicked within 1 sec

    # Fetch and display cashiers initially
    filter()

# function to retrieve all the unique terminal loc where a cashier is assigned
def fetch_terminal_locations(db):
    terminal_locations = []  # create a list to store data
    cashiers = db.collection('Cashier').stream()  # fetch all doc in collection cashier

    for cashier in cashiers:  # loop to docs in collection
        terminal_location = cashier.to_dict().get('terminal_location')  # store fetched doc to a dict
        if terminal_location and terminal_location not in terminal_locations:  # check if terminal is not on the list or is empty
            terminal_locations.append(terminal_location)  # append value to list
    return terminal_locations



def filter_cashiers(db, tree):
    global global_terminal_location, global_query, global_status_filter, global_id_query

    count = 1  # Set counter

    # Clear existing data in the treeview
    for item in tree.get_children():
        tree.delete(item)

    # Fetch all docs in the Cashier collection
    cashiers = db.collection('Cashier').stream()
    filtered_cashiers = []  # List to store filtered data

    # Apply filters
    for cashier in cashiers:
        data = cashier.to_dict()
        # Terminal Location Filter
        terminal_filter_pass = (global_terminal_location == "All" or 
                                data.get('terminal_location') == global_terminal_location)

        # Search Query Filter
        query_filter_pass = (global_query == "" or 
                             global_query.lower() in data.get('first_name', '').lower() or 
                             global_query.lower() in data.get('last_name', '').lower())

        # Status Filter
        status_filter_pass = (global_status_filter == "All" or 
                              data.get('status', '') == global_status_filter)

        # ID Query Filter
        id_filter_pass = (global_id_query == "" or 
                          global_id_query.upper() in data.get('ID', '') or 
                          global_id_query.lower() in data.get('uid', '').lower())

        # Combine filters
        if terminal_filter_pass and query_filter_pass and status_filter_pass and id_filter_pass:
            filtered_cashiers.append(data)

    # Add filtered data to the treeview
    for data in filtered_cashiers:
        row_tag = "Inactive" if data.get('status') == "Inactive" else "oddrow" if count % 2 == 0 else "evenrow"
        tree.insert("", ctk.END, iid=data.get('uid', 'N/A'), values=(
            count,
            data.get('ID', 'N/A'), 
            f"{data.get('last_name', '')}, {data.get('first_name', '')}", 
            data.get('email', ''), 
            data.get('address', ''), 
            data.get('phone_number', ''), 
            data.get('uid', ''), 
            data.get('terminal_location', ''), 
            f"₱. {data.get('hourly_wage', '')}", 
            data.get('status', '')
            ), tags=(row_tag,))
       
        count += 1  # Increment count



# function to generate the next available cashier Id based on exsisting IDS
def get_next_available_cashier_id(db):
    try:
        # Access a shared counter document in Firestore
        counter_doc = db.collection('Countsettings').document('CashierIDs')
        counter_data = counter_doc.get()

        # Check if the document exists and get the value
        if counter_data.exists:
            catt_count = counter_data.to_dict().get('count', 1)

        else:
            # If the document doesn't exist, initialize the bus count
            catt_count = 1
            # Create the document with the initial count
            counter_doc.set({'count': catt_count})

        while True:
            # Generate the bus ID as the document name
            catt_id = f"CATT-{catt_count:05d}"

            # Check if a document with this ID (name) exists
            existing_bus_doc = db.collection('Cashier').document(catt_id).get()

            if not existing_bus_doc.exists:
                # If no document found, use this bus_id as the new document name
                print(f"Unique driver ID generated: {catt_id}")
                # Update the counter in Firestore
                #counter_doc.update({'count': catt_count + 1})
                break
            else:
                # Increment and check again if there’s a conflict
                catt_count += 1
                print(f"driver ID occupied at: {catt_id}")

    except Exception as e:
        print("Error", f"Failed to generate Bus ID: {e}")
        return None

    return catt_id, catt_count + 1



#function to run when add button is clicked 
def add_cashier(db, tree):
    try:
        # Create window form
        add_window = ctk.CTkToplevel()
        add_window.title("Add Cashier")

        # Keep the window on top
        add_window.lift()
        add_window.attributes("-topmost", True)
        add_window.configure(fg_color="#03346E")

        cashier_id_val, value2 = get_next_available_cashier_id(db)
        # --- Validation for numeric entries ---
        def validate_numeric(P):
            if P == "":
                return True
            try:
                float(P)
                return True
            except ValueError:
                return False

        vcmd = (add_window.register(validate_numeric), '%P')
        
        def validate_phone_number(P):
            if P.isdigit() and len(P) <= 11 or P == "":
                return True  # Only digits allowed and maximum length is 11
            return False

        # Register the validation function
        phone_vcmd = add_window.register(validate_phone_number)
        # ---------------- LABELS AND ENTRIES ---------------- #

        ctk.CTkLabel(add_window, text="Cashier ID:", text_color="#E2E2B6").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        cashier_id_label = ctk.CTkEntry(add_window, text_color="#191970")
        cashier_id_label.grid(row=0, column=1, padx=10, pady=5)
        cashier_id_label.insert(0, cashier_id_val)
        cashier_id_label.configure(state="disabled")

        ctk.CTkLabel(add_window, text="First Name:", text_color="#E2E2B6").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        first_name = ctk.CTkEntry(add_window, placeholder_text="Juan", text_color="#191970")
        first_name.grid(row=1, column=1, padx=10, pady=5)

        ctk.CTkLabel(add_window, text="Last Name:", text_color="#E2E2B6").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        last_name = ctk.CTkEntry(add_window, placeholder_text="Cruz", text_color="#191970")
        last_name.grid(row=2, column=1, padx=10, pady=5)

        ctk.CTkLabel(add_window, text="Middle Name:", text_color="#E2E2B6").grid(row=3, column=0, padx=10, pady=5, sticky="e")
        middle_name = ctk.CTkEntry(add_window, placeholder_text="Dela", text_color="#191970")
        middle_name.grid(row=3, column=1, padx=10, pady=5)

        ctk.CTkLabel(add_window, text="Address:", text_color="#E2E2B6").grid(row=4, column=0, padx=10, pady=5, sticky="e")
        address = ctk.CTkEntry(add_window, placeholder_text="Barangay 307 Quiapo, City of Manila", text_color="#191970")
        address.grid(row=4, column=1, padx=10, pady=5)

        ctk.CTkLabel(add_window, text="Phone Number:", text_color="#E2E2B6").grid(row=5, column=0, padx=10, pady=5, sticky="e")
        phone_number = ctk.CTkEntry(add_window, placeholder_text="09123456789", text_color="#191970", validate="key", validatecommand=(phone_vcmd, '%P'))
        phone_number.grid(row=5, column=1, padx=10, pady=5)

        ctk.CTkLabel(add_window, text="Terminal Location:", text_color="#E2E2B6").grid(row=6, column=0, padx=10, pady=5, sticky="e")
        terminal_location = ctk.CTkEntry(add_window, placeholder_text="Manila", text_color="#191970")
        terminal_location.grid(row=6, column=1, padx=10, pady=5)

        ctk.CTkLabel(add_window, text="Hourly Wage:", text_color="#E2E2B6").grid(row=7, column=0, padx=10, pady=5, sticky="e")
        hourly_wage = ctk.CTkEntry(add_window, placeholder_text="100.00", text_color="#191970", validate="key", validatecommand=vcmd)
        hourly_wage.grid(row=7, column=1, padx=10, pady=5)

        ctk.CTkLabel(add_window, text="Email Address:", text_color="#E2E2B6").grid(row=8, column=0, padx=10, pady=5, sticky="e")
        email = ctk.CTkEntry(add_window, placeholder_text="Juan@gmail.com", text_color="#191970")
        email.grid(row=8, column=1, padx=10, pady=5)

        ctk.CTkLabel(add_window, text="Password:", text_color="#E2E2B6").grid(row=9, column=0, padx=10, pady=5, sticky="e")
        password = ctk.CTkEntry(add_window, show="*", text_color="#191970")
        password.grid(row=9, column=1, padx=10, pady=5)

        # ---------------- SAVE BUTTON FUNCTION ---------------- #
        def save_cashier():
            try:
                # Email validation
                email_input = email.get().strip()
                if not email_input.endswith("@gmail.com"):
                    messagebox.showerror("Error", "Please provide a valid gmail address '@gmail.com'.")
                    return

                # Check for duplicate email
                def email_exists(email):
                    users = db.collection('Cashier').where('email', '==', email).get()
                    return len(users) > 0

                if email_exists(email_input):
                    messagebox.showerror("Error", "The Email already exists! Please use a different email.")
                    return
                
                # Validate all fields are filled
                if not all([cashier_id_val, first_name.get(),last_name.get(),middle_name.get(), address.get(), phone_number.get(),terminal_location.get(),email_input,hourly_wage.get()]):
                    messagebox.showerror("Error", "All fields are required.")
                    return

                # Save cashier to Firestore
                user = auth.create_user(email=email_input, password=password.get())
                cashier_data = {
                    'ID': cashier_id_val,
                    'first_name': first_name.get(),
                    'last_name': last_name.get(),
                    'middle_name': middle_name.get(),
                    'address': address.get(),
                    'phone_number': phone_number.get(),
                    'terminal_location': terminal_location.get(),
                    'email': email_input,
                    'hourly_wage': hourly_wage.get(),
                    'status': 'Active',
                    'role': 'cashier',
                    'uid': user.uid
                }

                db.collection('Cashier').document(user.uid).set(cashier_data)
                db.collection('Countsettings').document('CashierIDs').update({'count': value2})

                
                # Update the Treeview table with new values
                # Function to select the item based on matching values
                def select_item_by_values(column_values):
                    for item in tree.get_children():
                        item_values = tree.item(item, "values")
                        if len(item_values) > 1 and item_values[1] == column_values:  # Check if the bus_id matches
                            tree.selection_set(item)
                            tree.see(item)  # Scroll to the selected item
                            return
                filter_cashiers(db, tree)
                select_item_by_values(cashier_id_val)

                add_window.destroy()
                messagebox.showinfo("Info", "New Cashier is Added Successfully!")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to add cashier: {e}")

        ctk.CTkButton(add_window, text="Save", command=save_cashier, text_color="#191970",
                      fg_color="#E2E2B6", hover_color="#6EACDA").grid(row=10, column=0, columnspan=2, pady=10)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to create add cashier window: {e}")





#function to run when the delete button is clcked 
def delete_cashier(db, tree):
    selected_item = tree.selection()
    selected_item = tree.item(selected_item)
    values = selected_item['values']

    if not selected_item:# check if theres a selected value in treeview
        messagebox.showwarning("Warning", "Please select a cashier to delete.")# show error mesage when none
        return # exit funct.

    cashier_id = values[1] # store the the Id of slected row in treeview

    #finding match
     # Confirm before deleting
    confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this driver?")
    if confirm: # if yes

        try:# try cach to prevent and detcte error 
            cashier_ref = db.collection('Cashier').where('ID', '==' ,cashier_id)
            cashier_docs = cashier_ref.stream()

            # Find the correct document and fetch the UID
            for doc in cashier_docs:
                uid = doc.id  # Use the document name as the UID
                auth.delete_user(uid)
                
                print(f"Successfully deleted authentication account with UID: {uid}")

                db.collection('Cashier').document(uid).delete() # delete doc with the match id to var cashier Id

                filter_cashiers(db, tree, terminal_location="All", query="")# refresh treeview
                messagebox.showinfo("Info", "Cashier deleted successfully.")# show success mesage box
                return
            
             # If no document matched the given cashier_id
            print(f"No document found with ID {cashier_id} in the cashier collection.")
        except exceptions.FirebaseError as e:
            messagebox.showerror("Error", f"Failed to delete cashier: {e}")# show notif with def about the error
    else: # if no
        return



# Function to run when edit button is clicked 
def edit_cashier(db, tree):
    selected_item = tree.selection()  # get selected item in treeview
    if not selected_item:  # check if no selected item on treeview
        messagebox.showwarning("Warning", "Please select a cashier to edit.")  # show warning message if none
        return  # exit function

    selected_item = tree.item(selected_item)
    values = selected_item['values']
    cashier_id = values[1]  # store the ID of selected row
    uid = values[6]
    cashier_data = db.collection('Cashier').document(uid).get().to_dict()  # fetch the document data

    # Function to validate phone number input
    def validate_phone_input(char):
        return char.isdigit() and len(phone_number.get()) <= 11  # Only digits and max 10 digits
    
    # Create a new window form 
    edit_window = ctk.CTkToplevel()
    edit_window.title("Edit Cashier")
    edit_window.lift()
    edit_window.attributes("-topmost", True)
    edit_window.configure(fg_color="#03346E")

     # --- Validation for numeric entries ---
    def validate_numeric(P):
        if P == "":
            return True
        try:                
            float(P)
            return True
        except ValueError:
            return False

    vcmd = (edit_window.register(validate_numeric), '%P')

    # Labels and Entry widgets for collecting inputs
    ctk.CTkLabel(edit_window, text="Cashier ID:", text_color="#E2E2B6").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    cashier_id_label = ctk.CTkEntry(edit_window, text_color="#191970")
    cashier_id_label.grid(row=0, column=1, padx=10, pady=5)
    cashier_id_label.insert(0, cashier_id)
    cashier_id_label.configure(state="disabled")

    ctk.CTkLabel(edit_window, text="First Name:", text_color="#E2E2B6").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    first_name = ctk.CTkEntry(edit_window, text_color="#191970")
    first_name.grid(row=1, column=1, padx=10, pady=5)
    first_name.insert(0, cashier_data['first_name'])

    ctk.CTkLabel(edit_window, text="Last Name:", text_color="#E2E2B6").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    last_name = ctk.CTkEntry(edit_window, text_color="#191970")
    last_name.grid(row=2, column=1, padx=10, pady=5)
    last_name.insert(0, cashier_data['last_name'])

    ctk.CTkLabel(edit_window, text="Middle Name:", text_color="#E2E2B6").grid(row=3, column=0, padx=10, pady=5, sticky="e")
    middle_name = ctk.CTkEntry(edit_window, text_color="#191970")
    middle_name.grid(row=3, column=1, padx=10, pady=5)
    middle_name.insert(0, cashier_data.get('middle_name',''))

    ctk.CTkLabel(edit_window, text="Address:", text_color="#E2E2B6").grid(row=4, column=0, padx=10, pady=5, sticky="e")
    address = ctk.CTkEntry(edit_window, text_color="#191970")
    address.grid(row=4, column=1, padx=10, pady=5)
    address.insert(0, cashier_data['address'])

    # Phone Number with validation
    ctk.CTkLabel(edit_window, text="Phone Number:", text_color="#E2E2B6").grid(row=5, column=0, padx=10, pady=5, sticky="e")
    phone_number = ctk.CTkEntry(edit_window, text_color="#191970", validate="key", 
                                validatecommand=(edit_window.register(validate_phone_input), "%S"))
    phone_number.grid(row=5, column=1, padx=10, pady=5)
    phone_number.insert(0, cashier_data['phone_number'])

    ctk.CTkLabel(edit_window, text="Terminal Location:", text_color="#E2E2B6").grid(row=6, column=0, padx=10, pady=5, sticky="e")
    terminal_location = ctk.CTkEntry(edit_window, text_color="#191970")
    terminal_location.grid(row=6, column=1, padx=10, pady=5)
    terminal_location.insert(0, cashier_data['terminal_location'])

    # Hourly Wage with numeric validation
    ctk.CTkLabel(edit_window, text="Hourly Wage:", text_color="#E2E2B6").grid(row=7, column=0, padx=10, pady=5, sticky="e")
    hourly_wage = ctk.CTkEntry(edit_window, text_color="#191970", validate="key",
                               validatecommand=vcmd)
    hourly_wage.grid(row=7, column=1, padx=10, pady=5)
    hourly_wage.insert(0, cashier_data['hourly_wage'])

    ctk.CTkLabel(edit_window, text="Status:", text_color="#E2E2B6").grid(row=8, column=0, padx=10, pady=5, sticky="e")
    status_options = ["Active", "Inactive"]
    status_var = ctk.StringVar(value=cashier_data['status'])
    status = ctk.CTkComboBox(edit_window, values=status_options, variable=status_var, text_color="#191970")
    status.grid(row=8, column=1, padx=10, pady=5)


    # Function to update cashier data
    def update_cashier():
        try:
            updated_cashier_data = {
                'ID': cashier_id,
                'first_name': first_name.get(),
                'last_name': last_name.get(),
                'middle_name': middle_name.get(),
                'address': address.get(),
                'phone_number': phone_number.get(),
                'terminal_location': terminal_location.get(),
                'hourly_wage': hourly_wage.get(),
                'status': status.get(),
            }
            # Validate all fields are filled
            if any(not value for value in updated_cashier_data.values()):
                messagebox.showerror("Error", "All fields must be filled.")
                return
            
            # Update the cashier document in Firestore
            db.collection('Cashier').document(uid).update(updated_cashier_data)

            # Update the Treeview table with new values
            # Function to select the item based on matching values
            def select_item_by_values(column_values):
                for item in tree.get_children():
                    item_values = tree.item(item, "values")                        
                    if len(item_values) > 1 and item_values[1] == column_values:    
                        # Check if the bus_id matches
                        tree.selection_set(item)
                        tree.see(item)  # Scroll to the selected item
                        return
            filter_cashiers(db, tree)
            select_item_by_values(cashier_id)
            
            edit_window.destroy()  # Close the window
            messagebox.showinfo("Info", "Cashier updated successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update cashier: {e}")

    # Save Button
    ctk.CTkButton(edit_window, text="Update", command=update_cashier, text_color="#191970",
                  fg_color="#E2E2B6", hover_color="#6EACDA").grid(row=9, column=0, columnspan=2, pady=10)

