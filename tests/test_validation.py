"""
Unit tests for validation module.
Tests for validate_counts, validate_samples, and related functions.
"""

import numpy as np
import pandas as pd
import pytest

from rnaseq.validation import validate_counts, validate_data, validate_samples


class TestValidateCounts:
    """Test suite for validate_counts function."""

    def test_valid_counts_dataframe(self):
        """Test that valid counts DataFrame passes validation."""
        df = pd.DataFrame(
            {"sample1": [10, 20, 30], "sample2": [5, 15, 25]}, index=["gene1", "gene2", "gene3"]
        )
        df.index.name = "gene_id"

        assert validate_counts(df) is None

    def test_counts_with_missing_values(self):
        """Test that counts with missing values raises ValueError."""
        df = pd.DataFrame(
            {"sample1": [10, np.nan, 30], "sample2": [5, 15, 25]}, index=["gene1", "gene2", "gene3"]
        )
        df.index.name = "gene_id"

        with pytest.raises(ValueError, match="Missing values"):
            validate_counts(df)

    def test_counts_with_duplicate_gene_ids(self):
        """Test that duplicate gene IDs raise ValueError."""
        df = pd.DataFrame(
            {"sample1": [10, 20, 30], "sample2": [5, 15, 25]}, index=["gene1", "gene1", "gene3"]
        )
        df.index.name = "gene_id"

        with pytest.raises(ValueError, match="not unique"):
            validate_counts(df)

    def test_counts_with_non_integer_values(self):
        """Test that non-integer counts raise ValueError."""
        df = pd.DataFrame(
            {"sample1": [10.5, 20, 30], "sample2": [5, 15, 25]}, index=["gene1", "gene2", "gene3"]
        )
        df.index.name = "gene_id"

        with pytest.raises(ValueError, match="integer"):
            validate_counts(df)

    def test_counts_with_negative_values(self):
        """Test that negative counts raise ValueError."""
        df = pd.DataFrame(
            {"sample1": [10, -20, 30], "sample2": [5, 15, 25]}, index=["gene1", "gene2", "gene3"]
        )
        df.index.name = "gene_id"

        with pytest.raises(ValueError, match="non-negative"):
            validate_counts(df)


class TestValidateSamples:
    """Test suite for validate_samples function."""

    def test_valid_samples_dataframe(self):
        """Test that valid samples DataFrame passes validation."""
        df = pd.DataFrame(
            {
                "sample_id": ["sample1", "sample2", "sample3", "sample4"],
                "condition": ["control", "control", "treatment", "treatment"],
                "replicate": [1, 2, 1, 2],
                "geo_accession": ["GSM1", "GSM2", "GSM3", "GSM4"],
            }
        )

        expected_conditions = {"control", "treatment"}
        assert validate_samples(df, expected_conditions) is None

    def test_samples_missing_required_columns(self):
        """Test that missing required columns raise ValueError."""
        df = pd.DataFrame(
            {"sample_id": ["sample1", "sample2"], "condition": ["control", "treatment"]}
        )

        expected_conditions = {"control", "treatment"}
        with pytest.raises(ValueError, match="Missing required columns"):
            validate_samples(df, expected_conditions)

    def test_samples_with_duplicate_sample_ids(self):
        """Test that duplicate sample IDs raise ValueError."""
        df = pd.DataFrame(
            {
                "sample_id": ["sample1", "sample1", "sample3"],
                "condition": ["control", "control", "treatment"],
                "replicate": [1, 2, 1],
                "geo_accession": ["GSM1", "GSM2", "GSM3"],
            }
        )

        expected_conditions = {"control", "treatment"}
        with pytest.raises(ValueError, match="not unique"):
            validate_samples(df, expected_conditions)

    def test_samples_with_missing_condition(self):
        """Test that missing expected condition raises ValueError."""
        df = pd.DataFrame(
            {
                "sample_id": ["sample1", "sample2"],
                "condition": ["control", "control"],
                "replicate": [1, 2],
                "geo_accession": ["GSM1", "GSM2"],
            }
        )

        expected_conditions = {"control", "treatment"}
        with pytest.raises(ValueError, match="do not match expected conditions"):
            validate_samples(df, expected_conditions)

    def test_samples_condition_with_single_replicate(self):
        """Test that condition with fewer than 2 samples raises ValueError."""
        df = pd.DataFrame(
            {
                "sample_id": ["sample1", "sample2", "sample3"],
                "condition": ["control", "treatment", "treatment"],
                "replicate": [1, 1, 2],
                "geo_accession": ["GSM1", "GSM2", "GSM3"],
            }
        )

        expected_conditions = {"control", "treatment"}
        with pytest.raises(ValueError, match="at least two samples"):
            validate_samples(df, expected_conditions)

    def test_samples_replicate_not_consecutive(self):
        """Test that non-consecutive replicates raise ValueError."""
        df = pd.DataFrame(
            {
                "sample_id": ["sample1", "sample2", "sample3", "sample4"],
                "condition": ["control", "control", "treatment", "treatment"],
                "replicate": [1, 3, 1, 2],
                "geo_accession": ["GSM1", "GSM2", "GSM3", "GSM4"],
            }
        )

        expected_conditions = {"control", "treatment"}
        with pytest.raises(ValueError, match="must be"):
            validate_samples(df, expected_conditions)


class TestValidateData:
    """Test suite for validate_data function (integrated validation)."""

    def test_valid_counts_and_samples(self):
        """Test that valid counts and samples data passes validation."""
        counts_df = pd.DataFrame(
            {
                "sample1": [10, 20, 30],
                "sample2": [5, 15, 25],
                "sample3": [8, 12, 22],
                "sample4": [15, 25, 35],
            },
            index=["gene1", "gene2", "gene3"],
        )
        counts_df.index.name = "gene_id"

        samples_df = pd.DataFrame(
            {
                "sample_id": ["sample1", "sample2", "sample3", "sample4"],
                "condition": ["control", "control", "treatment", "treatment"],
                "replicate": [1, 2, 1, 2],
                "geo_accession": ["GSM1", "GSM2", "GSM3", "GSM4"],
            }
        )

        expected_conditions = {"control", "treatment"}
        assert validate_data(counts_df, samples_df, expected_conditions) is None

    def test_counts_and_samples_mismatch(self):
        """Test that mismatched sample IDs raise ValueError."""
        counts_df = pd.DataFrame(
            {
                "sample1": [10, 20, 30],
                "sample2": [5, 15, 25],
                "sample3": [8, 12, 22],
                "sample4": [15, 25, 35],
            },
            index=["gene1", "gene2", "gene3"],
        )
        counts_df.index.name = "gene_id"

        # Only has sample1,sample3 but counts has sample1,sample2,sample3,sample4
        samples_df = pd.DataFrame(
            {
                "sample_id": ["sample1", "sample2", "sample5", "sample6"],
                "condition": ["control", "control", "treatment", "treatment"],
                "replicate": [1, 2, 1, 2],
                "geo_accession": ["GSM1", "GSM2", "GSM5", "GSM6"],
            }
        )

        expected_conditions = {"control", "treatment"}
        with pytest.raises(ValueError, match="Mismatch"):
            validate_data(counts_df, samples_df, expected_conditions)
