#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import re
import os 

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from rnaseq.io_setup import load_counts , load_samples

def library_size(df):
    """
    Docstring for library_size
    
    :param pd.DataFrame df: DataFrame containing gene expression counts.
    :return: Series with the sum of counts for each sample (column).
    """
    return df.sum(axis=0) # series with library sizes

def barplot(counts_df: pd.DataFrame, samples_df: pd.DataFrame, output_file: str) -> None:
    """
    Generate a bar plot of library sizes for each sample.
    
    :param pd.DataFrame counts_df: DataFrame containing gene expression counts.
    :param pd.DataFrame samples_df: DataFrame containing sample annotations.
    :param str output_file: Path to save the output plot image.
    """

    lib_sizes = library_size(counts_df)
    lib_sizes_df = pd.DataFrame({
        'sample_id': lib_sizes.index,
        'library_size': lib_sizes.values
    })

    # Merge with samples_df to get conditions
    merged_df = lib_sizes_df.merge(samples_df[['sample_id', 'condition']], on='sample_id')

    plt.figure(figsize=(10, 6))
    sns.barplot(data=merged_df, x='sample_id', y='library_size', hue='condition')
    plt.xticks(rotation=90)
    plt.title('Library Sizes per Sample')
    plt.ylabel('Library Size (Total Counts)')
    plt.xlabel('Sample ID')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

def zero_count_genes(df: pd.DataFrame , axis=0):
    """
    Count the number of zero-count entities along a given axis.

    If axis = 0, counts the number of samples whose total count is zero.
    If axis = 1, counts the number of genes whose total count across all samples is zero.

    :param pd.DataFrame df: DataFrame containing gene expression counts
                            (genes x samples).
    :param int axis: Axis along which to perform the check.
                    0 = samples (columns),
                    1 = genes (rows).
    :return: Number of entities (samples or genes) with zero total counts.
    :rtype: int
    """
    zero_count_genes = (df.sum(axis=axis) == 0).sum()
    return zero_count_genes

def zero_fraction(df: pd.DataFrame , axis=0):
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
    axis : int
        Reduction axis used to compute totals:
          - axis=0 -> evaluate samples (columns)
          - axis=1 -> evaluate genes (rows)

    Returns
    -------
    float
        Percentage (0–100) of samples (axis=0) or genes (axis=1) whose total count equals 0.
    """
    if axis not in (0, 1):
        raise ValueError("axis must be 0 (samples/columns) or 1 (genes/rows)")
    
    zero_count = (df.sum(axis=axis) == 0).sum()
    # axis=0 -> we get one total per column -> number of entities = n_samples
    # axis=1 -> we get one total per row    -> number of entities = n_genes
    total_entities = df.shape[1] if axis == 0 else df.shape[0]

    return (zero_count / total_entities) * 100

def plot_zero_count_genes(counts_df: pd.DataFrame, output_file: str) -> None:
    """
    Generate a plot showing the number of zero-count genes.
    
    :param pd.DataFrame counts_df: DataFrame containing gene expression counts.
    :param str output_file: Path to save the output plot image.
    """
    zero_count = zero_count_genes(counts_df)
    total_genes = counts_df.shape[0]
    
    plt.figure(figsize=(6, 4))
    plt.bar(['Zero Count Genes', 'Non-Zero Count Genes'], [zero_count, total_genes - zero_count], color=['red', 'green'])
    plt.title('Zero Count Genes')
    plt.ylabel('Number of Genes')
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

def expressed_gene(counts_df: pd.DataFrame) -> pd.DataFrame:
    """
    Docstring for expressed_Gene
    
    :param counts_df: Description
    :type counts_df: pd.DataFrame

    return:
    A dataframe with expressed genes
    """
    expressed_genes = counts_df[counts_df.sum(axis=1) != 0]
    return expressed_genes

def log_transform(counts_df, base="log1p"):
    """
    Docstring for log_transform
    
    :param counts_df: Description
    :type counts_df: pd.DataFrame
    :param base: Description
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

def plot_log_transformed_df(log_counts_df : pd.DataFrame , title='Distribution of log-transformed counts per sample',  output_dir: str ="output/qc"):
    """
    Docstring for plot_log_transformed_df
    :param log_df: Description
    :type log_df: pd.DataFrame
    :param output_dir: Description
    :type output_dir: str
    return
    A boxplot of log-transformed counts per sample
    """

    plt.figure(figsize=(6,4))
    plt.boxplot(log_counts_df.values,tick_labels=log_counts_df.columns)
    plt.xticks(rotation=90)
    plt.ylabel("log(count + 1)")
    plt.title(f'{title}')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/{title}.png')
    plt.close()

def correlation(log_counts_df: pd.DataFrame, samples_df : pd.DataFrame, method='pearson' , title='Sample_Correlation_Heatmap', output_dir='output/qc'):
    """
    Generate a heatmap of sample correlations.
    
    :param pd.DataFrame counts_df: DataFrame containing gene expression counts.
    :param str output_dir: Path to save the output heatmap image.
    """

    corr_df = log_counts_df.corr(method=method)

    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_df, annot=True, fmt=".2f", cmap='coolwarm', square=True)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/{title}.png')
    plt.close()

    return corr_df

def plot_sample_correlation(corr_df: pd.DataFrame,output_file: str,title: str = "Sample-sample correlation (log-counts)") -> None: 
    """
    Plot and save a heatmap of the sample-sample correlation matrix.

    Parameters
    ----------
    corr_df : pd.DataFrame
        Square correlation matrix (samples x samples).
    output_file : str
        Path to save the figure.
    title : str
        Plot title.
    """  

    fig, ax = plt.subplots(figsize=(8, 8))
    im = ax.imshow(corr_df.values, cmap='coolwarm', vmin=-1, vmax=1)
    ax.set_xticks(range(len(corr_df.columns)))
    ax.set_yticks(range(len(corr_df.index)))
    ax.set_xticklabels(corr_df.columns, rotation=90)
    ax.set_yticklabels(corr_df.index)

    ax.set_title(title)

    cbar = plt.colorbar (im, ax=ax , fraction=0.046, pad=0.04)
    cbar.set_label('Correlation')

    plt.tight_layout()
    plt.savefig(f'{output_file}+{title}.png')
    plt.close()


def qc_all(counts_file: str, samples_file: str, pattern: str) -> None:
    """
    Perform all QC steps and generate plots.

    Parameters
    ----------
    counts_file : str
        Path to the counts matrix file.
    samples_file : str
        Path to the sample annotation file.
    pattern : str
        Regex pattern to extract biological sample IDs.
    """

    counts_df, sample_ids = load_counts(counts_file, pattern)
    samples_df = load_samples(samples_file, sample_ids)


    # Ensure sample_id is aligned to counts columns
    meta_cols = ["sample_id", "condition", "replicate",'geo_accession']

    # basics metrics 
    meta = samples_df[meta_cols].copy()
    meta = meta.set_index("sample_id")
    meta = meta.loc[counts_df.columns] # alignement 


    librarysize = library_size(counts_df)
    zero_fraction = (counts_df.eq(0).mean(axis=0) * 100.0)
    n_genes_expressed = counts_df.gt(0).sum(axis=0)


    qc_df = meta.copy()
    qc_df["library_size"] = librarysize
    qc_df["zero_fraction"] = zero_fraction
    qc_df["n_genes_expressed"] = n_genes_expressed

    qc_df.index.name = "sample_id"  # name the index column
    # Final sanity checks
    if qc_df.isna().any().any():
        raise ValueError("QC table contains missing values after alignment/metrics.")
    if not qc_df.index.is_unique:
        raise ValueError("QC table index (sample_id) is not unique.")

    return qc_df

def save_qc_table(qc_df: pd.DataFrame, output_dir: str , filename :str) -> None:
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

if __name__ == "__main__":
    counts_file = 'data/GSE60450_Lactation-GenewiseCounts.txt'
    samples_file = 'data/GSE60450_series_matrix.txt'
    output_dir = 'output/qc'
    pattern = '^MCL1-([A-Z]{2})_'  # Pattern to extract biological sample IDs

    qc_df = qc_all(counts_file, samples_file, pattern)
    print(qc_df)
    save_qc_table(qc_df, 'output/qc', 'qc_table.csv')

