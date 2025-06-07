from crewai_tools import tool

@tool
def verify_otp(code: str, secret: str) -> bool:
    """
    Verify a time-based OTP code against the shared secret.
    Returns True if valid, False otherwise.
    """
    import time, hmac, hashlib
    interval = int(time.time()) // 30
    expected = hmac.new(secret.encode(), str(interval).encode(), hashlib.sha1).hexdigest()[:6]
    return hmac.compare_digest(expected, code)

my_tools = [verify_otp]
