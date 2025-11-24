# AltFlex Project Structure Documentation

This document outlines the directory structure and the specific purpose of each file and folder within the AltFlex project. This structure is designed to support the development of an AI-powered forensic framework for DeFi and cross-chain environments.

## Root Directory: `CCSFEN2L-ALTFLEX/`

### 1. Configuration & Setup
- **`.devcontainer/`**
  - **Purpose**: Contains configuration files for Visual Studio Code Remote - Containers.
  - **Function**: Automates the setup of the development environment, ensuring all team members (Forensics, Models, Research) have a consistent, reproducible environment with all necessary dependencies pre-installed.
  - **Key Files**: `devcontainer.json`, `Dockerfile`.

- **`docker-compose.yml`**
  - **Purpose**: Container orchestration configuration.
  - **Function**: Defines the services required to run the full AltFlex application stack (e.g., the API, the dashboard, database services) with a single command. Enables "One click startup" for testing and deployment.

- **`README.md`**
  - **Purpose**: The central documentation hub ("The Bible") of the project.
  - **Function**: Contains the Project Overview, Problem Statement, Objectives, Methodology, setup instructions, and contribution guidelines. It serves as the primary entry point for anyone new to the project.

### 2. Data Management
- **`data/`**
  - **Purpose**: Storage for raw and processed forensic datasets.
  - **Function**: Houses historical transaction data, smart contract code, and exploit reports.
  - **Note**: Managed via **GitLFS** (Large File Storage) due to the size of blockchain datasets.
  - **Contents**:
    - Raw CSV/JSON dumps from Etherscan/PolygonScan.
    - Cleaned datasets ready for model training.

### 3. Source Code (`src/`)
The core logic of the application, organized by functional area.

- **`src/collectors/`**
  - **Purpose**: Data ingestion layer.
  - **Function**: Python scripts designed to scrape and fetch data from external blockchain explorers and RPC nodes.
  - **Key Tasks**:
    - Fetching transaction histories from Etherscan/PolygonScan.
    - Monitoring cross-chain bridge events.

- **`src/forensics/`**
  - **Purpose**: Rule-based detection engine (Team's Area).
  - **Function**: Implements deterministic logic and heuristics to identify known attack patterns.
  - **Key Tasks**:
    - Signature matching for known exploits.
    - Static analysis of smart contract bytecode.

- **`src/models/`**
  - **Purpose**: Machine Learning engine (Your Area).
  - **Function**: Houses the logic for training and inference of AI models.
  - **Key Technologies**: Graph Neural Networks (GNN) for transaction graph analysis, XGBoost for tabular anomaly detection.
  - **Key Tasks**:
    - Feature engineering from raw blockchain data.
    - Model training pipelines.
    - Anomaly detection algorithms.

- **`src/app/`**
  - **Purpose**: User Interface and API layer.
  - **Function**: The user-facing component of AltFlex.
  - **Key Technologies**: Streamlit for the visualization dashboard, FastAPI for the backend API.
  - **Key Tasks**:
    - Visualizing forensic analysis results.
    - Serving model predictions via API endpoints.

### 4. Research & Experimentation
- **`notebooks/`**
  - **Purpose**: Sandbox for research and prototyping (Research Area).
  - **Function**: Jupyter notebooks used for exploratory data analysis (EDA), testing new model architectures, and visualizing data distributions before implementing them in production code (`src/`).

### 5. Quality Assurance
- **`tests/`**
  - **Purpose**: Automated testing suite.
  - **Function**: Ensures code reliability and prevents regressions. REQUIRED for Software Engineering compliance.
  - **Contents**:
    - Unit tests for individual functions (collectors, parsers).
    - Integration tests for the full pipeline (data -> model -> api).
