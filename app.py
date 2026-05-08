import streamlit as st
import pandas as pd
import json
import os
from datetime import date
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Expense Tracker", page_icon="💰", layout="wide")

DATA_FILE = "expenses.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# ── Init session state ──
if "expenses" not in st.session_state:
    st.session_state.expenses = load_data()

# ── Header ──
st.title("💰 Expense Tracker")
st.caption("Track, visualize, and manage your daily expenses")

# ── Add Expense Form ──
with st.expander("➕ Add New Expense", expanded=True):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        exp_date = st.date_input("Date", value=date.today())
    with col2:
        category = st.selectbox("Category", [
            "🍔 Food", "🚗 Transport", "🏠 Housing",
            "🎉 Entertainment", "🏥 Health", "🛍️ Shopping", "📦 Other"
        ])
    with col3:
        amount = st.number_input("Amount (₹)", min_value=0.0, step=10.0, format="%.2f")
    with col4:
        description = st.text_input("Description", placeholder="e.g. Lunch at cafe")

    if st.button("Add Expense", use_container_width=True):
        if amount > 0 and description:
            st.session_state.expenses.append({
                "date": str(exp_date),
                "category": category,
                "amount": amount,
                "description": description
            })
            save_data(st.session_state.expenses)
            st.success("✅ Expense added!")
            st.rerun()
        else:
            st.warning("Please fill in amount and description.")

# ── No data guard ──
if not st.session_state.expenses:
    st.info("No expenses yet. Add your first one above!")
    st.stop()

# ── Build DataFrame ──
df = pd.DataFrame(st.session_state.expenses)
df["date"] = pd.to_datetime(df["date"])
df["amount"] = df["amount"].astype(float)

# ── Summary Cards ──
st.markdown("---")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Spent", f"₹{df['amount'].sum():,.2f}")
c2.metric("This Month", f"₹{df[df['date'].dt.month == date.today().month]['amount'].sum():,.2f}")
c3.metric("Avg per Day", f"₹{df.groupby('date')['amount'].sum().mean():,.2f}")
c4.metric("Transactions", len(df))

# ── Charts ──
st.markdown("---")
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Spending by Category")
    cat_df = df.groupby("category")["amount"].sum().reset_index()
    fig = px.pie(cat_df, values="amount", names="category", hole=0.4)
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10), height=300)
    st.plotly_chart(fig, use_container_width=True)

with col_b:
    st.subheader("Daily Spending Trend")
    daily = df.groupby("date")["amount"].sum().reset_index()
    fig2 = px.bar(daily, x="date", y="amount", color_discrete_sequence=["#4F8EF7"])
    fig2.update_layout(xaxis_title="", yaxis_title="Amount (₹)",
                       margin=dict(t=10, b=10, l=10, r=10), height=300)
    st.plotly_chart(fig2, use_container_width=True)

# ── Expense Table ──
st.markdown("---")
st.subheader("📋 All Expenses")

# Filter
filter_cat = st.multiselect("Filter by Category", df["category"].unique(), default=list(df["category"].unique()))
filtered = df[df["category"].isin(filter_cat)].sort_values("date", ascending=False)

display_df = filtered.copy()
display_df["date"] = display_df["date"].dt.strftime("%d %b %Y")
display_df["amount"] = display_df["amount"].apply(lambda x: f"₹{x:,.2f}")
display_df.columns = ["Date", "Category", "Amount", "Description"]

st.dataframe(display_df, use_container_width=True, hide_index=True)

# ── Delete All ──
st.markdown("---")
if st.button("🗑️ Clear All Expenses", type="secondary"):
    st.session_state.expenses = []
    save_data([])
    st.rerun()

st.caption("Expense Tracker | Deployed on Streamlit Cloud")