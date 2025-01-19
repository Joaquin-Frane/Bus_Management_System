import customtkinter as ctk
import webbrowser 
from main_forget_pass import PAsswordRecover

new="#000"
base="#191970"
light="#e4e7f1"
demon="#040427"
shadow="#b0b8d6"
shadow2="#8d93ab"
high="#4050c4"

def password_recovery_window():
    # Create the main window
    window = ctk.CTkToplevel()  # Make this a top-level window so it can be called
    window.geometry("650x600")
    window.title("Password Recovery Guide")

    # Set the desired window size
    window_width = 650
    window_height = 600
    
    # Get the screen dimensions
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Calculate x and y coordinates to center the window
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)

    # Set the geometry of the window
    window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    window.lift()
    window.attributes("-topmost", True)

    # Create the main layout frame for scrollable content and fixed bottom section
    main_frame = ctk.CTkFrame(window)
    main_frame.pack(fill="both", expand=True)

    # Create a scrollable frame for the content
    content_frame = ctk.CTkFrame(main_frame,corner_radius=0)
    content_frame.pack(side="top", fill="both", expand=True)

    # Create the canvas and scrollbar
    canvas = ctk.CTkCanvas(content_frame)
    scrollbar = ctk.CTkScrollbar(content_frame, orientation="vertical", command=canvas.yview, fg_color=shadow2, button_color=base, button_hover_color=demon)

    # Pack canvas and scrollbar properly, side by side
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Configure canvas scroll
    canvas.configure(yscrollcommand=scrollbar.set)

    # Create a frame inside the canvas to place the content
    inner_frame = ctk.CTkFrame(canvas, fg_color=light, corner_radius=0)
    inner_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    # Use canvas window for placing the content inside the scrollable area
    canvas.create_window((0, 0), window=inner_frame, anchor="nw")

    # Add content to the scrollable frame
    title_label = ctk.CTkLabel(inner_frame, text="PASSWORD RECOVERY GUIDE:", font=("Arial", 30, "bold"), anchor="w", text_color=base)
    title_label.pack(pady=(30, 0), padx=30, anchor="w")

    intro_label = ctk.CTkLabel(inner_frame, text="This is your guide to recovering your forgotten account password and potential problems you might encounter doing so.", justify="left", text_color=new, font=("Helvetica",14))
    intro_label.pack(pady=(10, 30), padx=(40,10), anchor="w")

    # Add sections with indentation and extra padding
   
    # Function to adjust wraplength dynamically
    def adjust_wraplength(event=None):
        wrap_length = window.winfo_width() - 90  # Set wraplength dynamically based on window width

        # Adjust wrap length for labels
        intro_label.configure(wraplength=wrap_length)
        for section_label in section_labels:
            section_label.configure(wraplength=wrap_length)

    # Store section labels to adjust wrap length later
    section_labels = []

    def open_email(email_address):
        webbrowser.open(f"mailto:{email_address}")

    def open_website(url):
        webbrowser.open(url)

    heading1 = ctk.CTkLabel(inner_frame, text="RECOVER MY ACCOUNT:", font=("Arial", 16, "bold"), justify="left", anchor="w", text_color=base)
    heading1.pack(pady=10, padx=30, anchor="w")

    content1 = ctk.CTkLabel(inner_frame, justify="left", anchor="w",  font=("Helvetica",14),
    text=("If you happen to forget your password, But still remember your email, "
            "you can click the forgot password link in the app, then enter your registered email.\n\n"
            "An Email with the recovery link will be sent to your account. click it and manually reset your new account password.\n\n"
            "After updating your password. Try to login again with your new password."), text_color=new)

    content1.pack(fill="both", expand=True, padx=(60, 20), pady=(0,30))  # Added padding
    section_labels.append(content1)

    heading2 = ctk.CTkLabel(inner_frame, text="FAILED TO RECEIVE EMAIL:", font=("Arial", 16, "bold"), justify="left", anchor="w", text_color=base)
    heading2.pack(pady=10, padx=30, anchor="w")

    content2 = ctk.CTkLabel(inner_frame, justify="left", anchor="w", font=("Helvetica",14),
    text=( "If you don't receive any recovery email to your account. Try clicking the Resend email link located above the return button on the Success Message window.\n\n"
            "Re-enter your email and click send.\n\n"
            "If you still haven't received any recovery email, check if you input the correct registered email.\n\n"
            "Reason: The Email recovery sender does not check if the email you entered is registered to the system. "
            "If the email is not registered or invalid it just simply not send the email to the account and "
            "returns Success action despite not sending any email. Always double-check if the email you entered is the one you used to register your account."), text_color=new)
    content2.pack(fill="both", expand=True, padx=(60, 20), pady=(0,30))  # Added padding
    section_labels.append(content2)
    
    
    heading3 = ctk.CTkLabel(inner_frame, text="MISSING EMAIL / INVALID EMAIL:", font=("Arial", 16, "bold"), justify="left", anchor="w", text_color=base)
    heading3.pack(pady=10, padx=30, anchor="w")

    content3 = ctk.CTkLabel(inner_frame,  justify="left", anchor="w",font=("Helvetica",14),
    text=("For such scenario, a Missing Email response might mean you have forgotten to enter your email or the data is lost in the process. "
            "Check if you entered an email. If the problem still persists, please contact our help desk: "), text_color=new)
    content3.pack(fill="both", expand=True, padx=(60, 20), pady=(0,0))  # Added padding
    section_labels.append(content3)

    email_label1 = ctk.CTkLabel(inner_frame, text="asd@asd.com",justify="left", anchor="w", fg_color="transparent", text_color="blue", cursor="hand2",font=("Helvetica",14))
    email_label1.pack(fill="both", expand=True, padx=(70, 10), pady=(0, 5))
    section_labels.append(email_label1)
    
    # Bind the label to the open_email function
    email_label1.bind("<Button-1>", lambda e: open_email("asd@asd.com"))

    content5 = ctk.CTkLabel(inner_frame, justify="left", anchor="w",font=("Helvetica",14),
    text=("For the Invalid Email scenario, check if there is a misspelling as it is the most common problem that causes such scenarios. "
            "If the problem still persists after many attempts, there might be a problem with the data formatting of input. Contact us our helpdesk at: "), text_color=new)
    content5.pack(fill="both", expand=True, padx=(60, 20), pady=(0,5))  # Added padding
    section_labels.append(content5)

    email_label2 = ctk.CTkLabel(inner_frame, text="asd@asd.com",font=("Helvetica",14),justify="left", anchor="w", fg_color="transparent", text_color="blue", cursor="hand2")
    email_label2.pack(fill="both", expand=True, padx=(70, 10), pady=(0, 30))
    section_labels.append(email_label2)
    
    # Bind the label to the open_email function
    email_label2.bind("<Button-1>", lambda e: open_email("asd@asd.com"))
    
    
    heading4 = ctk.CTkLabel(inner_frame, text="FORGOT YOUR EMAIL:", font=("Arial", 16, "bold"), justify="left", anchor="w", text_color=base)
    heading4.pack(pady=10, padx=30, anchor="w")

    content4 = ctk.CTkLabel(inner_frame, justify="left", anchor="w",font=("Helvetica",14),
    text=("If you happened to forget your email, please contact your Manager/Supervisor or the service provider for assistance as this kind of scenario requires manual and \"authorized personnel only\" actions. "
            "Recovering such accounts might require you to provide a prof of identity; prepare the necessary documents as asked."), text_color=new)
    content4.pack(fill="both", expand=True, padx=(60, 20), pady=(0,30))  # Added padding
    section_labels.append(content4)

    heading7 = ctk.CTkLabel(inner_frame, text="FOR OTHER QUESTION CONTACT US AT:", font=("Arial", 16, "bold"), justify="left", anchor="w", text_color=base)
    heading7.pack(pady=10, padx=30, anchor="w")
    heading6 = ctk.CTkLabel(inner_frame, text="Website", font=("Helvetica",14), justify="left", anchor="w", fg_color="transparent", text_color="blue", cursor="hand2")
    heading6.pack(pady=(10,40), padx=(60,20), anchor="w")
    section_labels.append(heading6)
    
    # Bind the label to the open_email function
    heading6.bind("<Button-1>", lambda e: open_website("facebook.com"))


    # Fixed bottom section for buttons
    button_frame = ctk.CTkFrame(main_frame, fg_color=shadow, corner_radius=0)
    button_frame.pack(fill="x", side="bottom")

    close_button = ctk.CTkButton(button_frame, text="Close",font=("Arial", 18, "bold"), command=window.destroy, height=40, width=200, text_color=light, fg_color=base, hover_color=high)
    close_button.pack(side="left", padx=(60,10), pady=20)

    recover_button = ctk.CTkButton(button_frame, text="Recover Account", font=("Arial", 18, "bold"), height=40, width=200, text_color=light, fg_color=base, hover_color=high, command=PAsswordRecover)
    recover_button.pack(side="right", padx=(10,60), pady=20)

    # Bind the resize event to adjust wraplength dynamically
    window.bind("<Configure>", adjust_wraplength)

    # Function to bind the mouse wheel to the canvas for scrolling
    def on_mouse_wheel(event):
        canvas.yview_scroll(-1 * int((event.delta / 120)), "units")

    # Bind the mouse wheel event to the scrollable area
    window.bind_all("<MouseWheel>", on_mouse_wheel)

    window.mainloop()

# To call the function in your main application, just use:
# password_recovery_window()
