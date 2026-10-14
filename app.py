import sqlite3
from datetime import date
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Staff Management System", page_icon="👥", layout="wide")
DB_PATH = "web_staff.db"

def conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    with conn() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS staff (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, email TEXT NOT NULL, phone TEXT NOT NULL,
            department TEXT NOT NULL, salary REAL NOT NULL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT, staff_id INTEGER NOT NULL,
            date TEXT NOT NULL, status TEXT NOT NULL,
            UNIQUE(staff_id,date), FOREIGN KEY(staff_id) REFERENCES staff(id))""")
        c.execute("""CREATE TABLE IF NOT EXISTS leave_application (
            id INTEGER PRIMARY KEY AUTOINCREMENT, staff_id INTEGER NOT NULL,
            from_date TEXT NOT NULL, to_date TEXT NOT NULL, reason TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending', applied_date TEXT NOT NULL,
            FOREIGN KEY(staff_id) REFERENCES staff(id))""")
        c.execute("""CREATE TABLE IF NOT EXISTS salary_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT, staff_id INTEGER NOT NULL,
            year INTEGER NOT NULL, month INTEGER NOT NULL, salary REAL NOT NULL,
            days_present INTEGER DEFAULT 0, notes TEXT DEFAULT '',
            UNIQUE(staff_id,year,month), FOREIGN KEY(staff_id) REFERENCES staff(id))""")

def query(sql, params=()):
    with conn() as c:
        return pd.read_sql_query(sql, c, params=params)

def execute(sql, params=()):
    with conn() as c:
        cur = c.execute(sql, params)
        return cur.lastrowid

init_db()
st.title("👥 Staff Management System")
st.caption("Web demo • Python + Streamlit + SQLite")
st.info("Demo version: it creates a separate web_staff.db database and does not import your original staff.db. Use fictional/sample data for public demos.")

pages = ["Dashboard", "Staff Management", "Attendance", "Leave Applications", "Salary Reports"]
page = st.sidebar.radio("Navigation", pages)

staff = query("SELECT id, name, email, phone, department, salary FROM staff ORDER BY id")
staff_names = {f"{r['id']} — {r['name']}": int(r['id']) for _, r in staff.iterrows()}

if page == "Dashboard":
    a,b,c,d = st.columns(4)
    a.metric("Total staff", len(staff))
    b.metric("Attendance entries", int(query("SELECT COUNT(*) n FROM attendance").iloc[0]["n"]))
    c.metric("Pending leaves", int(query("SELECT COUNT(*) n FROM leave_application WHERE status='Pending'").iloc[0]["n"]))
    d.metric("Salary records", int(query("SELECT COUNT(*) n FROM salary_records").iloc[0]["n"]))
    st.subheader("Staff overview")
    st.dataframe(staff, use_container_width=True, hide_index=True)
    st.markdown("Use the left menu to add staff, record attendance, process leave requests, and manage monthly salary records.")

elif page == "Staff Management":
    st.subheader("Add staff")
    with st.form("add_staff", clear_on_submit=True):
        x1,x2 = st.columns(2)
        name = x1.text_input("Full name *")
        email = x2.text_input("Email *")
        phone = x1.text_input("Phone *")
        department = x2.text_input("Department *")
        salary = st.number_input("Monthly salary (₹) *", min_value=0.0, step=500.0)
        submitted = st.form_submit_button("Add staff")
        if submitted:
            if not all([name.strip(), email.strip(), phone.strip(), department.strip()]):
                st.error("Please fill all required fields.")
            else:
                execute("INSERT INTO staff(name,email,phone,department,salary) VALUES(?,?,?,?,?)",
                        (name.strip(), email.strip(), phone.strip(), department.strip(), salary))
                st.success("Staff member added.")
                st.rerun()
    st.divider()
    st.subheader("Search and view staff")
    term = st.text_input("Search by name, email, phone, department or ID")
    data = query("""SELECT id,name,email,phone,department,salary FROM staff
                    WHERE CAST(id AS TEXT) LIKE ? OR name LIKE ? OR email LIKE ?
                    OR phone LIKE ? OR department LIKE ? ORDER BY id""",
                 tuple([f"%{term}%"]*5))
    st.dataframe(data, use_container_width=True, hide_index=True)
    if not data.empty:
        st.subheader("Update or delete staff")
        options = {f"{r['id']} — {r['name']}": int(r['id']) for _,r in data.iterrows()}
        selected = st.selectbox("Select staff member", list(options))
        sid = options[selected]
        row = data[data.id == sid].iloc[0]
        with st.form("edit_staff"):
            ename = st.text_input("Name", str(row["name"]))
            eemail = st.text_input("Email", str(row["email"]))
            ephone = st.text_input("Phone", str(row["phone"]))
            edept = st.text_input("Department", str(row["department"]))
            esalary = st.number_input("Salary (₹)", min_value=0.0, value=float(row["salary"]), step=500.0)
            c1,c2 = st.columns(2)
            save = c1.form_submit_button("Save changes")
            delete = c2.form_submit_button("Delete staff")
            if save:
                execute("UPDATE staff SET name=?,email=?,phone=?,department=?,salary=? WHERE id=?",
                        (ename,eemail,ephone,edept,esalary,sid))
                st.success("Staff updated.")
                st.rerun()
            if delete:
                execute("DELETE FROM attendance WHERE staff_id=?", (sid,))
                execute("DELETE FROM leave_application WHERE staff_id=?", (sid,))
                execute("DELETE FROM salary_records WHERE staff_id=?", (sid,))
                execute("DELETE FROM staff WHERE id=?", (sid,))
                st.success("Staff deleted.")
                st.rerun()

elif page == "Attendance":
    st.subheader("Record attendance")
    if staff.empty:
        st.warning("Add staff first.")
    else:
        with st.form("attendance_form"):
            chosen = st.selectbox("Staff member", list(staff_names))
            adate = st.date_input("Date", value=date.today())
            status = st.selectbox("Status", ["Present", "Absent", "CL", "SL"])
            save = st.form_submit_button("Save attendance")
            if save:
                try:
                    execute("INSERT INTO attendance(staff_id,date,status) VALUES(?,?,?)",
                            (staff_names[chosen], adate.isoformat(), status))
                    st.success("Attendance saved.")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("Attendance already exists for this staff member and date.")
    st.subheader("Attendance history")
    x1,x2 = st.columns(2)
    start = x1.date_input("From date", value=date(date.today().year,1,1), key="att_start")
    end = x2.date_input("To date", value=date.today(), key="att_end")
    records = query("""SELECT a.id, s.name, a.date, a.status FROM attendance a
                       JOIN staff s ON s.id=a.staff_id
                       WHERE a.date BETWEEN ? AND ? ORDER BY a.date DESC, s.name""",
                    (start.isoformat(), end.isoformat()))
    st.dataframe(records, use_container_width=True, hide_index=True)
    if not records.empty:
        st.download_button("Download attendance CSV", records.to_csv(index=False).encode("utf-8"),
                           "attendance_report.csv", "text/csv")

elif page == "Leave Applications":
    st.subheader("Apply for leave")
    if staff.empty:
        st.warning("Add staff first.")
    else:
        with st.form("leave_form", clear_on_submit=True):
            chosen = st.selectbox("Staff member", list(staff_names))
            c1,c2 = st.columns(2)
            fdate = c1.date_input("From date", value=date.today())
            tdate = c2.date_input("To date", value=date.today())
            reason = st.text_area("Reason")
            submit = st.form_submit_button("Submit leave application")
            if submit:
                if tdate < fdate:
                    st.error("To date cannot be before From date.")
                elif not reason.strip():
                    st.error("Please enter a reason.")
                else:
                    execute("""INSERT INTO leave_application
                               (staff_id,from_date,to_date,reason,status,applied_date)
                               VALUES(?,?,?,?,?,?)""",
                            (staff_names[chosen],fdate.isoformat(),tdate.isoformat(),reason.strip(),"Pending",date.today().isoformat()))
                    st.success("Leave application submitted.")
                    st.rerun()
    st.subheader("Applications and approval")
    leaves = query("""SELECT l.id, s.name, l.from_date, l.to_date, l.reason, l.status, l.applied_date
                      FROM leave_application l JOIN staff s ON s.id=l.staff_id ORDER BY l.id DESC""")
    st.dataframe(leaves, use_container_width=True, hide_index=True)
    if not leaves.empty:
        ids = {f"#{int(r['id'])} — {r['name']} ({r['status']})": int(r['id']) for _,r in leaves.iterrows()}
        selected_leave = st.selectbox("Choose application to update", list(ids))
        new_status = st.selectbox("New status", ["Pending","Approved","Rejected"])
        if st.button("Update leave status"):
            execute("UPDATE leave_application SET status=? WHERE id=?", (new_status, ids[selected_leave]))
            st.success("Leave status updated.")
            st.rerun()
        st.download_button("Download leave report CSV", leaves.to_csv(index=False).encode("utf-8"),
                           "leave_report.csv", "text/csv")

elif page == "Salary Reports":
    st.subheader("Create monthly salary record")
    if staff.empty:
        st.warning("Add staff first.")
    else:
        with st.form("salary_form"):
            chosen = st.selectbox("Staff member", list(staff_names))
            c1,c2 = st.columns(2)
            year = c1.number_input("Year", min_value=2020, max_value=2100, value=date.today().year, step=1)
            month = c2.selectbox("Month", list(range(1,13)), format_func=lambda m: date(2000,m,1).strftime("%B"))
            salary = st.number_input("Salary amount (₹)", min_value=0.0, step=500.0)
            days = st.number_input("Days present", min_value=0, max_value=31, value=0)
            notes = st.text_input("Notes")
            save = st.form_submit_button("Save monthly salary")
            if save:
                execute("""INSERT INTO salary_records(staff_id,year,month,salary,days_present,notes)
                           VALUES(?,?,?,?,?,?) ON CONFLICT(staff_id,year,month) DO UPDATE SET
                           salary=excluded.salary, days_present=excluded.days_present, notes=excluded.notes""",
                        (staff_names[chosen],int(year),int(month),salary,int(days),notes))
                st.success("Salary record saved.")
                st.rerun()
    st.subheader("Salary report")
    salaries = query("""SELECT sr.id, s.name, sr.year, sr.month, sr.salary, sr.days_present, sr.notes
                        FROM salary_records sr JOIN staff s ON s.id=sr.staff_id
                        ORDER BY sr.year DESC, sr.month DESC, s.name""")
    st.dataframe(salaries, use_container_width=True, hide_index=True)
    if not salaries.empty:
        st.metric("Total recorded salary", f"₹{salaries['salary'].sum():,.2f}")
        st.download_button("Download salary report CSV", salaries.to_csv(index=False).encode("utf-8"),
                           "salary_report.csv", "text/csv")

st.sidebar.divider()
st.sidebar.caption("For demo use only. Do not enter real employee personal or salary data on a public app.")
