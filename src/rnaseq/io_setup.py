#!/usr/bin/env python3
import re
import pandas as pd
import numpy as np

def normalize_and_validate_counts(counts_df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate counts matrix canonical format:
    - index = gene_id (unique, non-null)
    - columns = sample_id (unique, non-null)
    - values = integers >= 0
    - no missing values
    """
    if counts_df.index.name is None: 
        raise ValueError("counts_df index must be gene_id (index name is None)")

    if counts_df.index.isna().any():
        raise ValueError("counts_df contains missing gene_id in index")

    if not counts_df.index.is_unique:
        raise ValueError("Gene IDs are not unique in counts_df index")

    if counts_df.columns.isna().any():
        raise ValueError("counts_df contains missing sample_id in columns")

    if len(set(counts_df.columns)) != len(counts_df.columns):
        raise ValueError("Duplicate sample_id found in counts_df columns")

    if counts_df.isna().any().any():
        raise ValueError("Missing values found in counts_df")

    # ensure integer + non-negative
    if not all(pd.api.types.is_integer_dtype(counts_df[c]) for c in counts_df.columns): # ensure all columns are integer dtype
        raise ValueError("Counts must be integer-valued")

    if (counts_df < 0).any().any():
        raise ValueError("Counts must be non-negative")

    return counts_df

def normalize_and_validate_samples(samples_df: pd.DataFrame, counts_df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize and validate a samples DataFrame against counts_df.

    Enforces:
    - required columns
    - no missing values
    - unique sample_id
    - replicate is int and >= 1
    - exact match with counts_df.columns
    - row order aligned with counts_df.columns
    """
    required_cols = {"sample_id", "condition", "replicate"}
    missing = required_cols - set(samples_df.columns)
    if missing:
        raise ValueError(f"Missing required columns in samples table: {missing}")

    if samples_df.isna().any().any():
        raise ValueError("Missing values detected in samples table")

    if not samples_df["sample_id"].is_unique:
        raise ValueError("sample_id column is not unique")

    if not pd.api.types.is_integer_dtype(samples_df["replicate"]):
        raise ValueError("replicate column must be integer-valued")

    if (samples_df["replicate"] < 1).any():
        raise ValueError("replicate values must be >= 1")

    counts_samples = list(counts_df.columns)
    meta_samples = list(samples_df["sample_id"])

    if set(counts_samples) != set(meta_samples): # exact match
        missing_in_meta = set(counts_samples) - set(meta_samples)
        extra_in_meta = set(meta_samples) - set(counts_samples)
        raise ValueError(
            "Mismatch between counts and samples. "
            f"Missing in samples: {sorted(missing_in_meta)}; "
            f"Extra in samples: {sorted(extra_in_meta)}"
        )

    # reorder rows to match counts_df columns
    samples_df = samples_df.set_index("sample_id").loc[counts_samples].reset_index()

    return samples_df

def load_counts_tsv(file_path: str, pattern: str , sep='\t',gene_id_candidates = ["EntrezGeneID", "GeneID", "gene_id"]) -> pd.DataFrame:
    """
    Load RNA-seq count data from a tab-delimited file and process sample IDs.

    Parameters:
    - file_path: str : Path to the input file.
    - pattern: str : Regular expression pattern to extract biological sample IDs.
    - sep: str : Delimiter used in the input file (default is tab).
    - gene_id_candidates: list[str] : List of possible gene ID column names. Can precise different gene_id if needed.
    Returns:
    - pd.DataFrame : Processed DataFrame with gene IDs as index and biological sample IDs as columns.
    """

    counts_df = pd.read_csv(file_path, sep=sep, index_col=0)

    gene_id_candidates = list(gene_id_candidates) # ensure it's a list if not already
    gene_id_col = next((c for c in gene_id_candidates if c in counts_df.columns), None)
    if gene_id_col is None:
        raise ValueError(
            f"No gene identifier column found. Expected one of {gene_id_candidates}. You may need to specify the correct gene_id_candidates parameter."
        )
    

    # Drop unnecessary columns and rename gene ID column
    # drop optional annotation columns
    for col in ["Length", "Chr", "Start", "End", "Strand"]:
        if col in counts_df.columns:
            counts_df.drop(columns=col, inplace=True)
    
    # set gene_id as index
    counts_df = counts_df.set_index(gene_id_col)
    counts_df.index.name = "gene_id"

    # Extract biological sample IDs using the provided pattern

    if pattern is None:
        raise ValueError("A pattern must be provided to extract sample IDs from column names.")
    sample_ids = []
    for col in counts_df.columns:  # skip the first column if it's gene_id
        r_match = re.search(pattern, col)
        if not r_match:
            raise ValueError(f"The following sample {col} does not match the expected pattern {pattern}.")
        sample_ids.append(r_match.group(1))

    # Ensure no duplicate sample IDs
    if len(set(sample_ids)) != len(sample_ids):
        raise ValueError("Duplicate sample IDs found after extraction.")
    
    counts_df.columns = sample_ids
    counts_df = counts_df.astype(np.int64)
    return normalize_and_validate_counts(counts_df)

def load_samples_csv(sample_file: str, counts_df: pd.DataFrame, separator: str = ",") -> pd.DataFrame:
    samples_df = pd.read_csv(sample_file, sep=separator)
    return normalize_and_validate_samples(samples_df, counts_df)

def load_samples_geo_series(sample_file: str, counts_df: pd.DataFrame,samples_pattern: str = r'".*?"')-> pd.DataFrame:
    """
    Load and construct a clean sample annotation table from a GEO series_matrix file.

    Parameters
    ----------
    sample_file : str
        Path to the GEO series_matrix file.
    sample_ids : list[str]
        Biological sample IDs extracted from the count matrix (e.g. DG, DH, ..., LF).
        These are used as the primary sample identifiers.
    samples_pattern : str
        Regex pattern used to extract quoted fields from GEO lines.

    Returns
    -------
    pd.DataFrame
        A DataFrame with columns:
        - sample_id
        - condition
        - replicate
        - geo_accession
    """

    sample_ids = list(counts_df.columns)
    
    geo_accessions = None

    with open(sample_file , 'r') as fh:
        for line in fh: # parse series_matrix file to find Series_sample_id line
            if line.startswith('!Series_sample_i'):
                matches = re.findall(samples_pattern, line)
                if not matches:
                    raise ValueError("No GEO accessions found in Series_sample_id line.")
                if len(matches) == 1:
                    geo_accessions = matches[0].replace('"', '').strip().split()
                else:
                    geo_accessions = [m.replace('"','').strip() for m in matches]
                break

    if geo_accessions is None:
        raise ValueError("Series_sample_id line not found in series_matrix file.")
    
    if len(geo_accessions) != len(sample_ids):
        raise ValueError(
            "Number of GEO accessions does not match number of sample IDs " f"({len(geo_accessions)} vs {len(sample_ids)})")

    if len(set(sample_ids)) != len(sample_ids):
        raise ValueError("Duplicate sample_ids provided.")

    condition = []
    replicate = []
    replicate_counter = {'virgin' : 0,'lactation' : 0} # initialize counters

    for sid in sample_ids: # infer condition and replicate from sample_id
        if sid.startswith("D"): # virgin
            cond = 'virgin'
        elif sid.startswith('L'): # lactation
            cond = 'lactation'
        else:
            raise ValueError(f"condition from sample_id: {sid} not known")

        replicate_counter[cond] += 1 # increment counter

        condition.append(cond) # assign condition
        replicate.append(replicate_counter[cond]) # assign replicate number

    samples_df = pd.DataFrame({
        "sample_id": sample_ids,
        "condition": condition,
        "replicate": replicate,
        "geo_accession": geo_accessions
    })
    return normalize_and_validate_samples(samples_df , counts_df)
