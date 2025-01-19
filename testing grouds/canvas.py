from tkinter import Tk, Canvas
from PIL import Image, ImageTk

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

# Main application
root = Tk()

# Set the window to full screen
root.attributes('-fullscreen', True)

# Get the screen width and height
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Load the background image using Pillow
image = Image.open("Bus_Reservation_System2/testing grouds/image sources/bg.jpg")  # Replace with your image file
image = image.resize((root.winfo_screenwidth(), root.winfo_screenheight()), Image.Resampling.LANCZOS)  # Resize to fit the screen
background_image = ImageTk.PhotoImage(image)

# Create a canvas
canvas = Canvas(root, width=screen_width, height=screen_height, highlightthickness=0)
canvas.pack(fill="both", expand=True)

# Display the background image
canvas.create_image(0, 0, image=background_image, anchor="nw")

# Set the rectangle dimensions
rect_width = 500
rect_height = 600

# Calculate the center position for the rectangle
x_center = (screen_width - rect_width) // 2
y_center = (screen_height - rect_height) // 2

# Draw a rounded rectangle at the center
rounded_rect = create_rounded_rectangle(
    canvas, 
    x1=x_center,  # Centered x-coordinate
    y1=y_center,  # Centered y-coordinate
    width=rect_width,  # Width of the rectangle
    height=rect_height,  # Height of the rectangle
    radius=50,  # Radius of the corners
    fill="#2a2a2a",  # Fill color
    outline=""  # No outline
)

root.mainloop()
