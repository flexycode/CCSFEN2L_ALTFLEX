# 💫 AltFlex: AI-Powered Forensic Framework for Exploit Detection in Web3 Cross-chain Bridges and DeFi Protocols

<!-- 🤖 Machine Learning 🤖 -->
<div align="center">
<img src="https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3N3NjdXJ1NWJ1NHZ5b2sxd2lhcXN3NDl3eHh3eTZtOWJ4dDNxdXpkaSZlcD12MV9zdGlja2Vyc19zZWFyY2gmY3Q9cw/LGz5uWk10fZi4q3hx0/giphy.gif" width="250">
<img src="https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3bXVqZjg3Z2k3N2xlOWM5NmRxcTZ0bHo3d3c1MmVlcWpsdzExNDlsYyZlcD12MV9zdGlja2Vyc19zZWFyY2gmY3Q9cw/jRUOCPIt1nJ1QwM1cK/giphy.gif" width="300">
<img src="https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3YjJpMHJjM2Jiejl0ZWNkNDFta29jbzFiejRoMHNuMHlmN2NmNm9veSZlcD12MV9zdGlja2Vyc19zZWFyY2gmY3Q9cw/wD0otRg0E3IIlN4x60/giphy.gif" width="250">
</div>

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

<!-- 🤖 Blue Pingie 🤖 -->
<div align="center">
<img src="https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3MnNjNXdxbTlyYmZodm9jamZhZjR1c3Fjdzc3djk3bW1iYTMyNDhwcyZlcD12MV9zdGlja2Vyc19yZWxhdGVkJmN0PXM/wH440SOB1dNUpweF93/giphy.gif" width="250">
<img src="https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3a3VudjJnOTZkbjJpNGV3c2ZjdHFiOXB6enpjcTU0dGJzanEwcnRwciZlcD12MV9zdGlja2Vyc19zZWFyY2gmY3Q9cw/xsrtTrbC5MxJ5ltuvj/giphy.gif" width="300">
<img src="https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3NjM5am54eWk0dWg4ZjNnc3Zka2NmcDFwOXI3dHRwcHAyam93MW9xNCZlcD12MV9zdGlja2Vyc19yZWxhdGVkJmN0PXM/RIqDQOdEJZzg2Zijvm/giphy.gif" width="250">
</div>

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

<!-- 🤖 Machine Learning 🤖 -->
<div align="center">
<img src="https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3Nmt5OThrcjRuYmlma2szdnBsNTZpbHFkbm9jOXdoMDBvbXhvcjNwbCZlcD12MV9zdGlja2Vyc19zZWFyY2gmY3Q9cw/QRaz83oxPmMefgZLiU/giphy.gif" width="250">
<img src="https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3Y2trNHM0YTN0MWhvZTIzcjA4dTl3bDBvZjYzYnBkejVuNWI1azR5YSZlcD12MV9zdGlja2Vyc19zZWFyY2gmY3Q9cw/6VG9cHMCJxlIM5guHs/giphy.gif" width="300">
<img src="https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3Nmt5OThrcjRuYmlma2szdnBsNTZpbHFkbm9jOXdoMDBvbXhvcjNwbCZlcD12MV9zdGlja2Vyc19zZWFyY2gmY3Q9cw/qP5XZwzVkmBF8odtPr/giphy.gif" width="250">
</div>


<!-- 🏆 Contributers down below -->
# 🏆 Contributing     

### Contributing     
If you would like to contribute to the Flight Booking App, please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them.
4. Push your changes to your forked repository.
5. Submit a pull request to the main repository.


### 🧠 Submitting Changes

🧠 Contributions are welcome! If you have ideas for improvements or want to add more exercises, follow these steps:

1. Fork the repository.
2. Create a new branch.
3. Make your changes and commit them.
4. Push to your fork and submit a pull request. 💕💕💕💕

<!-- Contributors down below, kindly paste your github URL thanks and also you can revise your suited job title position -->
### 👋 Contributors
### Special thanks to all my groupmates: 
 * ####  😎 [Jay Arre Talosig](https://github.com/flexycode) - Machine Learning Engineer | Blockchain Developer | AI Architect    
 * ####  🕵️‍♀️ [Rinoah Venedict Dela Rama](https://github.com/Noah-dev2217) - Python Developer | QA Engineer | Data Engineer 
 * ####  🕵️ [Alexander Castilo](https://github.com/xandercastillo0904) - Penetration Tester | Software Engineer | Threat Researcher
 * ####  🥷 [Nicko Nehcterg Dalida](https://github.com/nicknicndin) - Digital Forensics Analyst | QA Engineer | Smart Contract Auditor
 * ####  🧑‍💻 [Mark Jhosua Taberna](https://github.com/MjTaberna) - Digital Forensics Analyst | UI Specialist | Full Stack Engineer


# 🛸 FAQ
<!--  Reporting issues -->
### 🛸 Reporting Issues

```bash
Some changes need to be address
- TBA
- TBA
- TBA
```

# 📫 Changelogs 
Chronological list of updates, bug fixes, new features, and other modifications for our Software Engineering Project.

## 💻 [01.0.0] - 2025-11-17      
### Role & Project Management
- 💻 Final Project requirements for our project

## 💻 [01.1.0] - 2025-11-24      
### Role & Project Management
- 💻 Construct the important folder in the overall 

## 💻 [02.0.0] - 2025-11-25      
### Development Progress
- 💻 TBA

### Commit message for pushing or pull-request  
🧊 CCSFEN2L ALTFLEX

<!-- This comment is intended for commiting message in pull-request 
Always use this "🧊 Flight Booking" for commiting message for "Pull-request"
<!-- End point line for this comment  -->

<!-- Introduction Pannel button link, it will redirect to the top -->
#### [Back to Table of Content](#-introduction)

<!-- End point line insert Thanks for visiting enjoy your day, feel free to modify this  -->
---
<p align="center">
<img src="https://readme-typing-svg.demolab.com/?lines=Thanks+For+Visiting+Enjoy+Your+Day+~!;" alt="mystreak"/>
</p>

<!-- Software Engineering -->
<div align="center">
<img src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMnhvYXlpOXRveHR2YXFqY2xvMGhneXpvNWE3cDY2OXk3amZnam05NCZlcD12MV9zdGlja2Vyc19zZWFyY2gmY3Q9cw/eZBJ45h3X2ti2vM6Do/giphy.gif" width="300">
<img src="https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3emdwbHV4dWJkam1sd2tkbmdndGxtZ2ZkNGYzeHNzbHlvZTZlaXllNyZlcD12MV9zdGlja2Vyc19zZWFyY2gmY3Q9cw/19Oq26zZQ6ONnhjLx4/giphy.gif" width="300">
</div>

<!-- End point line insert Comeback again next time, feel free to modify this  -->
<p align="center">
<img src="https://readme-typing-svg.demolab.com/?lines=Come+Back+Again+next+time" alt="mystreak"/>
</p>

</p>
    
<br>
<!-- End point insert background effect line of sight color red -->
<img src="https://user-images.githubusercontent.com/74038190/212284100-561aa473-3905-4a80-b561-0d28506553ee.gif" width="1000">


   


