# imports for GUI and database connection
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox # treview and message box
from firebase_config import db  # Import the Firestore client from firebase_config.py
from forHover import set_hover_color

#function to update the main_content_frame from main window
count = 1

heavyrow = "#ADBBDA"
lightrow = "#EDE8F5"
vio = "#191970"
white = "white"
purplr ="#9747FF"
red ="#FF3737"
lightblue ="#4682B4"
vin="#03346E"

search_value = ""
status_filter = "All"
terminal_filter = "All"
id_filter=""

def manage_drivers(action, main_content_frame):
    global search_value, status_filter, terminal_filter, id_filter

    # Clear existing widgets from the frame
    for widget in main_content_frame.winfo_children():
        widget.destroy()

    # Fetch service terminals and drivers data
    terminals = ["All"]
    drivers = list(db.collection('Drivers').stream())  # Fetch all documents in 'Drivers' collection
    for driver in drivers:
        terminal = driver.to_dict().get('service_terminal', '')
        if terminal and terminal not in terminals:
            terminals.append(terminal)

    # Setup the UI components
    c_frame = ctk.CTkFrame(main_content_frame, corner_radius=0, fg_color=vin)
    c_frame.pack(fill="x")

    # Container Frames
    buttons_frame = ctk.CTkFrame(c_frame, corner_radius=0, fg_color=vin)
    search_frame = ctk.CTkFrame(c_frame, corner_radius=0, fg_color=vin)
    tree_frame = ctk.CTkFrame(main_content_frame)
    buttons_frame.pack(fill="x")
    search_frame.pack(fill="x")
    tree_frame.pack(fill="both", expand=True)

    search_frame.columnconfigure(tuple(range(7)), weight=1)

    # Title and Add Button
    ctk.CTkLabel(buttons_frame, text="DRIVERS", text_color=white, font=("Arial", 23, "bold")).pack(side="left", pady=(10, 5), padx=20)

    add = ctk.CTkButton(buttons_frame, text="Add", fg_color=white, text_color=vio, font=("Arial", 16, "bold"), command=lambda: create_driver(db, tree), height=35)
    add.pack(side="left", padx=5)
    set_hover_color(add, hover_bg_color=purplr, hover_text_color=white, normal_bg_color=white, normal_text_color=vio)

    # Filter Widgets
    service_terminal_var = ctk.StringVar(value=terminal_filter)

    # Status Button
    ctk.CTkLabel(search_frame, text="Status:", text_color=white, ).grid(row=0, column=0, padx=10, pady=(5,0), sticky="w")

    status_button = ctk.CTkButton(search_frame, text=status_filter, fg_color=white, text_color=vio, font=("Arial", 16, "bold"), command=lambda: cycle_status(status_button))
    status_button.grid(row=1, column=0, padx=(20, 5), pady=(0, 10), sticky="w")
    set_hover_color(status_button, hover_bg_color=purplr, hover_text_color=white, normal_bg_color=white, normal_text_color=vio)


    ctk.CTkLabel(search_frame, text="Service Terminal:", text_color=white).grid(row=0, column=1, padx=10, pady=(5, 0), sticky="w")
    service_terminal_dropdown = ctk.CTkComboBox(search_frame, variable=service_terminal_var, values=terminals, 
                                                command=lambda _: update_filters())
    service_terminal_dropdown.grid(row=1, column=1, padx=5, pady=(0, 10), sticky="w")

    ctk.CTkLabel(search_frame, text="NAME:", text_color=white).grid(row=0, column=2, padx=10, pady=(5, 0), sticky="w")
    search_entry = ctk.CTkEntry(search_frame, text_color="#191970", width=150, placeholder_text="Jaun D", 
                                placeholder_text_color="#6eacda")
    search_entry.grid(row=1, column=2, padx=5, pady=(0, 10), sticky="w")
    search_entry.bind("<Return>", lambda event: update_filters(search_entry.get()))

     # Search By ID Filter
    ctk.CTkLabel(search_frame, text="SEARCH BY ID:", text_color=white).grid(row=0, column=3, padx=10, pady=(5, 0), sticky="w")
    search_by_id_entry = ctk.CTkEntry(search_frame, text_color="#191970", width=150, placeholder_text="License or Name", 
                                      placeholder_text_color="#6eacda")
    search_by_id_entry.grid(row=1, column=3, padx=5, pady=(0, 10), sticky="w")
    search_by_id_entry.bind("<Return>", lambda event: update_filters(search_by_id_entry.get()))


    delete = ctk.CTkButton(search_frame, text="Delete", command=lambda: delete_driver(db, tree), fg_color=white, 
                           text_color=red, height=35, font=("Arial", 16, "bold"))
    delete.grid(row=0, column=7, rowspan=2, padx=(5, 20), pady=(20, 10), sticky="e")
    edit = ctk.CTkButton(search_frame, text="Edit", command=lambda: edit_driver(db, tree), fg_color=white, 
                         text_color=vio, height=35, font=("Arial", 16, "bold"))
    edit.grid(row=0, column=6, rowspan=2, padx=5, pady=(20, 10), sticky="e")

    set_hover_color(delete, hover_bg_color=red, hover_text_color=white, normal_bg_color=white, normal_text_color=red)
    set_hover_color(edit, hover_bg_color=lightblue, hover_text_color=white, normal_bg_color=white, normal_text_color=vio)

    # Treeview Configuration
    columns = ("No.", "Driver ID", "First Name", "Last Name", "License No.", "Phone No.", "Address", "Srvc. Trm", "Wage/Hr.", "Status")


    tree_scroll = tk.Scrollbar(tree_frame)
    tree_scroll.pack(side="right", fill="y")

    tree = ttk.Treeview(tree_frame, columns=columns, yscrollcommand=tree_scroll.set, show='headings')
    for col in columns:
        tree.heading(col, text=col)
        if col == "No.":
            tree.column(col, minwidth=0, width=60 )
        elif col == "Driver ID"  or col =="Srvc. Trm":
            tree.column(col, minwidth=0, width=100 )
        elif col == "Wage/Hr." :
            tree.column(col, minwidth=0, width=90 )
        elif col == "Status" :
            tree.column(col, minwidth=0, width=75, anchor='center')
        elif  col == "Address" or col=="Phone No.":
            tree.column(col, minwidth=0, width=120 )
        elif col == "License No.":
             tree.column(col, minwidth=0, width=110 )
        else:
            tree.column(col, minwidth=0, width=130 )

    tree.pack(fill="both", expand=True)
    tree_scroll.config(command=tree.yview)

    tree.tag_configure('oddrow', background=heavyrow)
    tree.tag_configure('evenrow', background=lightrow)
    tree.tag_configure('Inactive', background="#999")
    tree.bind("<Double-1>", lambda e: edit_driver(db, tree))

    # Update global filters
    def update_filters(*args):
        global search_value, status_filter, terminal_filter, id_filter
        search_value = search_entry.get() if search_entry.get() is not None else search_value
        status_filter = status_button.cget("text")
        terminal_filter = service_terminal_var.get()
        id_filter = search_by_id_entry.get() if search_by_id_entry.get() is not None else id_filter
        refresh_tree(db, tree)

    # Cycle Status Button Function
    def cycle_status(button):
        options = ["All", "Active", "Inactive"]
        current_index = options.index(button.cget("text"))
        new_status = options[(current_index + 1) % len(options)]
        button.configure(text=new_status)
        update_filters()

    refresh_tree(db, tree)


# function to generate the next driver id for creating new drivers
def get_next_driver_id(db):
    try:
        # Access a shared counter document in Firestore
        counter_doc = db.collection('Countsettings').document('DriverIDs')
        counter_data = counter_doc.get()

        # Check if the document exists and get the value
        if counter_data.exists:
            driver_count = counter_data.to_dict().get('count', 1)

        else: # If the document doesn't exist, initialize the bus count
            driver_count = 1
            # Create the document with the initial count
            counter_doc.set({'count': driver_count})

        while True: # Generate the bus ID as the document name
            driver_id = f"DRVR-{driver_count:05d}"

            # Check if a document with this ID (name) exists
            existing_bus_doc = db.collection('Drivers').document(driver_id).get()
            if not existing_bus_doc.exists:
                # If no document found, use this bus_id as the new document name
                print(f"Unique driver ID generated: {driver_id}")
                # Update the counter in Firestore
                #counter_doc.update({'count': driver_count + 1})
                break
            else: # Increment and check again if there’s a conflict
                driver_count += 1
                print(f"driver ID occupied at: {driver_id}")

    except Exception as e:
        print("Error", f"Failed to generate Bus ID: {e}")

    return driver_id, driver_count + 1 # return the value


# function to run when create button si clicked 
def create_driver(db, tree):
    #create new form window 
    create_window = ctk.CTkToplevel()
    create_window.title("Add Driver")

    # Keep the window on top
    create_window.lift()
    create_window.attributes("-topmost", True)
    create_window.configure(fg_color="#03346E")

    result1, result2 = get_next_driver_id(db)

     # --- Validation for numeric entries ---
    def validate_phone_number(P):
        if P.isdigit() and len(P) <= 11 or P == "":
            return True  # Only digits allowed and maximum length is 11
        return False
    # Register the validation function
    phone_vcmd = create_window.register(validate_phone_number)

    def validate_numeric(P):
        if P == "":
            return True
        try:
            float(P)
            return True
        except ValueError:
            return False

    vcmd = (create_window.register(validate_numeric), '%P')
    # label and entry object for needed user input. 
    ctk.CTkLabel(create_window, text="Driver ID:", text_color="#E2E2B6").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    driver_id = ctk.CTkEntry(create_window, text_color="#191970")
    driver_id.grid(row=0, column=1, padx=10, pady=5)
    driver_id.insert(0, result1)  # Suggestive Driver ID
    driver_id.configure(state='disabled')  # Disable editing of Driver ID

    ctk.CTkLabel(create_window, text="First Name:", text_color="#E2E2B6").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    first_name = ctk.CTkEntry(create_window, placeholder_text = "Juan", text_color="#191970")
    first_name.grid(row=1, column=1, padx=10, pady=5)

    ctk.CTkLabel(create_window, text="Last Name:", text_color="#E2E2B6").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    last_name = ctk.CTkEntry(create_window, placeholder_text = "Cruz", text_color="#191970")
    last_name.grid(row=2, column=1, padx=10, pady=5)

    ctk.CTkLabel(create_window, text="License Number:", text_color="#E2E2B6").grid(row=3, column=0, padx=10, pady=5, sticky="e")
    license_number = ctk.CTkEntry(create_window, placeholder_text = "A00-00-000000", text_color="#191970")
    license_number.grid(row=3, column=1, padx=10, pady=5)

    ctk.CTkLabel(create_window, text="Phone Number:", text_color="#E2E2B6").grid(row=4, column=0, padx=10, pady=5, sticky="e")
    phone_number = ctk.CTkEntry(create_window, placeholder_text = "09123456789", text_color="#191970", validate="key", validatecommand=(phone_vcmd, '%P'))
    phone_number.grid(row=4, column=1, padx=10, pady=5)

    ctk.CTkLabel(create_window, text="Address:", text_color="#E2E2B6").grid(row=5, column=0, padx=10, pady=5, sticky="e")
    address = ctk.CTkEntry(create_window, placeholder_text = "Barangay 307 Quiapo, City of Manila", text_color="#191970")
    address.grid(row=5, column=1, padx=10, pady=5)

    ctk.CTkLabel(create_window, text="Service Terminal:", text_color="#E2E2B6").grid(row=6, column=0, padx=10, pady=5, sticky="e")
    service_terminal = ctk.CTkEntry(create_window, placeholder_text = "Manila", text_color="#191970")
    service_terminal.grid(row=6, column=1, padx=10, pady=5)

    ctk.CTkLabel(create_window, text="Hourly Wage (₱):", text_color="#E2E2B6").grid(row=7, column=0, padx=10, pady=5, sticky="e")
    hourly_wage = ctk.CTkEntry(create_window, text_color="#191970", validate="key", validatecommand=(vcmd, '%P'))
    hourly_wage.grid(row=7, column=1, padx=10, pady=5)

    # Validation for hourly wage
    def validate_hourly_wage(char, current_value):
        # Allow only digits, decimal points, or empty value
        if char in "0123456789." and (current_value.count('.') <= 1):
            return True
        return False
    # Register validation callback
    validate_cmd = create_window.register(validate_hourly_wage)
    hourly_wage.configure(validate="key", validatecommand=(validate_cmd, "%S", "%P"))

    ctk.CTkLabel(create_window, text="Status:", text_color="#E2E2B6").grid(row=8, column=0, padx=10, pady=5, sticky="e")
    status_options = ["Active", "Inactive"]  # Predefined options
    status = ctk.StringVar(value="Active") 
    status_dropdown = ctk.CTkComboBox(create_window, values=status_options, variable=status, width=160, text_color="#191970")
    status_dropdown.grid(row=8, column=1,  padx=10, pady=5)

    # Function to run when Save button is clicked 
    def save_driver():
        driver_id_value = driver_id.get() # get the gen. driver ID

        try:
            # Convert hourly wage to float
            hourly_wage_value = float(hourly_wage.get())
        except ValueError:
            messagebox.showerror("Input Error", "Hourly Wage must be a valid number.")
            return

        #store user input in a dict.
        driver_data = {
            'first_name': first_name.get(),
            'last_name': last_name.get(),
            'license_number': license_number.get(),
            'phone_number': phone_number.get(),
            'address': address.get(),
            'service_terminal': service_terminal.get(),
            'hourly_wage': hourly_wage_value,
            'status': status.get()
        }
        # Validate all fields are filled
        if any(not value for value in driver_data.values()):
            messagebox.showerror("Error", "All fields must be filled.")
            return
        
        existing_drivers = db.collection('Drivers').where('license_number', '==', driver_data['license_number']).get()
        if existing_drivers:
            messagebox.showerror("Error", f"A driver with license number {driver_data['license_number']} already exists.")
            return
        
        # Check if the driver ID already exists
        if db.collection('Drivers').document(driver_id_value).get().exists:
            messagebox.showerror("Error", "Driver ID already exists.") # show error if theres 
            return # un execute the code
        
        # Create the new driver document
        db.collection('Drivers').document(driver_id_value).set(driver_data)

        # Function to select the item based on matching BusID
        def select_item_by_bus_id(bus_id):
            for item in tree.get_children():
                item_values = tree.item(item, "values")
                if item_values[1] == driver_id_value:  # Assuming column 1 is BusID
                    tree.selection_set(item)
                    tree.see(item)  # Scroll to the selected item
                    break  # Exit after finding the match
            
        db.collection('Countsettings').document('DriverIDs').update({'count' :  result2 })
        # Refresh the Treeview contents
        refresh_tree(db, tree)
        # Call the function to select the newly added item
        select_item_by_bus_id(driver_id_value)
        
        create_window.destroy() # destry created window form 
        messagebox.showinfo("Success", "Driver added successfully.") # show notif

    # save button
    ctk.CTkButton(create_window, text="Save", command=save_driver, text_color="#191970", fg_color="#e2e2b6", hover_color="#6EACDA").grid(row=9, columnspan=2, pady=10)


# function to run when edit button is clicked 
def edit_driver(db, tree):
    selected_item = tree.selection() # the the val of selected row in treeview table
    if selected_item:# check if theres a selcted value in treeview
        # fetch selected Item and its vals
        item = tree.item(selected_item) 
        values = item['values']

        # Fetch the document for the selected schedule
        driver_doc = db.collection('Drivers').document(values[1]).get()
        if not driver_doc.exists:
            messagebox.showerror("Error", "Selected Driver document is not exsisting in the system.")
            return
        driver_data = driver_doc.to_dict()

        # create a new window form
        edit_window = ctk.CTkToplevel()
        edit_window.title("Edit Driver")
        # Keep the window on top
        edit_window.lift()
        edit_window.attributes("-topmost", True)
        edit_window.configure(fg_color="#03346e")

        # abels and entry objs for needed user inputs 
        ctk.CTkLabel(edit_window, text="Driver ID:", text_color="#E2E2B6").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        driver_id = ctk.CTkEntry(edit_window)
        driver_id.grid(row=0, column=1, padx=10, pady=5)
        driver_id.insert(0, values[1])
        driver_id.configure(state='disabled')  # Disable editing of Driver ID

        ctk.CTkLabel(edit_window, text="First Name:", text_color="#E2E2B6").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        first_name = ctk.CTkEntry(edit_window, text_color="#191970")
        first_name.grid(row=1, column=1, padx=10, pady=5)
        first_name.insert(0, driver_data['first_name']) # fetch coressponding val frm the selected row in treview

        ctk.CTkLabel(edit_window, text="Last Name:", text_color="#E2E2B6").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        last_name = ctk.CTkEntry(edit_window, text_color="#191970")
        last_name.grid(row=2, column=1, padx=10, pady=5)
        last_name.insert(0, driver_data['last_name']) # fetch coressponding val frm the selected row in treview

        ctk.CTkLabel(edit_window, text="License Number:", text_color="#E2E2B6").grid(row=3, column=0, padx=10, pady=5, sticky="e")
        license_number = ctk.CTkEntry(edit_window, text_color="#191970")
        license_number.grid(row=3, column=1, padx=10, pady=5)
        license_number.insert(0, driver_data['license_number']) # fetch coressponding val frm the selected row in treview

        ctk.CTkLabel(edit_window, text="Phone Number:", text_color="#E2E2B6").grid(row=4, column=0, padx=10, pady=5, sticky="e")
        phone_number = ctk.CTkEntry(edit_window, text_color="#191970")
        phone_number.grid(row=4, column=1, padx=10, pady=5)
        phone_number.insert(0, driver_data['phone_number']) # fetch coressponding val frm the selected row in treview

        ctk.CTkLabel(edit_window, text="Address:", text_color="#E2E2B6").grid(row=5, column=0, padx=10, pady=5, sticky="e")
        address = ctk.CTkEntry(edit_window, text_color="#191970")
        address.grid(row=5, column=1, padx=10, pady=5)
        address.insert(0, driver_data['first_name']) # fetch coressponding val frm the selected row in treview

        ctk.CTkLabel(edit_window, text="Service Terminal:", text_color="#E2E2B6").grid(row=6, column=0, padx=10, pady=5, sticky="e")
        service_terminal = ctk.CTkEntry(edit_window, text_color="#191970")
        service_terminal.grid(row=6, column=1, padx=10, pady=5)
        service_terminal.insert(0, driver_data['service_terminal']) # fetch coressponding val frm the selected row in treview

        ctk.CTkLabel(edit_window, text="Hourly Wage:", text_color="#E2E2B6").grid(row=7, column=0, padx=10, pady=5, sticky="e")
        hourly_wage = ctk.CTkEntry(edit_window)
        hourly_wage.grid(row=7, column=1, padx=10, pady=5)
        hourly_wage.insert(0, driver_data['hourly_wage']) # fetch coressponding val frm the selected row in treview

        # Validation for hourly wage
        def validate_hourly_wage(char, current_value):
            # Allow only digits, decimal points, or empty value
            if char in "0123456789." and (current_value.count('.') <= 1):
                return True
            return False
        # Register validation callback
        validate_cmd = edit_window.register(validate_hourly_wage)
        hourly_wage.configure(validate="key", validatecommand=(validate_cmd, "%S", "%P"))

        ctk.CTkLabel(edit_window, text="Status:", text_color="#E2E2B6").grid(row=8, column=0, padx=10, pady=5, sticky="e")
        status_options = ["Active", "Inactive"]  # Predefined options
        status = ctk.StringVar(value = driver_data['status']) 
        status_dropdown = ctk.CTkComboBox(edit_window, values=status_options, variable=status, width=160, text_color="#191970")
        status_dropdown.grid(row=8, column=1,  padx=10, pady=5)

        # function to run when save button is clicked 
        def update_driver():
            try:
                # Convert hourly wage to float
                hourly_wage_value = float(hourly_wage.get())
            except ValueError:
                messagebox.showerror("Input Error", "Hourly Wage must be a valid number.")
                return
            # store user inputs in a dict.
            driver_data = {
                'first_name': first_name.get(),
                'last_name': last_name.get(),
                'license_number': license_number.get(),
                'phone_number': phone_number.get(),
                'address': address.get(),
                'service_terminal': service_terminal.get(),
                'hourly_wage': hourly_wage_value,
                'status': status.get()
            }
            # Validate all fields are filled
            if any(not value for value in driver_data.values()):
                messagebox.showerror("Error", "All fields must be filled.")
                return
        
            # Check for duplicate license_number in other documents
            existing_drivers = db.collection('Drivers').where('license_number', '==', driver_data['license_number']).get()
            for doc in existing_drivers:
                if doc.id != values[1]:  # Exclude the current document (Driver ID)
                    messagebox.showerror("Error", f"A driver with license number {driver_data['license_number']} already exists.")
                    return

            db.collection('Drivers').document(values[1]).update(driver_data) # update/insert data to the doc with match ID

            # Function to select the item based on matching BusID
            def select_item_by_bus_id(bus_id):
                for item in tree.get_children():
                    item_values = tree.item(item, "values")
                    if item_values[1] == bus_id:  # Assuming column 1 is BusID
                        tree.selection_set(item)
                        tree.see(item)  # Scroll to the selected item
                        break  # Exit after finding the match

            # Refresh the Treeview contents
            refresh_tree(db, tree)
            # Call the function to select the newly added item
            select_item_by_bus_id(values[1])
            
            edit_window.destroy()# destroy the created window form 
            messagebox.showinfo("Success", "Driver updated successfully.")# show success notif

        # save button
        ctk.CTkButton(edit_window, text="Save", command=update_driver , text_color="#191970", fg_color="#E2E2B6", hover_color="#6EACDA").grid(row=9, columnspan=2, pady=10)

    else:# when theres no selcted val in treeview
        messagebox.showerror("Error", "Please select a driver to edit.")# show error message 

# function to run when delete button is clicked 
def delete_driver(db, tree):
    selected_item = tree.selection() # fetch the selected val in treeview
    if selected_item: #check if theres a selected val in treeview
        # get the slected row an store its data in a list
        item = tree.item(selected_item) 
        driver_id = item['values'][1]
        
        # Confirm before deleting
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this driver?")
        if confirm: # if yes
            db.collection('Drivers').document(driver_id).delete()
            refresh_tree(db, tree)
            messagebox.showinfo("Success", "Driver deleted successfully.")
        else: # if no
            return
    else:
        messagebox.showerror("Error", "Please select a driver to delete.")

def refresh_tree(db, tree):
    global search_value, status_filter, terminal_filter, id_filter
    drivers = list(db.collection('Drivers').stream())  # Fetch all documents in 'Drivers' collection
    tree.delete(*tree.get_children())
    count = 1
    # Lowercase the search value for case-insensitive comparison
    value_search = id_filter.strip().upper() 

    for driver in drivers:
        data = driver.to_dict()

        id = driver.id
        full_name = f"{data.get('first_name', '')} {data.get('last_name', '')}".lower()
        license_number = data.get('license_number', '').strip().upper()

        # Apply filters
        if ((status_filter == "All" or data.get('status', '') == status_filter) and
            (terminal_filter == "All" or data.get('service_terminal', '') == terminal_filter) and
            (search_value.lower() in full_name) and
            (not value_search or value_search in id or value_search in license_number)):
            row_tag = "Inactive" if data.get('status') == "Inactive" else "oddrow" if count % 2 == 0 else "evenrow"
            tree.insert("", "end", 
                values=(count, 
                    driver.id, 
                    data.get('first_name', ''), 
                    data.get('last_name', ''), 
                    data.get('license_number', ''), 
                    data.get('phone_number', ''), 
                    data.get('address', ''), 
                    data.get('service_terminal', ''), 
                    f"₱. {data.get('hourly_wage', '')}", 
                    data.get('status', '')), tags=(row_tag,))
            count += 1