import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from firebase_config import db
from forHover import set_hover_color


heavyrow = "#ADBBDA"
lightrow = "#EDE8F5"
vio = "#191970"
white = "white"
purplr ="#9747FF"
red ="#FF3737"
lightblue ="#4682B4"
def create_bus_unit_manager(action,ccmainframe):


    for widget in ccmainframe.winfo_children():
        widget.destroy()

    mainframe=ctk.CTkFrame(ccmainframe, fg_color= vio)
    mainframe.pack(expand=True)
    mainframe.grid_columnconfigure(tuple(range(2)), weight=1)
    mainframe.grid_rowconfigure(tuple(range(10)), weight=1)

    # Title Label
    title_label = ctk.CTkLabel(mainframe, text="Unit Type:", font=("Arial", 24), text_color=white)
    title_label.grid(row=0, column=0, padx=20, pady=10, sticky="w", columnspan=2)
    
    
    treeframe = ctk.CTkFrame(mainframe, fg_color= vio)
    treeframe.grid(row=1, column=0, padx=10, pady=10, sticky="nsew", rowspan=9)

    tree_scroll = tk.Scrollbar(treeframe)
    tree_scroll.pack(side="right", fill="y")

    # Treeview for displaying unit types
    treeview = ttk.Treeview(treeframe, columns=("Unit type", "No. of Seats"), yscrollcommand=tree_scroll.set, show="headings", height=10)
    treeview.heading("Unit type", text="Unit type")
    treeview.heading("No. of Seats", text="No. of Seats")
    treeview.column("Unit type", width=200, anchor="center")
    treeview.column("No. of Seats", width=150, anchor="center")
    treeview.pack(fill="both", expand=True)

    treeview.tag_configure('oddrow', background=heavyrow)
    treeview.tag_configure('evenrow', background=lightrow)

    tree_scroll.config(command=treeview.yview)

    treeview.bind("<Double-1>", lambda e: view_layout(treeview))

    # Create button
    create_button = ctk.CTkButton(mainframe, text="Create Bus Unit", font=("Arial", 16, "bold"), width=250, height=50, command=lambda: open_create_window(mainframe, treeview), fg_color=white, text_color=vio)
    create_button.grid(row=1, column=1, padx=20, pady=10)


    # View Layout button
    view_layout_button = ctk.CTkButton(mainframe, text="View Bus Layout", font=("Arial", 16, "bold"), width=250, height=50, command=lambda: view_layout(treeview), fg_color=white, text_color=vio)
    view_layout_button.grid(row=2, column=1, padx=20, pady=10)

    # Delete button
    delete_button = ctk.CTkButton(mainframe, text="Delete Bus Unit", font=("Arial", 16, "bold"), width=250, height=50, command=lambda: delete_unit_type(treeview), fg_color=white, text_color=red)
    delete_button.grid(row=3, column=1, padx=20, pady=10)

    set_hover_color(delete_button, hover_bg_color=red, hover_text_color=white, normal_bg_color=white, normal_text_color=red)
    set_hover_color(view_layout_button, hover_bg_color=lightblue, hover_text_color=white, normal_bg_color=white, normal_text_color=vio)
    set_hover_color(create_button, hover_bg_color="#6C48C5", hover_text_color="#fff", normal_bg_color=white, normal_text_color=vio)

    # Populate the Treeview with data from Firestore
    populate_treeview(treeview)

def populate_treeview(treeview):
    # Clear existing entries in the Treeview
    for item in treeview.get_children():
        treeview.delete(item)

    # Fetch unit types from Firestore
    try:
        unit_types_ref = db.collection('Unit_type').stream()
        count = 1
        for doc in unit_types_ref:
            data = doc.to_dict()
            no_of_seats = data.get('no_of_seat', 0)
            
            row_tag = "oddrow" if count % 2 == 0 else "evenrow"
            treeview.insert("", "end", doc.id, values=(doc.id, no_of_seats),tags=(row_tag,))

            count +=1 
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch unit types: {e}")



def open_create_window(mainframe, treeview):
    create_window = ctk.CTkToplevel(mainframe)
    create_window.geometry("250x120")
    create_window.title("Create Unit Type")
    create_window.attributes("-topmost", True)
    create_window.configure(fg_color="#021526")

    # Input for unit_type ID
    unit_type_id_entry = ctk.CTkEntry(create_window, placeholder_text="Enter Unit Type ID", text_color="#191970", placeholder_text_color="#5A72A0")
    unit_type_id_entry.pack(padx=10, pady=10)

    # Set layout button
    set_layout_button = ctk.CTkButton(create_window, text="Set Layout", command=lambda: set_layout(create_window, unit_type_id_entry.get(), treeview), fg_color="#fff",text_color="#191970")
    set_layout_button.pack(padx=10, pady=10)
    set_hover_color(set_layout_button, "#4682b4", "#fff","#fff", "#191970")

def set_layout(create_window, unit_type_id, treeview):
    create_window.destroy()
    layout_window = ctk.CTkToplevel()
    layout_window.title("Set Layout")
    layout_window.attributes("-topmost", True)
    layout_window.configure(fg_color="#021526")

    buttons = {}
    selected_buttons = []

    # Create the 5x12 grid of buttons
    for row in range(16):  # 12 rows (a-l)
        for col in range(7):  # 5 columns (1-5)
            button_name = f"{col + 1}{chr(97 + row)}"  # e.g., 1a, 2a, ...
            button = ctk.CTkButton(layout_window, text=button_name, width=50, command=lambda name=button_name: toggle_button(name, buttons, selected_buttons), fg_color="#4682B4")
            button.grid(row=row, column=col, padx=5, pady=5)
            buttons[button_name] = button

    save_button = ctk.CTkButton(layout_window, text="Save", command=lambda: save_selection(unit_type_id, selected_buttons, treeview, layout_window), fg_color="#e2e2b6", hover_color="#6C48C5", text_color="#191970")
    save_button.grid(row=17, columnspan=7, padx=10, pady=10)
    set_hover_color(save_button,"#6C48C5", "#fff", "#e2e2b6", "#191970"  )

def toggle_button(name, buttons, selected_buttons):
    button = buttons[name]
    if name in selected_buttons:
        button.configure(fg_color="#4682B4")  # Set to deselected color
        selected_buttons.remove(name)
    else:
        button.configure(fg_color="red")  # Set to selected color
        selected_buttons.append(name)

def save_selection(unit_type_id, selected_buttons, treeview, layout_window):
    if not unit_type_id:
        messagebox.showwarning("Input Error", "Please enter a Unit Type ID.")
        return

    # Prepare data to insert into Firestore
    no_of_seat = len(selected_buttons)
    seats_map = {name: "Available" for name in selected_buttons}

    # Create a document in the 'Unit_type' collection
    data = {
        'id': unit_type_id,
        'no_of_seat': no_of_seat,
        'seats': seats_map
    }

    try:
        db.collection('Unit_type').document(unit_type_id).set(data)
        layout_window.destroy()
        messagebox.showinfo("Success", "Unit type data saved successfully.")
        populate_treeview(treeview)  # Refresh the Treeview
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save data: {e}")

def view_layout(treeview):
    selected_item = treeview.selection()
    if not selected_item:
        messagebox.showwarning("Selection Error", "Please select a unit type from the list.")
        return

    unit_type_id = selected_item[0]
    create_seat_selection_window(unit_type_id)




def delete_unit_type(treeview):
    selected_item = treeview.selection()
    unit_type_id = selected_item[0]

    if not selected_item:
        messagebox.showwarning("Selection Error", "Please select a unit type to delete.")
        return

    delete = messagebox.askyesno("Item Deletion:", f"Do you want to delete bus unit : {unit_type_id}")
    if delete: 
        try:
            db.collection('Unit_type').document(unit_type_id).delete()
            messagebox.showinfo("Success", f"Unit type {unit_type_id} deleted successfully.")
            populate_treeview(treeview)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete unit type: {e}")
    else:
        return

def create_seat_selection_window(bus_id):
    # Use Toplevel instead of Tk to avoid creating another root window
    root = tk.Toplevel()
    root.title("View Seat Layout")
    root.config(background="#E2E2B6")
    
    def fetch_seat_data(bus_id):
        try:
            unit_type_ref = db.collection('Unit_type').document(bus_id)
            unit_type_doc = unit_type_ref.get()
            if unit_type_doc.exists:  # Make sure to call exists correctly
                return unit_type_doc.to_dict().get('seats', {})
            else:
                print("No such document!")
                return {}  # Return an empty dictionary if document does not exist
        except Exception as e:
            print(f"Error fetching data: {e}")
            return {}

    seat_buttons = {}
    seat_status = fetch_seat_data(bus_id)  # Fetch seat status from Firestore

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
        else:
            button.config(command=lambda s=seat_id: reserve_seat(s), bg="#03346E", foreground="#fff")  # Available seats

        button.grid(row=row, column=col, padx=5, pady=5)

    root.mainloop()

def reserve_seat(seat_id):
    print(f"Reserving seat: {seat_id}")
    # Add your reservation logic here


"""app = ctk.CTk()
app.attributes("-fullscreen", True)  # Set the window to full screen
app.title("Admin Dashboard")
frame = ctk.CTkFrame(app, fg_color="blue")
frame.pack(expand=True)
create_bus_unit_manager(frame)

deep="#7091E6"

app.mainloop()"""