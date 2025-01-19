import customtkinter as ctk
from firebase_config import db
import requests

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

#check if email exsists
"""-----------------------------------------------IS EMAIL REGISTER CHECKING CODE-----------------------------------------------------"""

def check_if_email_exists(email):
    """Check if the email is registered in Firebase Authentication."""
    
    url = f'https://identitytoolkit.googleapis.com/v1/accounts:lookup?key=AIzaSyCZGeHPedLcAuJbPbApdRgjG4K94v_-LnQ'
    payload = {
        "email": [email]
    }
    print(f"test if check_if_email_exists : {email}")

    try:
        response = requests.post(url, json=payload)
        response_data = response.json()

        if response.status_code == 200 and "users" in response_data:
            print("email detected")
            # Email exists in Firebase Authentication
            return True
        else:
            # Email does not exist
            print("email detected")
            print(str(response_data))
            return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False



"""----------------------------------------------DEfine Window CREATION------------------------------------------------"""

def PAsswordRecover(app):

    """------------------------------------------DEfine Window SPECS--------------------------------------------------"""

    # Crexit_CHReate a new top-level window for the logout prompt
    logout_window = ctk.CTkToplevel()
    logout_window.title("Logout Confirmation")
    logout_window.geometry("600x200")  # Corrected syntax for window dimensions
    logout_window.lift()
    logout_window.attributes("-topmost", True)
    
    # Ensure other windows can't be clicked
    logout_window.grab_set()
    app.update_idletasks()  # Make sure the window is updated
    
    # Get screen width and height
    window_width = 400  # Since you set it manually
    window_height = 230  # Set manually
    
    
    position_right = int(app.winfo_screenwidth() / 2 - window_width / 2)
    position_down = int(app.winfo_screenheight() / 2 - window_height / 2)
    
    # Center the window on the screen
    logout_window.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")



    """----------------------------------------------DEfine Window Wigets --------------------------------------------------"""

    def Recover ():# Label for the logout prompt
        for widgets in logout_window.winfo_children():
            widgets.destroy()

        prompt_label = ctk.CTkLabel(logout_window, text="Recover Account", font=("Arial", 20))
        prompt_label.pack(pady=(20,5))
        prompt_label2 = ctk.CTkLabel(logout_window, text="Enter Registered Email Address", font=("Arial", 14))
        prompt_label2.pack(pady=(5,10))

        email_entry = ctk.CTkEntry(logout_window, width=300, height=30, corner_radius=10, placeholder_text="Email", font=("Arial", 20), fg_color=pearl, text_color=White)
        email_entry.pack(pady=(10,20), padx=20)

        def cy(args):
            logout_window.destroy()
            password_recovery_window(app)

        clickable_label1 = ctk.CTkLabel(logout_window, text=" Help ?", font=("Arial", 12), text_color='blue')
        clickable_label1.pack( side="bottom", padx=5, pady=(0,10) )
        clickable_label1.bind("<Button-1>", cy)


        # Yes button to log out
        yes_button = ctk.CTkButton(logout_window,width=200, text="Send Recovery to Email", command=lambda: confirm_logout(email_entry.get()), fg_color=new, text_color=White, font=("Arial", 12, "bold"), hover_color="red")
        yes_button.pack(pady=(10, 0), side="bottom", padx=20)

    """-------------------------------------------RUN WIDGET GENERATING CODE "RECOVER"-------------------------------------------------"""
    Recover()




    """-----------------------------------------------Define Email sending Action-----------------------------------------------------"""
    def confirm_logout(email):
        
        if True:
            url = f'https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key=AIzaSyCZGeHPedLcAuJbPbApdRgjG4K94v_-LnQ'
            payload = {
            "requestType": "PASSWORD_RESET",
            "email": email
            }

            try:
                response = requests.post(url, json=payload)
                response_data = response.json()

                print(f"Password reset email sent to {email}.")
                print(str(response_data))

                if response.status_code == 200:
                    print(str(response_data))

                    if 'error' in response_data:
                        # Handle error when email is not registered
                        error_message = response_data['error']['message']
                        print(str(response_data))

                        if error_message == "EMAIL_NOT_FOUND":
                            print(error_message)
                            fail_m("Email not registered.")
                        elif error_message == "MISSING_EMAIL": 
                            fail_m("No Email is entered")
                        else:
                            # Handle other potential errors
                            fail_m(error_message)

                
                    success_m()
                else:
                    print(f"Error sending password reset email: {response_data['error']['message']}")
                    error = response_data.get('error', {}).get('message', 'Unknown error occurred.')
                    fail_m(error)
            except Exception as e:
                print(f"An error occurred: {e}")
                fail_m(str(e))
        


        
            # Close both windows
            #main_window()
            #app.destroy()
            #success_m(email)
        else:
            # Email does not exist
            fail_m("The email is not registered!! \n\n Enter a valid email")





    """----------------------------------------Define IF EMAIL SENT Message Successs-----------------------------------------"""

    def success_m():
        # Crexit_CHReate a new top-level window for the logout prompt
        for widget in logout_window.winfo_children():
            widget.destroy()

        logout_window.title("Success")


        ssc_label = ctk.CTkLabel(logout_window, text="Recovery Email Sent", font=("Arial", 20))
        ssc_label.pack(pady=(20,0))
        ssy_label = ctk.CTkLabel(logout_window, text="The Recovery link is sent to your email successfully!!", font=("Arial", 14), wraplength=300)
        ssy_label.pack(pady=(15,0))

        ssy_label = ctk.CTkLabel(logout_window, text="Please check your email.", font=("Arial", 14), wraplength=300)
        ssy_label.pack(pady=(0,0))



        def ct(args):
            Recover()

        def cy(args):
            logout_window.destroy()
            password_recovery_window(app)

        clickable_label1 = ctk.CTkLabel(logout_window, text=" Help ?", font=("Arial", 12), text_color='blue')
        clickable_label1.pack( side="bottom", padx=5, pady=(0,10))
        clickable_label1.bind("<Button-1>", cy)


        ok_button = ctk.CTkButton(logout_window,width=200, text="Return", fg_color=new, text_color=White, font=("Arial", 12, "bold"), hover_color="red", command= logout_window.destroy)
        ok_button.pack(pady=(0,0), side="bottom", padx=20)


        clickable_label2 = ctk.CTkLabel(logout_window, text=" Resend email ?", font=("Arial", 12), text_color='blue')
        clickable_label2.pack( side="bottom", padx=5,pady=(0,0))
        clickable_label2.bind("<Button-1>", ct)

        





    """----------------------------------------Define IF EMAIL  NOT SENT Message FAILED-----------------------------------------"""

    def fail_m(response_data):
        # Crexit_CHReate a new top-level window for the logout prompt
        for widget in logout_window.winfo_children():
            widget.destroy()

        logout_window.title("Failed")


        ssc_label = ctk.CTkLabel(logout_window, text="Error", font=("Arial", 20,'bold'), text_color="red")
        ssc_label.pack(pady=(20,0))

        ssy_label = ctk.CTkLabel(logout_window, text="Failed sending Password Reset Email:", font=("Arial", 14), wraplength=300, text_color='red')
        ssy_label.pack(pady=(15,0))
        ssz_label = ctk.CTkLabel(logout_window, text=f"{response_data}", font=("Arial", 14), wraplength=300)
        ssz_label.pack(pady=(5,5))

        def ct(args):
            logout_window.destroy()
            password_recovery_window(app)

        clickable_label = ctk.CTkLabel(logout_window, text=" Help ?", font=("Arial", 12), text_color='blue')
        clickable_label.pack(pady=(0, 10), side="bottom")
        clickable_label.bind("<Button-1>", ct)
        
        ok_button = ctk.CTkButton(logout_window,width=200, text="Return", fg_color=new, text_color=White, font=("Arial", 12, "bold"), hover_color="red", command= Recover)
        ok_button.pack(pady=(10, 0), side="bottom", padx=20)

        


"""----------------------------------------------GUIDE RELATED SHITS------------------------------------------------"""

import webbrowser 
new1="#000"
base="#191970"
light="#e4e7f1"
demon="#040427"
shadow="#b0b8d6"
shadow2="#8d93ab"
high="#4050c4"

def exit(window, app):
    window.destroy()
    PAsswordRecover(app)

def password_recovery_window(app):
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

    intro_label = ctk.CTkLabel(inner_frame, text="This is your guide to recovering your forgotten account password and potential problems you might encounter doing so.", justify="left", text_color=new1, font=("Helvetica",14))
    intro_label.pack(pady=(10, 30), padx=(40,10), anchor="w")
   
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
            "After updating your password. Try to login again with your new password."), text_color=new1)
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
            "returns Success action despite not sending any email. Always double-check if the email you entered is the one you used to register your account."), text_color=new1)
    content2.pack(fill="both", expand=True, padx=(60, 20), pady=(0,30))  # Added padding
    section_labels.append(content2)
    
    
    heading3 = ctk.CTkLabel(inner_frame, text="MISSING EMAIL / INVALID EMAIL:", font=("Arial", 16, "bold"), justify="left", anchor="w", text_color=base)
    heading3.pack(pady=10, padx=30, anchor="w")

    content3 = ctk.CTkLabel(inner_frame,  justify="left", anchor="w",font=("Helvetica",14),
    text=("For such scenario, a Missing Email response might mean you have forgotten to enter your email or the data is lost in the process. "
            "Check if you entered an email. If the problem still persists, please contact our help desk: "), text_color=new1)
    content3.pack(fill="both", expand=True, padx=(60, 20), pady=(0,0))  # Added padding
    section_labels.append(content3)

    email_label1 = ctk.CTkLabel(inner_frame, text="asd@asd.com",justify="left", anchor="w", fg_color="transparent", text_color="blue", cursor="hand2",font=("Helvetica",14))
    email_label1.pack(fill="both", expand=True, padx=(70, 10), pady=(0, 5))
    section_labels.append(email_label1)
    # Bind the label to the open_email function
    email_label1.bind("<Button-1>", lambda e: open_email("asd@asd.com"))

    content5 = ctk.CTkLabel(inner_frame, justify="left", anchor="w",font=("Helvetica",14),
    text=("For the Invalid Email scenario, check if there is a misspelling as it is the most common problem that causes such scenarios. "
            "If the problem still persists after many attempts, there might be a problem with the data formatting of input. Contact us our helpdesk at: "), text_color=new1)
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
            "Recovering such accounts might require you to provide a prof of identity; prepare the necessary documents as asked."), text_color=new1)
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

    recover_button = ctk.CTkButton(button_frame, text="Recover Account", font=("Arial", 18, "bold"), height=40, width=200, text_color=light, fg_color=base, hover_color=high, command= lambda:  exit(window,app))
    recover_button.pack(side="right", padx=(10,60), pady=20)

    # Bind the resize event to adjust wraplength dynamically
    window.bind("<Configure>", adjust_wraplength)
    # Function to bind the mouse wheel to the canvas for scrolling
    def on_mouse_wheel(event):
        canvas.yview_scroll(-1 * int((event.delta / 120)), "units")

    # Bind the mouse wheel event to the scrollable area
    window.bind_all("<MouseWheel>", on_mouse_wheel)
    window.mainloop()


"""----------------------------------------------DEfine APP CREATION------------------------------------------------"""
"""
app = ctk.CTk()
app.attributes("-fullscreen", True)  # Set the window to full screen
app.title("Admin Dashboard")
exit_CHR(app)

deep="#7091E6"

app.mainloop()"""
