"""
response_helpers.py
===================
Standardized API response wrapper.
"""

from typing import Any, Optional

def success_response(data: Any = None, message: str = "Success") -> dict:
    return {
        "success": True,
        "message": message,
        "data": data or {}
    }

def error_response(message: str, details: Optional[Any] = None) -> dict:
    resp = {
        "success": False,
        "message": message,
        "data": {}
    }
    if details:
        resp["details"] = details
    return resp
