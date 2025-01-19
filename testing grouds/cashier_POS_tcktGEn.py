import customtkinter as ctk
import firebase_admin
from firebase_admin import credentials, firestore
import uuid
from tkinter import messagebox
import datetime
from datetime import datetime
import qrcode
import os

from printtest.qrprint import print_ticket_layout

# Initialize Firebase
from firebase_config import db


def update_daily_transaction_count(price):
    today = datetime.now().strftime('%Y-%m-%d')
    daily_ref = db.collection('DailyTransactions').document(today)

    dailysales_ref = db.collection('DailySales').document(today)

    # Increment the transaction count for today
    daily_ref.set({
        'date' : today,
        'transaction_count': firestore.Increment(1)
    }, merge=True)

    dailysales_ref.set({
        'date' : today,
        'sales_count': firestore.Increment(price)
    }, merge=True)



def generate_qr_code(transaction_id, trip_id):
    # Combine transaction ID and trip ID into a single string for the QR code
    qr_data = f"Transaction ID: {transaction_id}"
    
    # Generate the QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    # Create the QR code image
    img = qr.make_image(fill_color="black", back_color="white")

    # Define the folder path and create it if it doesn't exist
    # Set folder path relative to the location of pay.py
    folder_path = "Bus_Reservation_System2/testing grouds/qr_codes"

    # Check if the folder exists, create it if not
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print("Folder created successfully.")
    else:
        print("Folder already exists.")
        
    
    # Save the QR code image
    img_filename = os.path.join(folder_path, f"QR_{transaction_id}.png")
    img.save(img_filename)
    
    print(f"QR code generated and saved as {img_filename}")
    return img_filename


def save_data(ticket_list):
    for ticket in ticket_list:
            schedule_id = ticket.get("ScheduleID")
            bus_seat = ticket.get("Seat")
            departure_time = ticket.get("Time_Schedule")
            route = ticket.get("Route")
        
            # Check for duplicate entry in 'tripInfo'
            try:
                trip_info_ref = db.collection("tripInfo")
                query = trip_info_ref.where("ScheduleID", "==", schedule_id).where("bus_seat", "==", bus_seat).limit(1)
                results = list(query.stream())
            
                if results:
                    messagebox.showerror("Error", f"Duplicate found for ScheduleID: {schedule_id} and Seat: {bus_seat}. Skipping this ticket.")
                    continue  # Skip this ticket if duplicate is found
                
            except Exception as e:
                messagebox.showerror("Error",f"Error while checking for duplicates: {e}")
                continue  # Skip the ticket in case of any error during duplicate check

            # Proceed with saving the ticket if no duplicate is found
            departure_time = ticket.get("Time_Schedule")
            current_date = ticket.get("Current_Date")
            route = ticket.get("Route")
            class_type = ticket.get("Class")
            schedule = ticket.get("Dept_Date")
            bus_id = ticket.get("Bus_ID")
            mode = ticket.get("Mode")
            discount = ticket.get("Discount")
            price = float(ticket.get("Fare"))  # Convert price to a float
            cashier_id = ticket.get("Cashier_id")
            user_id = "Terminal-Purchase"
            #ticket.get("Acc_id")

            doc_ref = db.collection("Cashier").document(ticket.get('Acc_id'))

            # Fetch the document
            doc = doc_ref.get()

            #date related stuffs

            try:
                #Parse the string into a datetime object using strptime
                #prc_date = datetime.datetime.strptime(current_date, "%Y-%m-%d").date()
                dept_date = datetime.strptime(schedule, "%Y-%m-%d").date()

                #Print the date object
                #print("You entered the date:", prc_date)
                print("You entered the date1:", dept_date)
            except ValueError:
                print("Invalid date format. Please enter the date in YYYY-MM-DD format.")



            # Check if the document exists
            if doc.exists:
                # Convert document to dictionary
                doc_data = doc.to_dict()
                # Access specific field value
                terminal = doc_data.get('terminal_location')  # Replace 'your_field_name' with the actual field name
    
                # Store the field value in a variable
                print(f"Field value: {terminal}")
            else:
                print(f"No document found with ID: {ticket.get('Acc_id')}")

            def update_seat_status(selected_schedule, seat_id, new_status, route):
                try:
                    # Step 1: Query the 'BusSchedule' collection to find the document with matching 'schedule_id'
                    schedules_ref = db.collection('BusSchedule')
                    query = schedules_ref.where('departure_time', '==', selected_schedule).where('route', '==', route).limit(1)
                    results = query.stream()

                    # Step 2: Iterate through the results (since the query can return multiple documents)
                    for doc in results:
                        doc_ref = schedules_ref.document(doc.id)  # Get the document reference

                        # Step 3: Get the seat map (the 'seats' field) from the document
                        seat_map = doc.to_dict().get('seats', {})

                        # Step 4: Update the specific seat status (if the seat exists in the map)
                        if seat_id in seat_map:
                            seat_map[seat_id] = new_status  # Change seat status (e.g., 'reserved')

                            # Step 5: Update the Firestore document with the modified seat map
                            doc_ref.update({'seats': seat_map})

                            print(f"Seat {seat_id} updated to '{new_status}' in schedule {selected_schedule}")
                        else:
                            print(f"Seat {seat_id} not found in the seat map.")
                except Exception as e:
                    print(f"Error updating seat: {e}")
            
            update_seat_status(departure_time,bus_seat,"Reserved",route)

            # Document IDs
            trip_id = str(uuid.uuid4())
            transaction_id = str(uuid.uuid4())
            sale_id = str(uuid.uuid4())

            current_time = datetime.now()

            # Data for tripInfo collection
            trip_info_data = {
            "TripID": trip_id,
            "ScheduleID": schedule_id,
            "departure_time": departure_time,
            "transaction_date": current_time,
            "route": route,
            "class": class_type,
            "departure_date": schedule,
            "bus_id": bus_id,
            "bus_seat": bus_seat,
            "account_id": cashier_id,
            "status": "Active"
            }

            # Data for transactions collection
            transaction_data = {
                "transactionID": transaction_id,
                "TripID": trip_id,
                "ScheduleID": schedule_id,
                "discount": discount,
                "price": price,
                "mode": mode,
                "transaction_date": current_time,
                "route": route,
                "status":"Active",
                "account_id":cashier_id
            }

            # Data for sales collection
            sale_data = {
                "ID": sale_id,
                "transactionID": transaction_id,
                "TripID": trip_id,
                "ScheduleID": schedule_id,
                "price": price,
                "transaction_date": current_time,
                "account_id": cashier_id,
                "terminal": terminal,
                "status": "Payed"
            }

            qr_code_data = f"Transaction ID: {transaction_id}"
            additional_info = {
                "Transaction ID": transaction_id,  # string
                "Date": schedule,                  # string
                "Time": departure_time,            # string
                "Route": route,                    # string
                "BusID": bus_id,                   # string
                "Class": class_type,               # string
                "Discount": discount,              # string
                "Seat": bus_seat,                  # string
                "Price": price,                    # float
                "transaction_date": current_time   # timestamp
            }

            #user test
            #db.collection('MobileUser').document('PBZVbcayIgMWX2I9RiNAEDaP6T42').collection('Purchase').document(transaction_id).set(transaction_data)
            
            update_daily_transaction_count( price)

            # Save data to Firestore
            db.collection('tripInfo').document(trip_id).set(trip_info_data)
            db.collection('transactions').document(transaction_id).set(transaction_data)
            db.collection('sales').document(sale_id).set(sale_data)

            print(transaction_id)

            print_ticket_layout(qr_code_data, additional_info)


            print("Data saved successfully!")
    messagebox.showinfo("Information", "Ticket Generated Successfully!!!.")
