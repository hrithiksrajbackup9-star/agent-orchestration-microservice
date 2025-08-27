# 1. Setup project
mkdir agent-orchestration-service
cd agent-orchestration-service

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment
cp .env.example .env
# Edit .env with your credentials

# 5. Start services with Docker
docker-compose up -d

# OR start manually
# Start MongoDB locally
# Then run:
python -m app.main

# 6. Service will be available at http://localhost:8000
# API docs at http://localhost:8000/docs