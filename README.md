# Market Psychology Intelligence System (MPIS)

MPIS is a research platform skeleton for building long-lived quantitative
trading systems focused on measuring and fusing market psychology signals.

Project status: repository initialized with project layout, tooling, and
minimal package code and tests.

Key features
- Python 3.12+ ready
- Type-hinted, dataclass-based configuration
- Ruff and Black formatting configuration
- Pytest test harness and CI workflow

Installation
1. Create a virtual environment (Python 3.12+):

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

Running
- Run tests: `pytest`

Repository layout

MPIS
│
├── src/mpis/           # Package source
│   ├── config/         # Configuration dataclasses and loaders
│   ├── models/         # Domain models and data classes
│   ├── data/           # Data ingestion and processing
│   ├── replay/         # Market data replay utilities
│   ├── rules/          # Rule-based signal definitions
│   ├── psychology/     # Behavioral signal implementations
│   ├── fusion/         # Signal fusion and ensemble logic
│   ├── analytics/      # Analysis tools and metrics
│   ├── dashboard/      # Streamlit or web dashboard code
│   ├── live/           # Live trading connectors (placeholders)
│   ├── institutional/  # Institutional data adapters
│   ├── options/        # Options-specific modules
│   └── utils/          # Small utilities and helpers
├── tests/              # Pytest test suite
├── docs/               # Project documentation
├── notebooks/          # Research notebooks
├── data/               # Data storage (historical, cache, etc.)
├── configs/            # Configuration files and secrets (gitignored)
├── reports/            # Generated reports and artifacts
├── .github/            # CI workflows
├── pyproject.toml
├── requirements.txt
└── README.md

Roadmap
- Expand `models` with typed data classes for market events
- Implement signal extraction in `psychology` and `analytics`
- Add reproducible backtesting and replay tools

License
This project is licensed under the MIT License - see the `LICENSE` file.
