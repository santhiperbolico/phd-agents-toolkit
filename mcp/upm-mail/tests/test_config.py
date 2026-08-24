"""Tests for UPM mail environment settings."""

import pytest

from upm_mail_mcp.config import (
    ENV_ADDRESS,
    ENV_PASSWORD,
    IMAP_HOSTS,
    IMAP_SSL_PORT,
    KIND_STAFF,
    KIND_STUDENT,
    SMTP_HOST,
    SMTP_STARTTLS_PORT,
    STAFF_DOMAIN,
    STUDENT_DOMAIN,
    infer_kind,
    load_settings,
)
from upm_mail_mcp.errors import ConfigError


@pytest.mark.parametrize(
    "address, kind",
    [
        (f"ada@{STUDENT_DOMAIN}", KIND_STUDENT),
        (f"ada@{STAFF_DOMAIN}", KIND_STAFF),
        (f"Ada.Lovelace@{STUDENT_DOMAIN.upper()}", KIND_STUDENT),
    ],
)
def test_infer_kind(address: str, kind: str) -> None:
    assert infer_kind(address) == kind


def test_infer_kind_rejects_unknown_domain() -> None:
    with pytest.raises(ConfigError, match="alumnos.upm.es"):
        infer_kind("ada@gmail.com")


def test_load_settings_student() -> None:
    settings = load_settings(
        {
            ENV_ADDRESS: f"  nombre.apellido@{STUDENT_DOMAIN} ",
            ENV_PASSWORD: " secret ",
        }
    )
    assert settings.kind == KIND_STUDENT
    assert settings.imap_host == IMAP_HOSTS[KIND_STUDENT]
    assert settings.imap_port == IMAP_SSL_PORT
    assert settings.imap_username == "nombre.apellido"
    assert settings.smtp_host == SMTP_HOST
    assert settings.smtp_port == SMTP_STARTTLS_PORT
    assert settings.password == "secret"


def test_load_settings_staff() -> None:
    settings = load_settings(
        {
            ENV_ADDRESS: f"nombre.apellido@{STAFF_DOMAIN}",
            ENV_PASSWORD: "secret",
        }
    )
    assert settings.kind == KIND_STAFF
    assert settings.imap_host == IMAP_HOSTS[KIND_STAFF]
    assert settings.imap_username == "nombre.apellido"


@pytest.mark.parametrize(
    "env",
    [
        {},
        {ENV_ADDRESS: f"ada@{STUDENT_DOMAIN}"},
        {ENV_PASSWORD: "secret"},
        {ENV_ADDRESS: "not-an-email", ENV_PASSWORD: "secret"},
        {ENV_ADDRESS: "@alumnos.upm.es", ENV_PASSWORD: "secret"},
        {ENV_ADDRESS: "ada@gmail.com", ENV_PASSWORD: "secret"},
        {ENV_ADDRESS: "ada@@alumnos.upm.es", ENV_PASSWORD: "secret"},
    ],
)
def test_load_settings_rejects_invalid_env(env: dict[str, str]) -> None:
    with pytest.raises(ConfigError):
        load_settings(env)
