from fastapi import Request


def get_audit_metadata(
    request: Request,
) -> dict:

    return {
        "ip_address": (
            request.client.host
            if request.client
            else None
        ),
        "user_agent": request.headers.get(
            "user-agent"
        ),
    }