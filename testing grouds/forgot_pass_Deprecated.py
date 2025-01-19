import customtkinter as ctk
from tkinter import messagebox
from firebase_config import db  # Assuming this imports the Firestore database connection

def change_password(collection):
    # Create a new window for password change
    password_window = ctk.CTkToplevel()  # Creates a new top-level window
    password_window.title("Change Password")
    password_window.geometry("400x400")  # Set the window size
    
    # Set the window to always stay on top
    password_window.attributes("-topmost", True)

    # Create a frame for the password change form inside the new window
    password_frame = ctk.CTkFrame(password_window, fg_color="blue")
    password_frame.pack(fill='both', expand=True, padx=10, pady=10)

    # Frame to display error messages
    error_frame = None
    error_label = None

    # Function to display error messages inside a red frame
    def display_error(message):
        nonlocal error_frame, error_label
        if error_frame is not None:
            error_frame.destroy()  # Remove any previous error frame

        # Create red frame below the button
        error_frame = ctk.CTkFrame(password_frame, fg_color="red", corner_radius=8)
        error_frame.pack(pady=10, padx=10, fill='x')

        # Create a label inside the error frame
        error_label = ctk.CTkLabel(error_frame, text=message, text_color="white", font=("Arial", 12))
        error_label.pack(pady=5)

    # Function to clear the error frame
    def clear_error():
        nonlocal error_frame
        if error_frame is not None:
            error_frame.destroy()  # Remove any visible error frame
            error_frame = None  # Reset error_frame to None

    # Step 1: Ask for the email first
    lbl_email = ctk.CTkLabel(password_frame, text="Enter Email:", font=("Arial", 12), text_color="white")
    lbl_email.pack(pady=10)
    entry_email = ctk.CTkEntry(password_frame)
    entry_email.pack(pady=5)

    def check_email():
        email = entry_email.get()

        # Fetch the document for the email
        cashier_ref = db.collection(collection)
        query = cashier_ref.where('email', '==', email).get()

        if len(query) > 0:  # Email exists in the collection
            clear_error()  # Clear any previous error when valid email is entered
            entry_email.pack_forget()  # Remove email input
            lbl_email.pack_forget()    # Remove label
            btn_submit_email.pack_forget()  # Remove submit button

            # Step 2: Create passkey entry and submit button
            lbl_passkey = ctk.CTkLabel(password_frame, text="Enter Passkey:", font=("Arial", 12), text_color="white")
            lbl_passkey.pack(pady=10)
            entry_passkey = ctk.CTkEntry(password_frame, show="*")
            entry_passkey.pack(pady=5)

            def check_passkey():
                entered_passkey = entry_passkey.get()

                # Check if passkey matches
                doc = query[0]
                admin_data = doc.to_dict()
                stored_passkey = admin_data.get("passKey", None)

                if stored_passkey == entered_passkey:
                    clear_error()  # Clear error if the passkey is correct
                    lbl_passkey.pack_forget()
                    entry_passkey.pack_forget()
                    btn_submit_passkey.pack_forget()

                    # Step 3: Create new password and retype password entries
                    lbl_new_password = ctk.CTkLabel(password_frame, text="Enter New Password:", font=("Arial", 12), text_color="white")
                    lbl_new_password.pack(pady=10)
                    entry_new_password = ctk.CTkEntry(password_frame, show="*")
                    entry_new_password.pack(pady=5)

                    lbl_retype_password = ctk.CTkLabel(password_frame, text="Retype New Password:", font=("Arial", 12), text_color="white")
                    lbl_retype_password.pack(pady=10)
                    entry_retype_password = ctk.CTkEntry(password_frame, show="*")
                    entry_retype_password.pack(pady=5)

                    def save_new_password():
                        new_password = entry_new_password.get()
                        retype_password = entry_retype_password.get()

                        # Check if new passwords match
                        if new_password != retype_password:
                            display_error("New Password and Retype Password do not match!")
                            return

                        # Update the password in Firestore
                        doc.reference.update({"password": new_password})
                        messagebox.showinfo("Success", "Password updated successfully!")
                        password_window.destroy()  # Close window after success

                    # Save button for new password
                    btn_save = ctk.CTkButton(password_frame, text="Save", command=save_new_password)
                    btn_save.pack(pady=20)

                else:
                    display_error("Incorrect Passkey!")

            # Submit button for passkey
            btn_submit_passkey = ctk.CTkButton(password_frame, text="Submit Passkey", command=check_passkey)
            btn_submit_passkey.pack(pady=10)
        else:
            display_error("Email not found!")

    # Submit button for email
    btn_submit_email = ctk.CTkButton(password_frame, text="Submit Email", command=check_email)
    btn_submit_email.pack(pady=10)

