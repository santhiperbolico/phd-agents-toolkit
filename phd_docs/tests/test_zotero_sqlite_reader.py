"""Tests for Zotero SQLite helpers."""

import sqlite3

import pytest

from phd_docs.extractors.zotero import sqlite_reader


@pytest.fixture
def zotero_db(tmp_path):
    db_path = tmp_path / "zotero.sqlite"
    connection = sqlite3.connect(db_path)
    connection.executescript(
        """
        CREATE TABLE fields (
            fieldID INTEGER PRIMARY KEY,
            fieldName TEXT NOT NULL UNIQUE
        );
        CREATE TABLE itemTypes (
            itemTypeID INTEGER PRIMARY KEY,
            typeName TEXT NOT NULL UNIQUE
        );
        CREATE TABLE items (
            itemID INTEGER PRIMARY KEY,
            itemTypeID INTEGER NOT NULL,
            key TEXT NOT NULL,
            parentItemID INTEGER
        );
        CREATE TABLE itemAttachments (
            itemID INTEGER PRIMARY KEY,
            parentItemID INTEGER NOT NULL,
            contentType TEXT,
            path TEXT
        );
        CREATE TABLE itemData (
            itemID INTEGER NOT NULL,
            fieldID INTEGER NOT NULL,
            valueID INTEGER NOT NULL
        );
        CREATE TABLE itemDataValues (
            valueID INTEGER PRIMARY KEY,
            value TEXT NOT NULL
        );
        CREATE TABLE itemCreators (
            itemID INTEGER NOT NULL,
            creatorID INTEGER NOT NULL,
            orderIndex INTEGER NOT NULL
        );
        CREATE TABLE creators (
            creatorID INTEGER PRIMARY KEY,
            firstName TEXT,
            lastName TEXT
        );
        CREATE TABLE tags (
            tagID INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        );
        CREATE TABLE itemTags (
            itemID INTEGER NOT NULL,
            tagID INTEGER NOT NULL,
            type INTEGER NOT NULL
        );
        CREATE TABLE itemNotes (
            itemID INTEGER PRIMARY KEY,
            parentItemID INTEGER NOT NULL,
            note TEXT,
            title TEXT
        );
        CREATE TABLE itemAnnotations (
            itemID INTEGER PRIMARY KEY,
            parentItemID INTEGER NOT NULL,
            type INTEGER NOT NULL,
            authorName TEXT,
            text TEXT,
            comment TEXT,
            color TEXT,
            pageLabel TEXT,
            sortIndex TEXT NOT NULL,
            position TEXT NOT NULL,
            isExternal INTEGER NOT NULL
        );

        INSERT INTO itemTypes VALUES (1, 'journalArticle'), (2, 'note');
        INSERT INTO fields VALUES (1, 'title'), (2, 'date'), (3, 'abstractNote'), (4, 'DOI');
        INSERT INTO items VALUES (10, 1, 'PARENT1', NULL);
        INSERT INTO items VALUES (11, 1, 'ATTACH1', 10);
        INSERT INTO itemAttachments VALUES (11, 10, 'application/pdf', 'storage:paper.pdf');
        INSERT INTO itemDataValues VALUES
            (100, 'Sample Paper'),
            (101, '2024'),
            (102, 'An abstract.'),
            (103, '10.0000/test');
        INSERT INTO itemData VALUES (10, 1, 100), (10, 2, 101), (10, 3, 102), (10, 4, 103);
        INSERT INTO creators VALUES (1, 'Ada', 'Lovelace');
        INSERT INTO itemCreators VALUES (10, 1, 0);
        INSERT INTO tags VALUES (1, 'cosmology');
        INSERT INTO itemTags VALUES (10, 1, 0);
        INSERT INTO itemNotes VALUES (12, 10, 'Note body', 'Note title');
        INSERT INTO itemAnnotations VALUES (
            20, 11, 1, NULL, 'highlight', 'important', NULL, '3', '0', '0', 0
        );
        """
    )
    connection.commit()
    connection.close()
    storage_dir = tmp_path / "storage" / "ATTACH1"
    storage_dir.mkdir(parents=True)
    (storage_dir / "paper.pdf").write_bytes(b"%PDF-1.4\n")
    return tmp_path


def test_resolve_pdf_path_storage_prefix(zotero_db):
    resolved = sqlite_reader.resolve_pdf_path(
        zotero_db,
        "ATTACH1",
        "storage:paper.pdf",
    )
    assert resolved == zotero_db / "storage" / "ATTACH1" / "paper.pdf"


def test_iter_pdf_records_returns_metadata(zotero_db):
    records = sqlite_reader.iter_pdf_records(zotero_db / "zotero.sqlite")
    assert len(records) == 1
    record = records[0]
    assert record.parent_key == "PARENT1"
    assert record.title == "Sample Paper"
    assert record.creators == "Ada Lovelace"
    assert record.abstract == "An abstract."
    assert record.tags == ("cosmology",)


def test_iter_pdf_records_skips_excluded_tags(zotero_db):
    records = sqlite_reader.iter_pdf_records(
        zotero_db / "zotero.sqlite",
        exclude_tags=frozenset({"cosmology"}),
    )
    assert records == []


def test_build_document_path():
    assert sqlite_reader.build_document_path("ABC123") == "zotero://item/ABC123"


def test_build_document_content_includes_sections(zotero_db):
    record = sqlite_reader.iter_pdf_records(zotero_db / "zotero.sqlite")[0]
    notes = sqlite_reader.fetch_notes(zotero_db / "zotero.sqlite", record.parent_item_id)
    annotations = sqlite_reader.fetch_annotations(
        zotero_db / "zotero.sqlite",
        record.attachment_item_id,
    )
    content = sqlite_reader.build_document_content(
        record,
        pdf_text="Body text",
        notes=notes,
        annotations=annotations,
        include_parts=frozenset({"metadata", "abstract", "pdf", "notes", "annotations"}),
    )
    assert "Sample Paper" in content
    assert "An abstract." in content
    assert "Body text" in content
    assert "Note body" in content
    assert "highlight" in content
