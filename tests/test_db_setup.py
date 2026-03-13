"""Tests for database setup module."""

import pytest
import tempfile
import os
from unittest.mock import MagicMock, patch
from rnaseq.db_setup import (
    connect_database,
    create_tables,
    run_database
)


class TestDatabaseConnection:
    """Test database connection functions."""

    @patch('rnaseq.db_setup.psycopg2.connect')
    def test_connect_database_success(self, mock_connect):
        """Test successful database connection."""
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        with patch.dict(os.environ, {
            'DB_HOST': 'localhost',
            'DB_PORT': '5432',
            'DB_USER': 'test_user',
            'DB_PASSWORD': 'test_pass',
            'DB_NAME': 'test_db'
        }):
            conn = connect_database()
            assert conn is not None

    @patch('rnaseq.db_setup.psycopg2.connect')
    def test_connect_database_with_defaults(self, mock_connect):
        """Test connection with default values."""
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        with patch.dict(os.environ, {}, clear=True):
            conn = connect_database()
            assert conn is not None


class TestTableCreation:
    """Test table creation functions."""

    def test_create_tables_executes(self):
        """Test that create_tables executes SQL commands."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__.return_value = None

        sql_content = "CREATE TABLE test (id SERIAL);"
        
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = sql_content
            create_tables(mock_conn)
            
            # Verify execute was called
            assert mock_cursor.execute.called
            # Verify commit was called
            mock_conn.commit.assert_called()


class TestDatabaseSetup:
    """Test main database setup."""

    @patch('rnaseq.db_setup.connect_database')
    def test_run_database_creates_tables(self, mock_connect):
        """Test that run_database creates tables."""
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        with patch('rnaseq.db_setup.create_tables') as mock_create:
            with patch('os.path.exists', return_value=False):
                run_database()
                mock_create.assert_called_once()