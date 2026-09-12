import io
import os
import sys
import threading
import time
import zipfile
from pathlib import Path

import pytest

from lib import updater

SETTINGS = {"package_asset_name": "Rubitdd-Bot-Release.zip"}


@pytest.fixture
def temp_root(monkeypatch, tmp_path):
    monkeypatch.setattr(updater.tempfile, "tempdir", str(tmp_path))
    monkeypatch.setattr(sys, "executable", str(tmp_path / "app" / "Rubitdd-Bot.exe"))
    return tmp_path


def stage_dirs(root):
    return sorted(path.name for path in Path(root).glob(updater.STAGE_DIR_PREFIX + "*"))


def serve_bytes(monkeypatch, payload):
    def fake_download(url, destination, timeout=updater.DEFAULT_TIMEOUT, progress=None):
        Path(destination).write_bytes(payload)

    monkeypatch.setattr(updater, "download_file", fake_download)


def make_manifest(sha256=""):
    return updater.ReleaseManifest(
        version="9.9.9",
        asset_name="Rubitdd-Bot-Release.zip",
        asset_url="http://example.invalid/Rubitdd-Bot-Release.zip",
        sha256=sha256,
    )


def zip_with(name):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr(name, b"exe")
    return buffer.getvalue()


def test_checksum_mismatch_removes_staging_folder(temp_root, monkeypatch):
    serve_bytes(monkeypatch, zip_with(updater.UPDATE_EXE_NAME))

    with pytest.raises(updater.UpdateError, match="Checksum mismatch"):
        updater._stage_and_launch_update({}, make_manifest(sha256="0" * 64), SETTINGS)

    assert stage_dirs(temp_root) == []


def test_broken_package_removes_staging_folder(temp_root, monkeypatch):
    serve_bytes(monkeypatch, b"not a zip")

    with pytest.raises(zipfile.BadZipFile):
        updater._stage_and_launch_update({}, make_manifest(), SETTINGS)

    assert stage_dirs(temp_root) == []


def test_success_hands_staging_folder_to_restart_helper(temp_root, monkeypatch):
    serve_bytes(monkeypatch, zip_with(updater.UPDATE_EXE_NAME))
    launched = []
    monkeypatch.setattr(updater, "_launch_restart_helper", lambda *args: launched.append(args))

    updater._stage_and_launch_update({}, make_manifest(), SETTINGS)

    [(_pid, source_dir, _target_dir, exe_name)] = launched
    assert exe_name == updater.UPDATE_EXE_NAME
    assert Path(source_dir).is_dir()  # the restart helper deletes it after copying
    assert stage_dirs(temp_root) == [Path(source_dir).parent.name]


def test_remove_stale_update_dirs_keeps_recent_and_unrelated_folders(tmp_path):
    now = 1_000_000.0
    old_stage = tmp_path / (updater.STAGE_DIR_PREFIX + "old")
    old_helper = tmp_path / (updater.HELPER_DIR_PREFIX + "old")
    fresh_stage = tmp_path / (updater.STAGE_DIR_PREFIX + "fresh")
    unrelated = tmp_path / "someone_else_old"
    for path in (old_stage, old_helper, fresh_stage, unrelated):
        path.mkdir()
        (path / "file.bin").write_bytes(b"x")
    two_hours_ago = now - 2 * updater.STALE_UPDATE_DIR_SECONDS
    for path in (old_stage, old_helper, unrelated):
        os.utime(path, (two_hours_ago, two_hours_ago))
    os.utime(fresh_stage, (now - 60, now - 60))

    updater._remove_stale_update_dirs(temp_root=tmp_path, now=now)

    assert sorted(path.name for path in tmp_path.iterdir()) == sorted([fresh_stage.name, unrelated.name])


def test_fetch_treats_missing_release_as_no_update(monkeypatch, tmp_path):
    monkeypatch.setattr(updater.tempfile, "tempdir", str(tmp_path))

    def not_found(url, timeout=updater.DEFAULT_TIMEOUT):
        raise updater.urllib.error.HTTPError(url, 404, "Not Found", None, None)

    monkeypatch.setattr(updater, "fetch_json", not_found)
    settings = {"release_api_url": "http://example.invalid/latest", "manifest_asset_name": "release.json"}

    assert updater._fetch_available_update(settings) is None


class FakeResponse:
    def __init__(self, chunks, length):
        self.chunks = list(chunks)
        self.headers = {"Content-Length": str(length)}

    def read(self, size=-1):
        return self.chunks.pop(0) if self.chunks else b""

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        return False


def test_download_file_reports_progress(monkeypatch, tmp_path):
    monkeypatch.setattr(updater.urllib.request, "urlopen", lambda request, timeout: FakeResponse([b"ab", b"cde"], 5))
    progress = updater.DownloadProgress()

    updater.download_file("http://example.invalid/file", tmp_path / "file.bin", progress=progress)

    assert (progress.done, progress.total) == (5, 5)
    assert (tmp_path / "file.bin").read_bytes() == b"abcde"


class FakeRoot:
    """Collects root.after callbacks and runs them on the test thread, like Tk's main loop."""

    def __init__(self):
        self.callbacks = []

    def after(self, ms, callback):
        self.callbacks.append(callback)

    def run_until_idle(self, limit=5000):
        for _ in range(limit):
            if not self.callbacks:
                return
            self.callbacks.pop(0)()
            time.sleep(0.001)
        raise AssertionError("background work never finished")


def test_run_in_background_delivers_result_on_the_calling_thread():
    root = FakeRoot()
    seen = []

    updater._run_in_background(
        root,
        lambda: threading.current_thread().name,
        lambda result: seen.append((result, threading.current_thread().name)),
        lambda exc: seen.append(exc),
    )
    root.run_until_idle()

    [(worker_thread, callback_thread)] = seen
    assert callback_thread == threading.current_thread().name
    assert worker_thread != callback_thread


def test_run_in_background_delivers_errors():
    root = FakeRoot()
    seen = []

    def fail():
        raise updater.UpdateError("nope")

    updater._run_in_background(root, fail, seen.append, seen.append)
    root.run_until_idle()

    [error] = seen
    assert isinstance(error, updater.UpdateError)
