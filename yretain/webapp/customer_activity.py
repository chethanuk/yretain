import streamlit as st
import requests

from yretain.webapp import get_access_token, API_BASE_URL


def display_customers_activity(headers):
    st.title("Customer Activity Management")

    operation = st.sidebar.selectbox("Choose an operation", ["Create", "Read", "Update", "Delete"])
    bg_image_url = "https://images.unsplash.com/photo-1506377711776-dbdc2f3c20d9?ixlib=rb-4.0.3&q=85&fm=jpg&crop=entropy&cs=srgb&dl=becca-tapert-QofjUnxy9LY-unsplash.jpg"
    st.markdown(f"""
        <style>
            [data-testid="stAppViewContainer"] > .main {{
            background-image: url("{bg_image_url}");
        }}
        </style>
    """, unsafe_allow_html=True)

    api_headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {get_access_token()}'
    }

    if operation == "Create":
        create_customers_activity(api_headers)
    elif operation == "Read":
        read_customers_activity(api_headers)
    elif operation == "Update":
        update_customers_activity(api_headers)
    elif operation == "Delete":
        delete_customers_activity(api_headers)


def create_customers_activity(headers):
    st.header("Create Customer Activity")

    phone_number = st.text_input("Phone Number", "")

    if st.button("Create Customer Activity"):
        response = requests.post(
            f"{API_BASE_URL}/customers_activity",
            json={
                "phone_number": phone_number,
            },
            headers=headers
        )

        if response.status_code == 200:
            st.success("Customer activity created successfully!")
            st.write(response.json())
        else:
            st.error("An error occurred while creating the customer activity.")


def read_customers_activity(headers):
    st.header("Read Customer Activity")
    activity_id = st.text_input("Enter the Activity ID", "")

    if st.button("Search Customer Activity"):
        response = requests.get(f"{API_BASE_URL}/customers_activity/{activity_id}", headers=headers)

        if response.status_code == 200:
            activity = response.json()
            st.write(activity)
        else:
            st.error("Failed to retrieve customer activity.")


def update_customers_activity(headers):
    st.header("Update Customer Activity")
    activity_id = st.text_input("Enter the Activity ID", "")
    phone_number = st.text_input("New Phone Number", "")

    if st.button("Update Customer Activity"):
        response = requests.put(
            f"{API_BASE_URL}/customers_activity/{activity_id}",
            json={
                "phone_number": phone_number,
            },
            headers=headers
        )

        if response.status_code == 200:
            st.success("Customer activity updated successfully!")
            st.write(response.json())
        else:
            st.error("An error occurred while updating the customer activity.")


def delete_customers_activity(headers):
    st.header("Delete Customer Activity")
    activity_id = st.text_input("Enter the Activity ID", "")

    if st.button("Delete Customer Activity"):
        response = requests.delete(f"{API_BASE_URL}/customers_activity/{activity_id}", headers=headers)

        if response.status_code == 200:
            st.success("Customer activity deleted successfully!")
        else:
            st.error("An error occurred while deleting the customer activity.")
