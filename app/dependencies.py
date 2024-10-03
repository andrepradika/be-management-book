from fastapi import Header, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os

bearer_scheme = HTTPBearer()

def get_bearer_token(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    token = os.getenv("BEARER_TOKEN")
    if credentials.credentials != token:
        raise HTTPException(status_code=403, detail="Invalid token")
    return credentials.credentials
