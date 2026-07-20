# OpenWPM Tracker Analysis

This repository contains Python analysis scripts and selected CSV artifacts
for a CSC Summer Research 2026 project using OpenWPM crawl data.


## Project Goal

The project analyzes HTTP requests collected from OpenWPM browser crawls and
classifies network requests as first-party or third-party. Classification is
based on both technical domain comparison and a domain-to-entity hierarchy.


## Repository Structure

scripts/
  Python analysis scripts.

data/
  Selected CSV inputs and mapping artifacts used by the analysis pipeline.

results/
  Generated output CSVs from analysis runs. Only selected safe outputs
  should be committed.

results/sample_run/
  Optional small sample outputs that can be shared for reproducibility
  or inspection.

docs/
  Notes, workflow documentation, and methodology notes.


## Main Scripts

scripts/build_mapping_tree.py
  Builds domain/entity hierarchy from domain mapping sources and manual
  override rules.

scripts/tree_http_analysis.py
  Loads OpenWPM crawl data, classifies HTTP requests, and exports request-level
  visit-level, and tracker-prevalence summaries.


## Included CSV Files

data/ folder includes mapping artifacts such as
  raw_concatenated_map.csv of raw domain-entity databases
  canonical_domain_map.csv of preprocessed domain-entity map
  output_tree.csv of exported tree map

results/ folder includes output analysis results and stats
  all_requests_classified.csv
  full_visit_summaries.csv
  tracker_prevalence_stats.csv
  sample_run/ folder may include selected derived outputs from small test run

## Excluded Files

Raw OpenWPM crawl data bases are intentionally excluded from repository,
as well as certain CSV output files containing potentially sensitive information.
Environment runtime files, logs, large generated outputs, and other crawl data
are also excluded.


## Running the Analysis

From the repository root run:
  python3 scripts/tree_http_analysis.py

Script expects raw OpenWPM database files to exist outside this repository.
Update DB_PATH constant in file, or add as argument in terminal command, if
using a different crawl database.