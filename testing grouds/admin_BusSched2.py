import customtkinter as ctk  # widget GUI
import tkinter as tk  # for other widget GUI
from tkinter import ttk, messagebox  # treeview and message boxes
from tkinter import Canvas, Scrollbar  # for scrollable canvas
from firebase_config import db  # database
from CTkSpinbox import *  # spinbox
from datetime import datetime
from firebase_admin import firestore
import threading
from forHover import set_hover_color

count = 1  # global counter


heavyrow = "#ADBBDA"
lightrow = "#EDE8F5"
vio = "#191970"
white = "white"
purplr ="#9747FF"
red ="#FF3737"
lightblue ="#4682B4"
vin ="#03346E"

route = "All"
bus_class = "All"
search_date = ""
time_filter = ""
time_am_pm = 'AM'
status_var = 'All'
id_search_var = ""
id_search_text =""

def manage_bus_schedules(action, main_content_frame):
    global route, bus_class, search_date, time_filter, time_am_pm, status_var, id_search_var, id_search_text
    status_var = tk.StringVar(value="All")

    def toggle_status():
        current_status = status_var.get()
        if current_status == "All":
            status_var.set("Active")
        elif current_status == "Active":
            status_var.set("Cancelled")
        else:
            status_var.set("All")
        filter_schedules()


    # Clear the main_content_frame
    for widget in main_content_frame.winfo_children():
        widget.destroy()

    # Code for button frame for managing bus schedule (serve as title holder)
    c_frame = ctk.CTkFrame(main_content_frame, corner_radius=0, fg_color=vin)
    c_frame.pack(fill="x")
    button_frame = ctk.CTkFrame(c_frame, corner_radius=0, fg_color=vin)
    button_frame.pack(fill="x")

    # Title
    title_label = ctk.CTkLabel(button_frame,text=" BUS SCHEDULE ",text_color=white,font=("Arial", 23, "bold"),corner_radius=0)
    title_label.pack(side="left", pady=(10, 10), padx=20)
    # Create Bus Schedule button
    Add = ctk.CTkButton(button_frame,text="Add",fg_color=white, text_color=vio, font=("Arial", 16,"bold"), command=lambda: create_schedule(db, tree), height=35)
    Add.pack(side="left", padx=5)
    set_hover_color(Add,hover_bg_color=purplr, hover_text_color=white, normal_bg_color=white, normal_text_color=vio )

    Cancel = ctk.CTkButton(button_frame,text="Cancel Trip",fg_color=white, text_color=vio, font=("Arial", 16,"bold"), command=lambda : send_notification_based_on_schedule(main_content_frame, db, tree), height=35)
    Cancel.pack(side="right", padx=20)
    set_hover_color(Cancel,hover_bg_color="#6EACDA", hover_text_color=vio, normal_bg_color=white, normal_text_color=vio )

    # Add Status Toggle Button
    status_button = ctk.CTkButton( button_frame, textvariable=status_var, command=toggle_status, fg_color=white, text_color=vio, font=("Arial", 16,"bold"), height=35)
    status_button.pack(side="right", padx=10)
    set_hover_color(status_button, hover_bg_color=purplr, hover_text_color=white, normal_bg_color=white, normal_text_color=vio )

    # Filter frame (to hold widgets that will filter data on Treeview table)
    filter_frame = ctk.CTkFrame(c_frame, corner_radius=0, fg_color=vin)
    filter_frame.pack(fill="x")  # Added vertical padding for better spacing
    # Variables for dropdown objects
    for i in range(7):
        filter_frame.columnconfigure(i, weight=1)

    route_var = tk.StringVar(value="All")
    bus_class_var = tk.StringVar(value="All")
    # === NEW VARIABLES FOR TIME FILTER ===
    time_am_pm_var = tk.StringVar(value="AM")  # Default to AM

    
    # Function to filter schedules
    def filter_schedules(*args):
        global route, bus_class, search_date, time_filter, time_am_pm, status_var, id_search_text
        global count
        count = 1
        # Clear existing Treeview data
        for item in tree.get_children():
            tree.delete(item)

        # Get values from filter widgets
        route = route_var.get()
        bus_class = bus_class_var.get()
        search_date = date_entry.get().strip()
        id_search_text = id_search_entry.get().strip().upper()
        # === GET TIME FILTER VALUES ===
        time_hour = hour_entry.get().strip()
        time_minute = minute_entry.get().strip()
        time_am_pm = time_am_pm_var.get().strip().upper()  # Ensure uppercase
        # Initialize time filter string
        time_filter = ""
        # Input Validation
        try:
            if time_hour:
                hour_int = int(time_hour)
                if not 1 <= hour_int <= 12:
                    raise ValueError("Hour must be between 1 and 12.")
                if time_minute:
                    minute_int = int(time_minute)
                    if not 0 <= minute_int <= 59:
                        raise ValueError("Minute must be between 0 and 59.")
                    # Construct time_filter without leading zero for hour
                    time_filter = f"{hour_int}:{minute_int:02d} {time_am_pm}"
                else:
                    # Only hour and AM/PM are provided
                    time_filter = f"{hour_int}:"
        except ValueError as ve:
            # Show an error message to the user
            messagebox.showerror("Invalid Input", str(ve))
            return

        refresh_tree(db, tree)

    # Populate route dropdown
    routes = ['All']
    route_docs = db.collection('BusSchedule').stream()
    for doc in route_docs:
        route = doc.to_dict().get('route')
        if route and route not in routes:
            routes.append(route)

    # --- ROUTE Filter ---
    route_label = ctk.CTkLabel(filter_frame, text="ROUTE:", text_color=white)
    route_label.grid(row=0, column=0, padx=(25,0), pady=(5,0), sticky="w")
    route_dropdown = ctk.CTkComboBox(filter_frame, variable=route_var, values=routes, command=filter_schedules, width=150)
    route_dropdown.grid(row=1, column=0, padx=(20,0), pady=(0, 10), sticky="w")

    # --- BUS CLASS Filter ---
    bus_class_label = ctk.CTkLabel(filter_frame, text="BUS CLASS:", text_color=white)
    bus_class_label.grid(row=0, column=1, padx=10, pady=(5, 0), sticky="w")
    bus_class_dropdown = ctk.CTkComboBox(filter_frame, variable=bus_class_var, values=['All', 'AC', 'NAC'], command=filter_schedules, width=150)
    bus_class_dropdown.grid(row=1, column=1, padx=5, pady=(0, 10), sticky="w")

    # --- DATE Filter ---
    date_label = ctk.CTkLabel(filter_frame, text="DATE:", text_color=white)
    date_label.grid(row=0, column=2, padx=10, pady=(5, 0), sticky="w")
    date_entry = ctk.CTkEntry(filter_frame, placeholder_text="YYYY-MM-DD", width=150, text_color="#191970", placeholder_text_color="#6eacda")
    date_entry.grid(row=1, column=2, padx=5, pady=(0, 10), sticky="w")
    date_entry.bind("<Return>", filter_schedules)

    # --- TIME Filter ---
    time_label = ctk.CTkLabel(filter_frame, text="TIME:", text_color=white)
    time_label.grid(row=0, column=3, padx=10, pady=(5, 0), sticky="w")

    time_filter_frame = ctk.CTkFrame(filter_frame, fg_color=vin, corner_radius=5)
    time_filter_frame.grid(row=1, column=3, padx=5, pady=(0, 10), sticky="w")

    hour_entry = ctk.CTkEntry(time_filter_frame, placeholder_text="HH", width=50)
    hour_entry.grid(row=0, column=0, padx=(5, 0), pady=2)
    minute_entry = ctk.CTkEntry(time_filter_frame, placeholder_text="MM", width=50)
    minute_entry.grid(row=0, column=1, padx=2, pady=2)
    am_pm_dropdown = ctk.CTkComboBox(time_filter_frame, variable=time_am_pm_var, values=["AM", "PM"], width=60)
    am_pm_dropdown.grid(row=0, column=2, padx=2, pady=2)
    hour_entry.bind("<Return>", filter_schedules)
    minute_entry.bind("<Return>", filter_schedules)

    # --- SEARCH ID ---
    id_search_label = ctk.CTkLabel(filter_frame, text="ID SEARCH:", text_color=white)
    id_search_label.grid(row=0, column=4, padx=10, pady=(5, 0), sticky="w")
    id_search_entry = ctk.CTkEntry(filter_frame, textvariable=id_search_var, placeholder_text="Search Bus/Driver ID", text_color="#191970",placeholder_text_color="#6eacda")
    id_search_entry.grid(row=1, column=4, padx=5, pady=(0, 10), sticky="w")
    id_search_entry.bind("<Return>", filter_schedules)


    # --- DELETE and EDIT Buttons ---
    delete = ctk.CTkButton(filter_frame, text="Delete", command=lambda: delete_schedule(db, tree), fg_color=white, text_color=red, width=100, height=35,  font=("Arial", 16, "bold"))
    delete.grid(row=0, column=7, rowspan=2, padx=(10,20), pady=(25,10), sticky="e")
    edit = ctk.CTkButton(filter_frame, text="Edit", command=lambda: edit_schedule(db, tree), fg_color=white, text_color=vio, width=100, height=35,  font=("Arial", 16, "bold"))
    edit.grid(row=0, column=6, rowspan=2, padx=2, pady=(25,10), sticky="e")
    set_hover_color(delete, hover_bg_color=red, hover_text_color=white, normal_bg_color=white, normal_text_color=red)
    set_hover_color(edit, hover_bg_color=lightblue, hover_text_color=white, normal_bg_color=white, normal_text_color=vio)

    # Define columns and populate Treeview
    columns = ("No.", "Route", "Dep. Date", "Dep. Time", "Driver ID", "Bus ID", "Unit Type", "Class","Fare", "Schedule ID", "Status")
    tree_frame = ctk.CTkFrame(main_content_frame)
    tree_frame.pack(fill="both", expand=True)

    tree_scroll = tk.Scrollbar(tree_frame)
    tree_scroll.pack(side="right", fill="y")

    tree = ttk.Treeview(tree_frame, columns=columns, yscrollcommand=tree_scroll.set, show='headings')
    for col in columns:
        tree.heading(col, text=col)
        if col == 'No.':
            tree.column(col, width=40)
        elif col == "Dep. Date" or col == "Dep. Time":
            tree.column(col, minwidth=0, width=100)
        elif col == "Status"  :
            tree.column(col, minwidth=0, width=70, anchor="center")
        elif col == "Fare" :
            tree.column(col, minwidth=0, width=80)
        elif col == "Class"  :
            tree.column(col, minwidth=0, width=70, anchor="center")
        elif col == "Unit Type" :
            tree.column(col, minwidth=0, width=100)
        elif col == "Driver ID" :
            tree.column(col, minwidth=0, width=110)
        else:
            tree.column(col, minwidth=0, width=150)
    tree.pack(fill="both", expand=True)

    tree_scroll.config(command=tree.yview)
    # Set alternating row colors
    tree.tag_configure('oddrow', background=heavyrow)
    tree.tag_configure('evenrow', background=lightrow)
    tree.tag_configure('cancel', background="#cc3e40", foreground="#fff")
    # Bind double-click event to edit_schedule function
    tree.bind("<Double-1>", lambda e: view_layout(tree))
    # Initialize the Treeview with all schedules
    filter_schedules()


def show_loading_window():
    loading_window = tk.Toplevel()
    loading_window.geometry("300x100")
    loading_window.title("Sending Notifications")
    
    # Center the loading window
    screen_width = loading_window.winfo_screenwidth()
    screen_height = loading_window.winfo_screenheight()
    window_width = 300
    window_height = 100
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    loading_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    loading_label = tk.Label(loading_window, text="Processing Cancellation procedure, please wait...")
    loading_label.pack(expand=True, padx=10, pady=10)
        
    # Make loading window modal
    loading_window.update()
    return loading_window

def send_notification_based_on_schedule(main_content_frame, db, tree):
    selected_item = tree.selection()  # Get the selected row in the Treeview
    if selected_item:  # Ensure a row is selected
        item = tree.item(selected_item)
        values = item['values']
        schedule_id = values[9]  # Assume the 10th column contains Schedule ID
        part1, part2 = values[1].split('-')

        # Fetch the document for the selected schedule
        schedule_doc = db.collection('BusSchedule').document(schedule_id).get()
        if not schedule_doc.exists:
            messagebox.showerror("Error", "Selected schedule document not found.")
            return

        def send_process():
            try:
                schedule_ref = db.collection("BusSchedule").document(schedule_id)
                schedule_doc = schedule_ref.get()

                def update_ui(func, *args):
                    # This method schedules the GUI update on the main thread
                    main_content_frame.after(0, func, *args)

                if schedule_doc.exists:
                    seats = schedule_doc.get("seats")
                    if seats:
                        # Use a set to ensure unique user IDs
                        user_ids = {user_id for user_id in seats.values() if user_id not in ["Available", "Reserved"]}

                        if user_ids:
                            for user_id in user_ids:
                                # Send notification to each user
                                user_ref = db.collection("MobileUser").document(user_id)

                                user_doc = user_ref.get()
                                name = user_doc.get("first_name")

                                notification = {
                                 "title": f"Your Bus Trip has been Cancelled!!",
                                "category": "Trip Cancellation",

                                "body": f"""Dear {name},
 
    We regret to inform you that your scheduled bus trip on {values[2]} from {part1} to {part2}, with departure time at {values[3]}, has been cancelled due to unforeseen circumstances and operational issues.

Sched.ID: {schedule_id}

   We sincerely apologize for the inconvenience this may have caused and deeply appreciate your understanding during this time. Please rest assured that we are committed to appropriately compensating all affected passengers.

To process a refund or reschedule your trip, kindly contact us using the details provided below:

Email: support@company.com

Phone: +1-800-123-4567

Office Hours: Monday-Saturday, 9:00 AM-5:00 PM


Our team is standing by to assist you with your request.

    Once again, we apologize for the disruption to your plans and thank you for your patience. We value your trust and look forward to serving you better in the future.

Sincerely,
CERES.Corp.""",

                                "seen": False,
                                "timestamp": firestore.SERVER_TIMESTAMP  # Automatically sets the timestamp on creation
                                }



                                user_ref.collection("Notification").add(notification)

                                # Access user's "Purchase" subcollection
                                purchase_ref = user_ref.collection("Purchase")
                                purchases = purchase_ref.where("ScheduleID", "==", schedule_id).stream()
                                for purchase in purchases:
                                    purchase_id = purchase.id
                                    purchase_data = purchase.to_dict()

                                    # Update the status of the purchase
                                    purchase_ref.document(purchase_id).update({"status": "Cancelled"})

                                    # Fetch transactionID and TripID from the document
                                    transaction_id = purchase_data.get("transactionID")
                                    trip_id = purchase_data.get("TripID")

                                    # Update the corresponding documents in "Transaction" and "TripInfo"
                                    if transaction_id:
                                        db.collection("transactions").document(transaction_id).update({"status": "Cancelled"})
                                    if trip_id:
                                        db.collection("tripInfo").document(trip_id).update({"status": "Cancelled"})

                            update_ui(loading_window.destroy)
                            update_ui(messagebox.showinfo, "Success", "Notifications sent and statuses updated successfully.")
                        else:
                            update_ui(loading_window.destroy)
                            update_ui(messagebox.showwarning, "Warning", "No user IDs found in the seats map for this schedule.")
                    else:
                        update_ui(loading_window.destroy)
                        update_ui(messagebox.showwarning, "Warning", "No seats data found for this schedule.")
                else:
                    update_ui(loading_window.destroy)
                    update_ui(messagebox.showwarning, "Warning", f"Schedule ID {schedule_id} not found.")
            except Exception as e:
                def show_error():
                    loading_window.destroy()
                    messagebox.showerror("Error", f"An error occurred: {str(e)}")
                main_content_frame.after(0, show_error)

        # Save Button: Update schedule status to "Cancelled"
        def save_edited_schedule(db):   
            updated_data = {'status': "Cancelled"}
            db.collection('BusSchedule').document(schedule_id).update(updated_data)
            refresh_tree(db, tree)  # Refresh the Treeview contents

        # Show loading window
        loading_window = show_loading_window()

        # Run the sending process in a separate thread
        threading.Thread(target=send_process).start()
        save_edited_schedule(db)
    else:
        messagebox.showerror("ERROR", "No Schedule is selected.")





#function when add button is clicked
def create_schedule(db, tree):
    # Create a form window
    create_window = ctk.CTkToplevel()
    create_window.title("Create Schedule")
    create_window.lift()
    create_window.attributes("-topmost", True)
    create_window.configure(fg_color="#03346E")

    # Route dropdown
    ctk.CTkLabel(create_window, text="Route:", text_color="#E2E2B6").grid(row=0, column=0, padx=10, pady=5)
    route_var = ctk.StringVar()
    routes = db.collection('BusRoutes').where("status", "==", "Active").get()
    route_dropdown = ctk.CTkComboBox(create_window, variable=route_var, width=200, text_color="#191970")
    route_dropdown.configure(values=[route.id for route in routes])
    route_dropdown.grid(row=0, column=1, padx=10, pady=5)

    # Unit Type dropdown
    ctk.CTkLabel(create_window, text="Unit Type:", text_color="#E2E2B6").grid(row=1, column=0, padx=10, pady=5)
    unit_type_var = ctk.StringVar()
    unit_types = db.collection('Unit_type').get()
    unit_type_dropdown = ctk.CTkComboBox(create_window, variable=unit_type_var, width=200, text_color="#191970")
    unit_type_dropdown.configure(values=[unit.id for unit in unit_types])
    unit_type_dropdown.grid(row=1, column=1, padx=10, pady=5)

    # Bus Class dropdown
    ctk.CTkLabel(create_window, text="Bus Class:", text_color="#E2E2B6").grid(row=2, column=0, padx=10, pady=5)
    bus_class_var = ctk.StringVar()
    bus_class_dropdown = ctk.CTkComboBox(create_window, variable=bus_class_var, width=200, text_color="#191970")
    bus_class_dropdown.configure(values=["AC", "NAC"])
    bus_class_dropdown.grid(row=2, column=1, padx=10, pady=5)

    # Bus ID dropdown
    ctk.CTkLabel(create_window, text="Bus ID:", text_color="#E2E2B6").grid(row=3, column=0, padx=10, pady=5)
    bus_id_var = ctk.StringVar()
    bus_id_dropdown = ctk.CTkComboBox(create_window, variable=bus_id_var, width=200, text_color="#191970")
    bus_id_dropdown.grid(row=3, column=1, padx=10, pady=5)

    # Departure Date Entry
    ctk.CTkLabel(create_window, text="Departure Date:", text_color="#E2E2B6").grid(row=4, column=0, padx=10, pady=5)
    current_date = datetime.now().strftime("%Y-%m-%d")
    date_entry = ctk.CTkEntry(create_window, placeholder_text=current_date, width=200, text_color="#191970")
    date_entry.grid(row=4, column=1, padx=10, pady=5)

    # Departure Time Entry
    ctk.CTkLabel(create_window, text="Departure Time:", text_color="#E2E2B6").grid(row=5, column=0, padx=10, pady=5)
    
    hour_var = ctk.StringVar(value="1")
    minute_var = ctk.StringVar(value="00")
    am_pm_var = ctk.StringVar(value="AM")
    time_frame = ctk.CTkFrame(create_window, border_width=3, corner_radius=10, width=229)
    time_frame.grid(row=5, column=1)
    tk.Spinbox(time_frame, from_=1, to=12, textvariable=hour_var, width=3, bg="grey", font=("Arial", 12)).pack(side="left", padx=(5, 3), pady=5)
    tk.Spinbox(time_frame, from_=0, to=59, textvariable=minute_var, format="%02.0f", width=3, bg="grey", font=("Arial", 12)).pack(side="left", padx=(0, 3))
    ctk.CTkComboBox(time_frame, variable=am_pm_var, values=["AM", "PM"], width=95, height=23).pack(side="left", padx=(0, 5), pady=5)

    # Function to update Bus ID dropdown based on selected Route, Unit Type, and Bus Class
    def update_bus_id_dropdown(*args):
        selected_route = route_var.get()
        selected_unit_type = unit_type_var.get()
        selected_bus_class = bus_class_var.get()

        if selected_route and selected_unit_type and selected_bus_class:
            buses_query = db.collection('Buses').where('assigned_route', '==', selected_route) \
                .where('unit_type', '==', selected_unit_type).where('bus_class', '==', selected_bus_class).get()
            bus_ids = [bus.id for bus in buses_query]
            if bus_ids:
                bus_id_dropdown.configure(values=bus_ids)
                if bus_id_dropdown.get() not in bus_ids:
                    bus_id_dropdown.set('')
            else:
                bus_id_dropdown.configure(values=['No Buses Available'])
                bus_id_dropdown.set('No Buses Available')
        else:
            bus_id_dropdown.configure(values=[])
            bus_id_dropdown.set('')

    # Attach trace listeners to dropdowns
    route_var.trace_add('write', update_bus_id_dropdown)
    unit_type_var.trace_add('write', update_bus_id_dropdown)
    bus_class_var.trace_add('write', update_bus_id_dropdown)

    # Save Schedule function
    def save_schedule():
        selected_route = route_var.get()
        selected_unit_type = unit_type_var.get()
        selected_bus_class = bus_class_var.get()
        selected_bus_id = bus_id_var.get()
        departure_date = date_entry.get()
        departure_time = f"{hour_var.get()}:{minute_var.get()} {am_pm_var.get()}"

        if not all([selected_route, selected_unit_type, selected_bus_class, selected_bus_id, departure_date, departure_time]):
            messagebox.showerror("Error", "All fields are required.")
            return

        bus_data = db.collection('Buses').document(selected_bus_id).get().to_dict()
        fare_doc = db.collection('Fares').where('route', '==', selected_route).where('bus_unit_type', '==', selected_unit_type).where('bus_class', '==', selected_bus_class).get()
        if fare_doc:
            fare = fare_doc[0].to_dict().get('fare')
        else:
            # Display error message
            fare = 0.0
            messagebox.showerror("Error", "Fare data not found for the selected route and bus unit type.")
            return  # Stop further execution of the code

        # Check for existing schedule with the same departure time and driver
        existing_schedules = db.collection('BusSchedule').where('departure_time', '==', departure_time).where('driver', '==', bus_data.get('driver')).where('departure_date', '==',  departure_date).where('bus_id', '==', selected_bus_id).stream()

        if any(existing_schedules):
            messagebox.showerror("Error", "A similar schedule already exsists in the system.")
            return

        schedule_data = {
            'route': selected_route,
            'unit_type': selected_unit_type,
            'bus_class': selected_bus_class,
            'bus_id': selected_bus_id,
            'driver': bus_data.get('driver'),
            'driver_id': bus_data.get('driver_id'),
            'no_of_seats': bus_data.get('number_of_seats'),
            'seats': db.collection('Unit_type').document(selected_unit_type).get().to_dict().get('seats'),
            'fare': fare,
            'departure_date': departure_date,
            'departure_time': departure_time,
            'status': 'Active'
        }

        db.collection('BusSchedule').add(schedule_data)
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
        messagebox.showinfo("Success", "Schedule created successfully.")
        
    # Save button
    ctk.CTkButton(create_window, text="Save", command=save_schedule).grid(row=6, column=0, columnspan=2, pady=10)


def edit_schedule(db, tree):
    selected_item = tree.selection()  # Get the selected row in the Treeview
    if selected_item:  # Ensure a row is selected
        item = tree.item(selected_item)
        values = item['values']
        schedule_id = values[9]  # Assume first column contains Schedule ID
        
        # Fetch the document for the selected schedule
        schedule_doc = db.collection('BusSchedule').document(schedule_id).get()
        if not schedule_doc.exists:
            messagebox.showerror("Error", "Selected schedule document not found.")
            return
        
        schedule_data = schedule_doc.to_dict()

        # Create a form window
        edit_window = ctk.CTkToplevel()
        edit_window.title("Edit Schedule")
        edit_window.lift()
        edit_window.attributes("-topmost", True)
        edit_window.configure(fg_color="#03346E")

        # Route (Prefilled and Locked)
        ctk.CTkLabel(edit_window, text="Route:", text_color="#E2E2B6").grid(row=0, column=0, padx=10, pady=5)
        route_entry = ctk.CTkEntry(edit_window, width=200)
        route_entry.insert(0, schedule_data['route'])
        route_entry.configure(state="disabled")  # Lock the entry
        route_entry.grid(row=0, column=1, padx=10, pady=5)

        # Bus ID Dropdown
        ctk.CTkLabel(edit_window, text="Bus ID:", text_color="#E2E2B6").grid(row=1, column=0, padx=10, pady=5)
        bus_id_var = ctk.StringVar(value=schedule_data['bus_id'])
        bus_id_dropdown = ctk.CTkComboBox(edit_window, variable=bus_id_var, width=200)
        bus_query = db.collection('Buses').where('assigned_route', '==', schedule_data['route']).where(
            'unit_type', '==', schedule_data['unit_type']).where('bus_class', '==', schedule_data['bus_class']
        ).stream()
        bus_ids = [doc.id for doc in bus_query]
        bus_id_dropdown.configure(values=bus_ids)
        bus_id_dropdown.grid(row=1, column=1, padx=10, pady=5)

        # Driver ID (Prefilled and Dynamic Update)
        ctk.CTkLabel(edit_window, text="Driver ID:", text_color="#E2E2B6").grid(row=2, column=0, padx=10, pady=5)
        driver_id_var = ctk.StringVar(value=schedule_data.get('driver_id', "Not Available"))
        driver_id_entry = ctk.CTkEntry(edit_window, textvariable=driver_id_var, width=200)
        driver_id_entry.grid(row=2, column=1, padx=10, pady=5)


        def update_driver_id(*args):
            selected_bus_id = bus_id_var.get()
            if selected_bus_id:
                bus_doc = db.collection('Buses').document(selected_bus_id).get()
                if bus_doc.exists:
                    driver_id_var.set(bus_doc.to_dict().get('driver_id', ''))

        bus_id_var.trace_add('write', update_driver_id)

        # Departure Date
        ctk.CTkLabel(edit_window, text="Departure Date:", text_color="#E2E2B6").grid(row=3, column=0, padx=10, pady=5)
        departure_date_entry = ctk.CTkEntry(edit_window, width=200)
        departure_date_entry.insert(0, schedule_data['departure_date'])
        departure_date_entry.grid(row=3, column=1, padx=10, pady=5)

        # Departure Time
        # Add labels and spinboxes for time input
        ctk.CTkLabel(edit_window, text="Departure Time:", text_color="#E2E2B6").grid(row=4, column=0, padx=10, pady=5)

        # Split the string into two parts based on the space
        time_parts = schedule_data['departure_time'].split(" ")
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

        # Status
        ctk.CTkLabel(edit_window, text="Status:", text_color="#E2E2B6").grid(row=5, column=0, padx=10, pady=5)

        # Dropdown for status
        status_options = ["Active", "Cancelled", "Hold"]  # Predefined options
        status_var = ctk.StringVar(value=schedule_data['status'])  # Set initial value from schedule_data
        status_dropdown = ctk.CTkComboBox(edit_window, values=status_options, variable=status_var, width=200)
        status_dropdown.grid(row=5, column=1, padx=10, pady=5)

        # Save Button
        def save_edited_schedule():
            departure_time_entry = f"{hour_var.get()}:{minute_var.get()} {am_pm_var.get()}"

            if not all([status_var,  bus_id_var.get(), driver_id_var.get(), departure_date_entry.get(), departure_time_entry]):
                messagebox.showerror("Error", "All fields are required.")
                return

            # Check if a schedule with the same departure time and driver already exists
            existing_schedules = db.collection('BusSchedule').where('departure_date', '==', departure_date_entry.get()).where('departure_time', '==', departure_time_entry).where('driver_id', '==', driver_id_var.get()).stream()

             # Filter out documents with the same name as `idname`
            filtered_schedules = [sched for sched in existing_schedules if sched.id != schedule_id]

            if any(filtered_schedules) :   # If such a schedule exists
                messagebox.showerror("Error", "A schedule with the same departure time and driver already exists.")
                return
            
            
            
            #Fetch driver's full name
            driver_doc = db.collection('Drivers').document(driver_id_var.get()).get()
            if driver_doc.exists:
                driver_info = driver_doc.to_dict()
                driver = f"{driver_info['first_name']} {driver_info['last_name']}"

            updated_data = {
                'route' : schedule_data['route'],
                'bus_id': bus_id_var.get(),
                'driver_id': driver_id_var.get(),
                'driver':driver,
                'departure_date': departure_date_entry.get(),
                'departure_time': departure_time_entry,
                'status': status_var.get(),
            }
            db.collection('BusSchedule').document(schedule_id).update(updated_data)

            if status_var.get() == "Cancelled":
                send_notification_based_on_schedule(edit_window, db, tree)

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
            select_item_by_values(updated_data['route'], updated_data['departure_date'], updated_data['departure_time'], updated_data['driver_id'])
            edit_window.destroy()
            messagebox.showinfo("Success", "Bus schedule updated successfully.")

        save_button = ctk.CTkButton(edit_window, text="Save", command=save_edited_schedule)
        save_button.grid(row=6, column=0, columnspan=2, pady=10)

    else:  # If no selected rows, show error message
        messagebox.showerror("ERROR", "No Schedule is selected.")

        
def delete_schedule(db, tree):
    global count
    selected_item = tree.selection()  # fetch selected row in table
    if selected_item:  # check if there is a selected row
        
        # Confirm before deleting
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this schedule?")
        if confirm:
            item = tree.item(selected_item)
            values = item['values']
            driver = values[4]
            departure_time = values[3]
            departure_date = values[2]
            route = values[1]

            # Revert to using chained 'where' clauses
            sched = db.collection('BusSchedule').where('driver', '==', driver).where('departure_date', '==', departure_date).where('departure_time', '==', departure_time).where('route', '==', route).get()
            print(f"This is Deleted : {sched}")
            for doc in sched:
                doc.reference.delete()

            refresh_tree(db, tree)
            messagebox.showinfo("Success", "Bus schedule deleted successfully.")
        else:  # if not, return
            return
    else:  # if no selected rows show error message
        messagebox.showerror("ERROR", "No schedule is selected.")

#function to refresh the treeveiw
def refresh_tree(db, tree):
    global route, bus_class, search_date, time_filter, time_am_pm, status_var, id_search_text

    schedules = db.collection('BusSchedule').stream()  # Fetch all documents from the BusSchedule collectio
    # Clear the current items in the treeview
    for item in tree.get_children():
        tree.delete(item)
    count = 1  # Reset the counter

    for sched in schedules:
        data = sched.to_dict()
        departure_date = data.get('departure_date', '').strip()
        departure_time = data.get('departure_time', '').strip().upper()  # Normalize to uppercase
        status = data.get('status', '').strip()  # Retrieve the status field
        bus_id = data.get('bus_id', '').strip()
        driver_id = data.get('driver_id', '').strip()
            
        # === APPLY FILTERS ===
        # Route filter
        route_match = (route == "All" or data.get('route', '') == route)
        # Bus class filter
        bus_class_match = (bus_class == "All" or data.get('bus_class', '') == bus_class)
        # Date filter
        date_match = departure_date.startswith(search_date) if search_date else True
        #status filter
        status_match = (status_var.get() == "All" or status == status_var.get())
        #ID filter
        id_search_match = (not id_search_text or id_search_text in bus_id or id_search_text in driver_id)

        # Time filter
        if time_filter:
            if ':' in time_filter and not time_filter.endswith(':'):
                # Both hour and minute are provided; exact match
                time_match = departure_time == time_filter
            elif time_filter.endswith(':'):
                # Only hour and AM/PM are provided; match start and end
                time_match = departure_time.startswith(time_filter) and departure_time.endswith(time_am_pm)
            else:
                time_match = True  # If time_filter is not properly formatted
        else:
            time_match = True  # No time filter applied

        # Final filter condition
        if route_match and bus_class_match and date_match and time_match and status_match and id_search_match:
            # Determine row tag based on status
            if status == "Cancelled":
                row_tag = "cancel"
            else:
                row_tag = "oddrow" if count % 2 == 0 else "evenrow"
        
            tree.insert( "", "end",
                values=(
                    count,
                    data.get('route', 'Not available'),                        
                    data.get('departure_date', ''),
                    data.get('departure_time', 'Not specified'),
                    data.get('driver_id', 'Not available'),
                    data.get('bus_id', 'N/A'),
                    data.get('unit_type', 'N/A'),
                    data.get('bus_class', 'N/A'),
                    f"₱. {data.get('fare', 'N/A')}",
                    sched.id, 
                    data.get('status', 'N/A')),
                tags=(row_tag,)
                )
            count += 1



def view_layout(treeview):
    selected_item = treeview.selection()

    if not selected_item:
        messagebox.showwarning("Selection Error", "Please select a unit type from the list.")
        return

    item = treeview.item(selected_item)
    values = item['values']
    bus_id = values[9]
    create_seat_selection_window(bus_id)


def create_seat_selection_window(bus_id):
    root = tk.Toplevel()
    root.title("View Seat Layout")
    root.config(background="#E2E2B6")

    def fetch_seat_data(bus_id):
        try:
            unit_type_ref = db.collection('BusSchedule').document(bus_id)
            unit_type_doc = unit_type_ref.get()
            if unit_type_doc.exists:
                return unit_type_doc.to_dict().get('seats', {})
            else:
                print("No such document!")
                return {}
        except Exception as e:
            print(f"Error fetching data: {e}")
            return {}

    def open_seat_info_window(seat_data):
        """ Opens a new window to display seat information with fixed dimensions and scrollable content. """
        info_window = tk.Toplevel()
        info_window.title("Seat Info")
        info_window.geometry("325x400")  # Fixed width and height
        info_window.resizable(False, False)  # Disable resizing

        # Create a canvas widget
        canvas = tk.Canvas(info_window, bg="#FFF", width=300, height=400)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create a vertical scrollbar linked to the canvas
        scrollbar = tk.Scrollbar(info_window, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Link the scrollbar with the canvas
        canvas.config(yscrollcommand=scrollbar.set)

        # Frame inside the canvas for content
        content_frame = tk.Frame(canvas, bg="#FFF")
        canvas.create_window((0, 0), window=content_frame, anchor="nw")

        # Function to sort seat IDs
        def sort_seat_ids(seat_data):
            sorted_seats = sorted(seat_data.items(), key=lambda x: (int(x[0][:-1]), x[0][-1]))
            return sorted_seats

        # Sort the seat data
        sorted_seat_data = sort_seat_ids(seat_data)

        # Populate the content frame with sorted seat data
        row = 0
        for seat_id, seat_info in sorted_seat_data:
            tk.Label(content_frame, text=f"{seat_id}:", bg="#FFF", font=("Arial", 12, "bold")).grid(
            row=row, column=0, sticky="w", padx=10, pady=5
            )
            tk.Label(content_frame, text=f"{seat_info}", bg="#FFF", font=("Arial", 12)).grid(
                row=row, column=1, sticky="w", padx=10, pady=5
            )
            row += 1

        # Update the scrollable region of the canvas
        content_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

        # Bind mouse wheel to canvas to enable scrolling with the wheel
        def on_mouse_wheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        canvas.bind_all("<MouseWheel>", on_mouse_wheel)  # For Windows
        # For MacOS, use the following line instead of above:
        # canvas.bind_all("<Button-4>", on_mouse_wheel)  # For MacOS

        info_window.mainloop()

    seat_buttons = {}
    seat_status = fetch_seat_data(bus_id)

    # Determine the grid size based on the seat data
    max_row = 0
    max_col = 0
    for seat_id in seat_status.keys():
        row = int(seat_id[:-1])  # Extract row number from seat ID
        col = ord(seat_id[-1]) - ord('A')  # Extract column letter from seat ID
        max_row = max(max_row, row)
        max_col = max(max_col, col)

    # Create buttons only for existing seats in the seat map
    for seat_id, status in seat_status.items():
        row = int(seat_id[:-1]) - 1  # Convert to zero-based index
        col = ord(seat_id[-1]) - ord('A')  # Convert letter to index

        # Create the button and configure it
        button = tk.Button(root, text=seat_id, width=5, height=2)
        seat_buttons[seat_id] = button

        if status != 'Available':
            button.config(state=tk.DISABLED, bg='red')  # Reserved seats are disabled
        elif status == 'Reserved':
            button.config(state=tk.DISABLED, bg='red')  # Reserved seats are disabled
        else:
            button.config( bg="#03346E")  # Available seats

        button.grid(row=row, column=col, padx=5, pady=5)

    # Add the "More Info" button
    more_info_button = tk.Button(root, text="More Info", command=lambda: open_seat_info_window(seat_status), bg="#008CBA", fg="#FFF")
    more_info_button.grid(row=max_row + 1, column=0, columnspan=max_col + 1, pady=10)

    root.mainloop()
