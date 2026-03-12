"""Tests for configuration management."""

import pytest
import os
from src.utils.config import ConfigManager, DatabaseConfig, PipelineConfig


@pytest.fixture
def config_file(tmp_path):
    """Create temporary config file for testing."""
    config_content = """
database:
  host: localhost
  user: testuser
  password: testpass
  database: testdb
  port: 5432

pipeline:
  dataset_id: GSE60450
  data_dir: data
  output_dir: output
  batch_size: 1000
"""
    config_file = tmp_path / "test_config.yaml"
    config_file.write_text(config_content)
    return str(config_file)


def test_config_manager_load(config_file):
    """Test configuration loading."""
    manager = ConfigManager(config_file)
    assert manager.config is not None
    assert 'database' in manager.config
    assert 'pipeline' in manager.config


def test_database_config_retrieval(config_file):
    """Test database configuration retrieval."""
    manager = ConfigManager(config_file)
    db_config = manager.get_database_config()
    
    assert isinstance(db_config, DatabaseConfig)
    assert db_config.host == 'localhost'
    assert db_config.database == 'testdb'


def test_pipeline_config_retrieval(config_file):
    """Test pipeline configuration retrieval."""
    manager = ConfigManager(config_file)
    pipe_config = manager.get_pipeline_config()
    
    assert isinstance(pipe_config, PipelineConfig)
    assert pipe_config.dataset_id == 'GSE60450'
    assert pipe_config.batch_size == 1000


def test_environment_variable_override(config_file, monkeypatch):
    """Test environment variable override."""
    monkeypatch.setenv('DB_HOST', 'prod-host')
    
    manager = ConfigManager(config_file)
    db_config = manager.get_database_config()
    
    assert db_config.host == 'prod-host'