import tkinter as tk
from tkinter import messagebox
import sqlite3
import os


# =========================================================
# DATABASE
# =========================================================

DB_PATH = os.path.join(
    os.path.dirname(__file__),
    "staff.db"
)


# =========================================================
# COLORS
# =========================================================

BG = "#f4f7ff"
HEADER = "#071b49"
SIDEBAR = "#081633"

BLUE = "#2563eb"
PURPLE = "#7c3aed"
GREEN = "#16a34a"
RED = "#dc2626"

WHITE = "#ffffff"
TEXT = "#172554"
GRAY = "#64748b"
LINE = "#cbd5e1"


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():

    return sqlite3.connect(DB_PATH)


# =========================================================
# BACK TO DASHBOARD
# =========================================================

def back_dashboard():

    root.destroy()

    import dashboard
    dashboard.open_dashboard()


# =========================================================
# CLEAR FIELDS
# =========================================================

def clear_fields():

    name_entry.delete(0, tk.END)
    email_entry.delete(0, tk.END)
    phone_entry.delete(0, tk.END)
    department_entry.delete(0, tk.END)
    salary_entry.delete(0, tk.END)

    name_entry.focus()


# =========================================================
# ADD STAFF
# =========================================================

def add_staff():

    name = name_entry.get().strip()
    email = email_entry.get().strip()
    phone = phone_entry.get().strip()
    department = department_entry.get().strip()
    salary = salary_entry.get().strip()


    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

    if name == "":

        messagebox.showwarning(
            "Required",
            "Please enter staff name."
        )

        name_entry.focus()

        return


    if email == "":

        messagebox.showwarning(
            "Required",
            "Please enter email."
        )

        email_entry.focus()

        return


    if phone == "":

        messagebox.showwarning(
            "Required",
            "Please enter phone number."
        )

        phone_entry.focus()

        return


    if department == "":

        messagebox.showwarning(
            "Required",
            "Please enter department."
        )

        department_entry.focus()

        return


    if salary == "":

        messagebox.showwarning(
            "Required",
            "Please enter salary."
        )

        salary_entry.focus()

        return


    # -----------------------------------------------------
    # SALARY VALIDATION
    # -----------------------------------------------------

    try:

        salary_value = float(salary)

        if salary_value < 0:

            raise ValueError

    except:

        messagebox.showerror(
            "Invalid Salary",
            "Please enter a valid salary."
        )

        salary_entry.focus()

        return


    # -----------------------------------------------------
    # PHONE VALIDATION
    # -----------------------------------------------------

    if not phone.isdigit():

        messagebox.showerror(
            "Invalid Phone",
            "Phone number should contain digits only."
        )

        phone_entry.focus()

        return


    try:

        conn = get_connection()

        cursor = conn.cursor()


        # -------------------------------------------------
        # CREATE TABLE IF NOT EXISTS
        # -------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS staff (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                department TEXT NOT NULL,
                salary REAL NOT NULL
            )
        """)


        # -------------------------------------------------
        # INSERT STAFF
        # -------------------------------------------------

        cursor.execute("""
            INSERT INTO staff
            (
                name,
                email,
                phone,
                department,
                salary
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            name,
            email,
            phone,
            department,
            salary_value
        ))


        conn.commit()

        conn.close()


        messagebox.showinfo(
            "Success",
            "Staff added successfully!"
        )


        clear_fields()


    except sqlite3.IntegrityError as e:

        messagebox.showerror(
            "Database Error",
            str(e)
        )


    except Exception as e:

        messagebox.showerror(
            "Error",
            str(e)
        )


# =========================================================
# OPEN STAFF PAGE
# =========================================================

def open_staff():

    global root

    global name_entry
    global email_entry
    global phone_entry
    global department_entry
    global salary_entry


    # =====================================================
    # WINDOW
    # =====================================================

    root = tk.Tk()

    root.title(
        "Staff Management System - Add Staff"
    )

    root.geometry(
        "1200x700"
    )

    root.configure(
        bg=BG
    )

    root.resizable(
        False,
        False
    )


    # =====================================================
    # HEADER
    # =====================================================

    header = tk.Frame(
        root,
        bg=HEADER,
        height=90
    )

    header.pack(
        side="top",
        fill="x"
    )

    header.pack_propagate(False)


    # =====================================================
    # SMALL LOGO
    # =====================================================

    try:

        logo_path = os.path.join(
            os.path.dirname(__file__),
            "staff_small_logo.png"
        )

        logo_image = tk.PhotoImage(
            file=logo_path
        )

        logo_label = tk.Label(
            header,
            image=logo_image,
            bg=HEADER
        )

        logo_label.image = logo_image

        logo_label.place(
            x=18,
            y=12
        )


    except:

        tk.Label(
            header,
            text="S",
            font=(
                "Segoe UI",
                30,
                "bold"
            ),
            fg=WHITE,
            bg=BLUE
        ).place(
            x=25,
            y=18
        )


    # =====================================================
    # HEADER TITLE
    # =====================================================

    tk.Label(
        header,
        text="STAFF MANAGEMENT SYSTEM",
        font=(
            "Segoe UI",
            22,
            "bold"
        ),
        fg=WHITE,
        bg=HEADER
    ).place(
        x=100,
        y=15
    )


    tk.Label(
        header,
        text="Smart • Simple • Efficient Staff Management",
        font=(
            "Segoe UI",
            9
        ),
        fg="#bfdbfe",
        bg=HEADER
    ).place(
        x=103,
        y=53
    )


    # =====================================================
    # BACK TO DASHBOARD
    # =====================================================

    tk.Button(
        header,
        text="← Dashboard",
        font=(
            "Segoe UI",
            10,
            "bold"
        ),
        bg=BLUE,
        fg=WHITE,
        activebackground=PURPLE,
        activeforeground=WHITE,
        relief="flat",
        cursor="hand2",
        padx=15,
        pady=8,
        command=back_dashboard
    ).place(
        x=1030,
        y=25
    )


    # =====================================================
    # SIDEBAR
    # =====================================================

    sidebar = tk.Frame(
        root,
        bg=SIDEBAR,
        width=235
    )

    sidebar.pack(
        side="left",
        fill="y"
    )

    sidebar.pack_propagate(False)


    tk.Label(
        sidebar,
        text="MAIN MENU",
        font=(
            "Segoe UI",
            10,
            "bold"
        ),
        fg="#94a3b8",
        bg=SIDEBAR
    ).pack(
        pady=(30, 20)
    )


    # =====================================================
    # DASHBOARD
    # =====================================================

    tk.Button(
        sidebar,
        text="⌂   Dashboard",
        font=(
            "Segoe UI",
            11,
            "bold"
        ),
        fg="#e2e8f0",
        bg=SIDEBAR,
        activebackground=BLUE,
        activeforeground=WHITE,
        relief="flat",
        anchor="w",
        padx=25,
        pady=14,
        cursor="hand2",
        command=back_dashboard
    ).pack(
        fill="x",
        padx=10,
        pady=3
    )


    # =====================================================
    # ADD STAFF ACTIVE
    # =====================================================

    tk.Button(
        sidebar,
        text="👥   Add Staff",
        font=(
            "Segoe UI",
            11,
            "bold"
        ),
        fg=WHITE,
        bg=BLUE,
        relief="flat",
        anchor="w",
        padx=25,
        pady=14
    ).pack(
        fill="x",
        padx=10,
        pady=3
    )


    # =====================================================
    # VIEW STAFF
    # =====================================================

    def go_view_staff():

        root.destroy()

        import view_staff
        view_staff.open_view_staff()


    tk.Button(
        sidebar,
        text="📋   View Staff",
        font=(
            "Segoe UI",
            11,
            "bold"
        ),
        fg="#e2e8f0",
        bg=SIDEBAR,
        activebackground=BLUE,
        activeforeground=WHITE,
        relief="flat",
        anchor="w",
        padx=25,
        pady=14,
        cursor="hand2",
        command=go_view_staff
    ).pack(
        fill="x",
        padx=10,
        pady=3
    )


    # =====================================================
    # SEARCH STAFF
    # =====================================================

    def go_search():

        root.destroy()

        import search_staff
        search_staff.open_search_staff()


    tk.Button(
        sidebar,
        text="🔍   Search Staff",
        font=(
            "Segoe UI",
            11,
            "bold"
        ),
        fg="#e2e8f0",
        bg=SIDEBAR,
        activebackground=BLUE,
        activeforeground=WHITE,
        relief="flat",
        anchor="w",
        padx=25,
        pady=14,
        cursor="hand2",
        command=go_search
    ).pack(
        fill="x",
        padx=10,
        pady=3
    )


    # =====================================================
    # ATTENDANCE
    # =====================================================

    def go_attendance():

        root.destroy()

        import attendance
        attendance.open_attendance()


    tk.Button(
        sidebar,
        text="🕐   Attendance",
        font=(
            "Segoe UI",
            11,
            "bold"
        ),
        fg="#e2e8f0",
        bg=SIDEBAR,
        activebackground=BLUE,
        activeforeground=WHITE,
        relief="flat",
        anchor="w",
        padx=25,
        pady=14,
        cursor="hand2",
        command=go_attendance
    ).pack(
        fill="x",
        padx=10,
        pady=3
    )


    # =====================================================
    # MAIN CONTENT
    # =====================================================

    main = tk.Frame(
        root,
        bg=BG
    )

    main.pack(
        side="left",
        fill="both",
        expand=True
    )


    # =====================================================
    # PAGE TITLE
    # =====================================================

    tk.Label(
        main,
        text="Add Staff",
        font=(
            "Segoe UI",
            28,
            "bold"
        ),
        fg=TEXT,
        bg=BG
    ).pack(
        anchor="w",
        padx=45,
        pady=(25, 0)
    )


    tk.Label(
        main,
        text="Enter staff details to add a new staff member.",
        font=(
            "Segoe UI",
            11
        ),
        fg=GRAY,
        bg=BG
    ).pack(
        anchor="w",
        padx=47,
        pady=(2, 18)
    )


    # =====================================================
    # FORM CARD
    # =====================================================

    form_card = tk.Frame(
        main,
        bg=WHITE,
        highlightthickness=1,
        highlightbackground=LINE
    )

    form_card.pack(
        padx=45,
        fill="both",
        expand=True
    )


    # =====================================================
    # FORM
    # =====================================================

    form = tk.Frame(
        form_card,
        bg=WHITE
    )

    form.place(
        relx=0.5,
        rely=0.48,
        anchor="center",
        width=650
    )


    # =====================================================
    # LABEL FUNCTION
    # =====================================================

    def create_label(
        text,
        row,
        column
    ):

        tk.Label(
            form,
            text=text,
            font=(
                "Segoe UI",
                10,
                "bold"
            ),
            fg=TEXT,
            bg=WHITE
        ).grid(
            row=row,
            column=column,
            sticky="w",
            padx=12,
            pady=(8, 4)
        )


    # =====================================================
    # ENTRY FUNCTION
    # =====================================================

    def create_entry(
        row,
        column
    ):

        entry = tk.Entry(
            form,
            font=(
                "Segoe UI",
                11
            ),
            bg="#f8fafc",
            fg=TEXT,
            insertbackground=TEXT,
            relief="solid",
            bd=1
        )

        entry.grid(
            row=row,
            column=column,
            sticky="ew",
            padx=12,
            pady=(0, 10),
            ipady=7
        )

        return entry


    # =====================================================
    # NAME
    # =====================================================

    create_label(
        "Staff Name",
        0,
        0
    )

    name_entry = create_entry(
        1,
        0
    )


    # =====================================================
    # EMAIL
    # =====================================================

    create_label(
        "Email",
        0,
        1
    )

    email_entry = create_entry(
        1,
        1
    )


    # =====================================================
    # PHONE
    # =====================================================

    create_label(
        "Phone Number",
        2,
        0
    )

    phone_entry = create_entry(
        3,
        0
    )


    # =====================================================
    # DEPARTMENT
    # =====================================================

    create_label(
        "Department",
        2,
        1
    )

    department_entry = create_entry(
        3,
        1
    )


    # =====================================================
    # SALARY
    # =====================================================

    create_label(
        "Salary",
        4,
        0
    )

    salary_entry = create_entry(
        5,
        0
    )


    # =====================================================
    # COLUMN CONFIGURATION
    # =====================================================

    form.columnconfigure(
        0,
        weight=1
    )

    form.columnconfigure(
        1,
        weight=1
    )


    # =====================================================
    # BUTTON FRAME
    # =====================================================

    button_frame = tk.Frame(
        form,
        bg=WHITE
    )

    button_frame.grid(
        row=6,
        column=0,
        columnspan=2,
        pady=(18, 5)
    )


    # =====================================================
    # ADD BUTTON
    # =====================================================

    tk.Button(
        button_frame,
        text="✓  Add Staff",
        font=(
            "Segoe UI",
            11,
            "bold"
        ),
        bg=GREEN,
        fg=WHITE,
        activebackground="#15803d",
        activeforeground=WHITE,
        relief="flat",
        cursor="hand2",
        padx=25,
        pady=10,
        command=add_staff
    ).pack(
        side="left",
        padx=8
    )


    # =====================================================
    # CLEAR BUTTON
    # =====================================================

    tk.Button(
        button_frame,
        text="Clear",
        font=(
            "Segoe UI",
            11,
            "bold"
        ),
        bg="#e2e8f0",
        fg=TEXT,
        activebackground="#cbd5e1",
        relief="flat",
        cursor="hand2",
        padx=30,
        pady=10,
        command=clear_fields
    ).pack(
        side="left",
        padx=8
    )


    # =====================================================
    # FOOTER
    # =====================================================

    tk.Label(
        main,
        text="Staff Management System",
        font=(
            "Segoe UI",
            9
        ),
        fg=GRAY,
        bg=BG
    ).pack(
        pady=10
    )


    # =====================================================
    # FOCUS
    # =====================================================

    name_entry.focus()


    # =====================================================
    # MAIN LOOP
    # =====================================================

    root.mainloop()


# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    open_staff()