from typing import Any

from fastapi import status


def build_response(status_code: int, payload: Any, message: str) -> dict:
    return {"status_code": status_code, "payload": payload, "message": message}
