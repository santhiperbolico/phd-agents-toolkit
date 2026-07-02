# Patrones Python — ejemplos del ecosistema ClaudIA / Plataformas

## Client de API externa

```python
from __future__ import annotations

from typing import Any, Mapping, Optional

from t2o_apis.reporting.reporting_client import ReportingAPIClient


class EmptyMessageList(Exception):
    """Se lanza cuando la búsqueda no encuentra mensajes."""

    pass


class GmailClient(ReportingAPIClient):
    """Cliente para leer informes adjuntos en Gmail."""

    def fetch_messages(
        self,
        filters: Mapping[str, Any],
        limit: Optional[int] = None,
    ) -> list[dict[str, Any]]:
        ...
```

## Datos inmutables (attrs)

Usar `frozen=True` para inmutabilidad:

```python
import attr


@attr.s(auto_attribs=True, frozen=True)
class MetadataFilters:
    """
    Campos por los que filtrar el mail.

    Parameters
    ----------
    subject : str
        Asunto del mensaje.
    """

    subject: str
    state: str | None = "unread"
    from_email: str | None = None
```

## Factory / getter

```python
def loader_factory(config: dict[str, Any]) -> BaseWriter:
    """Devuelve el writer según la clave output del ETL."""
    ...
```
