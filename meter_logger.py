import streamlit as st
import pandas as pd
from datetime import datetime, date
import os

# Constants
CSV_FILE = "readings.csv"
METERS = ["Ground Floor", "First Floor"]

# Load or initialize CSV
def load_data():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE, parse_dates=["Date"])
    else:
        df = pd.DataFrame(columns=["Date"] + METERS)
        df.to_csv(CSV_FILE, index=False)
        return df

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

# Streamlit config
st.set_page_config(page_title="Electricity Meter Logger", layout="centered")
st.title("⚡ Electricity Meter Logger")

# Input Section
with st.form("input_form", clear_on_submit=False):
    st.subheader("➕ Add New Reading")
    reading_date = st.date_input("Date", value=date.today())
    readings = {meter: st.number_input(f"{meter} Reading", min_value=0.0, format="%.2f") for meter in METERS}
    submitted = st.form_submit_button("Save Reading")

    if submitted:
        df = load_data()
        new_entry = {"Date": pd.to_datetime(reading_date)}
        new_entry.update(readings)
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
        df.sort_values("Date", inplace=True)
        save_data(df)
        st.success("Reading saved successfully!")

# View/Edit/Delete Section
st.subheader("📊 View/Edit Readings")
df = load_data()

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("From Date", df["Date"].min() if not df.empty else date.today())
with col2:
    end_date = st.date_input("To Date", df["Date"].max() if not df.empty else date.today())

filtered_df = df[(df["Date"] >= pd.to_datetime(start_date)) & (df["Date"] <= pd.to_datetime(end_date))]

if not filtered_df.empty:
    st.write("✏️ Edit/Delete Below")
    editable_df = st.data_editor(filtered_df, num_rows="dynamic", use_container_width=True)

    if st.button("💾 Save Changes"):
        df = df[~df["Date"].isin(filtered_df["Date"])]
        updated_df = pd.concat([df, editable_df], ignore_index=True).sort_values("Date")
        save_data(updated_df)
        st.success("Changes saved.")

    if st.button("🗑️ Delete Selected"):
        df = df[~df["Date"].isin(editable_df["Date"])]
        save_data(df)
        st.warning("Deleted selected entries.")
else:
    st.info("No readings found for the selected range.")

# Summary Table (Metrics as rows, meters as columns)
if not filtered_df.empty:
    st.subheader("📈 Summary (Rows = Metrics, Columns = Meters)")

    filtered_df.sort_values("Date", inplace=True)
    earliest = filtered_df.iloc[0]
    latest = filtered_df.iloc[-1]
    days = (latest["Date"] - earliest["Date"]).days or 1

    summary_data = {
        "Metric": ["Start Date", "End Date", "Total Units", "Average/Day", "31 Day Estimate"]
    }

    for meter in METERS:
        try:
            total = latest[meter] - earliest[meter]
            avg = total / days
            estimate = avg * 31
            summary_data[meter] = [
                str(earliest["Date"].date()),
                str(latest["Date"].date()),
                f"{total:.2f}",
                f"{avg:.2f}",
                f"{estimate:.2f}"
            ]
        except:
            summary_data[meter] = ["N/A"] * 5

    summary_df = pd.DataFrame(summary_data)
    st.table(summary_df)
