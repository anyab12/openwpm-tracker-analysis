"""
config.py — Central path configurations for openwpm-tracker-analysis.

Other modules import from this file so that changing a path or adding
a profile only requires editing one location.
"""
import os
from pathlib import Path

# Anchor: this file's location = project root
PROJECT_ROOT = Path(__file__).resolve().parent

# Internal paths (always relative to repo — reviewer never needs to touch these)
DATA_DIR    = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"
SAMPLE_RUN_DIR = RESULTS_DIR / "sample_run"

# Output mapping data (produced by build_mapping_tree.py)
RAW_CONCAT_CSV = DATA_DIR / "raw_concatenated_map.csv"
CANONICAL_CSV   = DATA_DIR / "canonical_domain_map.csv"
TREE_OUTPUT_CSV = DATA_DIR / "output_tree.csv"

# Output analysis results (produced by tree_http_analysis.py)
OUTPUT_REQUESTS_CSV  = RESULTS_DIR / "all_requests_classified.csv"
OUTPUT_SUMMARIES_CSV = RESULTS_DIR / "full_visit_summaries.csv"
OUTPUT_TRACKERS_CSV  = RESULTS_DIR / "tracker_prevalence_stats.csv"

# External paths (reviewer's environment varies — override via env var, sensible default)
# Reads two tracker databases and crawl_data input
DDG_ENTITIES_PATH = Path(os.environ.get(
    "DDG_ENTITIES_PATH",
    PROJECT_ROOT.parent / "tracker-radar" / "entities"
))
DISCONNECT_PATH = Path(os.environ.get(
    "DISCONNECT_PATH",
    PROJECT_ROOT.parent / "disconnect-tracking-protection" / "entities.json"
))
DB_PATH = Path(os.environ.get(
    "OPENWPM_DB_PATH",
    PROJECT_ROOT.parent / "crawl-data-6.15.sqlite" # move to folder? / "crawl_data" / 
))

# Ensure output directories exist at import time
for d in (DATA_DIR, RESULTS_DIR, SAMPLE_RUN_DIR):
    d.mkdir(parents=True, exist_ok=True)