import streamlit as st

from yretain.webapp.coupons import display_coupons
from yretain.webapp.customer_activity import display_customers_activity
from yretain.webapp.customers import display_customers
from yretain.webapp.utils import authenticate_user
import requests
import json

# Set API endpoint and access key
UNSPLASH_ENDPOINT = "https://api.unsplash.com/photos/random"
# API keys
UNSPLASH_ACCESS_KEY = "vq4EoivATbOUwgtJGm2QEVEDH3VeBrSFU2rfKpSGXhw"
DEFAULT_IMAGE_URL = "https://images.unsplash.com/photo-1509822929063-6b6cfc9b42f2"


# Function to get a random image URL
def get_random_image_url():
    query_params = {
        "query": "technology",
        "orientation": "landscape",
        "client_id": UNSPLASH_ACCESS_KEY
    }
    response = requests.get(UNSPLASH_ENDPOINT, params=query_params)
    try:
        photo_data = json.loads(response.content)
        return photo_data["urls"]["regular"]
    except json.decoder.JSONDecodeError:
        return DEFAULT_IMAGE_URL


def main():
    # Print the photo URL
    st.set_page_config(page_title="Login Page", page_icon=":lock:")
    st.title("Welcome to the YRetain Login App")
    st.title("Please :blue[Login] :sunglasses:")
    bg_image_url = get_random_image_url()
    page_bg_img = f"""
                <style>
                [data-testid="stAppViewContainer"] > .main {{
                background-image: url("{bg_image_url}");
                background-size: cover;
                background-position: top left;
                background-attachment: local;
                background-color: rgba(255, 255, 255, 0.1) !important;
                }}
                .st-cn {{
                    background-color: rgba(255, 255, 255, 0.7) !important;
                    color: #333333 !important;
                }}              
                </style>
                """

    st.markdown(page_bg_img, unsafe_allow_html=True)

    # st.set_page_config(page_title="Awesome Login App", page_icon=":key:")

    # Check if the user is logged in
    logged_in = st.session_state.get("logged_in", False)

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        if "email" not in st.session_state:
            st.session_state.email = ""
        if "password" not in st.session_state:
            st.session_state.password = ""

        # Define the login form
        with st.container():
            st.session_state.email = st.text_input("Email", value=st.session_state.email)
            st.session_state.password = st.text_input("Password",
                                                      value=st.session_state.password,
                                                      type="password")

            if st.button("Login"):
                authenticated, headers = authenticate_user(st.session_state.email,
                                                           st.session_state.password)
                st.session_state.authenticated = authenticated
                st.session_state.headers = headers

                if st.session_state.authenticated:
                    st.success("Login successful!")
                else:
                    st.error("Login failed. Please check your credentials and try again.")

    if st.session_state.authenticated:
        st.title(f"Welcome, {st.session_state.email}!")
        logout_button = st.button("Logout")
        if logout_button:
            st.session_state["logged_in"] = False
            st.experimental_rerun()
            st.session_state.clear()
            st.success("Session cleared - Logged out successfully!")
            st.text("Please relogin")

        pages = {
            "Customer Management": display_customers,
            "Customer Activity Management": display_customers_activity,
            "Coupon Management": display_coupons,
        }

        if "page" not in st.session_state:
            st.session_state.page = "Customer Management"

        st.session_state.page = st.sidebar.radio("Select a page", tuple(pages.keys()),
                                                 index=list(pages.keys()).index(st.session_state.page))

        # Call the appropriate function to display the selected page
        pages[st.session_state.page](st.session_state.headers)


if __name__ == "__main__":
    main()
