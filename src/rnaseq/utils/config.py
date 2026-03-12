"""Configuration management."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class DatabaseConfig:
    """Database configuration."""
    host: str
    user: str
    password: str
    database: str
    port: int = 5432
    timeout: int = 10


@dataclass
class PipelineConfig:
    """Pipeline configuration."""
    dataset_id: str
    data_dir: str
    output_dir: str
    batch_size: int = 1000


class ConfigManager:
    """Manage configuration from YAML and environment variables."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize configuration manager."""
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not Path(self.config_path).exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        return config
    
    def get_database_config(self) -> DatabaseConfig:
        """Get database configuration with environment variable overrides."""
        db_config = self.config.get('database', {})
        
        return DatabaseConfig(
            host=os.getenv('DB_HOST', db_config.get('host', 'localhost')),
            user=os.getenv('DB_USER', db_config.get('user', 'postgres')),
            password=os.getenv('DB_PASSWORD', db_config.get('password', '')),
            database=os.getenv('DB_NAME', db_config.get('database', 'rnaseq_db')),
            port=int(os.getenv('DB_PORT', db_config.get('port', 5432))),
            timeout=int(os.getenv('DB_TIMEOUT', db_config.get('timeout', 10)))
        )
    
    def get_pipeline_config(self) -> PipelineConfig:
        """Get pipeline configuration."""
        pipe_config = self.config.get('pipeline', {})
        
        return PipelineConfig(
            dataset_id=os.getenv('DATASET_ID', pipe_config.get('dataset_id', 'GSE60450')),
            data_dir=os.getenv('DATA_DIR', pipe_config.get('data_dir', 'data')),
            output_dir=os.getenv('OUTPUT_DIR', pipe_config.get('output_dir', 'output')),
            batch_size=int(os.getenv('BATCH_SIZE', pipe_config.get('batch_size', 1000)))
        )