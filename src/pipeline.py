#!/usr/bin/env python3

from io_setup import *
from validation import *
from qc import * 
import yaml
from pathlib import Path
from pprint import pprint

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

config = load_config("config.yaml")
validate_config_structure(config)

counts_cfg = config["input"]["counts"]
samples_cfg = config["input"]["samples"]

counts_df = load_counts_tsv(file_path=counts_cfg["path"], pattern=counts_cfg["counts_pattern"], sep=counts_cfg.get("sep","\t"),
        gene_id_candidates=counts_cfg.get("gene_id_candidates", ["EntrezGeneID", "GeneID", "gene_id"]))
samples_df = load_samples_geo_series(sample_file=samples_cfg["path"], counts_df=counts_df , samples_pattern=samples_cfg["samples_pattern"])


validate_counts(counts_df)
validate_samples(samples_df, expected_conditions=set(samples_cfg["expected_conditions"]))




def main():
    # TODO: implement main function if needed
    
    pass



