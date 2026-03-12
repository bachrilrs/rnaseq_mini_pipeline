"""
Unit tests for QC metrics module.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
import pandas as pd
import numpy as np
from rnaseq.qc import library_size, zero_fraction, expressed_gene, log_transform


class TestLibrarySize:
    """Test suite for library_size function."""

    def test_library_size_basic(self):
        """Test basic library size calculation."""
        df = pd.DataFrame({
            'sample1': [10, 20, 30],
            'sample2': [5, 15, 25]
        }, index=['gene1', 'gene2', 'gene3'])
        
        result = library_size(df)
        
        assert result['sample1'] == 60
        assert result['sample2'] == 45

    def test_library_size_with_zeros(self):
        """Test library size with zero counts."""
        df = pd.DataFrame({
            'sample1': [0, 20, 30],
            'sample2': [5, 0, 25]
        }, index=['gene1', 'gene2', 'gene3'])
        
        result = library_size(df)
        
        assert result['sample1'] == 50
        assert result['sample2'] == 30

    def test_library_size_all_zeros(self):
        """Test library size with all zeros."""
        df = pd.DataFrame({
            'sample1': [0, 0, 0],
            'sample2': [0, 0, 0]
        }, index=['gene1', 'gene2', 'gene3'])
        
        result = library_size(df)
        
        assert result['sample1'] == 0
        assert result['sample2'] == 0


class TestZeroFraction:
    """Test suite for zero_fraction function."""

    def test_zero_fraction_no_zeros(self):
        """Test zero fraction with no zero values."""
        df = pd.DataFrame({
            'sample1': [10, 20, 30],
            'sample2': [5, 15, 25]
        }, index=['gene1', 'gene2', 'gene3'])
        
        result = zero_fraction(df)
        
        assert result['sample1'] == 0.0
        assert result['sample2'] == 0.0

    def test_zero_fraction_with_zeros(self):
        """Test zero fraction calculation with some zeros."""
        df = pd.DataFrame({
            'sample1': [10, 0, 30],
            'sample2': [0, 0, 25]
        }, index=['gene1', 'gene2', 'gene3'])
        
        result = zero_fraction(df)
        
        assert round(result['sample1'], 2) == 33.33
        assert round(result['sample2'], 2) == 66.67

    def test_zero_fraction_all_zeros(self):
        """Test zero fraction with all zeros."""
        df = pd.DataFrame({
            'sample1': [0, 0, 0],
            'sample2': [0, 0, 0]
        }, index=['gene1', 'gene2', 'gene3'])
        
        result = zero_fraction(df)
        
        assert result['sample1'] == 100.0
        assert result['sample2'] == 100.0


class TestExpressedGenes:
    """Test suite for expressed_gene function."""

    def test_expressed_genes_basic(self):
        """Test expressed gene count calculation."""
        df = pd.DataFrame({
            'sample1': [10, 0, 30],
            'sample2': [0, 15, 25]
        }, index=['gene1', 'gene2', 'gene3'])
        
        result = expressed_gene(df)
        
        assert result['sample1'] == 2
        assert result['sample2'] == 2

    def test_expressed_genes_all_expressed(self):
        """Test when all genes are expressed."""
        df = pd.DataFrame({
            'sample1': [10, 20, 30],
            'sample2': [5, 15, 25]
        }, index=['gene1', 'gene2', 'gene3'])
        
        result = expressed_gene(df)
        
        assert result['sample1'] == 3
        assert result['sample2'] == 3

    def test_expressed_genes_none_expressed(self):
        """Test when no genes are expressed."""
        df = pd.DataFrame({
            'sample1': [0, 0, 0],
            'sample2': [0, 0, 0]
        }, index=['gene1', 'gene2', 'gene3'])
        
        result = expressed_gene(df)
        
        assert result['sample1'] == 0
        assert result['sample2'] == 0


class TestLogTransform:
    """Test suite for log_transform function."""

    def test_log1p_transform(self):
        """Test log1p (natural log) transformation."""
        df = pd.DataFrame({
            'sample1': [0, 1, np.e - 1]
        })
        
        result = log_transform(df, base='log1p')
        
        assert result.loc[0, 'sample1'] == pytest.approx(0.0)
        assert result.loc[1, 'sample1'] == pytest.approx(np.log(2))
        assert result.loc[2, 'sample1'] == pytest.approx(1.0, abs=0.01)

    def test_log2_transform(self):
        """Test log2 transformation."""
        df = pd.DataFrame({
            'sample1': [0, 1, 3]
        })
        
        result = log_transform(df, base='log2')
        
        assert result.loc[0, 'sample1'] == pytest.approx(0.0)
        assert result.loc[1, 'sample1'] == pytest.approx(1.0)
        assert result.loc[2, 'sample1'] == pytest.approx(2.0)

    def test_log10_transform(self):
        """Test log10 transformation."""
        df = pd.DataFrame({
            'sample1': [0, 9, 99]
        })
        
        result = log_transform(df, base='log10')
        
        assert result.loc[0, 'sample1'] == pytest.approx(0.0)
        assert result.loc[1, 'sample1'] == pytest.approx(1.0)
        assert result.loc[2, 'sample1'] == pytest.approx(2.0)

    def test_log_transform_invalid_base(self):
        """Test that invalid log base raises ValueError."""
        df = pd.DataFrame({
            'sample1': [0, 1, 2]
        })
        
        with pytest.raises(ValueError, match="Unsupported log base"):
            log_transform(df, base='log999')

    def test_log_transform_no_negative_infinity(self):
        """Test that log transform handles zeros without -inf."""
        df = pd.DataFrame({
            'sample1': [0, 0, 0]
        })
        
        result = log_transform(df, base='log2')
        
        assert not np.any(np.isinf(result))
        assert not np.any(np.isnan(result))