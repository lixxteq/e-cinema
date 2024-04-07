from fastapi import HTTPException, status


class AuthorizationException(HTTPException):
    def __init__(self, detail="Authorization required"):
        self.status_code=status.HTTP_401_UNAUTHORIZED
        self.detail=detail
