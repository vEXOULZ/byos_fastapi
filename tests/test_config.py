import logging

import pytest

from trmnl_server import config


@pytest.fixture(autouse=True)
def _restore_config():
    yield
    config.load_config()


def test_plain_variable(monkeypatch):
    monkeypatch.setenv('SETUP_API_KEY', 'from-env')
    config.load_config()
    assert config.SETUP_API_KEY == 'from-env'
    assert 'setup_api_key' in config._ENV_OVERRIDES


def test_file_variable_wins_and_drops_one_newline(monkeypatch, tmp_path):
    secret = tmp_path / 'setup_api_key'
    secret.write_bytes(b'from-file\n\n')
    monkeypatch.setenv('SETUP_API_KEY', 'from-env')
    monkeypatch.setenv('FILE__SETUP_API_KEY', str(secret))
    config.load_config()
    assert config.SETUP_API_KEY == 'from-file\n'
    assert 'setup_api_key' in config._ENV_OVERRIDES


def test_file_variable_for_other_types(monkeypatch, tmp_path):
    port = tmp_path / 'port'
    port.write_bytes(b'8080\r\n')
    monkeypatch.setenv('FILE__SERVER_PORT', str(port))
    config.load_config()
    assert config.SERVER_PORT == 8080


def test_unreadable_file_falls_back(monkeypatch, tmp_path, caplog):
    monkeypatch.setenv('SETUP_API_KEY', 'from-env')
    monkeypatch.setenv('FILE__SETUP_API_KEY', str(tmp_path / 'missing'))
    with caplog.at_level(logging.WARNING, logger='trmnlServer'):
        config.load_config()
    assert config.SETUP_API_KEY == 'from-env'
    assert 'FILE__SETUP_API_KEY' in caplog.text


def test_secret_is_not_logged(caplog):
    with caplog.at_level(logging.INFO, logger='trmnlServer'):
        config.update_config('setup_api_key', 'do-not-log-me')
        config.update_config('setup_message', 'fine-to-log')
    assert config.SETUP_API_KEY == 'do-not-log-me'
    assert 'do-not-log-me' not in caplog.text
    assert 'fine-to-log' in caplog.text
