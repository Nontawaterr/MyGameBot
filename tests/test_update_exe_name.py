import sys

import pytest

from lib import updater


class InlineThread:
    """Runs the thread target immediately so the test can check its effect."""

    def __init__(self, target, args=(), daemon=None):
        self.target = target
        self.args = args

    def start(self):
        self.target(*self.args)


@pytest.fixture
def popen_calls(monkeypatch):
    calls = []
    monkeypatch.setattr(updater.subprocess, "Popen", lambda args, **kwargs: calls.append((args, kwargs)))
    monkeypatch.setattr(updater.time, "sleep", lambda seconds: None)
    monkeypatch.setattr(updater.threading, "Thread", InlineThread)
    return calls


@pytest.fixture
def run_as(monkeypatch, tmp_path):
    def make(exe_name):
        exe = tmp_path / exe_name
        exe.write_bytes(b"new build")
        monkeypatch.setattr(sys, "frozen", True, raising=False)
        monkeypatch.setattr(sys, "executable", str(exe))
        return exe

    return make


def test_not_frozen_does_nothing(monkeypatch, popen_calls):
    monkeypatch.delattr(sys, "frozen", raising=False)
    assert updater.migrate_update_exe_name() is False
    assert popen_calls == []


def test_update_exe_replaces_canonical_exe_and_restarts_it(run_as, popen_calls):
    exe = run_as(updater.UPDATE_EXE_NAME)
    canonical = exe.with_name(updater.CANONICAL_EXE_NAME)
    canonical.write_bytes(b"old build")

    assert updater.migrate_update_exe_name() is True

    assert canonical.read_bytes() == b"new build"
    [(args, kwargs)] = popen_calls
    assert args == [str(canonical)]
    assert kwargs["env"]["PYINSTALLER_RESET_ENVIRONMENT"] == "1"


def test_update_exe_keeps_running_when_canonical_exe_is_locked(run_as, popen_calls, monkeypatch):
    run_as(updater.UPDATE_EXE_NAME)

    def locked(source, destination):
        raise PermissionError("file is in use")

    monkeypatch.setattr(updater.shutil, "copyfile", locked)

    assert updater.migrate_update_exe_name() is False
    assert popen_calls == []


def test_canonical_exe_removes_leftover_update_exe(run_as, popen_calls):
    exe = run_as(updater.CANONICAL_EXE_NAME)
    leftover = exe.with_name(updater.UPDATE_EXE_NAME)
    leftover.write_bytes(b"new build")

    assert updater.migrate_update_exe_name() is False

    assert not leftover.exists()
    assert popen_calls == []
