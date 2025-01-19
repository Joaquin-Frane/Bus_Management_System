

#function when add button is clicked
def create_schedule(db, tree):
    #create a form window
    create_window = ctk.CTkToplevel()
    create_window.title("Create Schedule")
    # Keep the window on top
    create_window.lift()
    create_window.attributes("-topmost", True)
    create_window.configure(fg_color="#03346E")

    # Route dropdown
    ctk.CTkLabel(create_window, text="Route:",text_color="#E2E2B6").grid(row=0, column=0, padx=10, pady=5)
    route_var = ctk.StringVar() #hold the selected route value
    routes = db.collection('BusRoutes').get()# get all docs from colletion
    route_dropdown = ctk.CTkComboBox(create_window, variable=route_var, width=200, text_color="#191970")# dropdown obj 
    route_dropdown.configure(values=[route.id for route in routes])# configure variable vlas.
    route_dropdown.grid(row=0, column=1, padx=10, pady=5)

    # Driver dropdown
    ctk.CTkLabel(create_window, text="Driver:",text_color="#E2E2B6").grid(row=1, column=0, padx=10, pady=5)
    driver_var = ctk.StringVar()#hold the selected route value
    driver_dropdown = ctk.CTkComboBox(create_window, variable=driver_var, width=200, text_color="#191970") #dropdown obj
    driver_dropdown.grid(row=1, column=1, padx=10, pady=5)

    # Driver dropdown
    ctk.CTkLabel(create_window, text="Departure Date:",text_color="#E2E2B6").grid(row=2, column=0, padx=10, pady=5)
    date= datetime.now()
    cdate = date.strftime("%Y-%m-%d")
    date_entry = ctk.CTkEntry(create_window, placeholder_text=cdate,width=200, text_color="#191970") #dropdown obj
    date_entry.grid(row=2, column=1, padx=10, pady=5)

    #function to update the variable values of dropdown drivers
    def update_driver_dropdown(*args):
        route = route_var.get()# get the val from dropdown obj
          # Debugging statement
        if route: # check for bus that matches the route
            query = db.collection('Buses').where('assigned_route', '==', route)# fetch collection for buses assigned to the selected route.
            buses = query.stream() #get the result of query
            drivers = [bus.to_dict().get('driver', 'Unknown') for bus in buses] # Extracts the driver names from the bus documents
            unique_drivers = list(set(drivers))  # Remove duplicates

            if unique_drivers: #Checks if there are unique drivers
                driver_dropdown.configure(values=unique_drivers) # update the dropdown
                if driver_dropdown.get() not in unique_drivers:
                    driver_dropdown.set('') # Clears the dropdown if the selected driver is not available
            else: # If no drivers are found for the selected route in dropdown route
                driver_dropdown.configure(values=['No drivers available'])
                # give specific val on dropdown
                driver_dropdown.set('No drivers available')
        else: #  If no route is selected
            driver_dropdown.configure(values=[])
            driver_dropdown.set('')

    route_var.trace_add('write', update_driver_dropdown)  # Trigger update when route_var changes

    # Departure Time Entry
    ctk.CTkLabel(create_window, text="Departure Time:", text_color="#E2E2B6").grid(row=3, column=0, padx=10, pady=5)
    #hold the value from spinbox objs and set predefine val.
    hour_var = ctk.StringVar(value="1")
    minute_var = ctk.StringVar(value="00")
    am_pm_var = ctk.StringVar(value="AM")
    #freme to hold time related objs
    hour_frame = ctk.CTkFrame(create_window, border_width=3, corner_radius=10, width=229, fg_color="#03346E")
    hour_frame.grid(row=3, column=1)
    #spinboxes
    hour_spinbox = tk.Spinbox(hour_frame, from_=1, to=12, textvariable=hour_var, width=3, bg="grey", font=("Arial", 12))
    hour_spinbox.pack(side="left", padx=(5, 3), pady=5)
    
    minute_spinbox = tk.Spinbox(hour_frame, from_=0, to=59, textvariable=minute_var, format="%02.0f", width=3, bg="grey", font=("Arial", 12))
    minute_spinbox.pack(side="left", padx=(0, 3))
    #dropdown
    am_pm_dropdown = ctk.CTkComboBox(hour_frame, variable=am_pm_var, values=["AM", "PM"], width=95, height=23)
    am_pm_dropdown.pack(side="left", padx=(0, 5), pady=5)

    #function to run when save button is clicked to 
    def save_schedule():
        global count
        departure_time_str = f"{hour_var.get()}:{minute_var.get()} {am_pm_var.get()}"
        driver = driver_var.get()
        date = date_entry.get()

        # Query the Buses collection for the bus assigned to the selected driver
        bus_doc = db.collection('Buses').where('driver', '==', driver).limit(1).stream()
        bus_doc_list = list(bus_doc)
        if bus_doc_list:
            bus_data = bus_doc_list[0].to_dict()
            bus_id = bus_doc_list[0].id
            unit_type = bus_data.get('unit_type')
            bus_class = bus_data.get('bus_class')
        else:
            bus_id = None
            unit_type = None
            bus_class = None

        # Check for existing schedule with the same departure time and driver
        existing_schedules = db.collection('BusSchedule').where('departure_time', '==', departure_time_str).where('driver', '==', driver).where('departure_date', '==', date).stream()

        if any(existing_schedules):
            messagebox.showerror("Error", "A schedule with the same departure time and driver already exists.")
            return
        # Prepare the schedule data
        combined_string = route_var.get() + "_" + unit_type + "_" + bus_class
        
        # Step 2: Get the document from the "Fares" collection
        doc_ref = db.collection("Fares").document(combined_string)
        doc = doc_ref.get()

        if doc.exists:
            # Step 3: Fetch the "fare" field value
            fare_value = doc.to_dict().get('fare')
            print(f"Fare value: {fare_value}")
        else:
            print(f"Document '{combined_string}' not found in the Fares collection.")

        def fetch_fare_value():
            # Step 1: Combine the variables to form the document name
            combined_string = "_".join([route_var.get(), unit_type, bus_class])  # For example: "value1_value2_value3"
            try:
                # Step 2: Get the document from the "Fares" collection
                doc_ref = db.collection("Fares").document(combined_string)
                doc = doc_ref.get()
                if doc.exists:
                    # Step 3: Fetch the "fare" field value
                    fare_value = doc.to_dict().get('fare')
                    print(f"Fare value: {fare_value}")
                    return fare_value
                else:
                    print(f"Document '{combined_string}' not found in the Fares collection.")
                    return None
            except Exception as e:
                print(f"Error fetching fare: {e}")
                return None
                
        fare = fetch_fare_value()
        def fetch_seat_field(doc_name):
            try:
                doc_ref = db.collection('Unit_type').document(doc_name)# Reference to the collection where documents are stored
                # Fetch the document
                doc = doc_ref.get()
        
                # Check if the document exists
                if doc.exists:
                    # Extract the 'seat' field (which is a map data type)
                    seat_field = doc.get('seats')
                    global noOfSeat
                    noOfSeat = doc.get('no_of_seat')
                    # Check if the 'seats' field exists in the document
                    if seat_field:
                        print("Seat field:", seat_field)  # You can store it in a variable or return it
                        return seat_field
                    else:
                        print(f"No 'seats' field found in document: {doc_name}")
                        return None
                else:
                    print(f"No document found with the name: {doc_name}")
                    return None
            except Exception as e:
                print(f"Error fetching document: {e}")
                return None     
        seat_data = fetch_seat_field(unit_type)    
        schedule_data = {
            'route': route_var.get(),
            'departure_date':date,
            'departure_time': departure_time_str,
            'driver': driver,
            'bus_id': bus_id,
            'unit_type': unit_type,
            'bus_class': bus_class,
            'fare': float(fare),
            'no_of_seats': noOfSeat,
            'seats': seat_data,
            'status': 'Active'
        }
        db.collection('BusSchedule').add(schedule_data)# Add the schedule to the database
        refresh_tree(db, tree)# Refresh the Treeview contents
        # Function to select the item based on matching values in columns 2, 3, and 4
        def select_item_by_values(column_2, column_3, column_4, column_5):
            for item in tree.get_children():
                item_values = tree.item(item, "values")
                if (item_values[1] == column_2 and
                    item_values[2] == column_3 and
                    item_values[3] == column_4 and 
                    item_values[4] == column_5):
                    tree.selection_set(item)
                    tree.see(item)
                    return
        # Now call the function to select the newly added schedule row
        select_item_by_values(schedule_data['route'],schedule_data['departure_date'], schedule_data['departure_time'], schedule_data['driver'])
        create_window.destroy()
        messagebox.showinfo("Success", "Bus schedule created successfully.")
    # Save button
    ctk.CTkButton(create_window, text="Save", command=save_schedule, fg_color="#E2E2B6", text_color="#191970", hover_color="#6EACDA").grid(row=4, columnspan=4, pady=10)

#function for edit button function
def edit_schedule(db, tree):
    selected_item = tree.selection()  # Get the row selected on Treeview
    if selected_item:  # Check if there is a selected value on Treeview
        item = tree.item(selected_item)
        values = item['values']
        driver = values[4]
        departure_time = values[3]
        departure_date = values[2]
        route = values[1]
        status = values[9]
        #print(f"\n\n\n pretest: route {route}, driver{driver}, departure{departure}")

        # Revert to using chained 'where' clauses
        sched = db.collection('BusSchedule').where('driver', '==', driver).where('departure_date', '==', departure_date).where('departure_time', '==', departure_time).where('route', '==', route).get()

        doc = sched[0]
        doc_id = doc.id
        print(f"\n\n\nThis isedited : {doc_id}")
        # Create a form window
        edit_window = ctk.CTkToplevel()
        edit_window.title("Edit Schedule")
        edit_window.lift()
        edit_window.attributes("-topmost", True)
        edit_window.configure(fg_color="#03346E")

        # Function to update the variable values of driver dropdown
        def update_driver_dropdown(*args):
            print("update_driver_dropdown called")  # Debugging statement
            route = route_var.get()  # Fetch the value of the selected route
            print(f"Selected route: {route}")  # Debugging statement

            if route:  # Check if route is selected
                query = db.collection('Buses').where('assigned_route', '==', route)  # Query the Buses collection
                buses = query.stream()  # Stream the results of the query
                print(f"Query result: {query}")
                drivers = [bus.to_dict().get('driver', 'Unknown') for bus in buses]
                unique_drivers = list(set(drivers))  # Extract the driver names
                print(f"Unique drivers: {unique_drivers}")

                if unique_drivers:  # If it has unique values
                    driver_dropdown.configure(values=unique_drivers)  # Update dropdown values
                    if driver_dropdown.get() not in unique_drivers:  # If not a unique value, set to empty
                        driver_dropdown.set('')
                else:  # If none is selected, update dropdown with defined values
                    driver_dropdown.configure(values=['No drivers available'])
                    driver_dropdown.set('No drivers available')
            else:  # If no route selected
                driver_dropdown.configure(values=[])
                driver_dropdown.set('')

        # Labels, dropdown, and entry input for needed values
        ctk.CTkLabel(edit_window, text="Route:", text_color="#E2E2B6").grid(row=0, column=0, padx=10, pady=5)
        route_var = ctk.StringVar()
        routes = db.collection('BusRoutes').get()  # Fetch all bus routes
        route_dropdown = ctk.CTkComboBox(edit_window, variable=route_var, width=200)
        route_dropdown.configure(values=[route.id for route in routes])
        route_dropdown.grid(row=0, column=1, padx=10, pady=5)
        route_dropdown.set(route)

        ctk.CTkLabel(edit_window, text="Driver:", text_color="#E2E2B6").grid(row=1, column=0, padx=10, pady=5)
        driver_var = ctk.StringVar()
        driver_dropdown = ctk.CTkComboBox(edit_window, variable=driver_var, width=200)
        driver_dropdown.grid(row=1, column=1, padx=10, pady=5)
        
        ctk.CTkLabel(edit_window, text="Departure Date:", text_color="#E2E2B6").grid(row=2, column=0, padx=10, pady=5)
        date_entry = ctk.CTkEntry(edit_window,placeholder_text="YYYY-MM-DD", width=200) #dropdown obj
        date_entry.grid(row=2, column=1, padx=10, pady=5)
        date_entry.insert(0, departure_date)

        # Bind the update_driver_dropdown function to the event when a route is selected from the dropdown
        route_dropdown.bind("<<ComboboxSelected>>", update_driver_dropdown)

        # Trigger the dropdown update initially to populate driver dropdown
        update_driver_dropdown()

        # Set the driver dropdown to current driver in the selected schedule
        driver_dropdown.set(values[4])

        # Add labels and spinboxes for time input
        ctk.CTkLabel(edit_window, text="Departure Time:", text_color="#E2E2B6").grid(row=4, column=0, padx=10, pady=5)

        # Split the string into two parts based on the space
        time_parts = departure_time.split(" ")
        # Now split the first part (e.g., '6:00') based on the colon ':'
        hours, minutes = time_parts[0].split(":")
        # The second part will be the AM/PM value
        period = time_parts[1]
        
        # Variables to hold input/selected values
        hour_var = ctk.StringVar(value=hours)
        minute_var = ctk.StringVar(value=minutes)
        am_pm_var = ctk.StringVar(value=period)

        # Frame to hold the time-related widgets
        hour_frame = ctk.CTkFrame(edit_window, border_width=3, corner_radius=10, width=229)
        hour_frame.grid(row=4, column=1)

        hour_spinbox = tk.Spinbox(hour_frame, from_=1, to=12, textvariable=hour_var, width=3, bg="grey", font=("Arial", 12))
        hour_spinbox.pack(side="left", padx=(5, 3), pady=5)

        minute_spinbox = tk.Spinbox(hour_frame, from_=0, to=59, textvariable=minute_var, format="%02.0f", width=3, bg="grey", font=("Arial", 12))
        minute_spinbox.pack(side="left", padx=(0, 3))

        am_pm_dropdown = ctk.CTkComboBox(hour_frame, variable=am_pm_var, values=["AM", "PM"], width=95, height=23)
        am_pm_dropdown.pack(side="left", padx=(0, 5), pady=5)

        ctk.CTkLabel(edit_window, text="Status:", text_color="#E2E2B6").grid(row=4, column=0, padx=10, pady=5)
        status_entry = ctk.CTkEntry(edit_window, placeholder_text="Active", width=200) 
        status_entry.grid(row=4, column=1, padx=10, pady=5)
        status_entry.insert(0, status)

        # Function when save button is clicked
        def save_edited_schedule():
            global count
            departure_time_str = f"{hour_var.get()}:{minute_var.get()} {am_pm_var.get()}"
            driver = driver_var.get()  # Convert time-related inputs to one string and fetch it

            bus_doc = db.collection('Buses').where('driver', '==', driver).limit(1).stream()  # Query for the bus driven by the selected driver
            bus_doc_list = list(bus_doc)  # Convert the bus query result to a list

            if bus_doc_list:  # If any bus was found
                bus_data = bus_doc_list[0].to_dict()  # Get doc as a dict
                bus_id = bus_doc_list[0].id
                unit_type = bus_data.get('unit_type')
                bus_class = bus_data.get('bus_class')
            else:  # If none found
                bus_id = None
                unit_type = None
                bus_class = None

            # Check if a schedule with the same departure time and driver already exists
            existing_schedules = db.collection('BusSchedule').where('departure_date', '==', date_entry.get()).where('departure_time', '==', departure_time_str).where('driver', '==', driver).stream()

            # Filter out documents with the same name as `idname`
            filtered_schedules = [sched for sched in existing_schedules if sched.id != doc_id]

            if any(filtered_schedules) and departure_time_str != values[2] and driver != values[3]:  # If such a schedule exists
                messagebox.showerror("Error", "A schedule with the same departure time and driver already exists.")
                return
            

            def fetch_fare_value():
                # Step 1: Combine the variables to form the document name
                combined_string = "_".join([route_var.get(), unit_type, bus_class])  # For example: "value1_value2_value3"

                try:
                    # Step 2: Get the document from the "Fares" collection
                    doc_ref = db.collection("Fares").document(combined_string)
                    doc = doc_ref.get()

                    if doc.exists:
                        # Step 3: Fetch the "fare" field value
                        fare_value = doc.to_dict().get('fare')
                        print(f"Fare value: {fare_value}")
                        return fare_value
                    else:
                        print(f"Document '{combined_string}' not found in the Fares collection.")
                        return None

                except Exception as e:
                    print(f"Error fetching fare: {e}")
                    return None
                
            fare = fetch_fare_value()

            def fetch_seat_field(doc_name):
                try:
                    # Reference to the collection where documents are stored
                    doc_ref = db.collection('Unit_type').document(doc_name)
                    # Fetch the document
                    doc = doc_ref.get()
        
                    # Check if the document exists
                    if doc.exists:
                        # Extract the 'seat' field (which is a map data type)
                        seat_field = doc.get('seats')
                        global noOfSeat
                        noOfSeat = doc.get('no_of_seat')

                        # Check if the 'seats' field exists in the document
                        if seat_field:
                            print("Seat field:", seat_field)  # You can store it in a variable or return it
                            return seat_field
                        else:
                            print(f"No 'seats' field found in document: {doc_name}")
                            return None
                    else:
                        print(f"No document found with the name: {doc_name}")
                        return None
                except Exception as e:
                    print(f"Error fetching document: {e}")
                    return None
                
            seat_data = fetch_seat_field(unit_type)

            # Else, store inputted data in a dict
            schedule_data = {
                'route': route_var.get(),
                'departure_date': date_entry.get(),
                'departure_time': departure_time_str,
                'driver': driver,
                'bus_id': bus_id,
                'unit_type': unit_type,
                'bus_class': bus_class,
                'fare': float(fare),
                'no_of_seats': noOfSeat,
                "seats": seat_data,
                'status': status_entry.get(),
            }
            
            
            #print(f"This is edited:{selected_schedule}")
            db.collection('BusSchedule').document(doc_id).set(schedule_data)
            refresh_tree(db, tree)# Refresh the Treeview contents
            # Function to select the item based on matching values in columns 2, 3, and 4
            def select_item_by_values(column_2, column_3, column_4, column_5):
                for item in tree.get_children():
                    item_values = tree.item(item, "values")
                    if (item_values[1] == column_2 and
                        item_values[2] == column_3 and
                        item_values[3] == column_4 and 
                        item_values[4] == column_5):
                        tree.selection_set(item)
                        tree.see(item)
                        return
            # Now call the function to select the newly added schedule row
            select_item_by_values(schedule_data['route'],schedule_data['departure_date'], schedule_data['departure_time'], schedule_data['driver'])
            edit_window.destroy()
            messagebox.showinfo("Success", "Bus schedule updated successfully.")

        # Save button
        ctk.CTkButton(edit_window, text="Save", command=save_edited_schedule, fg_color="#E2E2B6", text_color="#191970", hover_color="#6EACDA").grid(row=5, columnspan=4, pady=10)

    else:  # If no selected rows, show error message
        messagebox.showerror("ERROR", "No Schedule is selected.")





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

    # Function to filter data
    def filter_data(*args):
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
            if (selected_boarding == "All" or data.get('boarding_point') == selected_boarding) and \
               (selected_dropping == "All" or data.get('dropping_point') == selected_dropping) and \
               (selected_status == "All" or status == selected_status):
                
                row_tag = "cancel" if status == "Inactive" else "oddrow" if count % 2 == 0 else "evenrow"
                tree.insert("", "end", values=(count,
                    route.id, 
                    data.get('boarding_point', 'N/A'), 
                    data.get('dropping_point', 'N/A'),
                    f"{data.get('distance', 'N/A')}  KM", 
                    data.get('approx_time', 'N/A'), 
                    status), tags=(row_tag,))
                count += 1

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
    boarding_dropdown = ctk.CTkComboBox(filter_frame, variable=global_boarding_var, values=boarding_points, command=filter_data)
    boarding_dropdown.grid(row=1, column=0, padx=(20, 0), pady=(0, 10), sticky="nw")

    ctk.CTkLabel(filter_frame, text="Dropping Point:", text_color=white).grid(row=0, column=1, padx=10, pady=(5, 0), sticky="nw")
    dropping_dropdown = ctk.CTkComboBox(filter_frame, variable=global_dropping_var, values=dropping_points, command=filter_data)
    dropping_dropdown.grid(row=1, column=1, padx=5, pady=(0, 10), sticky="nw")

    # Add Status filter
    ctk.CTkLabel(filter_frame, text="Status:", text_color=white).grid(row=0, column=2, padx=10, pady=(5, 0), sticky="nw")
    status_dropdown = ctk.CTkComboBox(filter_frame, variable=global_status_var, values=["All", "Active", "Inactive"], command=filter_data)
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
    filter_data()

import customtkinter as ctk
from tkinter import messagebox

# Function when button "Create Route" is clicked with parameters db and tree for Treeview table update
def create_bus_route(db, tree):
    # Define color variables for background, input boxes, and button
    fg_Color= "#03346E"
    bg_color = ""  # Light blue background
    input_color = "#FFB6C1"  # Light pink input boxes
    button_color = "#90EE90"  # Light green buttons

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

    vcmd = create_window.register(validate_integer)  # Register validation function

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
    distance = ctk.CTkEntry(create_window, validate="key", placeholder_text="100", validatecommand=(vcmd, '%P'), width=160, fg_color="#fff", text_color="#191970")
    distance.grid(row=3, column=1, columnspan=2, padx=10, pady=5)

    # Add separate entry fields for hours and minutes
    ctk.CTkLabel(create_window, text="Approx. Time (HH:MM):", text_color="#E2E2B6").grid(row=4, column=0, padx=10, pady=5, sticky='e')
    approx_hours = ctk.CTkEntry(create_window, placeholder_text="HH", validate="key", validatecommand=(vcmd, '%P'), width=70, fg_color="#fff", text_color="#191970")
    approx_hours.grid(row=4, column=1, padx=(10,5), pady=5, sticky="e")

    approx_minutes = ctk.CTkEntry(create_window, placeholder_text="MM", validate="key", validatecommand=(vcmd, '%P'), width=70, fg_color="#fff", text_color="#191970")
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




search_value = ""
status_filter = "All"
terminal_filter = "All"

def manage_drivers(action, main_content_frame):
    global search_value, status_filter, terminal_filter

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
    add = ctk.CTkButton(buttons_frame, text="Add", fg_color=white, text_color=vio, font=("Arial", 16, "bold"), 
                        command=lambda: create_driver(db, tree), height=35)
    add.pack(side="left", padx=5)
    set_hover_color(add, hover_bg_color=purplr, hover_text_color=white, normal_bg_color=white, normal_text_color=vio)

    # Filter Widgets
    status_var = ctk.StringVar(value=status_filter)
    service_terminal_var = ctk.StringVar(value=terminal_filter)

    ctk.CTkLabel(search_frame, text="Status:", text_color=white).grid(row=0, column=0, padx=(25,), pady=(5, 0), sticky="w")
    status_dropdown = ctk.CTkComboBox(search_frame, variable=status_var, values=["All", "Active", "Inactive"], 
                                      command=lambda _: update_filters())
    status_dropdown.grid(row=1, column=0, padx=(20, 5), pady=(0, 10), sticky="w")

    ctk.CTkLabel(search_frame, text="Service Terminal:", text_color=white).grid(row=0, column=1, padx=10, pady=(5, 0), sticky="w")
    service_terminal_dropdown = ctk.CTkComboBox(search_frame, variable=service_terminal_var, values=terminals, 
                                                command=lambda _: update_filters())
    service_terminal_dropdown.grid(row=1, column=1, padx=5, pady=(0, 10), sticky="w")

    ctk.CTkLabel(search_frame, text="NAME:", text_color=white).grid(row=0, column=2, padx=10, pady=(5, 0), sticky="w")
    search_entry = ctk.CTkEntry(search_frame, text_color="#191970", width=200, placeholder_text="Jaun D", 
                                placeholder_text_color="#6eacda")
    search_entry.grid(row=1, column=2, padx=5, pady=(0, 10), sticky="w")
    search_entry.bind("<Return>", lambda event: update_filters(search_entry.get()))

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
            tree.column(col, minwidth=0, width=50 )
        elif col == "Driver ID" or col == "Wage/Hr." or col =="Srvc. Trm":
            tree.column(col, minwidth=0, width=100 )
        elif col == "Status" :
            tree.column(col, minwidth=0, width=80, anchor='center')
        elif col == "License No." or col == "Address" or col=="Phone No.":
            tree.column(col, minwidth=0, width=120 )
        else:
            tree.column(col, minwidth=0, width=130 )

    tree.pack(fill="both", expand=True)
    tree_scroll.config(command=tree.yview)

    tree.tag_configure('oddrow', background=heavyrow)
    tree.tag_configure('evenrow', background=lightrow)
    tree.tag_configure('Inactive', background="#cc3e40", foreground="#fff")
    tree.bind("<Double-1>", lambda e: edit_driver(db, tree))

    # Update global filters
    def update_filters(new_search_value=None):
        global search_value, status_filter, terminal_filter
        search_value = new_search_value if new_search_value is not None else search_value
        status_filter = status_var.get()
        terminal_filter = service_terminal_var.get()
        refresh_tree(db, tree)

def refresh_tree(db, tree):
    global search_value, status_filter, terminal_filter
    drivers = list(db.collection('Drivers').stream())  # Fetch all documents in 'Drivers' collection
    tree.delete(*tree.get_children())
    count = 1
    for driver in drivers:
        data = driver.to_dict()
        if (status_filter == "All" or data.get('status', '') == status_filter) and \
           (terminal_filter == "All" or data.get('service_terminal', '') == terminal_filter):
            full_name = f"{data.get('first_name', '')} {data.get('last_name', '')}".lower()
            if search_value.lower() in full_name:
                tag = "oddrow" if count % 2 == 0 else "evenrow"
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
                        data.get('status', '')), tags=(tag,))
                count += 1



 # Define headings
    tree.heading("time", text="TIME")
    tree.heading("route", text="ROUTE")
    tree.heading("fare", text="FARE")
    tree.heading("unit_type", text="U.TYPE")
    tree.heading("class", text="CLASS")
    tree.heading("bus_id", text="BUS ID")

    # Define column widths
    tree.column("time", anchor="center", width=70)
    tree.column("route", width=130)
    tree.column("fare", anchor="center", width=70)
    tree.column("unit_type", anchor="center", width=120)
    tree.column("class", anchor="center", width=60)
    tree.column("bus_id", width=150)
    