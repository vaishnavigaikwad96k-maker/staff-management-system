
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os


# =========================================================
# LOGIN FUNCTION
# =========================================================

def login():

    username = username_entry.get().strip()
    password = password_entry.get().strip()

    if username == "sai" and password == "sai123":

        root.destroy()

        try:
            import dashboard
            dashboard.open_dashboard()

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Dashboard open .\n\n{e}"
            )

    else:

        messagebox.showerror(
            "Login Failed",
            "Invalid Username or Password!"
        )


# =========================================================
# SHOW / HIDE PASSWORD
# =========================================================

def toggle_password():

    if password_entry.cget("show") == "*":

        password_entry.config(show="")
        eye_button.config(text="Hide")

    else:

        password_entry.config(show="*")
        eye_button.config(text="Show")


# =========================================================
# MAIN WINDOW
# =========================================================

root = tk.Tk()

root.title(
    "Staff Management System - Login"
)

root.geometry(
    "1100x650"
)

root.resizable(
    False,
    False
)

root.configure(
    bg="#eef2ff"
)


# =========================================================
# LEFT PANEL
# =========================================================

left_panel = tk.Frame(
    root,
    bg="#071b49",
    width=520,
    height=650
)

left_panel.pack(
    side="left",
    fill="y"
)

left_panel.pack_propagate(False)


# =========================================================
# LOGO
# =========================================================

logo_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "staff_small_logo.png"
)

try:

    logo_image = Image.open(logo_path)

    logo_image = logo_image.resize(
        (370, 370),
        Image.LANCZOS
    )

    logo_photo = ImageTk.PhotoImage(
        logo_image
    )

    logo_label = tk.Label(
        left_panel,
        image=logo_photo,
        bg="#071b49"
    )

    logo_label.pack(
        pady=(75, 20)
    )

except Exception as e:

    tk.Label(
        left_panel,
        text="STAFF",
        font=("Arial", 45, "bold"),
        bg="#071b49",
        fg="white"
    ).pack(
        pady=180
    )


# =========================================================
# LEFT TITLE
# =========================================================

tk.Label(
    left_panel,
    text="STAFF MANAGEMENT SYSTEM",
    font=("Arial", 19, "bold"),
    bg="#071b49",
    fg="white"
).pack(
    pady=(0, 5)
)


tk.Label(
    left_panel,
    text="Smart • Simple • Efficient",
    font=("Arial", 10),
    bg="#071b49",
    fg="#bfdbfe"
).pack()


# =========================================================
# RIGHT PANEL
# =========================================================

right_panel = tk.Frame(
    root,
    bg="#eef2ff",
    width=580,
    height=650
)

right_panel.pack(
    side="right",
    fill="both",
    expand=True
)

right_panel.pack_propagate(False)


# =========================================================
# LOGIN CARD
# =========================================================

login_card = tk.Frame(
    right_panel,
    bg="white",
    width=400,
    height=500
)

login_card.place(
    relx=0.5,
    rely=0.5,
    anchor="center"
)

login_card.pack_propagate(False)


# =========================================================
# WELCOME
# =========================================================

tk.Label(
    login_card,
    text="Welcome Back!",
    font=("Arial", 25, "bold"),
    bg="white",
    fg="#071b49"
).pack(
    pady=(55, 5)
)


tk.Label(
    login_card,
    text="Login to Staff Management System",
    font=("Arial", 10),
    bg="white",
    fg="#64748b"
).pack(
    pady=(0, 35)
)


# =========================================================
# USERNAME LABEL
# =========================================================

tk.Label(
    login_card,
    text="Username",
    font=("Arial", 10, "bold"),
    bg="white",
    fg="#172554"
).pack(
    anchor="w",
    padx=45,
    pady=(0, 7)
)


# =========================================================
# USERNAME ENTRY
# =========================================================

username_entry = tk.Entry(
    login_card,
    font=("Arial", 12),
    bg="white",
    fg="#172554",
    bd=1,
    relief="solid"
)

username_entry.pack(
    fill="x",
    padx=45,
    ipady=9
)


# =========================================================
# PASSWORD LABEL
# =========================================================

tk.Label(
    login_card,
    text="Password",
    font=("Arial", 10, "bold"),
    bg="white",
    fg="#172554"
).pack(
    anchor="w",
    padx=45,
    pady=(25, 7)
)


# =========================================================
# PASSWORD FRAME
# =========================================================

password_frame = tk.Frame(
    login_card,
    bg="white"
)

password_frame.pack(
    fill="x",
    padx=45
)


# =========================================================
# PASSWORD ENTRY
# =========================================================

password_entry = tk.Entry(
    password_frame,
    font=("Arial", 12),
    bg="white",
    fg="#172554",
    bd=1,
    relief="solid",
    show="*"
)

password_entry.pack(
    side="left",
    fill="x",
    expand=True,
    ipady=9
)


# =========================================================
# PASSWORD SHOW BUTTON
# =========================================================

eye_button = tk.Button(
    password_frame,
    text="Show",
    font=("Arial", 8, "bold"),
    bg="white",
    fg="#2563eb",
    bd=1,
    relief="solid",
    cursor="hand2",
    command=toggle_password
)

eye_button.pack(
    side="right",
    padx=(5, 0),
    ipady=8
)


# =========================================================
# LOGIN BUTTON
# =========================================================

login_button = tk.Button(
    login_card,
    text="🔐  Login",
    font=("Arial", 12, "bold"),
    bg="#2563eb",
    fg="white",
    activebackground="#1d4ed8",
    activeforeground="white",
    relief="flat",
    cursor="hand2",
    command=login
)

login_button.pack(
    fill="x",
    padx=45,
    pady=(35, 10),
    ipady=10
)


# =========================================================
# ENTER KEY
# =========================================================

root.bind(
    "<Return>",
    lambda event: login()
)


# =========================================================
# FOCUS
# =========================================================

username_entry.focus()


# =========================================================
# START
# =========================================================

root.mainloop()

