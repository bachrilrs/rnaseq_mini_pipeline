import re
import pandas as pd
import numpy as np


def load_counts(file_path: str, pattern: str , sep='\t'):
    """
    Load RNA-seq count data from a tab-delimited file and process sample IDs.

    Parameters:
    - file_path: str : Path to the input file.
    - pattern: str : Regular expression pattern to extract biological sample IDs.

    Returns:
    - pd.DataFrame : Processed DataFrame with gene IDs as index and biological sample IDs as columns.
    """
    df = pd.read_csv(file_path, sep=sep)

    # Drop unnecessary columns and rename gene ID column
    df.drop(columns=['Length'], inplace=True)
    df.rename(columns={"EntrezGeneID": "gene_id"}, inplace=True)
    df.index = df['gene_id']
    df.drop(columns='gene_id', inplace=True)

    # Extract biological sample IDs using the provided pattern
    ids = []
    for id in df.columns:
        r_match = re.search(pattern, id)
        if r_match:
            ids.append(r_match.group(1))  # Add the biological ID of the sample
        else:
            raise ValueError(f"The following sample {id} does not match the expected pattern {pattern}.")

    # Ensure no duplicate sample IDs
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate sample IDs found after extraction.")

    df.columns = ids

    df = df.astype(np.int64)
    
    if df.isna().sum().sum() > 0:
        raise ValueError("Missing values found in the DataFrame after processing.")
    if not df.index.is_unique:
        raise ValueError("Gene IDs are not unique in the DataFrame index.")
    return df , ids

def load_samples(sample_file: str, sample_ids: list[str], quoted_pattern: str = r'".*?"') -> pd.DataFrame:
    """
    Load and construct a clean sample annotation table from a GEO series_matrix file.

    Parameters
    ----------
    sample_file : str
        Path to the GEO series_matrix file.
    sample_ids : list[str]
        Biological sample IDs extracted from the count matrix (e.g. DG, DH, ..., LF).
        These are used as the primary sample identifiers.
    quoted_pattern : str
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
    geo_accessions = None
    with open(sample_file , 'r') as fh:
        for line in fh:
            if line.startswith('!Series_sample_i'):
                matches = re.findall(quoted_pattern, line)
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
    
    replicate_counter = {'virgin' : 0,'lactation' : 0}

    for sid in sample_ids:
        if sid.startswith("D"):
            cond = 'virgin'
        elif sid.startswith('L'):
            cond = 'lactation'
        else:
            raise ValueError(f"condition from sample_id: {sid} not known")

        replicate_counter[cond] += 1

        condition.append(cond)
        replicate.append(replicate_counter[cond])

    samples_df = pd.DataFrame({
        "sample_id": sample_ids,
        "condition": condition,
        "replicate": replicate,
        "geo_accession": geo_accessions
    })

    if samples_df.isna().any().any():
        raise ValueError("Missing values detected in samples table.")

    if not samples_df["sample_id"].is_unique:
        raise ValueError("sample_id column is not unique.")

    return samples_df

if __name__ == '__main__':

    file_path = 'data/GSE60450_Lactation-GenewiseCounts.txt'
    sample_file = 'data/GSE60450_series_matrix.txt'
    pattern = '^MCL1-([A-Z]{2})_'  # Pattern to extract biological sample IDs
    df , ids = load_counts(file_path, pattern)
    
    pat_geo = r'".*?"'

    samples = load_samples(sample_file, ids)

    df.to_csv('data/counts.csv' ,index=True)
    samples.to_csv('data/samples.csv' ,index=False)
    print(df[df.sum(axis=1) != 0].shape[0])
    print(df.shape[0])

    print("Counts and samples loaded successfully.")