import traceback


class ExceptionHandler:
    """
    Handles exceptions by providing useful information about the error.
    """

    def __init__(self, error: Exception):
        """
        Initialize the ExceptionHandler.

        Args:
            error (Exception): The exception object.
        """
        self._error = error
        self._type = type(error).__name__
        self._message = str(error)
        self._traceback = traceback.format_exc()

    def __str__(self) -> str:
        """
        Convert the ExceptionHandler to a string.

        Returns:
            str: The formatted error message.
        """
        return f"{self.type}: {self.message}"

    @property
    def error(self) -> Exception:
        """
        Returns the original exception object.
        """
        return self._error

    @property
    def type(self) -> str:
        """
        Returns the type of the exception.
        """
        return self._type

    @property
    def message(self) -> str:
        """
        Returns the error message.
        """
        return self._message

    @property
    def traceback(self) -> str:
        """
        Returns the traceback information.
        """
        return self._traceback

    def __html__(self) -> str:
        """
        Generate an HTML representation of the exception.

        Returns:
            str: HTML representation of the exception.
        """
        return f"""
    <html>
      <head>
        <title>{self._type}</title>
        <style type="text/css">
        {'''
          * {
            box-sizing: border-box;
            padding: 0;
            margin: 0;
          }

          body {
            background-color: #8B5CF6;
            font-family: 'Roboto', sans-serif;
            color: #E2E8F0;
            font-weight: 700;
            padding: 2.625rem;
          }

          h1 {
            font-size: 4rem;
            color: #FFF;
          }

          h2 {
            font-size: 2.25rem;
            margin-bottom: 2rem;
          }

          pre {
            font-size: 1.25rem;
            margin-bottom: 1rem;
          }
        '''}
        </style>
      </head>
      <body>
        <h1>{self._type}</h1>
        <h2>{self._message}</h2>
        <h1>Traceback</h1>
        <pre>{self._traceback}</pre>
      </body>
    </html>
    """
