import customtkinter as ctk
from firebase_config import db
import requests
from PIL import Image, ImageTk  # PIL for handling images
from tkinter import ttk, messagebox
#from ADMIN2 import create_admin_dashboard #from CASHIERS2 import initialize_cashier
#from forgot_pass_Deprecated import change_password
from main_forget_pass import PAsswordRecover
from main_admin_email import send_email
from forHover import set_hover_color
import fontawesome as fa
from tkinter import Canvas


# Define color variables
red ="red"
Red = "#8697C4"
White = "white"
Black1 = "black"
DarkRed = "darkred"
DarkGray = '#fff'        # "#292929"
CanvasBG = "#040606"
Green = "green"
new="#191970"
pearl = "#D9D9D9"
bg_image_tk = None

def validate_number(char, entry_widget):
    # Allow digits, decimal point, and limit to one decimal point
    if char.isdigit():  # Check if the input character is a digit
        return True
    else:
        return False
    
def validate_email(current_value, entry_widget):
    # Append the new character to the current value
    if current_value.endswith("@gmail.com"):
        entry_widget.configure(border_color="green")  # Set border to green for valid email
    else:
        entry_widget.configure(border_color="red")  # Set border to red for invalid email
    return True  # Always return True to allow the typing

def load_image():
    global bg_image_tk  # Use the global variable
    bg_image = Image.open("Bus_Reservation_System2/testing grouds/image sources/bg.jpg")  # Change to your image path
    bg_image_tk = ImageTk.PhotoImage(bg_image)  # Create a PhotoImage


def center_window(window, width=300, height=150):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

def show_custom_error_popup(message):
    # Create a new Toplevel window for the popup
    popup = ctk.CTkToplevel()
    popup.title("Login Error")
    popup.geometry("350x150")
    popup.configure(bg_color="#e4e7f1")  # Light red background for error

    # Center the popup window
    center_window(popup)

    # Error message label
    message_label = ctk.CTkLabel(popup, text=message, bg_color="#e4e7f1", text_color="#191970", font=("Arial", 16, "bold"), wraplength=300,anchor="center")
    message_label.pack(pady=20)
    
    # Close button to dismiss the popup
    close_button = ctk.CTkButton(popup, text="Try Again", command=popup.destroy, fg_color="#f22", hover_color="#FF8A8A", text_color="#fff", height=40, font=("Arial", 16, "bold"))
    close_button.pack(pady=10)
    set_hover_color(close_button, "#FF8A8A", "#f22", "#f22", "#fff" )
    
    # Disable interactions with the main window while the popup is open
    popup.grab_set()


def show_custom_success_popup(message):
    # Create a new Toplevel window for the popup
    popup = ctk.CTkToplevel()
    popup.title("Login Error")
    popup.geometry("350x150")
    popup.configure(bg_color="#e4e7f1")  # Light red background for error

    # Center the popup window
    center_window(popup)

    # Error message label
    message_label = ctk.CTkLabel(popup, text=message, bg_color="#e4e7f1", text_color="#191970", font=("Arial", 16, "bold"), wraplength=300,anchor="center")
    message_label.pack(pady=20)
    
    # Close button to dismiss the popup
    close_button = ctk.CTkButton(popup, text="Continue", command=popup.destroy, fg_color="#191970", hover_color="#6EACDA", text_color="#fff", height=40, font=("Arial", 16, "bold"))
    close_button.pack(pady=10)
    set_hover_color(close_button, "#6EACDA", "#fff", "#191970", "#fff" )
    
    # Disable interactions with the main window while the popup is open
    popup.grab_set()


# Function to close the application
def close_app(app):
    app.destroy()

def create_rounded_rectangle(canvas, x1, y1, width, height, radius=25, **kwargs):
    """
    Draws a rounded rectangle on the canvas.
    - canvas: The Canvas widget.
    - x1, y1: Top-left coordinates of the rectangle.
    - width: The width of the rectangle.
    - height: The height of the rectangle.
    - radius: The radius of the rounded corners.
    """
    x2 = x1 + width  # Calculate bottom-right x-coordinate
    y2 = y1 + height  # Calculate bottom-right y-coordinate

    points = [
        x1 + radius, y1,  # Top-left corner
        x1 + radius, y1,
        x2 - radius, y1,  # Top-right corner
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y1 + radius,  # Bottom-right corner
        x2, y2 - radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x2 - radius, y2,  # Bottom-left corner
        x1 + radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1 + radius,
        x1, y1,
    ]
    return canvas.create_polygon(points, **kwargs, smooth=True)


# Function to check login credentials
def login(user_type, username, password,app):
    global current_user_id, current_cashier_id, current_user_id, current_username
    try:
        if user_type == 'Admin':

            url = 'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyCZGeHPedLcAuJbPbApdRgjG4K94v_-LnQ'  # Replace with your actual API key
            data = {
                "email": username,
                "password": password,
                "returnSecureToken": True
            }

            response = requests.post(url, json=data)
            print(response)

            if response.status_code == 200:
                user_data = response.json()
                user_ref = db.collection('Admin').document(user_data['localId'])
                user = user_ref.get()
                if  user.exists :
                    #print("User ID:", user_data['localId'])
                    # Store the document ID and username for admin
                    current_user_id = user_ref.id  # Document ID
                    current_username = user.to_dict().get('fn')  # Fetch username field from the document
                    return True
                else:
                    return False
            else:
                return False

        elif user_type == 'Cashier':
            url = 'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyCZGeHPedLcAuJbPbApdRgjG4K94v_-LnQ'  #actual API key
            data = {
                "email": username,
                "password": password,
                "returnSecureToken": True
            }

            response = requests.post(url, json=data)
            print(response)

            if response.status_code == 200:
                user_data = response.json()
                user_ref = db.collection('Cashier').document(user_data['localId'])
                user = user_ref.get()
                if user.exists:
                    # Store the document ID and username for admin
                    current_user_id = user_ref.id  # Document ID
                    current_cashier_id = user.to_dict().get('ID')  # Fetch cashierID field from the document
                    return True
                else:
                    return False
            else:
                return False
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False



def show_admin_login():
    # Function to toggle password visibility
    def toggle_password_visibility():
        # Toggle password visibility
        if password_entry.cget("show") == "*":
            password_entry.configure(show="")  # Show password
            toggle_button.configure(image=eye_open_image)  # Change to 'eye open' image
        else:
            password_entry.configure(show="*")  # Hide password
            toggle_button.configure(image=eye_closed_image)  # Change to 'eye closed' image

    # Load the images
    eye_open_image = ImageTk.PhotoImage(Image.open("Bus_Reservation_System2/testing grouds/image sources/show3.png").resize((30, 30)))
    eye_closed_image = ImageTk.PhotoImage(Image.open("Bus_Reservation_System2/testing grouds/image sources/hide5.png").resize((32, 32)))

    for widget in app.winfo_children():
        if widget.winfo_manager() == 'pack':
            widget.pack_forget()
        elif widget.winfo_manager() == 'grid':
            widget.grid_forget()
        elif widget.winfo_manager() == 'place':
            widget.place_forget()
    app.configure(bg=White)

    screen_width = app.winfo_screenwidth()
    screen_height = app.winfo_screenheight()

    canvas = ctk.CTkCanvas(app, width=screen_width, height=screen_height, bg=White, bd=0, highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    image3 = Image.open("Bus_Reservation_System2/testing grouds/image sources/fuk.png")
    bg3 = ImageTk.PhotoImage(image3)
    canvas.create_image(1020, 380, image=bg3)
    canvas.image = bg3

    admin_frame = ctk.CTkFrame(canvas, width=screen_width//2, height=screen_height, corner_radius=0, fg_color=new)
    admin_frame.place(x=0, y=0)

    admin_label = ctk.CTkLabel(admin_frame, text="LOGIN ADMIN \nACCOUNT", font=("Arial", 40, "bold"), text_color=White)
    admin_label.place(relx=0.5, rely=0.26, anchor=ctk.CENTER)

    username_entry = ctk.CTkEntry(admin_frame, width=400, height=75, corner_radius=20, placeholder_text="Username", font=("Arial", 20), fg_color=White, text_color="#191970")
    username_entry.place(relx=0.5, rely=0.41, anchor=ctk.CENTER)

    # Password entry
    password_entry = ctk.CTkEntry(admin_frame, width=400, height=75, corner_radius=20, placeholder_text="Password", show="*", font=("Arial", 20), fg_color=White, text_color="#191970")
    password_entry.place(relx=0.5, rely=0.54, anchor=ctk.CENTER)

    # Toggle password visibility button
    toggle_button = ctk.CTkButton(admin_frame, image=eye_closed_image,  # Initially, password is hidden
        text="",  # No text
        width=30,
        height=30,
        fg_color="transparent",  # Transparent background
        hover_color="#fff",  # Optional hover effect
        bg_color=White,
        command=toggle_password_visibility  # Call the toggle function
    )
    toggle_button.place(relx=0.75, rely=0.54, anchor=ctk.CENTER)

    def admin_login_action(*args):
        username = username_entry.get()
        password = password_entry.get()
        if login('Admin', username, password, app):
            show_custom_success_popup(f"ADMIN  LOGIN  SUCCESSFUL !!   \n\n {username}")
            for widget in app.winfo_children():
                widget.destroy()
            app.title("Admin Dashboard")
            create_admin_dashboard(app, current_user_id, current_username)
        else:
            show_custom_error_popup("INCORRECT  USERNAME  AND  PASSWORD !!")

    login_button = ctk.CTkButton(admin_frame, text="LOGIN", font=("Arial", 30, "bold"), width=400, height=60, fg_color=Red, text_color=White, hover_color="#fff", command=admin_login_action)
    login_button.place(relx=0.5, rely=0.69, anchor=ctk.CENTER)
    apply_hover_effect(login_button, White, new)
    password_entry.bind('<Return>', admin_login_action)
    username_entry.bind('<Return>', admin_login_action)


    register_button = ctk.CTkButton(admin_frame, text="Register", font=("Arial", 24, "bold"), width=350, height=65, corner_radius=0, fg_color=new, text_color=White)
    register_button.place(relx=0.5, rely=0.85, anchor=ctk.CENTER)
    apply_hover_effect(register_button, new, Red)
    register_button.configure(command=lambda: create_admin_registration(app))

    help_button = ctk.CTkButton(admin_frame, text="Forgot password", font=("Arial", 24, "bold"), width=350, height=65, corner_radius=0, fg_color=new, text_color=White)
    help_button.place(relx=0.5, rely=0.91, anchor=ctk.CENTER)
    apply_hover_effect(help_button, new, Red)
    help_button.configure(command=lambda: PAsswordRecover(app))

    exit_button = ctk.CTkButton(admin_frame, text="Return", font=("Arial", 40), width=40, height=50, fg_color=new, text_color=White, corner_radius=18, command=main_window)
    exit_button.place(relx=0.85, rely=0.05, anchor=ctk.CENTER)
    apply_hover_effect(exit_button, red, White)

def show_cashier_login(app):
    for widget in app.winfo_children():
        # Check if the widget is managed by pack, grid, or place, and forget accordingly
        if widget.winfo_manager() == 'pack':
            widget.pack_forget()
        elif widget.winfo_manager() == 'grid':
            widget.grid_forget()
        elif widget.winfo_manager() == 'place':
            widget.place_forget()
    app.configure(bg=Black1)

    # Load and resize the background image
    background_image = Image.open("C:/Users/jacaj/Downloads/python project/Bus_Reservation_System2/testing grouds/image sources/bg.jpg")
    resized_image = background_image.resize((app.winfo_screenwidth(), app.winfo_screenheight()), Image.Resampling.LANCZOS)

    # Convert the resized image to a format Tkinter can use
    bg_image_tk = ImageTk.PhotoImage(resized_image)

    canvas = Canvas(app, width=app.winfo_screenwidth(), height=app.winfo_screenheight(), highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    # Display the image on the canvas at (0, 0) position
    canvas.create_image(0, 0, image=bg_image_tk, anchor="nw")
    # Keep a reference to the image to avoid garbage collection
    canvas.image = bg_image_tk

    # Set the rectangle dimensions
    rect_width = 500
    rect_height = 600
    # Calculate the center position for the rectangle
    x_center = (app.winfo_screenwidth() - rect_width) // 2
    y_center = (app.winfo_screenheight() - rect_height) // 2

    # Draw a rounded rectangle at the center
    rounded_rect = create_rounded_rectangle(
        canvas,
        x1=x_center,  # Centered x-coordinate
        y1=y_center,  # Centered y-coordinate
        width=rect_width,  # Width of the rectangle
        height=rect_height,  # Height of the rectangle
        radius=30,  # Radius of the corners
        fill=new,  # Fill color
        outline=""  # No outline
    )

    main_frame = ctk.CTkFrame(app, width=490, height=590, fg_color=new, corner_radius=15)
    main_frame.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

    image1 = ctk.CTkImage(Image.open("Bus_Reservation_System2/testing grouds/image sources/texit1.png"), size=(50, 50))
    image2 = ctk.CTkImage(Image.open("Bus_Reservation_System2/testing grouds/image sources/texit2.png"), size=(50, 50))

    inner_frame = ctk.CTkFrame(main_frame, width=490, height=590, corner_radius=15, fg_color=DarkGray)
    inner_frame.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

    exit_button = ctk.CTkButton(main_frame, text="", image=image1, font=("Arial", 40), width=40, height=50,
                                fg_color=White, bg_color=White, hover_color=Black, text_color=White, corner_radius=5, command=main_window)
    exit_button.place(relx=0.91, rely=0.07, anchor=ctk.CENTER)

    def on_hover(event):
        exit_button.configure(image=image2)

    def on_leave(event):
        exit_button.configure(image=image1)

    exit_button.bind("<Enter>", on_hover)
    exit_button.bind("<Leave>", on_leave)

    label = ctk.CTkLabel(inner_frame, text="CASHIER LOGIN", font=("Arial", 40, "bold"), text_color=new)
    label.place(relx=0.5, rely=0.25, anchor=ctk.CENTER)

    username_entry = ctk.CTkEntry(inner_frame, width=400, height=60, corner_radius=20, placeholder_text="Username",
                                  font=("Arial", 30), fg_color=pearl, text_color=new)
    username_entry.place(relx=0.5, rely=0.38, anchor=ctk.CENTER)

    password_entry = ctk.CTkEntry(inner_frame, width=400, height=60, corner_radius=20, placeholder_text="Password",
                                  show="*", font=("Arial", 30), fg_color=pearl, text_color=new)
    password_entry.place(relx=0.5, rely=0.53, anchor=ctk.CENTER)

    # Load the images for the visibility toggle
    eye_open_image = ImageTk.PhotoImage(Image.open("Bus_Reservation_System2/testing grouds/image sources/show3.png").resize((30, 30)))
    eye_closed_image = ImageTk.PhotoImage(Image.open("Bus_Reservation_System2/testing grouds/image sources/hide5.png").resize((32, 32)))

    # Function to toggle password visibility
    def toggle_password_visibility():
        if password_entry.cget("show") == "*":
            password_entry.configure(show="")  # Show the password
            toggle_button.configure(image=eye_open_image)  # Change to the "eye open" image
        else:
            password_entry.configure(show="*")  # Hide the password
            toggle_button.configure(image=eye_closed_image)  # Change to the "eye closed" image

    # Add a button for toggling password visibility
    toggle_button = ctk.CTkButton(
        inner_frame,
        image=eye_closed_image,  # Initially "eye closed"
        text="",  # No text
        width=30,
        height=30,
        fg_color=pearl,
        hover_color=pearl,
        bg_color=pearl,
        command=toggle_password_visibility
    )
    toggle_button.place(relx=0.85, rely=0.53, anchor=ctk.CENTER)

    def admin_login_action(*args):
        username = username_entry.get()
        password = password_entry.get()

        if login('Cashier', username, password, app):
            show_custom_success_popup(f"WELCOME \n\n {username} !!")
            for widget in app.winfo_children():
                widget.destroy()

            initialize_cashier(app, current_user_id, current_cashier_id)
        else:
            show_custom_error_popup("INCORRECT  USERNAME  AND  PASSWORD !!")

    login_button = ctk.CTkButton(inner_frame, text="LOGIN", font=("Arial", 40, "bold"), width=350, height=65,
                                 corner_radius=20, fg_color=new, text_color=White, border_color=new, border_width=2, command=admin_login_action)
    login_button.place(relx=0.5, rely=0.7, anchor=ctk.CENTER)
    apply_hover_effect(login_button, White, new)
    password_entry.bind('<Return>', admin_login_action)
    username_entry.bind('<Return>', admin_login_action)

    help_button = ctk.CTkButton(inner_frame, text="Forgot password", font=("Arial", 24, "bold"), width=350, height=65,
                                corner_radius=0, fg_color=White, text_color=new)
    help_button.place(relx=0.5, rely=0.9, anchor=ctk.CENTER)
    apply_hover_effect(help_button, White, new)
    help_button.configure(command=lambda: PAsswordRecover(app))

def main_window():
    for widget in app.winfo_children():
        # Check if the widget is managed by pack, grid, or place, and forget accordingly
        if widget.winfo_manager() == 'pack':
            widget.pack_forget()
        elif widget.winfo_manager() == 'grid':
            widget.grid_forget()
        elif widget.winfo_manager() == 'place':
            widget.place_forget()



    screen_width = app.winfo_screenwidth()
    screen_height = app.winfo_screenheight()

    # Set up the canvas
    canvas = ctk.CTkCanvas(app, width=screen_width, height=screen_height, bg="white", bd=0, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    # Display the background image
    load_image()
    canvas.create_image(0, 0, image=bg_image_tk, anchor="nw")
    canvas.image = bg_image_tk  # Keep a reference to prevent garbage collection

    # Logo image
    logo_image = Image.open("Bus_Reservation_System2/testing grouds/image sources/bluelogo1.png")
    resized_logo = logo_image.resize((500, 500), Image.Resampling.LANCZOS)
    bg2 = ImageTk.PhotoImage(resized_logo)
    canvas.create_image(1025, 380, image=bg2)
    canvas.image2 = bg2  # Keep a reference to prevent garbage collection

    # Main frame for login
    main_frame = ctk.CTkFrame(canvas, width=screen_width // 2, height=screen_height, corner_radius=0, fg_color=new, bg_color=new)
    main_frame.place(x=0, y=0)

    # Exit button
    exit_button = ctk.CTkButton(main_frame, text="Exit", font=("Arial", 40), width=100, height=60, fg_color=new, hover_color=Red, text_color="white", corner_radius=10, command=lambda: close_app(app))
    exit_button.place(relx=0.90, rely=0.06, anchor=ctk.CENTER)

    # Labels and login buttons
    ctk.CTkLabel(main_frame, text="WELCOME", font=("Arial Black", 50), text_color=White).place(relx=0.5, rely=0.3, anchor=ctk.CENTER)
    ctk.CTkLabel(main_frame, text="Please select a User type login", font=("Arial", 24, "bold"), text_color=White).place(relx=0.5, rely=0.38, anchor=ctk.CENTER)

    # Admin login button
    admin_button = ctk.CTkButton(main_frame, text="LOGIN AS ADMIN", font=("Arial", 40, "bold"), width=500, height=100, fg_color=Red, text_color=White, corner_radius=20, command=show_admin_login)
    admin_button.place(relx=0.5, rely=0.56, anchor=ctk.CENTER, y=-20)
    apply_hover_effect(admin_button, White, new)

    # Cashier login button
    cashier_button = ctk.CTkButton(main_frame, text="LOGIN AS CASHIER", font=("Arial", 40, "bold"), width=500, height=100, fg_color=Red, corner_radius=20, text_color=White, command=lambda: show_cashier_login(app))
    cashier_button.place(relx=0.5, rely=0.7, anchor=ctk.CENTER, y=20)
    apply_hover_effect(cashier_button, White, new)



def apply_hover_effect(button, hover_bg_color, hover_text_color):
    def on_enter(event):
        button.configure(fg_color=hover_bg_color, text_color=hover_text_color)  # Change colors on hover
    def on_leave(event):
        button.configure(fg_color=button.default_bg_color, text_color=button.default_text_color)  # Revert colors
    button.default_bg_color = button.cget("fg_color")  # Default background color
    button.default_text_color = button.cget("text_color")  # Default text color
    button.bind("<Enter>", on_enter)
    button.bind("<Leave>", on_leave)


def create_admin_registration(app):
    # Clear the previous widgets in the app window
    for widget in app.winfo_children():
        # Check if the widget is managed by pack, grid, or place, and forget accordingly
        if widget.winfo_manager() == 'pack':
            widget.pack_forget()
        elif widget.winfo_manager() == 'grid':
            widget.grid_forget()
        elif widget.winfo_manager() == 'place':
            widget.place_forget()

    # Set up the frame to fit the window and center content
    app.geometry("800x600")  # Adjust window size as needed
    registration_frame = ctk.CTkFrame(app, fg_color="navy")
    registration_frame.pack(fill="both", expand=True, padx=40, pady=40)

    # Top Header section (with left-aligned label and right-aligned exit button)
    header_frame = ctk.CTkFrame(registration_frame, fg_color="transparent")
    header_frame.pack(fill="x", pady=10, padx=20)

    header_label = ctk.CTkLabel(header_frame, text="ADMIN REGISTRATION", text_color="white", font=("Arial", 40))
    header_label.pack(side="left", pady=10)

    close_button = ctk.CTkButton(header_frame, text="X", width=50, height=50, font=("Arial", 18), fg_color="red",
                                 command=show_admin_login)
    close_button.pack(side="right")

    # Horizontal separator line below the header
    separator_line = ctk.CTkFrame(registration_frame, height=2, fg_color="white")
    separator_line.pack(fill="x", padx=10)

    # Name Frame (for name-related widgets)
    name_frame = ctk.CTkFrame(registration_frame, fg_color="transparent")
    name_frame.pack(pady=(10, 50), padx=20, fill="x")

    name_label = ctk.CTkLabel(name_frame, text="NAME:", text_color="white", font=("Arial", 20))
    name_label.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 30))

    first_name_entry = ctk.CTkEntry(name_frame, width=450, height=40, font=("Arial", 18), placeholder_text="FIRST NAME")
    first_name_entry.grid(row=1, column=0, padx=(100,10), pady=5, sticky="we")

    last_name_entry = ctk.CTkEntry(name_frame, width=450, height=40, font=("Arial", 18), placeholder_text="LAST NAME")
    last_name_entry.grid(row=1, column=1, padx=10, pady=5, sticky="we")

    mi_entry = ctk.CTkEntry(name_frame, width=100, height=40, font=("Arial", 18), placeholder_text="M.I.")
    mi_entry.grid(row=1, column=2, padx=10, pady=5, sticky="we")

    # Contact Info Frame (for contact info-related widgets)
    contact_frame = ctk.CTkFrame(registration_frame, fg_color="transparent")
    contact_frame.pack(pady=10, padx=20, fill="x")

    contact_label = ctk.CTkLabel(contact_frame, text="CONTACT INFO:", text_color="white", font=("Arial", 20))
    contact_label.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 30))

    # Company ID
    company_id_label = ctk.CTkLabel(contact_frame, text="COMPANY I.D.:", text_color="white", font=("Arial", 18))
    company_id_label.grid(row=1, column=0, sticky="w",padx=(100,10), pady=(10,20))
    company_id_entry = ctk.CTkEntry(contact_frame, width=400, height=40, font=("Arial", 18), placeholder_text="Enter company ID")
    company_id_entry.grid(row=1, column=1, columnspan=2, padx=10, pady=(10,20), sticky="we")

    # Email Address
    email_label = ctk.CTkLabel(contact_frame, text="E-MAIL ADDRESS:", text_color="white", font=("Arial", 18))
    email_label.grid(row=2, column=0, sticky="w", padx=(100,10),pady=(10,20))
    email_entry = ctk.CTkEntry(contact_frame, width=400, height=40, font=("Arial", 18), placeholder_text="Enter email")
    email_entry.grid(row=2, column=1, columnspan=2, padx=10, pady=(10,20), sticky="we")

    vcmd1 = (app.register(lambda current_value: validate_email(current_value, email_entry)), '%P')

    email_entry.configure(validate='key', validatecommand=vcmd1)

    # Phone Number
    phone_label = ctk.CTkLabel(contact_frame, text="PHONE NUMBER:", text_color="white", font=("Arial", 18))
    phone_label.grid(row=3, column=0, sticky="w", padx=(100,10),pady=(10,0))
    phone_entry = ctk.CTkEntry(contact_frame, width=400, height=40, font=("Arial", 18))
    phone_entry.grid(row=3, column=1, columnspan=2, padx=10, pady=(10,0), sticky="we")

    vcmd = (app.register(lambda char: validate_number(char, phone_entry)), '%S')
    phone_entry.configure(validate='key', validatecommand=vcmd)

    # Register Button at the bottom-right corner
    register_button = ctk.CTkButton(registration_frame, text="REGISTER ACCOUNT", width=250, height=50, font=("Arial", 18),
                                    command=lambda: register_admin(first_name_entry.get(), last_name_entry.get(), mi_entry.get(), company_id_entry.get(), email_entry.get(), phone_entry.get(), registration_frame))
    register_button.pack(side="right", padx=(0,120), pady=(0, 60))

# Function to update the frame with the confirmation message
# Function to handle the registration and update the frame with the confirmation message
    def register_admin(first_name, last_name, mi, company_id, email, phone, main_frame):
        
        def confirm_form (main_frame):
            # Clear all widgets from the main frame
            for widget in main_frame.winfo_children():
                widget.destroy()

            # Create a new frame inside the main_frame for the confirmation message
            confirmation_frame = ctk.CTkFrame(main_frame, width=800, height=350, fg_color="white")
            confirmation_frame.pack(expand=True)  # Center it in the main frame

            # Create and place the confirmation message label inside the new frame
            confirmation_label = ctk.CTkLabel(confirmation_frame, text="  YOUR REGISTRATION IS SUBMITTED  ", font=("Arial", 32, "bold"), text_color="black")
            confirmation_label.pack(pady=50)

            # Subtext label inside the new frame
            subtext_label = ctk.CTkLabel(confirmation_frame, text="Your Admin account details will be \n sent to your e-mail after verification",font=("Arial", 28), text_color="black")
            subtext_label.pack(pady=20)

            # Add a 'Return' button to go back to the previous frame, also inside the confirmation frame
            return_button = ctk.CTkButton(confirmation_frame, text="RETURN",font=("Arial", 28), width=200, height=50, command=show_admin_login)
            return_button.pack(pady=40)
            apply_hover_effect(return_button, new, White)
        
        
        # Store the input values in a dictionary
        admin_data = {
        "First Name": first_name_entry.get(),
        "Last Name": last_name_entry.get(),
        "Middle Initial": mi_entry.get(),
        "Employee ID": company_id_entry.get(),
        "Email Address": email_entry.get(),
        "Phone Number":  int(phone_entry.get())}
    
        for key, value in admin_data.items():
           # Check if the value is considered empty
            if not value:
                messagebox.showwarning("Warning", f"Please Insert a Value for ({key}).")
                break

            if 'phone' in key:
                if isinstance(value, int):
                    if len(value) < 11:
                        messagebox.showwarning("Warning", "This is not A valid Phone Number")
                    else:
                        continue
                else:
                   messagebox.showwarning("Warning", f"Invalid phone number format for {key}: {value}")
            
        else:
            print("Admin Data Stored:", admin_data)
            x=send_email(admin_data)
            if x == True :  
                confirm_form(main_frame)
            else:
                messagebox.showwarning("Warning", f"Email not sent")
            
        # Here you can add logic to save the data to Firebase




"""------------------------------------------CASHIER RELATED SHITS--------------------------------------------------"""

from cashier_POS import update_main_frame
from cashier_schedule import update_main_frame_with_schedules
from cashier_route import update_main_frame_with_routes
from cashier_fares import update_main_frame_with_fares
from cashier_prof import update_main_frame_with_profile
# Define color variables
Black = "#191970"
Gray = "#2D2D2D"
blue = "#8697C4"


#loggiong out 

def exit_CHR():
    # Crexit_CHReate a new top-level window for the logout prompt
    logout_window = ctk.CTkToplevel()
    logout_window.title("Logout Confirmation")
    logout_window.geometry("400*200")
    logout_window.lift()
    logout_window.attributes("-topmost", True)

    # ensure other window wont be clickable
    logout_window.grab_set()
    app.update_idletasks()  # Make sure the root window has its updated geometry
    window_width = logout_window.winfo_reqwidth()
    window_height = logout_window.winfo_reqheight()
    position_right = int(app.winfo_screenwidth()/2 - window_width/2)
    position_down = int(app.winfo_screenheight()/2 - window_height/2)
    logout_window.geometry(f"+{position_right}+{position_down}")
    # Label for the logout prompt
    prompt_label = ctk.CTkLabel(logout_window, text="Do you wish to log out?", font=("Arial", 20))
    prompt_label.pack(pady=20)

    def confirm_logout():
        global Doc_id, acc_id
        Doc_id=''
        acc_id=''
        logout_window.destroy()
        # Close both windows
        main_window()
    def cancel_logout():
        # Close the logout prompt window
        logout_window.destroy()
    # Yes button to log out
    yes_button = ctk.CTkButton(logout_window,width=100, text="Logout", command=confirm_logout, fg_color=new, text_color=White, font=("Arial", 12, "bold"), hover_color="red")
    yes_button.pack(pady=10, side="left", padx=20)
    # No button to cancel
    no_button = ctk.CTkButton(logout_window, width=100, text="Cancel", command=cancel_logout, fg_color=Red, font=("Arial", 12, "bold"))
    no_button.pack(pady=10, side="left",padx=20)

def initialize_cashier(root,current_user_id,current_cashier_id):
    root.title("Collapsible Sidebar with Cashier Dashboard")
    root.attributes("-fullscreen", True)
    global Doc_id, acc_id

    Doc_id=current_user_id
    acc_id=current_cashier_id

    if Doc_id =="":
        root.destroy()

    # Clear any existing widgets from the window
    for widget in root.winfo_children():
        # Check if the widget is managed by pack, grid, or place, and forget accordingly
        if widget.winfo_manager() == 'pack':
            widget.pack_forget()
        elif widget.winfo_manager() == 'grid':
            widget.grid_forget()
        elif widget.winfo_manager() == 'place':
            widget.place_forget()


    # Define sidebar and main content frame
    button_width_expanded = 300
    sidebar_collapsed = [False]

    sidebar = ctk.CTkFrame(root, width=button_width_expanded, height=600, fg_color=Black, corner_radius=0)
    sidebar.pack(side="left", fill="y")

    main_frame = ctk.CTkFrame(root, fg_color="white")
    main_frame.pack(side="right", fill="both", expand=True)

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

    # Load icon image for the toggle button
    icon_image = ctk.CTkImage(Image.open("Bus_Reservation_System2/testing grouds/image sources/cashier_icons/menu1.png"), size=(50, 50))
    toggle_button = ctk.CTkButton(sidebar, image=icon_image, text="", hover_color=Black, command=lambda: toggle_sidebar(sidebar, toggle_button, buttons, sidebar_collapsed), width=100, fg_color=Black)
    toggle_button.pack(pady=5, anchor="ne")


    header_frame = ctk.CTkFrame(main_frame, height=50, fg_color=Black, corner_radius=0)
    header_frame.pack(fill="x", side="top")
    # ID Label
    id_label = ctk.CTkLabel(header_frame, text=str(acc_id), font=("Arial", 20, "bold"), text_color=White, fg_color=Red, corner_radius=10, padx=10, pady=5, height=50)
    id_label.pack(side="right", padx=10, pady=10)
    # Add buttons in two rows (4 on top, 2 below) in the main_frame
    content_frame = ctk.CTkFrame(main_frame, corner_radius=20)
    content_frame.pack(fill="both", expand=True)

    # Bottom bar frame (inside the main_frame)
    bottom_bar = ctk.CTkFrame(main_frame, height=100, fg_color=Black, corner_radius=0)
    bottom_bar.pack(side="bottom", fill="x")
    # Placeholder text for the bottom bar
    bottom_label = ctk.CTkLabel(bottom_bar, text="© 2024 Bus Reservation System", text_color=White, font=("Arial", 12), corner_radius=0)
    bottom_label.pack(pady=5)
    # Create buttons
    buttons = create_buttons(sidebar, content_frame, button_width_expanded, Black, White, root)

    # Create dashboard content
    create_dashboard_content(content_frame, root)
    root.mainloop()



def create_buttons(sidebar, main_frame, button_width_expanded, fg_color, text_color, root):
    global Doc_id, acc_id
    # Load and resize images for the buttons and hover images
    button_images = {
        "Schedule": (ctk.CTkImage(Image.open("Bus_Reservation_System2/testing grouds/image sources/cashier_icons/calendar1.png"), size=(70, 70)),
                ctk.CTkImage(Image.open("Bus_Reservation_System2/testing grouds/image sources/cashier_icons/calendar2.png"), size=(70, 70))),
        "Route": (ctk.CTkImage(Image.open("Bus_Reservation_System2/testing grouds/image sources/cashier_icons/route1.png"), size=(70, 70)),
                ctk.CTkImage(Image.open("Bus_Reservation_System2/testing grouds/image sources/cashier_icons/route2.png"), size=(70, 70))),
        "Fares": (ctk.CTkImage(Image.open("Bus_Reservation_System2/testing grouds/image sources/cashier_icons/ticket1.png"), size=(70, 70)),
                ctk.CTkImage(Image.open("Bus_Reservation_System2/testing grouds/image sources/cashier_icons/ticket2.png"), size=(70, 70))),
        "POS": (ctk.CTkImage(Image.open("Bus_Reservation_System2/testing grouds/image sources/cashier_icons/pos1.png"), size=(70, 70)),
                ctk.CTkImage(Image.open("Bus_Reservation_System2/testing grouds/image sources/cashier_icons/pos2.png"), size=(70, 70))),
        "Profile": (ctk.CTkImage(Image.open("Bus_Reservation_System2/testing grouds/image sources/cashier_icons/profile1.png"), size=(70, 70)), 
                ctk.CTkImage(Image.open("Bus_Reservation_System2/testing grouds/image sources/cashier_icons/profile2.png"), size=(70, 70))),
        "Home": (ctk.CTkImage(Image.open("Bus_Reservation_System2/testing grouds/image sources/cashier_icons/bahay1.png"), size=(70, 70)),
                ctk.CTkImage(Image.open("Bus_Reservation_System2/testing grouds/image sources/cashier_icons/bahay2.png"), size=(70, 70)))
    }
    # Create the buttons
    buttons = [
        create_button(sidebar, "SCHEDULE", button_images["Schedule"], lambda: update_main_frame_with_schedules(main_frame), button_width_expanded, fg_color, text_color),
        create_button(sidebar, "ROUTE", button_images["Route"], lambda: update_main_frame_with_routes(main_frame), button_width_expanded, fg_color, text_color),
        create_button(sidebar, "FARES", button_images["Fares"], lambda: update_main_frame_with_fares(main_frame), button_width_expanded, fg_color, text_color),
        create_button(sidebar, "P.O.S.", button_images["POS"], lambda: update_main_frame(main_frame, create_dashboard_content, root, Doc_id, acc_id), button_width_expanded, fg_color, text_color),
        create_button(sidebar, "MY PROFILE", button_images["Profile"], lambda: update_main_frame_with_profile(main_frame, Doc_id), button_width_expanded, fg_color, text_color),
        create_button(sidebar, "HOME", button_images["Home"], lambda: create_dashboard_content(main_frame, root), button_width_expanded, fg_color, text_color)
    ]
    return buttons

def create_button(sidebar, text, images, command, button_width_expanded, fg_color, text_color):

    normal_image, hover_image = images

    button = ctk.CTkButton(sidebar, image=normal_image, text=text,font=("Arial", 24, "bold"), anchor="w", width=button_width_expanded, fg_color=fg_color, corner_radius=0, command=command, height=100, text_color=text_color )
    button.original_text = text  # Store original text
    button.pack(pady=5, fill="x")
    add_hover_effect(button, normal_image, hover_image)
    return button

def add_hover_effect(button, normal_image, hover_image):
    """Adds hover effect to change the image of a button."""
    def on_enter(event):
        button.configure(image=hover_image)
        button.configure(fg_color=White, text_color=Black)
    def on_leave(event):
        button.configure(image=normal_image)
        button.configure(fg_color=Black,text_color=White)
        # Bind the enter and leave events to the button
    button.bind("<Enter>", on_enter)
    button.bind("<Leave>", on_leave)

    # Store the hover image for later use
    button.hover_image = hover_image
    button.normal_image = normal_image


def toggle_sidebar(sidebar, toggle_button, buttons, sidebar_collapsed):
    button_width_expanded = 300
    button_width_collapsed = 100
    if sidebar_collapsed[0]:# Expand sidebar
        icon_image = ctk.CTkImage(Image.open("Bus_Reservation_System2/testing grouds/image sources/cashier_icons/menu1.png"),size=(50,50))
        toggle_button.configure(image=icon_image, text="")
        sidebar.configure(width=button_width_expanded)
        for button in buttons:
            button.configure(width=button_width_expanded, text=button.original_text)
            # Reapply hover effect after expanding the sidebar
            reapply_hover_effect(button)
    else:# Collapse sidebar
        icon_image = ctk.CTkImage(Image.open("Bus_Reservation_System2/testing grouds/image sources/cashier_icons/menu2.png"),size=(50,50))
        toggle_button.configure(image=icon_image, text="")
        sidebar.configure(width=button_width_collapsed)
        for button in buttons:
            button.configure(width=button_width_collapsed, text="")

     # Toggle the state
    sidebar_collapsed[0] = not sidebar_collapsed[0]

def reapply_hover_effect(button):
    # Manually rebind the hover effect after expanding the sidebar
    button.unbind("<Enter>")
    button.unbind("<Leave>")
    normal_image = button.cget("image")
    hover_image = button.hover_image  # Store the hover image when the button is created
    def on_enter(event):
        button.configure(image=hover_image)
        button.configure(fg_color=White, text_color=Black)
    def on_leave(event):
        button.configure(image=normal_image)
        button.configure(fg_color=Black, text_color=White)
    # Rebind hover events
    button.bind("<Enter>", on_enter)
    button.bind("<Leave>", on_leave)


def create_dashboard_content(content_frame, app):
    """Creates the content of the Cashier Dashboard in the main_frame."""
    global Doc_id, acc_id
    # Clear the main frame
    for widget in content_frame.winfo_children():
        # Check if the widget is managed by pack, grid, or place, and forget accordingly
        if widget.winfo_manager() == 'pack':
            widget.pack_forget()
        elif widget.winfo_manager() == 'grid':
            widget.grid_forget()
        elif widget.winfo_manager() == 'place':
            widget.place_forget()
        # Header Frame

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

    sub_canvas = ctk.CTkCanvas(content_frame)
    sub_canvas.pack(fill="both", expand=True,)
    # Load the background image using PIL
    background_image = Image.open("Bus_Reservation_System2/testing grouds/image sources/background1.png")
    background_image = background_image.resize((1300, 680))  # Resize to fit the canvas
    background_image_tk = ImageTk.PhotoImage(background_image)  # Convert to Tkinter image format
    
    # Place the background image on the canvas
    sub_canvas.create_image(0, 0, anchor="nw", image=background_image_tk)
    # Keep a reference to the image to  garbage collection
    sub_canvas.image = background_image_tk

    sub_canvas.columnconfigure(tuple(range(4)), weight=1)

    Schedules_button = ctk.CTkButton(sub_canvas,compound="top", text='Schedules',font=("Helvetica", 24, "bold"),text_color=White, width=200, height=250, corner_radius=0, border_width=5, border_color=Black,fg_color=Black, command= lambda: update_main_frame_with_schedules(content_frame))
    Schedules_button.grid(row=0, column=0, padx=10, pady=30)

    button_with_hover(image_path="Bus_Reservation_System2/testing grouds/image sources/cashier_icons/calendar1.png",  hover_image_path="Bus_Reservation_System2/testing grouds/image sources/cashier_icons/calendar2.png", button=Schedules_button, fg_color=White, text_color=Black)

    Routes_button = ctk.CTkButton(sub_canvas,compound="top",text='Routes',font=("Helvetica", 24, "bold"), width=200, height=250, corner_radius=0, border_width=5, border_color=Black, command=lambda: update_main_frame_with_routes(content_frame))
    Routes_button.grid(row=0, column=1, padx=10, pady=10)

    button_with_hover(image_path="Bus_Reservation_System2/testing grouds/image sources/cashier_icons/route1.png", hover_image_path="Bus_Reservation_System2/testing grouds/image sources/cashier_icons/route2.png", button=Routes_button, fg_color=White, text_color=Black)

    Fares_button = ctk.CTkButton(sub_canvas,compound="top",text="Fares",font=("Helvetica", 24, "bold"), width=200, height=250, corner_radius=0, border_width=5, border_color=Black, command=lambda: update_main_frame_with_fares(content_frame))
    Fares_button.grid(row=0, column=2, padx=10, pady=10)

    button_with_hover(image_path="Bus_Reservation_System2/testing grouds/image sources/cashier_icons/ticket1.png", hover_image_path="Bus_Reservation_System2/testing grouds/image sources/cashier_icons/ticket2.png", button=Fares_button, fg_color=White, text_color=Black)

    POS_button = ctk.CTkButton(sub_canvas,compound="top", text="P.O.S.",font=("Helvetica", 24, "bold"), width=200, height=250, corner_radius=0, border_width=5, border_color=Black, command=lambda: update_main_frame(content_frame, create_dashboard_content, app, Doc_id, acc_id))
    POS_button.grid(row=0, column=3, padx=10, pady=10)

    button_with_hover(image_path="Bus_Reservation_System2/testing grouds/image sources/cashier_icons/pos1.png", hover_image_path="Bus_Reservation_System2/testing grouds/image sources/cashier_icons/pos2.png", button=POS_button, fg_color=White, text_color=Black)

    # Second row of buttons (Profile, Logout)
    Profile_button = ctk.CTkButton(sub_canvas,compound="top", text="Profile",font=("Helvetica", 24, "bold"), width=200, height=250, corner_radius=0, border_width=5, border_color=Black, command=lambda: update_main_frame_with_profile(content_frame,Doc_id))
    Profile_button.grid(row=1, column=0, padx=10, pady=10)

    button_with_hover(image_path="Bus_Reservation_System2/testing grouds/image sources/cashier_icons/profile1.png", hover_image_path="Bus_Reservation_System2/testing grouds/image sources/cashier_icons/profile2.png", button=Profile_button, fg_color=White, text_color=Black)

    Logout_button = ctk.CTkButton(sub_canvas,compound="top", text="Logout",font=("Helvetica", 24, "bold"), width=200, height=250, corner_radius=0, border_width=5, border_color=Black, command= exit_CHR)
    Logout_button.grid(row=1, column=1, padx=10, pady=30)

    button_with_hover(image_path="Bus_Reservation_System2/testing grouds/image sources/cashier_icons/out1.png", hover_image_path="Bus_Reservation_System2/testing grouds/image sources/cashier_icons/out1.png", button=Logout_button, fg_color='red', text_color=White)
        

def button_with_hover(image_path, hover_image_path, button, fg_color, text_color):
    # Load images
    image = Image.open(image_path)
    hover_image = Image.open(hover_image_path)
    # Convert images to CTkImage format for customtkinter
    image = ctk.CTkImage(image,size=(200, 200))
    hover_image = ctk.CTkImage(hover_image,size=(200, 200))
    # Configure the button
    button.configure(image=image, fg_color=Black, text_color=White)  # Set initial image and colors
    def on_enter(event):
        button.configure(image=hover_image)  # Change image on hover
        button.configure(fg_color=fg_color, text_color=text_color)  # Set initial image and colors
    def on_leave(event):
        button.configure(image=image)  # Revert image when not hovering
        button.configure(fg_color=Black, text_color=White)  # Set initial image and colors
    # Bind hover events
    button.bind("<Enter>", on_enter)
    button.bind("<Leave>", on_leave)

    







"""-------------------------------------------ADMIN RELATED SHITS---------------------------------------------------"""

# Other created files with functions being called
from admin_cashiers2 import manage_cashiers
from admin_BusSched2 import manage_bus_schedules
from admin_bus_routes2 import manage_bus_routes
from admin_buses2 import manage_buses
from admin_fares2 import manage_fares
from admin_gas_costing2 import manage_gas_costing
from admin_drivers2 import manage_drivers
from admin_mobuser import manage_users
from admin_Transaction import manage_transactions
from admin_sales import manage_sales
from admin_profile import display_admin_profile
from unit_tyope222 import create_bus_unit_manager
from admin_dashboard import create_dashboard
from admin_notification import create_notification_interface

current_active_button = None

# Function to update the widgets in the app window
def create_admin_dashboard(app,current_user_id,current_username):
    # Initialize window setup
    app.attributes("-fullscreen", True)
    app.title("Admin Dashboard")

    global doc_id, username
    doc_id = current_user_id
    username = current_username
    # Clear any existing widgets from the app window
    for widget in app.winfo_children():
        # Check if the widget is managed by pack, grid, or place, and forget accordingly
        if widget.winfo_manager() == 'pack':
            widget.pack_forget()
        elif widget.winfo_manager() == 'grid':
            widget.grid_forget()
        elif widget.winfo_manager() == 'place':
            widget.place_forget()

    # Custom colors
    red_color = "#FFFFFF"
    black_color ="#4682B4" 
    vio = "#191970"
    white_color = "white"
    Black = "Black"

    # Function to exit the application
    def exit_app():
        # Create a new top-level window for the logout prompt
        logout_window = ctk.CTkToplevel()
        logout_window.title("Logout")
        logout_window.geometry("400*200")
        logout_window.lift()
        logout_window.attributes("-topmost", True)

        # ensure other window wont be clickable
        logout_window.grab_set()
        app.update_idletasks()  # Make sure the root window has its updated geometry
        window_width = logout_window.winfo_reqwidth()
        window_height = logout_window.winfo_reqheight()
        position_right = int(app.winfo_screenwidth()/2 - window_width/2)
        position_down = int(app.winfo_screenheight()/2 - window_height/2)
        logout_window.geometry(f"+{position_right}+{position_down}")

        # Label for the logout prompt
        prompt_label = ctk.CTkLabel(logout_window, text="Do you wish to Sign out?", font=("Arial", 20, 'bold'))
        prompt_label.pack(pady=20)


        def confirm_logout():
            # Close both windows
            global doc_id ,username 
            username =""
            doc_id = ""
            logout_window.destroy()
            main_window()
        def cancel_logout():
            # Close the logout prompt window
            logout_window.destroy()

        # Yes button to log out
        yes_button = ctk.CTkButton(logout_window,width=100, text="Logout", command=confirm_logout, fg_color=new, text_color=White, font=("Arial", 12, "bold"), hover='red')
        yes_button.pack(pady=10, side="left", padx=20)
        # No button to cancel
        no_button = ctk.CTkButton(logout_window, width=100, text="Cancel", command=cancel_logout, fg_color=Red, font=("Arial", 12, "bold"), hover=new)
        no_button.pack(pady=10, side="left",padx=20)

            

    # Function to apply hover effects to buttons
    def apply_hover_effects(button, hover_fg_color, hover_text_color, original_fg_color, original_text_color):
        def on_enter(event):
            button.configure(fg_color=hover_fg_color, text_color=hover_text_color)
        def on_leave(event):
            button.configure(fg_color=original_fg_color, text_color=original_text_color)
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

    def handle_button_click(button, command):
        global current_active_button
        # Reset the previously active button, if any
        if current_active_button:
            current_active_button.configure(fg_color=black_color, text_color=white_color)

        # Set the clicked button as active (white color)
        button.configure(fg_color=white_color, text_color=Black)
        current_active_button = button  # Update the active button

        # Execute the button's command
        command()

    # General setup of Window
    # Top bar
    top_bar = ctk.CTkFrame(app, height=100, fg_color=black_color, corner_radius=0)
    top_bar.pack(side="top", fill="x")

    image_path = "Bus_Reservation_System2/testing grouds/image sources/cashier_icons/profile1.png"  # Correct path
    icon_image = ctk.CTkImage(Image.open(image_path), size=(40, 40))  # Resize if needed

    # Label ADMIN
    admin_button = ctk.CTkButton(top_bar, text=" ADMIN   ", command= lambda: create_dashboard(main_content_frame), fg_color=black_color,text_color=white_color,font=("Arial", 25, "bold"), hover_color=vio,image=icon_image, compound="left", width=210, height=60, corner_radius=0)
    admin_button.pack(side="left", padx=(0,10), pady=2)

    #admin_label = ctk.CTkLabel(top_bar, text="ADMIN", text_color=white_color, font=("Arial", 20, "bold"))
    #admin_label.pack(side="left", padx=10)

    # EXIT Button
    exit_button = ctk.CTkButton(top_bar, text=" LOGOUT ", command=exit_app, fg_color=Black, text_color=white_color, hover_color="#FF6666", width=70, height=50, corner_radius=15)
    exit_button.pack(side="right", padx=10)

    # Red line under the top bar
    red_line = ctk.CTkFrame(app, height=2, fg_color=red_color, corner_radius=0)
    red_line.pack(side="top", fill="x")

    # Sidebar frame
    sidebar_frame = ctk.CTkFrame(app, width=200, fg_color=black_color, corner_radius=0)
    sidebar_frame.pack(side="left", fill="y")

    # Buttons in the sidebar and  Functions to handle button clic
    buttons = [
        ("  BUS ROUTE", lambda: manage_bus_routes("ROUTES", main_content_frame)),
        ("  BUS SCHEDULE", lambda: manage_bus_schedules("SCHEDULES", main_content_frame)),
        ("  FIX FARES", lambda: manage_fares("FARES", main_content_frame)),
        ("  BUS UNITS", lambda: manage_buses("BUS_UNIT", main_content_frame)),
        ("  GAS COSTING", lambda: manage_gas_costing("GAS", main_content_frame)),
        ("  DRIVERS", lambda: manage_drivers("DRIVERS", main_content_frame)),
        ("  CASHIERS", lambda: manage_cashiers("CASHIERS", main_content_frame)),
        ("  MOBILE USER ACC.",lambda: manage_users("USERS", main_content_frame)),
        ("  TRANSACTIONS", lambda: manage_transactions("TRANSACTIONS", main_content_frame)),
        ("  SALES", lambda: manage_sales("SALES", main_content_frame)),
        ("  PROFILE", lambda: display_admin_profile("ADMIN", main_content_frame,doc_id)),
        ("  UNIT TYPE", lambda:create_bus_unit_manager("UNIT_TYPE",main_content_frame)),
        ("  NOTIFICATION", lambda:create_notification_interface("NOTIFICATION",main_content_frame)),
    ]

    # Create buttons and apply hover effects
    for text, command in buttons:
        # Create each button without the command argument first
        button = ctk.CTkButton(
            sidebar_frame, text=text, fg_color=black_color, text_color=white_color, anchor="w",
            hover_color=red_color, width=210, height=50, corner_radius=0, font=("Arial", 18)
        )
    
        # Assign the command with the lambda after button is created
        button.configure(command=lambda b=button, cmd=command: handle_button_click(b, cmd))
    
        # Pack the button and apply hover effects
        button.pack(pady=2)
        apply_hover_effects(button, red_color, "#191970", black_color, white_color)

    # Code for the main content frame: Handle the changing content done by the button action
    main_content_frame = ctk.CTkFrame(app)
    main_content_frame.pack(side="right", fill="both", expand=True)

    create_dashboard(main_content_frame)

    # Design in Treeview
    style = ttk.Style()
    # Themes to change the general themes of treeview objs (can be downloaded or created)
    style.theme_use("clam")  # clam style
    style.configure("Treeview", background= "#EDE8F5", foreground=vio,#7091E6 Default row text color
        rowheight=40, fieldbackground= "#8697C4", font=("Arial", 12)) # Configure the header (font, etc.)
    
    style.configure("Treeview.Heading", font=("Arial", 14),  # Header font
        background="white",   # Background color of the header
        foreground=vio)   # Text color of the header # Change selected color (background and foreground when selected)
    
    style.map('Treeview', background=[('selected', black_color)], # Set selected row background to white
        foreground=[('selected', red_color)])   # Set selected row text color to black
    



"""--------------------------------------------APPLICATION WINDOW------------------------------------------------------"""
app = ctk.CTk()
app.attributes("-fullscreen", True) 
#Set the window to full screen
#app.geometry(f"{app.winfo_screenwidth()}x{app.winfo_screenheight()}")
app.title("Login System")



main_window()
app.mainloop()