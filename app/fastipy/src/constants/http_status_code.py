class Status:
    """
    Class containing HTTP status codes and methods for checking status categories.
    """

    HTTP_200_OK = 200
    HTTP_201_CREATED = 201
    HTTP_202_ACCEPTED = 202
    HTTP_204_NO_CONTENT = 204
    HTTP_301_MOVED_PERMANENTLY = 301
    HTTP_302_FOUND = 302
    HTTP_303_SEE_OTHER = 303
    HTTP_304_NOT_MODIFIED = 304
    HTTP_307_TEMPORARY_REDIRECT = 307
    HTTP_308_PERMANENT_REDIRECT = 308
    HTTP_400_BAD_REQUEST = 400
    HTTP_401_UNAUTHORIZED = 401
    HTTP_403_FORBIDDEN = 403
    HTTP_404_NOT_FOUND = 404
    HTTP_405_METHOD_NOT_ALLOWED = 405
    HTTP_409_CONFLICT = 409
    HTTP_410_GONE = 410
    HTTP_411_LENGTH_REQUIRED = 411
    HTTP_412_PRECONDITION_FAILED = 412
    HTTP_413_PAYLOAD_TOO_LARGE = 413
    HTTP_415_UNSUPPORTED_MEDIA_TYPE = 415
    HTTP_422_UNPROCESSABLE_ENTITY = 422
    HTTP_429_TOO_MANY_REQUESTS = 429
    HTTP_500_INTERNAL_SERVER_ERROR = 500
    HTTP_501_NOT_IMPLEMENTED = 501
    HTTP_502_BAD_GATEWAY = 502
    HTTP_503_SERVICE_UNAVAILABLE = 503
    HTTP_504_GATEWAY_TIMEOUT = 504

    @staticmethod
    def is_informational(status: int) -> bool:
        """
        Check if the status code is in the informational range (100-199).

        Args:
            status (int): The HTTP status code.

        Returns:
            bool: True if the status code is in the informational range, False otherwise.
        """
        return 100 <= status < 200

    @staticmethod
    def is_success(status: int) -> bool:
        """
        Check if the status code is in the success range (200-299).

        Args:
            status (int): The HTTP status code.

        Returns:
            bool: True if the status code is in the success range, False otherwise.
        """
        return 200 <= status < 300

    @staticmethod
    def is_redirect(status: int) -> bool:
        """
        Check if the status code is in the redirection range (300-399).

        Args:
            status (int): The HTTP status code.

        Returns:
            bool: True if the status code is in the redirection range, False otherwise.
        """
        return 300 <= status < 400

    @staticmethod
    def is_client_error(status: int) -> bool:
        """
        Check if the status code is in the client error range (400-499).

        Args:
            status (int): The HTTP status code.

        Returns:
            bool: True if the status code is in the client error range, False otherwise.
        """
        return 400 <= status < 500

    @staticmethod
    def is_server_error(status: int) -> bool:
        """
        Check if the status code is in the server error range (500-599).

        Args:
            status (int): The HTTP status code.

        Returns:
            bool: True if the status code is in the server error range, False otherwise.
        """
        return 500 <= status < 600
