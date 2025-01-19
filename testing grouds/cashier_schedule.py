import customtkinter as ctk
from PIL import Image, ImageTk
from tkinter import ttk
import tkinter as tk
import firebase_admin
from firebase_admin import credentials, firestore
from firebase_config import db

# Define color variables
Red = "#8697C4"
White = "white"
Black = "#191970"
Gray = "#2D2D2D"
pearl = "#D9D9D9"

# Function to fetch unique values from a collection (with ALL option)
def get_unique_field_values(collection_name, field_name):
    docs = db.collection(collection_name).stream()
    unique_values = set()
    for doc in docs:
        doc_data = doc.to_dict()
        unique_values.add(doc_data.get(field_name, ""))
    return ["ALL"] + list(unique_values)  # Add "ALL" as the first option

# Function to fetch document names for the Route dropdown (with ALL option)
def get_document_names(collection_name):
    docs = db.collection(collection_name).stream()
    document_names = [doc.id for doc in docs]
    return ["ALL"] + document_names  # Add "ALL" as the first option

# This function will create the bus schedule management interface inside the provided main_frame
def update_main_frame_with_schedules(main_frame):
    # Clear main_frame content first
    for widget in main_frame.winfo_children():
        widget.destroy()

    # Design in Treeview
    style = ttk.Style()
    # Themes to change the general themes of treeview objs (can be downloaded or created)
    style.theme_use("clam")  # clam style
    style.configure("Treeview", background="transparent", foreground=pearl, rowheight=40, fieldbackground="transparent", font=("Arial", 12)) # Configure the header (font, etc.)
    style.configure("Treeview.Heading", font=("Arial", 14),  # Header font  #background="gray",   # Background color of the heade #foreground="white"   # Text color of the header
    )# Change selected color (background and foreground when selected)
    style.map(
        'Treeview', 
        background=[('selected', 'white')],  # Set selected row background to white
        foreground=[('selected', 'black')])  # Set selected row text color to black

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

    # A frame to hold other widgets to be set inside the canvas
    sub_frame = ctk.CTkFrame(canvas, fg_color='transparent')
    sub_frame.pack(fill="both", expand=True, padx=30, pady=30)

    # Configure the grid to support proper layout inside the main_frame
    sub_frame.grid_columnconfigure(0, weight=1)  # Sidebar column
    sub_frame.grid_columnconfigure(1, weight=4)  # Content column
    sub_frame.grid_rowconfigure(0, weight=1)

    # Create a frame for the sidebar
    sidebar_frame = ctk.CTkFrame(sub_frame, width=200, corner_radius=0, fg_color=Black)
    sidebar_frame.grid(row=0, column=0, sticky="nswe", padx=0)

    sidebar_frame.grid_columnconfigure(tuple(range(1)), weight=1)
    sidebar_frame.grid_rowconfigure(tuple(range(17)), weight=1)

    status_var = tk.StringVar(value="ALL")
    def toggle_status():
        current_status = status_var.get()
        if current_status == "ALL":
            status_var.set("Active")
        elif current_status == "Active":
            status_var.set("Cancelled")
        else:
            status_var.set("ALL")
        update_treeview()

    # Sidebar widgets (Dropdowns)
    title_label = ctk.CTkLabel(sidebar_frame, text="SCHEDULES", font=("Arial Black", 28, "bold"), text_color=White, width=150)
    title_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nswe")

    # Dropdown for Class (AC/NAC with ALL option)
    date_label = ctk.CTkLabel(sidebar_frame, text="Departure Date", font=("Arial Black", 16), text_color=White)
    date_label.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="nsw")

    date_entry = ctk.CTkEntry(sidebar_frame, placeholder_text="YYYY-MM-DD", width=130, height=35, font=("Arial", 16))
    date_entry.grid(row=2, column=0, padx=10, pady=(0,5), sticky="ew")

    # Dropdown for Class (AC/NAC with ALL option)
    class_label = ctk.CTkLabel(sidebar_frame, text="Class", font=("Arial Black", 16), text_color=White)
    class_label.grid(row=3, column=0, padx=10, pady=(10, 0), sticky="nsw")

    class_dropdown = ctk.CTkComboBox(sidebar_frame, values=["ALL", "AC", "NAC"], width=130, height=35, font=("Arial", 16), command=lambda choice: update_treeview())
    class_dropdown.grid(row=4, column=0, padx=10, pady=(0,5), sticky="ew")

    # Dropdown for Route (Fetched from BusRoutes collection, with ALL option)
    route_label = ctk.CTkLabel(sidebar_frame, text="Route", font=("Arial Black", 16), text_color=White)
    route_label.grid(row=5, column=0, padx=10, pady=(10, 0), sticky="nsw")
    route_dropdown = ctk.CTkComboBox(sidebar_frame, values=get_document_names("BusRoutes"), width=130, height=35, font=("Arial", 16), command=lambda choice: update_treeview())
    route_dropdown.grid(row=6, column=0, padx=10, pady=(0,5), sticky="ew")

    # Dropdown for Unit Type (Fetched from Buses collection, with ALL option)
    unit_type_label = ctk.CTkLabel(sidebar_frame, text="Unit Type", font=("Arial Black", 16), text_color=White)
    unit_type_label.grid(row=7, column=0, padx=10, pady=(10, 0), sticky="nsw")
    unit_type_dropdown = ctk.CTkComboBox(sidebar_frame, values=get_unique_field_values("Buses", "unit_type"), width=130, height=35, font=("Arial", 16), command=lambda choice: update_treeview())
    unit_type_dropdown.grid(row=8, column=0, padx=10, pady=(0,5), sticky="ew")

    status_label = ctk.CTkLabel(sidebar_frame, text="Status", font=("Arial Black", 16), text_color=White)
    status_label.grid(row=16, column=0, padx=10, pady=(10, 0), sticky="nsw")
    status_button = ctk.CTkButton( sidebar_frame, textvariable=status_var, fg_color="#fff", text_color="#191970", command=toggle_status, height=35, width=130, font=("Arial", 18, "bold"), hover_color="#9747FF")
    status_button.grid(row=17, column=0, padx=10, pady=(5,15), sticky="ew")

    # Create a frame for the main content (Treeview table)
    content_frame = ctk.CTkFrame(sub_frame)
    content_frame.grid(row=0, column=1, sticky="nsew", padx=0)

    # Configure the grid to allow expansion
    content_frame.grid_columnconfigure(0, weight=1)
    content_frame.grid_rowconfigure(0, weight=1)

    # Create the Treeview table
    columns = ("ROUTE", "TIME", "DATE", "FARE", "U. TYPE", "CLASS", "STATUS")
    tree = ttk.Treeview(content_frame, columns=columns, show="headings", height=10)

    for col in columns:
        tree.heading(col, text=col.capitalize().replace("_", " "))
        if col == 'TIME' or col == 'FARE':
            tree.column(col, width=60)
        elif col == 'U. TYPE':
            tree.column(col, width=80)
        elif col == 'CLASS':
            tree.column(col, anchor="center", width=50)
        elif col == 'STATUS' :
            tree.column(col, anchor="center", width=60)
        elif  col =="DATE":
            tree.column(col, anchor="center", width=70)
        elif col == "ROUTE":
            tree.column(col, width=120)
        else:
            tree.column(col, width=130)
        #tree.pack(fill="both", expand=True)

    tree.grid(row=0, column=0, sticky="nsew", padx=0)
    tree.tag_configure('Cancelled',  background="#cc3e40", foreground="#fff")
    tree.tag_configure('Active',  background="#000", foreground="#fff")

    # Add scrollbars
    scrollbar_y = ctk.CTkScrollbar(content_frame, orientation="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar_y.set)
    scrollbar_y.grid(row=0, column=1, sticky="ns", padx=0)

    def update_treeview(event=None):
        # Get the selected values from the dropdowns
        selected_class = class_dropdown.get()
        selected_route = route_dropdown.get()
        selected_unit_type = unit_type_dropdown.get()
        selected_date = date_entry.get().strip()
        status = status_var.get()

        # Clear the Treeview
        for row in tree.get_children():
            tree.delete(row)

        # Fetch filtered data from Firestore based on dropdown selections
        schedules_ref = db.collection("BusSchedule")

        # Apply partial date matching
        if selected_date:  # Check if the user entered a date
            schedules = schedules_ref.where("departure_date", ">=", selected_date).where(
                "departure_date", "<", selected_date + "\uf8ff"
            ).stream()
        else:
            schedules = schedules_ref.stream()  # No date filter if the entry is empty

        # Insert fetched data into the Treeview
        for schedule in schedules:
            schedule_data = schedule.to_dict()

            if ((selected_class == "ALL" or selected_class == schedule_data.get("bus_class")) and
               (selected_route == "ALL" or  selected_route == schedule_data.get("route")) and
               (selected_unit_type == "ALL" or  selected_unit_type == schedule_data.get("unit_type")) and 
               (status == "ALL" or status == schedule_data.get("status"))):
                
                if schedule_data.get('status') == "Cancelled":
                    row_tags = "Cancelled"
                else:
                    row_tags = "Active"

                tree.insert("", "end", values=(
                    f"  {schedule_data.get('route','')}",
                    f"  {schedule_data.get('departure_time','')}",
                    schedule_data.get('departure_date',''),
                    f"₱. {schedule_data.get('fare','')}",
                    f"  {schedule_data.get('unit_type','')}",
                    schedule_data.get('bus_class',''),
                    schedule_data.get('status','')
                ), tags=(row_tags,))

    date_entry.bind('<Return>', update_treeview)
    # Initialize the Treeview with all data
    update_treeview()

# Sample call to test the function (replace with actual main_frame)
# update_main_frame_with_schedules(main_frame)
# Testing the function with customtkinter root

"""class CollapsibleSidebarApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Collapsible Sidebar with Cashier Dashboard")
        self.geometry("800x600")

        # Default button width when expanded and collapsed
        self.button_width_expanded = 300
        self.button_width_collapsed = 100

        # Sidebar Frame with background color
        self.sidebar = ctk.CTkFrame(self, width=self.button_width_expanded, height=600, fg_color="black", corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        # Main Content Frame
        self.main_frame = ctk.CTkFrame(self, fg_color="white")
        self.main_frame.pack(side="right", fill="both", expand=True)

        # Toggle Button for Sidebar
        self.toggle_button = ctk.CTkButton(self.sidebar, text="<<", command=self.toggle_sidebar, width=self.button_width_expanded)
        self.toggle_button.pack(pady=10)

        # Sidebar State (collapsed/expanded)
        self.sidebar_collapsed = False

        # Create individual buttons with hover image change functionality and test commands
        self.create_buttons()

    def create_buttons(self):
        # Load images for the buttons and hover images
        button_images = {
            "Schedule": (ctk.CTkImage(Image.open("C:/Users/jacaj/Downloads/python project/Bus_Reservation_System2/testing grouds/image sources/cashier_icons/calendar1.png").resize((50, 50))),
                       ctk.CTkImage(Image.open("C:/Users/jacaj/Downloads/python project/Bus_Reservation_System2/testing grouds/image sources/cashier_icons/calendar2.png").resize((50, 50)))),
            "Route": (ctk.CTkImage(Image.open("C:/Users/jacaj/Downloads/python project/Bus_Reservation_System2/testing grouds/image sources/cashier_icons/route1.png").resize((50, 50))),
                         ctk.CTkImage(Image.open("C:/Users/jacaj/Downloads/python project/Bus_Reservation_System2/testing grouds/image sources/cashier_icons/route2.png").resize((50, 50)))),
            "Fares": (ctk.CTkImage(Image.open("C:/Users/jacaj/Downloads/python project/Bus_Reservation_System2/testing grouds/image sources/cashier_icons/ticket1.png").resize((50, 50))),
                    ctk.CTkImage(Image.open("C:/Users/jacaj/Downloads/python project/Bus_Reservation_System2/testing grouds/image sources/cashier_icons/ticket2.png").resize((50, 50)))),
            "POS": (ctk.CTkImage(Image.open("C:/Users/jacaj/Downloads/python project/Bus_Reservation_System2/testing grouds/image sources/cashier_icons/pos1.png").resize((50, 50))),
                        ctk.CTkImage(Image.open("C:/Users/jacaj/Downloads/python project/Bus_Reservation_System2/testing grouds/image sources/cashier_icons/pos2.png").resize((50, 50)))),
            "Profile": (ctk.CTkImage(Image.open("C:/Users/jacaj/Downloads/python project/Bus_Reservation_System2/testing grouds/image sources/cashier_icons/profile1.png").resize((50, 50))), 
                        ctk.CTkImage(Image.open("C:/Users/jacaj/Downloads/python project/Bus_Reservation_System2/testing grouds/image sources/cashier_icons/profile2.png").resize((50, 50)))),
            "Home": (ctk.CTkImage(Image.open("C:/Users/jacaj/Downloads/python project/Bus_Reservation_System2/testing grouds/image sources/cashier_icons/bahay1.png").resize((50, 50))),
                        ctk.CTkImage(Image.open("C:/Users/jacaj/Downloads/python project/Bus_Reservation_System2/testing grouds/image sources/cashier_icons/bahay2.png").resize((50, 50))))
                        
        }

        # Declare buttons individually with hover effect
        self.btn_generate_ticket = self.create_button("@ GENERATE REGULAR TICKET", button_images["Schedule"], self.test_command_ticket)
        self.btn_view_schedule = self.create_button("# VIEW BUS SCHEDULE", button_images["Route"], self.test_command_schedule)
        self.btn_gas_costing = self.create_button("$ GAS COSTING", button_images["Fares"], self.test_command_gas)
        self.btn_cashier_management = self.create_button("% CASHIER MANAGEMENT", button_images["POS"], self.test_command_cashier)
        self.btn_prof_management = self.create_button("% profile MANAGEMENT", button_images["Profile"], self.test_command_cashier)
        self.btn_home_management = self.create_button("% Home MANAGEMENT", button_images["Home"], self.test_command_cashier)

    def create_button(self, text, images, command):
        normal_image, hover_image = images
        button = ctk.CTkButton(self.sidebar, image=normal_image, text=text, anchor="w", width=self.button_width_expanded, fg_color="black", corner_radius=0, command=command, height=100)
        button.pack(pady=5, fill="x")
        self.add_hover_effect(button, normal_image, hover_image)
        return button

    def add_hover_effect(self, button, normal_image, hover_image):
        #Adds hover effect to change the image of a button.
        def on_enter(event):
            button.configure(image=hover_image)

        def on_leave(event):
            button.configure(image=normal_image)

        # Bind the enter and leave events to the button
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

    def toggle_sidebar(self):
        if self.sidebar_collapsed:
            # Expand sidebar
            self.sidebar.configure(width=self.button_width_expanded)
            self.toggle_button.configure(text="<<", width=self.button_width_expanded)
            self.btn_generate_ticket.configure(width=self.button_width_expanded, text="@ GENERATE REGULAR TICKET")
            self.btn_view_schedule.configure(width=self.button_width_expanded, text="# VIEW BUS SCHEDULE")
            self.btn_gas_costing.configure(width=self.button_width_expanded, text="$ GAS COSTING")
            self.btn_cashier_management.configure(width=self.button_width_expanded, text="% CASHIER MANAGEMENT")
            self.btn_prof_management.configure(width=self.button_width_expanded, text="% CASHIER MANAGEMENT")
            self.btn_home_management.configure(width=self.button_width_expanded, text="% CASHIER MANAGEMENT")
        else:
            # Collapse sidebar
            self.sidebar.configure(width=self.button_width_collapsed)
            self.toggle_button.configure(text=">>", width=self.button_width_collapsed)
            self.btn_generate_ticket.configure(width=self.button_width_collapsed, text="")
            self.btn_view_schedule.configure(width=self.button_width_collapsed, text="")
            self.btn_gas_costing.configure(width=self.button_width_collapsed, text="")
            self.btn_cashier_management.configure(width=self.button_width_collapsed, text="")
            self.btn_prof_management.configure(width=self.button_width_collapsed, text="")
            self.btn_home_management.configure(width=self.button_width_collapsed, text="")

        self.sidebar_collapsed = not self.sidebar_collapsed

    # Test commands for each button
    def test_command_ticket(self):
        print("Generate Regular Ticket button clicked!")

    def test_command_schedule(self):
        print("View Bus Schedule button clicked!")

    def test_command_gas(self):
        print("Gas Costing button clicked!")

    def test_command_cashier(self):
        print("Cashier Management button clicked!")

# Create and run the application
app = CollapsibleSidebarApp()
app.mainloop()
"""