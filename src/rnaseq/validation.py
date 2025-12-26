#!/usr/bin/env python3
import pandas as pd


def validate_counts(df: pd.DataFrame) -> None:
    """
    Validate the counts DataFrame for expected structure and content.
    Args:
        df (pd.DataFrame): DataFrame containing gene expression counts.
    Raises:
        ValueError: If any validation check fails.
    """
    # Check for missing values
    if df.isna().any().any():
        raise ValueError("Missing values found in the DataFrame.")

    # Check for unique gene IDs
    if not df.index.is_unique:
        raise ValueError("Gene IDs are not unique in the DataFrame index.")

    # Check that all counts are non-negative integers
    if not (df.dtypes == int).all():
        raise ValueError("Counts must be integer-valued.")
    
    if (df < 0).any().any():
        raise ValueError("Counts must be non-negative.")
    
def validate_samples(df: pd.DataFrame, expected_conditions: set) -> None:
    """
    Validate the samples DataFrame for expected structure and content.
    Args:
        df (pd.DataFrame): DataFrame containing sample annotations.
        expected_conditions (set): Set of expected condition names.
    Raises:
        ValueError: If any validation check fails.
    """
    # Check for required columns
    required_columns = {'sample_id', 'condition', 'replicate' , 'geo_accession'}
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns in samples DataFrame: {missing}")

    # Check for unique sample IDs
    if not df['sample_id'].is_unique:
        raise ValueError("Sample IDs are not unique in the samples DataFrame.")

    # Check that all expected conditions are present
    actual_conditions = set(df['condition'].unique())

    # check that conditions match expected conditions
    if actual_conditions != expected_conditions:
        raise ValueError(f"Conditions in samples DataFrame do not match expected conditions. "
                         f"Expected: {expected_conditions}, Found: {actual_conditions}")

    # check that each condition has at least two samples
    n_per_cond = df.groupby("condition").size()
    if (n_per_cond < 2).any():
        raise ValueError(f"Each condition must have at least two samples. Found: {n_per_cond.to_dict()}")
    
    
    # check that replicate numbers are consecutive starting from 1 for each condition
    if (df["replicate"] < 1).any():
        raise ValueError("Replicate values must be >= 1.")

    for cond , sub in df.groupby("condition"):
        replicates = sorted(sub["replicate"].tolist())
        expected = list(range(1, len(replicates)+1))
        if replicates != expected:
            raise ValueError(f"Replicate numbers for condition '{cond}' must be {expected} "
                             f"Found: {replicates}")

def validate_data(counts_df: pd.DataFrame, samples_df: pd.DataFrame, expected_conditions: set) -> None:
    """
    Validate both counts and samples DataFrames.
    Args:
        counts_df (pd.DataFrame): DataFrame containing gene expression counts.
        samples_df (pd.DataFrame): DataFrame containing sample annotations.
        expected_conditions (set): Set of expected condition names.
    Raises:
        ValueError: If any validation check fails.
    """
    validate_counts(counts_df)
    validate_samples(samples_df, expected_conditions)
    counts_samples = set(counts_df.columns) # count column names must be sample_ids column in samples_df
    meta_samples = set(samples_df['sample_id']) 

    if counts_samples != meta_samples: # we check for exact match
        missing_in_meta = counts_samples - meta_samples
        extra_in_meta = meta_samples - counts_samples
        raise ValueError(
            "Mismatch between counts columns and samples table. "
            f"Missing in samples: {sorted(missing_in_meta)}; Extra in samples: {sorted(extra_in_meta)}"
        )