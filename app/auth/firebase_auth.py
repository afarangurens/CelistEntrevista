from fastapi import FastAPI, HTTPException, status, Response, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import jwt
import json
import requests
from firebase_admin import auth, credentials, initialize_app
import os
from dotenv import load_dotenv


credential = credentials.Certificate('serviceAccountKey.json')
initialize_app(credential)

load_dotenv()
secret_key = os.getenv('SECRET_KEY')
if not secret_key:
    raise ValueError("No SECRET_KEY set for JWT encoding")

class UserCredentials(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    payload: str

def get_user_token(user_credentials: UserCredentials) -> str:
    """
    Authenticates a user with Firebase and returns a JWT token.

    Args:
        user_credentials (UserCredentials): User's email and password.

    Returns:
        str: JWT token.
    """
    try:
        payload = sign_in_with_email_and_password(user_credentials.email, user_credentials.password)
            
        token = jwt.encode(payload, secret_key, algorithm="HS256")
        return token
    
    except:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid credentials",
        )
    
def sign_in_with_email_and_password(email, password, return_secure_token=True):
    """
    Signs in a user with email and password using Firebase.

    Args:
        email (str): User's email.
        password (str): User's password.
        return_secure_token (bool): Whether to return a secure token.

    Returns:
        dict: Response from Firebase containing user data.
    """
    payload = json.dumps({"email":email, "password":password, "return_secure_token":return_secure_token})
    FIREBASE_WEB_API_KEY = 'AIzaSyAGkSKBSHehPeShJL7DNbM-yGi3MS8iOAw' 
    rest_api_url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"

    r = requests.post(rest_api_url,
                  params={"key": FIREBASE_WEB_API_KEY},
                  data=payload)
    return r.json()


bearer_scheme = HTTPBearer()

def verify_jwt_token(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> dict:
    """
    Verifies the JWT token sent in the request headers.

    Args:
        credentials (HTTPAuthorizationCredentials): Authorization credentials containing the JWT token.

    Returns:
        dict: Decoded user data from the JWT token.
    """
    try:
        decoded_token = jwt.decode(credentials.credentials, secret_key, algorithms=["HS256"])
        id_token = decoded_token["idToken"]
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
        
    except auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detrail="Invalid Token"
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something happened during validation."
        )