# AltFlex: AI & Digital Forensics Framework

## A. Project Overview
AltFlex is an integrated AI and digital forensics framework designed to proactively detect and analyze security exploits in cross-chain bridges and DeFi protocols. By combining machine learning anomaly detection with blockchain forensic analysis, the system provides a comprehensive security solution for the rapidly evolving Web3 ecosystem.

## B. Problem Statement
DeFi protocols and cross-chain bridges are increasingly vulnerable to exploits, resulting in significant financial losses. Current security measures often lack the agility and intelligence to detect sophisticated attack vectors. AltFlex addresses this critical need by providing a proactive and adaptive solution for identifying and mitigating potential exploits using advanced AI/ML techniques.

## C. Objectives
**Primary Objective:**
- Develop a functional AI-powered forensic framework (AltFlex) for automated exploit detection in DeFi and cross-chain environments.

**Secondary Objectives:**
- Implement machine learning models for anomaly detection and pattern recognition in transaction data.
- Create a user-friendly interface for visualizing forensic analysis results.
- Establish a comprehensive database of known exploit signatures and attack patterns.
- Evaluate the framework's effectiveness through rigorous testing and validation against real-world exploit scenarios.

## D. Methodology
The project will be executed in the following phases:
1. **Data Collection**: Gather historical transaction data, smart contract code, and exploit reports.
2. **Data Preprocessing**: Clean, transform, and normalize collected data.
3. **Model Development**: Develop and train AI/ML models for anomaly detection and pattern recognition.
4. **Framework Implementation**: Integrate models into the AltFlex framework with UI and visualization.
5. **Testing and Validation**: Evaluate performance against simulated and real-world scenarios.
6. **Integration and Testing**: Deploy and test in sandboxed blockchain environments.

## E. Conclusion
AltFlex addresses a critical gap in Web3 security through an innovative combination of artificial intelligence and digital forensics. The proposed framework provides a foundation for proactive security monitoring and comprehensive incident analysis.

---

## F. Project Structure

### Root Directory: `CCSFEN2L-ALTFLEX/`

#### 1. Configuration & Setup
- **`.devcontainer/`**
  - **Purpose**: Contains configuration files for Visual Studio Code Remote - Containers.
  - **Function**: Automates the setup of the development environment.
  - **Key Files**: `devcontainer.json`, `Dockerfile`.

- **`docker-compose.yml`**
  - **Purpose**: Container orchestration configuration.
  - **Function**: Defines the services required to run the full AltFlex application stack.

- **`README.md`**
  - **Purpose**: The central documentation hub ("The Bible") of the project.

#### 2. Data Management
- **`data/`**
  - **Purpose**: Storage for raw and processed forensic datasets.
  - **Note**: Managed via **GitLFS**.

#### 3. Source Code (`src/`)
- **`src/collectors/`**
  - **Purpose**: Data ingestion layer (Python scripts for scraping/fetching data).
- **`src/forensics/`**
  - **Purpose**: Rule-based detection engine (Signature matching, static analysis).
- **`src/models/`**
  - **Purpose**: Machine Learning engine (GNN, XGBoost models).
- **`src/app/`**
  - **Purpose**: User Interface and API layer (Streamlit, FastAPI).

#### 4. Research & Experimentation
- **`notebooks/`**
  - **Purpose**: Sandbox for research and prototyping (Jupyter notebooks).

#### 5. Quality Assurance
- **`tests/`**
  - **Purpose**: Automated testing suite.

---

## G. Getting Started

### Access Links
Once the application is running, you can access the services at:
- **Dashboard (Streamlit)**: [http://localhost:8501](http://localhost:8501)
- **API (FastAPI)**: [http://localhost:8000](http://localhost:8000)

### Option 1: Running Locally (Recommended if Docker fails)
Prerequisites: Python 3.10+

1. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Mac/Linux:
   source .venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   Run the API and Dashboard in separate terminals:
   ```bash
   # Terminal 1: API
   uvicorn src.app.main:app --reload

   # Terminal 2: Dashboard
   streamlit run src/app/dashboard.py
   ```

### Option 2: Running with Docker
1. **Build and start services:**
   ```bash
   docker-compose up -d --build
   ```
2. **Stop services:**
   ```bash
   docker-compose down
   ```
