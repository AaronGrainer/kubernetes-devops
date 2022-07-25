from datetime import datetime
from functools import wraps

from fastapi import Request


def construct_response(f):
    """Construct a JSON response for an endpoint's results."""

    @wraps(f)
    def wrap(request: Request, *args, **kwargs):
        results = f(request, *args, **kwargs)

        # Construct response
        response = {
            "method": request.method,
            "message": results["status_code"].phrase,
            "status_code": results["status_code"],
            "timestamp": datetime.now().isoformat(),
            "url": request.url._url,
        }

        # Add data
        if "data" in results:
            response["data"] = results["data"]

        return response

    return wrap


def filter_document(document):
    document.pop("_id", None)
    document.pop("created_at", None)
    document.pop("updated_at", None)

    return document
