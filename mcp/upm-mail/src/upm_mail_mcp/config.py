"""Load UPM mail MCP settings from the environment."""

import os
from collections.abc import Mapping
from dataclasses import dataclass

from upm_mail_mcp.errors import ConfigError

ENV_ADDRESS = "UPM_MAIL_ADDRESS"
ENV_PASSWORD = "UPM_MAIL_PASSWORD"

KIND_STUDENT = "alumnos"
KIND_STAFF = "personal"

STUDENT_DOMAIN = "alumnos.upm.es"
STAFF_DOMAIN = "upm.es"

IMAP_HOSTS = {
    KIND_STUDENT: "correo.alumnos.upm.es",
    KIND_STAFF: "correo.upm.es",
}
SMTP_HOST = "smtp.upm.es"
IMAP_SSL_PORT = 993
SMTP_STARTTLS_PORT = 587


@dataclass(frozen=True)
class Settings:
    """Runtime settings for the UPM mail MCP server."""

    address: str
    password: str
    kind: str

    @property
    def imap_host(self) -> str:
        """Return the IMAP host for the account kind."""
        return IMAP_HOSTS[self.kind]

    @property
    def imap_port(self) -> int:
        """Return the IMAP SSL port."""
        return IMAP_SSL_PORT

    @property
    def imap_username(self) -> str:
        """Return the IMAP login (local part of the address)."""
        return self.address.split("@", 1)[0]

    @property
    def smtp_host(self) -> str:
        """Return the SMTP host."""
        return SMTP_HOST

    @property
    def smtp_port(self) -> int:
        """Return the SMTP STARTTLS port."""
        return SMTP_STARTTLS_PORT


def infer_kind(address: str) -> str:
    """
    Infer student or staff kind from an email domain.

    Parameters
    ----------
    address
        Full UPM email address.

    Returns
    -------
    str
        ``alumnos`` or ``personal``.

    Raises
    ------
    ConfigError
        If the domain is not a UPM mail domain.
    """
    domain = address.rsplit("@", 1)[-1].lower()
    if domain == STUDENT_DOMAIN:
        return KIND_STUDENT
    if domain == STAFF_DOMAIN:
        return KIND_STAFF
    raise ConfigError(
        f"{ENV_ADDRESS} must use @{STUDENT_DOMAIN} or @{STAFF_DOMAIN}, got @{domain}."
    )


def load_settings(environ: Mapping[str, str] | None = None) -> Settings:
    """
    Load settings from environment variables.

    Parameters
    ----------
    environ
        Mapping of environment variables. Defaults to ``os.environ``.

    Returns
    -------
    Settings
        Parsed address, password and inferred account kind.

    Raises
    ------
    ConfigError
        If the address or password is missing, or the domain is unknown.
    """
    env = os.environ if environ is None else environ
    address = env.get(ENV_ADDRESS, "").strip()
    password = env.get(ENV_PASSWORD, "").strip()
    if not address:
        raise ConfigError(f"{ENV_ADDRESS} is required.")
    if address.count("@") != 1:
        raise ConfigError(f"{ENV_ADDRESS} must be a single email address.")
    local_part, domain = address.split("@", 1)
    if not local_part or not domain:
        raise ConfigError(f"{ENV_ADDRESS} must be a single email address.")
    if not password:
        raise ConfigError(f"{ENV_PASSWORD} is required.")
    normalized = f"{local_part}@{domain.lower()}"
    return Settings(address=normalized, password=password, kind=infer_kind(normalized))
