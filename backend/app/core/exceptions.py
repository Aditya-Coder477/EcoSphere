"""
exceptions.py
=============
Custom exception hierarchy for the backend API.
"""

from fastapi import HTTPException

class BaseAPIException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class ResourceNotFoundError(BaseAPIException):
    def __init__(self, resource: str):
        super().__init__(f"{resource} not found", status_code=404)

class ValidationException(BaseAPIException):
    def __init__(self, message: str):
        super().__init__(message, status_code=422)

class ServiceIntegrationError(BaseAPIException):
    def __init__(self, service: str, details: str):
        super().__init__(f"Error integrating with {service}: {details}", status_code=502)
