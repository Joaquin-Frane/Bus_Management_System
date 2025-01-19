import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from firebase_config import db
import firebase_admin
from firebase_admin import auth, credentials, exceptions

from tkinter import ttk
from PIL import Image, ImageTk  # Ensure you have PIL (Pillow) installed

from forHover import set_hover_color

# Define color variables
Red = "#8697C4"
White = "white"
Black = "#191970"
Gray = "#2D2D2D"
pearl="#D9D9D9"
blue = "#8697C4"


def change_password(document_name):
    # Create a new window for password change
    password_window = ctk.CTkToplevel()  # Creates a new top-level window
    password_window.title("Change Password")
    password_window.geometry("400x315")  # Set the window size
    
    # Set the window to always stay on top
    password_window.attributes("-topmost", True)

    # Create a frame for the password change form inside the new window
    password_frame = ctk.CTkFrame(password_window, fg_color="#021526")
    password_frame.pack(fill='both', expand=True, padx=10, pady=10)

    password_frame.columnconfigure(tuple(range(2)), weight=1)

    # Load images for the eye icons
    eye_open_image = ImageTk.PhotoImage(Image.open("Bus_Reservation_System2/testing grouds/image sources/show3.png").resize((20, 20)))
    eye_closed_image = ImageTk.PhotoImage(Image.open("Bus_Reservation_System2/testing grouds/image sources/hide5.png").resize((20, 20)))

    # Function to toggle password visibility
    def toggle_visibility(entry, button, is_visible):
        if is_visible[0]:  # If the text is currently visible
            entry.configure(show="*")  # Mask the text
            button.configure(image=eye_open_image)  # Switch to the 'open eye' icon
        else:  # If the text is currently masked
            entry.configure(show="")  # Show the text
            button.configure(image=eye_closed_image)  # Switch to the 'closed eye' icon
        is_visible[0] = not is_visible[0]  # Toggle the visibility state

    # Labels, Entry objects, and toggle buttons for New Password
    lbl = ctk.CTkLabel(password_frame, text="Change Password", font=("Arial", 18, "bold"), text_color="white")
    lbl.grid(row=0, column=0, columnspan=2, pady=10, sticky="nwse")

    # Labels, Entry objects, and toggle buttons for New Password
    lbl_new_password = ctk.CTkLabel(password_frame, text="Enter New Password:", font=("Arial", 14), text_color="white")
    lbl_new_password.grid(row=1, column=0, pady=10, sticky="nwse")
    
    entry_new_password = ctk.CTkEntry(password_frame, show="*", text_color="#191970", width=200)
    entry_new_password.grid(row=2, column=0, padx=(0, 10), pady=5, sticky="e")
    
    new_password_visibility = [False]  # Track visibility state for the new password
    btn_toggle_new_password = ctk.CTkButton( password_frame, text="", fg_color="#E2E2B6", hover_color="#8697C4", image=eye_open_image, width=30, height=30, command=lambda: toggle_visibility(entry_new_password, btn_toggle_new_password, new_password_visibility))
    btn_toggle_new_password.grid(row=2, column=1, pady=5, sticky="w")

    # Labels, Entry objects, and toggle buttons for Retype Password
    lbl_retype_password = ctk.CTkLabel(password_frame, text="Retype New Password:", font=("Arial", 14), text_color="white")
    lbl_retype_password.grid(row=3, column=0, pady=10, sticky="nwse")
    
    entry_retype_password = ctk.CTkEntry(password_frame, show="*", text_color="#191970", width=200)
    entry_retype_password.grid(row=4, column=0, padx=(0, 10), pady=5, sticky="e")
    
    retype_password_visibility = [False]  # Track visibility state for the retype password
    btn_toggle_retype_password = ctk.CTkButton(password_frame, text="", fg_color="#E2E2B6", hover_color="#8697C4", image=eye_open_image, width=30, height=30, command=lambda: toggle_visibility(entry_retype_password, btn_toggle_retype_password, retype_password_visibility))
    btn_toggle_retype_password.grid(row=4, column=1, pady=5, sticky="w")

    # Function to validate and save the new password
    def save_new_password():
        new_password = entry_new_password.get()
        retype_password = entry_retype_password.get()

        # Check if new passwords match
        if new_password != retype_password:
            messagebox.showerror("Error", "New Password and Retype Password do not match!")
            return
        
        # Fetch the document for the admin and validate the passKey
        admin_ref = db.collection('Admin').document(document_name)
        admin_doc = admin_ref.get()

        if admin_doc.exists:
            admin_data = admin_doc.to_dict()
            email = admin_data.get("email", None)

            try:
                # Update the password
                auth.update_user(document_name, password=new_password)
                password_window.destroy()  # Close the window after success
                messagebox.showinfo("Success", f"Successfully updated password for user with Email: {email}")

            except exceptions.FirebaseError as e:
                messagebox.showerror("Error", f"Error updating password: {e}")
        else:
            messagebox.showerror("Error", "Document not found!")
        
    # Save button to trigger password change logic
    btn_save = ctk.CTkButton(password_frame, text="Save", fg_color="white", text_color="black", font=("Arial", 14, "bold"), command=save_new_password, hover_color="#9747FF")
    btn_save.grid(row=5, column=0, columnspan=2, pady=20)
    set_hover_color(btn_save, "#9747FF", "#fff", "#fff", "#191970")

    


    



def display_admin_profile(action, parent, document_name):
    # Destroy children widgets inside main_frame
    for widget in parent.winfo_children():
        widget.destroy()

    # Fetch data from Firestore and populate the entry fields
    admin_ref = db.collection('Admin').document(document_name)
    admin_doc = admin_ref.get()

    # Create a canvas inside the canvas_frame
    canvas = ctk.CTkFrame(parent, fg_color="#021526", corner_radius=0)
    canvas.pack(fill="both", expand=True)

    # Create a frame inside the canvas to hold the content
    profile_frame = ctk.CTkFrame(canvas, fg_color="#03346E")
    profile_frame.pack(fill="both", expand=True, pady=40, padx=40)

    # Row and column configuration
    profile_frame.grid_rowconfigure(0, weight=1)
    profile_frame.grid_rowconfigure(1, weight=1)
    profile_frame.grid_rowconfigure(2, weight=1)
    profile_frame.grid_rowconfigure(3, weight=1)
    profile_frame.grid_rowconfigure(4, weight=1)
    profile_frame.grid_rowconfigure(5, weight=1)
    profile_frame.grid_rowconfigure(6, weight=1)
    profile_frame.grid_columnconfigure(0, weight=1)
    profile_frame.grid_columnconfigure(1, weight=1)
    profile_frame.grid_columnconfigure(2, weight=1)

    # Cashier Profile ID and Service Terminal
    id_label = ctk.CTkLabel(profile_frame, text="PROFILE", text_color="white", font=("Arial", 24, "bold"))
    id_label.grid(row=0, column=0, padx=20, pady=(30, 0), sticky="nw")

    terminal_label = ctk.CTkLabel(profile_frame, text=f"USER : {admin_doc.id}", text_color="white", font=("Arial", 24, "bold"))
    terminal_label.grid(row=0, column=1, pady=(30, 0), sticky="nw")

    # Create the name_frame for the name fields
    name_frame = ctk.CTkFrame(profile_frame, fg_color="#03346e")
    name_frame.grid(row=1, column=0, columnspan=2, sticky="nesw")

    # Name Section (First Name, Last Name, M.I.)
    name_label = ctk.CTkLabel(name_frame, text="NAME: ", text_color="white", font=("Arial", 24))
    name_label.grid(row=0, column=0, padx=20, pady=(10, 0), sticky="nws")

    first_name_entry = ctk.CTkEntry(name_frame, width=320, height=40, text_color="#191970", font=("Arial", 14))
    first_name_entry.grid(row=0, column=0, padx=(110, 20), pady=(10, 5), sticky="nw")

    last_name_entry = ctk.CTkEntry(name_frame, width=320, height=40, text_color="#191970", font=("Arial", 14))
    last_name_entry.grid(row=0, column=1, padx=(0, 20), pady=(10, 5), sticky="nw")

    mi_entry = ctk.CTkEntry(name_frame, width=100, height=40, text_color="#191970", font=("Arial", 14))
    mi_entry.grid(row=0, column=2, padx=(0, 20), pady=(10, 5), sticky="nw")

    # Labels under the name fields
    first_name_label = ctk.CTkLabel(name_frame, text="FIRST NAME", text_color="white", font=("Arial", 16))
    first_name_label.grid(row=1, column=0, padx=(115, 22), pady=(0, 5), sticky="nw")

    last_name_label = ctk.CTkLabel(name_frame, text="LAST NAME", text_color="white", font=("Arial", 16))
    last_name_label.grid(row=1, column=1, padx=(0, 102), pady=(0, 5), sticky="nw")

    mi_label = ctk.CTkLabel(name_frame, text="M.I.", text_color="white", font=("Arial", 16))
    mi_label.grid(row=1, column=2, padx=(0, 20), pady=(0, 5), sticky="nw")


    # Create contact_frame for phone, email, and address fields
    contact_frame = ctk.CTkFrame(profile_frame, fg_color="#03346e")
    contact_frame.grid(row=2, column=0, padx=20, columnspan=3, pady=(0, 0), sticky="w")

     # Cashier Profile ID and Service Terminal
    contact_label = ctk.CTkLabel(contact_frame, text="Contact Info.", text_color="white", font=("Arial", 24, "bold"))
    contact_label.grid(row=0, column=0, padx=20, pady=(0, 20), sticky="nw")

    # Phone Number Section
    phone_label = ctk.CTkLabel(contact_frame, text="PHONE NUMBER :", text_color="white", font=("Arial", 16), anchor="e")
    phone_label.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="e")

    phone_entry = ctk.CTkEntry(contact_frame, width=300, height=40, text_color="#191970", font=("Arial", 14))
    phone_entry.grid(row=1, column=1, padx=20, pady=(10, 5), columnspan=2, sticky="w")

    # Email Section
    email_label = ctk.CTkLabel(contact_frame, text="EMAIL :", text_color="white", font=("Arial", 16), anchor="e")
    email_label.grid(row=2, column=0, padx=20, pady=(10, 0), sticky="e")

    email_entry = ctk.CTkEntry(contact_frame, width=300, height=40, text_color="#191970", font=("Arial", 14))
    email_entry.grid(row=2, column=1, padx=20, pady=(10, 5), columnspan=2, sticky="w")



    

    if admin_doc.exists:
        admin_data = admin_doc.to_dict()

        # Populate the entry fields with the fetched data
        first_name_entry.insert(0, admin_data.get('fn', ''))
        last_name_entry.insert(0, admin_data.get('ln', ''))
        mi_entry.insert(0, admin_data.get('im', ''))
        phone_entry.insert(0, admin_data.get('Phone', ''))
        email_entry.insert(0, admin_data.get('email', ''))
        email_entry.configure(state='disabled')
        first_name_entry.configure(state="disabled")
        last_name_entry.configure(state="disabled")
        mi_entry.configure(state="disabled")
    else:
        messagebox.showerror("Error", "Admin document not found!")

    # Create button_frame for Update and Change Password Buttons
    button_frame = ctk.CTkFrame(profile_frame, fg_color="#03346e")
    button_frame.grid(row=3, column=0, padx=20, columnspan=3, pady=(10, 0), sticky="ne")

    update_button = ctk.CTkButton(button_frame, text="UPDATE CONTACT INFO.", width=180, height=50, font=("Arial", 14, "bold"), fg_color="#fff",  corner_radius=10,  text_color="#191970")
    update_button.grid(row=0, column=2, padx=20, pady=(20, 10), sticky="e")

    change_password_button = ctk.CTkButton(button_frame, text="CHANGE PASSWORD", text_color="#E72929", width=180, height=50, font=("Arial", 14, "bold"), fg_color=White, command= lambda: change_password(document_name))
    change_password_button.grid(row=0, column=3, padx=(20, 0), pady=(20, 10), sticky="e")

    set_hover_color(update_button, "#6EACDA", "#191970", "#fff", "#191970"  )
    set_hover_color(change_password_button, "#E72929","#fff", "#fff", "#E72929" )

    

    def update_contact_info():
        # Fetch the entered phone number and email from the entry objects
        phone_number = phone_entry.get()
        email = email_entry.get()

        # Validate the inputs (optional but recommended)
        if not phone_number or not email:
            messagebox.showerror("Error", "Both Phone Number and Email are required!")
            return

        # Reference the Firestore document with the name "Joaquin"
        admin_ref = db.collection('Admin').document(document_name)

        try:
            # Update the contact information fields in Firestore
            admin_ref.update({
                'Phone': phone_number,
                'email': email
            })
            messagebox.showinfo("Success", "Contact information updated successfully!")
        except Exception as e:
            # Handle any errors during the update
            messagebox.showerror("Error", f"Failed to update contact info: {str(e)}")

    update_button.configure(command=update_contact_info)

