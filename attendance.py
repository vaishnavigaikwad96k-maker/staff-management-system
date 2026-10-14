import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import os
from datetime import datetime, date, timedelta

# ============================================================
# DATABASE
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "staff.db")

CL_LIMIT = 12
SL_LIMIT = 10

STATUS_LIST = ["Present", "Absent", "CL", "SL"]

BG = "#f4f7ff"
HEADER = "#071b49"
SIDEBAR = "#081633"
BLUE = "#2563eb"
PURPLE = "#7c3aed"
GREEN = "#16a34a"
RED = "#dc2626"
ORANGE = "#ea580c"
WHITE = "#ffffff"
TEXT = "#172554"
GRAY = "#64748b"
LINE = "#cbd5e1"
BLACK = "#000000"

root = None

# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_attendance_table():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (staff_id) REFERENCES staff(id)
        )
    """)

    conn.commit()
    conn.close()


# ============================================================
# STAFF SERIAL ID
# ============================================================
# IMPORTANT:
# Database madhla actual staff.id change hot nahi.
# UI madhe Staff ID 1,2,3,4... series-wise disel.
# ============================================================

def get_staff_data():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name
        FROM staff
        ORDER BY id ASC
    """)

    rows = cur.fetchall()
    conn.close()

    return rows


def get_staff_display_data():
    """
    Returns:
        display_values = ["1 - Rahul", "2 - Priya", ...]
        display_to_real = {1: actual_db_id, 2: actual_db_id}
        real_to_display = {actual_db_id: 1, ...}
    """

    rows = get_staff_data()

    display_values = []
    display_to_real = {}
    real_to_display = {}

    for display_id, (real_id, name) in enumerate(rows, start=1):

        display_values.append(
            f"{display_id} - {name}"
        )

        display_to_real[display_id] = real_id
        real_to_display[real_id] = display_id

    return display_values, display_to_real, real_to_display


def get_real_staff_id_from_combo(combo, mapping):
    value = combo.get().strip()

    if not value:
        return None

    try:
        display_id = int(value.split(" - ")[0])
        return mapping.get(display_id)
    except:
        return None


# ============================================================
# DATE VALIDATION
# ============================================================

def valid_date(date_text):
    try:
        datetime.strptime(date_text, "%Y-%m-%d")
        return True
    except:
        return False


# ============================================================
# CL / SL LIMIT
# ============================================================

def get_year_status_count(staff_id, year, status):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT COUNT(*)
        FROM attendance
        WHERE staff_id = ?
        AND substr(date, 1, 4) = ?
        AND status = ?
    """, (staff_id, str(year), status))

    count = cur.fetchone()[0]

    conn.close()

    return count


def check_leave_limit(staff_id, year, status, extra_count=1, exclude_id=None):

    if status not in ("CL", "SL"):
        return True

    conn = get_connection()
    cur = conn.cursor()

    query = """
        SELECT COUNT(*)
        FROM attendance
        WHERE staff_id = ?
        AND substr(date, 1, 4) = ?
        AND status = ?
    """

    params = [staff_id, str(year), status]

    if exclude_id is not None:
        query += " AND id != ?"
        params.append(exclude_id)

    cur.execute(query, params)

    current_count = cur.fetchone()[0]

    conn.close()

    limit = CL_LIMIT if status == "CL" else SL_LIMIT

    if current_count + extra_count > limit:

        messagebox.showwarning(
            "Leave Limit",
            f"{status} limit exceeded.\n\n"
            f"Yearly {status} Limit : {limit}\n"
            f"Already Used : {current_count}\n"
            f"Remaining : {max(0, limit - current_count)}"
        )

        return False

    return True


# ============================================================
# NAVIGATION
# ============================================================

def back_dashboard():
    try:
        root.destroy()

        import dashboard
        dashboard.open_dashboard()

    except Exception as e:
        messagebox.showerror("Error", str(e))


def go_add_staff():
    try:
        root.destroy()

        import staff
        staff.open_staff()

    except Exception as e:
        messagebox.showerror("Error", str(e))


def go_view_staff():
    try:
        root.destroy()

        import view_staff
        view_staff.open_view_staff()

    except Exception as e:
        messagebox.showerror("Error", str(e))


def go_search_staff():
    try:
        root.destroy()

        import search_staff
        search_staff.open_search_staff()

    except Exception as e:
        messagebox.showerror("Error", str(e))


# ============================================================
# STAFF COMBO
# ============================================================

def load_staff_combo(combo, mapping_store):

    values, display_to_real, real_to_display = get_staff_display_data()

    mapping_store.clear()
    mapping_store.update(display_to_real)

    combo["values"] = values

    if values:
        combo.current(0)
    else:
        combo.set("")


# ============================================================
# DAILY ATTENDANCE
# ============================================================

def mark_attendance(staff_combo, mapping, date_entry, status_var):

    real_staff_id = get_real_staff_id_from_combo(
        staff_combo,
        mapping
    )

    if real_staff_id is None:
        messagebox.showwarning(
            "Select Staff",
            "Please select staff."
        )
        return

    attendance_date = date_entry.get().strip()
    status = status_var.get().strip()

    if not valid_date(attendance_date):

        messagebox.showwarning(
            "Invalid Date",
            "Date format must be YYYY-MM-DD."
        )

        return

    if status not in STATUS_LIST:

        messagebox.showwarning(
            "Select Status",
            "Please select attendance status."
        )

        return

    year = attendance_date[:4]

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id
        FROM attendance
        WHERE staff_id = ?
        AND date = ?
    """, (real_staff_id, attendance_date))

    exists = cur.fetchone()

    if exists:

        conn.close()

        messagebox.showwarning(
            "Already Exists",
            "Attendance for this staff and date already exists."
        )

        return

    conn.close()

    if status in ("CL", "SL"):

        if not check_leave_limit(
            real_staff_id,
            year,
            status,
            1
        ):
            return

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO attendance
        (staff_id, date, status)
        VALUES (?, ?, ?)
    """, (
        real_staff_id,
        attendance_date,
        status
    ))

    conn.commit()
    conn.close()

    messagebox.showinfo(
        "Success",
        "Attendance marked successfully."
    )

    load_attendance()


# ============================================================
# LOAD DAILY ATTENDANCE TABLE
# ============================================================

def load_attendance(search_text=""):

    for widget in table_frame.winfo_children():
        widget.destroy()

    conn = get_connection()
    cur = conn.cursor()

    query = """
        SELECT
            a.id,
            a.staff_id,
            s.name,
            a.date,
            a.status
        FROM attendance a
        LEFT JOIN staff s
        ON a.staff_id = s.id
    """

    params = []

    if search_text:

        query += """
            WHERE
                s.name LIKE ?
                OR a.date LIKE ?
                OR a.status LIKE ?
        """

        value = f"%{search_text}%"

        params = [
            value,
            value,
            value
        ]

    query += """
        ORDER BY a.date DESC, a.id DESC
    """

    cur.execute(query, params)

    rows = cur.fetchall()

    # Actual DB ID -> Display Serial ID
    _, _, real_to_display = get_staff_display_data()

    conn.close()

    headers = [
        "ID",
        "STAFF ID",
        "STAFF NAME",
        "DATE",
        "STATUS",
        "ACTION"
    ]

    widths = [
        60,
        100,
        200,
        130,
        120,
        180
    ]

    for col, header in enumerate(headers):

        lbl = tk.Label(
            table_frame,
            text=header,
            bg=HEADER,
            fg=WHITE,
            font=("Segoe UI", 10, "bold"),
            padx=8,
            pady=10
        )

        lbl.grid(
            row=0,
            column=col,
            sticky="nsew"
        )

        table_frame.grid_columnconfigure(
            col,
            minsize=widths[col]
        )

    for row_no, row in enumerate(rows, start=1):

        attendance_id = row[0]
        real_staff_id = row[1]
        staff_name = row[2] or ""
        attendance_date = row[3]
        status = row[4]

        # ====================================================
        # SERIES-WISE STAFF ID
        # ====================================================

        display_staff_id = real_to_display.get(
            real_staff_id,
            ""
        )

        values = [
            row_no,
            display_staff_id,
            staff_name,
            attendance_date,
            status
        ]

        for col, value in enumerate(values):

            lbl = tk.Label(
                table_frame,
                text=value,

                # IMPORTANT:
                # Staff ID BLACK COLOR
                fg=BLACK,

                bg=WHITE if row_no % 2 else "#f8fafc",

                font=(
                    "Segoe UI",
                    10,
                    "bold" if col == 1 else "normal"
                ),

                padx=8,
                pady=8
            )

            lbl.grid(
                row=row_no,
                column=col,
                sticky="nsew"
            )

        action_frame = tk.Frame(
            table_frame,
            bg=WHITE if row_no % 2 else "#f8fafc"
        )

        action_frame.grid(
            row=row_no,
            column=5,
            padx=5,
            pady=4
        )

        tk.Button(
            action_frame,
            text="EDIT",
            bg=BLUE,
            fg=WHITE,
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            command=lambda x=attendance_id:
                update_attendance(x)
        ).pack(
            side="left",
            padx=3
        )

        tk.Button(
            action_frame,
            text="DELETE",
            bg=RED,
            fg=WHITE,
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            command=lambda x=attendance_id:
                delete_attendance(x)
        ).pack(
            side="left",
            padx=3
        )

    if not rows:

        tk.Label(
            table_frame,
            text="No attendance record found.",
            bg=WHITE,
            fg=GRAY,
            font=("Segoe UI", 11)
        ).grid(
            row=1,
            column=0,
            columnspan=6,
            pady=30
        )


# ============================================================
# UPDATE ATTENDANCE
# ============================================================

def update_attendance(attendance_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT staff_id, date, status
        FROM attendance
        WHERE id = ?
    """, (attendance_id,))

    row = cur.fetchone()

    conn.close()

    if not row:
        return

    real_staff_id, old_date, old_status = row

    win = tk.Toplevel(root)
    win.title("Update Attendance")
    win.geometry("450x350")
    win.configure(bg=BG)
    win.resizable(False, False)

    tk.Label(
        win,
        text="UPDATE ATTENDANCE",
        bg=HEADER,
        fg=WHITE,
        font=("Segoe UI", 16, "bold"),
        pady=15
    ).pack(fill="x")

    values, display_to_real, real_to_display = get_staff_display_data()

    staff_display_id = real_to_display.get(
        real_staff_id,
        ""
    )

    staff_name = ""

    for value in values:

        if value.startswith(
            f"{staff_display_id} - "
        ):
            staff_name = value
            break

    tk.Label(
        win,
        text="Staff",
        bg=BG,
        fg=TEXT,
        font=("Segoe UI", 10, "bold")
    ).pack(anchor="w", padx=30, pady=(20, 5))

    tk.Label(
        win,
        text=staff_name,
        bg=WHITE,
        fg=BLACK,
        font=("Segoe UI", 11),
        anchor="w",
        padx=10
    ).pack(
        fill="x",
        padx=30
    )

    tk.Label(
        win,
        text="Date (YYYY-MM-DD)",
        bg=BG,
        fg=TEXT,
        font=("Segoe UI", 10, "bold")
    ).pack(anchor="w", padx=30, pady=(15, 5))

    date_var = tk.StringVar(value=old_date)

    date_entry = tk.Entry(
        win,
        textvariable=date_var,
        font=("Segoe UI", 11)
    )

    date_entry.pack(
        fill="x",
        padx=30
    )

    tk.Label(
        win,
        text="Status",
        bg=BG,
        fg=TEXT,
        font=("Segoe UI", 10, "bold")
    ).pack(anchor="w", padx=30, pady=(15, 5))

    status_var = tk.StringVar(value=old_status)

    status_combo = ttk.Combobox(
        win,
        textvariable=status_var,
        values=STATUS_LIST,
        state="readonly",
        font=("Segoe UI", 11)
    )

    status_combo.pack(
        fill="x",
        padx=30
    )

    def save_update():

        new_date = date_var.get().strip()
        new_status = status_var.get().strip()

        if not valid_date(new_date):

            messagebox.showwarning(
                "Invalid Date",
                "Date format must be YYYY-MM-DD.",
                parent=win
            )

            return

        if new_status not in STATUS_LIST:

            messagebox.showwarning(
                "Status",
                "Please select status.",
                parent=win
            )

            return

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id
            FROM attendance
            WHERE staff_id = ?
            AND date = ?
            AND id != ?
        """, (
            real_staff_id,
            new_date,
            attendance_id
        ))

        duplicate = cur.fetchone()

        conn.close()

        if duplicate:

            messagebox.showwarning(
                "Duplicate",
                "Attendance already exists for this date.",
                parent=win
            )

            return

        if new_status in ("CL", "SL"):

            if not check_leave_limit(
                real_staff_id,
                new_date[:4],
                new_status,
                1,
                attendance_id
            ):
                return

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            UPDATE attendance
            SET date = ?, status = ?
            WHERE id = ?
        """, (
            new_date,
            new_status,
            attendance_id
        ))

        conn.commit()
        conn.close()

        win.destroy()

        messagebox.showinfo(
            "Success",
            "Attendance updated successfully."
        )

        load_attendance()

    tk.Button(
        win,
        text="UPDATE",
        bg=GREEN,
        fg=WHITE,
        relief="flat",
        font=("Segoe UI", 11, "bold"),
        padx=25,
        pady=10,
        command=save_update
    ).pack(pady=25)


# ============================================================
# DELETE
# ============================================================

def delete_attendance(attendance_id):

    answer = messagebox.askyesno(
        "Delete",
        "Are you sure you want to delete this attendance?"
    )

    if not answer:
        return

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM attendance
        WHERE id = ?
    """, (attendance_id,))

    conn.commit()
    conn.close()

    messagebox.showinfo(
        "Deleted",
        "Attendance deleted successfully."
    )

    load_attendance()


# ============================================================
# MONTHLY ATTENDANCE ENTRY
# ============================================================

def open_monthly_entry():

    win = tk.Toplevel(root)

    win.title("Monthly Attendance Entry")
    win.geometry("900x700")
    win.configure(bg=BG)

    tk.Label(
        win,
        text="MONTHLY ATTENDANCE ENTRY",
        bg=HEADER,
        fg=WHITE,
        font=("Segoe UI", 18, "bold"),
        pady=15
    ).pack(fill="x")

    top = tk.Frame(
        win,
        bg=BG
    )

    top.pack(
        fill="x",
        padx=20,
        pady=15
    )

    # Staff
    tk.Label(
        top,
        text="Staff",
        bg=BG,
        fg=TEXT,
        font=("Segoe UI", 10, "bold")
    ).grid(row=0, column=0, padx=5, pady=5)

    staff_var = tk.StringVar()

    staff_combo = ttk.Combobox(
        top,
        textvariable=staff_var,
        state="readonly",
        width=25
    )

    staff_combo.grid(
        row=1,
        column=0,
        padx=5
    )

    mapping = {}

    load_staff_combo(
        staff_combo,
        mapping
    )

    # Year
    tk.Label(
        top,
        text="Year",
        bg=BG,
        fg=TEXT,
        font=("Segoe UI", 10, "bold")
    ).grid(row=0, column=1, padx=5)

    year_var = tk.StringVar(
        value=str(datetime.now().year)
    )

    year_entry = tk.Entry(
        top,
        textvariable=year_var,
        width=10,
        font=("Segoe UI", 11)
    )

    year_entry.grid(
        row=1,
        column=1,
        padx=5
    )

    # Month
    tk.Label(
        top,
        text="Month",
        bg=BG,
        fg=TEXT,
        font=("Segoe UI", 10, "bold")
    ).grid(row=0, column=2, padx=5)

    month_var = tk.StringVar(
        value=datetime.now().strftime("%m")
    )

    month_combo = ttk.Combobox(
        top,
        textvariable=month_var,
        values=[
            "01", "02", "03", "04",
            "05", "06", "07", "08",
            "09", "10", "11", "12"
        ],
        state="readonly",
        width=8
    )

    month_combo.grid(
        row=1,
        column=2,
        padx=5
    )

    # Table
    container = tk.Frame(
        win,
        bg=WHITE
    )

    container.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=10
    )

    canvas = tk.Canvas(
        container,
        bg=WHITE,
        highlightthickness=0
    )

    scrollbar = ttk.Scrollbar(
        container,
        orient="vertical",
        command=canvas.yview
    )

    inner = tk.Frame(
        canvas,
        bg=WHITE
    )

    canvas.create_window(
        (0, 0),
        window=inner,
        anchor="nw"
    )

    canvas.configure(
        yscrollcommand=scrollbar.set
    )

    canvas.pack(
        side="left",
        fill="both",
        expand=True
    )

    scrollbar.pack(
        side="right",
        fill="y"
    )

    status_vars = {}

    def load_month():

        for widget in inner.winfo_children():
            widget.destroy()

        status_vars.clear()

        real_staff_id = get_real_staff_id_from_combo(
            staff_combo,
            mapping
        )

        if real_staff_id is None:
            messagebox.showwarning(
                "Staff",
                "Please select staff.",
                parent=win
            )
            return

        try:
            year = int(year_var.get())
            month = int(month_var.get())

            first_day = date(
                year,
                month,
                1
            )

            if month == 12:
                next_month = date(
                    year + 1,
                    1,
                    1
                )
            else:
                next_month = date(
                    year,
                    month + 1,
                    1
                )

        except:

            messagebox.showwarning(
                "Invalid",
                "Enter valid year and month.",
                parent=win
            )

            return

        current_day = first_day

        headers = [
            "SR. NO.",
            "DATE",
            "DAY",
            "STATUS"
        ]

        widths = [80, 150, 150, 180]

        for col, header in enumerate(headers):

            tk.Label(
                inner,
                text=header,
                bg=HEADER,
                fg=WHITE,
                font=("Segoe UI", 10, "bold"),
                padx=10,
                pady=10
            ).grid(
                row=0,
                column=col,
                sticky="nsew"
            )

            inner.grid_columnconfigure(
                col,
                minsize=widths[col]
            )

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT date, status
            FROM attendance
            WHERE staff_id = ?
            AND date >= ?
            AND date < ?
        """, (
            real_staff_id,
            first_day.strftime("%Y-%m-%d"),
            next_month.strftime("%Y-%m-%d")
        ))

        existing = {
            r[0]: r[1]
            for r in cur.fetchall()
        }

        conn.close()

        row_no = 1

        while current_day < next_month:

            day_string = current_day.strftime(
                "%Y-%m-%d"
            )

            status_var = tk.StringVar(
                value=existing.get(
                    day_string,
                    ""
                )
            )

            status_vars[day_string] = status_var

            bg = WHITE if row_no % 2 else "#f8fafc"

            tk.Label(
                inner,
                text=row_no,
                bg=bg,
                fg=BLACK,
                font=("Segoe UI", 10)
            ).grid(
                row=row_no,
                column=0,
                pady=4
            )

            tk.Label(
                inner,
                text=day_string,
                bg=bg,
                fg=BLACK,
                font=("Segoe UI", 10)
            ).grid(
                row=row_no,
                column=1
            )

            tk.Label(
                inner,
                text=current_day.strftime("%A"),
                bg=bg,
                fg=BLACK,
                font=("Segoe UI", 10)
            ).grid(
                row=row_no,
                column=2
            )

            combo = ttk.Combobox(
                inner,
                textvariable=status_var,
                values=["", *STATUS_LIST],
                state="readonly",
                width=15
            )

            combo.grid(
                row=row_no,
                column=3,
                padx=10,
                pady=3
            )

            current_day += timedelta(days=1)
            row_no += 1

        inner.update_idletasks()

        canvas.configure(
            scrollregion=canvas.bbox("all")
        )

    def save_month():

        real_staff_id = get_real_staff_id_from_combo(
            staff_combo,
            mapping
        )

        if real_staff_id is None:
            return

        try:
            year = int(year_var.get())
            month = int(month_var.get())
        except:
            return

        cl_count = 0
        sl_count = 0

        for value in status_vars.values():

            if value.get() == "CL":
                cl_count += 1

            elif value.get() == "SL":
                sl_count += 1

        if cl_count > CL_LIMIT:

            messagebox.showwarning(
                "CL Limit",
                f"Maximum {CL_LIMIT} CL allowed in a year.",
                parent=win
            )

            return

        if sl_count > SL_LIMIT:

            messagebox.showwarning(
                "SL Limit",
                f"Maximum {SL_LIMIT} SL allowed in a year.",
                parent=win
            )

            return

        conn = get_connection()
        cur = conn.cursor()

        for day_string, status_var in status_vars.items():

            status = status_var.get().strip()

            cur.execute("""
                SELECT id
                FROM attendance
                WHERE staff_id = ?
                AND date = ?
            """, (
                real_staff_id,
                day_string
            ))

            existing = cur.fetchone()

            if status == "":

                if existing:

                    cur.execute("""
                        DELETE FROM attendance
                        WHERE id = ?
                    """, (
                        existing[0],
                    ))

                continue

            if existing:

                cur.execute("""
                    UPDATE attendance
                    SET status = ?
                    WHERE id = ?
                """, (
                    status,
                    existing[0]
                ))

            else:

                cur.execute("""
                    INSERT INTO attendance
                    (staff_id, date, status)
                    VALUES (?, ?, ?)
                """, (
                    real_staff_id,
                    day_string,
                    status
                ))

        conn.commit()
        conn.close()

        messagebox.showinfo(
            "Success",
            "Monthly attendance saved successfully.",
            parent=win
        )

        load_attendance()

    def apply_status_to_all():

        status = all_status_var.get()

        if not status:
            return

        for var in status_vars.values():
            var.set(status)

    all_status_var = tk.StringVar()

    ttk.Combobox(
        top,
        textvariable=all_status_var,
        values=STATUS_LIST,
        state="readonly",
        width=15
    ).grid(
        row=1,
        column=3,
        padx=10
    )

    tk.Button(
        top,
        text="APPLY ALL",
        bg=PURPLE,
        fg=WHITE,
        relief="flat",
        font=("Segoe UI", 10, "bold"),
        command=apply_status_to_all
    ).grid(
        row=1,
        column=4,
        padx=5
    )

    tk.Button(
        top,
        text="LOAD MONTH",
        bg=BLUE,
        fg=WHITE,
        relief="flat",
        font=("Segoe UI", 10, "bold"),
        command=load_month
    ).grid(
        row=1,
        column=5,
        padx=5
    )

    tk.Button(
        win,
        text="SAVE MONTHLY ATTENDANCE",
        bg=GREEN,
        fg=WHITE,
        relief="flat",
        font=("Segoe UI", 12, "bold"),
        padx=25,
        pady=10,
        command=save_month
    ).pack(
        pady=15
    )

    load_month()


# ============================================================
# YEARLY ATTENDANCE ENTRY
# ============================================================

def open_yearly_entry():

    win = tk.Toplevel(root)

    win.title("Yearly Attendance Entry")
    win.geometry("900x700")
    win.configure(bg=BG)

    tk.Label(
        win,
        text="YEARLY ATTENDANCE ENTRY",
        bg=HEADER,
        fg=WHITE,
        font=("Segoe UI", 18, "bold"),
        pady=15
    ).pack(fill="x")

    top = tk.Frame(
        win,
        bg=BG
    )

    top.pack(
        fill="x",
        padx=20,
        pady=15
    )

    tk.Label(
        top,
        text="Staff",
        bg=BG,
        fg=TEXT,
        font=("Segoe UI", 10, "bold")
    ).grid(row=0, column=0)

    staff_combo = ttk.Combobox(
        top,
        state="readonly",
        width=25
    )

    staff_combo.grid(
        row=1,
        column=0,
        padx=10
    )

    mapping = {}

    load_staff_combo(
        staff_combo,
        mapping
    )

    tk.Label(
        top,
        text="Year",
        bg=BG,
        fg=TEXT,
        font=("Segoe UI", 10, "bold")
    ).grid(row=0, column=1)

    year_var = tk.StringVar(
        value=str(datetime.now().year)
    )

    tk.Entry(
        top,
        textvariable=year_var,
        width=10,
        font=("Segoe UI", 11)
    ).grid(
        row=1,
        column=1,
        padx=10
    )

    container = tk.Frame(
        win,
        bg=WHITE
    )

    container.pack(
        fill="both",
        expand=True,
        padx=20
    )

    canvas = tk.Canvas(
        container,
        bg=WHITE,
        highlightthickness=0
    )

    scrollbar = ttk.Scrollbar(
        container,
        orient="vertical",
        command=canvas.yview
    )

    inner = tk.Frame(
        canvas,
        bg=WHITE
    )

    canvas.create_window(
        (0, 0),
        window=inner,
        anchor="nw"
    )

    canvas.configure(
        yscrollcommand=scrollbar.set
    )

    canvas.pack(
        side="left",
        fill="both",
        expand=True
    )

    scrollbar.pack(
        side="right",
        fill="y"
    )

    status_vars = {}

    def load_year():

        for widget in inner.winfo_children():
            widget.destroy()

        status_vars.clear()

        real_staff_id = get_real_staff_id_from_combo(
            staff_combo,
            mapping
        )

        if real_staff_id is None:
            return

        try:
            year = int(year_var.get())
            first_day = date(year, 1, 1)
            next_year = date(year + 1, 1, 1)
        except:
            messagebox.showwarning(
                "Invalid",
                "Enter valid year.",
                parent=win
            )
            return

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT date, status
            FROM attendance
            WHERE staff_id = ?
            AND date >= ?
            AND date < ?
        """, (
            real_staff_id,
            first_day.strftime("%Y-%m-%d"),
            next_year.strftime("%Y-%m-%d")
        ))

        existing = {
            r[0]: r[1]
            for r in cur.fetchall()
        }

        conn.close()

        headers = [
            "SR. NO.",
            "DATE",
            "DAY",
            "STATUS"
        ]

        for col, header in enumerate(headers):

            tk.Label(
                inner,
                text=header,
                bg=HEADER,
                fg=WHITE,
                font=("Segoe UI", 10, "bold"),
                padx=10,
                pady=10
            ).grid(
                row=0,
                column=col,
                sticky="nsew"
            )

        current = first_day
        row_no = 1

        while current < next_year:

            day_string = current.strftime(
                "%Y-%m-%d"
            )

            var = tk.StringVar(
                value=existing.get(
                    day_string,
                    ""
                )
            )

            status_vars[day_string] = var

            bg = WHITE if row_no % 2 else "#f8fafc"

            tk.Label(
                inner,
                text=row_no,
                bg=bg,
                fg=BLACK
            ).grid(
                row=row_no,
                column=0,
                pady=3
            )

            tk.Label(
                inner,
                text=day_string,
                bg=bg,
                fg=BLACK
            ).grid(
                row=row_no,
                column=1
            )

            tk.Label(
                inner,
                text=current.strftime("%A"),
                bg=bg,
                fg=BLACK
            ).grid(
                row=row_no,
                column=2
            )

            ttk.Combobox(
                inner,
                textvariable=var,
                values=["", *STATUS_LIST],
                state="readonly",
                width=15
            ).grid(
                row=row_no,
                column=3,
                pady=3
            )

            current += timedelta(days=1)
            row_no += 1

        inner.update_idletasks()

        canvas.configure(
            scrollregion=canvas.bbox("all")
        )

    def save_year():

        real_staff_id = get_real_staff_id_from_combo(
            staff_combo,
            mapping
        )

        if real_staff_id is None:
            return

        cl_count = sum(
            1 for v in status_vars.values()
            if v.get() == "CL"
        )

        sl_count = sum(
            1 for v in status_vars.values()
            if v.get() == "SL"
        )

        if cl_count > CL_LIMIT:

            messagebox.showwarning(
                "CL Limit",
                f"Maximum {CL_LIMIT} CL allowed.",
                parent=win
            )

            return

        if sl_count > SL_LIMIT:

            messagebox.showwarning(
                "SL Limit",
                f"Maximum {SL_LIMIT} SL allowed.",
                parent=win
            )

            return

        conn = get_connection()
        cur = conn.cursor()

        for day_string, var in status_vars.items():

            status = var.get().strip()

            cur.execute("""
                SELECT id
                FROM attendance
                WHERE staff_id = ?
                AND date = ?
            """, (
                real_staff_id,
                day_string
            ))

            existing = cur.fetchone()

            if status == "":

                if existing:

                    cur.execute("""
                        DELETE FROM attendance
                        WHERE id = ?
                    """, (
                        existing[0],
                    ))

            elif existing:

                cur.execute("""
                    UPDATE attendance
                    SET status = ?
                    WHERE id = ?
                """, (
                    status,
                    existing[0]
                ))

            else:

                cur.execute("""
                    INSERT INTO attendance
                    (staff_id, date, status)
                    VALUES (?, ?, ?)
                """, (
                    real_staff_id,
                    day_string,
                    status
                ))

        conn.commit()
        conn.close()

        messagebox.showinfo(
            "Success",
            "Yearly attendance saved successfully.",
            parent=win
        )

        load_attendance()

    tk.Button(
        top,
        text="LOAD YEAR",
        bg=BLUE,
        fg=WHITE,
        relief="flat",
        font=("Segoe UI", 10, "bold"),
        command=load_year
    ).grid(
        row=1,
        column=2,
        padx=10
    )

    tk.Button(
        win,
        text="SAVE YEARLY ATTENDANCE",
        bg=GREEN,
        fg=WHITE,
        relief="flat",
        font=("Segoe UI", 12, "bold"),
        padx=25,
        pady=10,
        command=save_year
    ).pack(
        pady=15
    )

    load_year()


# ============================================================
# MONTHLY RECORD - SEPARATE
# ============================================================

def open_monthly_record():

    win = tk.Toplevel(root)

    win.title("Monthly Attendance Record")
    win.geometry("1100x650")
    win.configure(bg=BG)

    tk.Label(
        win,
        text="MONTHLY ATTENDANCE RECORD",
        bg=HEADER,
        fg=WHITE,
        font=("Segoe UI", 18, "bold"),
        pady=15
    ).pack(fill="x")

    filter_frame = tk.Frame(
        win,
        bg=BG
    )

    filter_frame.pack(
        fill="x",
        padx=20,
        pady=15
    )

    tk.Label(
        filter_frame,
        text="Month",
        bg=BG,
        fg=TEXT,
        font=("Segoe UI", 10, "bold")
    ).grid(row=0, column=0)

    month_var = tk.StringVar(
        value=str(datetime.now().month).zfill(2)
    )

    ttk.Combobox(
        filter_frame,
        textvariable=month_var,
        values=[
            "01", "02", "03", "04",
            "05", "06", "07", "08",
            "09", "10", "11", "12"
        ],
        state="readonly",
        width=8
    ).grid(
        row=1,
        column=0,
        padx=5
    )

    tk.Label(
        filter_frame,
        text="Year",
        bg=BG,
        fg=TEXT,
        font=("Segoe UI", 10, "bold")
    ).grid(row=0, column=1)

    year_var = tk.StringVar(
        value=str(datetime.now().year)
    )

    tk.Entry(
        filter_frame,
        textvariable=year_var,
        width=10,
        font=("Segoe UI", 11)
    ).grid(
        row=1,
        column=1,
        padx=5
    )

    tk.Label(
        filter_frame,
        text="Staff ID",
        bg=BG,
        fg=TEXT,
        font=("Segoe UI", 10, "bold")
    ).grid(row=0, column=2)

    staff_var = tk.StringVar()

    staff_combo = ttk.Combobox(
        filter_frame,
        textvariable=staff_var,
        state="readonly",
        width=25
    )

    staff_combo.grid(
        row=1,
        column=2,
        padx=5
    )

    mapping = {}

    load_staff_combo(
        staff_combo,
        mapping
    )

    container = tk.Frame(
        win,
        bg=WHITE
    )

    container.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=10
    )

    canvas = tk.Canvas(
        container,
        bg=WHITE,
        highlightthickness=0
    )

    scrollbar = ttk.Scrollbar(
        container,
        orient="vertical",
        command=canvas.yview
    )

    inner = tk.Frame(
        canvas,
        bg=WHITE
    )

    canvas.create_window(
        (0, 0),
        window=inner,
        anchor="nw"
    )

    canvas.configure(
        yscrollcommand=scrollbar.set
    )

    canvas.pack(
        side="left",
        fill="both",
        expand=True
    )

    scrollbar.pack(
        side="right",
        fill="y"
    )

    def show_record():

        for widget in inner.winfo_children():
            widget.destroy()

        try:
            year = int(year_var.get())
            month = int(month_var.get())
        except:

            messagebox.showwarning(
                "Invalid",
                "Enter valid month/year.",
                parent=win
            )

            return

        real_staff_id = get_real_staff_id_from_combo(
            staff_combo,
            mapping
        )

        query = """
            SELECT
                a.date,
                a.status,
                s.name
            FROM attendance a
            LEFT JOIN staff s
            ON a.staff_id = s.id
            WHERE substr(a.date,1,4) = ?
            AND substr(a.date,6,2) = ?
        """

        params = [
            str(year),
            f"{month:02d}"
        ]

        if real_staff_id is not None:

            query += " AND a.staff_id = ?"
            params.append(real_staff_id)

        query += " ORDER BY a.date ASC"

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            query,
            params
        )

        rows = cur.fetchall()

        _, _, real_to_display = get_staff_display_data()

        conn.close()

        headers = [
            "SR. NO.",
            "STAFF ID",
            "STAFF NAME",
            "DATE",
            "DAY",
            "STATUS"
        ]

        for col, header in enumerate(headers):

            tk.Label(
                inner,
                text=header,
                bg=HEADER,
                fg=WHITE,
                font=("Segoe UI", 10, "bold"),
                padx=8,
                pady=10
            ).grid(
                row=0,
                column=col,
                sticky="nsew"
            )

        for row_no, row in enumerate(rows, start=1):

            attendance_date = row[0]
            status = row[1]
            staff_name = row[2] or ""

            # Find actual staff ID from name/date safely
            conn = get_connection()
            cur = conn.cursor()

            cur.execute("""
                SELECT staff_id
                FROM attendance
                WHERE date = ?
                AND status = ?
                LIMIT 1
            """, (
                attendance_date,
                status
            ))

            result = cur.fetchone()

            conn.close()

            real_id = result[0] if result else None

            display_id = real_to_display.get(
                real_id,
                ""
            )

            d = datetime.strptime(
                attendance_date,
                "%Y-%m-%d"
            )

            values = [
                row_no,
                display_id,
                staff_name,
                attendance_date,
                d.strftime("%A"),
                status
            ]

            for col, value in enumerate(values):

                tk.Label(
                    inner,
                    text=value,
                    bg=WHITE if row_no % 2 else "#f8fafc",
                    fg=BLACK,
                    font=(
                        "Segoe UI",
                        10,
                        "bold" if col == 1 else "normal"
                    ),
                    padx=8,
                    pady=8
                ).grid(
                    row=row_no,
                    column=col,
                    sticky="nsew"
                )

        if not rows:

            tk.Label(
                inner,
                text="No monthly record found.",
                bg=WHITE,
                fg=GRAY,
                font=("Segoe UI", 11)
            ).grid(
                row=1,
                column=0,
                columnspan=6,
                pady=30
            )

        inner.update_idletasks()

        canvas.configure(
            scrollregion=canvas.bbox("all")
        )

    tk.Button(
        filter_frame,
        text="SHOW MONTHLY RECORD",
        bg=BLUE,
        fg=WHITE,
        relief="flat",
        font=("Segoe UI", 10, "bold"),
        padx=15,
        pady=7,
        command=show_record
    ).grid(
        row=1,
        column=3,
        padx=15
    )

    show_record()


# ============================================================
# YEARLY RECORD - SEPARATE
# ============================================================

def open_yearly_record():

    win = tk.Toplevel(root)

    win.title("Yearly Attendance Record")
    win.geometry("1100x650")
    win.configure(bg=BG)

    tk.Label(
        win,
        text="YEARLY ATTENDANCE RECORD",
        bg=HEADER,
        fg=WHITE,
        font=("Segoe UI", 18, "bold"),
        pady=15
    ).pack(fill="x")

    top = tk.Frame(
        win,
        bg=BG
    )

    top.pack(
        fill="x",
        padx=20,
        pady=15
    )

    tk.Label(
        top,
        text="Year",
        bg=BG,
        fg=TEXT,
        font=("Segoe UI", 10, "bold")
    ).grid(row=0, column=0)

    year_var = tk.StringVar(
        value=str(datetime.now().year)
    )

    tk.Entry(
        top,
        textvariable=year_var,
        width=10,
        font=("Segoe UI", 11)
    ).grid(
        row=1,
        column=0,
        padx=10
    )

    tk.Label(
        top,
        text="Staff",
        bg=BG,
        fg=TEXT,
        font=("Segoe UI", 10, "bold")
    ).grid(row=0, column=1)

    staff_combo = ttk.Combobox(
        top,
        state="readonly",
        width=25
    )

    staff_combo.grid(
        row=1,
        column=1,
        padx=10
    )

    mapping = {}

    load_staff_combo(
        staff_combo,
        mapping
    )

    table = tk.Frame(
        win,
        bg=WHITE
    )

    table.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=10
    )

    def show_year():

        for widget in table.winfo_children():
            widget.destroy()

        try:
            year = int(year_var.get())
        except:
            return

        real_staff_id = get_real_staff_id_from_combo(
            staff_combo,
            mapping
        )

        query = """
            SELECT
                a.date,
                a.status,
                s.name,
                a.staff_id
            FROM attendance a
            LEFT JOIN staff s
            ON a.staff_id = s.id
            WHERE substr(a.date,1,4) = ?
        """

        params = [str(year)]

        if real_staff_id is not None:

            query += " AND a.staff_id = ?"
            params.append(real_staff_id)

        query += " ORDER BY a.date ASC"

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            query,
            params
        )

        rows = cur.fetchall()

        _, _, real_to_display = get_staff_display_data()

        conn.close()

        headers = [
            "SR. NO.",
            "STAFF ID",
            "STAFF NAME",
            "DATE",
            "DAY",
            "STATUS"
        ]

        for col, header in enumerate(headers):

            tk.Label(
                table,
                text=header,
                bg=HEADER,
                fg=WHITE,
                font=("Segoe UI", 10, "bold"),
                padx=8,
                pady=10
            ).grid(
                row=0,
                column=col,
                sticky="nsew"
            )

        for row_no, row in enumerate(rows, start=1):

            attendance_date = row[0]
            status = row[1]
            staff_name = row[2] or ""
            actual_staff_id = row[3]

            display_id = real_to_display.get(
                actual_staff_id,
                ""
            )

            d = datetime.strptime(
                attendance_date,
                "%Y-%m-%d"
            )

            values = [
                row_no,
                display_id,
                staff_name,
                attendance_date,
                d.strftime("%A"),
                status
            ]

            for col, value in enumerate(values):

                tk.Label(
                    table,
                    text=value,
                    bg=WHITE if row_no % 2 else "#f8fafc",
                    fg=BLACK,
                    font=(
                        "Segoe UI",
                        10,
                        "bold" if col == 1 else "normal"
                    ),
                    padx=8,
                    pady=8
                ).grid(
                    row=row_no,
                    column=col,
                    sticky="nsew"
                )

        if not rows:

            tk.Label(
                table,
                text="No yearly record found.",
                bg=WHITE,
                fg=GRAY,
                font=("Segoe UI", 11)
            ).grid(
                row=1,
                column=0,
                columnspan=6,
                pady=30
            )

    tk.Button(
        top,
        text="SHOW YEARLY RECORD",
        bg=PURPLE,
        fg=WHITE,
        relief="flat",
        font=("Segoe UI", 10, "bold"),
        padx=15,
        pady=7,
        command=show_year
    ).grid(
        row=1,
        column=2,
        padx=15
    )

    show_year()


# ============================================================
# STAFF REPORT
# ============================================================

def open_staff_report():

    win = tk.Toplevel(root)

    win.title("Staff Attendance Report")
    win.geometry("1150x750")
    win.configure(bg=BG)

    tk.Label(
        win,
        text="STAFF ATTENDANCE REPORT",
        bg=HEADER,
        fg=WHITE,
        font=("Segoe UI", 18, "bold"),
        pady=15
    ).pack(fill="x")

    top = tk.Frame(
        win,
        bg=BG
    )

    top.pack(
        fill="x",
        padx=20,
        pady=15
    )

    tk.Label(
        top,
        text="Staff",
        bg=BG,
        fg=TEXT,
        font=("Segoe UI", 10, "bold")
    ).grid(row=0, column=0)

    staff_combo = ttk.Combobox(
        top,
        state="readonly",
        width=25
    )

    staff_combo.grid(
        row=1,
        column=0,
        padx=10
    )

    mapping = {}

    load_staff_combo(
        staff_combo,
        mapping
    )

    tk.Label(
        top,
        text="Year",
        bg=BG,
        fg=TEXT,
        font=("Segoe UI", 10, "bold")
    ).grid(row=0, column=1)

    year_var = tk.StringVar(
        value=str(datetime.now().year)
    )

    tk.Entry(
        top,
        textvariable=year_var,
        width=10,
        font=("Segoe UI", 11)
    ).grid(
        row=1,
        column=1,
        padx=10
    )

    report_area = tk.Frame(
        win,
        bg=WHITE
    )

    report_area.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=10
    )

    def generate_report():

        for widget in report_area.winfo_children():
            widget.destroy()

        real_staff_id = get_real_staff_id_from_combo(
            staff_combo,
            mapping
        )

        if real_staff_id is None:
            messagebox.showwarning(
                "Staff",
                "Please select staff.",
                parent=win
            )
            return

        try:
            year = int(year_var.get())
        except:

            messagebox.showwarning(
                "Year",
                "Enter valid year.",
                parent=win
            )

            return

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT name
            FROM staff
            WHERE id = ?
        """, (real_staff_id,))

        staff_row = cur.fetchone()

        cur.execute("""
            SELECT status, COUNT(*)
            FROM attendance
            WHERE staff_id = ?
            AND substr(date,1,4) = ?
            GROUP BY status
        """, (
            real_staff_id,
            str(year)
        ))

        summary = dict(cur.fetchall())

        cur.execute("""
            SELECT date, status
            FROM attendance
            WHERE staff_id = ?
            AND substr(date,1,4) = ?
            ORDER BY date ASC
        """, (
            real_staff_id,
            str(year)
        ))

        records = cur.fetchall()

        conn.close()

        staff_name = (
            staff_row[0]
            if staff_row
            else ""
        )

        _, _, real_to_display = get_staff_display_data()

        display_staff_id = real_to_display.get(
            real_staff_id,
            ""
        )

        info = tk.Frame(
            report_area,
            bg=WHITE
        )

        info.pack(
            fill="x",
            padx=10,
            pady=10
        )

        tk.Label(
            info,
            text=f"Staff ID : {display_staff_id}",
            bg=WHITE,
            fg=BLACK,
            font=("Segoe UI", 12, "bold")
        ).pack(
            side="left",
            padx=15
        )

        tk.Label(
            info,
            text=f"Staff Name : {staff_name}",
            bg=WHITE,
            fg=BLACK,
            font=("Segoe UI", 12, "bold")
        ).pack(
            side="left",
            padx=15
        )

        # Summary
        summary_frame = tk.Frame(
            report_area,
            bg=WHITE
        )

        summary_frame.pack(
            fill="x",
            padx=10,
            pady=10
        )

        summary_items = [
            ("Present", summary.get("Present", 0)),
            ("Absent", summary.get("Absent", 0)),
            ("CL", summary.get("CL", 0)),
            ("SL", summary.get("SL", 0))
        ]

        for title, count in summary_items:

            card = tk.Frame(
                summary_frame,
                bg="#f8fafc",
                bd=1,
                relief="solid"
            )

            card.pack(
                side="left",
                expand=True,
                fill="x",
                padx=5
            )

            tk.Label(
                card,
                text=title,
                bg="#f8fafc",
                fg=TEXT,
                font=("Segoe UI", 11, "bold")
            ).pack(
                pady=(10, 2)
            )

            tk.Label(
                card,
                text=str(count),
                bg="#f8fafc",
                fg=BLACK,
                font=("Segoe UI", 20, "bold")
            ).pack(
                pady=(0, 10)
            )

        # Monthly summary
        tk.Label(
            report_area,
            text="MONTHLY RECORD SUMMARY",
            bg=HEADER,
            fg=WHITE,
            font=("Segoe UI", 12, "bold"),
            pady=8
        ).pack(
            fill="x",
            padx=10,
            pady=(15, 0)
        )

        monthly_frame = tk.Frame(
            report_area,
            bg=WHITE
        )

        monthly_frame.pack(
            fill="x",
            padx=10
        )

        monthly_headers = [
            "MONTH",
            "PRESENT",
            "ABSENT",
            "CL",
            "SL"
        ]

        for col, h in enumerate(monthly_headers):

            tk.Label(
                monthly_frame,
                text=h,
                bg="#e2e8f0",
                fg=BLACK,
                font=("Segoe UI", 9, "bold"),
                pady=7
            ).grid(
                row=0,
                column=col,
                sticky="nsew"
            )

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                substr(date,6,2),
                status,
                COUNT(*)
            FROM attendance
            WHERE staff_id = ?
            AND substr(date,1,4) = ?
            GROUP BY substr(date,6,2), status
        """, (
            real_staff_id,
            str(year)
        ))

        monthly_data = {}

        for month, status, count in cur.fetchall():

            if month not in monthly_data:
                monthly_data[month] = {}

            monthly_data[month][status] = count

        conn.close()

        for r, month in enumerate(
            sorted(monthly_data.keys()),
            start=1
        ):

            try:
                month_name = datetime.strptime(
                    month,
                    "%m"
                ).strftime("%B")
            except:
                month_name = month

            vals = [
                month_name,
                monthly_data[month].get(
                    "Present", 0
                ),
                monthly_data[month].get(
                    "Absent", 0
                ),
                monthly_data[month].get(
                    "CL", 0
                ),
                monthly_data[month].get(
                    "SL", 0
                )
            ]

            for c, value in enumerate(vals):

                tk.Label(
                    monthly_frame,
                    text=value,
                    bg=WHITE,
                    fg=BLACK,
                    font=("Segoe UI", 9),
                    pady=6
                ).grid(
                    row=r,
                    column=c,
                    sticky="nsew"
                )

        # Daily record
        tk.Label(
            report_area,
            text="YEARLY DAILY RECORD",
            bg=HEADER,
            fg=WHITE,
            font=("Segoe UI", 12, "bold"),
            pady=8
        ).pack(
            fill="x",
            padx=10,
            pady=(15, 0)
        )

        daily_container = tk.Frame(
            report_area,
            bg=WHITE
        )

        daily_container.pack(
            fill="both",
            expand=True,
            padx=10
        )

        daily_canvas = tk.Canvas(
            daily_container,
            bg=WHITE,
            highlightthickness=0
        )

        daily_scroll = ttk.Scrollbar(
            daily_container,
            orient="vertical",
            command=daily_canvas.yview
        )

        daily_inner = tk.Frame(
            daily_canvas,
            bg=WHITE
        )

        daily_canvas.create_window(
            (0, 0),
            window=daily_inner,
            anchor="nw"
        )

        daily_canvas.configure(
            yscrollcommand=daily_scroll.set
        )

        daily_canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        daily_scroll.pack(
            side="right",
            fill="y"
        )

        headers = [
            "SR. NO.",
            "STAFF ID",
            "STAFF NAME",
            "DATE",
            "DAY",
            "STATUS"
        ]

        for c, h in enumerate(headers):

            tk.Label(
                daily_inner,
                text=h,
                bg=HEADER,
                fg=WHITE,
                font=("Segoe UI", 9, "bold"),
                pady=7
            ).grid(
                row=0,
                column=c,
                sticky="nsew"
            )

        for r, record in enumerate(
            records,
            start=1
        ):

            attendance_date = record[0]
            status = record[1]

            d = datetime.strptime(
                attendance_date,
                "%Y-%m-%d"
            )

            vals = [
                r,
                display_staff_id,
                staff_name,
                attendance_date,
                d.strftime("%A"),
                status
            ]

            for c, value in enumerate(vals):

                tk.Label(
                    daily_inner,
                    text=value,
                    bg=WHITE if r % 2 else "#f8fafc",
                    fg=BLACK,
                    font=(
                        "Segoe UI",
                        9,
                        "bold" if c == 1 else "normal"
                    ),
                    pady=6
                ).grid(
                    row=r,
                    column=c,
                    sticky="nsew"
                )

        daily_inner.update_idletasks()

        daily_canvas.configure(
            scrollregion=daily_canvas.bbox("all")
        )

    tk.Button(
        top,
        text="GENERATE REPORT",
        bg=BLUE,
        fg=WHITE,
        relief="flat",
        font=("Segoe UI", 10, "bold"),
        padx=20,
        pady=8,
        command=generate_report
    ).grid(
        row=1,
        column=2,
        padx=15
    )

# ============================================================
# MAIN ATTENDANCE WINDOW
# ============================================================

def open_attendance():

    global root
    global table_frame

    create_attendance_table()

    root = tk.Tk()

    root.title(
        "Staff Management System - Attendance"
    )

    root.geometry("1250x800")

    root.configure(
        bg=BG
    )

    root.minsize(
        1100,
        700
    )

    # ========================================================
    # SIDEBAR
    # ========================================================

    sidebar = tk.Frame(
        root,
        bg=SIDEBAR,
        width=220
    )

    sidebar.pack(
        side="left",
        fill="y"
    )

    sidebar.pack_propagate(False)

    tk.Label(
        sidebar,
        text="STAFF\nMANAGEMENT",
        bg=SIDEBAR,
        fg=WHITE,
        font=("Segoe UI", 18, "bold"),
        justify="left"
    ).pack(
        anchor="w",
        padx=20,
        pady=(25, 35)
    )

    buttons = [
        ("DASHBOARD", back_dashboard),
        ("ADD STAFF", go_add_staff),
        ("VIEW STAFF", go_view_staff),
        ("SEARCH STAFF", go_search_staff)
    ]

    for text, command in buttons:

        tk.Button(
            sidebar,
            text=text,
            bg=SIDEBAR,
            fg=WHITE,
            activebackground=BLUE,
            activeforeground=WHITE,
            relief="flat",
            anchor="w",
            padx=20,
            font=("Segoe UI", 10, "bold"),
            command=command
        ).pack(
            fill="x",
            pady=3
        )

    # ========================================================
    # MAIN AREA
    # ========================================================

    main = tk.Frame(
        root,
        bg=BG
    )

    main.pack(
        side="left",
        fill="both",
        expand=True
    )

    # Header
    header = tk.Frame(
        main,
        bg=HEADER,
        height=70
    )

    header.pack(
        fill="x"
    )

    tk.Label(
        header,
        text="ATTENDANCE MANAGEMENT",
        bg=HEADER,
        fg=WHITE,
        font=("Segoe UI", 20, "bold")
    ).pack(
        side="left",
        padx=25,
        pady=18
    )

    # ========================================================
    # DAILY ENTRY
    # ========================================================

    daily_card = tk.Frame(
        main,
        bg=WHITE,
        bd=1,
        relief="solid"
    )

    daily_card.pack(
        fill="x",
        padx=20,
        pady=15
    )

    tk.Label(
        daily_card,
        text="DAILY ATTENDANCE",
        bg=WHITE,
        fg=TEXT,
        font=("Segoe UI", 14, "bold")
    ).grid(
        row=0,
        column=0,
        columnspan=8,
        sticky="w",
        padx=15,
        pady=12
    )

    tk.Label(
        daily_card,
        text="Staff",
        bg=WHITE,
        fg=TEXT,
        font=("Segoe UI", 10, "bold")
    ).grid(
        row=1,
        column=0,
        padx=8,
        pady=8
    )

    staff_combo = ttk.Combobox(
        daily_card,
        state="readonly",
        width=25
    )

    staff_combo.grid(
        row=1,
        column=1,
        padx=8
    )

    staff_mapping = {}

    load_staff_combo(
        staff_combo,
        staff_mapping
    )

    tk.Label(
        daily_card,
        text="Date",
        bg=WHITE,
        fg=TEXT,
        font=("Segoe UI", 10, "bold")
    ).grid(
        row=1,
        column=2
    )

    date_entry = tk.Entry(
        daily_card,
        width=14,
        font=("Segoe UI", 10)
    )

    date_entry.insert(
        0,
        datetime.now().strftime("%Y-%m-%d")
    )

    date_entry.grid(
        row=1,
        column=3,
        padx=8
    )

    tk.Label(
        daily_card,
        text="Status",
        bg=WHITE,
        fg=TEXT,
        font=("Segoe UI", 10, "bold")
    ).grid(
        row=1,
        column=4
    )

    status_var = tk.StringVar(
        value="Present"
    )

    status_combo = ttk.Combobox(
        daily_card,
        textvariable=status_var,
        values=STATUS_LIST,
        state="readonly",
        width=12
    )

    status_combo.grid(
        row=1,
        column=5,
        padx=8
    )

    tk.Button(
        daily_card,
        text="MARK ATTENDANCE",
        bg=GREEN,
        fg=WHITE,
        relief="flat",
        font=("Segoe UI", 10, "bold"),
        padx=12,
        pady=8,
        command=lambda:
            mark_attendance(
                staff_combo,
                staff_mapping,
                date_entry,
                status_var
            )
    ).grid(
        row=1,
        column=6,
        padx=8
    )

    # ========================================================
    # RECORD BUTTONS
    # ========================================================

    button_frame = tk.Frame(
        main,
        bg=BG
    )

    button_frame.pack(
        fill="x",
        padx=20,
        pady=5
    )

    tk.Button(
        button_frame,
        text="MONTHLY ENTRY",
        bg=BLUE,
        fg=WHITE,
        relief="flat",
        font=("Segoe UI", 10, "bold"),
        padx=15,
        pady=9,
        command=open_monthly_entry
    ).pack(
        side="left",
        padx=5
    )

    tk.Button(
        button_frame,
        text="MONTHLY RECORD",
        bg=GREEN,
        fg=WHITE,
        relief="flat",
        font=("Segoe UI", 10, "bold"),
        padx=15,
        pady=9,
        command=open_monthly_record
    ).pack(
        side="left",
        padx=5
    )

    tk.Button(
        button_frame,
        text="YEARLY ENTRY",
        bg=PURPLE,
        fg=WHITE,
        relief="flat",
        font=("Segoe UI", 10, "bold"),
        padx=15,
        pady=9,
        command=open_yearly_entry
    ).pack(
        side="left",
        padx=5
    )

    tk.Button(
        button_frame,
        text="YEARLY RECORD",
        bg=ORANGE,
        fg=WHITE,
        relief="flat",
        font=("Segoe UI", 10, "bold"),
        padx=15,
        pady=9,
        command=open_yearly_record
    ).pack(
        side="left",
        padx=5
    )

    tk.Button(
        button_frame,
        text="STAFF REPORT",
        bg=HEADER,
        fg=WHITE,
        relief="flat",
        font=("Segoe UI", 10, "bold"),
        padx=15,
        pady=9,
        command=open_staff_report
    ).pack(
        side="left",
        padx=5
    )

    # ========================================================
    # SEARCH
    # ========================================================

    search_frame = tk.Frame(
        main,
        bg=BG
    )

    search_frame.pack(
        fill="x",
        padx=20,
        pady=8
    )

    tk.Label(
        search_frame,
        text="Search:",
        bg=BG,
        fg=TEXT,
        font=("Segoe UI", 10, "bold")
    ).pack(
        side="left",
        padx=5
    )

    search_entry = tk.Entry(
        search_frame,
        width=35,
        font=("Segoe UI", 10)
    )

    search_entry.pack(
        side="left",
        padx=5
    )

    tk.Button(
        search_frame,
        text="SEARCH",
        bg=BLUE,
        fg=WHITE,
        relief="flat",
        font=("Segoe UI", 9, "bold"),
        command=lambda:
            load_attendance(
                search_entry.get().strip()
            )
    ).pack(
        side="left",
        padx=5
    )

    tk.Button(
        search_frame,
        text="CLEAR",
        bg=GRAY,
        fg=WHITE,
        relief="flat",
        font=("Segoe UI", 9, "bold"),
        command=lambda: (
            search_entry.delete(0, tk.END),
            load_attendance()
        )
    ).pack(
        side="left",
        padx=5
    )

    # ========================================================
    # ATTENDANCE TABLE
    # ========================================================

    table_container = tk.Frame(
        main,
        bg=WHITE,
        bd=1,
        relief="solid"
    )

    table_container.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=(5, 20)
    )

    table_canvas = tk.Canvas(
        table_container,
        bg=WHITE,
        highlightthickness=0
    )

    table_scroll_y = ttk.Scrollbar(
        table_container,
        orient="vertical",
        command=table_canvas.yview
    )

    table_scroll_x = ttk.Scrollbar(
        table_container,
        orient="horizontal",
        command=table_canvas.xview
    )

    table_frame = tk.Frame(
        table_canvas,
        bg=WHITE
    )

    table_canvas.create_window(
        (0, 0),
        window=table_frame,
        anchor="nw"
    )

    table_canvas.configure(
        yscrollcommand=table_scroll_y.set,
        xscrollcommand=table_scroll_x.set
    )

    table_canvas.pack(
        side="left",
        fill="both",
        expand=True
    )

    table_scroll_y.pack(
        side="right",
        fill="y"
    )

    table_scroll_x.pack(
        side="bottom",
        fill="x"
    )

    def update_scroll():

        table_frame.update_idletasks()

        table_canvas.configure(
            scrollregion=table_canvas.bbox("all")
        )

    table_frame.bind(
        "<Configure>",
        lambda e: update_scroll()
    )

    # ========================================================
    # LOAD
    # ========================================================

    load_attendance()

    root.mainloop()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    open_attendance()