import pytest
from pathlib import Path
from unittest.mock import patch, AsyncMock
from datetime import datetime, timezone

from app.handlers.file_handling import (
    get_session_dir,
    get_session_file,
    write_session_to_file,
    load_session_from_file,
    cleanup_session_files,
)
from app.models import Session


@pytest.fixture
def mock_settings(tmp_path):
    with patch("app.handlers.file_handling.SETTINGS") as mock:
        mock.session_storage_folder = str(tmp_path)
        yield mock


@pytest.fixture
def sample_session():
    return Session(
        session_id="test123",
        last_active=datetime.now(timezone.utc)
    )


def test_get_session_dir_creates_directory(mock_settings, tmp_path):
    session_dir = get_session_dir("test123", create=True)
    assert session_dir.exists()
    assert session_dir.is_dir()


def test_get_session_dir_no_create(mock_settings, tmp_path):
    session_dir = get_session_dir("test123", create=False)
    assert not session_dir.exists()


def test_get_session_file_path(mock_settings):
    session_file = get_session_file("test123")
    assert session_file.name == "session.json"
    assert session_file.parent.name == "test123"


@pytest.mark.asyncio
async def test_write_and_load_session_roundtrip(mock_settings, sample_session):
    await write_session_to_file(sample_session)
    loaded = await load_session_from_file(sample_session.session_id)

    assert loaded is not None
    assert loaded.session_id == sample_session.session_id
    assert loaded.last_active == sample_session.last_active


@pytest.mark.asyncio
async def test_load_session_returns_none_when_missing(mock_settings):
    result = await load_session_from_file("nonexistent")
    assert result is None


@pytest.mark.asyncio
async def test_cleanup_removes_directory(mock_settings, sample_session):
    await write_session_to_file(sample_session)
    assert get_session_dir(sample_session.session_id, create=False).exists()

    await cleanup_session_files(sample_session.session_id)
    assert not get_session_dir(sample_session.session_id, create=False).exists()


@pytest.mark.asyncio
async def test_cleanup_warns_when_directory_missing(mock_settings, caplog):
    await cleanup_session_files("nonexistent")
    assert "does not exist" in caplog.text
