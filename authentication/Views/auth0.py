import requests
import jwt
from jwt import PyJWTError
from django.conf import settings
from datetime import datetime, timezone
# Fetch Auth0 JWKS (JSON Web Key Set) URL
JWKS_URL = f'{settings.AUTH0_DOMAIN}/.well-known/jwks.json'

def get_jwk_keys():
    """Fetch the JSON Web Key Set from Auth0 to validate the JWT"""
    try:
        response = requests.get(JWKS_URL)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise ValueError("Failed to fetch JWK keys from Auth0: " + str(e))

def get_public_key(kid):
    """Retrieve the public key from the JWK set"""
    jwks_data = get_jwk_keys()
    for key in jwks_data['keys']:
        if key['kid'] == kid:
            return key
    raise ValueError(f"Public key not found for kid: {kid}")

def validate_id_token(id_token):
    """Validate the ID token received from Auth0"""

    # Decode the token header to get the 'kid' (Key ID)
    try:
        unverified_header = jwt.get_unverified_header(id_token)
        if not unverified_header:
            raise ValueError("Unable to parse JWT header")
        kid = unverified_header.get('kid')
        if not kid:
            raise ValueError("Token header missing 'kid' field")
    except jwt.PyJWTError as e:
        raise ValueError(f"Error decoding token header: {str(e)}")

    # Get the public key corresponding to the 'kid'
    try:
        public_key_data = get_public_key(kid)
        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(public_key_data)
    except ValueError as e:
        raise ValueError(f"Error fetching public key: {str(e)}")

    # Validate the JWT using the public key
    try:
        decoded_token = jwt.decode(
            id_token,
            public_key,
            algorithms=["RS256"],
            audience=settings.AUTH0_CLIENT_ID,  # Verify audience
            issuer=f"{settings.AUTH0_DOMAIN}/",  # Verify issuer
        )
    except PyJWTError as e:
        raise ValueError(f"Token validation failed: {str(e)}")

    # Check the token's expiration time
    exp = decoded_token.get("exp")
    if exp and exp < datetime.now(timezone.utc).timestamp():
        raise ValueError("Token has expired")

    return decoded_token  # Return the decoded user data
