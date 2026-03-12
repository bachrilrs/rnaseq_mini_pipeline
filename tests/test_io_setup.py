"""
Unit tests for IO setup module.
Tests for load_counts_tsv, load_samples_csv, load_samples_geo_series, and validation functions.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
from rnaseq.io_setup import (
    normalize_and_validate_counts,
    normalize_and_validate_samples,
    load_counts_tsv,
    load_samples_csv,
    load_samples_geo_series
)


class TestNormalizeAndValidateCounts:
    """Test suite for normalize_and_validate_counts function."""

    def test_valid_counts_dataframe(self):
        """Test that valid counts DataFrame passes validation."""
        df = pd.DataFrame({
            'sample1': [10, 20, 30],
            'sample2': [5, 15, 25]
        }, index=['gene1', 'gene2', 'gene3'])
        df.index.name = 'gene_id'
        
        result = normalize_and_validate_counts(df)
        assert isinstance(result, pd.DataFrame)
        assert result.index.name == 'gene_id'

    def test_counts_missing_index_name(self):
        """Test that missing index name raises ValueError."""
        df = pd.DataFrame({
            'sample1': [10, 20, 30],
            'sample2': [5, 15, 25]
        }, index=['gene1', 'gene2', 'gene3'])
        
        with pytest.raises(ValueError, match="index must be gene_id"):
            normalize_and_validate_counts(df)

    def test_counts_with_missing_gene_ids(self):
        """Test that missing gene IDs raise ValueError."""
        df = pd.DataFrame({
            'sample1': [10, 20, 30],
            'sample2': [5, 15, 25]
        }, index=['gene1', np.nan, 'gene3'])
        df.index.name = 'gene_id'
        
        with pytest.raises(ValueError, match="missing gene_id"):
            normalize_and_validate_counts(df)

    def test_counts_with_duplicate_gene_ids(self):
        """Test that duplicate gene IDs raise ValueError."""
        df = pd.DataFrame({
            'sample1': [10, 20, 30],
            'sample2': [5, 15, 25]
        }, index=['gene1', 'gene1', 'gene3'])
        df.index.name = 'gene_id'
        
        with pytest.raises(ValueError, match="not unique"):
            normalize_and_validate_counts(df)

    def test_counts_with_missing_sample_ids(self):
        """Test that missing sample IDs raise ValueError."""
        df = pd.DataFrame({
            'sample1': [10, 20, 30],
            np.nan: [5, 15, 25]
        }, index=['gene1', 'gene2', 'gene3'])
        df.index.name = 'gene_id'
        
        with pytest.raises(ValueError, match="missing sample_id"):
            normalize_and_validate_counts(df)

    def test_counts_with_duplicate_sample_ids(self):
        """Test that duplicate sample IDs raise ValueError."""
        df = pd.DataFrame({
            'sample1': [10, 20, 30],
            'sample2': [5, 15, 25],
            'sample3': [8, 12, 22]
        }, index=['gene1', 'gene2', 'gene3'])
        df.index.name = 'gene_id'
        
        # Manually set duplicate columns to test
        df.columns = ['sample1', 'sample1', 'sample2']
        
        with pytest.raises(ValueError, match="Duplicate sample_id"):
            normalize_and_validate_counts(df)

    def test_counts_with_missing_values(self):
        """Test that missing values in counts raise ValueError."""
        df = pd.DataFrame({
            'sample1': [10, np.nan, 30],
            'sample2': [5, 15, 25]
        }, index=['gene1', 'gene2', 'gene3'])
        df.index.name = 'gene_id'
        
        with pytest.raises(ValueError, match="Missing values"):
            normalize_and_validate_counts(df)

    def test_counts_with_non_integer_values(self):
        """Test that non-integer values raise ValueError."""
        df = pd.DataFrame({
            'sample1': [10.5, 20, 30],
            'sample2': [5, 15, 25]
        }, index=['gene1', 'gene2', 'gene3'])
        df.index.name = 'gene_id'
        
        with pytest.raises(ValueError, match="integer-valued"):
            normalize_and_validate_counts(df)

    def test_counts_with_negative_values(self):
        """Test that negative values raise ValueError."""
        df = pd.DataFrame({
            'sample1': [10, -20, 30],
            'sample2': [5, 15, 25]
        }, index=['gene1', 'gene2', 'gene3'])
        df.index.name = 'gene_id'
        
        with pytest.raises(ValueError, match="non-negative"):
            normalize_and_validate_counts(df)


class TestNormalizeAndValidateSamples:
    """Test suite for normalize_and_validate_samples function."""

    def test_valid_samples_dataframe(self):
        """Test that valid samples DataFrame passes validation."""
        counts_df = pd.DataFrame({
            'sample1': [10, 20, 30],
            'sample2': [5, 15, 25]
        }, index=['gene1', 'gene2', 'gene3'])
        counts_df.index.name = 'gene_id'
        
        samples_df = pd.DataFrame({
            'sample_id': ['sample1', 'sample2'],
            'condition': ['control', 'treatment'],
            'replicate': [1, 1]
        })
        
        result = normalize_and_validate_samples(samples_df, counts_df)
        assert isinstance(result, pd.DataFrame)
        assert list(result['sample_id']) == ['sample1', 'sample2']

    def test_samples_missing_required_columns(self):
        """Test that missing required columns raise ValueError."""
        counts_df = pd.DataFrame({
            'sample1': [10, 20, 30],
            'sample2': [5, 15, 25]
        }, index=['gene1', 'gene2', 'gene3'])
        counts_df.index.name = 'gene_id'
        
        samples_df = pd.DataFrame({
            'sample_id': ['sample1', 'sample2'],
            'condition': ['control', 'treatment']
        })
        
        with pytest.raises(ValueError, match="Missing required columns"):
            normalize_and_validate_samples(samples_df, counts_df)

    def test_samples_with_missing_values(self):
        """Test that missing values in samples raise ValueError."""
        counts_df = pd.DataFrame({
            'sample1': [10, 20, 30],
            'sample2': [5, 15, 25]
        }, index=['gene1', 'gene2', 'gene3'])
        counts_df.index.name = 'gene_id'
        
        samples_df = pd.DataFrame({
            'sample_id': ['sample1', np.nan],
            'condition': ['control', 'treatment'],
            'replicate': [1, 1]
        })
        
        with pytest.raises(ValueError, match="Missing values"):
            normalize_and_validate_samples(samples_df, counts_df)

    def test_samples_with_duplicate_sample_ids(self):
        """Test that duplicate sample IDs raise ValueError."""
        counts_df = pd.DataFrame({
            'sample1': [10, 20, 30],
            'sample2': [5, 15, 25]
        }, index=['gene1', 'gene2', 'gene3'])
        counts_df.index.name = 'gene_id'
        
        samples_df = pd.DataFrame({
            'sample_id': ['sample1', 'sample1'],
            'condition': ['control', 'treatment'],
            'replicate': [1, 2]
        })
        
        with pytest.raises(ValueError, match="not unique"):
            normalize_and_validate_samples(samples_df, counts_df)

    def test_samples_with_non_integer_replicate(self):
        """Test that non-integer replicate values raise ValueError."""
        counts_df = pd.DataFrame({
            'sample1': [10, 20, 30],
            'sample2': [5, 15, 25]
        }, index=['gene1', 'gene2', 'gene3'])
        counts_df.index.name = 'gene_id'
        
        samples_df = pd.DataFrame({
            'sample_id': ['sample1', 'sample2'],
            'condition': ['control', 'treatment'],
            'replicate': [1.5, 1]
        })
        
        with pytest.raises(ValueError, match="integer-valued"):
            normalize_and_validate_samples(samples_df, counts_df)

    def test_samples_with_zero_replicate(self):
        """Test that replicate < 1 raises ValueError."""
        counts_df = pd.DataFrame({
            'sample1': [10, 20, 30],
            'sample2': [5, 15, 25]
        }, index=['gene1', 'gene2', 'gene3'])
        counts_df.index.name = 'gene_id'
        
        samples_df = pd.DataFrame({
            'sample_id': ['sample1', 'sample2'],
            'condition': ['control', 'treatment'],
            'replicate': [0, 1]
        })
        
        with pytest.raises(ValueError, match=">= 1"):
            normalize_and_validate_samples(samples_df, counts_df)

    def test_samples_mismatch_with_counts(self):
        """Test that mismatched sample IDs with counts raise ValueError."""
        counts_df = pd.DataFrame({
            'sample1': [10, 20, 30],
            'sample2': [5, 15, 25],
            'sample3': [8, 12, 22]
        }, index=['gene1', 'gene2', 'gene3'])
        counts_df.index.name = 'gene_id'
        
        samples_df = pd.DataFrame({
            'sample_id': ['sample1', 'sample2'],
            'condition': ['control', 'treatment'],
            'replicate': [1, 1]
        })
        
        with pytest.raises(ValueError, match="Mismatch"):
            normalize_and_validate_samples(samples_df, counts_df)

    def test_samples_reordering(self):
        """Test that samples are reordered to match counts columns."""
        counts_df = pd.DataFrame({
            'sample1': [10, 20, 30],
            'sample2': [5, 15, 25]
        }, index=['gene1', 'gene2', 'gene3'])
        counts_df.index.name = 'gene_id'
        
        # Provide samples in different order
        samples_df = pd.DataFrame({
            'sample_id': ['sample2', 'sample1'],
            'condition': ['treatment', 'control'],
            'replicate': [1, 1]
        })
        
        result = normalize_and_validate_samples(samples_df, counts_df)
        assert list(result['sample_id']) == ['sample1', 'sample2']

class TestLoadCountsTsv:
    """Test suite for load_counts_tsv function."""

    def test_load_counts_basic(self):
        """Test loading counts from TSV file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            # First column becomes index, GeneID must be second column
            f.write("Unnamed\tGeneID\tsample1\tsample2\n")
            f.write("0\tgene1\t10\t5\n")
            f.write("1\tgene2\t20\t15\n")
            f.write("2\tgene3\t30\t25\n")
            temp_file = f.name
        
        try:
            result = load_counts_tsv(
                file_path=temp_file,
                pattern=r"(sample\d+)",
                sep='\t',
                gene_id_candidates=['GeneID']
            )
            
            assert result.shape == (3, 2)
            assert result.index.name == 'gene_id'
            assert list(result.columns) == ['sample1', 'sample2']
            assert result.iloc[0, 0] == 10
        finally:
            os.unlink(temp_file)

    def test_load_counts_with_entrez_gene_id(self):
        """Test loading counts with EntrezGeneID column."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Unnamed\tEntrezGeneID\tsample_A\tsample_B\n")
            f.write("0\t12345\t10\t5\n")
            f.write("1\t12346\t20\t15\n")
            temp_file = f.name
        
        try:
            result = load_counts_tsv(
                file_path=temp_file,
                pattern=r"(sample_\w+)",
                sep='\t',
                gene_id_candidates=['EntrezGeneID', 'GeneID']
            )
            
            assert result.shape == (2, 2)
            assert result.index.name == 'gene_id'
        finally:
            os.unlink(temp_file)

    def test_load_counts_missing_gene_id_column(self):
        """Test that missing gene ID column raises ValueError."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Unnamed\tBadColumn\tsample1\tsample2\n")
            f.write("0\tgene1\t10\t5\n")
            temp_file = f.name
        
        try:
            with pytest.raises(ValueError, match="No gene identifier column"):
                load_counts_tsv(
                    file_path=temp_file,
                    pattern=r"(sample\d+)",
                    sep='\t'
                )
        finally:
            os.unlink(temp_file)

    def test_load_counts_pattern_mismatch(self):
        """Test that pattern mismatch raises ValueError."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Unnamed\tGeneID\tbad_col\tsample2\n")
            f.write("0\tgene1\t10\t5\n")
            temp_file = f.name
        
        try:
            with pytest.raises(ValueError, match="does not match the expected pattern"):
                load_counts_tsv(
                    file_path=temp_file,
                    pattern=r"(sample\d+)",
                    sep='\t',
                    gene_id_candidates=['GeneID']
                )
        finally:
            os.unlink(temp_file)

    def test_load_counts_missing_pattern_none(self):
        """Test that None pattern raises ValueError."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Unnamed\tGeneID\tsample1\tsample2\n")
            f.write("0\tgene1\t10\t5\n")
            temp_file = f.name
        
        try:
            with pytest.raises(ValueError, match="pattern must be provided"):
                load_counts_tsv(
                    file_path=temp_file,
                    pattern=None,
                    sep='\t',
                    gene_id_candidates=['GeneID']
                )
        finally:
            os.unlink(temp_file)

class TestLoadSamplesCsv:
    """Test suite for load_samples_csv function."""

    def test_load_samples_csv_basic(self):
        """Test loading samples from CSV file."""
        counts_df = pd.DataFrame({
            'sample1': [10, 20, 30],
            'sample2': [5, 15, 25]
        }, index=['gene1', 'gene2', 'gene3'])
        counts_df.index.name = 'gene_id'
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("sample_id,condition,replicate\n")
            f.write("sample1,control,1\n")
            f.write("sample2,treatment,1\n")
            temp_file = f.name
        
        try:
            result = load_samples_csv(temp_file, counts_df)
            assert result.shape == (2, 3)
            assert 'sample_id' in result.columns
        finally:
            os.unlink(temp_file)