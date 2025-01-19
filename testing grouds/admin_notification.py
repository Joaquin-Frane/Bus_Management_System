import customtkinter as ctk
import tkinter.messagebox as messagebox
import tkinter as tk
from firebase_admin import firestore
from firebase_config import db
import threading
from forHover import set_hover_color

def create_notification_interface(action, Cmain_frame):
    # Clear main_frame before adding new widgets
    for widget in Cmain_frame.winfo_children():
        widget.destroy()

    # Functions to create and send notifications
    def create_notification(title, category, body):
        return {
            "title": title,
            "category": category,
            "body": body,
            "seen": False,
            "timestamp": firestore.SERVER_TIMESTAMP  # Automatically sets the timestamp on creation
        }

    # Center the loading window on the screen
    def show_loading_window():
        loading_window = tk.Toplevel()
        loading_window.geometry("300x100")
        loading_window.title("Sending Notifications")
        
        # Center the loading window
        screen_width = loading_window.winfo_screenwidth()
        screen_height = loading_window.winfo_screenheight()
        window_width = 300
        window_height = 100
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        loading_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        loading_label = tk.Label(loading_window, text="Sending notifications, please wait...")
        loading_label.pack(expand=True, padx=10, pady=10)
        
        # Make loading window modal
        loading_window.transient(main_frame)
        loading_window.grab_set()
        
        loading_window.update()
        return loading_window

    def send_notification_to_all(notification):
        # Function to handle sending notifications in a separate thread
        def send_process():
            users_ref = db.collection("MobileUser")
            users = users_ref.stream()
            for user in users:
                user_ref = db.collection("MobileUser").document(user.id)
                user_ref.collection("Notification").add(notification)
            
            # Close the loading window and show success message
            loading_window.destroy()
            messagebox.showinfo("Success", "Notification sent to all users.")

        # Display a confirmation message centered on the screen
        confirm = messagebox.askyesno("Confirm Send to All", "Sending notification to all users may take time. Do you want to continue?")
        if confirm:
            # Show loading window
            loading_window = show_loading_window()
            # Run the sending process in a separate thread
            threading.Thread(target=send_process).start()

    def send_notification_to_user(notification, user_id):
        def send_process():
            user_ref = db.collection("MobileUser").document(user_id)
            user_ref.collection("Notification").add(notification)
            
            # Close the loading window and show success message
            loading_window.destroy()
            messagebox.showinfo("Success", f"Notification sent to user {user_id}.")

        # Show loading window
        loading_window = show_loading_window()
        # Run the sending process in a separate thread
        threading.Thread(target=send_process).start()

    def send_notification_based_on_schedule(notification, schedule_id):
        def send_process():
            schedule_ref = db.collection("BusSchedule").document(schedule_id)
            schedule_doc = schedule_ref.get()
            
            if schedule_doc.exists:
                seats = schedule_doc.get("seats")
                if seats:
                    user_ids = [user_id for user_id in seats.values() if user_id not in ["Available", "Reserved"]]
                    
                    if user_ids:
                        for user_id in user_ids:
                            user_ref = db.collection("MobileUser").document(user_id)
                            user_ref.collection("Notification").add(notification)
                        loading_window.destroy()
                        messagebox.showinfo("Success", "Notification sent based on schedule.")
                    else:
                        loading_window.destroy()
                        messagebox.showwarning("Warning", "No user IDs found in the seats map for this schedule.")
                else:
                    loading_window.destroy()
                    messagebox.showwarning("Warning", "No seats data found for this schedule.")
            else:
                loading_window.destroy()
                messagebox.showwarning("Warning", f"Schedule ID {schedule_id} not found.")

        # Show loading window
        loading_window = show_loading_window()
        # Run the sending process in a separate thread
        threading.Thread(target=send_process).start()

    def send_notification():
        title = title_entry.get()
        category = category_combobox.get()
        body = body_entry.get("1.0", "end-1c")
        schedule_id = schedule_id_entry.get().strip()
        user_id = user_id_entry.get().strip()

        # Check if both schedule_id and user_id are empty
        if not schedule_id and not user_id:
            messagebox.showerror("Error", "Please enter either a Schedule ID or a User ID to proceed.")
            return

        notification = create_notification(title, category, body)
        
        if user_id:
            send_notification_to_user(notification, user_id)
        elif schedule_id:
            send_notification_based_on_schedule(notification, schedule_id)
        else:
            send_notification_to_all(notification)
    
    
    sub_frame = ctk.CTkFrame(Cmain_frame, fg_color="#ddd")
    sub_frame.pack(expand=True, fill="both", )
    
    main_frame = ctk.CTkFrame(sub_frame, fg_color="#021526")
    main_frame.pack(expand=True, fill="both", pady=40, padx=40)

    title_label = ctk.CTkLabel(main_frame, text="GLOBAL NOTIFICATION SENDER", font=("Arial", 30, 'bold'), text_color="#fff" )
    title_label.pack(padx=30, pady=15, anchor="nw")

    # Left frame for notification details
    left_frame = ctk.CTkFrame(main_frame, corner_radius=5, fg_color="#03346e")
    left_frame.place(relx=0.03, rely=0.13, relwidth=0.63, relheight=0.85)

    # Right frame for parameters and send options
    right_frame = ctk.CTkFrame(main_frame, corner_radius=5, fg_color="#4682B4")
    right_frame.place(relx=0.67, rely=0.13, relwidth=0.3, relheight=0.85)

    # Title entry
    ctk.CTkLabel(left_frame, text="TITLE:", font=("Arial", 24, 'bold'), text_color="#fff" ).pack(pady=(20,5),padx=30, anchor="w")
    title_entry = ctk.CTkEntry(left_frame, placeholder_text="Enter title here",font=('Arial', 16), height=40, text_color="#191970")
    title_entry.pack(fill="x", padx=20)

    # Category dropdown
    ctk.CTkLabel(left_frame, text="CATEGORY:", font=("Arial", 24, 'bold'), text_color="#fff" ).pack(pady=(25,5),padx=30, anchor="w")
    category_combobox = ctk.CTkComboBox(left_frame, values=["General Notification", "Urgent", "Reminder", "Cancellation", "Promotion"],font=('Arial', 16), height=40, text_color="#191970")
    category_combobox.set("General Notification")
    category_combobox.pack(fill="x", padx=20)

    # Body entry (Text widget)
    ctk.CTkLabel(left_frame, text="MESSAGE:", font=("Arial", 24, 'bold'), text_color="#fff" ).pack(pady=(25,5),padx=30, anchor="w")
    body_entry = ctk.CTkTextbox(left_frame, height=250, wrap="word", text_color="#191970")
    body_entry.insert("1.0", "Enter message here")
    body_entry.pack(fill="both", padx=20, pady=(0, 10))

    # Schedule ID entry
    ctk.CTkLabel(right_frame, text="Specify Schedule ID:", font=("Arial", 20, "bold"), text_color="#fff").pack(pady=(20,15),padx=20,  anchor="w" )
    schedule_id_entry = ctk.CTkEntry(right_frame, placeholder_text="Enter Schedule ID", height=35, text_color="#191970")
    schedule_id_entry.pack(fill="x", padx=20)

    # User ID entry
    ctk.CTkLabel(right_frame, text="Specify User ID:", font=("Arial", 20, "bold"), text_color="#fff").pack(pady=(40,15),padx=20,  anchor="w" )
    user_id_entry = ctk.CTkEntry(right_frame, placeholder_text="Enter Account ID", height=35, text_color="#191970")
    user_id_entry.pack(fill="x", padx=20)

    # Send buttons
    send_param_button = ctk.CTkButton(right_frame, text="Send based on Param.", font=("Arial", 22), height=58, corner_radius=28,fg_color="#191970" ,command=send_notification, hover_color="#9747FF", border_width=2, border_color="#191970")
    send_param_button.pack(pady=(70,20), fill="x", padx=20, anchor="s")

    send_all_button = ctk.CTkButton(right_frame, text="Send to All Users", font=("Arial", 22), height=60, corner_radius=30,fg_color="#191970" , hover_color="#fff", command=lambda: send_notification_to_all(create_notification(title_entry.get(), category_combobox.get(), body_entry.get("1.0", "end-1c"))))
    send_all_button.pack(pady=(0, 15), fill="x", padx=20, anchor="s")

    set_hover_color(send_param_button, "#9747FF","#fff", "#191970" , "#fff")
    set_hover_color(send_all_button, '#fff', '#191970',  "#191970" , "#fff")




'''
# Initialize your main app window and main_frame here
app = ctk.CTk()
app.geometry("1100x600")  # Example size; adjust as needed
app.title("Main Application")

# Create the main_frame where the content will be updated
main_frame = ctk.CTkFrame(app)
main_frame.pack(fill="both", expand=True)

# Call the function to populate main_frame
create_notification_interface( "action", main_frame)

app.mainloop()'''