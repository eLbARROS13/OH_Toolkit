# OH Parser Project Context

> This document provides context about the OH Parser project for LLM assistants.

---

## Project Overview

**OH Parser** is a Python library for extracting data from Occupational Health (OH) profile JSON files into pandas DataFrames. It's designed to work with nested JSON structures containing health metrics, questionnaire data, and sensor readings.

### Key Characteristics
- **Pure function-based architecture** (no classes)
- **Dot-notation path resolution** for navigating nested JSON
- **Flexible filtering** by subject ID, date range, etc.
- **CLI interface** for quick testing and exploration

---

## Project Structure

```
oh_parser_project/
├── oh_parser/
│   ├── __init__.py          # Public API exports
│   ├── __main__.py          # Module entrypoint (python -m oh_parser)
│   ├── cli.py               # Command-line interface
│   ├── loader.py            # Load OH profile JSON files
│   ├── path_resolver.py     # Dot-notation path navigation
│   ├── filters.py           # Subject/date filtering
│   ├── extract.py           # DataFrame extraction functions
│   └── utils.py             # Utility functions
├── oh_parser_venv/          # Virtual environment
├── requirements.txt         # Dependencies
└── README.md
```

---

## Data Source

- **Location**: `E:\Backup PrevOccupAI_PLUS Data\OH_profiles`
- **Format**: JSON files named `{subject_id}_OH_profile.json`
- **Count**: 37 profiles
- **Subject IDs**: 103, 104, 105, 106, 107, 108, 109, 110, 112, 113, etc.

### Typical OH Profile Structure

```json
{
  "meta_data": {
    "age": 45,
    "gender": "M",
    ...
  },
  "single_instance_questionnaires": { ... },
  "daily_questionnaires": {
    "2024-01-15": { ... },
    "2024-01-16": { ... }
  },
  "sensor_metrics": {
    "emg": {
      "2024-01-15": {
        "session_1": {
          "left": {
            "EMG_intensity": { "mean_percent_mvc": 0.23 },
            "EMG_apdf": { "active": { "p50": 0.31 } }
          },
          "right": { ... }
        }
      },
      "EMG_weekly_metrics": { ... },
      "EMG_daily_metrics": { ... }
    }
  },
  "sensor_timeline": { ... },
  "human_activities": { ... },
  "background": {
    "socialHistory": {
      "tobaccoUse": { ... }
    }
  }
}
```

---

## Module Documentation

### 1. `loader.py` - Load Profiles

**Public Functions:**
- `load_profiles(directory, verbose=True)` → `Dict[str, dict]` - Load all profiles from directory
- `load_profile(filepath)` → `dict` - Load single profile
- `list_subjects(profiles)` → `List[str]` - Get sorted list of subject IDs
- `get_profile(profiles, subject_id)` → `dict | None` - Get specific subject's profile

**Private Functions:**
- `_discover_oh_profiles(directory)` → `List[Path]` - Find all `*_OH_profile.json` files
- `_extract_subject_id(filepath)` → `str` - Extract subject ID from filename

**Constant:**
- `_OH_PROFILE_SUFFIX = "_OH_profile.json"`

### 2. `path_resolver.py` - Navigate Nested JSON

**Key Functions:**
- `resolve_path(data, path)` - Navigate to value at dot-notation path
- `path_exists(data, path)` - Check if path exists
- `list_keys_at_path(data, path)` - List keys at a given path
- `expand_wildcards(data, path_pattern)` - Expand `*` in paths

**Example:**
```python
resolve_path(profile, "sensor_metrics.emg.EMG_weekly_metrics.left.EMG_apdf.active.p50")
# Returns: 0.31
```

### 3. `filters.py` - Filtering Functions

**Key Functions:**
- `create_filters(...)` → `Dict` - Create a filters dict with optional parameters
- `apply_subject_filters(profiles, filters)` - Filter profiles by subject list
- `filter_date_keys(keys, date_range)` - Filter date-like keys by range
- `exclude_keys(keys, patterns)` - Exclude keys matching patterns

**Filter Dict Structure:**
```python
{
    "subjects": ["103", "104", "105"],    # Include only these subjects
    "exclude_subjects": ["108"],           # Exclude these subjects
    "date_range": ("2024-01-01", "2024-03-31"),  # Date filtering
}
```

### 4. `extract.py` - DataFrame Extraction

**Main Functions:**

#### `extract(profiles, paths, filters=None)` → Wide DataFrame
One row per subject. Cherry-pick specific paths.

```python
df = extract(profiles, {
    "age": "meta_data.age",
    "emg_p50_left": "sensor_metrics.emg.EMG_weekly_metrics.left.EMG_apdf.active.p50",
})
```

#### `extract_nested(profiles, base_path, level_names, value_paths=None)` → Long DataFrame
Iterates through nested levels (dates, sessions, sides).

```python
df = extract_nested(
    profiles,
    base_path="sensor_metrics.emg",
    level_names=["date", "session", "side"],
    value_paths=["EMG_intensity.mean_percent_mvc"],
    exclude_patterns=["EMG_daily_metrics", "EMG_weekly_metrics"],
)
```

#### `extract_flat(profiles, base_path)` → Wide DataFrame
Flattens everything under a path into columns.

#### `inspect_profile(profile, max_depth=4)` → Prints tree structure

#### `summarize_profiles(profiles)` → DataFrame showing data availability

### 5. `utils.py` - Utilities

- `flatten_dict(d, sep=".")` - Flatten nested dict to single level
- `is_date_key(key)` - Check if string looks like a date
- `is_time_key(key)` - Check if string looks like a time
- `get_nested_keys(d, max_depth)` - Get all keys recursively
- `print_tree(d, max_depth)` - Pretty-print dict structure

### 6. `cli.py` - Command-Line Interface

**Default OH Directory:** `E:\Backup PrevOccupAI_PLUS Data\OH_profiles`

**Commands:**
```bash
# Basic info (no args needed - uses default path)
python -m oh_parser

# List all subject IDs
python -m oh_parser --list

# Inspect a subject's profile structure
python -m oh_parser --inspect 103 --depth 5

# List all available JSON paths
python -m oh_parser --paths 103

# Show data availability summary
python -m oh_parser --summary

# Suppress loading messages
python -m oh_parser --quiet
```

---

## Usage Examples

### Basic Extraction

```python
from oh_parser import load_profiles, extract, list_subjects

# Load all profiles (uses default directory)
profiles = load_profiles()

# List subjects
subjects = list_subjects(profiles)  # ['103', '104', '105', ...]

# Extract specific fields into DataFrame
df = extract(profiles, {
    "age": "meta_data.age",
    "gender": "meta_data.gender",
    "emg_p50_left": "sensor_metrics.emg.EMG_weekly_metrics.left.EMG_apdf.active.p50",
})
```

### Nested Extraction (Time Series)

```python
from oh_parser import load_profiles, extract_nested, create_filters

profiles = load_profiles()

# Filter to specific subjects and date range
filters = create_filters(
    subjects=["103", "104", "105"],
    date_range=("2024-01-01", "2024-03-31"),
)

# Extract EMG data across dates/sessions/sides
df = extract_nested(
    profiles,
    base_path="sensor_metrics.emg",
    level_names=["date", "session", "side"],
    value_paths=["EMG_intensity.mean_percent_mvc", "EMG_apdf.active.p50"],
    exclude_patterns=["EMG_daily_metrics", "EMG_weekly_metrics"],
    filters=filters,
)
```

### Exploring Profile Structure

```python
from oh_parser import load_profiles, get_profile, inspect_profile, get_available_paths

profiles = load_profiles()
profile = get_profile(profiles, "103")

# Print tree structure
inspect_profile(profile, max_depth=4)

# Get all available paths
paths = get_available_paths(profile, max_depth=6)
for p in paths[:20]:
    print(p)
```

---

## Environment

- **Python**: 3.14
- **Dependencies**: pandas, numpy, python-dateutil, pytz, tzdata
- **Virtual Environment**: `oh_parser_venv`
- **Git Repository**: `https://github.com/eLbARROS13/OH_Parser.git`

---

## Design Decisions

1. **No classes** - All functionality via pure functions
2. **Dict-based filters** - `create_filters()` returns a dict, not a dataclass
3. **Dot-notation paths** - Navigate nested JSON with strings like `"a.b.c"`
4. **Public/private separation** - Private functions prefixed with `_`
5. **Default OH directory** - CLI defaults to the standard data location

---

## Data Pipeline Flow

```
OH Profile JSON Files
        │
        ▼
   load_profiles()        ← loader.py
        │
        ▼
  Dict[subject_id, profile]
        │
        ├──► apply_subject_filters()  ← filters.py
        │
        ▼
  Filtered Profiles
        │
        ├──► resolve_path()           ← path_resolver.py
        │
        ▼
   extract() / extract_nested()       ← extract.py
        │
        ▼
   pandas DataFrame
```

---

## Notes for LLM Assistants

1. **Profile access**: Always use `get_profile(profiles, subject_id)` - returns `None` if not found
2. **Path resolution**: Use dot notation. Invalid paths return `None`, not errors
3. **Filtering**: Pass `None` for filters to skip filtering entirely
4. **Wildcards**: `extract_nested` supports `value_paths=["EMG_intensity.*"]` to extract all keys
5. **Exclude patterns**: Use `exclude_patterns=["EMG_*_metrics"]` to skip aggregated data when extracting raw sessions
