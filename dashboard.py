
import tkinter as tk
from tkinter import messagebox
import sqlite3
import os
import subprocess
import sys
from datetime import datetime


# =========================================================
# DATABASE
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "staff.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


# =========================================================
# DASHBOARD FUNCTIONS
# =========================================================

def get_total_staff():

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM staff")

        total = cursor.fetchone()[0]

        conn.close()

        return total

    except:
        return 0


def get_today_attendance():

    try:
        conn = get_connection()
        cursor = conn.cursor()

        today = datetime.now().strftime("%Y-%m-%d")

        cursor.execute("""
            SELECT COUNT(*)
            FROM attendance
            WHERE date = ?
            AND status = 'Present'
        """, (today,))

        total = cursor.fetchone()[0]

        conn.close()

        return total

    except:
        return 0


# =========================================================
# OPEN PAGES
# =========================================================

def open_page(filename):

    try:

        file_path = os.path.join(
            BASE_DIR,
            filename
        )

        subprocess.Popen([
            sys.executable,
            file_path
        ])

    except Exception as e:

        messagebox.showerror(
            "Error",
            f"Page open करता आली नाही.\n\n{e}"
        )


def open_staff():
    open_page("staff.py")


def open_view_staff():
    open_page("view_staff.py")


def open_search_staff():
    open_page("search_staff.py")


def open_attendance():
    open_page("attendance.py")


def open_staff_report():
    open_page("staff_report.py")


def open_salary_report():
    open_page("salary_report.py")


def open_attendance_report():
    open_page("attendance_report.py")


def open_leave_application():
    open_page("leave_application.py")


# =========================================================
# LOGOUT
# =========================================================

def logout():

    answer = messagebox.askyesno(
        "Logout",
        "तुम्हाला Logout करायचे आहे का?"
    )

    if answer:

        root.destroy()

        try:

            import login

            login.open_login()

        except Exception:

            pass


# =========================================================
# CLOCK
# =========================================================

def update_clock():

    current = datetime.now().strftime(
        "%d-%m-%Y   %I:%M:%S %p"
    )

    clock_label.config(
        text=current
    )

    root.after(
        1000,
        update_clock
    )


# =========================================================
# REFRESH DASHBOARD
# =========================================================

def refresh_dashboard():

    total_staff_label.config(
        text=str(get_total_staff())
    )

    today_attendance_label.config(
        text=str(get_today_attendance())
    )

    root.after(
        5000,
        refresh_dashboard
    )


# =========================================================
# MAIN DASHBOARD
# =========================================================

def open_dashboard():

    global root
    global clock_label
    global total_staff_label
    global today_attendance_label

    root = tk.Tk()

    root.title(
        "Staff Management System - Dashboard"
    )

    root.geometry(
        "1250x750"
    )

    root.minsize(
        1000,
        650
    )

    root.resizable(
        True,
        True
    )

    root.configure(
        bg="#f4f7ff"
    )


    # =====================================================
    # COLORS
    # =====================================================

    BG = "#f4f7ff"
    HEADER = "#071b49"
    SIDEBAR = "#081633"
    BLUE = "#2563eb"
    CYAN = "#06b6d4"
    GREEN = "#16a34a"
    ORANGE = "#f59e0b"
    WHITE = "#ffffff"
    TEXT = "#172554"
    GRAY = "#64748b"


    # =====================================================
    # HEADER
    # =====================================================

    header = tk.Frame(
        root,
        bg=HEADER,
        height=80
    )

    header.pack(
        side="top",
        fill="x"
    )

    header.pack_propagate(False)


    tk.Label(
        header,
        text="STAFF MANAGEMENT SYSTEM",
        font=("Arial", 22, "bold"),
        bg=HEADER,
        fg=WHITE
    ).place(
        x=280,
        y=12
    )


    tk.Label(
        header,
        text="Smart • Simple • Efficient Staff Management",
        font=("Arial", 10),
        bg=HEADER,
        fg="#dbeafe"
    ).place(
        x=350,
        y=47
    )


    clock_label = tk.Label(
        header,
        text="",
        font=("Arial", 10, "bold"),
        bg=HEADER,
        fg=WHITE
    )

    clock_label.place(
        x=870,
        y=28
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


    # =====================================================
    # SCROLLABLE SIDEBAR
    # =====================================================

    sidebar_top = tk.Frame(sidebar, bg=SIDEBAR)
    sidebar_top.pack(side="top", fill="x")

    tk.Label(
        sidebar_top,
        text="MAIN MENU",
        font=("Arial", 11, "bold"),
        bg=SIDEBAR,
        fg="#94a3b8"
    ).pack(
        anchor="w",
        padx=25,
        pady=(25, 12)
    )

    menu_area = tk.Frame(sidebar, bg=SIDEBAR)
    menu_area.pack(side="top", fill="both", expand=True)

    menu_canvas = tk.Canvas(
        menu_area,
        bg=SIDEBAR,
        highlightthickness=0,
        bd=0
    )
    menu_scrollbar = tk.Scrollbar(
        menu_area,
        orient="vertical",
        command=menu_canvas.yview
    )
    menu_canvas.configure(yscrollcommand=menu_scrollbar.set)

    menu_scrollbar.pack(side="right", fill="y")
    menu_canvas.pack(side="left", fill="both", expand=True)

    sidebar_menu = tk.Frame(menu_canvas, bg=SIDEBAR)
    menu_window = menu_canvas.create_window(
        (0, 0),
        window=sidebar_menu,
        anchor="nw"
    )

    def update_sidebar_scroll(event=None):
        menu_canvas.configure(scrollregion=menu_canvas.bbox("all"))
        menu_canvas.itemconfigure(menu_window, width=menu_canvas.winfo_width())

    sidebar_menu.bind("<Configure>", update_sidebar_scroll)
    menu_canvas.bind("<Configure>", update_sidebar_scroll)

    def sidebar_mousewheel(event):
        menu_canvas.yview_scroll(
            int(-1 * (event.delta / 120)),
            "units"
        )

    menu_canvas.bind_all("<MouseWheel>", sidebar_mousewheel)


    # =====================================================
    # SIDEBAR BUTTON FUNCTION
    # =====================================================

    def sidebar_button(
        text,
        command,
        bg_color=SIDEBAR
    ):

        button = tk.Button(
            sidebar_menu,
            text=text,
            font=("Arial", 10, "bold"),
            bg=bg_color,
            fg=WHITE,
            activebackground=BLUE,
            activeforeground=WHITE,
            relief="flat",
            anchor="w",
            padx=20,
            pady=11,
            cursor="hand2",
            command=command
        )

        button.pack(
            fill="x",
            padx=10,
            pady=2
        )

        return button


    # =====================================================
    # MENU
    # =====================================================

    sidebar_button(
        "🏠  Dashboard",
        lambda: None
    )

    sidebar_button(
        "👤  Add Staff",
        open_staff
    )

    sidebar_button(
        "📋  View Staff",
        open_view_staff
    )

    sidebar_button(
        "🔎  Search Staff",
        open_search_staff
    )

    sidebar_button(
        "📅  Attendance",
        open_attendance
    )


    sidebar_button(
        "📊  Staff Report",
        open_staff_report
    )

    sidebar_button(
        "📝  Attendance Report",
        open_attendance_report
    )

    sidebar_button(
        "📄  Leave Application",
        open_leave_application
    )

    sidebar_button(
        "💰  Salary Report",
        open_salary_report
    )


    # =====================================================
    # LOGOUT
    # =====================================================

    tk.Button(
        sidebar,
        text="🚪  Logout",
        font=("Arial", 10, "bold"),
        bg="#dc2626",
        fg=WHITE,
        activebackground="#b91c1c",
        activeforeground=WHITE,
        relief="flat",
        anchor="w",
        padx=20,
        pady=11,
        cursor="hand2",
        command=logout
    ).pack(
        side="bottom",
        fill="x",
        padx=10,
        pady=20
    )


    # =====================================================
    # MAIN CONTENT
    # =====================================================

    content = tk.Frame(
        root,
        bg=BG
    )

    content.pack(
        side="left",
        fill="both",
        expand=True
    )


    # =====================================================
    # WELCOME
    # =====================================================

    tk.Label(
        content,
        text="Welcome to Dashboard 👋",
        font=("Arial", 24, "bold"),
        bg=BG,
        fg=TEXT
    ).pack(
        anchor="w",
        padx=35,
        pady=(30, 5)
    )


    tk.Label(
        content,
        text="Manage your staff records and attendance easily.",
        font=("Arial", 11),
        bg=BG,
        fg=GRAY
    ).pack(
        anchor="w",
        padx=37
    )


    # =====================================================
    # STATISTICS FRAME
    # =====================================================

    stats_frame = tk.Frame(
        content,
        bg=BG
    )

    stats_frame.pack(
        fill="x",
        padx=35,
        pady=30
    )


    # =====================================================
    # TOTAL STAFF CARD
    # =====================================================

    staff_card = tk.Frame(
        stats_frame,
        bg=WHITE,
        width=240,
        height=130,
        bd=1,
        relief="solid"
    )

    staff_card.pack(
        side="left",
        padx=(0, 15)
    )

    staff_card.pack_propagate(False)


    tk.Label(
        staff_card,
        text="👤",
        font=("Arial", 25),
        bg=WHITE,
        fg=BLUE
    ).pack(
        pady=(15, 0)
    )


    tk.Label(
        staff_card,
        text="Total Staff",
        font=("Arial", 11, "bold"),
        bg=WHITE,
        fg=GRAY
    ).pack()


    total_staff_label = tk.Label(
        staff_card,
        text=str(get_total_staff()),
        font=("Arial", 22, "bold"),
        bg=WHITE,
        fg=TEXT
    )

    total_staff_label.pack()


    # =====================================================
    # ATTENDANCE CARD
    # =====================================================

    attendance_card = tk.Frame(
        stats_frame,
        bg=WHITE,
        width=240,
        height=130,
        bd=1,
        relief="solid"
    )

    attendance_card.pack(
        side="left",
        padx=15
    )

    attendance_card.pack_propagate(False)


    tk.Label(
        attendance_card,
        text="📅",
        font=("Arial", 25),
        bg=WHITE,
        fg=GREEN
    ).pack(
        pady=(15, 0)
    )


    tk.Label(
        attendance_card,
        text="Today's Present",
        font=("Arial", 11, "bold"),
        bg=WHITE,
        fg=GRAY
    ).pack()


    today_attendance_label = tk.Label(
        attendance_card,
        text=str(get_today_attendance()),
        font=("Arial", 22, "bold"),
        bg=WHITE,
        fg=TEXT
    )

    today_attendance_label.pack()


    # =====================================================
    # QUICK ACCESS
    # =====================================================

    quick_frame = tk.Frame(
        content,
        bg=WHITE,
        bd=1,
        relief="solid"
    )

    quick_frame.pack(
        fill="x",
        padx=35,
        pady=5
    )


    tk.Label(
        quick_frame,
        text="Quick Access",
        font=("Arial", 16, "bold"),
        bg=WHITE,
        fg=TEXT
    ).pack(
        anchor="w",
        padx=25,
        pady=(20, 15)
    )


    quick_buttons = tk.Frame(
        quick_frame,
        bg=WHITE
    )

    quick_buttons.pack(
        padx=20,
        pady=(0, 20)
    )


    tk.Button(
        quick_buttons,
        text="➕ Add New Staff",
        font=("Arial", 10, "bold"),
        bg=BLUE,
        fg=WHITE,
        relief="flat",
        cursor="hand2",
        padx=20,
        pady=10,
        command=open_staff
    ).pack(
        side="left",
        padx=5
    )


    tk.Button(
        quick_buttons,
        text="📋 View Staff",
        font=("Arial", 10, "bold"),
        bg=CYAN,
        fg=WHITE,
        relief="flat",
        cursor="hand2",
        padx=20,
        pady=10,
        command=open_view_staff
    ).pack(
        side="left",
        padx=5
    )


    tk.Button(
        quick_buttons,
        text="📊 Staff Report",
        font=("Arial", 10, "bold"),
        bg=ORANGE,
        fg=WHITE,
        relief="flat",
        cursor="hand2",
        padx=20,
        pady=10,
        command=open_staff_report
    ).pack(
        side="left",
        padx=5
    )


    tk.Button(
        quick_buttons,
        text="📝 Attendance Report",
        font=("Arial", 10, "bold"),
        bg=GREEN,
        fg=WHITE,
        relief="flat",
        cursor="hand2",
        padx=20,
        pady=10,
        command=open_attendance_report
    ).pack(
        side="left",
        padx=5
    )


    tk.Button(
        quick_buttons,
        text="📄 Leave Application",
        font=("Arial", 10, "bold"),
        bg=BLUE,
        fg=WHITE,
        relief="flat",
        cursor="hand2",
        padx=20,
        pady=10,
        command=open_leave_application
    ).pack(
        side="left",
        padx=5
    )


    # =====================================================
    # FOOTER
    # =====================================================

    tk.Label(
        content,
        text="Staff Management System  •  Smart • Simple • Efficient",
        font=("Arial", 9),
        bg=BG,
        fg=GRAY
    ).pack(
        side="bottom",
        pady=12
    )


    # =====================================================
    # START
    # =====================================================

    update_clock()

    refresh_dashboard()

    root.mainloop()


# =========================================================
# DIRECT RUN
# =========================================================

if __name__ == "__main__":
    open_dashboard()
