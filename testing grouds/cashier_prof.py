import customtkinter as ctk
from PIL import Image, ImageTk
from tkinter import ttk, messagebox
from firebase_config import db
import firebase_admin
from firebase_admin import auth, credentials, exceptions
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
    password_frame = ctk.CTkFrame(password_window, fg_color="#191970")
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
        admin_ref = db.collection('Cashier').document(document_name)
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



def update_main_frame_with_profile(parent, Doc_id):
    #destroy children widgest inside main_frame
    for widget in parent.winfo_children():
        widget.destroy()
        #call function to repopulate main_mainframe with widgets

    # Fetch data from Firestore using Doc_id
    cashier_ref = db.collection('Cashier').document(Doc_id)
    cashier_data = cashier_ref.get()

    if cashier_data.exists:
        cashier_info = cashier_data.to_dict()  # Get the document data as a dictionary

        # Create a canvas inside the canvas_frame
        canvas = ctk.CTkCanvas(parent, bd=0, highlightthickness=0)
        canvas.pack(fill="both", expand=True)

         # Load the background image using PIL
        background_image = Image.open("C:/Users/jacaj/Downloads/python project/Bus_Reservation_System2/testing grouds/image sources/background1.png")
        background_image = background_image.resize((1300, 680))  # Resize to fit the canvas
        background_image_tk = ImageTk.PhotoImage(background_image)  # Convert to Tkinter image format

        # Place the background image on the canvas
        canvas.create_image(0, 0, anchor="nw", image=background_image_tk)

        # Keep a reference to the image to prevent garbage collection
        canvas.image = background_image_tk

        # Cr    eate a frame inside the canvas to hold the content
        profile_frame = ctk.CTkFrame(canvas, fg_color=Black)
        profile_frame.pack(fill="both", expand=True, pady=40, padx=40)

            #ow configuration
        profile_frame.grid_rowconfigure(0, weight=1)
        profile_frame.grid_rowconfigure(1, weight=1)
        profile_frame.grid_rowconfigure(2, weight=1)
        profile_frame.grid_rowconfigure(3, weight=1)
        #column configuration
        profile_frame.grid_columnconfigure(0, weight=1)
        profile_frame.grid_columnconfigure(1, weight=1)
        profile_frame.grid_columnconfigure(2, weight=1)

        #canvas.create_window((0, 0), window=profile_frame, anchor="nw")

        # Cashier Profile ID and Service Terminal
        id_label = ctk.CTkLabel(profile_frame, text=f"ID : {cashier_info.get('ID', 'Unknown')}", text_color="white", font=("Arial", 24, "bold"))
        id_label.grid(row=0, column=0, padx=20, pady=(30, 5), sticky="nw")

        terminal_label = ctk.CTkLabel(profile_frame, text=f"SERVICE TERMINAL : {cashier_info.get('terminal_location', 'Unknown')}", text_color="white", font=("Arial",   24, "bold"))
        terminal_label.grid(row=0, column=1, pady=(30, 5), sticky="nw")


        # Create a frame inside the canvas to hold the content
        name_frame = ctk.CTkFrame(profile_frame, fg_color=Black)
        name_frame.grid(row=1, column=0,columnspan=2, sticky="nesw")


            #ow configuration
        name_frame.grid_rowconfigure(0, weight=1)
        name_frame.grid_rowconfigure(1, weight=1)
        #column configuration
        name_frame.grid_columnconfigure(0, weight=1)
        name_frame.grid_columnconfigure(1, weight=1)
        profile_frame.grid_columnconfigure(2, weight=1)



        # Name Section (First Name, Last Name, M.I.)
        name_label = ctk.CTkLabel(name_frame, text="NAME: ", text_color="white", font=("Arial", 20, "bold"))
        name_label.grid(row=0, column=0, padx=20, pady=(15, 0), sticky="nw")

        first_name_entry = ctk.CTkEntry(name_frame, placeholder_text="JUAN", width=350, height=40, text_color="#191970", font=("Arial", 16, "bold"))
        first_name_entry.grid(row=0, column=0, padx=(90, 0), pady=(10, 0), sticky="nw")
        first_name_entry.insert(0, cashier_info.get('first_name', ''))

        last_name_entry = ctk.CTkEntry(name_frame, placeholder_text="CRUZ", width=350, height=40, text_color="#191970", font=("Arial", 16, "bold"))
        last_name_entry.grid(row=0, column=1, padx=(0, 20), pady=(10, 0), sticky="nw")
        last_name_entry.insert(0, cashier_info.get('last_name', ''))

        # Preprocess the middle name to get the desired format
        middle_name = cashier_info.get("middle_name", "")
        formatted_middle_name = ".".join(word[0].upper() for word in middle_name.split() if word) + "."

        mi_entry = ctk.CTkEntry(name_frame, placeholder_text="D.", width=100, height=40, text_color="#191970", font=("Arial", 16, "bold"))
        mi_entry.grid(row=0, column=2, padx=(0, 20), pady=(10, 0), sticky="nw")
        mi_entry.insert(0, formatted_middle_name)

        first_name_entry.configure(state="disabled")
        last_name_entry.configure(state="disabled")
        mi_entry.configure(state="disabled")

        # Labels under the name fields
        first_name_label = ctk.CTkLabel(name_frame, text="FIRST NAME", text_color="white", font=("Arial", 14))
        first_name_label.grid(row=1, column=0, padx=(100, 0), pady=(0, 5), sticky="nw")

        last_name_label = ctk.CTkLabel(name_frame, text="LAST NAME", text_color="white", font=("Arial", 14))
        last_name_label.grid(row=1, column=1, padx=(0, 80), pady=(0, 5), sticky="nw")

        mi_label = ctk.CTkLabel(name_frame, text="M.I.", text_color="white", font=("Arial", 14))
        mi_label.grid(row=1, column=2, padx=(0, 20), pady=(0, 5), sticky="nw")

        # Create a frame inside the canvas to hold the content
        contact_frame = ctk.CTkFrame(profile_frame, fg_color=Black)
        contact_frame.grid(row=2, column=0, padx=20, columnspan=3, pady=(10, 0), sticky="w")

        #ow configuration
        contact_frame.grid_rowconfigure(0, weight=1)
        contact_frame.grid_rowconfigure(1, weight=1)
        contact_frame.grid_rowconfigure(2, weight=1)
        #column configuration
        contact_frame.grid_columnconfigure(0, weight=1)
        contact_frame.grid_columnconfigure(1, weight=1)
        contact_frame.grid_columnconfigure(2, weight=1)

        # Phone Number Section
        phone_label = ctk.CTkLabel(contact_frame, text="PHONE NUMBER :", text_color="white", font=("Arial", 20, "bold"),    anchor="e")
        phone_label.grid(row=0, column=0, padx=20, pady=(16, 0), sticky="ne")

        phone_entry = ctk.CTkEntry(contact_frame, placeholder_text="0998-866-9677", font=("Arial", 16), width=300, height=40, text_color="#191970")
        phone_entry.grid(row=0, column=1, padx=(10,20), pady=(10, 5), columnspan=2, sticky="nw")
        phone_entry.insert(0, cashier_info.get('phone_number', ''))

        # Email Section
        email_label = ctk.CTkLabel(contact_frame, text="EMAIL :", text_color="white", font=("Arial", 20, "bold"), anchor="e")
        email_label.grid(row=1, column=0, padx=20, pady=(16, 0), sticky="ne")

        email_entry = ctk.CTkEntry(contact_frame, placeholder_text="Cruz1@gmail.com", font=("Arial", 16), width=300, height=40, text_color="#191970")
        email_entry.grid(row=1, column=1, padx=(10,20), pady=(10, 5), columnspan=2, sticky="nw")
        email_entry.insert(0, cashier_info.get('email', ''))
        email_entry.configure(state='disabled')

        # Address Section
        address_label = ctk.CTkLabel(contact_frame, text="ADDRESS :", text_color="white", font=("Arial", 20, "bold"),anchor="e")
        address_label.grid(row=2, column=0, padx=20, pady=(16, 0), sticky="ne")

        address_entry = ctk.CTkEntry(contact_frame, placeholder_text="PLC, Tondo, Manila", font=("Arial", 16), width=500, height=40, text_color="#191970")
        address_entry.grid(row=2, column=1,padx=(10,20), pady=(10, 5), columnspan=2, sticky="nw")
        address_entry.insert(0, cashier_info.get('address', ''))

        # Update and Change Password Buttons
        # Create a frame inside the canvas to hold the content
        button_frame = ctk.CTkFrame(profile_frame, fg_color=Black)
        button_frame.grid(row=3, column=0, padx=20, columnspan=3, pady=(10, 0), sticky="ne")

        contact_frame.grid_rowconfigure(0, weight=1)
        contact_frame.grid_columnconfigure(0, weight=2)
        contact_frame.grid_columnconfigure(1, weight=2)
        contact_frame.grid_columnconfigure(2, weight=1)
        contact_frame.grid_columnconfigure(3, weight=1)

        # Function to update Firestore with contact info
        def update_contact_info():
            phone = phone_entry.get()
            email = email_entry.get()
            address = address_entry.get()

            try:# Check if the entries are filled
                if phone and email and address:
                    # Update Firestore document with Doc_id
                    doc_ref = db.collection('Cashier').document(Doc_id)
                    doc_ref.update({
                        'phone_number': phone,
                        'address': address
                    })
                    messagebox.showinfo("Success", "Contact information updated successfully!")
                else:
                    messagebox.showerror("Error", f"Failed to update contact info: {str(e)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update contact info: {str(e)}")


        update_button = ctk.CTkButton(button_frame, text="UPDATE CONTACT INFO.", width=180, height=50, fg_color="#fff", text_color="#191970" , font=("Arial", 16, "bold"), corner_radius=10, command=lambda: update_contact_info())
        update_button.grid(row=0, column=2, padx=20, pady=(20, 10), sticky="e")

        change_password_button = ctk.CTkButton(button_frame, text="CHANGE PASSWORD",text_color="#E72929", font=("Arial", 16, "bold"), width=180,  height=50, fg_color=White,hover_color="#E72929", command=lambda: change_password(Doc_id))
        change_password_button.grid(row=0, column=3, padx=(20, 0), pady=(20, 10), sticky="e")

        set_hover_color(update_button, "#9747FF", "#fff", "#fff", "#191970"  )
        set_hover_color(change_password_button, "#E72929","#fff", "#fff", "#E72929" )


    else:
        print(f"No document found with Doc_id: {Doc_id}")

"""# Example usage
app = ctk.CTk()
app.geometry("1100x600")

# Frame to hold the canvas
canvas_frame = ctk.CTkFrame(app, fg_color="white", width=600, height=400)
canvas_frame.pack(fill="both", expand=True)

# Call the cashier_profile function
update_main_frame_with_profile(canvas_frame, "TX0WVyWsmob7fN2IOdgTTDb1TDM2")

app.mainloop()"""
