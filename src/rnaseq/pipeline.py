#!/usr/bin/env python3
import yaml
import time
from rnaseq.io_setup import *
from rnaseq.validation import *
from rnaseq.qc import * 
from rnaseq.db_setup import *
from pathlib import Path


def load_config(config_path: str) -> dict:
    """
    Load a YAML configuration file and return it as a dictionary.

    Parameters
    ----------
    config_path : str
        Path to the YAML configuration file.

    Returns
    -------
    dict
        Parsed configuration.
    """
    config_file = Path(config_path)

    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    if config_file.suffix not in {".yml", ".yaml"}:
        raise ValueError("Config file must have .yml or .yaml extension")

    with open(config_file, "r") as fh:
        try:
            config = yaml.safe_load(fh)
        except yaml.YAMLError as e:
            raise ValueError(f"Error while parsing YAML config: {e}")

    if not isinstance(config, dict):
        raise ValueError("Config file must define a YAML mapping (dictionary)")

    return config

def validate_config_structure(config: dict) -> None:
    required_sections = {"run", "input", "qc", "output"}

    missing = required_sections - set(config.keys())
    if missing:
        raise ValueError(f"Missing required config sections: {missing}")

def run_pipeline() -> None:
    """
    Run the RNA-seq QC pipeline based on a configuration file.

    """
    config = load_config("/app/config.yaml")
    validate_config_structure(config)

    counts_cfg = config["input"]["counts"]
    samples_cfg = config["input"]["samples"]

    counts_df = load_counts_tsv(file_path=counts_cfg["path"], pattern=counts_cfg["counts_pattern"], sep=counts_cfg.get("sep","\t"),
            gene_id_candidates=counts_cfg.get("gene_id_candidates", ["EntrezGeneID", "GeneID", "gene_id"]))
    samples_df = load_samples_geo_series(sample_file=samples_cfg["path"], counts_df=counts_df , samples_pattern=samples_cfg["samples_pattern"])


    validate_counts(counts_df)
    validate_samples(samples_df, expected_conditions=set(samples_cfg["expected_conditions"]))

    qc_all(counts_df, samples_df, output_dir=config["output"]["base_dir"])

def main():
    """
    Main function to run the RNA-seq QC pipeline based on a configuration file.
    Parameters: None
    """
    try:
        print("Starting Pipeline")
        run_pipeline()
        
        # Supprime le message "Waiting 10 minutes"
        print("Exporting results to PostgreSQL...")
        run_database()
        
        print("Pipeline execution completed successfully.")
        # Le script va maintenant s'arrêter ici et rendre la main à entrypoint.sh

    except Exception as e:
        print(f"Error occurred: {e}")
        # Optionnel : ne pas mettre de sleep ici non plus pour voir l'erreur de suite

if __name__ == "__main__":
    main()