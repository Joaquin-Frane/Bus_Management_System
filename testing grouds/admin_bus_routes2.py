#imports for the GUi (custom tkinter), treeview table(ttk), and database connection
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from firebase_config import db

from forHover import set_hover_color

count = 1

heavyrow = "#ADBBDA"
lightrow = "#EDE8F5"
vio = "#191970"
white = "white"
purplr ="#9747FF"
red ="#FF3737"
lightblue ="#4682B4"

# Define global variables for filter options
global_boarding_var = None
global_dropping_var = None
global_status_var = None

def manage_bus_routes(action, main_content_frame):
    global global_boarding_var, global_dropping_var, global_status_var

    for widget in main_content_frame.winfo_children():
        widget.destroy()

    # Fetch unique boarding and dropping points from the database
    boarding_points = ['All']
    dropping_points = ['All']
    route_docs = db.collection('BusRoutes').stream()

    for route in route_docs:
        data = route.to_dict()
        if data.get('boarding_point') not in boarding_points:
            boarding_points.append(data.get('boarding_point'))
        if data.get('dropping_point') not in dropping_points:
            dropping_points.append(data.get('dropping_point'))

    # Initialize global dropdown variables
    global_boarding_var = ctk.StringVar(value="All")
    global_dropping_var = ctk.StringVar(value="All")
    global_status_var = ctk.StringVar(value="All")  # New variable for Status filter
    
    # Top bar
    c_frame = ctk.CTkFrame(main_content_frame, corner_radius=0, fg_color="#03346E")
    c_frame.pack(fill="x")
    button_frame = ctk.CTkFrame(c_frame, corner_radius=0, fg_color="#03346E")
    button_frame.pack(fill="x")
    title_label = ctk.CTkLabel(button_frame, text=" BUS ROUTE ", text_color=white, font=("Arial", 23, "bold"))
    title_label.pack(side="left", pady=(10, 10), padx=20)
    create_button = ctk.CTkButton(button_frame, text="Create", command=lambda: create_bus_route(db, tree), fg_color=white, text_color=vio, font=("Arial", 16, "bold"), height=35)
    create_button.pack(side="left", padx=5)

    set_hover_color(create_button, hover_bg_color=purplr, hover_text_color=white, normal_bg_color=white, normal_text_color=vio)

    # Filter frame
    filter_frame = ctk.CTkFrame(c_frame, corner_radius=0, fg_color="#03346E")
    filter_frame.pack(fill="x")
    filter_frame.columnconfigure(tuple(range(7)), weight=1)

    ctk.CTkLabel(filter_frame, text="Boarding Point:", text_color=white).grid(row=0, column=0, padx=(25, 0), pady=(5, 0), sticky="nw")
    boarding_dropdown = ctk.CTkComboBox(filter_frame, variable=global_boarding_var, values=boarding_points, command=lambda _: refresh_tree(db, tree))
    boarding_dropdown.grid(row=1, column=0, padx=(20, 0), pady=(0, 10), sticky="nw")

    ctk.CTkLabel(filter_frame, text="Dropping Point:", text_color=white).grid(row=0, column=1, padx=10, pady=(5, 0), sticky="nw")
    dropping_dropdown = ctk.CTkComboBox(filter_frame, variable=global_dropping_var, values=dropping_points, command=lambda _: refresh_tree(db, tree))
    dropping_dropdown.grid(row=1, column=1, padx=5, pady=(0, 10), sticky="nw")

    # Add Status filter
    ctk.CTkLabel(filter_frame, text="Status:", text_color=white).grid(row=0, column=2, padx=10, pady=(5, 0), sticky="nw")
    status_dropdown = ctk.CTkComboBox(filter_frame, variable=global_status_var, values=["All", "Active", "Inactive"], command=lambda _: refresh_tree(db, tree))
    status_dropdown.grid(row=1, column=2, padx=5, pady=(0, 10), sticky="nw")

    # Buttons for Edit and Delete
    delete = ctk.CTkButton(filter_frame, text="Delete", command=lambda: delete_bus_route(db, tree), fg_color=white, text_color=red, height=35, font=("Arial", 16, "bold"))
    delete.grid(row=0, column=7, padx=(10, 20), pady=(25, 10), rowspan=2, sticky="e")
    edit = ctk.CTkButton(filter_frame, text="Edit", command=lambda: edit_bus_route(db, tree), fg_color=white, text_color=vio, height=35, font=("Arial", 16, "bold"))
    edit.grid(row=0, column=6, padx=5, pady=(25, 10), rowspan=2, sticky="e")

    set_hover_color(delete, hover_bg_color=red, hover_text_color=white, normal_bg_color=white, normal_text_color=red)
    set_hover_color(edit, hover_bg_color=lightblue, hover_text_color=white, normal_bg_color=white, normal_text_color=vio)

    # Code for the treeview TAble 
    columns = ("No.","Route", "Boarding Point", "Dropping Point", "Distance", "Approx. Time", "Status") #values for col. names
    tree_frame = ctk.CTkFrame(main_content_frame)
    tree_frame.pack(fill="both", expand=True)

    #scroll bar
    tree_scroll = tk.Scrollbar(tree_frame)
    tree_scroll.pack(side="right",fill="y")# position of scrollbar
    tree = ttk.Treeview(tree_frame, columns=columns, yscrollcommand=tree_scroll.set, show='headings') # set column as headers, bind scrollbar to the treeview table 
    # set alternating color for individual rows 
    tree.tag_configure('oddrow', background=heavyrow)
    tree.tag_configure('evenrow', background=lightrow)
    tree.tag_configure('cancel', background="#cc3e40", foreground="#fff")

    #Show data for the treeview in a layout
    for col in columns:
        tree.heading(col, text=col)
        if col == 'No.':
            tree.column(col, width=20)
        elif col =='Approx. Time' or col == 'Distance':
            tree.column(col, width=120)
        elif col =='Status' :
            tree.column(col, width=100, anchor="center")
        else:
            tree.column(col, minwidth=0, width=200)
    tree.pack(fill="both", expand=True)

    #configure scroll bar
    tree_scroll.config(command=tree.yview)
    #function to run when an item in treeview is doubled clicked
    def clicker(e):
        edit_bus_route(db,tree)

    tree.bind("<Double-1>", clicker)# event listener in treeview check if an item / row is douled clicked within 1 sec
    # Initial fetch and display bus routes
    refresh_tree(db, tree)

import customtkinter as ctk
from tkinter import messagebox

# Function when button "Create Route" is clicked with parameters db and tree for Treeview table update
def create_bus_route(db, tree):
    # Define color variables for background, input boxes, and button
    fg_Color= "#03346E"
    #bg_color = ""  # Light blue background
    #input_color = "#FFB6C1"  # Light pink input boxes
    #button_color = "#90EE90"  # Light green buttons

    # Create a new app window ensure it's on top of the existing window
    create_window = ctk.CTkToplevel()
    create_window.title("Create Bus Route")
    create_window.geometry("400x300")  # Set initial window size
    create_window.resizable(False, False)  # Disable window resizing
    create_window.configure(fg_color=fg_Color)  # Set background color
    create_window.columnconfigure(tuple(range(3)), weight=1)

    # Keep the window on top from the main window
    create_window.lift()
    create_window.attributes("-topmost", True)

    # Validation function to allow only integers
    def validate_integer(P):
        if P.isdigit() or P == "":
            return True
        return False

    time_vcmd = create_window.register(validate_integer)  # Register validation function

    def validate_numeric(P):
        if P == "":
            return True
        try:
            float(P)
            return True
        except ValueError:
            return False

    vcmd = (create_window.register(validate_numeric), '%P')

    # Add title label on top
    title_label = ctk.CTkLabel(create_window, text="Create New Bus Route", font=("Arial", 18), text_color="#fff")
    title_label.grid(row=0, columnspan=3, pady=10)

    # Code for entry objects and labels for input for new document creation
    ctk.CTkLabel(create_window, text="Boarding Point:", text_color="#E2E2B6").grid(row=1, column=0, padx=10, pady=5, sticky='e')
    boarding_point = ctk.CTkEntry(create_window, placeholder_text="Manila", width=160, fg_color="#fff", text_color="#191970")
    boarding_point.grid(row=1, column=1, columnspan=2, padx=10, pady=5)

    ctk.CTkLabel(create_window, text="Dropping Point:", text_color="#E2E2B6").grid(row=2, column=0, padx=10, pady=5, sticky='e')
    dropping_point = ctk.CTkEntry(create_window, placeholder_text="Manila", width=160, fg_color="#fff", text_color="#191970")
    dropping_point.grid(row=2, column=1, columnspan=2, padx=10, pady=5)

    ctk.CTkLabel(create_window, text="Distance (Km):", text_color="#E2E2B6").grid(row=3, column=0, padx=10, pady=5, sticky='e')
    distance = ctk.CTkEntry(create_window, validate="key", placeholder_text="100", validatecommand=vcmd, width=160, fg_color="#fff", text_color="#191970")
    distance.grid(row=3, column=1, columnspan=2, padx=10, pady=5)

    # Add separate entry fields for hours and minutes
    ctk.CTkLabel(create_window, text="Approx. Time (HH:MM):", text_color="#E2E2B6").grid(row=4, column=0, padx=10, pady=5, sticky='e')
    approx_hours = ctk.CTkEntry(create_window, placeholder_text="HH", validate="key", validatecommand=(time_vcmd, '%P'), width=70, fg_color="#fff", text_color="#191970")
    approx_hours.grid(row=4, column=1, padx=(10,5), pady=5, sticky="e")

    approx_minutes = ctk.CTkEntry(create_window, placeholder_text="MM", validate="key", validatecommand=(time_vcmd, '%P'), width=70, fg_color="#fff", text_color="#191970")
    approx_minutes.grid(row=4, column=2, padx=(5,10), pady=5, sticky="w")

    # Dropdown for status
    ctk.CTkLabel(create_window, text="Status (Active/Inactive):", text_color="#E2E2B6").grid(row=5, column=0, padx=10, pady=5, sticky='e')
    status_options = ["Active", "Inactive"]  # Predefined options
    status_var = ctk.StringVar(value="Active")  # Set initial value from schedule_data
    status_dropdown = ctk.CTkComboBox(create_window, values=status_options, variable=status_var, width=160, text_color="#191970")
    status_dropdown.grid(row=5, column=1,columnspan=2, padx=10, pady=5)

    # Function to save the input as a new document in collection once save button is clicked
    def save_route():
        # Retrieve values entered in boarding and dropping point
        boarding = boarding_point.get()
        dropping = dropping_point.get()
        # Connect the two values to be the document ID
        route_id_value = f"{boarding}-{dropping}"

        # Retrieve hours and minutes, and calculate total time in hours
        try:
            hours = int(approx_hours.get())
            minutes = int(approx_minutes.get())
            approx_time_value = hours + (minutes / 60)
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for hours and minutes.")
            return
        
        if not all([status_var.get, approx_time_value, distance.get(), dropping,  boarding]):
            messagebox.showerror("Error", "All fields are required.")
            return

        # Create a dictionary and pass the values
        route_data = {
            'boarding_point': boarding,
            'dropping_point': dropping,
            'distance': float(distance.get()),
            'approx_time': approx_time_value,
            'status': status_var.get()
        }

        # Check if the route already exists
        if db.collection('BusRoutes').document(route_id_value).get().exists:
            messagebox.showerror("Error", "Route already exists.")  # Shows a messagebox warning
            return
        else:
            # Save the dictionary as a new document in the collection with the custom doc. ID
            db.collection('BusRoutes').document(route_id_value).set(route_data)

            # Refresh the Treeview table
            refresh_tree(db, tree)

            # Function to select the item based on matching values
            def select_item_by_values(column_values):
                for item in tree.get_children():
                    item_values = tree.item(item, "values")
                    if item_values[1] == column_values:  # Check if the route_id_value matches
                        tree.selection_set(item)
                        tree.see(item)  # Scroll to the selected item
                        return
            # Call the function to select the newly added route
            select_item_by_values(route_id_value)

        create_window.destroy()  # Destroy the created window
        messagebox.showinfo("Success", "Bus route created successfully.")  # Display a confirmation messagebox

    # Initialize save button with custom color
    save_button = ctk.CTkButton(create_window, text="Save", command=save_route, fg_color="#6EACDA", text_color="#191970", hover_color="#E2E2B6")
    save_button.grid(row=6, columnspan=3, pady=10)



def edit_bus_route(db, tree):
    # Define color variables
    bg_color = "#E2E2B6"  # Light green for background
    input_color = "#fff"   #90caf9"  # Light blue for input boxes
    button_color = "#6EACDA"  # Red for button

    selected_item = tree.selection()  # Retrieves the currently selected item in the Treeview
    if selected_item:  # Checks if any item is selected then fetch data
        item = tree.item(selected_item)
        values = item['values']
        route_id = values[1]

        # Create a window form on top of main app window
        edit_window = ctk.CTkToplevel()
        edit_window.title("Edit Bus Route")
        edit_window.geometry("400x300")  # Set initial window size
        edit_window.resizable(False, False)  # Disable window resizing
        edit_window.configure(fg_color="#03346E")  # Set background color
        edit_window.columnconfigure(tuple(range(3)), weight=1)

        # Keep the window on top
        edit_window.lift()
        edit_window.attributes("-topmost", True)

        # Validation function to allow only integers
        def validate_integer(P):
            if P.isdigit() or P == "":
                return True
            return False

        time_vcmd = edit_window.register(validate_integer)  # Register validation function

        def validate_numeric(P):
            if P == "":
                return True
            try:
                float(P)
                return True
            except ValueError:
                return False

        vcmd = (edit_window.register(validate_numeric), '%P')

        # Add title label
        ctk.CTkLabel(edit_window, text="Edit Bus Route", font=("Arial", 16, "bold"), text_color=bg_color).grid(row=0, column=0, columnspan=3, pady=10)

        # Label and entry objects for needed inputs for editing document while fetching the selected list/row values to the entry objects
        ctk.CTkLabel(edit_window, text="Boarding Point:", text_color=bg_color).grid(row=1, column=0, padx=10, pady=5, sticky='e')
        boarding_point = ctk.CTkEntry(edit_window, width=160, fg_color=input_color,text_color="#191970")
        boarding_point.grid(row=1, column=1,columnspan=2, padx=10, pady=5)

        ctk.CTkLabel(edit_window, text="Dropping Point:", text_color=bg_color).grid(row=2, column=0, padx=10, pady=5, sticky='e')
        dropping_point = ctk.CTkEntry(edit_window, width=160, fg_color=input_color, text_color="#191970")
        dropping_point.grid(row=2, column=1,columnspan=2, padx=10, pady=5)

        ctk.CTkLabel(edit_window, text="Distance:", text_color=bg_color).grid(row=3, column=0, padx=10, pady=5, sticky='e')
        distance = ctk.CTkEntry(edit_window, width=160, fg_color=input_color, text_color="#191970", validate="key", validatecommand=vcmd)
        distance.grid(row=3, column=1,columnspan=2, padx=10, pady=5)

        # Add separate entry fields for hours and minutes (HH:MM format)
        ctk.CTkLabel(edit_window, text="Approx. Time (HH:MM):", text_color=bg_color).grid(row=4, column=0, padx=10, pady=5, sticky='e')
        approx_hours = ctk.CTkEntry(edit_window, placeholder_text="HH", validate="key", validatecommand=(time_vcmd, '%P'), width=70, fg_color=input_color, text_color="#191970")
        approx_hours.grid(row=4, column=1, padx=(10,5), pady=5, sticky="e")

        approx_minutes = ctk.CTkEntry(edit_window, placeholder_text="MM", validate="key", validatecommand=(time_vcmd, '%P'), width=70, fg_color=input_color, text_color="#191970")
        approx_minutes.grid(row=4, column=2, padx=(5,10), pady=5,  sticky="w")

        ctk.CTkLabel(edit_window, text="Status (Active/Inactive):", text_color=bg_color).grid(row=5, column=0, padx=10, pady=5, sticky='e')
        status_options = ["Active", "Inactive"]  # Predefined options
        status_var = ctk.StringVar(value=values[6]) 
        status_dropdown = ctk.CTkComboBox(edit_window, values=status_options, variable=status_var, width=160, text_color="#191970")
        status_dropdown.grid(row=5, column=1, columnspan=2, padx=10, pady=5)
        

        # Fetch and set existing route data (selected row)
        route_doc = db.collection('BusRoutes').document(route_id)  # Retrieve data based on the given doc ID
        route_data = route_doc.get().to_dict()  # Create a dictionary to hold the data from the selected doc ID

        if route_data:  # Checks if the route data exists for each entry obj/fields
            # Insert values to the entry objects
            boarding_point.insert(0, route_data.get('boarding_point', ''))
            dropping_point.insert(0, route_data.get('dropping_point', ''))
            boarding_point.configure(state='disabled')  # Disable boarding point editing
            dropping_point.configure(state='disabled')  # Disable dropping point editing
            distance.insert(0, route_data.get('distance', ''))
            
            # Fetching and setting hours and minutes from 'approx_time'
            approx_time = route_data.get('approx_time', 0)
            hours = int(approx_time)  # Extract hours as an integer
            minutes = int((approx_time - hours) * 60)  # Extract minutes as an integer
            
            approx_hours.insert(0, hours)  # Insert hours into the entry field
            approx_minutes.insert(0, minutes)  # Insert minutes into the entry field


        # Function to run when update button is clicked
        def update_route():
            # Retrieve values entered in boarding and dropping point
            num = values[0]

            # Fetch the data from the entry objects and store it in a dictionary
            try:
                hours = int(approx_hours.get())
                minutes = int(approx_minutes.get())
                approx_time_value = hours + (minutes / 60)
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers for hours and minutes.")
                return
            
            if not all([boarding_point.get(), dropping_point.get(), distance.get(), approx_time_value,  status_var.get()]):
                messagebox.showerror("Error", "All fields are required.")
                return

            updated_data = {
                'boarding_point': boarding_point.get(),
                'dropping_point': dropping_point.get(),
                'distance': float(distance.get()),
                'approx_time': approx_time_value,
                'status': status_var.get()
            }

            db.collection('BusRoutes').document(route_id).update(updated_data)  # Update the document with the new data
            # Refresh the Treeview table
            refresh_tree(db, tree)

            # Function to select the item based on matching values
            def select_item_by_values(column_values):
                for item in tree.get_children():
                    item_values = tree.item(item, "values")
                    if item_values[1] == column_values:  # Check if the route_id_value matches
                        tree.selection_set(item)
                        tree.see(item)  # Scroll to the selected item
                        return
                    
            # Call the function to select the newly added route
            select_item_by_values(route_id)

            edit_window.destroy()  # Destroy the created form
            messagebox.showinfo("Success", "Bus route updated successfully.")  # Provide a confirmation messagebox

        # Update button
        ctk.CTkButton(edit_window, text="Update", command=update_route, fg_color=button_color, text_color="#191970", hover_color="#E2E2B6").grid(row=6, columnspan=3, pady=10)
    else:  # If no value is selected
        messagebox.showerror("Error", "Please select a bus route to edit.")


#function if delete button is clicekd
def delete_bus_route(db, tree):
    selected_item = tree.selection() # fetch the selected vale in treeeview

    if selected_item:# check if there is a selected val in treeview
         # Confirm before deleting
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this driver?")
        if confirm:# if yes
            item = tree.item(selected_item)
            route_id = item['values'][1] #Retrieves the route ID
        
            db.collection('BusRoutes').document(route_id).delete()# delete the doc with a match doc ID
            refresh_tree(db,tree)# reffesth the treview
            messagebox.showinfo("Success", "Bus route deleted successfully.") # confirm the deletion is success
        else: # if no\
            return   
    else:
        messagebox.showerror("Error", "Please select a driver to delete.")


#function to refresh the values in the treview
def refresh_tree(db, tree):
    global global_boarding_var, global_dropping_var, global_status_var

    tree.delete(*tree.get_children())
    selected_boarding = global_boarding_var.get()
    selected_dropping = global_dropping_var.get()
    selected_status = global_status_var.get()

    routes = db.collection('BusRoutes').stream()
    count = 1
    for route in routes:
        data = route.to_dict()
        status = data.get('status', '').strip()  # Retrieve and strip whitespace from status

        # Apply filters
        if (selected_boarding == "All" or data.get('boarding_point') == selected_boarding) and (selected_dropping == "All" or data.get('dropping_point') == selected_dropping) and (selected_status == "All" or status == selected_status):
                
            row_tag = "cancel" if status == "Inactive" else "oddrow" if count % 2 == 0 else "evenrow"
            tree.insert("", "end", values=(count,
                route.id, 
                data.get('boarding_point', 'N/A'), 
                data.get('dropping_point', 'N/A'),
                f"{data.get('distance', 'N/A')}  KM", 
                data.get('approx_time', 'N/A'), 
                status), tags=(row_tag,))
            count += 1