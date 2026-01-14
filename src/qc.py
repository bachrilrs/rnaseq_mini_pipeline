#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os 


from io_setup import *

def library_size(df):
    """
    Docstring for library_size
    
    :param pd.DataFrame df: DataFrame containing gene expression counts.
    :return: Series with the sum of counts for each sample (column).
    """
    return df.sum(axis=0) # series with library sizes

def zero_fraction(counts_df: pd.DataFrame , axis=0):
    """
    Compute the percentage of entities whose total count is zero.

    This function checks which entities have a total count of 0 after summing along `axis`.
    Note: `axis` indicates the dimension being reduced:
      - axis=0 reduces rows -> returns one value per column (samples)
      - axis=1 reduces columns -> returns one value per row (genes)

    Parameters
    ----------
    df : pd.DataFrame
        Count matrix with shape (n_genes, n_samples).
    
    Returns
    -------
    float
        Percentage (0–100) of samples (axis=0) or genes (axis=1) whose total count equals 0.
    """
    return (counts_df.eq(0).mean(axis=0) * 100)

def expressed_gene(counts_df: pd.DataFrame) -> pd.DataFrame:
    """
    Docstring for expressed_Gene
    
    param: counts_df: 
    
    return:
    A dataframe with expressed genes
    """
    return counts_df.gt(0).sum(axis=0)

def log_transform(counts_df, base="log1p"):
    """
    Log-transform counts.
    
    :param counts_df: 
    :type counts_df: pd.DataFrame
    :param base: 
    :type base: str

    return:
    A dataframe with log-transformed counts
    """
    if base == "log1p":
        log_df = np.log1p(counts_df)
        return log_df
    elif base == "log2":
        log_df = np.log2(counts_df+1) # avoid log(0)--> -inf
        return log_df
    elif base == "log10":
        log_df = np.log10(counts_df+1) # avoid log(0)--> -inf
        return log_df
    else:
        raise ValueError("Unsupported log base. Use 'log1p' 'log10' or 'log2'.")

def plot_log_boxplot(counts_df: pd.DataFrame,output_dir: str) -> None:
    os.makedirs(output_dir, exist_ok=True)

    log_df = log_transform(counts_df)

    plt.figure(figsize=(8, 4))
    plt.boxplot(log_df.values, labels=log_df.columns)
    plt.xticks(rotation=90)
    plt.ylabel("log(count + 1)")
    plt.title("Log-transformed count distribution")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "log_counts_boxplot.png"))
    plt.close()

def plot_library_size(counts_df: pd.DataFrame,samples_df: pd.DataFrame,output_dir: str) -> None:
    os.makedirs(output_dir, exist_ok=True)

    libsize = library_size(counts_df)
    plot_df = pd.DataFrame({"sample_id": libsize.index,"library_size": libsize.values}).merge(samples_df[["sample_id", "condition"]],on="sample_id")

    plt.figure(figsize=(10, 6))
    sns.barplot(data=plot_df, x="sample_id", y="library_size", hue="condition")
    plt.xticks(rotation=90)
    plt.title("Library size per sample")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "library_size.png"))
    plt.close()


def plot_sample_correlation(counts_df: pd.DataFrame,output_dir: str) -> pd.DataFrame:
    os.makedirs(output_dir, exist_ok=True)

    corr_df = log_transform(counts_df).corr()

    plt.figure(figsize=(8, 8))
    sns.heatmap(corr_df, cmap="coolwarm", square=True)
    plt.title("Sample–sample correlation")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "sample_correlation.png"))
    plt.close()

    return corr_df

def build_qc_table(counts_df, samples_df) -> pd.DataFrame:
    """
    Build a per-sample QC summary table.

    Parameters
    ----------
    counts_df : pd.DataFrame
        DataFrame containing gene expression counts.
    samples_df : pd.DataFrame
        DataFrame containing sample annotations.
    Returns
    -------
    pd.DataFrame
        QC summary table with metrics for each sample.
    """

    samples_df = samples_df.set_index("sample_id").loc[counts_df.columns]

    qc_df = samples_df.copy()
    qc_df["library_size"] = library_size(counts_df)
    qc_df["zero_fraction"] = zero_fraction(counts_df)
    qc_df["expressed_gene"] = expressed_gene(counts_df)

    if qc_df.isna().any().any():
        raise ValueError("QC table contains missing values")

    return qc_df

def save_qc_table(qc_df: pd.DataFrame,output_dir: str,filename: str = "qc_table.csv") -> None:
    """
    Save the QC table to a CSV file.

    Parameters
    ----------
    qc_df : pd.DataFrame
        DataFrame containing QC metrics for each sample.
    output_file : str
        Path to save the QC table CSV file.
    """
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, filename) # join the directory and filename
    
    qc_df.to_csv(out_path, index=True)

def qc_all(counts_df: pd.DataFrame, samples_df: pd.DataFrame, output_dir: str) -> pd.DataFrame:
    """
    Perform all QC analyses and generate outputs.

    Parameters
    ----------
    counts_df : pd.DataFrame
        DataFrame containing gene expression counts.
    samples_df : pd.DataFrame
        DataFrame containing sample annotations.
    output_dir : str
        Directory to save QC output files.  
    """

    qc_dir = os.path.join(output_dir, "qc")

    plot_library_size(counts_df, samples_df, qc_dir)
    plot_log_boxplot(counts_df, qc_dir)
    plot_sample_correlation(counts_df, qc_dir)

    qc_df = build_qc_table(counts_df, samples_df)
    save_qc_table(qc_df, output_dir)

    return qc_df
