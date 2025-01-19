#imports for GUI and database connections
import customtkinter as ctk # better gui
import tkinter as tk #for treview
from tkinter import ttk, messagebox #for meassega box
from firebase_config import db # database connection
from forHover import set_hover_color

heavyrow = "#ADBBDA"
lightrow = "#EDE8F5"
vio = "#191970"
white = "white"
purplr ="#9747FF"
red ="#FF3737"
lightblue ="#4682B4"
vin= "#03346E"

unit_type_var =''
assigned_route_var = ''
bus_class_var =''
search_var = ''
status_var = ''
#function to change the objects in main_content_frame for Bus management 
def manage_buses(action, main_content_frame):
    global unit_type_var, assigned_route_var, bus_class_var, search_var, status_var
    
    status_var = tk.StringVar(value="All")
    def toggle_status():
        current_status = status_var.get()
        if current_status == "All":
            status_var.set("Active")
        elif current_status == "Active":
            status_var.set("Inactive")
        else:
            status_var.set("All")
        update_table()

    # Destroy all the current obj in main_content_frame
    for widget in main_content_frame.winfo_children():
        widget.destroy()
        
    # Code for button frame for managing bus schedule (serve as title holder)
    c_frame = ctk.CTkFrame(main_content_frame, corner_radius=0, fg_color=vin)
    c_frame.pack(fill="x")
    
    # Code for button frame as top bar
    button_frame = ctk.CTkFrame(c_frame, corner_radius=0, fg_color=vin)
    button_frame.pack(fill="x")

    # Label
    title_label = ctk.CTkLabel(button_frame, text=" BUS UNITS ", text_color=white, font=("Arial", 23, "bold"), corner_radius=0)
    title_label.pack(side="left", pady=(10, 10), padx=(20,10))

    # Code for Create button for actions
    add= ctk.CTkButton(button_frame, text="Create", fg_color=white, text_color=vio, command=lambda: create_bus(db, tree), font=("Arial", 16, "bold"), height=35)
    add.pack(side="left", pady=5, padx=5)
    set_hover_color(add, hover_bg_color=purplr, hover_text_color=white, normal_bg_color=white, normal_text_color=vio)

    # Add Status Toggle Button
    status_button = ctk.CTkButton( button_frame, textvariable=status_var, command=toggle_status, fg_color=white, text_color=vio, font=("Arial", 16,"bold"), height=35)
    status_button.pack(side="right", padx=10)
    set_hover_color(status_button, hover_bg_color=purplr, hover_text_color=white, normal_bg_color=white, normal_text_color=vio )

    # Code for Filter frame to hold filter related obj.
    filter_frame = ctk.CTkFrame(c_frame, corner_radius=0, fg_color=vin)
    filter_frame.pack(fill="x")
    # Ensuring the 7th column is left empty for spacing
    filter_frame.grid_columnconfigure(6, weight=1)

    # Variable to hold values for Dropdowns of filters
    unit_type_var = tk.StringVar(value="All")
    assigned_route_var = tk.StringVar(value="All")
    bus_class_var = tk.StringVar(value="All")
    search_var = tk.StringVar()

    # Function to update the treeview table contents
    def update_table(*args):
        refresh_tree(db, tree)

    # Initialize dropdown values
    def initialize_dropdowns():
        unit_types = set()
        routes = set()
        buses = db.collection('Buses').stream()
        unit_type = db.collection('Unit_type').stream()
        unit_type_filter = [doc.id for doc in unit_type]

        for bus in buses:
            data = bus.to_dict()
            routes.add(data.get('assigned_route', ''))

        unit_type_values = ["All"] + sorted(unit_type_filter)
        assigned_route_values = ["All"] + sorted(routes)
        unit_type_dropdown.configure(values=unit_type_values)
        assigned_route_dropdown.configure(values=assigned_route_values)
        bus_class_dropdown.configure(values=["All", "AC", "NAC"])

    # Grid layout for filter frame
    ctk.CTkLabel(filter_frame, text=" Unit Type:", text_color=white).grid(row=0, column=0, padx=(25,10), pady=0, sticky="w")
    unit_type_dropdown = ctk.CTkComboBox(filter_frame, variable=unit_type_var, values=["All"], command=update_table)
    unit_type_dropdown.grid(row=1, column=0, padx=(20,10), pady=(0,10), sticky="w")

    ctk.CTkLabel(filter_frame, text="Assigned Route:", text_color=white).grid(row=0, column=1, padx=(15,0), pady=0, sticky="w")
    assigned_route_dropdown = ctk.CTkComboBox(filter_frame, variable=assigned_route_var, values=["All"], command=update_table)
    assigned_route_dropdown.grid(row=1, column=1, padx=10, pady=(0,10), sticky="w")

    ctk.CTkLabel(filter_frame, text="Bus Class:", text_color=white).grid(row=0, column=2, padx=15, pady=0, sticky="w")
    bus_class_dropdown = ctk.CTkComboBox(filter_frame, variable=bus_class_var, values=["All", "AC", "NAC"], command=update_table)
    bus_class_dropdown.grid(row=1, column=2, padx=10, pady=(0,10), sticky="w")

    # Search box for Bus ID
    ctk.CTkLabel(filter_frame, text="Search Bus ID:", text_color=white).grid(row=0, column=3, padx=15, pady=0, sticky="w")
    search_entry = ctk.CTkEntry(filter_frame, textvariable=search_var, placeholder_text="BUSS-0000", text_color="#191970", placeholder_text_color="#6EACDA", width=200)
    search_entry.grid(row=1, column=3, padx=10, pady=(0,10), sticky="w")
    
    # Search on pressing Enter
    search_entry.bind("<Return>", update_table)

    # Buttons for delete and edit
    delete = ctk.CTkButton(filter_frame, text="Delete", command=lambda: delete_bus(db, tree), fg_color=white, text_color=red, font=("Arial", 16, "bold"), height=35)
    delete.grid(row=0, column=7, rowspan=2, padx=(5,20 ), pady=(20,10), sticky='e')
    edit = ctk.CTkButton(filter_frame, text="Edit", command=lambda: edit_bus(db, tree), fg_color=white, text_color="#191970", font=("Arial", 16, "bold"), height=35)
    edit.grid(row=0, column=6, rowspan=2, padx=5, pady=(20,10), sticky="e")

    set_hover_color(delete, hover_bg_color=red, hover_text_color=white, normal_bg_color=white, normal_text_color=red)
    set_hover_color(edit, hover_bg_color=lightblue, hover_text_color=white, normal_bg_color=white, normal_text_color=vio)

    # Treeview table
    columns = ("No.", "Bus ID", "Class", "Fuel Cst.", "MNT Cst.", "Seat No.", "Unit Type", "Assigned Route", "Driver ID", "Status")
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
        if col =="Status" :
            tree.column(col, width=50, anchor="center")
        elif col == 'Seat No.':
            tree.column(col, width=37)
        elif col == 'Class':
            tree.column(col, width=40, anchor= "center")
        elif col == 'Unit Type':
            tree.column(col, width=70)
        elif col == 'No.':
            tree.column(col, width=30)
        elif col == "MNT Cst." or col == 'Fuel Cst.':
            tree.column(col, width=80)
        elif col == 'Bus ID' :
            tree.column(col, width=80)
        else:
            tree.column(col, minwidth=0, width=130)
    tree.pack(fill=ctk.BOTH, expand=True)

    tree_scroll.config(command=tree.yview)

    # Bind double-click event for editing
    tree.bind("<Double-1>", lambda e: edit_bus(db, tree))

    # Initialize dropdowns and load initial data
    initialize_dropdowns()
    update_table()



# Function for Create button
def create_bus(db, tree):
    # Create a frame for creating a new bus
    add_window = ctk.CTkToplevel()
    add_window.title("Add Bus")# Keep the window on top
    add_window.lift()
    add_window.attributes("-topmost", True)
    add_window.configure(fg_color="#03346E")
    # Create frame to hold the form contents
    create_bus_frame = ctk.CTkFrame(add_window, fg_color="#03346E")
    create_bus_frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)

    # Function to update seats based on selected unit type
    def update_seats(*args):
        current_value = selected_unit.get()
        print(f"Selected Unit Type: {selected_unit}")
        if current_value and current_value != "Select Unit Type":
            try:
                unit_doc = db.collection('Unit_type').document(current_value).get()
                print(unit_doc.to_dict())
                if unit_doc.exists:
                    no_of_seat = unit_doc.to_dict().get('no_of_seat', '')
                    print("No 'no_of_seat' field found.")
                    seats.configure(state='normal')
                    seats.delete(0, ctk.END)
                    seats.insert(0, str(no_of_seat))
                    seats.configure(state='readonly')
                else:
                    seats.configure(state='normal')
                    seats.delete(0, ctk.END)
                    seats.configure(state='readonly')
            except Exception as e:
                messagebox.showerror("Error", f"Failed to fetch number of seats: {e}")
        else:
            seats.configure(state='normal')
            seats.delete(0, ctk.END)
            seats.configure(state='readonly')
    
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
    # --- Unit Type ---
    ctk.CTkLabel(create_bus_frame, text="Unit Type:", text_color="#E2E2B6").grid(row=0, column=0, padx=10, pady=5, sticky='e')
    selected_unit = ctk.StringVar(value="Select Unit Type")
    unit_type = ctk.CTkComboBox(create_bus_frame, variable=selected_unit, command=update_seats)  # Remove the parentheses
    unit_type.grid(row=0, column=1, padx=10, pady=5, sticky='w')
    
    # Fetch Unit Types from the database
    try:
        unit_types = db.collection('Unit_type').get()
        unit_type_names = [ut.id for ut in unit_types]
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch Unit Types: {e}")
        unit_type_names = []
    unit_type.configure(values=unit_type_names)  # Set a default prompt
    
    # --- Number of Seats ---
    ctk.CTkLabel(create_bus_frame, text="Number of Seats:", text_color="#E2E2B6").grid(row=1, column=0, padx=10, pady=5, sticky='e')
    seats = ctk.CTkEntry(create_bus_frame, text_color="#191970")
    seats.grid(row=1, column=1, padx=10, pady=5, sticky='w')
    seats.configure(state='readonly')  # Make seats read-only since it's auto-filled
    # --- Bus Class ---
    ctk.CTkLabel(create_bus_frame, text="Bus Class:", text_color="#E2E2B6").grid(row=2, column=0, padx=10, pady=5, sticky='e')
    bus_class = ctk.CTkComboBox(create_bus_frame, values=["AC", "NAC"])
    bus_class.grid(row=2, column=1, padx=10, pady=5, sticky='w')
    bus_class.set("Select Bus Class")  # Set a default prompt
    # --- Fuel Cost ---
    ctk.CTkLabel(create_bus_frame, text="Fuel Cost per Km:", text_color="#E2E2B6").grid(row=3, column=0, padx=10, pady=5, sticky='e')
    fuel_cost = ctk.CTkEntry(create_bus_frame, validate="key", validatecommand=vcmd, text_color="#191970")
    fuel_cost.grid(row=3, column=1, padx=10, pady=5, sticky='w')
    # --- Maintenance Cost ---
    ctk.CTkLabel(create_bus_frame, text="Maintenance Cost:", text_color="#E2E2B6").grid(row=4, column=0, padx=10, pady=5, sticky='e')
    maintenance_cost = ctk.CTkEntry(create_bus_frame, validate="key", validatecommand=vcmd, text_color="#191970")
    maintenance_cost.grid(row=4, column=1, padx=10, pady=5, sticky='w')
    # --- Assigned Route ---
    ctk.CTkLabel(create_bus_frame, text="Assigned Route:", text_color="#E2E2B6").grid(row=5, column=0, padx=10, pady=5, sticky='e')
    assigned_route = ctk.CTkComboBox(create_bus_frame)
    assigned_route.grid(row=5, column=1, padx=10, pady=5, sticky='w')
    
    # Fetch bus routes document names/IDs
    try:
        routes = db.collection('BusRoutes').get()  # Fetch all docs in collection
        route_names = [route.id for route in routes]  # Create a list to store doc names
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch Bus Routes: {e}")
        route_names = []
    assigned_route.configure(values=route_names)
    assigned_route.set("Select Route")  # Set a default prompt
    
    # --- Driver ---
    ctk.CTkLabel(create_bus_frame, text="Driver:", text_color="#E2E2B6").grid(row=6, column=0, padx=10, pady=5, sticky='e')
    driver = ctk.CTkComboBox(create_bus_frame)
    driver.grid(row=6, column=1, padx=10, pady=5, sticky='w')
    
    # Fetch and filter drivers
    try:
        drivers = db.collection('Drivers').get()  # Fetch all docs in collection
        # Create a set of driver IDs that are already assigned to buses
        used_driver_ids = {bus.to_dict().get('driver_id') for bus in db.collection('Buses').get() if bus.to_dict().get('driver_id')}
        
        driver_names = []
        driver_map = {}
        for driver_doc in drivers:
            driver_id = driver_doc.id
            if driver_id not in used_driver_ids:
                last_name = driver_doc.get('last_name')
                first_name = driver_doc.get('first_name')
                name = f"{last_name} {first_name}"
                driver_names.append(name)
                driver_map[name] = driver_id
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch Drivers: {e}")
        driver_names = []
        driver_map = {}
    
    driver.configure(values=driver_names)
    driver.set("Select Driver")  # Set a default prompt
    
    # --- Save Function ---
    def save_bus():
        # Fetch the selected value from the dropdown
        selected_driver_name = driver.get()
        driver_id = driver_map.get(selected_driver_name)
        
        # Validation checks
        if unit_type.get() == "Select Unit Type" or not unit_type.get():
            messagebox.showerror("Error", "Please select a Unit Type.")
            return
        if bus_class.get() == "Select Bus Class" or not bus_class.get():
            messagebox.showerror("Error", "Please select a Bus Class.")
            return
        if not maintenance_cost.get():
            messagebox.showerror("Error", "Please enter Maintenance Cost.")
            return
        if not fuel_cost.get():
            messagebox.showerror("Error", "Please enter Fuel Cost per Km.")
            return
        if assigned_route.get() == "Select Route" or not assigned_route.get():
            messagebox.showerror("Error", "Please select an Assigned Route.")
            return
        if selected_driver_name == "Select Driver" or not selected_driver_name:
            messagebox.showerror("Error", "Please select a Driver.")
            return
        
        try:
            fuel_cost_value = float(fuel_cost.get())
            maintenance_cost_value = float(maintenance_cost.get())
        except ValueError:
            messagebox.showerror("Error", "Fuel Cost and Maintenance Cost must be numerical values.")
            return
        


        # Generate the bus ID
        try:
            # Access a shared counter document in Firestore
            counter_doc = db.collection('Countsettings').document('bus_counter')
            counter_data = counter_doc.get().to_dict()
            bus_count = counter_data.get('next_bus_id', 1)

            while True:
                # Generate the bus ID
                bus_id = f"BUSS-{bus_count:04d}"

                # Check if this ID is already in use
                existing_bus = db.collection('Buses').document(bus_id).get()


                if not existing_bus.exists:
                    # If no document found, use this ID
                    print(f"Unique Bus ID generated: {bus_id}")
                    # Update the counter in Firestore
                    counter_doc.update({'next_bus_id': bus_count + 1})
                    break
                else:
                    # Increment and check again if there’s a conflict
                    bus_count += 1
                    print(f"{bus_id}: occupied , skipping...")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate Bus ID: {e}")
        
        # Retrieve all necessary data from the widgets
        bus_class_value = bus_class.get()
        seats_value = seats.get()
        unit_type_value = unit_type.get()
        assigned_route_value = assigned_route.get()
        
        # Store input and selected inputs into a dictionary
        bus_data = {
            'bus_class': bus_class_value,
            'fuel_cost_per_km': fuel_cost_value,
            'maintenance_cost': maintenance_cost_value,
            'number_of_seats': int(seats_value) if seats_value.isdigit() else seats_value,
            'unit_type': unit_type_value,
            'assigned_route': assigned_route_value,
            'driver': selected_driver_name,
            'driver_id': driver_id,
            'status': "Active"
        }
        
        # Save the new bus data to the database with the generated bus_id
        try:
            db.collection('Buses').document(bus_id).set(bus_data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save Bus data: {e}")
            return
        
        # Function to select the item based on matching values
        def select_item_by_values(column_values):
            for item in tree.get_children():
                item_values = tree.item(item, "values")
                if len(item_values) > 1 and item_values[1] == column_values:  # Check if the bus_id matches
                    tree.selection_set(item)
                    tree.see(item)  # Scroll to the selected item
                    return
    
        # Refresh the Treeview contents
        try:
            refresh_tree(db, tree)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh the Treeview: {e}")
        
        # Select the newly added bus in the Treeview
        select_item_by_values(bus_id)
        # Destroy the add window
        add_window.destroy()
        # Show success message
        messagebox.showinfo("Success", "Bus created successfully.")
    # --- Save Button --
    ctk.CTkButton(create_bus_frame, text="Save", command=save_bus, text_color="#191970", fg_color="#E2E2B6", hover_color="#6EACDA").grid(row=7, column=0, columnspan=2, pady=20)



# Function for Edit button
def edit_bus(db, tree):
    # Get the selected row/clicked row in the treeview table
    selected_item = tree.selection()

    if selected_item:  # Check if a row is selected
        item = tree.item(selected_item)
        values = item['values']
        bus_id = values[1]
        bus_doc = db.collection("Buses").document(bus_id).get()
        if not bus_doc.exists:
            messagebox.showerror("Error", "Selected schedule document not found.")
            return
        bus_data = bus_doc.to_dict()
        
        # Create a new app window
        edit_window = ctk.CTkToplevel()
        edit_window.title("Edit Bus")
        # Keep the window on top
        edit_window.attributes("-topmost", True)
        edit_window.configure(fg_color="#03346E")
        # Code for edit bus frame for GUI
        edit_bus_frame = ctk.CTkFrame(edit_window, fg_color="#03346E")
        edit_bus_frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)

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
        # --- Unit Type ---
        unit_type_var = ctk.StringVar(value=bus_data.get('unit_type', ''))
        ctk.CTkLabel(edit_bus_frame, text="Unit Type:", text_color="#E2E2B6").grid(row=0, column=0, padx=10, pady=5, sticky='e')
        unit_type = ctk.CTkEntry(edit_bus_frame, textvariable=unit_type_var, text_color="#191970")
        unit_type.grid(row=0, column=1, padx=10, pady=5, sticky='w')
        unit_type.configure(state='disabled')

        # --- Number of Seats ---
        seats_var = ctk.StringVar(value=bus_data.get('number_of_seats', ''))
        ctk.CTkLabel(edit_bus_frame, text="Number of Seats:", text_color="#E2E2B6").grid(row=1, column=0, padx=10, pady=5, sticky='e')
        seats = ctk.CTkEntry(edit_bus_frame, textvariable=seats_var, text_color="#191970")
        seats.grid(row=1, column=1, padx=10, pady=5, sticky='w')
        seats.configure(state='readonly')

        # --- Bus Class ---
        bus_class_var = ctk.StringVar(value=bus_data.get('bus_class', ''))
        ctk.CTkLabel(edit_bus_frame, text="Bus Class:", text_color="#E2E2B6").grid(row=2, column=0, padx=10, pady=5, sticky='e')
        bus_class = ctk.CTkEntry(edit_bus_frame, textvariable=bus_class_var, text_color="#191970")
        bus_class.grid(row=2, column=1, padx=10, pady=5, sticky='w')
        bus_class.configure(state='readonly')

        # --- Fuel Cost per Km ---
        fuel_cost_var = ctk.StringVar(value=str(bus_data.get('fuel_cost_per_km', '0.0')))
        ctk.CTkLabel(edit_bus_frame, text="Fuel Cost per Km:", text_color="#E2E2B6").grid(row=3, column=0, padx=10, pady=5, sticky='e')
        fuel_cost = ctk.CTkEntry(edit_bus_frame, textvariable=fuel_cost_var, validate="key", validatecommand=vcmd, text_color="#191970")
        fuel_cost.grid(row=3, column=1, padx=10, pady=5, sticky='w')

        # --- Maintenance Cost ---
        maintenance_cost_var = ctk.StringVar(value=str(bus_data.get('maintenance_cost', '0.0')))
        ctk.CTkLabel(edit_bus_frame, text="Maintenance Cost:", text_color="#E2E2B6").grid(row=4, column=0, padx=10, pady=5, sticky='e')
        maintenance_cost = ctk.CTkEntry(edit_bus_frame, textvariable=maintenance_cost_var, validate="key", validatecommand=vcmd, text_color="#191970")
        maintenance_cost.grid(row=4, column=1, padx=10, pady=5, sticky='w')

        # --- Assigned Route ---
        route_var = ctk.StringVar(value=str(bus_data.get('assigned_route', 'Select Route')))
        ctk.CTkLabel(edit_bus_frame, text="Assigned Route:", text_color="#E2E2B6").grid(row=5, column=0, padx=10, pady=5, sticky='e')
        assigned_route = ctk.CTkComboBox(edit_bus_frame, variable=route_var)
        assigned_route.grid(row=5, column=1, padx=10, pady=5, sticky='w')
        
        # Fetch bus route document names
        try:
            routes = db.collection('BusRoutes').get()
            route_names = [route.id for route in routes]
            route_names.append("Vacant")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch Bus Routes: {e}")
            route_names = ['Vacant']
        assigned_route.configure(values=route_names)

        # --- Driver ID ---
        ctk.CTkLabel(edit_bus_frame, text="Driver ID:", text_color="#E2E2B6").grid(row=6, column=0, padx=10, pady=5, sticky='e')
        driver_id_var = ctk.StringVar(value=bus_data.get('driver_id','Select Driver'))
        driver = ctk.CTkComboBox(edit_bus_frame, variable=driver_id_var)
        driver.grid(row=6, column=1, padx=10, pady=5, sticky='w')

        # --- Status ---
        ctk.CTkLabel(edit_bus_frame, text="Status:", text_color="#E2E2B6").grid(row=7, column=0, padx=10, pady=5, sticky='e')
        status = ctk.StringVar(value=bus_data.get('status',"Not Available"))
        status_dropdown = ctk.CTkComboBox(edit_bus_frame, variable= status, values=["Active", "Inactive"])
        status_dropdown.grid(row=7, column=1, padx=10, pady=5, sticky='w')

        try:
            drivers = db.collection('Drivers').get()
            # Create a set of driver IDs that are already assigned to buses, except the current bus
            used_driver_ids = {
                bus.to_dict().get('driver_id') for bus in db.collection('Buses').get()
                if bus.to_dict().get('driver_id') and bus.id != bus_id
            }
            driver_map = {}

            for driver_doc in drivers:
                driver_id = driver_doc.id
                if driver_id not in used_driver_ids:
                    # Using to_dict() to get fields
                    driver_data = driver_doc.to_dict()
                    last_name = driver_data.get('last_name', '')
                    first_name = driver_data.get('first_name', '')
                    name = f"{last_name} {first_name}".strip()
                    if name:
                        driver_map[driver_id] = name
            # Add the unique "Vacant" option to the driver_map
            driver_map["Vacant"] = "N/A"
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch Drivers: {e}")
            driver_map = {}
        driver.configure(values=driver_map)
        
        # --- Save Function ---
        def save_bus():
            selected_driver_id = driver.get()
            driver_id = driver_map.get(selected_driver_id)
            # Validation checks
            if unit_type.get() == "Select Unit Type" or not unit_type.get():
                messagebox.showerror("Error", "Please select a Unit Type.")
                return
            if bus_class.get() == "Select Bus Class" or not bus_class.get():
                messagebox.showerror("Error", "Please select a Bus Class.")
                return
            if not fuel_cost.get():
                messagebox.showerror("Error", "Please enter Fuel Cost per Km.")
                return
            if not maintenance_cost.get():
                messagebox.showerror("Error", "Please enter Maintenance Cost.")
                return
            if assigned_route.get() == "Select Route" or not assigned_route.get():
                messagebox.showerror("Error", "Please select an Assigned Route.")
                return
            if selected_driver_id == "Select Driver" or not selected_driver_id:
                messagebox.showerror("Error", "Please select a Driver.")
                return

            # Validate numeric inputs
            try:
                fuel_cost_value = float(fuel_cost.get())
                maintenance_cost_value = float(maintenance_cost.get())
            except ValueError:
                messagebox.showerror("Error", "Fuel Cost and Maintenance Cost must be numerical values.")
                return

            # Retrieve all necessary data from the widgets
            unit_type_value = unit_type.get()
            seats_value = seats.get()
            bus_class_value = bus_class.get()
            assigned_route_value = assigned_route.get()
            status_value = status_dropdown.get()

            # Store input and selected inputs into a dictionary
            updated_data = {
                'bus_class': bus_class_value,
                'fuel_cost_per_km': fuel_cost_value,
                'maintenance_cost': maintenance_cost_value,
                'number_of_seats': int(seats_value) if seats_value.isdigit() else seats_value,
                'unit_type': unit_type_value,
                'assigned_route': assigned_route_value,
                'driver': driver_id,
                'driver_id': selected_driver_id, 
                'status': status_value
            }

            # Save the updated bus data to the database
            try:
                db.collection('Buses').document(bus_id).update(updated_data)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update Bus data: {e}")
                return

            # Update the Treeview table with new values
            # Function to select the item based on matching values
            def select_item_by_values(column_values):
                for item in tree.get_children():
                    item_values = tree.item(item, "values")
                    if len(item_values) > 1 and item_values[1] == column_values:  # Check if the bus_id matches
                        tree.selection_set(item)
                        tree.see(item)  # Scroll to the selected item
                        return
    
            # Refresh the Treeview contents
            try:
                refresh_tree(db, tree)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to refresh the Treeview: {e}")
        
            # Select the newly added bus in the Treeview
            select_item_by_values(bus_id)

            # Destroy the edit window
            edit_window.destroy()
            messagebox.showinfo("Success", "Bus updated successfully.")
    else:  # If no row is selected in treeview
        messagebox.showerror("Error", "Please select a row to edit.")
    # --- Save Button ---
    ctk.CTkButton(edit_bus_frame, text="Save", text_color="#191970",fg_color="#E2E2B6", hover_color="#6EACDA", command=save_bus).grid(row=8, column=0, columnspan=2, pady=20)



#function to when deleted button is cliked 
def delete_bus(db, tree):
    global count
    count=1
    selected_item = tree.selection() # get the selected row in treview

    if not selected_item: # to show smsbox if none selctd
        messagebox.showwarning("Warning", "Please select a cashier to delete.")
        return
    
    if selected_item:# check if thres a selected value in treeview
        item = tree.item(selected_item)
        bus_id = item['values'][1]
        # Confirm deletion
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete Bus ID {bus_id}?"):# show a warning before deleting the data
            db.collection('Buses').document(bus_id).delete()
            messagebox.showinfo("Success", "Bus deleted successfully.")# message box notif for success
            refresh_tree(db, tree)

    else: # if no row is selected in trevie
        messagebox.showwarning("Warning", "Please select a cashier to delete.")


def refresh_tree(db, tree):
    global unit_type_var, assigned_route_var, bus_class_var, search_var, status_var
    count = 1  # Set counter to 1
    buses = db.collection('Buses').stream()
    # Delete items in treeview
    for item in tree.get_children():
        tree.delete(item)

    unit_type_filter = unit_type_var.get()
    assigned_route_filter = assigned_route_var.get()
    bus_class_filter = bus_class_var.get()
    search_filter = search_var.get().strip().upper()  # Strip whitespace and standardize to uppercase
    status_filter = status_var.get()

    for bus in buses:
        data = bus.to_dict()
        bus_id = bus.id
        driver_id = data.get('driver_id', '')  # Ensure both are uppercase
        # Apply filters
        if ((unit_type_filter == "All" or data.get('unit_type', '') == unit_type_filter) and
            (assigned_route_filter == "All" or data.get('assigned_route', '') == assigned_route_filter) and
            (bus_class_filter == "All" or data.get('bus_class', '') == bus_class_filter) and
            (search_filter in bus_id or search_filter in driver_id ) and
            (status_filter == data.get('status', '') or status_filter == 'All')):

            driver = data.get('driver_id', 'Vacant')
            row_tag = "Inactive" if data.get('status') == "Inactive" else "oddrow" if count % 2 == 0 else "evenrow"
            tree.insert("", ctk.END, values=(
                count, 
                bus.id, 
                data['bus_class'], 
                f"₱. {data['fuel_cost_per_km']}",  # Add peso sign
                f"₱. {data['maintenance_cost']}",  # Add peso sign
                data['number_of_seats'], 
                data['unit_type'], 
                data.get('assigned_route', 'Vacant'), 
                driver, data['status']
            ), tags=(row_tag,))
            count += 1