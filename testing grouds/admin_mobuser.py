#imports for the GUi (custom tkinter), treeview table(ttk), and database connection
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from firebase_config import db
from google.cloud.firestore import Increment
import firebase_admin
from firebase_admin import credentials, auth, exceptions
from forHover import set_hover_color

current_email = None
current_phone = None
current_user_id = None

heavyrow = "#ADBBDA"
lightrow = "#EDE8F5"
vio = "#191970"
white = "white"
purplr ="#9747FF"
red ="#FF3737"
lightblue ="#4682B4"
vin="#03346E"

# Function to handle the Manage Users display on the Admin app window (updating the main_content_frame)
def manage_users(action, main_content_frame):
    # Clear the current content in the main_content_frame
    for widget in main_content_frame.winfo_children():
        widget.destroy()

    # Frame for the title
    c_frame = ctk.CTkFrame(main_content_frame, corner_radius=0, fg_color=vin)
    c_frame.pack(fill="x")

    # Title bar
    button_frame = ctk.CTkFrame(c_frame, corner_radius=0, fg_color=vin)
    button_frame.pack(fill="x")
    title_label = ctk.CTkLabel(button_frame, text="Manage Mobile Users", text_color=white, font=("Arial", 23, "bold"))
    title_label.pack(side="left", pady=(10,10), padx=(20, 10))

    # Create button for adding new users
    create_button = ctk.CTkButton(button_frame, text="Create User", fg_color=white, text_color=vio,  font=("Arial", 16, "bold"), height=35,
                                  command=lambda: create_user_window(treeview))
    create_button.pack(side="left", padx=5)

    set_hover_color(create_button, hover_bg_color=purplr, hover_text_color=white, normal_bg_color=white, normal_text_color=vio)

    # Search and filter frame
    filter_frame = ctk.CTkFrame(c_frame, corner_radius=0, fg_color=vin)
    filter_frame.pack(fill="x")
    filter_frame.grid_columnconfigure(tuple(range(7)), weight=1)

    def new (*args):
        global current_email, current_phone, current_user_id
        current_user_id = user_id_entry.get()
        current_email = email_entry.get()
        current_phone = phone_entry.get()
        search_user(treeview)

    # Search boxes and search buttons
    email_label = ctk.CTkLabel(filter_frame, text="Search by Email", text_color="white")
    email_label.grid(row=0, column=0, padx=(25,5), pady=(5,0), sticky="w")
    email_entry = ctk.CTkEntry(filter_frame, placeholder_text="Search by Email", width=160, text_color="#191970", placeholder_text_color="#6eacda")
    email_entry.grid(row=1, column=0, padx=(20,5), pady=(0,10), sticky="w")
    email_entry.bind("<Return>",new)

    phone_label = ctk.CTkLabel(filter_frame, text="Search by Phone", text_color="white")
    phone_label.grid(row=0, column=1, padx=10, pady=(5,0), sticky="w")
    phone_entry = ctk.CTkEntry(filter_frame, placeholder_text="Search by Phone", width=170, text_color="#191970", placeholder_text_color="#6eacda")
    phone_entry.grid(row=1, column=1, padx=5, pady=(0,10), sticky="w")
    phone_entry.bind("<Return>", new)

    user_id_label = ctk.CTkLabel(filter_frame, text="Search by User ID", text_color="white")
    user_id_label.grid(row=0, column=2, padx=10, pady=(5,0), sticky="w")
    user_id_entry = ctk.CTkEntry(filter_frame, placeholder_text="Search by User ID", width=170, text_color="#191970", placeholder_text_color="#6eacda")
    user_id_entry.grid(row=1, column=2, padx=5, pady=(0,10), sticky="w")
    user_id_entry.bind("<Return>",new)

    # Buttons for Edit and Delete
    delete_button = ctk.CTkButton(filter_frame, text="Delete", fg_color=white, text_color=red, font=("Arial", 16, "bold"), height=35, command= lambda: delete_user(treeview))
    delete_button.grid(row=0, rowspan=2, column=7, padx=(5,20), pady=(25,10), sticky="e")

    edit_button = ctk.CTkButton(filter_frame, text="Edit", fg_color=white, text_color=vio, font=("Arial", 16, "bold"), height=35, command= lambda: edit_user(treeview))
    edit_button.grid(row=0, rowspan=2, column=6, padx=5, pady=(25,10), sticky="e")

    set_hover_color(delete_button, hover_bg_color=red, hover_text_color=white, normal_bg_color=white, normal_text_color=red)
    set_hover_color(edit_button, hover_bg_color=lightblue, hover_text_color=white, normal_bg_color=white, normal_text_color=vio)

    columns = ("No","Email", "First Name", "Last Name", "Birth Date",  "Phone No.","User ID")
    # Treeview frame for displaying MobileUser data
    treeview_frame = ctk.CTkFrame(main_content_frame)
    treeview_frame.pack(fill="both", expand=True)

    # Scrollbar for vertical and horizontal scrolling
    vertical_scroll = tk.Scrollbar(treeview_frame, orient="vertical")
    vertical_scroll.pack(side="right", fill="y")

    treeview = ttk.Treeview(treeview_frame, columns=columns, yscrollcommand=vertical_scroll.set,  show="headings")
    treeview.tag_configure('oddrow', background=heavyrow)
    treeview.tag_configure('evenrow', background=lightrow)

    for col in columns:
        treeview.heading(col, text=col)
        if col =="First Name" or col =="Last Name" :
            treeview.column(col, width=120)
        elif col =="Phone No." :
            treeview.column(col, width=60)
        elif col =="Birth Date" :
            treeview.column(col, width=40)
        elif col =="User ID" or col == "Email" :
            treeview.column(col, width=140)
        elif col =="No" :
            treeview.column(col, width=20)
        else:
            treeview.column(col, width=150)
    
    treeview.pack(fill="both", expand=True)
    # configure scrollbars
    vertical_scroll.config(command=treeview.yview)
    # Fetch and display MobileUser data from Firebase Firestore
    search_user(treeview)


def search_user(treeview):
    global current_email, current_phone, current_user_id
    count = 1
    # Clear the current data in the treeview
    for row in treeview.get_children():
        treeview.delete(row)
    # Start with a base query
    query_ref = db.collection("MobileUser")

    # Apply the most restrictive query first
    if current_email:
        query_ref = query_ref.where("email", ">=", current_email).where("email", "<=", current_email + "\uf8ff")
    elif current_phone:
        query_ref = query_ref.where("phone", ">=", current_phone).where("phone", "<=", current_phone + "\uf8ff")
    elif current_user_id:
        query_ref = query_ref.where("user_id", ">=", current_user_id).where("user_id", "<=", current_user_id + "\uf8ff")

    # Fetch the initial data from Firestore
    users_ref = query_ref.get()

    # Filter results locally for additional conditions
    filtered_users = []
    for user in users_ref:
        user_data = user.to_dict()
        # Check other conditions locally
        if current_phone and current_phone not in user_data.get("phone", ""):
            continue
        if current_user_id and current_user_id not in user_data.get("user_id", ""):
            continue
        # Add to the filtered list if all conditions are met
        filtered_users.append(user_data)

    # Display the filtered data in the Treeview
    for user_data in filtered_users:
        row_tag = "oddrow" if count % 2 == 0 else "evenrow"
        treeview.insert("", "end", values=(
            count,
            user_data.get("email"),
            user_data.get("first_name"),
            user_data.get("last_name"),
            user_data.get("birthday"),
            user_data.get("phone"),
            user_data.get("user_id"),
        ), tags=(row_tag,))
        count += 1




# Function to create a new user window
def create_user_window(treeview):
    create_window = ctk.CTkToplevel()
    create_window.title("Create New User")
    create_window.geometry("400x360")

    # Make the window stay on top
    create_window.attributes("-topmost", True)
    create_window.configure(fg_color=("#03346E"))

    # Function to validate phone number input
    def validate_phone_input(value):
        return value.isdigit() and len(value) <= 11 or value == ""
    phone_vcmd = create_window.register(validate_phone_input)

    # Function to validate reward points input
    def validate_reward_points_input(value):
        if value == "":
            return True
        try:
            float(value)
            return True
        except ValueError:
            return False
    reward_points_vcmd = create_window.register(validate_reward_points_input)

    # Function to create labeled entry fields with validation
    def create_labeled_entry(parent, label_text, placeholder_text, validation_command=None):
        frame = ctk.CTkFrame(parent, fg_color="#03346E")
        frame.pack(pady=(10, 5), fill="x", padx=40)

        entry = ctk.CTkEntry(frame, placeholder_text=placeholder_text, fg_color="#f0f0f0", text_color="#191970", width=200)
        if validation_command:
            entry.configure(validate="key", validatecommand=validation_command)
        entry.pack(side="right")

        label = ctk.CTkLabel(frame, text=label_text, text_color="#E2E2B6")
        label.pack(side="right", padx=(0, 25))
        return entry

    label = ctk.CTkLabel(create_window, text="Creating User Account: ", text_color="#E2E2B6")
    label.pack(pady=10)

    # Create labeled entries
    first_name_entry = create_labeled_entry(create_window, "First Name:", "First Name")
    last_name_entry = create_labeled_entry(create_window, "Last Name:", "Last Name")
    birthday_entry = create_labeled_entry(create_window, "Birthday:", "Birthday")
    email_entry = create_labeled_entry(create_window, "Email:", "Email")
    phone_entry = create_labeled_entry(create_window, "Phone:", "Phone", validation_command=(phone_vcmd, "%P"))
    reward_points_entry = create_labeled_entry(create_window, "Reward Points:", "Reward Points", validation_command=(reward_points_vcmd, "%P"))
    reward_points_entry.insert(0, "0.0")  # Set initial value for reward points

    submit_button = ctk.CTkButton(
        create_window, 
        text="Submit", 
        text_color="#191970", 
        fg_color="#E2E2B6", 
        hover_color="#6EACDA",
        command=lambda: add_user(create_window, treeview)
    )
    submit_button.pack(pady=10)

    # Function to add a user to Firebase Firestore
    def add_user(window, treeview):
        first_name = first_name_entry.get()
        last_name = last_name_entry.get()
        birthday = birthday_entry.get()
        email1 = email_entry.get()
        phone = phone_entry.get()
        reward_points = reward_points_entry.get()
        password = "123456"

        if all([first_name, last_name, birthday, email1, phone, reward_points]):
            try:
                if not all([first_name, last_name, birthday, email1, phone, reward_points]):
                    messagebox.showerror("Error", "All fields are required.")
                    return
                # Email validation
                email_input = email1
                if not email_input.endswith("@gmail.com"):
                    messagebox.showerror("Error", "Please provide a valid gmail address '@gmail.com'.")
                    return

                def email_exists(email1):
                    users = db.collection("MobileUser").where("email", "==", email1).get()
                    return len(users) > 0

                if email_exists(email1):
                    messagebox.showerror("Error", "Email already exists. Please use a different email.")
                    return

                # Create the user with Firebase Authentication
                user = auth.create_user(
                    email=email1,
                    password=password
                )
                # Add user to Firebase Firestore
                db.collection("MobileUser").document(user.uid).set({
                    "user_id": user.uid,
                    "first_name": first_name,
                    "last_name": last_name,
                    "birthday": birthday,
                    "email": email1,
                    "phone": int(phone),  # Ensure phone is stored as an integer
                    "reward_points": float(reward_points),  # Ensure reward points are stored as a float
                    "role": "user",
                })
                doc_ref = db.collection("GenCounter").document("total_Mob")
                doc_ref.update({
                    "count": Increment(1)
                })

                # Close the window and refresh the Treeview
                window.destroy()
                search_user(treeview)  # Refresh the Treeview with updated data
                messagebox.showinfo("Success", "User created successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add MobileUser: {e}")
        else:
            messagebox.showerror("Error", "Please fill in all fields.")






# Function to handle editing a selected user
def edit_user(treeview):
    selected_item = treeview.selection()  # Get selected row
    if not selected_item:
        messagebox.showerror("Error", "Please select a user to edit.")
        return
    # Fetch selected user data from the Treeview
    values = treeview.item(selected_item, "values")
    # DEBUG: Print the fetched user_id to confirm it's correct
    print("Fetched user_id:", values[6])

    user_doc = db.collection("MobileUser").document(values[6]).get()
    if not user_doc.exists:
        messagebox.showerror("Error", "Selected User document is not exsisting in the system.")
        return
    user_data = user_doc.to_dict()

    # Create the edit window
    edit_window = ctk.CTkToplevel()
    edit_window.title("Edit User")
    edit_window.geometry("400x360")
    edit_window.attributes("-topmost", True)
    edit_window.configure(fg_color="#03346E")

    # Function to validate phone number input
    def validate_phone_input(value):
        return value.isdigit() and len(value) <= 11 or value == ""
    phone_vcmd = edit_window.register(validate_phone_input)

    # Function to validate reward points input
    def validate_reward_points_input(value):
        if value == "":
            return True
        try:
            float(value)
            return True
        except ValueError:
            return False
    reward_points_vcmd = edit_window.register(validate_reward_points_input)

    # Function to create labeled entry fields
    def create_labeled_entry(parent, label_text, placeholder_text, initial_value="", is_disabled=False, validation_command=None):
        frame = ctk.CTkFrame(parent, fg_color="#03346E")
        frame.pack( fill="x", padx=40, pady=(10,5))

        label = ctk.CTkLabel(frame, text=label_text, bg_color="#03346E", text_color="#E2E2B6")
        label.pack(side="left", padx=(5, 25))
        
        entry = ctk.CTkEntry(frame, placeholder_text=placeholder_text, fg_color="#f0f0f0", text_color="#191970", width=200, validate="key", 
        validatecommand=(validation_command, "%P") if validation_command else None)
        entry.insert(0, initial_value)
        entry.pack(side="right" )
        
        if is_disabled:
            entry.configure(state="disabled")  # Disable the entry field again
        return entry

    # Create labeled entries
    user_id_entry = create_labeled_entry(edit_window, "User ID:", "User ID", values[6], is_disabled=True)
    first_name_entry = create_labeled_entry(edit_window, "First Name:", "First Name", user_data['first_name'])
    last_name_entry = create_labeled_entry(edit_window, "Last Name:", "Last Name", user_data['last_name'])
    birthday_entry = create_labeled_entry(edit_window, "Birthday:", "Birthday", user_data['birthday'])
    email_entry = create_labeled_entry(edit_window, "Email:", "Email", user_data['email'], is_disabled=True)
    phone_entry = create_labeled_entry(edit_window, "Phone:", "Phone", user_data['phone'], validation_command=phone_vcmd)
    reward_points_entry = create_labeled_entry(edit_window, "Reward Points:", "Reward Points", user_data['reward_points'], validation_command=reward_points_vcmd)

    # Save button to update the data
    save_button = ctk.CTkButton(edit_window, text="Save", command=lambda: save_edited_user(values[6], edit_window, treeview), fg_color="#E2E2B6", text_color="#191970", 
    
    hover_color="#6EACDA")
    save_button.pack(pady=10)

    # Function to save the edited user data to the database and update the Treeview
    def save_edited_user(user_id,  window, treeview):
        # DEBUG: Print the user_id before updating the Firestore document
        print("Saving user with ID:", user_id)

        if not all([first_name_entry.get(), last_name_entry.get(), birthday_entry.get(), phone_entry.get(), reward_points_entry.get()]):
            messagebox.showerror("Error", "All fields are required.")
            return

        # Update the user document in Firestore
        try:
            db.collection("MobileUser").document(user_id).update({
                "first_name": first_name_entry.get(),
                "last_name": last_name_entry.get(),
                "birthday": birthday_entry.get(),
                "phone": phone_entry.get(),
                "reward_points": float(reward_points_entry.get())
            })
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update user: {e}")
            return
        
        # Close the edit window and refresh the Treeview with the updated data
        search_user(treeview)
        # Function to select the item based on matching BusID
        def select_item_by_bus_id(bus_id):
            for item in treeview.get_children():
                item_values = treeview.item(item, "values")
                if item_values[1] == bus_id:  # Assuming column 1 is BusID
                    treeview.selection_set(item)
                    treeview.see(item)  # Scroll to the selected item
                    break  # Exit after finding the match

        select_item_by_bus_id(values[1])
        window.destroy()
        messagebox.showinfo("Success", "User updated successfully!")



# Function to handle deleting a selected user
def delete_user(treeview):
    selected_item = treeview.selection()  # Get selected row
    if not selected_item:
        messagebox.showerror("Error", "Please select a user to delete.")
        return
    # Fetch the selected user data (specifically the user_id)
    values = treeview.item(selected_item, "values")
    user_id = values[6]
    email = values[1]

    # Confirm the deletion
    confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete user:  {email} ? \n\nThis process will delete all account data and Authentication.\n\n UID: {user_id}")
    if not confirm:
        return

    # Delete the user document from Firestore
    try:
        user_doc = db.collection("MobileUser").document(user_id).get()

        if user_doc.exists:
            auth.delete_user(user_id)
            db.collection("MobileUser").document(user_id).delete()
            # Refresh the Treeview after deletion
            search_user(treeview)
            messagebox.showinfo("Success", f"User: {email} is deleted successfully! \n\n UID: {user_id}")
        else:
            messagebox.showerror("Error", f"User document with ID:  {user_id} does not exist.")
    except exceptions.FirebaseError as e:
        messagebox.showerror("Error", f"Error deleting user account: {e}")
