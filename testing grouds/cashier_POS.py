import customtkinter as ctk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from firebase_config import db
import re  # Import regular expressions
from datetime import datetime
from tkcalendar import Calendar
import tkinter as tk
from forHover import set_hover_color

from cashier_POS_tcktGEn import save_data

Red = "#8697C4"
White = "white"
Black = "#191970"
Gray = "#2D2D2D"
pearl="#D9D9D9"
blue = "#8697C4"


"""___________________main Code_________________________---"""
# function to u[pdate main frame
def update_main_frame(main_frame, create_widgets, app, Doc_id, acc_id):
    """___________________window generation_________________________---"""

    #destroy children widgest inside main_frame
    global acco_id, cashier_id, schedule_time_dic, selected_schedule_id
    acco_id =Doc_id
    cashier_id =acc_id
    for widget in main_frame.winfo_children():
        widget.destroy()
        #call function to repopulate main_mainframe with widgets

    # Canvas to set a background image 
    canvas = ctk.CTkCanvas(main_frame)
    canvas.pack(fill="both", expand=True)

    # Load the background image using PIL
    background_image = Image.open("C:/Users/jacaj/Downloads/python project/Bus_Reservation_System2/testing grouds/image sources/background1.png")
    background_image = background_image.resize((1300, 680))  # Resize to fit the canvas
    background_image_tk = ImageTk.PhotoImage(background_image)  # Convert to Tkinter image format

    # Place the background image on the canvas
    canvas.create_image(0, 0, anchor="nw", image=background_image_tk)

    # Keep a reference to the image to prevent garbage collection
    canvas.image = background_image_tk


    """____________genearate the main canvas contentb __________________________"""
    create_content_frame(canvas, app)

#make the content of the main_frame
def create_content_frame(parent,app):
    """Frame setting nagd grid configurations """

    #creat a frame holder inside the frame 
    content_frame = ctk.CTkFrame(parent, fg_color="transparent", corner_radius=0)
    content_frame.pack(fill="both", expand=True, padx=40, pady=40)# same size a current main frame
    
    #The grid layout is configured for the content frame. Each row and column is set to expand equally with weight=1, creating a flexible grid that adjusts based on the window size.
    #ow configuration
    content_frame.grid_rowconfigure(0, weight=1)
    content_frame.grid_rowconfigure(1, weight=1)
    #column configuration
    content_frame.grid_columnconfigure(0, weight=1)
    content_frame.grid_columnconfigure(1, weight=1)
    content_frame.grid_columnconfigure(2, weight=1)

    """Ticket setting genertion"""
    # call other functions that serves a section in the main frame re population using content frame configuration to allow using .grid 
    create_ticket_frame(content_frame,app)
    
    #create_ticket_preview_frame(content_frame)
"""         ticket generation holder          """
# Global list to hold ticket data dictionaries
ticket_data_list = []


"""Dropdown varaible value fetching """
# Function to fetch route names from BusRoutes collection
def fetch_routes():
    routes = []
    bus_routes_ref = db.collection('BusRoutes')
    docs = bus_routes_ref.stream()
    for doc in docs:
        routes.append(doc.id)  # Document name is the route name
    return routes

def update_schedule_treeview(tree,selected_route, selected_class, date):
    # Clear the Treeview
    for row in tree.get_children():
        tree.delete(row)
        
    global schedule_time_dic
    schedule_time_dic = {}
    if selected_route and selected_class and date:
        # Fetch the schedule data as a list of dictionaries
        schedules_ref = db.collection("BusSchedule")
        docs = schedules_ref.stream()
     

        # Populate the Treeview with the fetched data
        for schedule in docs:
            no_of_seats = schedule.get("no_of_seats")
            time =schedule.get('departure_time')
            if ((selected_class == "ALL" or selected_class == schedule.get("bus_class")) and
                (selected_route == "ALL" or  selected_route == schedule.get("route")) and
                (date == "ALL" or  date == schedule.get("departure_date"))):
                    
                # Calculate the number of available seats
                schedule_dict = schedule.to_dict() if schedule.exists else {}
                seats_data = schedule_dict.get("seats", {})
                available_seats = sum(1 for seat in seats_data.values() if seat == "Available")

                # Format the seats as "Available/Total"
                seats_formatted = f"{available_seats}/{no_of_seats}"
                schedule_time_dic[time] = schedule.id  # Store both the document ID and time
                print (f"time : {time} , id {schedule.id}")
                # Add the data as a new row in the Treeview
                tree.insert("", "end", values=(schedule.get("departure_time"), schedule.get("bus_class"), schedule.get("unit_type"), seats_formatted))
        else:
            print("Please select a route, class, and date.")


"""_____________________________Ticket creation Function____________________________"""
# Function to create the ticket frame and widgets
def create_ticket_frame(parent, app):

    # Create a frame that holds the widgets
    ticket_frame = ctk.CTkFrame(parent, fg_color=Black, corner_radius=0)
    ticket_frame.grid(row=0, column=0, columnspan=3, sticky="nsew")
    ticket_frame.grid_columnconfigure(tuple(range(4)), weight=1)
    ticket_frame.grid_rowconfigure(tuple(range(8)), weight=1)

    # --- Labels and Dropdowns ---
    # Create a label for the ticket section
    ticket_label = ctk.CTkLabel(ticket_frame, text="TICKET", text_color="white", font=("Arial", 30, "bold")) # Place the label at the top center of the ticket_frame
    ticket_label.grid(row=0, column=0, columnspan=2, rowspan=2, pady=(10,10),padx=(20,10), sticky="nw")

    # Label and entry for Date
    ctk.CTkLabel(ticket_frame, text="Date", text_color="white", font=("Arial", 16)).grid(row=2, column=0, padx=(30, 10), sticky="nsw")
    current_datetime = datetime.now()
    formatted_date = current_datetime.strftime("%Y-%m-%d")
    date_variable = formatted_date
    date_entry = ctk.CTkEntry(ticket_frame, placeholder_text="", text_color="black", fg_color="#fff", font=("Arial", 18), width=200, height=40)
    date_entry.insert(0, date_variable)
    date_entry.grid(row=3, column=0, pady=(0,10), padx=(20,10), sticky="ew")
    
    # Label and dropdown for Route
    ctk.CTkLabel(ticket_frame, text="Route", text_color="white", font=("Arial", 16)).grid(row=4, column=0, padx=(30, 10), sticky="nsw")
    routes = fetch_routes()
    route_var = ctk.StringVar()
    route_dropdown = ctk.CTkOptionMenu( ticket_frame, variable=route_var, values=routes, fg_color="#fff", button_color="#8697C4", button_hover_color="#6eacda", dropdown_fg_color="white", dropdown_hover_color="gray80", text_color="black", font=("Helvetica", 18), dropdown_font=("Helvetica", 14), height = 40)
    route_dropdown.grid(row=5, column=0, pady=(0,10), padx=(20, 10), sticky="ew")

    # Label and dropdown for Class
    ctk.CTkLabel(ticket_frame, text="Class", text_color="white", font=("Arial", 16)).grid(row=6, column=0, padx=(30, 10), sticky="nsw")
    class_var = ctk.StringVar()

    # Create a CTkOptionMenu
    class_dropdown = ctk.CTkOptionMenu(ticket_frame, variable=class_var, values=["ALL","AC", "NAC"], fg_color="white", button_color="#8697C4", button_hover_color="#6eacda", dropdown_fg_color="white", dropdown_hover_color="gray80", text_color="black", font=("Helvetica", 18), dropdown_font=("Helvetica", 14), height = 40)
    class_dropdown.grid(row=7, column=0, pady=(0,20), padx=(20,10), sticky="ew")
    class_dropdown.set("ALL")
    #print(date_entry.get())

    # Label and dropdown for Schedule
    ctk.CTkLabel(ticket_frame, text="Schedule", text_color="white", font=("Arial", 16)).grid(row=2, column=1,padx=(20, 10), sticky="nsw")
    # Create a frame for the main content (Treeview table)
    Schedule_frame = ctk.CTkFrame(ticket_frame, width=250)
    Schedule_frame.grid(row=3, column=1, columnspan=2, rowspan=5, sticky="nsew", padx=(10,10), pady=(0,20))

    # Configure the grid to allow expansion
    Schedule_frame.grid_columnconfigure(0, weight=1)
    Schedule_frame.grid_rowconfigure(0, weight=1)

    # Create the Treeview table
    columns = ( "TIME", "CLASS", "U. TYPE", "SEATS")
    tree = ttk.Treeview(Schedule_frame, columns=columns, show="headings", height=10)

    for col in columns:
        tree.heading(col, text=col)
        if col == 'TIME' or col == 'FARE':
            tree.column(col, width=50)
        elif col == 'U. TYPE':
            tree.column(col, width=80)
        elif col == 'CLASS':
            tree.column(col, anchor="center", width=30)
        elif col == 'SEATS' :
            tree.column(col, anchor="center", width=40)
    tree.grid(row=0, column=0, sticky="nsew", padx=0)
    tree.tag_configure('Cancelled',  background="#cc3e40", foreground="#fff")
    tree.tag_configure('Active',  background="#000", foreground="#fff")

    # Add scrollbars
    scrollbar_y = ctk.CTkScrollbar(Schedule_frame, orientation="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar_y.set)
    scrollbar_y.grid(row=0, column=1, sticky="ns", padx=0)

    global selected_schedule_id
    # Label and dropdown for Seat
    ctk.CTkLabel(ticket_frame, text="Seat", text_color="white", font=("Arial", 16)).grid(row=2, column=3, padx=(20, 10), sticky="w")
    seat_var  = ctk.CTkButton(ticket_frame, text="Select a Seat", command= lambda: create_seat_selection_window(selected_tree (tree)),text_color="#191970", font=("Arial", 16, "bold"), fg_color="#fff", border_width=2, border_color="#fff", height=40, width=150)
    seat_var.grid(row=3, column=3, pady=(0,10), padx=(10,20), sticky="ew")
    set_hover_color(seat_var, "#6eacda", "#fff" ,"#fff","#191970"  )
    
    # Label and dropdown for Discount
    ctk.CTkLabel(ticket_frame, text="Discount", text_color="white", font=("Arial", 16)).grid(row=4, column=3, padx=(20, 10), sticky="w")
    discount_var = ctk.StringVar()
    discount_dropdown = ctk.CTkOptionMenu( ticket_frame, variable=discount_var, values=["STUDENT", "PWD","SENIOR","REGULAR"], fg_color="#Fff", button_color="#8697C4", button_hover_color="#6eacda", dropdown_fg_color="white", dropdown_hover_color="gray80", text_color="black", font=("Helvetica", 18), dropdown_font=("Helvetica", 14),width=200, height = 40)
    discount_dropdown.grid(row=5, column=3, pady=(0,10), padx=(10,20), sticky="ew")
    discount_dropdown.set("REGULAR")

    def update(*args) :
        selected_route = route_var.get()
        selected_class = class_var.get()
        date = date_entry.get()
        update_schedule_treeview(tree, selected_route, selected_class, date)

    route_var.trace_add("write", update)
    class_var.trace_add("write", update)
    date_entry.bind("<Return>", update)


    def selected_tree (tree):
        selected_item = tree.selection()  # Get the selected row in the Treeview
        if selected_item:  # Ensure a row is selected
            item = tree.item(selected_item)
            values = item['values']
            schedule_time = values[0]  # Assume first column contains Schedule ID
            return schedule_time
        else:
            return None

    """ Bus seat selection function"""
    def create_seat_selection_window(selected_schedule_time):
        global schedule_time_dic
        if not selected_schedule_time:
            messagebox.showerror("Error", "Please select a schedule first!")
            return

        root = tk.Tk()
        root.title("Select Your Seat")
        id = schedule_time_dic[selected_schedule_time]

        # Fetch seat data from BusSchedule collection using selected_schedule value
        def fetch_seat_data(id):
            try:
                schedules_ref = db.collection('BusSchedule').document(id)
                results = schedules_ref.get()

                if results.exists:  # Check if the document exists
                    seats_data =  results.to_dict().get('seats', {})
                    if not isinstance(seats_data, dict):
                        raise ValueError("Expected 'seats' to be a dictionary.")
                    return seats_data
                else:
                    print("No matching schedule found.")
                    return {}
            except Exception as e:
                print(f"Error fetching data 1: {e}")
                return {}
            
        seat_buttons = {}
        seat_status = fetch_seat_data(id)# Fetch seat status from Firestore
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
            if selected_seat and seat_buttons[selected_seat].cget('bg') == 'red':
                seat_buttons[selected_seat].configure(bg='blue')
        
            # Select the new seat (set to red)
            selected_seat = seat_id
            seat_buttons[selected_seat].configure(bg='red')
            print(f"Selected seat: {selected_seat}")

        # Create buttons for each seat
        for seat_id, status in seat_status.items():
            row = int(seat_id[:-1]) - 1  # Convert to zero-based index
            col = ord(seat_id[-1]) - ord('A')  # Convert letter to index
                # Create the seat button
            
            button = tk.Button(root, text=seat_id, width=5, height=2, bg='blue')

            # Disable reserved seats
            if status != 'Available':
                button.configure(state=tk.DISABLED, bg='grey')  # Reserved seats
            else:
                button.configure(command=lambda s=seat_id: reserve_seat(s))  # Available seats

            button.grid(row=row, column=col, padx=5, pady=5)
            seat_buttons[seat_id] = button

        # Function to confirm the seat selection
        def confirm_selection():
            if selected_seat:
                print(f"Confirmed seat: {selected_seat}")
                if seat_var:
                    seat_var.configure(text=f"Seat: {selected_seat}")  # Update seat_var button text
                    global seat
                    seat = selected_seat
                    root.destroy()
                else:
                    print("seat_var button is not defined.")
            else:
                print("No seat selected.")
                messagebox.showwarning("No Seat", "Please select a seat before confirming.")

        # Confirm button to finalize seat selection
        select_button = tk.Button(root, text="Select", command=confirm_selection, width=10)
        select_button.grid(row=max_row + 1, columnspan=max_col + 1, pady=10)
        root.mainloop()

        # Assuming seat_var is defined somewhere in your main program.


        # Example usage:
        # create_seat_selection_window("2024-04-27 10:00 AM")
        # Assuming seat_var is defined somewhere in your main program
    

    def fetch_schedule_data(schedule_id):
        try:
            schedules_ref = db.collection('BusSchedule').document(schedule_id)
            doc = schedules_ref.get()
            if doc.exists:
                schedule_data = doc.to_dict()
                # Extract required fields, providing default values if they don't exist
                fare = schedule_data.get('fare', 0)  # Default to 0 if fare is not found
                bus_id = schedule_data.get('bus_id', None)  # Default to None if bus_id is not found
                bus_class = schedule_data.get('bus_class', None)  # Default to None if bus_class is not found
                return {
                    "fare": fare,
                    "bus_id": bus_id,
                    "bus_class": bus_class
                }
        except Exception as e:
            print(f"Error fetching schedule data: {e}")
        # Return default values if document doesn't exist or an error occurs
        return {
            "fare": 0,
            "bus_id": None,
            "bus_class": None
        }
    
    def refresh_treeview():
        # Clear all items from Treeview
        for item in treeview1.get_children():
            treeview1.delete(item)
    
        # Re-insert each entry from ticket_data_list into Treeview with updated index
        for index, data in enumerate(ticket_data_list, start=1):
            # Combine the data fields for display
            combined_data = " | ".join([
                data["Route"], 
                data["Class"], 
                data["Time_Schedule"], 
                data["Seat"], 
                data["Discount"], 
                data["Dept_Date"]
            ])
            # Insert the data into Treeview with index as the first column
            treeview1.insert("", "end", values=(index, combined_data, data["Fare"]))

    #schedule_var.trace('w', create_seat_selection_window)

    discounts = {
        "STUDENT": 0.12,  # 12%
        "PWD": 0.20,      # 20%
        "SENIOR": 0.10,   # 10%
        "REGULAR": 0.0    # 0%
    }
    def apply_discount(selected_discount, price):
        try:
            # Convert price to float to ensure it works for both integers and decimals
            price = float(price)
        except ValueError:
            print("Invalid price value!")
            return None  # Exit the function if price is invalid
    
        discount_value = discounts.get(selected_discount, 0)  # Get the discount value or default to 0
        final_price = price - (price * discount_value)
        return final_price

    # Function to handle Add button click
    def add_ticket_data():
        time = selected_tree (tree)
        global schedule_time_dic
        schedule_data = fetch_schedule_data(schedule_time_dic[time])
        fare = schedule_data["fare"]
        bus_id = schedule_data["bus_id"]
        bus_class = schedule_data["bus_class"]
        mode="CASH"
        #current date related 
        current_datetime = datetime.now()
        formatted_date = current_datetime.strftime("%Y-%m-%d")
        date_variable = formatted_date

        final_price = apply_discount(discount_var.get(), fare)

        # Collect all field values
        data = {
            "ScheduleID": schedule_time_dic[time],
            "Route": route_var.get(),
            "Class": bus_class,
            "Time_Schedule": time,
            "Seat": seat,
            "Discount": discount_var.get(),
            "Dept_Date": date_entry.get(),
            "Fare": final_price,
            "Acc_id": acco_id, # chasier document ID
            "Cashier_id": cashier_id, # cashier normal id
            "Mode": mode,
            "Bus_ID": bus_id,
            "Current_Date": date_variable
        }

        # Check if similar schedule and seat already exist in ticket_data_list
        for existing_ticket in ticket_data_list:
            if existing_ticket["ScheduleID"] == data["ScheduleID"] and existing_ticket["Seat"] == data["Seat"]:
                # Show error message if duplicate found
                messagebox.showerror("Error", "This seat has already been booked. Please select a diffrent seat or schedule.")
                return  # Exit the function, preventing the ticket from being added


        # Append the data dictionary to the list
        ticket_data_list.append(data)

        # Refresh Treeview to show the updated list
        refresh_treeview()

        # After adding a row, update the total price
        update_total_price()

    

    def delete_selected():
        selected_item = treeview1.selection()
        if selected_item:

            confirm = messagebox.askyesno('Warning', "Delete this Item?")

            if confirm:
                # Get the values of the selected item (the first value is the index)
                selected_values = treeview1.item(selected_item, "values")
                ticket_index = int(selected_values[0]) - 1  # Convert to zero-based index

                # Remove item from ticket_data_list using the index
                if 0 <= ticket_index < len(ticket_data_list):
                    del ticket_data_list[ticket_index]

                messagebox.showwarning('Deleted',"Item Removed")
        
                # Delete the item from the Treeview
                # Refresh Treeview to update display
                refresh_treeview()
        
                # Update the total price or other UI elements if needed
                update_total_price()

    
    # Create the CLEAR button and place it at the top-right corner inside the ticket_frame
    """clear_button = ctk.CTkButton(ticket_frame, text="CLEAR", text_color="black", fg_color="#F4EAD5", font=("Arial", 16))
    clear_button.grid(row=1, column=3, sticky="se", padx=(10,30), pady=(30,10))"""


    # Add button to submit ticket data
    add_button = ctk.CTkButton(ticket_frame, text="ADD", text_color="#191970", fg_color="white", font=("Arial", 24,"bold"),width=198, height=60, command=add_ticket_data, border_width=2, border_color="white")
    add_button.grid(row=6, column=3, rowspan=2, sticky="sew", padx=(10, 20), pady=(10,20))
    set_hover_color(add_button, "#6eacda","white", "white", "#191970" )


    lower_frame =ctk.CTkFrame(parent, fg_color=blue, corner_radius=0)
    lower_frame.grid(row=1, column=0, columnspan=3, sticky="nesw")

    # Configure the grid for lower_frame (3 columns max)
    lower_frame.grid_columnconfigure(0, weight=1)
    discount_frame = ctk.CTkFrame(lower_frame, fg_color=blue, corner_radius=0)
    discount_frame.grid(row=0, column=0, sticky="nesw", padx=(20,10), pady=(20,40))

    # Configure the parent frame to allow dynamic resizing
    parent.grid_columnconfigure(0, weight=1)
    parent.grid_rowconfigure(0, weight=1)

    # Configure rows and columns in the discount_frame
    discount_frame.grid_columnconfigure(0, weight=1)  # First column expands
    discount_frame.grid_columnconfigure(1, weight=1)  # Second column expands
    discount_frame.grid_columnconfigure(2, weight=0)  # Third column remains fixed
    discount_frame.grid_rowconfigure(0, weight=0)  # Header row remains fixed
    discount_frame.grid_rowconfigure(1, weight=1)  # Content row expands vertically

    # Header frame at the top spanning columns 0 and 1
    head_frame = ctk.CTkFrame(discount_frame, fg_color=Black, corner_radius=0, height=60)
    head_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=(0,10))

    head_frame.grid_columnconfigure(0, weight=1)  # First column expands
    head_frame.grid_columnconfigure(1, weight=1)  # Second column expands

    # Label inside the header frame
    dropping_label = ctk.CTkLabel(head_frame, text="Purchase List", font=("Arial Black", 16), text_color="white")
    dropping_label.grid(row=0, column=0, padx=10, pady=(5, 5), sticky="nw")

    delete_button = ctk.CTkButton(head_frame, text="Delete", font=("Arial Black", 16), text_color="#191970", fg_color=White, command=delete_selected)
    delete_button.grid(row=0, column=2, padx=10, pady=(5, 5), sticky="ne")
    set_hover_color(delete_button, "red", "white", White, "#191970")

    # Table frame below the header, spanning columns 0 and 1
    table_frame = ctk.CTkFrame(discount_frame, fg_color="white", corner_radius=0)
    table_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(0,10), padx=(0,10))


    style = ttk.Style()
    style.theme_use("clam")  # clam style
    style.configure(
        "Treeview", 
        background="white", 
        foreground="black",  # Default row text color
        rowheight=20, 
        fieldbackground="transparent",
        font=("Arial", 12)
    )
        # Configure the header (font, etc.)
    style.configure(
        "Treeview.Heading", 
        font=("Arial", 12),  # Header font
    )
    # Change selected color (background and foreground when selected)
    style.map(
        'Treeview', 
        background=[('selected', 'blue')],  # Set selected row background to white
        foreground=[('selected', 'white')]   # Set selected row text color to black
    )


    # Treeview widget inside the table frame
    treeview1 = ttk.Treeview(table_frame, columns=("Number", "Item","Price"), show="headings", height=10)
    treeview1.heading("Number", text="No.",)
    treeview1.heading("Item", text="Item")
    treeview1.heading("Price", text="Price")
    treeview1.column("Number", width=20, anchor="w")
    treeview1.column("Item",width=400, anchor="w")
    treeview1.column("Price", width=50,anchor="w")
    treeview1.grid(row=0, column=0, sticky="nsew")

    # Scrollbar for Treeview
    scrollbar = ctk.CTkScrollbar(table_frame, command=treeview1.yview)
    treeview1.configure(yscrollcommand=scrollbar.set)
    scrollbar.grid(row=0, column=1, sticky='ns')

    # Configure the table_frame to resize dynamically
    table_frame.grid_columnconfigure(0, weight=1)  # Let Treeview expand horizontally
    table_frame.grid_rowconfigure(0, weight=1)  # Let Treeview expand vertically

    # Third frame (right side) that remains fixed
    third_frame = ctk.CTkFrame(discount_frame, fg_color=pearl, corner_radius=10, width=300 )
    third_frame.grid(row=0, column=2, rowspan=2, sticky="nsew", padx=(10, 10), pady=(0,10))  # Right-aligned with fixed width

    third_frame.grid_columnconfigure(0, weight=1)  # Let Treeview expand horizontally
    third_frame.grid_columnconfigure(1, weight=1)  # Let Treeview expand horizontally
    third_frame.grid_rowconfigure(0, weight=1)  # Let Treeview expand vertically
    third_frame.grid_rowconfigure(1, weight=1)  # Let Treeview expand vertically
    third_frame.grid_rowconfigure(2, weight=1)  # Let Treeview expand vertically
    third_frame.grid_rowconfigure(3, weight=1)  # Let Treeview expand vertically

    def check_float(event):
        input_value = total_entry.get()
        try:
            # Try converting the input to float
            if input_value == "":  # Allow empty input
                return
            float(input_value)
            total_entry.configure(fg_color="white")  # Valid input: change background to white (or normal)
        except ValueError:
            # Invalid input: change background color to red
            total_entry.configure(fg_color="red")

    def update_total_price():
        global total_price
        total_price = 0.0  # Initialize the total price as 0.0

        # Regular expression to extract numeric values (both integers and floats)
        number_pattern = re.compile(r"[-+]?\d*\.\d+|\d+")

         # Loop through each row in the Treeview
        for child in treeview1.get_children():
            # Get the values in each row
            row_values = treeview1.item(child, "values")
            # Assuming that the Price is the third column (index 2)
            price_value = row_values[2]
        
            # Try to find a number in the price value string using regex
            match = number_pattern.search(price_value)
        
            if match:
                # If a number is found, convert it to a float and add to total_price
                total_price += float(match.group())

       
        # Update the label with the total price
        receive_price.configure(text=f"{total_price:.2f}")

    def calculate_change():
        # Get the value from total_entry (user input) and convert it to a float
        try:
            total_entry_total = float(total_entry.get())
        except ValueError:
            print("Invalid float value in total_entry")
            generate_button.configure(state='disabled')
            return

        # Subtract total_price (sum from the treeview) from the total_entry value
        change_value = total_entry_total - total_price

        # Update the label `change_price` with the calculated change_value
        change_price.configure(text=f"{change_value:.2f}")  # Format to 2 decimal places

        if change_value < 0:
            generate_button.configure(state='disabled')
        else: 
            generate_button.configure(state='enabled', hover_color="green")

# Function to handle the Enter key press event
    def on_enter_key(event):
        calculate_change()  # Call the function when Enter key is pressed

    


    # Row 0: Receive Label
    receive_label = ctk.CTkLabel(third_frame, text="Receive: P.", font=("Arial", 15))
    receive_label.grid(row=0, column=0, sticky="e", padx=20, pady=(20, 5))

    total_entry = ctk.CTkEntry(third_frame, width=100, font=("Arial", 15))
    total_entry.grid(row=0, column=1, padx=(10,20), pady=(20,5))
    total_entry.bind("<KeyRelease>", check_float)
    # Bind the Enter key to the total_entry widget
    total_entry.bind("<Return>", on_enter_key)


    # Row 1: Total Label and Disabled Entry (using two columns)
    total_label = ctk.CTkLabel(third_frame, text="Total: P.", font=("Arial", 15))
    total_label.grid(row=1, column=0, sticky="e", padx=20, pady=(11, 5))

    receive_price = ctk.CTkLabel(third_frame, text="00.00", font=("Arial", 15))
    receive_price.grid(row=1, column=1, sticky="w", padx=20, pady=(15, 5))


    # Row 2: Change Label
    change_label = ctk.CTkLabel(third_frame, text="Change: P.", font=("Arial", 15))
    change_label.grid(row=2, column=0, sticky="e", padx=20, pady=(15, 5))

    change_price = ctk.CTkLabel(third_frame, text="00.00", font=("Arial", 15))
    change_price.grid(row=2, column=1, sticky="w", padx=20, pady=(15, 5))

    #   Row 3: Generate Button (spanning two columns)
    generate_button = ctk.CTkButton(third_frame, text="GENERATE", font=("Arial", 18), width=200, height=55, fg_color='#191970', command= lambda: gen(), text_color='#fff', border_width=2, border_color="#191970")
    generate_button.grid(row=3, column=0, columnspan=2, pady=(30,20), sticky="ns")
    set_hover_color(generate_button, White ,'#191970' ,'#191970', White )
    generate_button.configure(state='disabled')
    

    def gen():
        save_data(ticket_data_list)
        messagebox.showinfo("Information", "Clear Data!!!.")
        for item in treeview1.get_children():
            treeview1.delete(item)
        change_price.configure(text="00.00")
        receive_price.configure(text="00.00")
        total_entry.delete(0, tk.END)
        calculate_change()
        ticket_data_list.clear()

