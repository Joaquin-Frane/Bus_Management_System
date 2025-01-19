#imports for the GUi (custom tkinter), treeview table(ttk), and database connection
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from firebase_config import db
from tkcalendar import DateEntry
from datetime import datetime, timedelta
from forHover import set_hover_color

count = 1
heavyrow = "#ADBBDA"
lightrow = "#EDE8F5"
vio = "#191970"
white = "white"
purplr ="#9747FF"
red ="#FF3737"
lightblue ="#4682B4"
vin="#03346E"

def manage_transactions(action, main_content_frame):
    for widget in main_content_frame.winfo_children():
        widget.destroy()

    c_frame = ctk.CTkFrame(main_content_frame, corner_radius=0, fg_color=vin)
    c_frame.pack(fill="x")

    button_frame = ctk.CTkFrame(c_frame, corner_radius=0, fg_color=vin)
    button_frame.pack(fill="x")
    title_label = ctk.CTkLabel(button_frame, text="Manage Transactions", text_color=white, font=("Arial", 23, "bold"))
    title_label.pack(side="left", padx=(20,10), pady=(10,10))

    filter_frame = ctk.CTkFrame(c_frame, corner_radius=0, fg_color=vin)
    filter_frame.pack(fill="x")
    filter_frame.grid_columnconfigure(tuple(range(7)), weight=1)

    view_button = ctk.CTkButton(filter_frame, text="View Full Data", fg_color=white, text_color=vio, height=70, font=("Arial", 23, "bold"), command=lambda: view_full_data(treeview), hover_color="#6eacda")
    view_button.grid(row=0, column=7, rowspan=2, padx=(10,20), pady=10, sticky="e")

    mode_label = ctk.CTkLabel(filter_frame, text="Mode:", text_color=white)
    mode_label.grid(row=0, column=0, padx=(20,10), pady=(5, 0), sticky="w")

    mode_values = ["ALL", "CASH", "GCASH"]
    mode_var = ctk.StringVar(value="ALL")
    mode_dropdown = ctk.CTkComboBox(filter_frame, values=mode_values, variable=mode_var)
    mode_dropdown.grid(row=1, column=0, padx=(25,10), pady=(0, 10), sticky="w")

    route_label = ctk.CTkLabel(filter_frame, text="Route:", text_color=white)
    route_label.grid(row=0, column=1, padx=10, pady=(5, 0), sticky="w")

    route_var = ctk.StringVar(value="ALL")
    route_dropdown = ctk.CTkComboBox(filter_frame, variable=route_var)
    route_dropdown.grid(row=1, column=1, padx=5, pady=(0, 10), sticky="w")
    fetch_routes(route_dropdown)

    date_label = ctk.CTkLabel(filter_frame, text="Date Search:", text_color=white)
    date_label.grid(row=0, column=2, columnspan=2, padx=10, pady=(5, 0), sticky="w")

    date_frame = ctk.CTkFrame(filter_frame, fg_color=vin)
    date_frame.grid(row=1, column=2, padx=5, pady=(0, 10), sticky="w")

    year_entry = ctk.CTkEntry(date_frame, placeholder_text="Year", width=60)
    year_entry.grid(row=0, column=0, padx=2, pady=5, sticky="w")

    month_entry = ctk.CTkEntry(date_frame, placeholder_text="Month", width=40)
    month_entry.grid(row=0, column=1, padx=2, pady=5, sticky="w")

    day_entry = ctk.CTkEntry(date_frame, placeholder_text="Day", width=40)
    day_entry.grid(row=0, column=2, padx=2, pady=5, sticky="w")

    update_button = ctk.CTkButton(date_frame, text="Update", fg_color=white, text_color=vio, hover_color="#6eacda",
                                   command=lambda: fetch_transactions(treeview, mode_var.get(), route_var.get(), 
                                                                      year_entry.get(), month_entry.get(), day_entry.get(), 
                                                                      transactionID_entry.get()))
    update_button.grid(row=0, column=3, padx=2, pady=5, sticky="w")

    tnr_label = ctk.CTkLabel(filter_frame, text="TNR ID Search:", text_color=white)
    tnr_label.grid(row=0, column=4, padx=10, pady=(5, 0), sticky="w")
    transactionID_entry = ctk.CTkEntry(filter_frame, placeholder_text="Transaction ID", width=200, placeholder_text_color="#6eacda", text_color="#191970")
    transactionID_entry.grid(row=1, column=4, padx=0, pady=(0,10), sticky="w")
    transactionID_entry.bind('<Return>', lambda e: fetch_transactions(treeview, mode_var.get(), route_var.get(), 
                                                                      year_entry.get(), month_entry.get(), day_entry.get(), 
                                                                      transactionID_entry.get()))

    treeview_frame = ctk.CTkFrame(main_content_frame, corner_radius=0)
    treeview_frame.pack(fill="both", expand=True)

    columns = ("No.", "TRN ID", "Trip ID", "Mode", "Route", "TRN Date", "Discount", "Price")

    #scroll bar
    tree_scroll = tk.Scrollbar(treeview_frame)
    tree_scroll.pack(side="right",fill="y")# position of scrollbar

    treeview = ttk.Treeview(treeview_frame, columns=columns, yscrollcommand=tree_scroll.set, show="headings", height=10)

    for col in columns:
        treeview.heading(col, text=col.capitalize().replace("_", " "))
        treeview.column(col, width=100, anchor="center")
    treeview.pack(fill="both", expand=True)

    #configure scroll bar
    tree_scroll.config(command=treeview.yview)

    treeview.tag_configure('oddrow', background=heavyrow)
    treeview.tag_configure('evenrow', background=lightrow)

    fetch_transactions(treeview, mode="ALL", route="ALL")

    mode_var.trace_add('write', lambda *args: fetch_transactions(treeview, mode_var.get(), route_var.get()))
    route_var.trace_add('write', lambda *args: fetch_transactions(treeview, mode_var.get(), route_var.get()))



def fetch_transactions(treeview, mode, route, year=None, month=None, day=None, transactionID=None):
    # Clear the Treeview
    for row in treeview.get_children():
        treeview.delete(row)
    
    # Firebase query to fetch transactions
    query = db.collection('transactions')

    # Apply filters if not "ALL"
    if mode != "ALL":  
        query = query.where('mode', '==', mode)
    if route != "ALL":  
        query = query.where('route', '==', route)

    # Filter by specific date if year, month, and day are provided
    if year and month and day:
        try:
            # Set up the current date and next day for the date range
            current_date = datetime(int(year), int(month), int(day), 0, 0, 0)  # start of the day
            next_day = current_date + timedelta(days=1)  # start of the next day
            
            # Convert to UTC timestamps if needed (depends on Firestore setup)
            print(f"Filtering from: {current_date} to {next_day}")
            query = query.where('transaction_date', '>=', current_date)
            query = query.where('transaction_date', '<', next_day)
        
        except ValueError as e:
            print(f"Error with date filtering: {e}")

    # Filter by transaction ID if provided
    if transactionID:
        query = query.where('transactionID', '==', transactionID)

    query_results = query.stream()

    # Loop through the query results and insert them into the Treeview
    for count, doc in enumerate(query_results, start=1):
        data = doc.to_dict()
        row_tags = 'oddrow' if count % 2 == 0 else 'evenrow'

        # Handle transaction_date formatting
        try:
            transaction_date = data.get('transaction_date', 'N/A')
            # Attempt to convert the transaction date to a string if it’s a timestamp
            if isinstance(transaction_date, datetime):
                transaction_date_str = transaction_date.strftime('%Y-%m-%d')
            else:
                raise TypeError("Invalid date format")  # Trigger exception for invalid type
        except (TypeError, AttributeError):
            transaction_date_str = "Invalid Date Format"

        treeview.insert("", "end", values=(
            count, 
            data.get('transactionID', 'N/A'), 
            data.get('TripID', 'N/A'), 
            data.get('mode', 'N/A'), 
            data.get('route', 'N/A'),
            transaction_date_str,
            data.get('discount', 'N/A'), 
            data.get('price', 'N/A')
        ), tags=(row_tags,))


def fetch_routes(route_dropdown):
    routes_query = db.collection('BusRoutes').stream()
    routes = ["ALL"] + [doc.id for doc in routes_query]
    route_dropdown.configure(values=routes)




def view_full_data(treeview):
    # Get the selected item from the Treeview
    selected_item = treeview.focus()
    if not selected_item:
        messagebox.showwarning("Warning", "Please select a transaction to view.")
        return

    # Get the values of the selected row
    selected_values = treeview.item(selected_item, 'values')
    transaction_id = selected_values[1]  # Assuming the TRN ID is the second column
    trip_id = selected_values[2]         # Assuming the Trip ID is the third column

    # Create a new window to display the full data
    full_data_window = ctk.CTkToplevel()
    full_data_window.title(f"Full Data for Transaction {transaction_id}")
    full_data_window.geometry("650x400")
    full_data_window.configure(fg_color="#021526")

    # Main frame to hold the side-by-side frames
    main_frame = ctk.CTkFrame(full_data_window, corner_radius=10, fg_color="#021526")
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    main_frame.columnconfigure(tuple(range(2)), weight=1)

    # Left frame for transaction data
    transaction_frame = ctk.CTkFrame(main_frame, corner_radius=10, fg_color="#e0e0e0")
    transaction_frame.grid(row=0, column=0, padx=10, pady=(10,5), sticky="nsew")

    # Right frame for trip info data
    trip_info_frame = ctk.CTkFrame(main_frame, corner_radius=10, fg_color="#e0e0e0")
    trip_info_frame.grid(row=0, column=1, padx=10, pady=(10,5), sticky="nsew")

    # Configure the grid to adjust properly
    main_frame.columnconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=1)
    main_frame.rowconfigure(0, weight=1)

    # Fetch the selected transaction document from Firebase (Transaction collection)
    transaction_doc = db.collection('transactions').document(transaction_id).get()

    if transaction_doc.exists:
        data = transaction_doc.to_dict()

        # Fields to fetch and their corresponding labels for transactions
        transaction_fields = {
            'transactionID': "ID",
            'route': "Route",
            'discount': "Discount",
            'price': "Price",
            'mode': "Mode of Payment",
            'transaction_date': "TRN Date",
            'status': "Status"
        }

        # Transaction details (in the left frame)
        transaction_title = ctk.CTkLabel(transaction_frame, text="Transaction Data", font=("Arial", 16, "bold"), text_color="#191970")
        transaction_title.pack(anchor="w", padx=10, pady=5)

        for field, label_text in transaction_fields.items():
            value = data.get(field, 'N/A')  # Fetch field value or use 'N/A' if it doesn't exist
            label = ctk.CTkLabel(transaction_frame, text=f"   {label_text}:    {value}", text_color="#191970")
            label.pack(anchor="w", padx=10, pady=2)

    else:
        messagebox.showerror("Error", f"No transaction data found for {transaction_id}")

    # Fetch the related Trip Info document based on TripID (TripInfo collection)
    trip_info_doc = db.collection('tripInfo').document(trip_id).get()

    if trip_info_doc.exists:
        trip_data = trip_info_doc.to_dict()

        # Fields to fetch and their corresponding labels for trip info
        trip_info_fields = {
            'TripID': "Trip ID",
            'route': "Route",
            'class': "Class",
            'bus_id': "Bus ID",
            'bus_seat': "Bus Seat",
            'departure_date': "Departure Date",
            'departure_time': "Departure Time"
        }

        # Trip Info details (in the right frame)
        trip_title = ctk.CTkLabel(trip_info_frame, text="Trip Information", font=("Arial", 16, "bold"), text_color="#191970")
        trip_title.pack(anchor="w", padx=10, pady=5)

        for field, label_text in trip_info_fields.items():
            value = trip_data.get(field, 'N/A')  # Fetch field value or use 'N/A' if it doesn't exist
            trip_label = ctk.CTkLabel(trip_info_frame, text=f"   {label_text}: {value}", text_color="#191970")
            trip_label.pack(anchor="w", padx=10, pady=2)

    else:
        messagebox.showerror("Error", f"No trip information found for {trip_id}")

    # Add Exit and Edit Trip Info buttons at the bottom
    button_frame = ctk.CTkFrame(full_data_window, fg_color="#021526")
    button_frame.pack(pady=5)

    # Exit Button
    exit_button = ctk.CTkButton(button_frame, text="Exit", command=full_data_window.destroy, fg_color="#6eacda", text_color="#191970", hover_color="#F95454")
    exit_button.pack(side="left", padx=10)

    # Edit Trip Info Button
    edit_trip_button = ctk.CTkButton(button_frame, text="Edit Trip Info", command=lambda: edit_trip_info(trip_id, full_data_window), fg_color="#6eacda", text_color="#191970", hover_color="#e2e2b6")
    edit_trip_button.pack(side="left", padx=10)





def edit_trip_info(trip_id, full_data_window ):

    full_data_window.destroy()
    # Create a new window for editing Trip Info
    edit_window = ctk.CTkToplevel()
    edit_window.title(f"Edit Trip Info for TripID: {trip_id}")
    edit_window.geometry("550x320")
    edit_window.configure(fg_color="#021526")

    

    # Fetch the TripInfo document from Firebase
    trip_info_doc = db.collection('tripInfo').document(trip_id).get()

    if not trip_info_doc.exists:
        messagebox.showerror("Error", f"No trip information found for {trip_id}")
        edit_window.destroy()
        return

    trip_data = trip_info_doc.to_dict()

    # Create a frame to hold the entry fields
    entry_frame = ctk.CTkFrame(edit_window, fg_color="#03346E")
    entry_frame.pack(fill="both", expand=True, padx=10, pady=10)

    entry_frame.columnconfigure(tuple(range(3)), weight=1)

    # Route Entry (disabled)
    route_label = ctk.CTkLabel(entry_frame, text="Route", anchor="w", text_color="#fff")
    route_label.grid(row=0, column=0, padx=10, pady=(15,5), sticky="e")
    
    route_entry = ctk.CTkEntry(entry_frame, text_color="#191970")
    route_entry.insert(0, trip_data.get('route', ''))
    route_entry.configure(state="disabled")  # Disable the route entry
    route_entry.grid(row=0, column=1, padx=10, pady=(15,5), sticky="w")

    # Class Entry (disabled after fetching value)
    class_label = ctk.CTkLabel(entry_frame, text="Class", anchor="w", text_color="#fff")
    class_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")
    
    class_entry = ctk.CTkEntry(entry_frame, text_color="#191970")
    class_entry.insert(0, trip_data.get('class', ''))  # Fetch the class from Firestore
    class_entry.configure(state="disabled")  # Disable after fetching value
    class_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")

    # Date Entry for departure_date
    date_label = ctk.CTkLabel(entry_frame, text="Departure Date", anchor="w", text_color="#fff")
    date_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")
    
    date_entry = ctk.CTkEntry(entry_frame, text_color="#191970")
    date_entry.insert(0, trip_data.get('departure_date', ''))  # Pre-fill with existing date
    date_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")

    # Seat Number Entry and Select Seat Button
    seat_label = ctk.CTkLabel(entry_frame, text="Seat No", anchor="w", text_color="#fff")
    seat_label.grid(row=3, column=0, padx=10, pady=5, sticky="e")
    
    seat_no_entry = ctk.CTkEntry(entry_frame, text_color="#191970")
    seat_no_entry.insert(0, trip_data.get('bus_seat', ''))  # Pre-fill with the existing seat number
    seat_no_entry.grid(row=3, column=1, padx=(10,0), pady=5, sticky="w")

    oldseat = trip_data.get('bus_seat', '')
    
    select_seat_button = ctk.CTkButton(entry_frame, text="Select Seat", command=lambda: create_seat_selection_window(schedule_dropdown.get(), route_entry.get(), seat_no_entry, date_entry.get()), fg_color="#e2e2b6", text_color="#191970", hover_color="#4682B4")
    select_seat_button.grid(row=3, column=2, padx=0, pady=5, sticky="w")

    # Schedule Time Dropdown (fetch from BusSchedule collection)
    schedule_label = ctk.CTkLabel(entry_frame, text="Schedule Time", anchor="w", text_color="#fff")
    schedule_label.grid(row=4, column=0, padx=10, pady=5, sticky="e")
    
    schedule_dropdown = ctk.CTkComboBox(entry_frame, values=[], text_color="#191970")
    schedule_dropdown.grid(row=4, column=1, padx=10, pady=5, sticky="w")

    # Status Dropdown with values "Active" and "Refunded"
    status_label = ctk.CTkLabel(entry_frame, text="Status", anchor="w", text_color="#fff")
    status_label.grid(row=5, column=0, padx=10, pady=5, sticky="e")

    status_dropdown = ctk.CTkComboBox(entry_frame, values=["Active", "Refunded"], text_color="#191970")
    status_dropdown.set(trip_data.get('status', 'Active'))  # Pre-fill with existing status or default to 'Active'
    status_dropdown.grid(row=5, column=1, padx=10, pady=5, sticky="w")

    
    # Function to fetch schedule times based on Route, Class, and Departure Date
    def update_schedule_times():
        selected_route = route_entry.get()
        selected_class = class_entry.get()  # Use the class from the entry
        selected_date = date_entry.get()

        print(f"{selected_route},  {selected_class},  {selected_date}")

        # Fetch schedule times from BusSchedule collection based on the filters
        query = db.collection('BusSchedule').where('route', '==', selected_route).where('bus_class', '==', selected_class).where('departure_date', '==', selected_date)
        docs = query.stream()
        schedule_times = [doc.get('departure_time') for doc in docs]
        
        # Update the dropdown values
        schedule_dropdown.configure(values=schedule_times)
        if schedule_times:
            schedule_dropdown.set(schedule_times[0])  # Set first available time by default

    # Bind date entry to trigger schedule fetch
    update_schedule_times()
    date_entry.bind("<FocusOut>", lambda e: update_schedule_times())  # Trigger when date is selected
    date_entry.bind("<Return>", lambda e: update_schedule_times())

    button_frame =ctk.CTkFrame(edit_window,fg_color="#021526")
    button_frame.pack(pady=(5, 20))

    # Update button to save changes to Firestore
    update_button = ctk.CTkButton(button_frame, text="Update", command=lambda: update_trip_info(trip_id, status_dropdown, date_entry, schedule_dropdown, seat_no_entry, route_entry, oldseat), text_color="#191970", fg_color="#fff", hover_color="#4682B4")
    update_button.pack(side="right", pady=5, padx=10)

    # Exit button to close the window without saving
    exit_button = ctk.CTkButton(button_frame, text="Exit", command=edit_window.destroy, text_color="#191970", fg_color="#FF8A8A", hover_color="#F95454")
    exit_button.pack(side="left", pady=5, padx=10)




def create_seat_selection_window(selected_schedule, route, seat_no_entry, date_entry):
    seat_window = tk.Toplevel()
    seat_window.title("Select Your Seat")
    seat_window.geometry("400x370")

    # Fetch seat data from BusSchedule collection using selected_schedule value
    def fetch_seat_data(selected_schedule, route, date_entry, seat_no_entry):
        print(date_entry)
        print(selected_schedule)
        print(seat_no_entry.get())
        try:
            schedules_ref = db.collection('BusSchedule')
            query = schedules_ref.where('route', '==', route).where('departure_time', '==', selected_schedule).where('departure_date', '==', date_entry).limit(1)
            results = query.stream()

            for doc in results:
                doc_id = doc.id  # Extract the document ID
                doc_ref = db.collection('BusSchedule').document(doc_id)
                seats ='seats'
                # Use dot notation to reference the field inside the map
                doc_ref.update({f"{seats}.{seat_no_entry.get()}": "Available"})
                print(f"{seat_no_entry.get()} is now available")
                return doc.to_dict().get('seats', {})
            print("No matching schedule found.")

            return {}
        except Exception as e:
            print(f"Error fetching data: {e}")
            return {}

    seat_buttons = {}
    seat_status = fetch_seat_data(selected_schedule, route, date_entry,seat_no_entry)  # Fetch seat status from Firestore
    selected_seat = None  # Track the selected seat

    # Determine the grid size
    max_row = 0
    max_col = 0
    for seat_id in seat_status.keys():
        row = int(seat_id[:-1])  # Extracting the row number
        col = ord(seat_id[-1]) - ord('A')  # Extracting the column number
        max_row = max(max_row, row)
        max_col = max(max_col, col)

    # Function to handle seat selection
    def reserve_seat(seat_id):
        nonlocal selected_seat  # Use nonlocal to refer to the selected_seat inside the outer function
        # Deselect previously selected seat (reset to blue)
        if selected_seat and seat_buttons[selected_seat].cget('bg') == '#4682B4':
            seat_buttons[selected_seat].configure(bg='#191970', fg="#fff")
    
        # Select the new seat (set to red)
        selected_seat = seat_id
        seat_buttons[selected_seat].configure(bg='#4682B4')
        print(f"Selected seat: {selected_seat}")

    # Create buttons for each seat
    for seat_id, status in seat_status.items():
        row = int(seat_id[:-1]) - 1  # Convert to zero-based index
        col = ord(seat_id[-1]) - ord('A')  # Convert letter to index
        
        button = tk.Button(seat_window, text=seat_id, width=5, height=2, bg='#191970', fg="#fff")

        # Disable reserved seats
        if status == 'Reserved':
            button.configure(state=tk.DISABLED, bg='grey')  # Reserved seats
        else:
            button.configure(command=lambda s=seat_id: reserve_seat(s))  # Available seats

        button.grid(row=row, column=col, padx=5, pady=5)
        seat_buttons[seat_id] = button

    # Function to confirm the seat selection
    def confirm_selection():
        if selected_seat:
            print(f"Confirmed seat: {selected_seat}")
            seat_no_entry.delete(0, tk.END)
            seat_no_entry.insert(0, selected_seat)
            seat_window.destroy()
        else:
            print("No seat selected.")
            messagebox.showwarning("No Seat", "Please select a seat before confirming.")

    # Confirm button to finalize seat selection
    select_button = tk.Button(seat_window, text="Select", command=confirm_selection, width=10, bg="#4682B4" )
    select_button.grid(row=max_row + 1, columnspan=max_col + 1, pady=10)

    seat_window.mainloop()


def update_trip_info(trip_id, status_dropdown, date_entry, schedule_dropdown, seat_no_entry, route, oldseat):
    if status_dropdown.get() == 'Refunded':
        try:
            query = db.collection('transactions').where('TripID', '==', trip_id).limit(1)
            results = query.stream()
            for doc in results:
                doc_id = doc.id  # Extract the document ID
                doc_ref = db.collection('transactions').document(doc_id)
            
                doc_ref.update({
                    'price': 0.0,
                    'status': 'Refunded'
                })

                try:
                    query4 = db.collection('sales').where('transactionID', '==', doc_id).limit(1)
                    results4 = query4.stream()
                    for doc in results4:
                        doc_id1 = doc.id  # Extract the document ID

                        doc_ref = db.collection('sales').document(doc_id1)
                        doc_ref.update({"price":0.0, "status":'Refunded'})
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to update trip info@@@: {e}")

            try:    
                schedules_ref1 = db.collection('BusSchedule')
                query2 = schedules_ref1.where('route', '==', route.get()).where('departure_time', '==', schedule_dropdown.get()).where('departure_date', '==', date_entry.get()).limit(1)
                results2 = query2.stream()

                for doc in results2:
                    doc_id = doc.id  # Extract the document ID
                    doc_ref = db.collection('BusSchedule').document(doc_id)
                    seats='seats'

                    doc_ref.update({f"{seats}.{seat_no_entry.get()}": "Available"})
                    print(f"{seat_no_entry.get()} is now available")




            except Exception as e:
                messagebox.showerror("Error", f"Failed to update trip info !!!: {e}")

            updated_data = {
                #'status': "Refunded",
                'departure_date': date_entry.get(),
                'departure_time': schedule_dropdown.get(),
                'bus_seat': ""
            }

            try:
                db.collection('tripInfo').document(trip_id).update(updated_data)
                messagebox.showinfo("Success", "Trip info updated successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update trip info@@@: {e}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to update trip info###: {e}")
    
    else: 
        try:
            schedules_ref2 = db.collection('BusSchedule')
            query3 = schedules_ref2.where('route', '==', route.get()).where('departure_time', '==', schedule_dropdown.get()).where('departure_date', '==', date_entry.get()).limit(1)
            results3 = query3.stream()

            for doc in results3:
                doc_id = doc.id  # Extract the document ID
                doc_ref = db.collection('BusSchedule').document(doc_id)
                seats='seats'

                doc_ref.update({f"{seats}.{seat_no_entry.get()}": "Reserved"})
                print(f"{seat_no_entry.get()} is now Reserved")

                doc_ref.update({f"{seats}.{oldseat}": "Available"})
                print(f"{oldseat} is now Available")

            updated_data = {
            #'status': status_dropdown.get(),
            'departure_date': date_entry.get(),
            'departure_time': schedule_dropdown.get(),
            'bus_seat': seat_no_entry.get()
            }
            # Update Firestore document
            try:
                db.collection('tripInfo').document(trip_id).update(updated_data)
                messagebox.showinfo("Success", "Trip info updated successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update trip info: {e}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to update trip info: {e}")
