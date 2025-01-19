import customtkinter as ctk
from tkinter import *


def set_hover_color(button, hover_bg_color, hover_text_color, normal_bg_color, normal_text_color):
    # Function to change the button's color when hovered
    def on_enter(event):
        button.configure(fg_color=hover_bg_color, text_color=hover_text_color)

    # Function to reset the button's color when not hovered
    def on_leave(event):
        button.configure(fg_color=normal_bg_color, text_color=normal_text_color)

    # Bind the hover events to the button
    button.bind("<Enter>", on_enter)
    button.bind("<Leave>", on_leave)