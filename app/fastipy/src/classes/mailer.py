import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from typing import Dict, List, Tuple, Union


def create_message(
    subject: str,
    body: str,
    from_email: str,
    to_email: Union[str, List[str]],
    cc: Union[str, List[str], None] = None,
    bcc: Union[str, List[str], None] = None,
    reply_to: Union[str, List[str], None] = None,
    headers: Dict[str, str] = None,
    attachments: List[str] = None,
    alternatives: List[Tuple[str, str]] = None,
) -> MIMEMultipart:
    message = MIMEMultipart()
    message["From"] = from_email
    message["To"] = to_email if isinstance(to_email, str) else ", ".join(to_email)
    message["Date"] = formatdate(localtime=True)
    message["Subject"] = subject

    if cc:
        message["Cc"] = cc if isinstance(cc, str) else ", ".join(cc)

    if bcc:
        message["Bcc"] = bcc if isinstance(bcc, str) else ", ".join(bcc)

    if reply_to:
        message["Reply-To"] = (
            reply_to if isinstance(reply_to, str) else ", ".join(reply_to)
        )

    if headers and isinstance(headers, dict):
        for header, value in headers.items():
            message.add_header(header, value)

    if alternatives:
        for content, mimetype in alternatives:
            message.attach(MIMEText(content, mimetype))

    if body and not alternatives:
        message.attach(MIMEText(body))

    if attachments:
        for attachment_path in attachments:
            with open(attachment_path, "rb") as attachment_file:
                attachment = MIMEBase("application", "octet-stream")
                attachment.set_payload(attachment_file.read())

            encoders.encode_base64(attachment)
            attachment.add_header(
                "Content-Disposition",
                f'attachment; filename="{attachment_path.split("/")[-1]}"',
            )
            message.attach(attachment)

    return message


class Mailer:
    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        auth_user: str,
        auth_password: str,
        ssl: bool = True,
        tls: bool = False,
        timeout: int = 10,
    ) -> None:
        self._smtp_host = smtp_host
        self._smtp_port = smtp_port
        self._auth_user = auth_user
        self._auth_password = auth_password
        self._timeout = timeout
        self._ssl = ssl
        self._tls = tls

    @property
    def host(self):
        return self._smtp_host

    @property
    def port(self):
        return self._smtp_port

    @property
    def ssl(self):
        return self._ssl

    @property
    def tls(self):
        return self._tls

    @property
    def timeout(self):
        return self._timeout

    def send_email(
        self, message: Union[MIMEMultipart, List[MIMEMultipart]], raise_exceptions=False
    ):
        try:
            if self.ssl:
                smtp_conn = smtplib.SMTP_SSL(self.host, self.port, timeout=self.timeout)
            elif self.tls:
                smtp_conn = smtplib.SMTP(self.host, self.port, timeout=self.timeout)
                smtp_conn.starttls()
            else:
                if raise_exceptions:
                    raise ValueError("Either SSL or TLS should be enabled.")

            smtp_conn.login(self._auth_user, self._auth_password)

            if not isinstance(message, list):
                message = [message]

            for message_data in message:
                smtp_conn.sendmail(
                    message_data["From"], message_data["To"], message_data.as_string()
                )

            smtp_conn.quit()
        except Exception as e:
            if raise_exceptions:
                raise e

    def send_emails(self, messages: List[MIMEMultipart], raise_exceptions=False):
        self.send_email(messages, raise_exceptions)
