from typing import Optional


class CORSGenerator:
    def __init__(
        self,
        allow_origin: str = "*",
        allow_headers: str = "*",
        allow_methods: str = "*",
        allow_credentials: bool = True,
        expose_headers: Optional[str] = None,
        max_age: Optional[int] = None,
        content_security_policy: str = "default-src 'self'",
        custom_headers: dict = {},
    ) -> None:
        self.allow_origin = allow_origin
        self.allow_headers = allow_headers
        self.allow_methods = allow_methods
        self.allow_credentials = allow_credentials
        self.expose_headers = expose_headers
        self.max_age = max_age
        self.content_security_policy = content_security_policy

        self.custom_headers = custom_headers

    def generate_headers(self) -> dict:
        headers = {
            "X-XSS-Protection": "1; mode=block",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "SAMEORIGIN",
            "Referrer-Policy": "no-referrer",
            "Content-Security-Policy": self.content_security_policy,
            "Access-Control-Allow-Origin": self.allow_origin,
            "Access-Control-Allow-Headers": self.allow_headers,
            "Access-Control-Allow-Methods": self.allow_methods,
            "Access-Control-Allow-Credentials": str(self.allow_credentials).lower(),
        }

        if self.expose_headers:
            headers["Access-Control-Expose-Headers"] = self.expose_headers
        if self.max_age:
            headers["Access-Control-Max-Age"] = self.max_age

        headers.update(self.custom_headers)
        return headers
