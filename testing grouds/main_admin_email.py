import configparser
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Function to send email with formatted dictionary data
def send_email(data):

    #Data config 
    # Load email credentials from configuration file
    config = configparser.ConfigParser()
    config.read('/Users/jacaj/Downloads/python project/Bus_Reservation_System2/testing grouds/config.ini')  # Make sure config.ini is in the same directory as this script
    print("Loaded sections:", config.sections())
    # Accessing the email credentials
    try:
        sender_email = config['email']['user']
        sender_password = config['email']['password']
    except KeyError as e:
        print(f"Missing key in config file: {e}")
        exit(1)

     # mail sending 

    # Extract the employee ID from the dictionary
    employee_id = data.get("Employee ID", "Unknown")  # Default to "Unknown" if key is missing

    # Create a multipart email message
    subject = f"ADMIN REGISTRATION : {employee_id}"  # Set the email subject
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = "joaquin.jaca@student.pnm.edu.ph"  # Replace with recipient's email
    msg['Subject'] = subject

    # Prepare the body of the email
    body = "CONTENT: USER IS REGISTERING FOR AN ADMIN ACCOUNT:\n\nFORM:\n"
    body += "\n".join(f"{key}: {value}" for key, value in data.items())  # Format key-value pairs

    # Attach the body to the email
    msg.attach(MIMEText(body, 'plain'))

    # Set up the SMTP server and send the email
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Upgrade the connection to a secure encrypted SSL/TLS connection
            server.login(sender_email, sender_password)  # Log in to your email account
            server.send_message(msg)  # Send the email
            return True
    except Exception as e:
        return False



