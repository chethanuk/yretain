import requests

# FastAPI endpoint URL
# API_BASE_URL = "http://127.0.0.1:8001"
API_BASE_URL = "http://scp-backend.eba-khhz9ncy.us-east-1.elasticbeanstalk.com"

def get_access_token(url=f'{API_BASE_URL}/auth/jwt/login',
                     username='vishwas1@example.com',
                     password='vishwas1'):
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'username': username,
        'password': password
    }

    response = requests.post(url, headers=headers, data=data)

    # Check if the response contains the access token
    access_token = response.json().get('access_token')

    if access_token:
        return access_token
    else:
        raise ValueError("Authentication failed. Please check your credentials and try again.")


def authenticate_user(email, password, return_header=True):
    access_token = get_access_token(username=email,
                                    password=password)
    # print(f"Access token: {access_token}")
    if return_header:
        return (True, {
            'Authorizaion': f'Bearer {access_token}',
            'accept': 'application/json'
        })
    else:
        return (False, None)
