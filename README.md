# Agent Orchestration Service with ERP Exception Management

A comprehensive microservice framework for AI agent orchestration with specialized ERP Exception Management capabilities.

## Features

### Core Framework
- **Dynamic Agent Registration**: Register and manage AI agents with full configuration
- **Execution Management**: Track and monitor agent executions with real-time updates
- **WebSocket Support**: Real-time execution updates via WebSocket connections
- **MCP Integration**: Model Context Protocol support for external tool integration
- **Multiple Model Providers**: Support for Bedrock, OpenAI, Anthropic, and Perplexity

### ERP Exception Management
- **Comprehensive Analysis**: Full ERP exception detection across all business processes
- **SAP Integration**: Direct SAP system access via MCP ABAP ADT API
- **Research Integration**: Web research capabilities via Perplexity MCP
- **Multi-Category Detection**: Financial, Procurement, Inventory, Production, and more
- **Automated Reporting**: JSON reports with business impact analysis
- **Real-time Monitoring**: Background execution with status tracking

## Quick Start

### 1. Setup Environment

```bash
# Clone and setup
git clone <repository>
cd agent-orchestration-service

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your credentials
```

### 2. Start Services

```bash
# Using Docker (recommended)
docker-compose up -d

# Or manually
# Start MongoDB and Redis locally, then:
python -m app.main
```

### 3. Register ERP Agent

```bash
# Register the ERP Exception Management Agent
python scripts/register_erp_agent.py
```

### 4. Use the ERP Client

```bash
# Check service status
python client/erp_client.py status

# Start comprehensive analysis
python client/erp_client.py analyze --wait

# Quick analysis
python client/erp_client.py quick "analyze financial exceptions"

# Get specific result
python client/erp_client.py result <execution_id>
```

## API Endpoints

### Core Agent Management
- `POST /api/v1/agents/register` - Register new agent
- `GET /api/v1/agents/{agent_id}/config` - Get agent configuration
- `PUT /api/v1/agents/{agent_id}/config` - Update agent configuration
- `POST /api/v1/agents/{agent_id}/execute` - Execute agent
- `GET /api/v1/agents/` - List all agents

### ERP Exception Management
- `GET /api/v1/erp/status` - Get ERP service status
- `POST /api/v1/erp/analyze` - Start comprehensive analysis
- `GET /api/v1/erp/analyze/{execution_id}` - Get analysis result
- `POST /api/v1/erp/quick-analysis` - Quick analysis

### Execution Management
- `GET /api/v1/executions/{execution_id}` - Get execution details
- `GET /api/v1/executions/` - List executions
- `DELETE /api/v1/executions/{execution_id}` - Cancel execution

### WebSocket
- `WS /ws/execution/{execution_id}` - Real-time execution updates

## ERP Exception Categories

The system detects and analyzes exceptions across these categories:

### 🔴 Financial Exceptions
- Budget overruns and variance analysis
- Unreconciled transactions and aging
- Currency conversion discrepancies
- Tax calculation errors

### 🟡 Procurement Exceptions
- Unapproved vendors and compliance violations
- Exceeded budget limits
- Missing approvals and expired contracts
- Price variance analysis

### 🟠 Inventory Exceptions
- Stock-outs and availability issues
- Overstock and slow-moving inventory
- Expired items and count discrepancies
- Negative stock situations

### 🔵 Order Fulfillment Exceptions
- Insufficient inventory for orders
- Partial shipments and backorders
- Delivery delays and customer impact
- Credit limit exceeded

### 🟢 Production Exceptions
- Material shortages and supply chain issues
- Quality control failures
- Capacity constraints and bottlenecks
- Production delays

### 🟣 Invoice Matching Exceptions
- Three-way matching discrepancies
- Price and quantity variances
- Missing documents
- Duplicate invoices

## Configuration

### Environment Variables

```bash
# MongoDB
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=agent_orchestration

# Model API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
PERPLEXITY_API_KEY=your_perplexity_key

# AWS (for Bedrock)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# ERP Configuration
MCP_ABAP_SERVER_PATH=/path/to/mcp-abap-server/dist/index.js
ERP_REPORTS_DIRECTORY=erp_exception_reports

# Monitoring
LANGFUSE_PUBLIC_KEY=your_public_key
LANGFUSE_SECRET_KEY=your_secret_key
LANGFUSE_HOST=https://cloud.langfuse.com
```

### MCP Server Setup

#### SAP ABAP ADT MCP Server
```bash
# Install the SAP MCP server
git clone https://github.com/your-org/mcp-abap-abap-adt-api
cd mcp-abap-abap-adt-api
npm install
npm run build

# Set the path in environment
export MCP_ABAP_SERVER_PATH=/path/to/mcp-abap-abap-adt-api/dist/index.js
```

#### Perplexity MCP Docker
```bash
# Pull the Perplexity MCP image
docker pull mcp/perplexity-ask

# Set your API key
export PERPLEXITY_API_KEY=your_perplexity_api_key
```

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client Apps   │    │   Web Client    │    │   CLI Client    │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────┴─────────────┐
                    │     FastAPI Service      │
                    │   (Agent Orchestration)   │
                    └─────────────┬─────────────┘
                                 │
                    ┌─────────────┴─────────────┐
                    │    Agent Services        │
                    │  ┌─────────────────────┐  │
                    │  │ ERP Exception Mgmt  │  │
                    │  │ Dynamic Agent       │  │
                    │  │ Builder             │  │
                    │  └─────────────────────┘  │
                    └─────────────┬─────────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          │                      │                      │
    ┌─────┴─────┐         ┌─────┴─────┐         ┌─────┴─────┐
    │ MongoDB   │         │   MCP     │         │  External │
    │ (Config & │         │ Servers   │         │   APIs    │
    │ Execution)│         │ (SAP,     │         │(Perplexity│
    └───────────┘         │Research)  │         │ etc.)     │
                          └───────────┘         └───────────┘
```

## Development

### Adding New Agents

1. Create agent service in `app/services/`
2. Add API endpoints in `app/api/`
3. Register agent configuration
4. Update routing in `app/main.py`

### Testing

```bash
# Run tests
pytest

# Test specific ERP functionality
python -m pytest tests/test_erp_agent.py

# Integration tests
python -m pytest tests/test_integration.py
```

### Monitoring

The service includes comprehensive monitoring:

- **Langfuse Integration**: Trace all agent executions
- **Execution Tracking**: Database storage of all runs
- **WebSocket Updates**: Real-time status updates
- **Error Handling**: Comprehensive error tracking and recovery

## Production Deployment

### Docker Deployment

```bash
# Build and deploy
docker-compose -f docker-compose.prod.yml up -d

# Scale services
docker-compose up --scale app=3
```

### Kubernetes Deployment

```yaml
# See k8s/ directory for full configuration
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent-orchestration
spec:
  replicas: 3
  selector:
    matchLabels:
      app: agent-orchestration
  template:
    spec:
      containers:
      - name: app
        image: agent-orchestration:latest
        ports:
        - containerPort: 8000
```

## Troubleshooting

### Common Issues

1. **MCP Server Not Found**
   ```bash
   # Check path and permissions
   ls -la /path/to/mcp-server
   node /path/to/mcp-server/dist/index.js
   ```

2. **Docker Issues**
   ```bash
   # Check Docker status
   docker --version
   docker images | grep mcp
   ```

3. **Database Connection**
   ```bash
   # Test MongoDB connection
   mongosh mongodb://localhost:27017
   ```

### Logs

```bash
# View service logs
docker-compose logs -f app

# View specific execution logs
tail -f logs/executions.log
```

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the documentation in `/docs`
- Review the API documentation at `http://localhost:8000/docs`