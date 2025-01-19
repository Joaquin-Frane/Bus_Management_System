import customtkinter as ctk
from PIL import Image, ImageTk
from tkinter import ttk
import tkinter as tk
from firebase_config import db

# Define color variables
Red = "#8697C4"
White = "white"
Black = "#191970"
Gray = "#2D2D2D"
pearl = "#D9D9D9"

def get_unique_field_values(collection_name, field_name):
    docs = db.collection(collection_name).stream()
    unique_values = set()
    for doc in docs:
        doc_data = doc.to_dict()
        unique_values.add(doc_data.get(field_name, ""))
    return ["ALL"] + list(unique_values)  # Add "ALL" as the first option

def populate_dropdown_with_doc_names(collection):
    collection_ref = db.collection(collection)
    docs = collection_ref.stream()
    doc_names = ['ALL'] + [doc.id for doc in docs]
    return doc_names

# Update Treeview contents based on filters
def filter_and_update_treeview(tree, selected_route, selected_unit_type, selected_class, status):
    tree.delete(*tree.get_children())  # Clear existing rows

    fares_ref = db.collection('Fares')
    query = fares_ref
    docs = query.stream()
    for doc in docs:
        data = doc.to_dict()
        route_info = data.get('route_info', {})
        set_stat = route_info.get('status','Unknown')
        
        if ((selected_route == 'ALL' or selected_route == data.get('route')) and 
            (selected_unit_type == 'ALL' or selected_unit_type == data.get("bus_unit_type")) and 
            (selected_class == 'ALL' or selected_class == data.get('bus_class')) and 
            (status == "ALL" or status == set_stat)):

            if set_stat == "Inactive":
                row_tags = "Inactive"
            else:
                row_tags = "Active"
        
            # Insert filtered data into Treeview
            tree.insert("", "end", values=(
                f"   {data.get('route', 'N/A')}",
                f"  {data.get('bus_unit_type', 'N/A')}",
                data.get('bus_class', 'N/A'),
                f"₱. {data.get('fare', 'N/A')}",
                set_stat
            ), tags=(row_tags,))

# This function will create the bus schedule management interface inside the provided main_frame
def update_main_frame_with_fares(main_frame):
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

    canvas = ctk.CTkCanvas(main_frame)
    canvas.pack(fill="both", expand=True)

    background_image = Image.open("C:/Users/jacaj/Downloads/python project/Bus_Reservation_System2/testing grouds/image sources/background1.png")
    background_image = background_image.resize((1300, 680))
    background_image_tk = ImageTk.PhotoImage(background_image)

    canvas.create_image(0, 0, anchor="nw", image=background_image_tk)
    canvas.image = background_image_tk

    sub_frame = ctk.CTkFrame(canvas, fg_color='transparent')
    sub_frame.pack(fill="both", expand=True, padx=30, pady=30)

    sub_frame.grid_columnconfigure(0, weight=1)
    sub_frame.grid_columnconfigure(1, weight=4)
    sub_frame.grid_rowconfigure(0, weight=1)

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
            status_var.set("Inactive")
        else:
            status_var.set("ALL")
        on_dropdown_change()

    title_label = ctk.CTkLabel(sidebar_frame, text="FARES", font=("Arial Black", 28, "bold"), text_color=White, width=150)
    title_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nswe")

    route_label = ctk.CTkLabel(sidebar_frame, text="BUS ROUTES", font=("Arial Black", 16), text_color=White)
    route_label.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="nsw")

    route_dropdown = ctk.CTkComboBox(sidebar_frame, values=populate_dropdown_with_doc_names('BusRoutes'), width=130, height=35, font=("Arial", 16))
    route_dropdown.grid(row=2, column=0, padx=10, pady=(0,5), sticky="ew")

    unit_label = ctk.CTkLabel(sidebar_frame, text="UNIT TYPE", font=("Arial Black", 16), text_color=White)
    unit_label.grid(row=3, column=0, padx=10, pady=(10, 0), sticky="nsw")

    unit_dropdown = ctk.CTkComboBox(sidebar_frame, values=get_unique_field_values("Buses", "unit_type"), width=130, height=35, font=("Arial", 16))
    unit_dropdown.grid(row=4, column=0,  padx=10, pady=(0,5), sticky="ew")

    class_label = ctk.CTkLabel(sidebar_frame, text="BUS CLASS", font=("Arial Black", 16), text_color=White)
    class_label.grid(row=5, column=0, padx=10, pady=(10, 0), sticky="nsw")

    class_dropdown = ctk.CTkComboBox(sidebar_frame, values=["ALL","AC", "NAC"], width=130, height=35, font=("Arial", 16))
    class_dropdown.grid(row=6, column=0, padx=10, pady=(0,5), sticky="ew")

    status_label = ctk.CTkLabel(sidebar_frame, text="Status", font=("Arial Black", 16), text_color=White)
    status_label.grid(row=16, column=0, padx=10, pady=(10, 0), sticky="nsw")
    status_button = ctk.CTkButton( sidebar_frame, textvariable=status_var, fg_color="#fff", text_color="#191970", command=toggle_status, height=35, width=130, font=("Arial", 18, "bold"), hover_color="#9747FF")
    status_button.grid(row=17, column=0, padx=10, pady=(5,15), sticky="ew")

    content_frame = ctk.CTkFrame(sub_frame)
    content_frame.grid(row=0, column=1, sticky="nsew", padx=0)
    content_frame.grid_columnconfigure(0, weight=1)
    content_frame.grid_rowconfigure(0, weight=1)

    columns = ("ROUTE", "UNIT TYPE", "CLASS", "FARE", "STATUS")
    tree = ttk.Treeview(content_frame, columns=columns, show="headings", height=10)

    for col in columns:
        tree.heading(col, text=col)
        if col == 'UNIT TYPE' :
            tree.column(col, width=100)
        elif col == 'ROUTE':
            tree.column(col, width=150)
        elif col == 'STATUS' :
            tree.column(col, anchor="center", width=60)
        elif col == 'CLASS' :
            tree.column(col, anchor="center", width=60)
        elif col == 'FARE' :
            tree.column(col, width=80)
        else:
            tree.column(col, width=130)

    tree.grid(row=0, column=0, sticky="nsew", padx=0)
    tree.tag_configure('Inactive',  background="#cc3e40", foreground="#fff")
    tree.tag_configure('Active',  background="#000", foreground="#fff")

    scrollbar_y = ctk.CTkScrollbar(content_frame, orientation="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar_y.set)
    scrollbar_y.grid(row=0, column=1, sticky="ns", padx=0)

    # Function to update Treeview when a dropdown value is selected
    def on_dropdown_change(*args):
        selected_route = route_dropdown.get()
        selected_unit_type = unit_dropdown.get()
        selected_class = class_dropdown.get()
        status =status_var.get()
        filter_and_update_treeview(tree, selected_route, selected_unit_type, selected_class, status)

    # Set the command for dropdown changes
    route_dropdown.configure(command=on_dropdown_change)
    unit_dropdown.configure(command=on_dropdown_change)
    class_dropdown.configure(command=on_dropdown_change)

    # Fetch initial data (without filters)
    filter_and_update_treeview(tree, 'ALL', 'ALL', 'ALL', 'ALL')
