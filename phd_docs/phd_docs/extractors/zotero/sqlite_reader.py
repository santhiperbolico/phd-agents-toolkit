"""Read-only access to the local Zotero SQLite database."""

import sqlite3
from dataclasses import dataclass
from pathlib import Path

STORAGE_PREFIX = "storage:"
ATTACHMENTS_PREFIX = "attachments:"


@dataclass(frozen=True)
class ZoteroPdfRecord:
    """One PDF attachment linked to a bibliographic item."""

    parent_item_id: int
    parent_key: str
    attachment_item_id: int
    attachment_key: str
    attachment_path: str
    title: str
    creators: str
    year: str
    abstract: str
    doi: str
    tags: tuple[str, ...]


@dataclass(frozen=True)
class ZoteroNote:
    """A user note attached to a bibliographic item."""

    text: str


@dataclass(frozen=True)
class ZoteroAnnotation:
    """A PDF highlight or annotation."""

    text: str
    comment: str
    page_label: str


def open_readonly_database(db_path: Path) -> sqlite3.Connection:
    """
    Open the Zotero database in read-only mode.

    Parameters
    ----------
    db_path : Path
        Path to ``zotero.sqlite``.

    Returns
    -------
    sqlite3.Connection
        Read-only connection.
    """
    uri = f"file:{db_path.as_posix()}?mode=ro"
    return sqlite3.connect(uri, uri=True)


def resolve_pdf_path(
    data_dir: Path,
    attachment_key: str,
    attachment_path: str,
    *,
    linked_attachment_base: Path | None = None,
) -> Path | None:
    """
    Resolve a Zotero attachment path to an absolute filesystem path.

    Parameters
    ----------
    data_dir : Path
        Zotero data directory containing ``storage/``.
    attachment_key : str
        Attachment item key used for stored files.
    attachment_path : str
        Value from ``itemAttachments.path``.
    linked_attachment_base : Path, optional
        Base directory for linked attachments.

    Returns
    -------
    Path or None
        Absolute path when the file exists, otherwise ``None``.
    """
    if attachment_path.startswith(STORAGE_PREFIX):
        relative_name = attachment_path[len(STORAGE_PREFIX) :]
        candidate = data_dir / "storage" / attachment_key / relative_name
        return candidate if candidate.is_file() else None

    if attachment_path.startswith(ATTACHMENTS_PREFIX) and linked_attachment_base is not None:
        relative_name = attachment_path[len(ATTACHMENTS_PREFIX) :]
        candidate = linked_attachment_base / relative_name
        return candidate if candidate.is_file() else None

    return None


def iter_pdf_records(
    db_path: Path,
    *,
    exclude_tags: frozenset[str] | None = None,
) -> list[ZoteroPdfRecord]:
    """
    List PDF attachments with bibliographic metadata.

    Parameters
    ----------
    db_path : Path
        Path to ``zotero.sqlite``.
    exclude_tags : frozenset[str], optional
        Skip parent items that contain any of these tag names.

    Returns
    -------
    list[ZoteroPdfRecord]
        PDF records sorted by parent key.
    """
    connection = open_readonly_database(db_path)
    connection.row_factory = sqlite3.Row
    try:
        rows = connection.execute(
            """
            SELECT
                parent.itemID AS parent_item_id,
                parent.key AS parent_key,
                attachment.itemID AS attachment_item_id,
                attachment.key AS attachment_key,
                ia.path AS attachment_path
            FROM itemAttachments ia
            JOIN items attachment ON attachment.itemID = ia.itemID
            JOIN items parent ON parent.itemID = ia.parentItemID
            WHERE ia.path IS NOT NULL
              AND (
                ia.contentType = 'application/pdf'
                OR ia.path LIKE '%.pdf'
              )
            ORDER BY parent.key, attachment.key
            """
        ).fetchall()
    finally:
        connection.close()

    records: list[ZoteroPdfRecord] = []
    for row in rows:
        parent_item_id = int(row["parent_item_id"])
        tags = _fetch_tags(db_path, parent_item_id)
        tag_names = {tag.lower() for tag in tags}
        if exclude_tags and tag_names.intersection(exclude_tags):
            continue
        records.append(
            ZoteroPdfRecord(
                parent_item_id=parent_item_id,
                parent_key=str(row["parent_key"]),
                attachment_item_id=int(row["attachment_item_id"]),
                attachment_key=str(row["attachment_key"]),
                attachment_path=str(row["attachment_path"]),
                title=_fetch_field(db_path, parent_item_id, "title"),
                creators=_fetch_creators(db_path, parent_item_id),
                year=_fetch_field(db_path, parent_item_id, "date"),
                abstract=_fetch_field(db_path, parent_item_id, "abstractNote"),
                doi=_fetch_field(db_path, parent_item_id, "DOI"),
                tags=tags,
            )
        )
    return records


def fetch_notes(db_path: Path, parent_item_id: int) -> list[ZoteroNote]:
    """
    Return note texts linked to a bibliographic item.

    Parameters
    ----------
    db_path : Path
        Path to ``zotero.sqlite``.
    parent_item_id : int
        Parent bibliographic item identifier.

    Returns
    -------
    list[ZoteroNote]
        Notes attached to the item.
    """
    connection = open_readonly_database(db_path)
    try:
        rows = connection.execute(
            """
            SELECT title, note
            FROM itemNotes
            WHERE parentItemID = ?
            ORDER BY itemID
            """,
            (parent_item_id,),
        ).fetchall()
    finally:
        connection.close()

    notes: list[ZoteroNote] = []
    for title, body in rows:
        text = _format_note_text(str(title or ""), str(body or ""))
        if text.strip():
            notes.append(ZoteroNote(text=text.strip()))
    return notes


def fetch_annotations(db_path: Path, attachment_item_id: int) -> list[ZoteroAnnotation]:
    """
    Return PDF annotations for one attachment item.

    Parameters
    ----------
    db_path : Path
        Path to ``zotero.sqlite``.
    attachment_item_id : int
        Attachment item identifier.

    Returns
    -------
    list[ZoteroAnnotation]
        Highlights and comments stored in Zotero.
    """
    connection = open_readonly_database(db_path)
    connection.row_factory = sqlite3.Row
    try:
        rows = connection.execute(
            """
            SELECT text, comment, pageLabel
            FROM itemAnnotations
            WHERE parentItemID = ?
            ORDER BY sortIndex
            """,
            (attachment_item_id,),
        ).fetchall()
    finally:
        connection.close()

    annotations: list[ZoteroAnnotation] = []
    for row in rows:
        text = str(row["text"] or "").strip()
        comment = str(row["comment"] or "").strip()
        page_label = str(row["pageLabel"] or "").strip()
        if text or comment:
            annotations.append(ZoteroAnnotation(text=text, comment=comment, page_label=page_label))
    return annotations


def build_document_path(parent_key: str) -> str:
    """Return the stable document path used in the sync manifest."""
    return f"zotero://item/{parent_key}"


def _metadata_section(record: ZoteroPdfRecord, include_parts: frozenset[str]) -> str:
    if "metadata" not in include_parts and "abstract" not in include_parts:
        return ""
    header_lines = [f"Title: {record.title or record.parent_key}"]
    if record.creators:
        header_lines.append(f"Authors: {record.creators}")
    if record.year:
        header_lines.append(f"Year: {record.year}")
    if record.doi:
        header_lines.append(f"DOI: {record.doi}")
    if record.tags:
        header_lines.append(f"Tags: {', '.join(record.tags)}")
    return "\n".join(header_lines)


def _annotations_section(
    annotations: list[ZoteroAnnotation],
    include_parts: frozenset[str],
) -> str:
    if "annotations" not in include_parts or not annotations:
        return ""
    annotation_lines = []
    for annotation in annotations:
        parts = []
        if annotation.page_label:
            parts.append(f"Page {annotation.page_label}")
        if annotation.text:
            parts.append(annotation.text)
        if annotation.comment:
            parts.append(f"Comment: {annotation.comment}")
        if parts:
            annotation_lines.append(" | ".join(parts))
    if not annotation_lines:
        return ""
    return "Annotations:\n" + "\n\n".join(annotation_lines)


def build_document_content(
    record: ZoteroPdfRecord,
    *,
    pdf_text: str,
    notes: list[ZoteroNote],
    annotations: list[ZoteroAnnotation],
    include_parts: frozenset[str],
) -> str:
    """
    Compose the full text payload for one Zotero item.

    Parameters
    ----------
    record : ZoteroPdfRecord
        Bibliographic metadata and attachment identifiers.
    pdf_text : str
        Extracted PDF plain text.
    notes : list[ZoteroNote]
        User notes linked to the item.
    annotations : list[ZoteroAnnotation]
        PDF annotations linked to the attachment.
    include_parts : frozenset[str]
        Enabled content sections from configuration.

    Returns
    -------
    str
        Concatenated document body for indexing.
    """
    sections: list[str] = []

    metadata = _metadata_section(record, include_parts)
    if metadata:
        sections.append(metadata)

    if "abstract" in include_parts and record.abstract.strip():
        sections.append(f"Abstract:\n{record.abstract.strip()}")

    if "notes" in include_parts and notes:
        note_lines = [note.text for note in notes]
        sections.append("Notes:\n" + "\n\n".join(note_lines))

    annotations_text = _annotations_section(annotations, include_parts)
    if annotations_text:
        sections.append(annotations_text)

    if "pdf" in include_parts and pdf_text.strip():
        sections.append(f"PDF text:\n{pdf_text.strip()}")

    return "\n\n".join(section for section in sections if section.strip())


def _fetch_field(db_path: Path, item_id: int, field_name: str) -> str:
    connection = open_readonly_database(db_path)
    try:
        row = connection.execute(
            """
            SELECT idv.value
            FROM itemData id
            JOIN fields f ON f.fieldID = id.fieldID
            JOIN itemDataValues idv ON idv.valueID = id.valueID
            WHERE id.itemID = ? AND f.fieldName = ?
            LIMIT 1
            """,
            (item_id, field_name),
        ).fetchone()
    finally:
        connection.close()
    if row is None:
        return ""
    return str(row[0] or "")


def _fetch_creators(db_path: Path, item_id: int) -> str:
    connection = open_readonly_database(db_path)
    try:
        rows = connection.execute(
            """
            SELECT c.lastName, c.firstName
            FROM itemCreators ic
            JOIN creators c ON c.creatorID = ic.creatorID
            WHERE ic.itemID = ?
            ORDER BY ic.orderIndex
            """,
            (item_id,),
        ).fetchall()
    finally:
        connection.close()

    names: list[str] = []
    for last_name, first_name in rows:
        last = str(last_name or "").strip()
        first = str(first_name or "").strip()
        if first and last:
            names.append(f"{first} {last}")
        elif last:
            names.append(last)
        elif first:
            names.append(first)
    return ", ".join(names)


def _fetch_tags(db_path: Path, item_id: int) -> tuple[str, ...]:
    connection = open_readonly_database(db_path)
    try:
        rows = connection.execute(
            """
            SELECT t.name
            FROM itemTags it
            JOIN tags t ON t.tagID = it.tagID
            WHERE it.itemID = ?
            ORDER BY t.name
            """,
            (item_id,),
        ).fetchall()
    finally:
        connection.close()
    return tuple(str(row[0]) for row in rows if row[0])


def _format_note_text(title: str, body: str) -> str:
    title = title.strip()
    body = body.strip()
    if title and body:
        return f"{title}\n{body}"
    return title or body
