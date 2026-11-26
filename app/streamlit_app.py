import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Smart Shopping List", page_icon="🛒", layout="centered")

st.title("🛒 Smart Shopping List")
st.markdown("Add items, track prices, and calculate your total easily.")

# File to store the shopping list
DATA_FILE = "data/shopping_list.csv"

# Load existing data
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=["Item", "Category", "Quantity", "Price", "Bought", "Date Added"])

# Sidebar - Add new item
st.sidebar.header("Add New Item")

with st.sidebar.form("add_item_form"):
    item = st.text_input("Item Name")
    category = st.selectbox("Category", ["Grocery", "Vegetables", "Fruits", "Dairy", "Snacks", "Household", "Other"])
    quantity = st.number_input("Quantity", min_value=1, value=1)
    price = st.number_input("Price (per item)", min_value=0.0, value=0.0, step=0.5)
    submitted = st.form_submit_button("Add Item")

    if submitted:
        if item.strip() == "":
            st.sidebar.warning("Please enter an item name.")
        else:
            new_row = {
                "Item": item.strip(),
                "Category": category,
                "Quantity": quantity,
                "Price": price,
                "Bought": False,
                "Date Added": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.sidebar.success(f"'{item}' added successfully!")
            st.rerun()

# Main area
if df.empty:
    st.info("Your shopping list is empty. Add items from the sidebar.")
else:
    st.subheader("Your Shopping List")

    # Calculate total
    df["Total"] = df["Quantity"] * df["Price"]
    total_cost = df[df["Bought"] == False]["Total"].sum()

    st.metric("Estimated Total (Not Bought Yet)", f"Rs. {total_cost:.2f}")

    # Show the list
    for index, row in df.iterrows():
        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])

        with col1:
            st.write(f"**{row['Item']}** ({row['Category']})")
            st.caption(f"Qty: {row['Quantity']} × Rs. {row['Price']:.2f}")

        with col2:
            st.write(f"Rs. {row['Total']:.2f}")

        with col3:
            bought = st.checkbox("Bought", value=row["Bought"], key=f"bought_{index}")
            if bought != row["Bought"]:
                df.at[index, "Bought"] = bought
                df.to_csv(DATA_FILE, index=False)
                st.rerun()

        with col4:
            if st.button("🗑️", key=f"delete_{index}"):
                df = df.drop(index).reset_index(drop=True)
                df.to_csv(DATA_FILE, index=False)
                st.rerun()

    st.divider()

    # Summary by category
    st.subheader("Summary by Category")
    summary = df.groupby("Category")["Total"].sum().reset_index()
    st.dataframe(summary, use_container_width=True, hide_index=True)

# Clear all button
if st.sidebar.button("Clear All Items", type="primary"):
    df = pd.DataFrame(columns=["Item", "Category", "Quantity", "Price", "Bought", "Date Added"])
    df.to_csv(DATA_FILE, index=False)
    st.rerun()