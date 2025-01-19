
# imports for gui and database connection
import customtkinter as ctk # gui
import tkinter as tk
from tkinter import ttk, messagebox # treeview and messagebox
from firebase_config import db # database connection
from forHover import set_hover_color

count =1
heavyrow = "#ADBBDA"
lightrow = "#EDE8F5"
vio = "#191970"
white = "white"
purplr ="#9747FF"
red ="#FF3737"
lightblue ="#4682B4"
vin ="#03346E"

# Define global variables for filters
global_route_var = "All"
global_unit_type_var = "All"
global_bus_class_var = "All"
global_search_var = ""

# Function to update the main_content_function
def manage_gas_costing(action, main_content_frame):
    global global_route_var, global_unit_type_var, global_bus_class_var, global_search_var

    # Clear the main_content_frame
    for widget in main_content_frame.winfo_children():
        widget.destroy()

    # Code for button frame for managing bus schedule (serve as title holder)
    c_frame = ctk.CTkFrame(main_content_frame, corner_radius=0, fg_color=vin)
    c_frame.pack(fill="x")
    
    # Button frame to hold the topbar, title, and add button
    button_frame = ctk.CTkFrame(c_frame, corner_radius=0, fg_color=vin)
    button_frame.pack(fill="x")

    # Title
    title_label = ctk.CTkLabel(button_frame, text="GAS COSTING", text_color=white, font=("Arial", 23, "bold"), corner_radius=0)
    title_label.pack(side="left", pady=(10, 10), padx=20)

    # Add button
    add = ctk.CTkButton(button_frame, text="Add", fg_color="#fff", text_color="#191970", command=lambda: create_gas_costing(db, tree), font=("Arial", 16, "bold"), height=35)
    add.pack(side=ctk.LEFT, padx=5)
    set_hover_color(add, hover_bg_color=purplr, hover_text_color=white, normal_bg_color=white, normal_text_color=vio)

    # Filter frame to hold filtering widgets
    filter_frame = ctk.CTkFrame(c_frame, corner_radius=0, fg_color=vin)
    filter_frame.pack(fill="x")
    filter_frame.columnconfigure(tuple(range(7)), weight=1)

    # Dropdown for ScheduleRoute
    ctk.CTkLabel(filter_frame, text="Filter by Route:", text_color=white).grid(row=0, column=0, padx=(25, 5), pady=(5, 0), sticky="w")
    routes = {"All"}
    gas_costing = db.collection('GasCosting').get()
    for gas in gas_costing:
        data = gas.to_dict()
        routes.add(data['ScheduleRoute'])
    route_dropdown = ctk.CTkComboBox(filter_frame, values=list(sorted(routes)), variable=ctk.StringVar(value=global_route_var))
    route_dropdown.grid(row=1, column=0, padx=(20, 5), pady=(0, 10), sticky="w")

    # Dropdown for Unit Type
    ctk.CTkLabel(filter_frame, text="Filter by Unit Type:", text_color=white).grid(row=0, column=1, padx=10, pady=(5, 0), sticky="w")
    unit_types = {"All"}
    unit_type_docs = db.collection('Unit_type').get()
    for doc in unit_type_docs:
        unit_types.add(doc.id)  # Assuming document names are used as dropdown values
    unit_type_dropdown = ctk.CTkComboBox(filter_frame, values=list(sorted(unit_types)), variable=ctk.StringVar(value=global_unit_type_var))
    unit_type_dropdown.grid(row=1, column=1, padx=(0,5), pady=(0, 10), sticky="w")

    # Dropdown for Bus Class
    ctk.CTkLabel(filter_frame, text="Filter by Bus Class:", text_color=white).grid(row=0, column=2, padx=10, pady=(5, 0), sticky="w")
    bus_classes = ["All", "AC", "NAC"]
    bus_class_dropdown = ctk.CTkComboBox(filter_frame, values=bus_classes, variable=ctk.StringVar(value=global_bus_class_var))
    bus_class_dropdown.grid(row=1, column=2, padx=(0,5), pady=(0, 10), sticky="w")

    # Search Bar
    ctk.CTkLabel(filter_frame, text="Search Bus ID:", text_color=white).grid(row=0, column=3, padx=10, pady=(5, 0), sticky="w")
    search_entry = ctk.CTkEntry(filter_frame, width=200, placeholder_text="BUSS-0000", placeholder_text_color="#6eacda")
    search_entry.insert(0, global_search_var)
    search_entry.grid(row=1, column=3, padx=(0,5), pady=(0, 10), sticky="w")

    # Treeview Filter Function
    def filter_treeview(*args):
        global count, global_route_var, global_unit_type_var, global_bus_class_var, global_search_var
        
        # Update global variables
        global_search_var = search_entry.get().lower()
        global_route_var = route_dropdown.get()
        global_unit_type_var = unit_type_dropdown.get()
        global_bus_class_var = bus_class_dropdown.get()

        refresh_tree(db,tree)


    # Bind dropdowns and search entry to filter_treeview
    route_dropdown.configure(command=filter_treeview)
    unit_type_dropdown.configure(command=filter_treeview)
    bus_class_dropdown.configure(command=filter_treeview)
    search_entry.bind("<Return>", filter_treeview)

     # Bind the search entry to filter_treeview to update when the search button is clicked
    #ctk.CTkButton(filter_frame, text="Search", command=filter_treeview).grid(row=1, column=2, padx=5, pady=5, sticky="w")

    delete=ctk.CTkButton(filter_frame, text="Delete", command=lambda: delete_gas_costing(db, tree),fg_color=white,text_color=red, height=35, font=("Arial", 16, "bold"))
    delete.grid(row=0, column=7, rowspan=2, padx=(5,20), pady=(25,10), sticky="e")
    edit=ctk.CTkButton(filter_frame, text="Edit", command=lambda: edit_gas_costing(db, tree),fg_color=white,text_color=vio, height=35, font=("Arial", 16, "bold"))
    edit.grid(row=0, column=6, rowspan=2, padx=5, pady=(25,10), sticky="e")

    # Treeview Table Setup
    columns = ("No.", "Bus ID", "Unit Type", "Bus Class", "Gas Cost/Km", "Gas Fund", "Schedule Route")
    tree_frame = ctk.CTkFrame(main_content_frame)
    tree_frame.pack(fill="both", expand=True)
    tree_scroll = tk.Scrollbar(tree_frame)
    tree_scroll.pack(side="right", fill="y")
    tree = ttk.Treeview(tree_frame, columns=columns, yscrollcommand=tree_scroll.set, show='headings')
    tree.tag_configure('oddrow', background=heavyrow)
    tree.tag_configure('evenrow', background=lightrow)
    for col in columns:
        tree.heading(col, text=col)
        if col == "No.":
           tree.column(col, minwidth=0, width=30)
        elif col == "Bus Class":
            tree.column(col, minwidth=0, width=70, anchor="center")
        elif col == "Unit Type":
            tree.column(col, minwidth=0, width=90)
        elif col == "Bus ID":
            tree.column(col, minwidth=0, width=100)
        elif col == "Gas Cost/Km":
            tree.column(col, minwidth=0, width=140)
        else:
            tree.column(col, minwidth=0, width=170)
    tree.pack(fill=ctk.BOTH, expand=True)
    tree_scroll.config(command=tree.yview)

    # Bind double-click to edit function
    def clicker(e):
        edit_gas_costing(db, tree)
    tree.bind("<Double-1>", clicker)

    # Load initial data
    filter_treeview()



    
def create_gas_costing(db, tree):

    # Function to validate Bus ID and update fields
    def validate_and_update_fields():
        bus_id = bus_id_var.get()
        if bus_id:
            bus_doc = db.collection('Buses').document(bus_id).get()
            if bus_doc.exists:
                bus_data = bus_doc.to_dict()

                # Enable fields to update values
                bus_unit_type.configure(state=ctk.NORMAL)
                bus_class.configure(state=ctk.NORMAL)
                gas_cost_per_km.configure(state=ctk.NORMAL)
                schedule_route.configure(state=ctk.NORMAL)

                # Update entry fields
                bus_unit_type.delete(0, ctk.END)
                bus_unit_type.insert(0, bus_data.get('unit_type', ''))
                bus_class.delete(0, ctk.END)
                bus_class.insert(0, bus_data.get('bus_class', ''))
                gas_cost_per_km.delete(0, ctk.END)
                gas_cost_per_km.insert(0, bus_data.get('fuel_cost_per_km', ''))
                schedule_route.delete(0, ctk.END)
                schedule_route.insert(0, bus_data.get('assigned_route', ''))

                # Disable fields again after updating
                bus_unit_type.configure(state=ctk.DISABLED)
                bus_class.configure(state=ctk.DISABLED)
                gas_cost_per_km.configure(state=ctk.DISABLED)
                schedule_route.configure(state=ctk.DISABLED)
            else:
                messagebox.showerror("Error", "Bus ID not found.")
        else:
            messagebox.showerror("Error", "Please enter a Bus ID.")

    # Create a window form
    create_window = ctk.CTkToplevel()
    create_window.title("Add Gas Costing")

    # Keep the window on top
    create_window.lift()
    create_window.attributes("-topmost", True)
    create_window.configure(fg_color="#03346E")

     # --- Validation for numeric entries ---
    def validate_numeric(P):
        if P == "":
            return True
        try:
            float(P)
            return True
        except ValueError:
            return False

    vcmd = (create_window.register(validate_numeric), '%P')

    # Label and entry objects for user inputs
    ctk.CTkLabel(create_window, text="Bus ID:", text_color="#E2E2B6").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    bus_id_var = ctk.StringVar()
    bus_id_entry = ctk.CTkEntry(create_window, textvariable=bus_id_var)
    bus_id_entry.grid(row=0, column=1, padx=10, pady=5)

    # Button to load data based on Bus ID, positioned directly below Bus ID entry
    load_button = ctk.CTkButton(create_window, text="Load Bus ID Data", fg_color="#6EACDA", hover_color="#E2E2B6", text_color="#191970", command=validate_and_update_fields)
    load_button.grid(row=1, columnspan=2, pady=(10,20))

    # Remaining labels and entry objects
    ctk.CTkLabel(create_window, text="Bus Unit Type:", text_color="#E2E2B6").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    bus_unit_type = ctk.CTkEntry(create_window, text_color="#191970")
    bus_unit_type.grid(row=2, column=1, padx=10, pady=5)
    bus_unit_type.configure(state=ctk.DISABLED)

    ctk.CTkLabel(create_window, text="Bus Class:", text_color="#E2E2B6").grid(row=3, column=0, padx=10, pady=5, sticky="e")
    bus_class = ctk.CTkEntry(create_window, text_color="#191970")
    bus_class.grid(row=3, column=1, padx=10, pady=5)
    bus_class.configure(state=ctk.DISABLED)

    ctk.CTkLabel(create_window, text="Gas Cost (per km):", text_color="#E2E2B6").grid(row=4, column=0, padx=10, pady=5, sticky="e")
    gas_cost_per_km = ctk.CTkEntry(create_window, text_color="#191970")
    gas_cost_per_km.grid(row=4, column=1, padx=10, pady=5)
    gas_cost_per_km.configure(state=ctk.DISABLED)

    ctk.CTkLabel(create_window, text="Gas Fund:", text_color="#E2E2B6").grid(row=5, column=0, padx=10, pady=5, sticky="e")
    gas_fund = ctk.CTkEntry(create_window, text_color="#191970",validate="key", validatecommand=vcmd)
    gas_fund.grid(row=5, column=1, padx=10, pady=5)

    ctk.CTkLabel(create_window, text="Schedule Route:", text_color="#E2E2B6").grid(row=6, column=0, padx=10, pady=5, sticky="e")
    schedule_route = ctk.CTkEntry(create_window, text_color="#191970")
    schedule_route.grid(row=6, column=1, padx=10, pady=5)
    schedule_route.configure(state=ctk.DISABLED)

    def save_gas_costing():

        if bus_id_var.get() == "" or bus_unit_type.get()=="" or bus_class.get()=="" or gas_cost_per_km.get() == "" or gas_fund.get()=="" or  schedule_route.get() =="":
            messagebox.showerror("Error", "TPlease fill all the required Inputs.")
            return

        # Check for existing schedule with the same departure time and driver
        existing_costings = db.collection('GasCosting').where('BusID', '==',  bus_id_var.get()).stream()

        if any(existing_costings):
            messagebox.showerror("Error", "The Bus Unit already have an exsisting costing in the system.")
            return
        try:
            # Retrieve and store all inputs into a dictionary
            gas_costing_data = {
                'BusID': bus_id_var.get(),
                'BusUnitType': bus_unit_type.get(),
                'BusClass': bus_class.get(),
                'GasCostPerKm': float(gas_cost_per_km.get()),
                'GasFund': float(gas_fund.get()),
                'ScheduleRoute': schedule_route.get()
            }
        
            # Insert the new dictionary as a document in the database
            db.collection('GasCosting').document(bus_id_var.get()).set(gas_costing_data)
        
            # Refresh the Treeview contents to include the new entry
            refresh_tree(db, tree)

            # Function to select the item based on matching BusID
            def select_item_by_bus_id(bus_id):
                for item in tree.get_children():
                    item_values = tree.item(item, "values")
                    if item_values[1] == bus_id:  # Assuming column 1 is BusID
                        tree.selection_set(item)
                        tree.see(item)  # Scroll to the selected item
                        break  # Exit after finding the match
        
            # Select the newly added item in the tree
            select_item_by_bus_id(gas_costing_data['BusID'])
        
            # Destroy the creation window
            create_window.destroy()
        
            # Show success notification
            messagebox.showinfo("Success", "Gas costing added successfully.")
    
        except Exception as e:
            # Handle exceptions and show error message
            messagebox.showerror("Error", f"An error occurred: {e}")

    # Save button
    ctk.CTkButton(create_window, text="Save", command=save_gas_costing, fg_color="#E2E2B6", text_color="#191970", hover_color="#6EACDA").grid(row=7, columnspan=2, pady=10)


#function to run when edit button is clicked
def edit_gas_costing(db, tree):
    selected_item = tree.selection() # fethc the selected data in treeview table 
    if selected_item:# check if theres a selected data in treeview 
        #select the item and turn ist col val to a list 
        item = tree.item(selected_item)
        values = item['values']

        #fetch the apecific document that matches the values from the lits "values" 
        gas_ref = db.collection('GasCosting').where('BusID', '==', values[1]).get()
        if gas_ref:# if matched 
            gas_data = gas_ref[0].to_dict()# convetr the doc into a dictionary

            # create a window form
            edit_window = ctk.CTkToplevel()
            edit_window.title("Edit Gas Costing")
            
            # Keep the window on top
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

            #label and entry object for user inputs
            ctk.CTkLabel(edit_window, text="Bus ID:", text_color="#E2E2B6").grid(row=0, column=0, padx=10, pady=5)
            bus_id = ctk.CTkEntry(edit_window , text_color="#191970")
            bus_id.grid(row=0, column=1, padx=10, pady=5)
            bus_id.insert(0,  gas_data['BusID']) # insert the vaue from the list "values"
            bus_id.configure(state="disabled")

            ctk.CTkLabel(edit_window, text="Bus Unit Type:", text_color="#E2E2B6").grid(row=1, column=0, padx=10, pady=5)
            bus_unit_type = ctk.CTkEntry(edit_window , text_color="#191970")
            bus_unit_type.grid(row=1, column=1, padx=10, pady=5)
            bus_unit_type.insert(0, gas_data['BusUnitType']) # insert the vaue from the list "values"
            bus_unit_type.configure(state="disabled")

            ctk.CTkLabel(edit_window, text="Bus Class:", text_color="#E2E2B6").grid(row=2, column=0, padx=10, pady=5)
            bus_class = ctk.CTkEntry(edit_window , text_color="#191970")
            bus_class.grid(row=2, column=1, padx=10, pady=5)
            bus_class.insert(0, values[3]) # insert the vaue from the list "values"
            bus_class.configure(state="disabled")

            ctk.CTkLabel(edit_window, text="Gas Cost (per km):", text_color="#E2E2B6").grid(row=3, column=0, padx=10, pady=5)
            gas_cost_per_km = ctk.CTkEntry(edit_window , text_color="#191970")
            gas_cost_per_km.grid(row=3, column=1, padx=10, pady=5)
            gas_cost_per_km.insert(0,  gas_data['GasCostPerKm']) # insert the vaue from the list "values"
            gas_cost_per_km.configure(state="disabled")

            ctk.CTkLabel(edit_window, text="Gas Fund:", text_color="#E2E2B6").grid(row=4, column=0, padx=10, pady=5)
            gas_fund = ctk.CTkEntry(edit_window, text_color="#191970", validate="key", validatecommand=vcmd)
            gas_fund.grid(row=4, column=1, padx=10, pady=5)
            gas_fund.insert(0,  gas_data['GasFund']) # insert the vaue from the list "values"

            ctk.CTkLabel(edit_window, text="Schedule Route:", text_color="#E2E2B6").grid(row=5, column=0, padx=10, pady=5)
            schedule_route = ctk.CTkEntry(edit_window, text_color="#191970" )
            schedule_route.grid(row=5, column=1, padx=10, pady=5)
            schedule_route.insert(0,  gas_data['ScheduleRoute']) # insert the vaue from the list "values"
            schedule_route.configure(state="disabled")

            # funtion to run when save button is clicked 
            def save_edit():
                if gas_fund.get() =="":
                    messagebox.showinfo("Success", "Please Enter A value for Gas fund.")# show succes notif 
                    return
                #store the edited inputs to a new dictionary
                updated_data = {
                    'BusID': bus_id.get(),
                    'BusUnitType': bus_unit_type.get(),
                    'BusClass': bus_class.get(),
                    'GasCostPerKm': float(gas_cost_per_km.get()),
                    'GasFund': float(gas_fund.get()),
                    'ScheduleRoute': schedule_route.get()
                }
                #update the document that matches the doc id with vales stored in the created dict.
                db.collection('GasCosting').document(gas_ref[0].id).update(updated_data)
                 # Refresh the Treeview contents to include the new entry
                refresh_tree(db, tree)

                # Function to select the item based on matching BusID
                def select_item_by_bus_id(bus_id):
                    for item in tree.get_children():
                        item_values = tree.item(item, "values")
                        if item_values[1] == bus_id:  # Assuming column 1 is BusID
                            tree.selection_set(item)
                            tree.see(item)  # Scroll to the selected item
                            break  # Exit after finding the match
        
                # Select the newly added item in the tree
                select_item_by_bus_id(gas_data['BusID'])
                edit_window.destroy()# destroy the window
                messagebox.showinfo("Success", "Gas costing updated successfully.")# show succes notif 

            # save button
            ctk.CTkButton(edit_window, text="Save", command=save_edit, text_color="#191970", fg_color="#E2E2B6", hover_color="#6EACDA" ).grid(row=6, columnspan=2, pady=(20,15))
        else: #if no document matched or no value is selcted 
            messagebox.showerror("Error", " No match Gas costing.")# show error notif
    else: #if no value is selcted
        messagebox.showerror("Error", " No Gas costing is Selected.")# show error notif

#function to run when delete button is clicked
def delete_gas_costing(db, tree):
    selected_item = tree.selection()# get the selected row in the treeview table 
    if selected_item:# check if theres a selected row in treeview
        #fetch it and store its col values to a list
        item = tree.item(selected_item)
        values = item['values']

         # Confirm before deleting
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this driver?")
        if confirm: # if yes
            #get the document from the collection that matches all the values from the list
            gas_ref = db.collection('GasCosting').where('BusID', '==', values[1]).where('BusUnitType', '==', values[2]).where('BusClass', '==', values[3]).get()

            if gas_ref:# check if the document exsist
                db.collection('GasCosting').document(gas_ref[0].id).delete()# delet the document
                refresh_tree(db,tree)# refresh the treeview table 
                
                messagebox.showinfo("Success", "Gas costing deleted successfully.") # show success message
            else:# if no doc match
                messagebox.showerror("Error", "No such Document exists in the database!") # show error message
        else: # if no
            return
    else: # if no value is selected in treeview
        messagebox.showerror("Error", "No Gas costing is selected.") # show error message


def refresh_tree(db,tree):
    global count, global_route_var, global_unit_type_var, global_bus_class_var, global_search_var
    count =1
    # Fetch gas costing data and filter based on search term and selected route
    gas_costing = db.collection('GasCosting').get()# fetch all the documents in collection GasCosting
    #delete items in treview
    for item in tree.get_children():
        tree.delete(item)

    for gas in gas_costing:
        data = gas.to_dict()
        bus_id = data['BusID'].lower()
        schedule_route = data['ScheduleRoute']
        unit_type = data['BusUnitType']
        bus_class = data['BusClass']

        # Apply filters
        if ((global_route_var == "All" or global_route_var == schedule_route) and
            (global_unit_type_var == "All" or global_unit_type_var == unit_type) and
            (global_bus_class_var == "All" or global_bus_class_var == bus_class) and
            (global_search_var in bus_id)):
            row_tag = "oddrow" if count % 2 == 0 else "evenrow"
            tree.insert("", ctk.END, values=(count,
                data['BusID'], 
                data['BusUnitType'], 
                data['BusClass'], 
                f"₱. {data['GasCostPerKm']}",
                f"₱. {data['GasFund']}", 
                data['ScheduleRoute']), tags=(row_tag,))
            count += 1

