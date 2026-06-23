"""Generate VAPID keys for web push. Run: venv\\Scripts\\python.exe scripts\\generate_vapid.py"""
from py_vapid import Vapid01, b64urlencode
from cryptography.hazmat.primitives import serialization

v = Vapid01()
v.generate_keys()
pub = v.public_key.public_bytes(
    serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint
)
priv = v.private_key.private_bytes(
    serialization.Encoding.DER,
    serialization.PrivateFormat.PKCS8,
    serialization.NoEncryption(),
)
print("Add to backend/.env:")
print(f"VAPID_PUBLIC={b64urlencode(pub)}")
print(f"VAPID_PRIVATE={b64urlencode(priv)}")
print()
print("Add to frontend/.env and .env.production.local:")
print(f"REACT_APP_VAPID_PUBLIC={b64urlencode(pub)}")