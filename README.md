# Staff Management System — Web Demo

This is a Streamlit web adaptation starter based on the uploaded Tkinter project. It includes:
- Dashboard
- Staff management (add, search, update, delete)
- Attendance (Present, Absent, CL, SL; one entry per staff/date)
- Leave applications and status updates
- Monthly salary records and CSV reports

## Run locally
```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

## Deploy
Push `app.py`, `requirements.txt`, and this README to a GitHub repository. In Streamlit Community Cloud, create an app from that repository and choose `app.py` as the entry point.

## Important
This web adaptation uses a new `web_staff.db` file, not your original `staff.db`. It is a starter conversion of the core workflows; it does not copy the Tkinter screen design or existing PDF/Excel report-generation logic. Public hosting is not suitable for real staff personal/salary data without proper authentication and access controls. Use fictional demo records only.
