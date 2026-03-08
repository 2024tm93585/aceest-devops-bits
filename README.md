# ACEest Fitness & Gym — DevOps CI/CD Project

> **Course:** Introduction to DevOps (CSIZG514 / SEZG514 / SEUSZG514) — S2-25
> **Student ID:** 2024TM93585
> **Assignment 1:** Implementing Automated CI/CD Pipelines

---

## Application Overview

ACEest Fitness & Gym is a Flask REST API converted from a Python Tkinter desktop application (versions 1.0 through 3.2.4). The application manages gym clients, fitness programs, workout tracking, and membership status.

### Version Evolution (Git History)

| Version | Features Added |
|---------|---------------|
| v1.0 | Basic program display (Fat Loss, Muscle Gain, Beginner) |
| v1.1 | Client profile form, calorie calculator, weekly adherence slider |
| v1.1.2 | CSV export, matplotlib progress chart, multi-client table |
| v2.0.1 | SQLite persistence, save/load client data |
| v2.1.2 | Weekly progress logging to database |
| v2.2.1 | Progress chart visualization |
| v2.2.4 | Enhanced client management and reports |
| v3.0.1 | Role-based login screen |
| v3.1.2 | Workout logging tab, exercise tracking |
| v3.2.4 | Full Tkinter version — AI program generator, PDF reports, membership billing |
| **Flask** | **Converted to REST API for DevOps deployment** |

---

## Repository Structure

```
2024tm93585/
├── app.py                        ← Flask REST API (converted from Aceestver-3.2.4)
├── requirements.txt              ← Python dependencies
├── Dockerfile                    ← Multi-stage Docker build
├── Jenkinsfile                   ← Jenkins BUILD pipeline (6 stages)
├── README.md                     ← This file
├── .github/
│   └── workflows/
│       └── main.yml              ← GitHub Actions CI/CD (3 jobs)
└── tests/
    ├── __init__.py
    └── test_app.py               ← Pytest suite (28 tests)
```

---

## Local Setup & Execution Instructions

### Prerequisites
- Python 3.10 or higher
- pip
- Docker Desktop (for containerisation)
- Git

### Step 1 — Clone the Repository
```bash
git clone https://github.com/ashokbh/2024tm93585.git
cd 2024tm93585
```

### Step 2 — Create a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### Step 3 — Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Run the Application
```bash
python app.py
```

The API starts at **http://localhost:5000**

### Step 5 — Verify the App
Open **http://localhost:5000** in your browser to see the landing page.

```bash
curl http://localhost:5000/health
# Response: {"status": "healthy", "app": "ACEest Fitness & Gym"}
```

### Default Login
| Username | Password |
|----------|----------|
| admin    | admin123 |

---

## Steps to Run Tests Manually

### Run Full Test Suite
```bash
source venv/bin/activate
pytest tests/ -v
```

### Run with Coverage Report
```bash
pytest tests/ -v --cov=app --cov-report=term-missing
```

### Run a Specific Test
```bash
pytest tests/test_app.py::test_create_client_valid -v
```

### Expected Output (28 tests)
```
tests/test_app.py::test_health_check                  PASSED
tests/test_app.py::test_login_valid_credentials       PASSED
tests/test_app.py::test_login_invalid_credentials     PASSED
tests/test_app.py::test_login_missing_fields          PASSED
tests/test_app.py::test_list_clients_empty            PASSED
tests/test_app.py::test_create_client_valid           PASSED
tests/test_app.py::test_create_client_duplicate       PASSED
tests/test_app.py::test_create_client_missing_program PASSED
tests/test_app.py::test_create_client_invalid_program PASSED
tests/test_app.py::test_get_client_exists             PASSED
tests/test_app.py::test_get_client_not_found          PASSED
tests/test_app.py::test_update_client                 PASSED
tests/test_app.py::test_delete_client                 PASSED
tests/test_app.py::test_list_programs                 PASSED
tests/test_app.py::test_get_program_detail            PASSED
tests/test_app.py::test_get_program_not_found         PASSED
tests/test_app.py::test_log_progress_valid            PASSED
tests/test_app.py::test_log_progress_invalid_adherence PASSED
tests/test_app.py::test_get_progress                  PASSED
tests/test_app.py::test_log_workout                   PASSED
tests/test_app.py::test_get_workouts                  PASSED
tests/test_app.py::test_check_membership              PASSED
tests/test_app.py::test_check_membership_not_found    PASSED
tests/test_app.py::test_calorie_calculation_fat_loss  PASSED
tests/test_app.py::test_calorie_calculation_muscle_gain PASSED
tests/test_app.py::test_calorie_calculation_beginner  PASSED
============= 26 passed =============
```

---

## Docker Usage

### Build the Image
```bash
docker build -t aceest-fitness:latest .
```

### Run the Container
```bash
docker run -d --name aceest -p 5000:5000 aceest-fitness:latest
```

### Verify
```bash
curl http://localhost:5000/health
```

### View Logs
```bash
docker logs aceest
```

### Stop and Remove
```bash
docker stop aceest && docker rm aceest
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | HTML landing page |
| GET | `/health` | Health check |
| POST | `/api/login` | Login `{"username":"admin","password":"admin123"}` |
| POST | `/api/logout` | Logout |
| GET | `/api/clients` | List all clients |
| POST | `/api/clients` | Create client |
| GET | `/api/clients/<name>` | Get client |
| PUT | `/api/clients/<name>` | Update client |
| DELETE | `/api/clients/<name>` | Delete client |
| GET | `/api/programs` | List all programs |
| GET | `/api/programs/<name>` | Program detail |
| GET | `/api/clients/<name>/progress` | Get progress history |
| POST | `/api/clients/<name>/progress` | Log weekly adherence `{"adherence":85}` |
| GET | `/api/clients/<name>/workouts` | Get workout log |
| POST | `/api/clients/<name>/workouts` | Log workout |
| GET | `/api/clients/<name>/membership` | Check membership status |

---

## GitHub Actions Integration Logic

**File:** `.github/workflows/main.yml`

**Trigger:** Every `push` to `main`/`develop` and every `pull_request` targeting `main`.

### Pipeline Architecture

```
Push to GitHub
      │
      ▼
┌──────────────┐     ┌──────────────────┐     ┌──────────────┐
│ Build & Lint │────▶│ Automated Tests  │────▶│ Docker Build │
│  Job 1       │     │  Job 2           │     │  Job 3       │
└──────────────┘     └──────────────────┘     └──────────────┘
     ~12s                  ~15s                    ~40s
```

### Job 1 — Build & Lint
- Checks out code from the GitHub repository
- Sets up Python 3.12 environment
- Installs all packages from `requirements.txt`
- Runs `flake8` to detect syntax errors, undefined names, and critical issues
- Fails the entire pipeline immediately if any error is found

### Job 2 — Automated Tests (runs only if Job 1 passes)
- Sets up a clean Python environment
- Installs dependencies
- Runs the full `pytest` suite (28 tests) against the Flask app
- Each test uses an isolated temporary SQLite database (no shared state)
- Fails the pipeline if any test fails

### Job 3 — Docker Build (runs only if Job 2 passes)
- Builds the multi-stage Docker image from the `Dockerfile`
- Starts the container and hits `/health` to confirm it runs correctly
- Cleans up the test container
- Ensures the containerised app is deployable

**View live pipeline:** `https://github.com/ashokbh/2024tm93585/actions`

---

## Jenkins BUILD Integration Logic

**File:** `Jenkinsfile`

Jenkins provides a controlled BUILD environment that mirrors production more closely than GitHub Actions runners. It is triggered via a GitHub Webhook on every push.

### Pipeline Stages

```
Checkout → Environment Setup → Lint → Unit Tests → Docker Build → Smoke Test
```

| Stage | What It Does |
|-------|-------------|
| **Checkout** | Pulls latest code from GitHub |
| **Environment Setup** | Creates Python venv, installs all dependencies |
| **Lint** | Runs `flake8` — build fails on syntax errors |
| **Unit Tests** | Runs `pytest`, generates JUnit XML + coverage report |
| **Docker Build** | Builds image tagged with Jenkins `BUILD_NUMBER` |
| **Smoke Test** | Starts container on port 5001, verifies `/health`, tears down |

### Jenkins Setup Steps

**1. Run Jenkins via Docker:**
```bash
docker run -d -p 8080:8080 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  jenkins/jenkins:lts
```

**2. Required Plugins:** Git, Pipeline, Docker Pipeline, JUnit, Cobertura

**3. Create Pipeline Job:**
- New Item → Pipeline → Pipeline script from SCM
- SCM: Git → Repository URL: `https://github.com/ashokbh/2024tm93585.git`
- Script Path: `Jenkinsfile`

**4. Configure Webhook:**
- GitHub → Settings → Webhooks → Add webhook
- Payload URL: `http://<jenkins-host>:8080/github-webhook/`

### How GitHub Actions and Jenkins Work Together

```
Developer pushes code
        │
        ├──▶ GitHub Actions (automatic, ~1 min)
        │         Fast feedback on PR — Lint → Test → Docker
        │
        └──▶ Webhook notifies Jenkins (~5 min)
                  Full BUILD — virtual env, test reports, versioned Docker image
```

GitHub Actions gives **instant feedback** on every pull request. Jenkins provides **controlled BUILD artifacts** with numbered Docker images and archived test reports for audit and compliance.

---

## Evaluation Checklist

| Criterion | Implementation |
|-----------|---------------|
| Application Integrity | Flask API with 15 endpoints, SQLite persistence |
| VCS Maturity | Commits per Tkinter version (v1.0 → v3.2.4 → Flask) |
| Testing Coverage | 26 Pytest cases covering all endpoints and edge cases |
| Docker Efficiency | Multi-stage build, non-root user, minimal python:3.12-slim |
| Jenkins BUILD | 6-stage Jenkinsfile with JUnit reports |
| GitHub Actions | 3-job pipeline triggered on push/PR |
| Documentation | This README with setup, test, and pipeline documentation |

---

*Submitted for Introduction to DevOps (CSIZG514) — BITS Pilani, S2-2025*
*Student ID: 2024TM93585*
