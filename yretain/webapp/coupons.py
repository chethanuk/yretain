import streamlit as st
import requests

from yretain.webapp.utils import API_BASE_URL, get_access_token


def display_coupons(headers):
    st.title("Coupon Management")

    # Add a sidebar for navigation
    operation = st.sidebar.selectbox("Choose an operation", ["Create", "Read", "Update", "Delete"])
    bg_image_url = "https://images.unsplash.com/photo-1566997560041-002fd549180b?ixlib=rb-4.0.3&q=85&fm=jpg&crop=entropy&cs=srgb&dl=alberto-bigoni-tqoewekYKUQ-unsplash.jpg"
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
    print(f"Read Coupon headerz: {api_headers}")

    # Add input fields and submit buttons for each operation
    if operation == "Create":
        create_coupon(api_headers)
    elif operation == "Read":
        read_coupon(api_headers)
    elif operation == "Update":
        update_coupon(api_headers)
    elif operation == "Delete":
        delete_coupon(api_headers)


def create_coupon(headers):
    st.header("Create Coupon")

    code = st.text_input("Code", "")
    message = st.text_input("Message", "")
    expiry_days = st.number_input("Expiry Days", min_value=1)

    if st.button("Create Coupon"):
        # 4. Make a request to the FastAPI endpoint
        response = requests.post(
            f"{API_BASE_URL}/coupons",
            json={
                "code": code,
                "message": message,
                "expiry_days": expiry_days,
            },
            headers=headers
        )

        # 5. Display the response
        if response.status_code == 200:
            st.success("Coupon created successfully!")
            st.write(response.json())
        else:
            st.error(f"An error occurred while creating the coupon. \n"
                     f"Response: {response.json()}")


def read_coupon(headers):
    st.header("Read Coupon")
    code = st.text_input("Enter the Coupon Code", "")

    if st.button("Search Coupon"):
        # headers = {
        #     'accept': 'application/json',
        #     'Authorization': f'Bearer {get_access_token()}'
        # }
        # print(f"Read Coupon headerz: {headers}")

        response = requests.get(f"{API_BASE_URL}/coupons/{code}", headers=headers)

        st.write(f"Coupan Code: {code} details: ")

        if response.status_code == 200:
            coupon = response.json()
            st.write(coupon)
        elif response.status_code == 401:
            st.error("Unauthorized: Invalid access token provided. \n"
                     f"Response: {response.json()}")
        else:
            st.error(f"Error {response.status_code}: Failed to retrieve coupon {code}")


def update_coupon(headers):
    st.header("Update Coupon")
    code = st.text_input("Enter the Coupon Code", "")
    message = st.text_input("New Message", "")
    expiry_days = st.number_input("New Expiry Days", min_value=1, value=1, step=1)

    if st.button("Update Coupon"):
        response = requests.put(
            f"{API_BASE_URL}/coupons/{code}",
            json={
                "message": message,
                "expiry_days": expiry_days,
            },
            headers=headers
        )

        if response.status_code == 200:
            st.success("Coupon updated successfully!")
            st.write(response.json())
        else:
            st.error("An error occurred while updating the coupon.")


def delete_coupon(headers):
    st.header("Delete Coupon")
    code = st.text_input("Enter the Coupon Code", "")

    if st.button("Delete Coupon"):
        response = requests.delete(f"{API_BASE_URL}/coupons/{code}", headers=headers)

        if response.status_code == 200:
            st.success("Coupon deleted successfully!")
            st.write(response.json())
        else:
            st.error("An error occurred while updating the coupon.")
