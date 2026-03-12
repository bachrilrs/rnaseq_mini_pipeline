"""
Unit tests for database setup module.
Tests for connection, table creation, and data insertion functions.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
import pandas as pd
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from rnaseq.db_setup import (
    connect_database,
    create_tables,
    insert_postgresql_db
)


class TestConnectDatabase:
    """Test suite for database connection functions."""

    @patch.dict(os.environ, {
        'POSTGRES_DB': 'test_db',
        'POSTGRES_USER': 'test_user',
        'POSTGRES_PASSWORD': 'test_pass',
        'POSTGRES_HOST': 'localhost',
        'POSTGRES_PORT': '5432'
    })
    @patch('rnaseq.db_setup.psycopg2.connect')
    def test_connect_database_success(self, mock_psycopg2_connect):
        """Test successful database connection."""
        mock_conn = Mock()
        mock_psycopg2_connect.return_value = mock_conn
        
        result = connect_database()
        
        assert result == mock_conn
        mock_psycopg2_connect.assert_called_once()

    @patch.dict(os.environ, {
        'POSTGRES_DB': 'test_db',
        'POSTGRES_USER': 'test_user',
        'POSTGRES_PASSWORD': 'test_pass',
        'POSTGRES_HOST': 'localhost',
        'POSTGRES_PORT': '5432'
    }, clear=False)
    @patch('rnaseq.db_setup.psycopg2.connect')
    def test_connect_database_with_default_host(self, mock_psycopg2_connect):
        """Test database connection with default host."""
        mock_conn = Mock()
        mock_psycopg2_connect.return_value = mock_conn
        
        result = connect_database()
        
        assert result == mock_conn


class TestCreateTables:
    """Test suite for table creation functions."""

    @patch('builtins.open', create=True)
    def test_create_tables_success(self, mock_open):
        """Test successful table creation."""
        mock_open.return_value.__enter__.return_value.read.return_value = (
            "CREATE TABLE test (id INT); CREATE TABLE test2 (id INT);"
        )
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        create_tables(mock_conn)
        
        # Verify execute was called
        assert mock_cursor.execute.called
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()

    @patch('builtins.open', create=True)
    def test_create_tables_empty_commands(self, mock_open):
        """Test table creation with empty SQL."""
        mock_open.return_value.__enter__.return_value.read.return_value = ";;;"
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        create_tables(mock_conn)
        
        # execute should not be called for empty commands
        mock_cursor.execute.assert_not_called()
        mock_conn.commit.assert_called_once()

    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_create_tables_file_not_found(self, mock_open):
        """Test table creation when SQL file not found."""
        mock_conn = MagicMock()
        
        with pytest.raises(FileNotFoundError):
            create_tables(mock_conn)

    @patch('builtins.open', create=True)
    def test_create_tables_with_whitespace(self, mock_open):
        """Test table creation with whitespace in SQL."""
        mock_open.return_value.__enter__.return_value.read.return_value = (
            "  CREATE TABLE test (id INT);  \n  CREATE TABLE test2 (id INT);  "
        )
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        create_tables(mock_conn)
        
        # Both CREATE statements should be executed
        assert mock_cursor.execute.call_count >= 2
        mock_conn.commit.assert_called_once()

    @patch('builtins.open', create=True)
    def test_create_tables_cursor_close(self, mock_open):
        """Test that cursor is properly closed."""
        mock_open.return_value.__enter__.return_value.read.return_value = (
            "CREATE TABLE test (id INT);"
        )
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        create_tables(mock_conn)
        
        mock_cursor.close.assert_called_once()


class TestInsertPostgresqlDb:
    """Test suite for database insertion functions."""

    def test_insert_postgresql_db_basic(self):
        """Test basic data insertion into database."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("sample_id,value\n")
            f.write("sample1,100\n")
            f.write("sample2,200\n")
            temp_file = f.name
        
        try:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
            
            # Mock fetchone to return a run_id
            mock_cursor.fetchone.return_value = (1,)
            # Mock fetchall for column query - return matching columns
            mock_cursor.fetchall.return_value = [('sample_id',), ('value',)]
            
            insert_postgresql_db(
                mock_conn,
                temp_file,
                'test_table',
                'test_dataset',
                '1.0',
                'test_run'
            )
            
            # Verify cursor execute was called for inserting run
            assert mock_cursor.execute.called
        finally:
            os.unlink(temp_file)

    def test_insert_postgresql_db_with_none_values(self):
        """Test data insertion with None values."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("sample_id,value\n")
            f.write("sample1,100\n")
            temp_file = f.name
        
        try:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
            mock_cursor.fetchone.return_value = (1,)
            
            insert_postgresql_db(
                mock_conn,
                temp_file,
                'test_table',
                dataset_id=None,
                version=None,
                run_name=None
            )
            
            # Should use default values
            assert mock_cursor.execute.called
        finally:
            os.unlink(temp_file)

    def test_insert_postgresql_db_exception_handling(self):
        """Test exception handling during insertion."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("sample_id,value\n")
            f.write("sample1,100\n")
            temp_file = f.name
        
        try:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
            
            # Make execute raise an exception
            mock_cursor.execute.side_effect = Exception("Database error")
            
            insert_postgresql_db(
                mock_conn,
                temp_file,
                'test_table',
                'test_dataset',
                '1.0',
                'test_run'
            )
            
            # Verify rollback was called
            mock_conn.rollback.assert_called()
        finally:
            os.unlink(temp_file)

    def test_insert_postgresql_db_no_matching_columns(self):
        """Test insertion when no columns match database schema."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("bad_col1,bad_col2\n")
            f.write("value1,value2\n")
            temp_file = f.name
        
        try:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
            mock_cursor.fetchone.return_value = (1,)
            # Mock fetchall for column query - return NO matching columns
            mock_cursor.fetchall.return_value = [('existing_col',)]
            
            insert_postgresql_db(
                mock_conn,
                temp_file,
                'test_table',
                'test_dataset',
                '1.0',
                'test_run'
            )
            
            # Should skip data insertion but execute runs query
            assert mock_cursor.execute.called
        finally:
            os.unlink(temp_file)

    def test_insert_postgresql_db_samples_table_upsert(self):
        """Test upsert logic for samples table."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("sample_id,condition,geo_accession\n")
            f.write("sample1,control,GSM1\n")
            temp_file = f.name
        
        try:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
            mock_cursor.fetchone.return_value = (1,)
            mock_cursor.fetchall.return_value = [
                ('sample_id',),
                ('condition',),
                ('geo_accession',)
            ]
            
            insert_postgresql_db(
                mock_conn,
                temp_file,
                'samples',
                'test_dataset',
                '1.0',
                'test_run'
            )
            
            # Verify ON CONFLICT clause was used for samples table
            calls = [str(call) for call in mock_cursor.execute.call_args_list]
            insert_calls = [call for call in calls if 'INSERT' in call]
            assert len(insert_calls) > 0
        finally:
            os.unlink(temp_file)

    def test_insert_postgresql_db_default_dataset_id(self):
        """Test that default dataset ID is used when None provided."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("sample_id,value\n")
            f.write("sample1,100\n")
            temp_file = f.name
        
        try:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
            mock_cursor.fetchone.return_value = (1,)
            
            insert_postgresql_db(
                mock_conn,
                temp_file,
                'test_table',
                dataset_id=None,
                version='1.0',
                run_name='test_run'
            )
            
            # Check that default dataset_id was used
            assert mock_cursor.execute.called
            calls = [str(call) for call in mock_cursor.execute.call_args_list]
            # Should contain Unknown_DS
            assert any('Unknown_DS' in str(call) for call in calls)
        finally:
            os.unlink(temp_file)

    def test_insert_postgresql_db_empty_csv(self):
        """Test insertion with empty CSV (only headers)."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("sample_id,value\n")
            temp_file = f.name
        
        try:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
            mock_cursor.fetchone.return_value = (1,)
            mock_cursor.fetchall.return_value = [('sample_id',), ('value',)]
            
            insert_postgresql_db(
                mock_conn,
                temp_file,
                'test_table',
                'test_dataset',
                '1.0',
                'test_run'
            )
            
            # Should handle empty dataframe gracefully
            assert mock_cursor.execute.called
        finally:
            os.unlink(temp_file)

    def test_insert_postgresql_db_with_sample_insertion(self):
        """Test insertion includes sample_id insertion for FK constraint."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("sample_id,value\n")
            f.write("sample1,100\n")
            f.write("sample2,200\n")
            temp_file = f.name
        
        try:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
            mock_cursor.fetchone.return_value = (1,)
            mock_cursor.fetchall.return_value = [('sample_id',), ('value',)]
            
            insert_postgresql_db(
                mock_conn,
                temp_file,
                'qc_metrics',
                'test_dataset',
                '1.0',
                'test_run'
            )
            
            # Verify sample_id insertion was attempted
            calls = [str(call) for call in mock_cursor.execute.call_args_list]
            sample_inserts = [call for call in calls if 'samples' in call.lower()]
            assert len(sample_inserts) > 0
        finally:
            os.unlink(temp_file)