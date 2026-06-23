"""Shared helpers for SSC backend integration tests."""
import requests


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def make_mutual_contacts(api: str, token_from: str, token_to: str, username_to: str) -> None:
    """From-user sends a friend request; to-user accepts (bidirectional contacts)."""
    r = requests.post(
        f"{api}/contacts/request",
        json={"username": username_to},
        headers=auth_headers(token_from),
    )
    assert r.status_code == 200, r.text

    r2 = requests.get(f"{api}/contacts/requests", headers=auth_headers(token_to))
    assert r2.status_code == 200, r2.text
    reqs = r2.json()
    assert reqs, f"No pending requests for acceptor (target={username_to})"
    req_id = reqs[-1]["request_id"]

    r3 = requests.post(
        f"{api}/contacts/requests/accept",
        json={"request_id": req_id},
        headers=auth_headers(token_to),
    )
    assert r3.status_code == 200, r3.text