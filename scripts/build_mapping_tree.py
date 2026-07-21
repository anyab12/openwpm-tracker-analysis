"""
Script: /home/anya/openwpm-tracker-analysis/build_mapping_tree.py

Author: Anya Barringer, aided by Claude Sonnet 4.6 and
        Codestral through Furman University BoodleBox

Container:  Part of CSC Summer Research 2026 Project
            "Pervasive Online Third-Party Tracking: A Measurement Study"
            with Graham Fink, under Dr. Rebecca Drucker

Goal:   Builds domain-entity relationship hierarcy mapping tree from
        two tracker / domian mapping lists and a manually curated list.
        Outputs tree as .csv file to be loaded by other scripts for
        downstream data analysis, e.g. first- vs third-party classification.
"""



import os
import json
import logging
import pandas as pd
from collections import defaultdict
from bigtree import Node, Tree, dataframe_to_tree, tree_to_dataframe
from utilities.utils import normalize_string, strip_suffixes
from utilities.treemap_preprocessing_constants import MANUAL_OVERRIDES, ENTITY_NAME_REPLACEMENTS, PARENT_OVERRIDES


# --- CONSTANTS ---
DDG_ENTITIES_PATH = "/home/anya/tracker-radar/entities/"
DISCONNECT_PATH = "/home/anya/disconnect-tracking-protection/entities.json"
RAW_CONCAT_PATH = "data/raw_concatenated_map.csv"
CANONICAL_PATH = "data/canonical_domain_map.csv"
TREE_OUTPUT_CSV = "data/output_tree.csv"

# --- LOGGING SETUP ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s"
)
logger = logging.getLogger(__name__)



# =============================================================================
# (1) DATA LOADING
# =============================================================================
def load_ddg_entities(entities_dir: str) -> pd.DataFrame:
    """
    Loads domain-entity mappings from the DDG Tracker Radar entities/ folder.
    
    Each JSON file contains:
        - 'name': broader corporate label → used as parent_entity
        - 'displayName': more specific entity name → used as subsidiary_entity
        - 'properties': list of owned domains
    
    Args:
        entities_dir: Path to the tracker-radar/entities/ directory
    
    Returns:
        DataFrame with columns: domain, subsidiary_entity, parent_entity, source, priority
    """
    rows = []

    for filename in os.listdir(entities_dir):
        if not filename.endswith(".json"):
            continue

        filepath = os.path.join(entities_dir, filename)

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Skipping malformed file: {filename} — {e}")
            continue

        parent_entity = data.get("name", "").strip().lower()
        subsidiary_entity = data.get("displayName", "").strip().lower()
        domains = data.get("properties", [])

        if not parent_entity and not subsidiary_entity:
            logger.warning(f"Skipping file with no entity name: {filename}")
            continue

        for domain in domains:
            if not isinstance(domain, str):
                logger.warning(f"Non-string domain entry in {filename}: {domain}")
                continue

            clean_domain = domain.strip().lower()
            if not clean_domain:
                continue

            rows.append({
                "domain": clean_domain,
                "subsidiary_entity": subsidiary_entity,
                "parent_entity": parent_entity,
                "source": "ddg",
                "priority": 1
            })

    df = pd.DataFrame(rows, columns=[
        "domain", "subsidiary_entity", "parent_entity", "source", "priority"
    ])

    logger.info(f"DDG: loaded {len(df)} domain rows from {entities_dir}")
    return df

def load_disconnect_entities(disconnect_path: str) -> pd.DataFrame:
    """
    Loads domain-entity mappings from the Disconnect.me entities.json file.
    
    Structure:
        - Single JSON file with top-level 'entities' key
        - Each entity key is used as both subsidiary_entity and parent_entity
        - Domains pulled from both 'properties' and 'resources' lists
        - Duplicates across both lists are collapsed to one row per domain
    
    Args:
        disconnect_path: Path to the Disconnect.me entities.json file
    
    Returns:
        DataFrame with columns: domain, subsidiary_entity, parent_entity, source, priority
    """
    rows = []

    try:
        with open(disconnect_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.error(f"Could not load Disconnect file: {disconnect_path} — {e}")
        return pd.DataFrame(columns=[
            "domain", "subsidiary_entity", "parent_entity", "source", "priority"
        ])

    entities = data.get("entities", {})

    if not isinstance(entities, dict):
        logger.error(f"Unexpected structure in Disconnect file — 'entities' is not a dict")
        return pd.DataFrame(columns=[
            "domain", "subsidiary_entity", "parent_entity", "source", "priority"
        ])

    for entity_name, entity_info in entities.items():
        if not isinstance(entity_info, dict):
            logger.warning(f"Skipping malformed entity entry: {entity_name}")
            continue

        clean_entity = entity_name.strip().lower()
        if not clean_entity:
            logger.warning(f"Skipping entity with empty name")
            continue

        properties = entity_info.get("properties", [])
        resources = entity_info.get("resources", [])

        if not isinstance(properties, list):
            logger.warning(f"Non-list 'properties' for entity: {entity_name} — skipping properties")
            properties = []

        if not isinstance(resources, list):
            logger.warning(f"Non-list 'resources' for entity: {entity_name} — skipping resources")
            resources = []

        unique_domains = set()
        for domain in properties + resources:
            if not isinstance(domain, str):
                logger.warning(f"Non-string domain entry for entity {entity_name}: {domain}")
                continue
            clean_domain = domain.strip().lower()
            if clean_domain:
                unique_domains.add(clean_domain)

        for domain in unique_domains:
            rows.append({
                "domain": domain,
                "subsidiary_entity": clean_entity,
                "parent_entity": clean_entity,
                "source": "disconnect",
                "priority": 2
            })

    df = pd.DataFrame(rows, columns=[
        "domain", "subsidiary_entity", "parent_entity", "source", "priority"
    ])

    logger.info(f"Disconnect: loaded {len(df)} domain rows from {disconnect_path}")
    return df

def flatten_manual_overrides(overrides: dict) -> pd.DataFrame:
    """
    Flattens the hardcoded MANUAL_OVERRIDES dictionary into a DataFrame
    matching the canonical column schema.

    Args:
        overrides: MANUAL_OVERRIDES dictionary
            Dictionary structure: { domain: (subsidiary_entity, parent_entity) }

    Returns:
        DataFrame with columns: domain, subsidiary_entity, parent_entity, source, priority
    """

    rows = []

    for domain, (subsidiary_entity, parent_entity) in overrides.items():
        clean_domain = domain.strip().lower()
        clean_subsidiary = subsidiary_entity.strip().lower()
        clean_parent = parent_entity.strip().lower()

        if not clean_domain:
            logger.warning(f"Skipping MANUAL_OVERRIDES entry with empty domain: {domain}")
            continue
        if not clean_subsidiary and not clean_parent:
            logger.warning(f"Skipping MANUAL_OVERRIDES entry with no entity names: {domain}")
            continue

        rows.append({
            "domain":               clean_domain,
            "subsidiary_entity":    clean_subsidiary,
            "parent_entity":        clean_parent,
            "source":               "manual",
            "priority":             3
        })

    df = pd.DataFrame(rows, columns=[
        "domain", "subsidiary_entity", "parent_entity", "source", "priority"
    ])

    logger.info(f"Manual overrides: loaded {len(df)} domain rows")
    return df

def concatenate_sources(
    df_ddg: pd.DataFrame,
    df_disconnect: pd.DataFrame,
    df_manual: pd.DataFrame,
    export_path: str,
) -> pd.DataFrame:
    """
    Concatenates the three source DataFrames into a single raw combined DataFrame
    and exports to CSV for inspection before preprocessing.

    Args:
        df_ddg:        Output of load_ddg_entities()
        df_disconnect: Output of load_disconnect_entities()
        df_manual:     Output of flatten_manual_overrides()
        export_path:   Path to write the raw inspection CSV

    Returns:
        Raw combined DataFrame with all conflicts and duplicates intact
    """
    dfs = [df for df in [df_ddg, df_disconnect, df_manual] if not df.empty]

    if not dfs:
        logger.warning("All three source DataFrames are empty — returning empty DataFrame")
        return pd.DataFrame(columns=[
            "domain", "subsidiary_entity", "parent_entity", "source", "priority"
        ])

    raw_df = pd.concat(dfs, ignore_index=True)

    # Log source breakdown to sanity check row counts per source
    for source in ["ddg", "disconnect", "manual"]:
        count = len(raw_df[raw_df["source"] == source])
        logger.info(f"  {source}: {count} rows")
    logger.info(f"  total: {len(raw_df)} rows across all sources")

    # Export complete combined data to csv file
    try:
        raw_df.to_csv(export_path, index=False)
        logger.info(f"Raw concatenated map saved to: {export_path}")
    except Exception as e:
        logger.error(f"Failed to write raw concatenated map to {export_path} — {e}")

    return raw_df


# =============================================================================
# (2) DATA PREPROCESSING
# =============================================================================

# --- HELPER FUNCTIONS ---

def resolve_dba_entities(df: pd.DataFrame) -> pd.DataFrame:
    """
    Step 1.5: Resolve 'x dba y' (doing business as) constructions
    in parent_entity column. Split so x = legal registrant name,
    which is stored in new column parent_legal_name, and y = operating
    name, which replaces parent_entity.
    """

    # Initialize provenance column with None for all rows
    df['parent_legal_name'] = None

    # Identify rows where parent_entity contains ' dba '
    dba_mask = df['parent_entity'].str.contains(' dba ', na=False)
    dba_count = dba_mask.sum()

    if dba_count == 0:
        return df

    # Split on first occurrence of ' dba ' only
    split_result = df.loc[dba_mask, 'parent_entity'].str.split(' dba ', n=1, expand=True)
    legal_half = split_result[0].str.strip()
    operating_half = split_result[1].str.strip()

    # Guard: warn on empty legal half (no registrant name before dba)
    empty_legal = legal_half.eq('')
    if empty_legal.any():
        logger.warning(
            f"[resolve_dba] {empty_legal.sum()} rows have empty legal name before 'dba' — "
            f"parent_legal_name will be None for these rows"
        )

    # Guard: warn on empty operating half (no operating name after dba)
    empty_operating = operating_half.eq('')
    if empty_operating.any():
        logger.warning(
            f"[resolve_dba] {empty_operating.sum()} rows have empty operating name after 'dba' — "
            f"parent_entity will not be updated for these rows"
        )

    # Apply strip_suffixes() to legal half and store as provenance column
    # Only store where legal half is non-empty
    valid_legal = dba_mask & ~empty_legal
    df.loc[valid_legal, 'parent_legal_name'] = strip_suffixes(
        legal_half[valid_legal[dba_mask]]
    )

    # Replace parent_entity with operating half where operating half is non-empty
    valid_operating = dba_mask & ~empty_operating
    df.loc[valid_operating, 'parent_entity'] = operating_half[valid_operating[dba_mask]]

    return df

def apply_name_replacements(series: pd.Series) -> pd.Series:
    """
    Step 3: Replace known entity name variants with their canonical form.
    Uses ENTITY_NAME_REPLACEMENTS dict.
    """
    return series.replace(ENTITY_NAME_REPLACEMENTS)

def apply_parent_overrides(df: pd.DataFrame) -> pd.DataFrame:
    """
    Step 4: Enforce correct subsidiary-parent hierarchy using PARENT_OVERRIDES.
    Keys on subsidiary_entity only.
    """
    df['parent_entity'] = df['subsidiary_entity'].map(PARENT_OVERRIDES).fillna(df['parent_entity'])
    return df

def remove_duplicates(df: pd.DataFrame) -> tuple[pd.DataFrame, int, int]:
    """
    Step 5: Remove duplicate rows in two phases.

    Phase A — Exact duplicate removal:
        Drop redundant rows where (domain, subsidiary_entity, parent_entity) are identical.
        Priority number used as tiebreaker (higher number = higher authority wins).

    Phase B — Domain conflict resolution:
        Where multiple sources disagree on entity ownership for the same domain,
        keep the highest-authority source. Sort ascending by priority number so
        keep='last' retains the highest-numbered (most authoritative) source.
        Priority cascade: Manual (3) > Disconnect (2) > DDG (1)

    Returns:
        tuple[pd.DataFrame, int, int]: tuple containing updated dataframe index
                                        and counts of duplicate rows removed
    """
    # Sort ascending so highest priority number ends up last
    df = df.sort_values('priority', ascending=True)

    # Phase A: drop exact triples — sources agree, row is simply redundant
    before_a = len(df)
    df = df.drop_duplicates(
        subset=['domain', 'subsidiary_entity', 'parent_entity'],
        keep='last'
    )
    after_a = len(df)

    # Phase B: resolve domain conflicts — sources disagree on entity ownership
    before_b = len(df)
    df = df.drop_duplicates(
        subset=['domain'],
        keep='last'
    )
    after_b = len(df)

    exact_dropped = before_a - after_a
    conflict_dropped = before_b - after_b

    return df.reset_index(drop=True), exact_dropped, conflict_dropped


# --- MAIN PREPROCESS FUNCTION ---

def preprocess_combined(
    raw_df: pd.DataFrame,
    export_path: str,
) -> pd.DataFrame:
    """
    Full preprocessing pipeline for concatenated domain-entity mappings.
    
    Takes raw DataFrame from concatenate_sources() and applies all normalization,
    standardization, and deduplication steps.
    
    Args:
        raw_df (pd.DataFrame): Output from concatenate_sources()
                Required columns: domain, subsidiary_entity, parent_entity, source, priority
    
    Returns:
        pd.DataFrame: Clean, deduplicated DataFrame ready for analysis
    """
    df = raw_df.copy()
    
    logger.info(f"Starting preprocessing pipeline — input rows: {len(df)}")
    
    # Step 1: Normalize entity names (lowercase, remove punctuation/whitespace)
    df['subsidiary_entity'] = normalize_string(df['subsidiary_entity'])
    df['parent_entity'] = normalize_string(df['parent_entity'])
    
    # Step 1.5: Resolve DBA names in parent_entity
    df = resolve_dba_entities(df)

    # Step 2: Strip legal entity suffixes
    df['subsidiary_entity'] = strip_suffixes(df['subsidiary_entity'])
    df['parent_entity'] = strip_suffixes(df['parent_entity'])
    
    # Step 3: Apply name replacements (standardization)
    df['subsidiary_entity'] = apply_name_replacements(df['subsidiary_entity'])
    df['parent_entity'] = apply_name_replacements(df['parent_entity'])
    
    # Step 4: Apply parent overrides (hierarchy enforcement)
    df = apply_parent_overrides(df)
    
    try:
        df.to_csv("data/names_processed.csv", index=False)
        logger.info(f"Pre-deduplication snapshot written to: data/names_processed.csv ({len(df)} rows)")
    except Exception as e:
        logger.error(f"Failed to write pre-deduplication snapshot — {e}")

    # Step 5: Remove duplicates (exact matches + domain conflicts)
    df, exact_dropped, conflict_dropped = remove_duplicates(df)
    logger.info(
        f"Deduplication — exact rows dropped: {exact_dropped} | "
        f"domain conflict rows dropped: {conflict_dropped} | "
        f"rows remaining: {len(df)}"
    )

    logger.info(f"Preprocessing pipeline complete — output rows: {len(df)}")
    
   # Step 6: Write preprocessed canonical domain map to CSV
    try:
        df.to_csv(export_path, index=False)
        logger.info(f"Canonical domain map saved to: {export_path}")
    except Exception as e:
        logger.error(f"Failed to write canonical domain map to {export_path} — {e}")

    return df


# =============================================================================
# (3) TREE + INDEX BUILDING
# =============================================================================
def build_path(row) -> str:
    """
    Constructs a bigtree path string for a given DataFrame row.
    Format: root/{parent_entity}/{subsidiary_entity}/{domain}
    
    Null handling:
    - domain null → logs error, returns None (row will be dropped before tree build)
    - one entity null → fills from the other to maintain fixed depth
    - both entities null → pass-through: both set to domain value
    - slash sanitization → replaces "/" in any value to prevent false hierarchy levels
    """
    domain = row.get("domain")
    parent = row.get("parent_entity")
    subsidiary = row.get("subsidiary_entity")

    # --- NULL DOMAIN: unrecoverable, log and skip ---
    if pd.isna(domain) or str(domain).strip() == "":
        print(f"Warning: Null domain encountered in row — skipping. Row: {row.to_dict()}")
        return None

    # --- CLEAN ALL VALUES ---
    domain     = str(domain).strip()
    parent     = str(parent).strip()     if pd.notna(parent)     else ""
    subsidiary = str(subsidiary).strip() if pd.notna(subsidiary) else ""

    # --- NULL ENTITY HANDLING ---
    if parent == "" and subsidiary == "":
        # Both null — pass-through fallback
        print(f"Warning: Both entities null for domain '{domain}' — using domain as pass-through.")
        parent = domain
        subsidiary = domain

    elif parent == "":
        # Parent null only — fill from subsidiary
        print(f"Warning: Parent entity null for domain '{domain}' — filling from subsidiary '{subsidiary}'.")
        parent = subsidiary

    elif subsidiary == "":
        # Subsidiary null only — fill from parent
        print(f"Warning: Subsidiary entity null for domain '{domain}' — filling from parent '{parent}'.")
        subsidiary = parent

    # --- SLASH SANITIZATION ---
    # Replace forward slashes to avoid creating phantom hierarchy levels in bigtree
    domain     = domain.replace("/", "-")
    parent     = parent.replace("/", "-")
    subsidiary = subsidiary.replace("/", "-")

    return f"root/{parent}/{subsidiary}/{domain}"

def get_domain_index(root: Node) -> dict:
    """
    Builds a fast O(1) lookup index from the constructed entity tree.
    Maps domain strings to their corresponding leaf node objects.
    Called after build_entity_tree().

    Args:
        root: The root node of the bigtree structure.

    Returns:
        domain_to_node: dict mapping domain string → leaf node object.
    """
    return {node.name: node for node in root.leaves}

def build_entity_tree(df: pd.DataFrame, output_csv: str) -> tuple[Node, dict]:
    """"
    Constructs the corporate entity tree from the canonical preprocessed DataFrame.
    Exports the tree to CSV for reconstruction by downstream scripts.

    Tree structure: root / parent_entity / subsidiary_entity / domain

    Leaf node attributes attached automatically from DataFrame columns:
        node.name              → domain string (the node identity)
        node.domain            → domain name
        node.subsidiary_entity → subsidiary entity name        
        node.parent_entity     → parent entity name
        node.source            → originating dataset ("ddg", "disconnect", "manual")
        node.priority          → source priority integer (1, 2, or 3)

    Args:
        df:         Preprocessed canonical DataFrame with columns:
                    domain, subsidiary_entity, parent_entity, source, priority
        output_csv: Filepath for the exported tree CSV artifact.
                    Loaded by http_analysis.py and any other downstream scripts.

    Returns:
        root:           Root node of the constructed bigtree structure.
        domain_to_node: Dict mapping domain strings to leaf nodes for O(1) lookup.
    """

    # Generate path column with build_path(), returns
    # None for unrecoverable rows (null domain)
    df = df.copy()
    df["path"] = df.apply(build_path, axis=1)

    # Drop rows where build_path() returned None
    dropped = df[df["path"].isna()]
    if not dropped.empty:
        print(f"Warning: {len(dropped)} rows dropped due to null domain values.")
    df = df.dropna(subset=["path"])

    # Construct tree from path column
    root = dataframe_to_tree(df, path_col="path")

    # Build domain-to-node index by calling helper function
    domain_to_node = get_domain_index(root)

    # Export live tree object to flat CSV for future reconstruction
    # by dataframe_to_tree() in analysis scripts
    tree_export_df = tree_to_dataframe(root, all_attrs=True)
    tree_export_df.to_csv(output_csv, index=False)

    return root, domain_to_node


def main():

    # --- STEP 1: LOAD & CONCATENATE ---
    logger.info("=== Step 1: Loading data sources ===")
    df_ddg        = load_ddg_entities(DDG_ENTITIES_PATH)
    df_disconnect = load_disconnect_entities(DISCONNECT_PATH)
    df_manual     = flatten_manual_overrides(MANUAL_OVERRIDES)

    logger.info("=== Concatenating sources ===")
    raw_df = concatenate_sources(df_ddg, df_disconnect, df_manual, RAW_CONCAT_PATH)
    logger.info(f"Review {RAW_CONCAT_PATH} before proceeding.")

    # --- STEP 2: PREPROCESS ---
    logger.info("=== Step 2: Preprocessing and conflict resolution ===")
    canonical_df = preprocess_combined(raw_df, CANONICAL_PATH)
    logger.info(f"Review {CANONICAL_PATH} before proceeding.")

    # # --- STEP 3: BUILD TREE & INDEX ---
    # logger.info("=== Step 3: Building entity tree and domain index ===")
    # root, domain_to_node = build_entity_tree(canonical_df, TREE_OUTPUT_CSV)

    # logger.info(f"Tree contains {len(domain_to_node)} mapped domains.")
    # logger.info(f"=== Build_mapping_tree.py complete. Entity tree exported to {TREE_OUTPUT_CSV} and ready for analysis. ===")


if __name__ == "__main__":
    main()