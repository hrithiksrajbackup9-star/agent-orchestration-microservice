#!/bin/bash

# Create project structure
mkdir -p agent-orchestration-service/{app/{models,services,api,utils},client,tests,docker}

# Create Python package files
touch agent-orchestration-service/app/__init__.py
touch agent-orchestration-service/app/models/__init__.py
touch agent-orchestration-service/app/services/__init__.py
touch agent-orchestration-service/app/api/__init__.py
touch agent-orchestration-service/app/utils/__init__.py
touch agent-orchestration-service/client/__init__.py
touch agent-orchestration-service/tests/__init__.py

# Copy .env.example to .env
cp .env.example .env

# Install dependencies
pip install -r requirements.txt

# Start MongoDB (if using Docker)
docker-compose up -d mongodb redis

# Run the service
python -m app.main