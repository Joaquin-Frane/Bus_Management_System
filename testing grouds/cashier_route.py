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
pearl="#D9D9D9"

def get_unique_field_values(collection_name, field_name):
    docs = db.collection(collection_name).stream()
    unique_values = set()
    for doc in docs:
        doc_data = doc.to_dict()
        unique_values.add(doc_data.get(field_name, ""))
    return ["ALL"] + list(unique_values)  # Add "ALL" as the first option

def update_main_frame_with_routes(main_frame):
    # Clear main_frame content first
    for widget in main_frame.winfo_children():
        widget.destroy()

    # Design in Treeview
    style = ttk.Style()
    # Themes to change the general themes of treeview objs (can be downloaded or created)
    style.theme_use("clam")  # clam style
    style.configure("Treeview", background="transparent", foreground=pearl, rowheight=40, fieldbackground="transparent", font=("Arial", 12)) # Configure the header (font, etc.)
    style.configure("Treeview.Heading", font=("Arial", 14))# Change selected color (background and foreground when selected)
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

    title_label = ctk.CTkLabel(sidebar_frame, text="ROUTES", font=("Arial Black", 28, "bold"), text_color=White, width=150)
    title_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nswe")
  
    boarding_label = ctk.CTkLabel(sidebar_frame, text="BOARDING POINTS", font=("Arial Black", 16), text_color=White)
    boarding_label.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="nsw")
    boarding_dropdown = ctk.CTkComboBox(sidebar_frame, values=get_unique_field_values("BusRoutes", "boarding_point"), font=("Arial", 16), width=130, height=35)
    boarding_dropdown.grid(row=2, column=0, padx=10, pady=(0,5), sticky="ew")

    dropping_label = ctk.CTkLabel(sidebar_frame, text="DROPPING POINT", font=("Arial Black", 16), text_color=White)
    dropping_label.grid(row=3, column=0, padx=10, pady=(10, 0), sticky="nsw")
    dropping_dropdown = ctk.CTkComboBox(sidebar_frame, values=get_unique_field_values("BusRoutes", "dropping_point"), font=("Arial", 16), width=130, height=35)
    dropping_dropdown.grid(row=4, column=0, padx=10, pady=(0,5), sticky="ew")

    status_label = ctk.CTkLabel(sidebar_frame, text="Status", font=("Arial Black", 16), text_color=White)
    status_label.grid(row=16, column=0, padx=10, pady=(10, 0), sticky="nsw")
    status_button = ctk.CTkButton( sidebar_frame, textvariable=status_var, fg_color="#fff", text_color="#191970", command=toggle_status, height=35, width=130, font=("Arial", 18, "bold"), hover_color="#9747FF")
    status_button.grid(row=17, column=0, padx=10, pady=(5,15), sticky="ew")

    content_frame = ctk.CTkFrame(sub_frame)
    content_frame.grid(row=0, column=1, sticky="nsew", padx=0)
    content_frame.grid_columnconfigure(0, weight=1)
    content_frame.grid_rowconfigure(0, weight=1)

    columns = ("ROUTE", "BOARDING", "DROPPING", "STATUS")
    tree = ttk.Treeview(content_frame, columns=columns, show="headings", height=10)

    for col in columns:
        tree.heading(col, text=col)
        if col == 'BOARDING' or col == 'DROPPING':
            tree.column(col, width=100, anchor="center")
        elif col == 'ROUTE':
            tree.column(col, width=150)
        elif col == 'STATUS' :
            tree.column(col, anchor="center", width=100)
        else:
            tree.column(col, width=130)
            
    tree.grid(row=0, column=0, sticky="nsew", padx=0)
    tree.tag_configure('Inactive',  background="#cc3e40", foreground="#fff")
    tree.tag_configure('Active',  background="#000", foreground="#fff")

    scrollbar_y = ctk.CTkScrollbar(content_frame, orientation="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar_y.set)
    scrollbar_y.grid(row=0, column=1, sticky="ns", padx=0)

    def populate_treeview():
        # Clear existing rows in the Treeview
        for row in tree.get_children():
            tree.delete(row)
        # Get selected filter values
        selected_status = status_var.get()
        selected_boarding = boarding_dropdown.get()
        selected_dropping = dropping_dropdown.get()
        # Fetch data from Firestore
        data = db.collection('BusRoutes').stream()

        # Insert filtered data into the Treeview
        for doc in data:
            doc_data = doc.to_dict()  # Get document data (fields)
            route = doc.id  # Extract the document ID (route name)

            # Apply filters
            if ((selected_status == "ALL" or doc_data.get("status") == selected_status) and 
                (selected_boarding == "ALL" or  doc_data.get("boarding_point") == selected_boarding) and 
                (selected_dropping == "ALL" or doc_data.get("dropping_point") == selected_dropping)):
                # Set row tag based on status
                row_tags = "Inactive" if doc_data.get("status") == "Inactive" else "Active"

                # Insert the row into the Treeview
                tree.insert("", "end", values=(
                    f"  {route}", 
                    doc_data.get("boarding_point"), 
                    doc_data.get("dropping_point"), 
                    doc_data.get("status")
                ), tags=(row_tags,))

    # Add event listeners to dropdowns and status button
    def on_filter_change(*args):
        populate_treeview()

    # Attach event listeners
    status_var.trace_add("write", on_filter_change)
    boarding_dropdown.configure(command=on_filter_change)
    dropping_dropdown.configure(command=on_filter_change)

    populate_treeview()



