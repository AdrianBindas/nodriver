# Test the configuration options of the agent loop
import sys
import os
import pytest

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from agent.config import Config

@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv('LOOP_DURATION', '120')
    monkeypatch.setenv('SCENARIO_NAME', 'test_scenario')
    monkeypatch.setenv('USER_NAME', 'test_user')
    monkeypatch.setenv('LANGUAGE', 'fr-FR')
    monkeypatch.setenv('STORAGE_PATH', '/tmp/test_storage')
    monkeypatch.setenv('LOG_FILE', '/tmp/test_storage/test.log')
    monkeypatch.setenv('PROXY_SERVER', 'http://proxy.server:8080')

def test_config_initialization(mock_env):
    config = Config()
    assert config.loop_duration == 120
    assert config.scenario_name == 'test_scenario'
    assert config.user_name == 'test_user'
    assert config.lang == 'fr-FR'
    assert config.storage_path == '/tmp/test_storage'
    assert config.log_file == '/tmp/test_storage/test.log'
    assert '--proxy-server=http://proxy.server:8080' in config.browser_options

def test_to_dict(mock_env):
    config = Config()
    config_dict = config.to_dict()
    assert config_dict['loop_duration'] == 120
    assert config_dict['scenario_name'] == 'test_scenario'
    assert config_dict['user_name'] == 'test_user'
    assert config_dict['lang'] == 'fr-FR'
    assert config_dict['storage_path'] == '/tmp/test_storage'
    assert config_dict['log_file'] == '/tmp/test_storage/test.log'
    assert '--proxy-server=http://proxy.server:8080' in config_dict['browser_options']

def test_default_values(monkeypatch):
    monkeypatch.delenv('LOOP_DURATION', raising=False)
    monkeypatch.delenv('SCENARIO_NAME', raising=False)
    monkeypatch.delenv('USER_NAME', raising=False)
    monkeypatch.delenv('LANGUAGE', raising=False)
    monkeypatch.delenv('STORAGE_PATH', raising=False)
    monkeypatch.delenv('LOG_FILE', raising=False)
    monkeypatch.delenv('PROXY_SERVER', raising=False)

    config = Config()
    assert config.loop_duration == 100
    assert config.scenario_name == 'default_scenario'
    assert config.user_name == 'default_user'
    assert config.lang == 'en-US'
    assert config.storage_path == os.path.join('default_scenario', 'default_user')
    assert config.log_file == os.path.join(config.storage_path, 'app.log')
    assert '--proxy-server=' not in config.browser_options
