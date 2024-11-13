import requests

def exchange_authorization_code(token_uri, client_id, client_secret, redirect_uri, auth_code, code_verifier):
    """Exchange authorization code for access tokens."""
    # Prepare the data for token exchange
    data = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'client_secret': client_secret,
        'code': auth_code,
        'redirect_uri': redirect_uri,
        'code_verifier': code_verifier,
    }
    print(data, ' is the data going through')
    # Make the request to exchange the authorization code for tokens
    response = requests.post(token_uri, data=data)
    
    if response.status_code == 200:
        tokens = response.json()
        print("Access Token:", tokens.get("access_token"))
        return tokens
    else:
        print("Error exchanging tokens:", response.json())
        return None

if __name__ == "__main__":
    # Define your OAuth configuration
    TOKEN_URI = "https://dev-0biozzwskqs6o65f.us.auth0.com/oauth/token"  # Replace with your Auth0 token endpoint
    CLIENT_ID = "HM0PdW9MjGEtDTUAOMJo8QsCUT5PThdz"  # Your client ID
    CLIENT_SECRET = "xgnUcPBtoVvt6NoLlh8zeSmwRqRQZX1aCUkr1zklEoil93fiXlzhfQ9fgutypts9"  # Your client secret
    REDIRECT_URI = "http://localhost:3000/callback"  # Your redirect URI
    
    # Input code verifier, code challenge, and authorization code from user
    code_verifier = input("Enter the code verifier: ")
    auth_code = input("Enter the authorization code received: ")

    # Authenticate user and exchange authorization code for tokens
    tokens = exchange_authorization_code(TOKEN_URI, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, auth_code, code_verifier)