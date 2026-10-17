"""Personal income-tax calculator (new and old regimes).

Slabs are modelled on FY 2025-26. For teaching only, not tax advice.
"""
import os
import re
from wsgiref.handlers import CGIHandler  # nosec B412

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from defusedxml import minidom

STANDARD_DEDUCTION_NEW = 75000
STANDARD_DEDUCTION_OLD = 50000
REBATE_LIMIT_NEW = 1200000
REBATE_LIMIT_OLD = 500000
LIMIT_80C = 150000
CESS = 0.04
INF = float("inf")

# (upper limit of slab, rate)
NEW_SLABS = [
    (400000, 0.0), (800000, 0.05), (1200000, 0.10), (1600000, 0.15),
    (2000000, 0.20), (2400000, 0.25), (INF, 0.30),
]
OLD_SLABS = [(250000, 0.0), (500000, 0.05), (1000000, 0.20), (INF, 0.30)]

PAN_PATTERN = re.compile(r"[A-Z]{5}[0-9]{4}[A-Z]")


def _load_pan_key():
    """Read the AES key from PAN_KEY_HEX, or make a throw-away one."""
    key_hex = os.environ.get("PAN_KEY_HEX")
    if key_hex:
        return bytes.fromhex(key_hex)
    return AESGCM.generate_key(bit_length=256)


PAN_KEY = _load_pan_key()


def _progressive_tax(taxable, slabs, exemption=0):
    """Tax each slice of income at its own slab rate (marginal rates)."""
    total = 0.0
    lower = 0
    for upper, rate in slabs:
        start = max(lower, exemption)
        portion = min(taxable, upper) - start
        if portion > 0:
            total += portion * rate
        lower = upper
    return total


def new_regime_tax(salary):
    """Tax payable under the new regime, including cess."""
    taxable = max(0, salary - STANDARD_DEDUCTION_NEW)
    tax = _progressive_tax(taxable, NEW_SLABS)
    if taxable <= REBATE_LIMIT_NEW:
        tax = 0
    else:
        tax = min(tax, taxable - REBATE_LIMIT_NEW)  # marginal relief
    return round(tax * (1 + CESS))


def basic_exemption(age):
    """Basic exemption limit for the old regime, by age."""
    if age >= 80:
        return 500000
    if age >= 60:
        return 300000
    return 250000


def old_regime_tax(salary, age, deductions):
    """Tax payable under the old regime, including cess."""
    taxable = salary - STANDARD_DEDUCTION_OLD
    for section, amount in deductions.items():
        if section == "80C":
            amount = min(amount, LIMIT_80C)
        taxable -= amount
    taxable = max(0, taxable)
    if taxable <= REBATE_LIMIT_OLD:
        return 0
    tax = _progressive_tax(taxable, OLD_SLABS, basic_exemption(age))
    return round(tax * (1 + CESS))


def better_regime(salary, age, deductions):
    """Return the regime ('new' or 'old') with the lower tax."""
    new_tax = new_regime_tax(salary)
    old_tax = old_regime_tax(salary, age, deductions)
    return "new" if new_tax <= old_tax else "old"


def is_valid_pan(pan):
    """True only if the whole string is a valid PAN (AAAAA9999A)."""
    return isinstance(pan, str) and PAN_PATTERN.fullmatch(pan) is not None


def encrypt_pan(pan):
    """Encrypt a PAN with AES-GCM and a fresh random nonce (hex output)."""
    if not is_valid_pan(pan):
        raise ValueError("Invalid PAN")
    nonce = os.urandom(12)
    cipher_text = AESGCM(PAN_KEY).encrypt(nonce, pan.encode(), None)
    return (nonce + cipher_text).hex()


def decrypt_pan(token):
    """Reverse encrypt_pan."""
    raw = bytes.fromhex(token)
    return AESGCM(PAN_KEY).decrypt(raw[:12], raw[12:], None).decode()


def signing_key():
    """Generate a 2048-bit RSA signing key."""
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


def _read_int(doc, tag):
    """Read an integer from the first <tag> element of a parsed XML doc."""
    nodes = doc.getElementsByTagName(tag)
    if not nodes or nodes[0].firstChild is None:
        raise ValueError(f"Form 16 is missing <{tag}>")
    return int(nodes[0].firstChild.data)


def parse_form16(xml_text):
    """Return (salary, tds) from Form-16 XML, parsed safely."""
    doc = minidom.parseString(xml_text)
    return _read_int(doc, "salary"), _read_int(doc, "tds")


def run_as_cgi(app):
    """Run a WSGI app as a CGI script."""
    os.environ.pop("HTTP_PROXY", None)  # httpoxy mitigation
    CGIHandler().run(app)  # nosec B412


def main():
    """Print a demo of every feature."""
    deductions = {"80C": 200000, "80D": 30000}
    print("New regime, salary 12,75,000:", new_regime_tax(1275000))
    print("New regime, salary 18,00,000:", new_regime_tax(1800000))
    print("Old regime, salary 18,00,000:",
          old_regime_tax(1800000, 35, deductions))
    print(f"Better regime: {better_regime(1800000, 35, deductions)}")
    print(f"Basic exemption at age 80: {basic_exemption(80)}")
    print("PAN 'ABCDE1234FXYZ' valid?", is_valid_pan("ABCDE1234FXYZ"))
    same = encrypt_pan("ABCDE1234F") == encrypt_pan("ABCDE1234F")
    print("Same PAN encrypts the same way twice?", same)
    print("Form 16:", parse_form16(
        "<form16><salary>1800000</salary><tds>150000</tds></form16>"))
    print(f"Signing key size: {signing_key().key_size}")


if __name__ == "__main__":
    main()
