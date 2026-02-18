# ELIS v2.0.0 Functional Qualification Report

Candidate SHA: 6c60febea2ce8d8abfedac25d7994081b852ef3f
Date: 2026-02-18
Executor: CODEX

## Summary Verdict
FAIL

## Suite Results
| Suite | Result | Notes |
|---|---|---|
| FT-01 | FAIL | CLI contract partly passes help/arg checks, but `elis validate DOES_NOT_EXIST.json` crashes with `ModuleNotFoundError: No module named 'scripts'`. |
| FT-02 | NOT RUN | Pre-FT-02 secrets gate failed (`SCOPUS_API_KEY`, `ELIS_CONTACT` missing). |
| FT-03 | NOT RUN | Stopped after FT-01 failure per execution constraint. |
| FT-04 | NOT RUN | Stopped after FT-01 failure per execution constraint. |
| FT-05 | NOT RUN | Stopped after FT-01 failure per execution constraint. |
| FT-06 | NOT RUN | Stopped after FT-01 failure per execution constraint. |
| FT-07 | NOT RUN | Stopped after FT-01 failure per execution constraint. |
| FT-08 | NOT RUN | Stopped after FT-01 failure per execution constraint. |
| FT-09 | NOT RUN | Stopped after FT-01 failure per execution constraint. |
| FT-10 | NOT RUN | Stopped after FT-01 failure per execution constraint. |
| FT-11 | NOT RUN | Stopped after FT-01 failure per execution constraint. |
| FT-12 | NOT RUN | Stopped after FT-01 failure per execution constraint. |

## Blocking Findings
1. FT-01 failure: `elis validate DOES_NOT_EXIST.json` does not return a controlled CLI validation error; it crashes with `ModuleNotFoundError: No module named 'scripts'`.
2. Pre-FT-02 gate failure: required environment secrets missing (`SCOPUS_API_KEY`, `ELIS_CONTACT`).

## Non-Blocking Findings
1. None recorded in this halted run.

## Decision
NO-GO for v2.0.0 tag

## Execution Evidence

### Preflight Pin Check
```text
$ git rev-parse HEAD
6c60febea2ce8d8abfedac25d7994081b852ef3f
```

### Environment Setup (per plan §3)
Artifact: `reports/ft/setup/00_environment_setup.log.txt`

```text
$ python -m venv .venv
ExitCode: 0
Output:

`n$ .\.venv\Scripts\python -m pip install -U pip
ExitCode: 0
Output:
Requirement already satisfied: pip in .\.venv\Lib\site-packages (26.0.1)

`n$ .\.venv\Scripts\python -m pip install -e ".[dev]"
ExitCode: 0
Output:
Obtaining file:///C:/Users/carlo/ELIS-SLR-Agent
  Installing build dependencies: started
  Installing build dependencies: finished with status 'done'
  Checking if build backend supports build_editable: started
  Checking if build backend supports build_editable: finished with status 'done'
  Getting requirements to build editable: started
  Getting requirements to build editable: finished with status 'done'
  Preparing editable metadata (pyproject.toml): started
  Preparing editable metadata (pyproject.toml): finished with status 'done'
Requirement already satisfied: jsonschema==4.23.0 in .\.venv\Lib\site-packages (from elis-slr-agent==2.0.0) (4.23.0)
Requirement already satisfied: requests==2.31.0 in .\.venv\Lib\site-packages (from elis-slr-agent==2.0.0) (2.31.0)
Requirement already satisfied: PyYAML==6.0.2 in .\.venv\Lib\site-packages (from elis-slr-agent==2.0.0) (6.0.2)
Requirement already satisfied: black in .\.venv\Lib\site-packages (from elis-slr-agent==2.0.0) (24.8.0)
Requirement already satisfied: ruff in .\.venv\Lib\site-packages (from elis-slr-agent==2.0.0) (0.6.9)
Requirement already satisfied: pytest in .\.venv\Lib\site-packages (from elis-slr-agent==2.0.0) (9.0.1)
Requirement already satisfied: attrs>=22.2.0 in .\.venv\Lib\site-packages (from jsonschema==4.23.0->elis-slr-agent==2.0.0) (25.4.0)
Requirement already satisfied: jsonschema-specifications>=2023.03.6 in .\.venv\Lib\site-packages (from jsonschema==4.23.0->elis-slr-agent==2.0.0) (2025.9.1)
Requirement already satisfied: referencing>=0.28.4 in .\.venv\Lib\site-packages (from jsonschema==4.23.0->elis-slr-agent==2.0.0) (0.37.0)
Requirement already satisfied: rpds-py>=0.7.1 in .\.venv\Lib\site-packages (from jsonschema==4.23.0->elis-slr-agent==2.0.0) (0.28.0)
Requirement already satisfied: charset-normalizer<4,>=2 in .\.venv\Lib\site-packages (from requests==2.31.0->elis-slr-agent==2.0.0) (3.4.4)
Requirement already satisfied: idna<4,>=2.5 in .\.venv\Lib\site-packages (from requests==2.31.0->elis-slr-agent==2.0.0) (3.11)
Requirement already satisfied: urllib3<3,>=1.21.1 in .\.venv\Lib\site-packages (from requests==2.31.0->elis-slr-agent==2.0.0) (2.5.0)
Requirement already satisfied: certifi>=2017.4.17 in .\.venv\Lib\site-packages (from requests==2.31.0->elis-slr-agent==2.0.0) (2025.11.12)
Requirement already satisfied: click>=8.0.0 in .\.venv\Lib\site-packages (from black->elis-slr-agent==2.0.0) (8.3.0)
Requirement already satisfied: mypy-extensions>=0.4.3 in .\.venv\Lib\site-packages (from black->elis-slr-agent==2.0.0) (1.1.0)
Requirement already satisfied: packaging>=22.0 in .\.venv\Lib\site-packages (from black->elis-slr-agent==2.0.0) (25.0)
Requirement already satisfied: pathspec>=0.9.0 in .\.venv\Lib\site-packages (from black->elis-slr-agent==2.0.0) (0.12.1)
Requirement already satisfied: platformdirs>=2 in .\.venv\Lib\site-packages (from black->elis-slr-agent==2.0.0) (4.5.0)
Requirement already satisfied: colorama in .\.venv\Lib\site-packages (from click>=8.0.0->black->elis-slr-agent==2.0.0) (0.4.6)
Requirement already satisfied: iniconfig>=1.0.1 in .\.venv\Lib\site-packages (from pytest->elis-slr-agent==2.0.0) (2.3.0)
Requirement already satisfied: pluggy<2,>=1.5 in .\.venv\Lib\site-packages (from pytest->elis-slr-agent==2.0.0) (1.6.0)
Requirement already satisfied: pygments>=2.7.2 in .\.venv\Lib\site-packages (from pytest->elis-slr-agent==2.0.0) (2.19.2)
Building wheels for collected packages: elis-slr-agent
  Building editable for elis-slr-agent (pyproject.toml): started
  Building editable for elis-slr-agent (pyproject.toml): finished with status 'done'
  Created wheel for elis-slr-agent: filename=elis_slr_agent-2.0.0-0.editable-py3-none-any.whl size=3099 sha256=4a0e2b078f4ee04b6ee4b460ad186ff9262b139bb973ea4807464de8d4fd0820
  Stored in directory: C:\Users\carlo\AppData\Local\Temp\pip-ephem-wheel-cache-477cwpfp\wheels\ee\93\c5\aeabeb4ac85bbca275337b450409549be93d92b94d71efcd82
Successfully built elis-slr-agent
Installing collected packages: elis-slr-agent
  Attempting uninstall: elis-slr-agent
    Found existing installation: elis-slr-agent 0.3.0
    Uninstalling elis-slr-agent-0.3.0:
      Successfully uninstalled elis-slr-agent-0.3.0
Successfully installed elis-slr-agent-2.0.0


```

### FT-01: CLI Contract
Artefacts:
- `reports/ft/FT-01/01.log.txt`
- `reports/ft/FT-01/02.log.txt`
- `reports/ft/FT-01/03.log.txt`
- `reports/ft/FT-01/04.log.txt`
- `reports/ft/FT-01/05.log.txt`
- `reports/ft/FT-01/06.log.txt`
- `reports/ft/FT-01/07.log.txt`
- `reports/ft/FT-01/08.log.txt`
- `reports/ft/FT-01/09.log.txt`
- `reports/ft/FT-01/10.log.txt`
- `reports/ft/FT-01/11.log.txt`

### 01.log.txt

```text
$ .\\.venv\\Scripts\\elis --help
ExitCode: 0
Output:
usage: elis [-h]
            {validate,harvest,merge,dedup,screen,agentic,export-latest} ...

ELIS SLR Agent CLI

positional arguments:
  {validate,harvest,merge,dedup,screen,agentic,export-latest}
    validate            Validate JSON data against schema or run legacy full
                        validation
    harvest             Harvest records from an academic source
    merge               Merge per-source Appendix A outputs into canonical
                        Appendix A
    dedup               Deduplicate canonical Appendix A (PE4)
    screen              Screen canonical Appendix A into Appendix B
    agentic             Agentic sidecar workflows (PE5)
    export-latest       Copy canonical artefacts from runs/<run_id>/ to
                        json_jsonl/ (backward-compat export)

options:
  -h, --help            show this help message and exit


```

### 02.log.txt

```text
$ .\\.venv\\Scripts\\elis harvest --help
ExitCode: 0
Output:
usage: elis harvest [-h] [--search-config SEARCH_CONFIG]
                    [--tier {testing,pilot,benchmark,production,exhaustive}]
                    [--max-results MAX_RESULTS] [--output OUTPUT]
                    source

positional arguments:
  source                Source to harvest from (e.g. openalex, crossref,
                        scopus)

options:
  -h, --help            show this help message and exit
  --search-config SEARCH_CONFIG
                        Path to search configuration YAML
  --tier {testing,pilot,benchmark,production,exhaustive}
                        Max-results tier
  --max-results MAX_RESULTS
                        Override max_results regardless of config or tier
  --output OUTPUT       Output file path (default:
                        json_jsonl/ELIS_Appendix_A_Search_rows.json)


```

### 03.log.txt

```text
$ .\\.venv\\Scripts\\elis merge --help
ExitCode: 0
Output:
usage: elis merge [-h] [--inputs INPUTS [INPUTS ...]]
                  [--from-manifest FROM_MANIFEST] [--output OUTPUT]
                  [--report REPORT]

options:
  -h, --help            show this help message and exit
  --inputs INPUTS [INPUTS ...]
                        Input JSON/JSONL files to merge
  --from-manifest FROM_MANIFEST
                        Run manifest path to read input_paths from (used when
                        --inputs is omitted)
  --output OUTPUT       Merged Appendix A output file path
  --report REPORT       Merge report output path


```

### 04.log.txt

```text
$ .\\.venv\\Scripts\\elis dedup --help
ExitCode: 0
Output:
usage: elis dedup [-h] [--input INPUT] [--output OUTPUT] [--report REPORT]
                  [--fuzzy] [--threshold THRESHOLD] [--config CONFIG_PATH]
                  [--duplicates DUPLICATES_PATH]

options:
  -h, --help            show this help message and exit
  --input INPUT         Merged Appendix A input file
  --output OUTPUT       Deduped Appendix A output path
  --report REPORT       Dedup report output path
  --fuzzy               Enable fuzzy title-based deduplication (opt-in)
  --threshold THRESHOLD
                        Similarity threshold for fuzzy mode (default: 0.85)
  --config CONFIG_PATH  Path to sources.yml for keeper priority
  --duplicates DUPLICATES_PATH
                        JSONL sidecar for dropped records with cluster_id +
                        duplicate_of


```

### 05.log.txt

```text
$ .\\.venv\\Scripts\\elis screen --help
ExitCode: 0
Output:
usage: elis screen [-h] [--input INPUT] [--output OUTPUT]
                   [--year-from YEAR_FROM] [--year-to YEAR_TO]
                   [--languages LANGUAGES] [--allow-unknown-language]
                   [--enforce-preprint-policy] [--dry-run]

options:
  -h, --help            show this help message and exit
  --input INPUT         Path to canonical Appendix A JSON array
  --output OUTPUT       Path to write canonical Appendix B JSON array
  --year-from YEAR_FROM
                        Lower bound (inclusive). If omitted, read from
                        Appendix A _meta.
  --year-to YEAR_TO     Upper bound (inclusive). If omitted, read from
                        Appendix A _meta.
  --languages LANGUAGES
                        Comma-separated ISO codes. If omitted, read from
                        Appendix A _meta.
  --allow-unknown-language
                        Keep records where language is missing/unknown.
  --enforce-preprint-policy
                        Respect per-topic include_preprints flags.
  --dry-run             Compute screening but do not write output.


```

### 06.log.txt

```text
$ .\\.venv\\Scripts\\elis validate --help
ExitCode: 0
Output:
usage: elis validate [-h] [schema_path] [json_path]

positional arguments:
  schema_path  Path to JSON schema
  json_path    Path to JSON data file

options:
  -h, --help   show this help message and exit


```

### 07.log.txt

```text
$ .\\.venv\\Scripts\\elis agentic asta discover --help
ExitCode: 0
Output:
usage: elis agentic asta discover [-h] --query QUERY --run-id RUN_ID
                                  [--output OUTPUT] [--config CONFIG_PATH]
                                  [--limit LIMIT]

options:
  -h, --help            show this help message and exit
  --query QUERY         Discovery query text
  --run-id RUN_ID       Run identifier
  --output OUTPUT       Optional output path (default under
                        runs/<run_id>/agentic/asta/)
  --config CONFIG_PATH  Path to ASTA config
  --limit LIMIT         Candidate limit (default: 100)


```

### 08.log.txt

```text
$ .\\.venv\\Scripts\\elis agentic asta enrich --help
ExitCode: 0
Output:
usage: elis agentic asta enrich [-h] --input INPUT_PATH --run-id RUN_ID
                                [--output OUTPUT] [--config CONFIG_PATH]
                                [--limit LIMIT]

options:
  -h, --help            show this help message and exit
  --input INPUT_PATH    Input records file (JSON/JSONL)
  --run-id RUN_ID       Run identifier
  --output OUTPUT       Optional output path (default under
                        runs/<run_id>/agentic/asta/)
  --config CONFIG_PATH  Path to ASTA config
  --limit LIMIT         Snippet limit per record (default: 20)


```

### 09.log.txt

```text
$ .\\.venv\\Scripts\\elis merge
ExitCode: 1
Output:
Provide --inputs or --from-manifest.


```

### 10.log.txt

```text
$ .\\.venv\\Scripts\\elis merge --from-manifest DOES_NOT_EXIST.json
ExitCode: 1
Output:
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "C:\Users\carlo\ELIS-SLR-Agent\.venv\Scripts\elis.exe\__main__.py", line 5, in <module>
    sys.exit(main())
             ~~~~^^
  File "C:\Users\carlo\ELIS-SLR-Agent\elis\cli.py", line 723, in main
    return args.func(args)
           ~~~~~~~~~^^^^^^
  File "C:\Users\carlo\ELIS-SLR-Agent\elis\cli.py", line 252, in _run_merge
    inputs = _resolve_merge_inputs(args)
  File "C:\Users\carlo\ELIS-SLR-Agent\elis\cli.py", line 60, in _resolve_merge_inputs
    return _load_inputs_from_manifest(args.from_manifest)
  File "C:\Users\carlo\ELIS-SLR-Agent\elis\cli.py", line 43, in _load_inputs_from_manifest
    payload = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
                         ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^
  File "C:\Users\carlo\AppData\Local\Python\pythoncore-3.14-64\Lib\pathlib\__init__.py", line 792, in read_text
    with self.open(mode='r', encoding=encoding, errors=errors, newline=newline) as f:
         ~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\carlo\AppData\Local\Python\pythoncore-3.14-64\Lib\pathlib\__init__.py", line 776, in open
    return io.open(self, mode, buffering, encoding, errors, newline)
           ~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: 'DOES_NOT_EXIST.json'


```

### 11.log.txt

```text
$ .\\.venv\\Scripts\\elis validate DOES_NOT_EXIST.json
ExitCode: 1
Output:
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "C:\Users\carlo\ELIS-SLR-Agent\.venv\Scripts\elis.exe\__main__.py", line 5, in <module>
    sys.exit(main())
             ~~~~^^
  File "C:\Users\carlo\ELIS-SLR-Agent\elis\cli.py", line 723, in main
    return args.func(args)
           ~~~~~~~~~^^^^^^
  File "C:\Users\carlo\ELIS-SLR-Agent\elis\cli.py", line 66, in _run_validate
    from scripts._archive.validate_json import (
    ...<2 lines>...
    )
ModuleNotFoundError: No module named 'scripts'


```



### Gate Check Before FT-02
Artifact: `reports/ft/gate/pre_ft02_secrets_check.log.txt`

```text
$ env secrets gate check
SCOPUS_API_KEY=<MISSING>
ELIS_CONTACT=<MISSING>
SCOPUS_INST_TOKEN=<MISSING> (tenant-conditional)
GATE_RESULT=FAIL
MISSING_REQUIRED=SCOPUS_API_KEY,ELIS_CONTACT

```

### FT-02 through FT-12
Not executed due stop conditions above.
