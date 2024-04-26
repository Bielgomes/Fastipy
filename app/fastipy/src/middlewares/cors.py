from typing import Dict, List, Optional, Union


class CORSGenerator:
    """Class to manage and generate CORS headers."""

    def __init__(
        self,
        allow_origins: Union[str, List[str]] = "*",
        allow_headers: Union[str, List[str]] = "*",
        allow_methods: Union[str, List[str]] = "*",
        allow_credentials: bool = True,
        expose_headers: Optional[Union[str, List[str]]] = None,
        max_age: Optional[int] = None,
        content_security_policys: Union[str, List[str]] = "default-src 'self'",
        custom_headers: Dict[str, Union[str, List[str]]] = {},
    ) -> None:
        """
        Initialize the CORS generator with default values.

        Args:
            allow_origins (Union[str, List[str]], optional): Allowed origins. Defaults to "*".
            allow_headers (Union[str, List[str]], optional): Allowed headers. Defaults to "*".
            allow_methods (Union[str, List[str]], optional): Allowed methods. Defaults to "*".
            allow_credentials (bool, optional): Allow credentials. Defaults to True.
            expose_headers (Optional[Union[str, List[str]]], optional): Expose headers. Defaults to None.
            max_age (Optional[int], optional): Max age. Defaults to None.
            content_security_policys (Union[str, List[str]], optional): Content security policies. Defaults to "default-src 'self'".
            custom_headers (Dict[str, Union[str, List[str]]], optional): Custom headers. Defaults to {}.
        """
        self.allow_origins = (
            allow_origins
            if isinstance(allow_origins, str)
            else "*" if "*" in allow_origins else ", ".join(allow_origins)
        )

        self.allow_headers = (
            allow_headers
            if isinstance(allow_headers, str)
            else "*" if "*" in allow_headers else ", ".join(allow_headers)
        )

        self.allow_methods = (
            allow_methods
            if isinstance(allow_methods, str)
            else "*" if "*" in allow_methods else ", ".join(allow_methods)
        )

        self.allow_credentials = str(allow_credentials).lower()
        if expose_headers:
            self.expose_headers = (
                expose_headers
                if isinstance(expose_headers, str)
                else "*" if "*" in expose_headers else ", ".join(expose_headers)
            )
        else:
            self.expose_headers = None

        self.max_age = max_age
        self.content_security_policys = (
            content_security_policys
            if isinstance(content_security_policys, str)
            else "; ".join(content_security_policys)
        )

        self.custom_headers = custom_headers

    def generate_headers(self) -> Dict[str, str]:
        """
        Generate CORS headers.

        Returns:
            dict: Generated CORS headers.
        """
        headers = {
            "X-XSS-Protection": "1; mode=block",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "SAMEORIGIN",
            "Referrer-Policy": "no-referrer",
            "Content-Security-Policy": self.content_security_policys,
            "Access-Control-Allow-Origin": self.allow_origins,
            "Access-Control-Allow-Headers": self.allow_headers,
            "Access-Control-Allow-Methods": self.allow_methods,
            "Access-Control-Allow-Credentials": self.allow_credentials,
        }

        if self.expose_headers:
            headers["Access-Control-Expose-Headers"] = self.expose_headers
        if self.max_age:
            headers["Access-Control-Max-Age"] = self.max_age

        for key, value in self.custom_headers.items():
            headers[key] = value if isinstance(value, str) else ", ".join(value)

        return headers
