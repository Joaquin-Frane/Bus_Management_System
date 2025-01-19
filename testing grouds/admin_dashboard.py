import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import customtkinter as ctk
from datetime import datetime, timedelta
import threading  # For background queries
from firebase_config import db
from PIL import Image, ImageTk
from customtkinter import CTkImage

from report import setup_gui
current_canvas = None

normal_d_image = ctk.CTkImage(Image.open("C:/Users/jacaj/Downloads/python project/Bus_Reservation_System2/testing grouds/image sources/download-file-w.png"), size=(30, 30))
hover_d_image = ctk.CTkImage(Image.open("C:/Users/jacaj/Downloads/python project/Bus_Reservation_System2/testing grouds/image sources/download-file-b.png"), size=(30, 30))


def create_dashboard(c_frame):
    # Clear existing widgets in the frame
    for widget in c_frame.winfo_children():
        widget.destroy()

    # Main frame setup
    main_frame = ctk.CTkFrame(c_frame, fg_color="#021526", corner_radius=0)
    main_frame.pack(fill='both', expand=True)
    main_frame.rowconfigure(tuple(range(10)), weight=1)
    main_frame.columnconfigure(tuple(range(7)), weight=1)

    # Create button frame
    button_frame = ctk.CTkFrame(main_frame, fg_color="#021526", corner_radius=0)
    button_frame.grid(row=0, column=0, columnspan=7, pady=(10, 5), padx=(10, 20), sticky="ew")
    button_frame.columnconfigure(tuple(range(7)), weight=1)

    global normal_d_image, hover_d_image, normal_excel_image, hover_excel_image , normal_pdf_image, hover_pdf_image
    # Persist images to avoid garbage collection
    button_frame.normal_d_image = normal_d_image
    button_frame.hover_d_image = hover_d_image
    

    # Create plot frame
    plot_frame = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=10)
    plot_frame.grid(row=1, column=0, columnspan=7, rowspan=4, pady=5, padx=20, sticky="nsew")

    # Create title label
    plot_title_label = ctk.CTkLabel(button_frame, text="Transaction Tracker", font=("Arial", 26), text_color="#fff")
    plot_title_label.grid(row=0, column=0, padx=5, pady=5)

    def fetch_total_sales():
        total_price = 0
        sales_docs = db.collection('DailySales').stream()
        for doc in sales_docs:
            total_price += doc.to_dict().get('sales_count', 0)
        return total_price

    def fetch_total_user():
        sales_docs = db.collection('MobileUser').stream()
        return len([doc for doc in sales_docs])

    def fetch_total_transactions():
        total_price = 0
        sales_docs = db.collection('DailyTransactions').stream()
        for doc in sales_docs:
            total_price += doc.to_dict().get('transaction_count', 0)
        return total_price

    def update_total_sales():
        total_sales = round(fetch_total_sales(), 2)
        total_user = fetch_total_user()
        total_transactions = fetch_total_transactions()
        label_sales_value.configure(text=f"{total_sales:2,} php")
        label_users_value.configure(text=f"{total_user:,} Users")
        label_transactions_value.configure(text=f"{total_transactions:,} bookings")

    def plot_data(data, title):
        global current_canvas
        plt.clf()

        if not data:
            print("No data to plot.")
            return

        sorted_data = dict(sorted(data.items()))
        plt.plot(sorted_data.keys(), sorted_data.values(), marker='o', color="black")
        plt.title(title)
        plt.xlabel('Date / Month')
        plt.ylabel('Number of Transactions')
        plt.xticks(rotation=0)
        plt.grid(True)
        plt.tight_layout()

        if current_canvas is not None:
            current_canvas.get_tk_widget().pack_forget()
            current_canvas.get_tk_widget().destroy()

        current_canvas = FigureCanvasTkAgg(plt.gcf(), master=plot_frame)
        current_canvas.draw()
        current_canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)

    def fetch_data(days=7):
        today = datetime.now()
        start_date = today - timedelta(days=days)

        docs = db.collection('DailyTransactions')\
             .where('date', '>=', start_date.strftime('%Y-%m-%d'))\
             .stream()

        transaction_counts = {}
        for doc in docs:
            transaction_data = doc.to_dict()
            transaction_date = transaction_data.get('date')
            if transaction_date:
                transaction_counts[transaction_date] = transaction_data.get('transaction_count', 0)

        for i in range(days):
            date = (start_date + timedelta(days=i+1)).strftime('%Y-%m-%d')
            if date not in transaction_counts:
                transaction_counts[date] = 0

        return transaction_counts

    def fetch_monthly_data(months=4):
        today = datetime.now()
        start_date = today.replace(day=1) - timedelta(days=months * 30)

        transactions_query = db.collection('DailyTransactions').where('date', '>=', start_date.strftime('%Y-%m-%d')).stream()

        transaction_counts = {}
        for doc in transactions_query:
            transaction_data = doc.to_dict()
            transaction_date = transaction_data.get('date')
            if transaction_date:
                month_key = transaction_date[:7]
                transaction_counts[month_key] = transaction_counts.get(month_key, 0) + transaction_data.get('transaction_count', 0)

        month_starts = [(today.replace(day=1) - timedelta(days=i * 30)).strftime('%Y-%m') for i in range(months)]

        for month_key in month_starts:
            if month_key not in transaction_counts:
                transaction_counts[month_key] = 0

        return transaction_counts

    def run_in_thread(func, num, title):
        def wrapper():
            data = func(num)
            plot_data(data, f"Transactions Data for {title}")
        threading.Thread(target=wrapper).start()

    def display_7_days():
        run_in_thread(fetch_data, 7, title="7 Days")

    def display_months():
        run_in_thread(fetch_monthly_data, 4, title="4 Months")

    def set_hover_image(button, normal_image, hover_image, color):
         
        def on_enter(event):
            button.configure(image=hover_image, text_color=color, fg_color="#fff")

        def on_leave(event):
            button.configure(image=normal_image, text_color="#fff", fg_color=color)
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

    btn_7_days = ctk.CTkButton(button_frame, text="Show Last 7 Days", command=display_7_days, width=150, height=40, font=("Arial", 14), text_color="#191970", fg_color="#6EACDA", corner_radius=10, hover_color="#fff")
    btn_7_days.grid(row=0, column=6, padx=5, sticky="e")

    btn_months = ctk.CTkButton(button_frame, text="Show Last 4 Months", command=display_months, width=150, height=40, font=("Arial", 14), text_color="#191970", fg_color="#6EACDA", corner_radius=10, hover_color="#fff")
    btn_months.grid(row=0, column=7, padx=5, sticky="e")

    pdf_button = ctk.CTkButton(
        button_frame,
        text="",
        width=50,
        height=40,
        fg_color="#191970",
        text_color="#fff",
        hover_color="#fff",
        command=setup_gui,
        image=button_frame.normal_d_image,
        compound="left",
    )
    pdf_button.grid(row=0, column=8, padx=5, sticky="e")
    set_hover_image(pdf_button, button_frame.normal_d_image, button_frame.hover_d_image, "#191970")


    info_frame = ctk.CTkFrame(main_frame, fg_color='transparent')
    info_frame.grid(row=5, column=0,rowspan=5,columnspan=7, pady=5, padx=20, sticky="ew")
    info_frame.grid_columnconfigure(0, weight=1)
    info_frame.grid_columnconfigure(1, weight=1)
    info_frame.grid_columnconfigure(2, weight=1)

    frame_sales = ctk.CTkFrame(info_frame, fg_color="#03346E", corner_radius=10)
    frame_sales.grid(row=0, column=0, padx=20, pady=(5,20), sticky="nesw")
    label_sales_title = ctk.CTkLabel(frame_sales, text="Total Sales", font=("Arial", 28,"bold"), text_color="#6EACDA")
    label_sales_title.pack(pady=(10,10))
    label_sales_value = ctk.CTkLabel(frame_sales, text="0", font=("Arial", 32), text_color="#E2E2B6")
    label_sales_value.pack(pady=(10,20))

    frame_users = ctk.CTkFrame(info_frame, fg_color="#03346E", corner_radius=10)
    frame_users.grid(row=0, column=1, padx=20, pady=(5,20), sticky="nesw")
    label_users_title = ctk.CTkLabel(frame_users, text="Total App Users", font=("Arial", 28,"bold"), text_color="#6EACDA")
    label_users_title.pack(pady=(10,10))
    label_users_value = ctk.CTkLabel(frame_users, text="100", font=("Arial", 32), text_color="#E2E2B6")
    label_users_value.pack(pady=(10,20))

    frame_transactions = ctk.CTkFrame(info_frame, fg_color="#03346E", corner_radius=10)
    frame_transactions.grid(row=0, column=2, padx=20, pady=(5,20), sticky="nesw")
    label_transactions_title = ctk.CTkLabel(frame_transactions, text="Total Transactions", font=("Arial",28), text_color="#6EACDA")
    label_transactions_title.pack(pady=(10,10))
    label_transactions_value = ctk.CTkLabel(frame_transactions, text="100", font=("Arial", 32), text_color="#E2E2B6")
    label_transactions_value.pack(pady=(10,20))

    update_total_sales()
    display_7_days()


# Uncomment this part to run your application
# if __name__ == "__main__":
#     root = ctk.CTk()
#     create_dashboard(root)
#     root.mainloop()

'''
app = ctk.CTk()
app.geometry("800x600")

# Main frame where the dashboard will be inserted
main_frame = ctk.CTkFrame(app, width=1000, height=800)
main_frame.grid(row=0, column=0, sticky="nsew")

create_dashboard(main_frame)

app.mainloop()'''