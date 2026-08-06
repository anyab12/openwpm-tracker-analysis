"""
Script: /src/utilities/treemap_preprocessing_constants.py

Author: Anya Barringer, aided by Claude Sonnet 4.6 and
        Codestral through Furman University BoodleBox

Container:  Part of CSC Summer Research 2026 Project
            "Pervasive Online Third-Party Tracking: A Measurement Study"
            with Graham Fink, under Dr. Rebecca Drucker

Goal:   Contains constants used in preprocessing data for domain-entity
        hierarchy tree map. Imported in build_mapping_tree.py and applied
        during step 2 preprocess_combined() in its helper functions.
        
        Constants include:
            - MANUAL_OVERRIDES - contains hardcoded domain-entity decisions
                with highest source priority. Used for missing or misattributed
                domain mappings.
            - ENTITY_NAME_REPLACEMENTS - contains normalized entity names to
                eliminate discrepancies between source mappings
            - PARENT_OVERRIDES - contains correct mappings for normalized subsidiary
"""



# Hardcoded editorial decisions with highest priority in the cascade.
# Structure: { domain: (subsidiary_entity, parent_entity) }
# Correctly maps any missing or misattributed domains (e.g. dt.fox,
# destinythegame.com). Naming conventions and hierarchy decisions
# dealt with below in ENTITY_NAME_REPLACEMENTS and PARENT_OVERRIDES.
MANUAL_OVERRIDES = {
        # --- Fox Corporation ---
        "dt.fox":                   ("fox", "fox corporation"),
        "apt.fox":                  ("fox", "fox corporation"),
        "strike.fox":               ("fox", "fox corporation"),

        # --- Salesforce ---
        "sfdcdigital.com":          ("salesforce", "salesforce"),
        "salesforce-scrt.com":      ("salesforce", "salesforce"),

        # --- Disney / National Geographic ---
        "disneyaccount.com":        ("disney", "disney"),
        "natgeofe.com":             ("national geographic", "disney"),

        # --- IBM acquisitions ---
        "hashicorp.com":            ("hashicorp", "international business machines"),
        "datastax.com":             ("datastax", "international business machines"),

        # --- The Weather Company - from IBM to Francisco Partners ---
        "weather.com":              ("weather company", "francisco partners"),
        "weatherfx.com":            ("weather company", "francisco partners"),
        "wfxtriggers.com":          ("weather company", "francisco partners"),
        "w-x.co":                   ("weather company", "francisco partners"),

        # --- Riot Games -> Tencent ---
        "leagueoflegends.com":      ("riot games", "tencent"),
        "riotgames.com":            ("riot games", "tencent"),

        # --- TakeTwo Interactive ---
        "zynga.com":                ("zynga", "take two interactive"),
        "rockstargames.com":        ("rockstar games", "take two interactive"),
        "take2games.com":           ("take two interatctive", "take two interactive"),

        # --- Connexity -> Taboola ---
        "connexity.com":            ("connexity", "taboola"),
        "connexity.net":            ("connexity", "taboola"),

        # --- SAS Institute ---
        "sas.com":                  ("sas institute", "sas institute"),
        "aimatch.com":              ("sas institute", "sas institute"),

        # --- Russian domains ---
        "tns-counter.ru":           ("mediascope", "mediascope"),
        "sputnik.ru":               ("rostelecom", "rostelecom"),
        "mts.ru":                   ("mobile telesystems", "afk sistema"),

        # --- Awes / Awesome acquisitions ---
        "flickr.com":               ("flickr", "awesome"),
        "statickflickr.com":        ("flickr", "awesome"),
        "smugmug.com":              ("smugmug", "awesome"),

        # --- Automattic ---
        "tumblr.com":               ("tumblr", "automattic"),
        "parse.ly":                 ("wordpress vip", "automattic"),
        "woocommerce.com":          ("woocommerce", "automattic"),
        "beeper.com":               ("beeper", "automattic"),
        "beeperstatus.com":         ("beeper", "automattic"),
        "pocketcasts.com":          ("pocket casts", "automattic"),
        "gravatar.com":             ("gravatar", "automattic"),

        # --- Criteo acquisitions ---
        "iponweb.com":              ("iponweb", "criteo"),
        "iponweb.net":              ("iponweb", "criteo"),
        "bidswitch.com":            ("bidswitch", "criteo"),
        "bidswitch.net":            ("bidswitch", "criteo"),
        "mfadsrvr.com":             ("bidswitch", "criteo"),

        # --- Manually discovered from crawl data inspection ---
        "rokt-api.com":             ("rokt", "rokt"),
        "mediagotechnology.com":    ("baidu", "baidu"),

        # --- Miscellaneous ---
        "chartboost.com":           ("chartboost", "loopme"),
        "t13.io":                   ("freestar", "freestar"),
        "sizmek.com":               ("amazon", "amazon"),
        "pointroll.com":            ("pointroll", "amazon"),
        "admarvel.com":             ("adcolony", "digital turbine"),
        "destinythegame.com":       ("bungie", "sony"),
        "wbmdstatic.com":           ("webmd", "webmd"),
        "profootballhof.com":       ("pro football hall of fame", "pro football hall of fame"),
        "greatamericancountry.com": ("great american media", "great american media"),
        "bungie.net":               ("bungie", "sony"),
    }


# Maps normalized entity names to their canonical replacement.
ENTITY_NAME_REPLACEMENTS = {
    # name consistency
    "hearst":                           "hearst communications",
    "slack":                            "slack technologies",
    "ibm":                              "international business machines",
    "iab":                              "interactive advertising bureau",
    "deutsche post":                    "deutsche post dhl",
    "visually crm":                     "visually",
    "narrative":                        "narrative i/o",
    "narrative i o":                    "narrative i/o",
    "online solution":                  "online solution int",
    "fluct gsm div":                    "fluct",
    "take two":                         "take two interactive",
    "awes":                             "awesome",
    "vk":                               "vkontakte",

    # corporate renamings / acquisitions
    # "gannett":      "usa today",
    "scripps networks":                 "warner bros discovery",
    "unity ironsource":                 "unity",
    "cm group":                         "marigold",
    
    # edge cases where "suffix" appears as prefix
    "ltd sape":                         "sape",
    "llc smi2":                         "smi2",
    "llc internest holding":            "internest holding",
    "llc amberdata":                    "amberdata",
    "llc palitrumlab":                  "palitrumlab",
    "limited liability company ngenix": "ngenix",

    # edge cases with inconsistent internal word spacing in names
    "42ads":                            "42 ads",
    "abtasty":                          "ab tasty",
    "alibabagroup":                     "alibaba group",
    "alibaba":                          "alibaba group",
    "admanmedia":                       "adman media",
    "advancedstore":                    "advanced store",
    "arkoselabs":                       "arkose labs",
    "assertiveyield":                   "assertive yield",
    "avidmedia":                        "avid media",
    "bluetriangle":                     "blue triangle",
    "calltrackingmetrics":              "call tracking metrics",
    "civicscience":                     "civic science",
    "constantcontact":                  "constant contact",
    "contactimpact":                    "contact impact",
    "cookieinformation":                "cookie information",
    "deepintent":                       "deep intent",
    "digitaleast":                      "digital east",
    "digitalturbine":                   "digital turbine",
    "dts":                              "dts technology",
    "dtstechnology":                    "dts technology",
    "durationmedia":                    "duration media",
    "engagebdr":                        "engage bdr",
    "godaddy":                          "go daddy",
    "hackerrank":                       "hacker rank",
    "helpscout":                        "help scout",
    "humansecurity":                    "human security",
    "indexexchange":                    "index exchange",
    "intimatemerger":                   "intimate merger",
    "intuitionmachines":                "intuition machines",
    "luckyorange":                      "lucky orange",
    "mathereconomics":                  "mather economics",
    "nativeads":                        "native ads",
    "nextmillennium":                   "next millennium media",
    "next millennium":                  "next millennium media",
    "ninjatools":                       "ninja tools",
    "optidigital":                      "opti digital",
    "ozoneproject":                     "ozone project",
    "quantummetric":                    "quantum metric",
    "resetdigital":                     "reset digital",
    "retailrocket":                     "retail rocket",
    "roqad":                            "roq ad",
    "rtbhouse":                         "rtb house",
    "siftscience":                      "sift science",
    "simplifi":                         "simpli fi",
    # "singular":                         "singular labs",
    # "singularlabs":                     "singular labs",
    "siriusxm":                         "sirius xm",
    "snowplowanalytics":                "snowplow analytics",
    "so netmedianetworks":              "so net media networks",
    # "taptap":                           "taptap digital",
    # "taptapdigital":                    "taptap digital",
    "timesinternet":                    "times internet",
    "tmtdigital":                       "tmt digital",
    "traffichaus":                      "traffic haus",
    "trafficstars":                     "traffic stars",
    "treasuredata":                     "treasure data",
    "unitedinternet":                   "united internet",
    "verticalhealth":                   "vertical health",
    "vervegroup":                       "verve group",
    "wpengine":                         "wp engine",
    "zetaglobal":                       "zeta global",
    "ziffdavis":                        "ziff davis",
}


# Maps normalized subsidiary names to their correct parent.
# Key = normalized subsidiary entity name
# Value = normalized correct parent entity name
PARENT_OVERRIDES = {
    "instagram":              "meta",
    "facebook":               "meta",
    "whatsapp":               "meta",
    "tiktok":                 "bytedance",
    "google":                 "alphabet",
    "youtube":                "alphabet",
    "doubleclick":            "alphabet",
    "fitbit":                 "alphabet",
    "waze":                   "alphabet",
    "waymo":                  "alphabet",
    "goodread":               "amazon",
    "audible":                "amazon",
    "github":                 "microsoft",
    "linkedin":               "microsoft",
    "slack technologies":     "salesforce",
    "riot games":             "tencent",
    "riot games inc tencent subsidiary": "tencent",
    "cookie trust":           "interactive advertising bureau",
    "peer39":                 "o3 industries",
    "flickr":                 "awesome",
    "smugmug":                "awesome",
    "wordpress vip":          "automattic",
    "tumblr":                 "automattic",
    "woocommerce":            "automattic",
    "beeper":                 "automattic",
    "pocket casts":           "automattic",
    "gravatar":               "automattic",
    "bidswitch":              "criteo",
    "iponweb":                "criteo",
    "hashicorp":              "international business machines",
    "datastax":               "international business machines",
    "bungie":                 "sony",
    "ab tasty":               "everstone capital",
    "wingify":                "everstone capital",
    "connexity":              "taboola",
    "emma":                   "marigold",
}