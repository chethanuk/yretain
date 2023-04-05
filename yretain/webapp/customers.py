import streamlit as st
import requests

from yretain.webapp import get_access_token, API_BASE_URL


def display_customers(headers):
    st.title("Customer Management")

    operation = st.sidebar.selectbox("Choose an operation", ["Create", "Read", "Update", "Delete"])
    bg_image_url = "https://images.unsplash.com/photo-1454923634634-bd1614719a7b?ixlib=rb-4.0.3&q=85&fm=jpg&crop=entropy&cs=srgb&dl=timon-studler-ABGaVhJxwDQ-unsplash.jpg"
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
        create_customer(api_headers)
    elif operation == "Read":
        read_customer(api_headers)
    elif operation == "Update":
        update_customer(api_headers)
    elif operation == "Delete":
        delete_customer(api_headers)


def create_customer(headers):
    st.header("Create Customer")

    phone_number = st.text_input("Phone Number", "")
    name = st.text_input("Name", "")
    email = st.text_input("Email", "")
    city = st.text_input("City", "")

    if st.button("Create Customer"):
        response = requests.post(
            f"{API_BASE_URL}/customers",
            json={
                "phone_number": phone_number,
                "name": name,
                "email": email,
                "city": city,
            },
            headers=headers
        )

        if response.status_code == 200:
            st.success("Customer created successfully!")
            st.write(response.json())
        else:
            st.error("An error occurred while creating the customer.")


def read_customer(headers):
    st.header("Read Customer")
    phone_number = st.text_input("Enter the Customer's Phone Number", "")

    if st.button("Search Customer"):
        response = requests.get(f"{API_BASE_URL}/customers/{phone_number}", headers=headers)

        if response.status_code == 200:
            customer = response.json()
            st.write(customer)
        else:
            st.error("Failed to retrieve customer.")


def update_customer(headers):
    st.header("Update Customer")
    phone_number = st.text_input("Enter the Customer's Phone Number", "")
    name = st.text_input("New Name", "")
    email = st.text_input("New Email", "")
    city = st.text_input("New City", "")

    if st.button("Update Customer"):
        response = requests.put(
            f"{API_BASE_URL}/customers/{phone_number}",
            json={
                "name": name,
                "email": email,
                "city": city,
            },
            headers=headers
        )

        if response.status_code == 200:
            st.success("Customer updated successfully!")
            st.write(response.json())
        else:
            st.error("An error occurred while updating the customer.")


def delete_customer(headers):
    st.header("Delete Customer")
    phone_number = st.text_input("Enter the Customer's Phone Number", "")

    if st.button("Delete Customer"):
        response = requests.delete(f"{API_BASE_URL}/customers/{phone_number}", headers=headers)

        if response.status_code == 200:
            st.success("Customer deleted successfully!")
        else:
            st.error("An error occurred while deleting the customer.")
