# Docker Setup Guide

> **Version:** 1.0.0  
> **Last Updated:** 2026-01-22  
> **Compatibility:** Linux (Pop!_OS, Linux Mint, Ubuntu) & Windows 10/11

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Linux Setup (Pop!\_OS 22.04 LTS / Linux Mint)](#linux-setup-pop_os-2204-lts--linux-mint)
- [Windows Setup](#windows-setup)
- [Running the Application](#running-the-application)
- [Useful Commands](#useful-commands)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

| Component | Minimum Version | Purpose |
|-----------|----------------|---------|
| Docker Engine | 24.0+ | Container runtime |
| Docker Compose | 2.20+ | Multi-container orchestration |
| Git | 2.30+ | Version control |

---

## Linux Setup (Pop!_OS 22.04 LTS / Linux Mint)

### Step 1: Remove Old Docker Versions (if any)

```bash
sudo apt remove docker docker-engine docker.io containerd runc
```

### Step 2: Install Dependencies

```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg lsb-release
```

### Step 3: Add Docker's Official GPG Key

```bash
sudo mkdir -m 0755 -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
```

### Step 4: Set Up Docker Repository

**For Pop!_OS 22.04 LTS:**
```bash
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  jammy stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

**For Linux Mint (based on Ubuntu 22.04):**
```bash
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  jammy stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

### Step 5: Install Docker Engine

```bash
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### Step 6: Configure Docker to Run Without sudo

```bash
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker
```

### Step 7: Verify Installation

```bash
docker --version
docker compose version
docker run hello-world
```

### Step 8: Enable Docker on Boot

```bash
sudo systemctl enable docker
sudo systemctl start docker
```

---

## Windows Setup

### Option 1: Docker Desktop (Recommended)

1. **Download Docker Desktop** from [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)

2. **Install Docker Desktop** - Run the installer and follow prompts

3. **Enable WSL 2 Backend** (recommended for performance):
   - Open Docker Desktop Settings → General
   - Enable "Use WSL 2 based engine"

4. **Verify Installation** in PowerShell:
   ```powershell
   docker --version
   docker compose version
   docker run hello-world
   ```

### Option 2: Rancher Desktop (Free Alternative)

1. **Download Rancher Desktop** from [https://rancherdesktop.io](https://rancherdesktop.io)
2. Install and select "dockerd (moby)" as container runtime
3. Verify installation as shown above

---

## Running the Application

### Clone the Repository

```bash
git clone https://github.com/flexycode/CCSFEN2L_ALTFLEX.git
cd CCSFEN2L_ALTFLEX
```

### Configure Environment

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your configuration:
   ```bash
   nano .env  # Linux
   notepad .env  # Windows
   ```

### Build and Start Services

**Development Mode (with live reload):**
```bash
docker compose up --build
```

**Detached Mode (background):**
```bash
docker compose up --build -d
```

### Access the Application

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | Next.js Dashboard |
| Backend API | http://localhost:8000 | FastAPI Endpoints |
| API Docs | http://localhost:8000/docs | Swagger UI |

### Stop Services

```bash
docker compose down
```

**Stop and remove volumes (full reset):**
```bash
docker compose down -v
```

---

## Useful Commands

### Container Management

| Command | Description |
|---------|-------------|
| `docker compose ps` | List running containers |
| `docker compose logs -f` | Follow logs from all services |
| `docker compose logs -f backend` | Follow backend logs only |
| `docker compose logs -f frontend` | Follow frontend logs only |
| `docker compose restart` | Restart all services |
| `docker compose restart backend` | Restart backend only |

### Development Workflow

| Command | Description |
|---------|-------------|
| `docker compose build --no-cache` | Rebuild images without cache |
| `docker compose exec backend bash` | Shell into backend container |
| `docker compose exec frontend sh` | Shell into frontend container |

### Cleanup

| Command | Description |
|---------|-------------|
| `docker system prune` | Remove unused containers/images |
| `docker system prune -a` | Remove all unused images |
| `docker volume prune` | Remove unused volumes |

---

## Troubleshooting

### Linux: Permission Denied Error

```bash
# If you see "permission denied" errors
sudo chmod 666 /var/run/docker.sock

# Permanent fix: ensure user is in docker group
sudo usermod -aG docker $USER
# Then log out and log back in
```

### Linux: Docker Service Not Starting

```bash
# Check Docker service status
sudo systemctl status docker

# Restart Docker service
sudo systemctl restart docker

# Check logs for errors
sudo journalctl -u docker.service
```

### Windows: WSL 2 Backend Issues

1. Open PowerShell as Administrator:
   ```powershell
   wsl --update
   wsl --set-default-version 2
   ```

2. Restart Docker Desktop

### Port Already in Use

```bash
# Linux: Find process using port 3000
sudo lsof -i :3000
sudo kill -9 <PID>

# Windows (PowerShell):
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

### Container Health Check Failing

```bash
# Check container health
docker inspect altflex-backend --format='{{.State.Health.Status}}'

# View health check logs
docker inspect altflex-backend --format='{{json .State.Health}}' | jq
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Network                        │
│                   (altflex-network)                      │
│                                                          │
│  ┌──────────────────┐      ┌──────────────────┐         │
│  │   Frontend       │      │    Backend       │         │
│  │  (Next.js 16)    │ ───► │   (FastAPI)      │         │
│  │   Port: 3000     │      │   Port: 8000     │         │
│  └──────────────────┘      └──────────────────┘         │
│                                     │                    │
│                                     ▼                    │
│                            ┌──────────────────┐         │
│                            │  Shared Volumes  │         │
│                            │  ./data, ./logs  │         │
│                            └──────────────────┘         │
└─────────────────────────────────────────────────────────┘
```

---

> [!NOTE]
> For production deployments, additional configuration is recommended including SSL/TLS certificates, environment-specific settings, and resource limits.

**Created by:** AltFlex Development Team  
**Repository:** [flexycode/CCSFEN2L_ALTFLEX](https://github.com/flexycode/CCSFEN2L_ALTFLEX)
