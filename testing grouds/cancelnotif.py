import customtkinter as ctk
import tkinter.messagebox as messagebox
import tkinter as tk
from firebase_admin import firestore
from firebase_config import db
import threading

# Create a root window
root = tk.Tk()
root.withdraw()  # Hide the root window as it's not needed for the loading window

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
    loading_window.update()
    return loading_window

def send_notification_based_on_schedule(db, tree):
    selected_item = tree.selection()  # Get the selected row in the Treeview
    if selected_item:  # Ensure a row is selected
        item = tree.item(selected_item)
        values = item['values']
        schedule_id = values[9]  # Assume first column contains Schedule ID

    notification = {
        "title": "Cancel trip",
        "category": "Cancel",
        "body": """The trip 
        asda asda asda asda asda asd a""",
        "seen": False,
        "timestamp": firestore.SERVER_TIMESTAMP  # Automatically sets the timestamp on creation
    }
    
    def send_process():
        schedule_ref = db.collection("BusSchedule").document(schedule_id)
        schedule_doc = schedule_ref.get()
        
        def update_ui(func, *args):
            # This method schedules the GUI update on the main thread
            root.after(0, func, *args)
        
        if schedule_doc.exists:
            seats = schedule_doc.get("seats")
            if seats:
                # Use a set to ensure unique user IDs
                user_ids = {user_id for user_id in seats.values() if user_id not in ["Available", "Reserved"]}
                
                if user_ids:
                    for user_id in user_ids:
                        user_ref = db.collection("MobileUser").document(user_id)
                        user_ref.collection("Notification").add(notification)
                    update_ui(loading_window.destroy)
                    update_ui(messagebox.showinfo, "Success", "Notification sent based on schedule.")
                else:
                    update_ui(loading_window.destroy)
                    update_ui(messagebox.showwarning, "Warning", "No user IDs found in the seats map for this schedule.")
            else:
                update_ui(loading_window.destroy)
                update_ui(messagebox.showwarning, "Warning", "No seats data found for this schedule.")
        else:
            update_ui(loading_window.destroy)
            update_ui(messagebox.showwarning, "Warning", f"Schedule ID {schedule_id} not found.")
    
    # Show loading window
    loading_window = show_loading_window()
    
    # Run the sending process in a separate thread
    threading.Thread(target=send_process).start()


    # Save Button
        def save_edited_schedule():
           
            updated_data = {
                'status': "Cancelled",
            }
            db.collection('BusSchedule').document(schedule_id).update(updated_data)

            refresh_tree(db, tree)# Refresh the Treeview contents
            # Function to select the item based on matching values in columns 2, 3, and 4
            def select_item_by_values(column_2, column_3, column_4, column_5):
                for item in tree.get_children():
                    item_values = tree.item(item, "values")
                    if (item_values[1] == column_2 and
                        item_values[2] == column_3 and
                        item_values[3] == column_4 and 
                        item_values[4] == column_5):
                        tree.selection_set(item)
                        tree.see(item)
                    return
            # Now call the function to select the newly added schedule row
            select_item_by_values(schedule_data['route'],schedule_data['departure_date'], schedule_data['departure_time'], schedule_data['driver'])
            messagebox.showinfo("Success", "Schedule updated successfully.")






notification = {
    "title": "Cancel trip",
    "category": "Cancel",
    "body": """The trip 
    asda asda asda asda asda asd a""",
    "seen": False,
    "timestamp": firestore.SERVER_TIMESTAMP  # Automatically sets the timestamp on creation
}

# Start the notification process
send_notification_based_on_schedule(notification)

# Start the Tkinter event loop
root.mainloop()


refresh_tree(db, tree)# Refresh the Treeview contents
        # Function to select the item based on matching values in columns 2, 3, and 4
        def select_item_by_values(column_2, column_3, column_4, column_5):
            for item in tree.get_children():
                item_values = tree.item(item, "values")
                if (item_values[1] == column_2 and
                    item_values[2] == column_3 and
                    item_values[3] == column_4 and 
                    item_values[4] == column_5):
                    tree.selection_set(item)
                    tree.see(item)
                    return
        # Now call the function to select the newly added schedule row
         select_item_by_values(schedule_data['route'], updated_data['departure_date'], updated_data['departure_time'], updated_data['driver_id'])

        select_item_by_values(schedule_data['route'],schedule_data['departure_date'], schedule_data['departure_time'], schedule_data['driver_id'])
        create_window.destroy()
