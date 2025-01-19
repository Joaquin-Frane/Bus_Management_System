import qrcode
import win32print
import win32ui
from PIL import Image, ImageWin
from win32con import *

def generate_qr_code_image(data, border=2, box_size=10):
    # Create QR code with specified border and box size
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    qr_image = qr.make_image(fill="black", back_color="white")
    return qr_image

def print_image(image_path, hdc, y_position):
    image = Image.open(image_path)
    if image.mode not in ("RGB", "L"):
        image = image.convert("RGB")
    dib = ImageWin.Dib(image)
    dib.draw(hdc.GetHandleOutput(), (0, y_position, image.width, y_position + image.height))
    return y_position + image.height

def print_qr_image(hdc, qr_image, x, y, scale=1.7):
    # Scale the QR code by the specified factor while maintaining aspect ratio
    qr_width, qr_height = qr_image.size
    scaled_width = int(qr_width * scale)
    scaled_height = int(qr_height * scale)
    qr_dib = ImageWin.Dib(qr_image)
    qr_dib.draw(hdc.GetHandleOutput(), (x, y, x + scaled_width, y + scaled_height))
    return y + scaled_height

def print_text(hdc, x, y, text, font_size=25, bold=False):
    font = win32ui.CreateFont({
        "name": "Arial",
        "height": font_size,
        "weight": FW_BOLD if bold else FW_NORMAL,
    })
    hdc.SelectObject(font)
    hdc.TextOut(x, y, text)
    return y + font_size + 5

def print_ticket_layout( qr_code_data, info_dict):
    try:
        printer_name = win32print.GetDefaultPrinter()
        print(f"Using default printer: {printer_name}")
        hdc = win32ui.CreateDC()
        hdc.CreatePrinterDC(printer_name)
        hdc.StartDoc("QR Code Ticket")
        hdc.StartPage()

        y_position = print_text(hdc, 0, 1, "************************************************************", font_size=30, bold=True)

        # Print the header image
        y_position = print_image("C:/Users/jacaj/Downloads/New Project (11).png", hdc, 0)

        # Print separator line
        y_position = print_text(hdc, 0, y_position, "************************************************************", font_size=30, bold=True)

        # Print transaction information
        y_position = print_text(hdc, 10, y_position, f"TRN: {info_dict['Transaction ID']}", font_size=20)
        y_position = print_text(hdc, 10, y_position, f"Date:  {info_dict['transaction_date'].strftime('%Y-%m-%d')}    Time: {info_dict['transaction_date'].strftime('%H:%M:%S')}", font_size=20)

        # Generate and print QR code image with reduced border and scaling
        qr_image = generate_qr_code_image(qr_code_data, border=1, box_size=5)  # Adjust border here
        y_position = print_qr_image(hdc, qr_image, 40, y_position, scale=2)

        # Print separator line
        y_position = print_text(hdc, 0, y_position, "************************************************************", font_size=30, bold=True)

        # Print route with larger font
        y_position = print_text(hdc,0, y_position, info_dict['Route'], font_size=35, bold=True)
        y_position += 20

        # Additional information with aligned formatting
        y_position = print_text(hdc, 30, y_position, f"BusID:          {info_dict['BusID']}", font_size=25)
        y_position = print_text(hdc, 30, y_position, f"Date:            {info_dict['Date']}", font_size=25)
        y_position = print_text(hdc, 30, y_position, f"Time:           {info_dict['Time']}", font_size=25)
        y_position = print_text(hdc, 30, y_position, f"Class:           {info_dict['Class']}", font_size=25)
        y_position = print_text(hdc, 30, y_position, f"Discount:     {info_dict['Discount']}", font_size=25)
        y_position += 20

        
        y_position = print_text(hdc, 0, y_position, "************************************************************", font_size=30, bold=True)
        # Seat and price with larger font
        y_position = print_text(hdc, 10, y_position, f"SEAT:     {info_dict['Seat']}", font_size=35)
        y_position = print_text(hdc, 10, y_position, f"PHP.       {info_dict['Price']:.2f}", font_size=35)

        # Footer message
        y_position = print_text(hdc, 0, y_position, "************************************************************", font_size=30, bold=True)
        y_position = print_text(hdc, 10, y_position, "KEEP THE TICKET FOR INSPECTION", font_size=25, bold=True)
        y_position = print_text(hdc, 120, y_position, "THANK YOU !!!", font_size=25, bold=True)

        # End the page and document
        hdc.EndPage()
        hdc.EndDoc()
        hdc.DeleteDC()

    except Exception as e:
        print(f"Error during printing: {e}")


"""
if __name__ == "__main__":
    qr_code_data = "Transaction ID: 205ae546-ff48-4588-bf51-aafdf0f0c37a"
    additional_info = {
        "Transaction ID": "205ae546-ff48-4588-bf51-aafdf0f0c37a",
        "Date": "2024-10-27",
        "Time": "12:00 PM",
        "Route": "Destination_A - Destination_B",
        "BusID": "23ED3WEDW42W",
        "Class": "AC",
        "Discount": "STUDENT",
        "Seat": "1A",
        "Price": "100.00",
        "transaction_date": "timestamp"
    }
    image_path = "C:/Users/jacaj/Downloads/New Project (11).png"
    print_ticket_layout(image_path, qr_code_data, additional_info)
"""