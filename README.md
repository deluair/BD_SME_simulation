# Bangladesh SME Sector Simulation (2025-2035)

A Python-based agent-based simulation modeling the dynamics of the Small and Medium Enterprise (SME) ecosystem in Bangladesh.

## Overview

This project simulates the evolution of a population of Bangladeshi SMEs under different policy scenarios between 2025 and 2035. It models various factors influencing SME performance, including financing, technology adoption, market access, human capital, regulation, innovation, sustainability, resilience, internationalization, and inclusion. The simulation compares outcomes across defined scenarios (e.g., 'baseline', 'pro_investment', 'digital_leap') to assess potential policy impacts.

## Project Structure

- `main.py`: Main simulation execution script. Runs scenarios defined in `config.yaml`.
- `reporting.py`: Generates comparative plots and an HTML summary report from simulation results.
- `config.yaml`: Configuration file for simulation parameters, scenario definitions, and model settings.
- `requirements.txt`: Project dependencies.
- `models/`: Directory containing the core simulation component models (Agent-Based Models for different dynamics).
- `data_handler.py`: Module for loading and managing data (currently configured for synthetic data generation).
- `output/`: Directory where simulation results and reports are saved.
  - `*.pkl`: Pickled pandas DataFrames containing detailed simulation results for each scenario.
  - `plots/`: Directory containing comparative plots saved as PNG images.
  - `simulation_report.html`: HTML report summarizing results and embedding plots.
- `data/`: Placeholder for storing static data files (if needed in the future).
- `notebooks/`: Jupyter notebooks for analysis, visualization, and experimentation (optional).
- `tests/`: Unit and integration tests (optional).
- `README.md`: This file.

## Core Model Components (in `models/`)

The simulation incorporates distinct models for:

- SME Segmentation & Demographics
- Financing and Capital Access
- Technology Adoption
- Market Access & Supply Chains
- Human Capital & Skills
- Regulatory Environment & Compliance
- Business Environment & Infrastructure
- Innovation & Product Development
- Sustainability & Green Transition
- Resilience & Risk Management
- Internationalization & Exports
- Inclusion & Diversity

## Getting Started

1. Clone the repository:

```bash
git clone https://github.com/deluair/BD_SME_simulation.git
cd BD_SME_simulation
```

2. Create and activate a virtual environment:

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Configure Simulation (Optional): Modify `config.yaml` to adjust parameters like the simulation duration, number of SMEs (`num_synthetic_smes`), model parameters, or scenario definitions.

2. Run Simulation: Execute the main script. This will run all scenarios defined in the config and save results to the `output/` directory.

```bash
python main.py
```

*(Note: Running with a large number of SMEs, e.g., 100,000, can take significant time.)*

3. Generate Report: After the simulation completes, run the reporting script.

```bash
python reporting.py
```

This generates comparative plots in `output/plots/` and a summary report at `output/simulation_report.html`.

4. View Results: Open `output/simulation_report.html` in a web browser to view the comparative plots and summary statistics.
