# imports for GUi and database connection
import customtkinter as ctk
import tkinter as tk # for treeview
from tkinter import ttk, messagebox # for treeview and  mesage box
from firebase_config import db # database connectiion
from forHover import set_hover_color

heavyrow = "#ADBBDA"
lightrow = "#EDE8F5"
vio = "#191970"
white = "white"
purplr ="#9747FF"
red ="#FF3737"
lightblue ="#4682B4"
vin ="#03346E"

route_filter = "All"
unit_type_filter = "All"
bus_class_filter = "All"
# function to update the widgets in the main_content_frame 
def manage_fares(action, main_content_frame):
    # Clear the frame
    for widget in main_content_frame.winfo_children():# select individual widget
        widget.destroy() # delete the widgets 

    # Code for button frame for managing bus schedule (serve as title holder)
    c_frame = ctk.CTkFrame(main_content_frame, corner_radius=0, fg_color=vin)
    c_frame.pack(fill="x")
    # Button frame to hold title and add/create button(serve as top bar)
    button_frame = ctk.CTkFrame(c_frame, corner_radius=0,fg_color=vin)
    button_frame.pack(fill="x")
    
    # tit;e
    title_label = ctk.CTkLabel(button_frame, text="FARES", text_color=white, font=("Arial", 23, "bold"), corner_radius=0)
    title_label.pack(side="left", pady=(10, 10), padx=20)

    # create button
    create_button = ctk.CTkButton(button_frame, text="Create", fg_color=white, text_color=vio, font=("Arial", 16,"bold"), command=lambda: create_fare(tree, db), height=35)
    create_button.pack(side=ctk.LEFT, padx=5)

    set_hover_color(create_button, hover_bg_color=purplr, hover_text_color=white, normal_bg_color=white, normal_text_color=vio)

    # frame to hold filter related widgets 
    filter_frame = ctk.CTkFrame(c_frame, corner_radius=0,fg_color=vin)
    filter_frame.pack(fill="x")
    filter_frame.columnconfigure(tuple(range(7)), weight=1)

    # ars to hold the values selected ion dropdwon objs with intial val ALL 
    route_var = tk.StringVar(value="All")
    unit_type_var = tk.StringVar(value="All")
    bus_class_var = tk.StringVar(value="All")

    # Create dropdowns for filtering
    ctk.CTkLabel(filter_frame, text="Route: ", text_color=white).grid(row=0, column=0, padx=(25,5), pady=(5,0), sticky="w")
    route_dropdown = ctk.CTkComboBox(filter_frame, variable=route_var, values=[], command=lambda _: filter_fares())
    route_dropdown.grid(row=1, column=0, padx=(20,5), pady=(0,10), sticky="w")
    
    ctk.CTkLabel(filter_frame, text="Bus Unit Type:", text_color=white).grid(row=0, column=1, padx=10, pady=(5,0), sticky="w")
    unit_type_dropdown = ctk.CTkComboBox(filter_frame, variable=unit_type_var, values=[], command=lambda _: filter_fares())
    unit_type_dropdown.grid(row=1, column=1, padx=5, pady=(0,10), sticky="w")

    ctk.CTkLabel(filter_frame, text="Bus Class:", text_color=white).grid(row=0, column=2, padx=10, pady=(0,5), sticky="w")
    bus_class_dropdown = ctk.CTkComboBox(filter_frame, variable=bus_class_var, values=["All", "AC", "NAC"], command=lambda _: filter_fares())
    bus_class_dropdown.grid(row=1, column=2, padx=5, pady=(0,10), sticky="w")

    # edit and delete buttons 
    delete_button = ctk.CTkButton(filter_frame, text="Delete", command=lambda: delete_fare(tree, db),fg_color=white,text_color=red, font=("Arial", 16,"bold"), height=35)
    delete_button.grid(row=0, rowspan=2, column=7, padx=(5,20), pady=(25,10), sticky="e")

    edit_button = ctk.CTkButton(filter_frame, text="Edit", command=lambda: edit_fare(tree, db),fg_color=white,text_color="#191970", font=("Arial", 16,"bold"), height=35)
    edit_button.grid(row=0, rowspan=2, column=6, padx=5, pady=(25,10), sticky="e")

    set_hover_color(delete_button, hover_bg_color=red, hover_text_color=white, normal_bg_color=white, normal_text_color=red)
    set_hover_color(edit_button, hover_bg_color=lightblue, hover_text_color=white, normal_bg_color=white, normal_text_color=vio)
    
    # store header names to a list
    columns = ("No.","Route", "Bus Unit Type", "Bus Class", "Fare", "ID")

    # create a tree frame 
    tree_frame = ctk.CTkFrame(main_content_frame)
    tree_frame.pack(fill="both", expand=True)
    #scroll bar
    tree_scroll = tk.Scrollbar(tree_frame)
    tree_scroll.pack(side="right",fill="y")# position of scrollbar

    tree = ttk.Treeview(tree_frame, columns=columns, yscrollcommand=tree_scroll.set, show='headings') # set column as headers, bind scrollbar to the treeview table 
    # set alternating color for individual rows 
    tree.tag_configure('oddrow', background=heavyrow)
    tree.tag_configure('evenrow', background=lightrow)

    #code to set the headers and cols.
    for col in columns:
        tree.heading(col, text=col)# create heading
        if col == 'No.':
            tree.column(col, width=30) #give val from array
        elif col == "Bus Class" or col == "Bus Unit Type" :
            tree.column(col, minwidth=0, width=120, anchor="center")
        elif col == "Fare":
            tree.column(col, minwidth=0, width=120, )
        else:
            tree.column(col, minwidth=0, width=170) #give val from array
    tree.pack(fill="both", expand=True)

    #configure scroll bar
    tree_scroll.config(command=tree.yview)

    tree.bind("<Double-1>", lambda e: edit_fare(tree, db))# event listener in treeview check if an item / row is douled clicked within 1 sec

    # function to run to put variable value set for dropdowns
    def populate_dropdowns(route_dropdown, unit_type_dropdown):
        # Fetch route names and unit types
        fares = db.collection('Fares').stream()# collect in a stream all doc in collection Fares

        #initialize set var to hold set of values for dropdown objs 
        route_values = set() 
        unit_type_values = set()

        for fare in fares:# loop through each fare in stream
            data = fare.to_dict()# fetch data as a dict
            # fetch the field val from dict
            route = data.get('route')
            unit_type = data.get('bus_unit_type')
            
            if route:# check if theres a route val field
                route_values.add(route)# add to the set
            if unit_type:# check if theres a unit type val field
                unit_type_values.add(unit_type)# add to the set

        # Convert sets to sorted lists and add "All" option
        route_values = ["All"] + sorted(list(route_values))
        unit_type_values = ["All"] + sorted(list(unit_type_values))

        # Update dropdown values
        route_dropdown.configure(values=route_values)
        unit_type_dropdown.configure(values=unit_type_values)

    #function to filter the treeview table based on selected val i dropdowns
    def filter_fares():
        global route_filter, unit_type_filter, bus_class_filter
        count =1 #counter 
        # Clear the existing data in the treeview
        for item in tree.get_children():
            tree.delete(item)

        # var to Fetch all fares and apply filters in code
        route_filter = route_var.get()
        unit_type_filter = unit_type_var.get()
        bus_class_filter = bus_class_var.get()

        refresh_tree(db, tree)

    # Populate the dropdowns and display all fares initially
    populate_dropdowns(route_dropdown, unit_type_dropdown)
    filter_fares()


#function for when create button is clicked
def create_fare(tree, database):
    #function to run when save button is clicked 
    def save_fare():
        count = 1
        route_id = route_var.get()  # Get the value for route Id input 

        # Fetch the document from the database that matches the route_id var value
        route_doc = database.collection('BusRoutes').document(route_id).get()
        route_data = route_doc.to_dict()  # Store the doc data in a dict
        route_name = f"{route_data['boarding_point']}-{route_data['dropping_point']}"  # Combine 2 field vals to 1 and store to a var

        if route_id == "" or route_name =="" or route_data =="" or bus_unit_type_var.get()=='' or bus_class_var =='' or fare_var == "":
            messagebox.showerror("Error", "Please provide all the needed Inputs.")  # Show error message 
            return
    
        # Define other data in the dict and pass the user inputs from the entry objs
        fare_data = {
            'route_id': route_id,
            'route': route_name,
            'route_info': route_data,
            'bus_unit_type': bus_unit_type_var.get(),
            'bus_class': bus_class_var.get(),
            'fare': float(fare_var.get())
        }

        # Turn var value for Id into its doc name/id in the database 
        fare_doc_name = f"{route_id}_{fare_data['bus_unit_type']}_{fare_data['bus_class']}"

        # Check if a doc with the same name/id already exists in the database
        if database.collection('Fares').document(fare_doc_name).get().exists:
            messagebox.showerror("Error", "Fare document already exists.")  # Show error message 
            return

         # Add the fare document to the database
        database.collection('Fares').document(fare_doc_name).set(fare_data)

        # Function to select the item based on matching values
        def select_item_by_values(column_2, column_3, column_4):
            for item in tree.get_children():
                item_values = tree.item(item, "values")
                if (item_values[1] == column_2 and
                    item_values[2] == column_3 and
                    item_values[3] == column_4):  # Check if the values match
                    tree.selection_set(item)
                    tree.see(item)  # Scroll to the selected item
                    return

        # Refresh the Treeview contents
        refresh_tree(database, tree)
    
        # Call the function to select the newly added row
        select_item_by_values(route_name, bus_unit_type_var.get(), bus_class_var.get())
    
        create_window.destroy()  # Destroy the created form window 
        messagebox.showinfo("Success", "Fare created successfully.")  # Show success message 


    # start of the main code
    # create window form
    create_window = ctk.CTkToplevel()
    create_window.title("Create Fare")

    # Keep the window on top
    create_window.lift()
    create_window.attributes("-topmost", True)
    create_window.configure(fg_color="#03346E")

    def validate_integer(P):
        if P == "":
            return True
        try:
            float(P)
            return True
        except ValueError:
            return False
    vcmd = create_window.register(validate_integer)  # Register validation function
    
    # labels and entry objs for needed user input 
    ctk.CTkLabel(create_window, text="Route:", text_color="#E2E2B6").grid(row=0, column=0, padx=10, pady=5)
    route_var = tk.StringVar()
    routes = database.collection('BusRoutes').get()
    route_values = [route.id for route in routes] # fetch route val from the database as variable values of dropdown
    route_dropdown = ctk.CTkComboBox(create_window, variable=route_var, values=route_values)
    route_dropdown.grid(row=0, column=1, padx=10, pady=5)

    ctk.CTkLabel(create_window, text="Bus Unit Type:", text_color="#E2E2B6").grid(row=1, column=0, padx=10, pady=5)
    bus_unit_type_var = tk.StringVar()
    unit_type_values = list(set([bus.to_dict()['unit_type'] for bus in database.collection('Buses').get()]))# fetch specific field value (unittype) in fetched doc and store as variabe value for dropdown and loop the code for all collected doc.
    bus_unit_type_dropdown = ctk.CTkComboBox(create_window, variable=bus_unit_type_var, values=unit_type_values)
    bus_unit_type_dropdown.grid(row=1, column=1, padx=10, pady=5)

    ctk.CTkLabel(create_window, text="Bus Class:", text_color="#E2E2B6").grid(row=2, column=0, padx=10, pady=5)
    bus_class_var = tk.StringVar()
    bus_class_dropdown = ctk.CTkComboBox(create_window, variable=bus_class_var, values=["AC", "NAC"])# predefined variable val 
    bus_class_dropdown.grid(row=2, column=1, padx=10, pady=5)

    ctk.CTkLabel(create_window, text="Fare:", text_color="#E2E2B6").grid(row=3, column=0, padx=10, pady=5)
    fare_var = tk.StringVar()
    fare_entry = ctk.CTkEntry(create_window, textvariable=fare_var, text_color="#191970", validate="key",  validatecommand=(vcmd, '%P'))
    fare_entry.grid(row=3, column=1, padx=10, pady=5)

    # save button
    save_button = ctk.CTkButton(create_window, text="Save", command=save_fare,text_color="#191970", fg_color="#E2E2B6", hover_color="#6EACDA" )
    save_button.grid(row=4, columnspan=2, pady=10)


# function to run when edit button from main_content frame is clicekd 
def edit_fare(tree, database):
    selected_item = tree.selection()# fetch the val of selected row in the treeview table 
    if selected_item: # check if a value is se;ected in a treeview
        # fetch its column value and store to a set
        item = tree.item(selected_item)
        values = item['values']
        fare_id = values[5]
        fare_doc = database.collection('Fares').document(fare_id).get()
        if not fare_doc.exists:
            messagebox.showerror("Error", "Selected schedule document not found.")
            return
        fare_data = fare_doc.to_dict()

       #function to run when save button is clicked in the created form
        def update_fare():
            route_id = route_var.get()# fetch the value from input/ genrated Id 
            route_doc = database.collection('BusRoutes').document(route_id).get()# fetch the doc with the same doc name as with the var that is fetched 
            route_data = route_doc.to_dict()# store the doc field and vals to a dict
            route_name = f"{route_data['boarding_point']}-{route_data['dropping_point']}"# make a var to hold abnd combine the firstname and lastname field values

            if fare_var.get() =="":
                messagebox.showinfo("Success", "Please Enter A value for Fare.")# show succes notif 
                return
            
            # update the dict with user inputs in the entry objs from the form
            updated_data = {
                'route_id': route_id,
                'route': route_name,
                'route_info': route_data,
                'bus_unit_type': bus_unit_type_var.get(),
                'bus_class': bus_class_var.get(),
                'fare': float(fare_var.get())
            }
            database.collection('Fares').document(fare_id).update(updated_data)# update the document with the vals from the dict 

            # Function to select the item based on matching values
            def select_item_by_values(column_2, column_3, column_4):
                for item in tree.get_children():
                    item_values = tree.item(item, "values")
                    if (item_values[1] == column_2 and
                        item_values[2] == column_3 and
                        item_values[3] == column_4):  # Check if the values match
                        tree.selection_set(item)
                        tree.see(item)  # Scroll to the selected item
                        return

            # Refresh the Treeview contents
            refresh_tree(database, tree)
            # Call the function to select the newly added row
            select_item_by_values(route_name, bus_unit_type_var.get(), bus_class_var.get())

            edit_window.destroy()# destroy the window form
            messagebox.showinfo("Success", "Fare updated successfully.")# show message for success input

        # Code for the window frame 
        #create the new window 
        edit_window = ctk.CTkToplevel()
        edit_window.title("Edit Fare")
        # Keep the window on top
        edit_window.lift()
        edit_window.attributes("-topmost", True)
        edit_window.configure(fg_color="#03346E")

        def validate_integer(P):
            if P == "":
                return True
            try:
                float(P)
                return True
            except ValueError:
                return False
        vcmd = edit_window.register(validate_integer)  # Register validation function

        #label and entry objs for needed user input
        ctk.CTkLabel(edit_window, text="Route:", text_color="#E2E2B6").grid(row=0, column=0, padx=10, pady=5)
        route_var = tk.StringVar(value=fare_data['route_id'])
        routes = database.collection('BusRoutes').get()
        route_values = [route.id for route in routes] # fetch thevalue for dropdown variable values from database 
        route_dropdown = ctk.CTkComboBox(edit_window, variable=route_var, values=route_values)
        route_dropdown.grid(row=0, column=1, padx=10, pady=5)
        route_dropdown.set(fare_data['route'])# set value from the seletcted row converted to a list
        route_dropdown.configure(state="disabled")

        ctk.CTkLabel(edit_window, text="Bus Unit Type:", text_color="#E2E2B6").grid(row=1, column=0, padx=10, pady=5)
        bus_unit_type_var = tk.StringVar(value=fare_data['bus_unit_type'])
        unit_type_values = list(set([bus.to_dict()['unit_type'] for bus in database.collection('Buses').get()])) # fetch a field value from evry document inside the collection and store values to a list
        bus_unit_type_dropdown = ctk.CTkComboBox(edit_window, variable=bus_unit_type_var, values=unit_type_values)
        bus_unit_type_dropdown.grid(row=1, column=1, padx=10, pady=5)
        bus_unit_type_dropdown.set(values[2]) # set value from the seletcted row converted to a list
        bus_unit_type_dropdown.configure(state="disabled")

        ctk.CTkLabel(edit_window, text="Bus Class:", text_color="#E2E2B6").grid(row=2, column=0, padx=10, pady=5)
        bus_class_var = tk.StringVar(value=fare_data['bus_class'])
        bus_class_dropdown = ctk.CTkComboBox(edit_window, variable=bus_class_var, values=["AC", "NAC"])# predefine variable values 
        bus_class_dropdown.grid(row=2, column=1, padx=10, pady=5)
        bus_class_dropdown.set(values[3]) # set value from the seletcted row converted to a list
        bus_class_dropdown.configure(state="disabled")

        ctk.CTkLabel(edit_window, text="Fare:", text_color="#E2E2B6").grid(row=3, column=0, padx=10, pady=5)
        fare_var = tk.StringVar()
        fare_entry = ctk.CTkEntry(edit_window, textvariable=fare_var, text_color="#191970", validate="key",  validatecommand=(vcmd, '%P'))
        fare_entry.grid(row=3, column=1, padx=10, pady=5)
        fare_entry.insert(0, fare_data['fare']) # set value from the seletcted row converted to a list

        # save button
        save_button = ctk.CTkButton(edit_window, text="Save", command=update_fare, text_color="#191970", fg_color="#E2E2B6", hover_color="#6EACDA")
        save_button.grid(row=4, columnspan=2, pady=10)
    else:# if there is no seletcted data in the treeview
        messagebox.showerror("Eror", "No Frae is Selected!")# show an error message 


# function to run when the delete button from the main_content_frame is clicked 
def delete_fare(tree, database):
    selected_item = tree.selection() # fetch the selected data in treeview table 
    if selected_item:# check if there is a selected data in treeview table 
        # fetch and store as a list
        item = tree.item(selected_item)
        values = item['values']

        # collect all document from database then check if the combinde value of dropping and boarding value from fetch document matches the selected row in treview table
        route_id = [x for x in database.collection('BusRoutes').get() 
                    if f"{x.to_dict()['boarding_point']}-{x.to_dict()['dropping_point']}" == values[1]] [0].id

        fare_doc_name = f"{route_id}_{values[2]}_{values[3]}"# store anc combine the values

        # Make a confiramtion before deletion
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this driver?")
        if confirm: # if yes 
            database.collection('Fares').document(fare_doc_name).delete()# fetch the document in database that matechs the fare_doc_name and delete it 

            refresh_tree(db,tree) # refresh the content of the treeview table 
            messagebox.showinfo("Success", "Fare deleted successfully.")# display mesage for success
        else:# if no
            return
        
def refresh_tree(db,tree):
    global route_filter, unit_type_filter, bus_class_filter
    count = 1

    #delete items in treview
    for item in tree.get_children():
        tree.delete(item)
        
    fares = db.collection('Fares').stream()# fetch all docs in collection in form of stream
    for fare in fares:# loop through the stream
        data = fare.to_dict()# fetch the value from stream and store in form of a dict,

        if (route_filter == "All" or data.get('route') == route_filter) and \
            (unit_type_filter == "All" or data.get('bus_unit_type') == unit_type_filter) and \
            (bus_class_filter == "All" or data.get('bus_class') == bus_class_filter): # check for parameters that matches a doc
                
            row_tag = "oddrow" if count % 2 == 0 else "evenrow"
            tree.insert("", ctk.END, values=(count,
                data.get('route', 'Not available'), 
                data.get('bus_unit_type', 'Not available'), 
                data.get('bus_class', 'Not available'), 
                f"₱. {data.get('fare', 'N/A')}",
                fare.id ),tags=(row_tag,))
            count +=1 # increment counter