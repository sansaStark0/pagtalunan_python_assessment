import tkinter as tk
from tkinter import messagebox

def on_button_click():
    messagebox.showinfo("Saving File", "File Saved.")


# Create the main window
root = tk.Tk()
root.title("Power Calculator")
root.geometry("800x600")

# Create a button
button = tk.Button(root, text="Save Data", command=on_button_click)
button.pack(side=tk.LEFT, padx=10)



# Start the main event loop
root.mainloop()