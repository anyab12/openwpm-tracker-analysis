# OpenWPM Tracker Analysis

This repository contains Python analysis scripts and selected CSV artifacts
for a CSC Summer Research 2026 project using OpenWPM crawl data.


## Project Goal

The project analyzes HTTP requests collected from OpenWPM browser crawls and
classifies network requests as first-party or third-party. Classification is
based on both technical domain comparison and a domain-to-entity hierarchy.


## Repository Structure

docs/
  Notes, workflow documentation, and methodology notes.

data/
  Selected CSV inputs and mapping artifacts used by the analysis pipeline.

src/scripts/
  Python analysis scripts. Import from src/utilities as needed.

src/utilities/
  Python utility scripts. Contain constants and helper functions.

results/
  Generated output CSVs from analysis runs. Only selected safe outputs should be committed.

results/sample_run/
  Optional small sample outputs that can be shared for reproducibility or inspection.


## Main Scripts

src/scripts/build_mapping_tree.py
  Builds domain/entity hierarchy from domain mapping sources and manual override rules.

src/scripts/tree_http_analysis.py
  Loads OpenWPM crawl data, classifies HTTP requests, and exports
  request-level visit-level, and tracker-prevalence summaries.


## Included CSV Files

data/ folder includes mapping artifacts such as
  - raw_concatenated_map.csv of raw domain-entity databases
  - canonical_domain_map.csv of preprocessed domain-entity map
  - output_tree.csv of exported tree map

results/ folder includes output analysis results and stats
  - all_requests_classified.csv
  - full_visit_summaries.csv
  - tracker_prevalence_stats.csv
  - sample_run/ folder may include selected derived outputs from small test run

## Excluded Files

Raw OpenWPM crawl data bases are intentionally excluded from repository,
as well as certain CSV output files containing potentially sensitive information.
Environment runtime files, logs, large generated outputs, and other crawl data
are also excluded.


## Setup

Clone this repo alongside the two tracker database sources:

    git clone https://github.com/duckduckgo/tracker-radar.git
    git clone https://github.com/disconnectme/disconnect-tracking-protection.git
    git clone https://github.com/anyab12/openwpm-tracker-analysis.git
    

Enter project directory and install required modules. Also can be installed in .venv.

    cd openwpm-tracker-analysis
    pip install -r requirements.txt


Place your OpenWPM crawl SQLite data file one level up in sibling directory (`../crawl_data/crawl-data-6.15.sqlite`)
OR set `OPENWPM_DB_PATH` to point elsewhere:
    export OPENWPM_DB_PATH=/your/path/to/crawl.sqlite


## Run
    python3 -m src.scripts.build_mapping_tree
    python3 -m src.scripts.tree_http_analysis

Check output CSV files, specifically canonical_domain_map and output_tree, after building tree
to ensure correct mapping before moving to classification.


## Related Project

For the rest of the OpenWPM tracking analysis research work, see Graham Fink's repository at
https://github.com/gfink15/Tracking-Analysis.git and clone alongside this one. Graham's analysis
scripts make heavy use of the mapping tree and classification algorithms from this
openwpm-tracker-analysis repository. To run some of his basic analysis scripts, specifically trackers.py
and cookies.py, be sure to clone this repository and run build_mapping_tree.py first.