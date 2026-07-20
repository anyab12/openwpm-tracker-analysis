"""
Script: /home/anya/Openwpm/utils.py

Author: Anya Barringer, aided by Claude Sonnet 4.6 and
        Codestral through Furman University BoodleBox

Container:  Part of CSC Summer Research 2026 Project
            "Pervasive Online Third-Party Tracking: A Measurement Study"
            with Graham Fink, under Dr. Rebecca Drucker

Goal:   Contains shared utility functions that are called
        by other analysis scripts, as well as related constants.
        Does not contain pipeline-specific dependencies, file
        paths, database connections or loading, or output logic.
        
        Functions include:
            - URL and domain extraction - get_registered_domain()
            - Entity tree loading and node / domain lookup -
                load_tree(), get_node_info()
            - Hierarchial relationship classification - classify_relationship()
            - Summary statistic helpers - get_number_children()
            - Entity name normalization - normalize_string(),
                strip_suffixes() + ENTITY_SUFFIXES
"""



import logging
import tldextract
import pandas as pd
from types import SimpleNamespace
from bigtree import Node, Tree, dataframe_to_tree

logger = logging.getLogger(__name__)



# --- CONSTANTS FOR strip_suffixes ---

# Safe, unambiguous legal suffixes only. Handle risky tokens
# explicitly in ENTITY_NAME_REPLACEMENTS where verified safe.
ENTITY_SUFFIXES = {
    'inc', 'incorporated',
    'corp', 'corporation',
    'ltd', 'limited',
    'com', 'company',
    'llc', 'co', 'llp', 'lp',
    'plc', 'pllc', 'pty',
    'gmbh', 'ag', 'kg', 'mbh',
    'ohg', 'se', 'evp', 'sas',
    'sl', 'srl', 'sarl', 'sa','lda', 'ltda',
    'bv', 'nv', 'cv', 'bvba',
    'ab', 'as', 'asa', 'aps', 'oy',
    'kft', 'jsc', 'ooo',
    'pte', 'pvt', 'cz', 'ou',
    'uab', 'fzco', 'fz', 'zrt',
    'cn', 'me', 'tv', # not explicit legal suffixes, preceeded by "." & created after name normalization
    'holdings', 'industries', 'entities',
    'enterprises', 'technologies', 'software' # Note: spacing inconsistency issues
}

# Legal suffixes with several letters and punctuation.
# Must be handled separately due to normalize_string()
# logic that replaces punctuation with spaces.
MULTI_TOKEN_ENTITY_SUFFIXES = {
    # ('s', 'a', 'de', 'c', 'v'),       # s.a. de c.v.
    ('gmbh', 'und', 'co', 'kg'),      # gmbh und co. kg
    ('sp', 'z', 'o', 'o'),            # sp. z o.o.
    # ('s', 'a', 'r', 'l'),             # S.A.R.L.
    ('spol', 's', 'r', 'o'),          # spol. s r.o.
    # ('ges', 'g', 'b', 'h'),           # ges.m.b.h.

    ('s', 'p', 'a'),                  # S.p.A.
    ('s', 'r', 'l'),                  # S.r.l.
    ('s', 'r', 'o'),                  # s.r.o.
    # ('z', 'o', 'o'),                  # z o.o.
    ('d', 'o', 'o'),                  # d.o.o.
    # ('de', 'c', 'v'),                 # de C.V.
    ('s', 'a', 's'),                  # S.A.S.
    ('l', 'l', 'c'),                  # L.L.C.
    # ('m', 'b', 'h'),                  # m.b.H.
    # ('a', 'r', 'l'),                  # À R.L.
    # ('s', 'l', 'u'),                  # S.L.U.
    # ('s', 'a', 'c'),                  # S.A.C.
    # ('p', 'l', 'c'),                  # P.L.C.

    ('private', 'limited'),
    ('pvt', 'ltd'),                   # Pty. Ltd
    ('pte', 'ltd'),                   # Pvt. Ltd
    ('pty', 'ltd'),                   # Pte. Ltd
    # ('sdn', 'bhd'),                   # Sdn. Bhd.
    ('b', 'v'),                       # B.V.
    ('s', 'a'),                       # S.A.
    ('a', 's'),                       # A.S., A/S
    ('s', 'l'),                       # S.L.
    ('l', 'p'),                       # L.P.
    # ('e', 'v'),                       # e.V. 
    # ('e', 'k'),                       # e.K.
    # ('d', 'd'),                       # d.d.
    # ('r', 'o'),                       # r.o.
}


def normalize_string(series: pd.Series) -> pd.Series:
    """
    Step 1 normalization: Lowercase, remove punctuation, and normalize
    whitespace. Also remove "the" at beginning of all entity names.
    Must run before all other steps so downstream helpers operate on clean tokens.
    """
    return (
        series
        .str.lower()
        .str.strip()
        .str.replace(r'^the\s+', '', regex=True)    # strip leading article
        .str.replace(r'[^\w\s]', ' ', regex=True)   # remove punctuation and replace with space
        .str.replace(r'\s+', ' ', regex=True)       # collapse multiple spaces
        .str.strip()
    )


def strip_suffixes(series: pd.Series) -> pd.Series:
    """
    Step 2 normalization: Remove legal suffixes (single- and multi-token) token
    by token. Only removes trailing suffix tokens to avoid partial name corruption.
    
    Multi-token trailing suffixes checked first (longest-first) for character
    sequences that can't be safely added as individual tokens to ENTITY_SUFFIXES.
    Then single-token suffixes removed. Both passes iterate until fixed point
    (no changes in a full cycle).
    """

    def _strip(text: str) -> str:
        if not isinstance(text, str):
            return text

        tokens = text.split()

        # Iterate until fixed point: no changes in full pass through both lists
        changed = True
        while changed and tokens:
            changed = False

            # Strip trailing multi-token suffix sequences (longest-first)
            for suffix in MULTI_TOKEN_ENTITY_SUFFIXES:
                n = len(suffix)
                if len(tokens) > n and tuple(t.lower() for t in tokens[-n:]) == suffix:
                    tokens = tokens[:-n]
                    changed = True
                    break  # restart from top of MULTI_TOKEN_ENTITY_SUFFIXES

            # Strip trailing single-token suffix tokens
            while tokens and tokens[-1].lower() in ENTITY_SUFFIXES:
                tokens.pop()
                changed = True

        return ' '.join(tokens) if tokens else text  # return original if all tokens stripped

    return series.apply(_strip)


def get_registered_domain(url: str) -> str:
    """
    Extracts the eTLD+1 (registrable domain) from a URL using tldextract.
    Handles None, NaN, empty strings, bare IPs, and malformed URLs.
    Adds branded gTLD handling for domains like .google, .fox.
    Returns a lowercase domain string, or None if unresolvable.
    """
    if not url or pd.isna(url):
        return None
    
    try:
        ext = tldextract.extract(str(url))
        if not ext.domain or not ext.suffix:
            # Branded gTLD fallback — tldextract may put these entirely in suffix
            if ext.suffix and not ext.domain:
                return ext.suffix.lower()
            return None
        return f"{ext.domain}.{ext.suffix}".lower()
    except Exception:
        return None


def load_tree(tree_csv_path) -> tuple[Node, dict]:
    """
    Loads pre-built entity tree from CSV and reconstructs bigtree object.
    Also builds domain_to_node index for O(1) classification lookup.

    Args:
        tree_csv_path: Path to output_tree.csv produced by build_mapping_tree.py

    Returns:
        root:           Root node of reconstructed bigtree structure.
        domain_to_node: Dict mapping domain strings to leaf node objects.
    """
    try:
        tree_df = pd.read_csv(tree_csv_path)
    except FileNotFoundError:
        logger.error(f"Entity tree not found at '{tree_csv_path}'. Run build_mapping_tree.py first.")
        raise

    root = dataframe_to_tree(tree_df, path_col="path")
    domain_to_node = {node.name: node for node in root.leaves}

    logger.info(f"Entity tree loaded: {len(domain_to_node)} domains mapped.")
    return root, domain_to_node


def get_node_info(domain: str, domain_to_node: dict) -> SimpleNamespace:
    """
    Retrieves node from the index. If domain is unknown and
    dictionary returns None, function returns Virtual Node.
    """
    node = domain_to_node.get(domain)
    if node:
        return node
    
    return SimpleNamespace(
        name=domain,
        subsidiary_entity=domain,
        parent_entity=domain,
        source="none",
        priority=0
    )


def classify_relationship(req_node: Node, top_node: Node) -> dict:
    """
    Compares two entity tree nodes to determine their relationship.
    Uses nested checks so each tier only fires if the previous tier confirmed
    a difference — avoids redundant comparisons.

    Args:
        req_node:       request URL domain node
        top_node:       top-level URL domain node

    Returns dict of boolean flags:
        is_technical_third_party   → eTLD+1 differs
        is_subsidiary_third_party  → subsidiary entity differs
        is_parent_third_party      → parent entity differs
    """
    result = {
        "is_technical_third_party":  False,
        "is_subsidiary_third_party": False,
        "is_parent_third_party":     False,
    }

    # Technical check — node names are the domain strings
    if req_node.name != top_node.name:
        result["is_technical_third_party"] = True

        # Subsidiary check — attribute, or immediate parent node
        if req_node.subsidiary_entity != top_node.subsidiary_entity:
            result["is_subsidiary_third_party"] = True

            # Parent check — attribute, or grandparent node
            if req_node.parent_entity != top_node.parent_entity:
                result["is_parent_third_party"] = True
    return result


def get_number_children(node: Node) -> int:
    """
    Returns number of nodes in node.children list as number of
    subsidiaries per parent, or number of domains per subsidiary. 
    """
    return len(node.children)