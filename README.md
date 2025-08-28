# Agent Orchestration Service with ERP Exception Management

A comprehensive microservice framework for AI agent orchestration with database-driven configuration and specialized ERP Exception Management capabilities.

## Features

### Core Framework
- **Database-Driven Configuration**: All agent configurations, prompts, and tools stored in MongoDB
- **Template System**: Create agents from configurable templates with variable substitution
- **Dynamic Agent Registration**: Register and manage AI agents with full configuration
- **Execution Management**: Track and monitor agent executions with real-time updates
- **WebSocket Support**: Real-time execution updates via WebSocket connections
- **MCP Integration**: Model Context Protocol support for external tool integration
- **Multiple Model Providers**: Support for Bedrock, OpenAI, Anthropic, and Perplexity
- **Result Storage**: All execution results stored in database with structured metadata

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
# Setup ERP templates and registry (one-time setup)
python scripts/setup_erp_templates.py
```

### 4. Use the Dynamic ERP Client

```bash
# List available templates
python client/dynamic_erp_client.py templates

# Execute the ERP agent (async)
python client/dynamic_erp_client.py execute erp-exception-management-001 --wait

# Execute with custom variables
python client/dynamic_erp_client.py execute erp-exception-management-001 \
  --variables '{"system_name": "SAP Production", "focus_areas": "Financial Exceptions"}' \
  --wait

# Check execution status
python client/dynamic_erp_client.py status <execution_id>

# Get execution result
python client/dynamic_erp_client.py result <execution_id>

# List recent executions
python client/dynamic_erp_client.py list --limit 5
```

## API Endpoints

### Dynamic Agent Management
- `POST /api/v1/dynamic/execute/{agent_id}` - Execute agent by ID
- `GET /api/v1/dynamic/execution/{execution_id}/status` - Get execution status
- `GET /api/v1/dynamic/execution/{execution_id}/result` - Get execution result
- `GET /api/v1/dynamic/executions` - List executions
- `POST /api/v1/dynamic/agents/from-template` - Create agent from template
- `GET /api/v1/dynamic/templates` - List agent templates
- `GET /api/v1/dynamic/templates/prompts` - List system prompt templates
- `GET /api/v1/dynamic/registry/mcp-servers` - List MCP servers
- `GET /api/v1/dynamic/registry/tools` - List available tools

### Legacy ERP Exception Management
- `GET /api/v1/erp/status` - Get ERP service status
- `POST /api/v1/erp/analyze` - Start comprehensive analysis
- `GET /api/v1/erp/analyze/{execution_id}` - Get analysis result
- `POST /api/v1/erp/quick-analysis` - Quick analysis

### Legacy Execution Management
- `GET /api/v1/executions/{execution_id}` - Get execution details
- `GET /api/v1/executions/` - List executions
- `DELETE /api/v1/executions/{execution_id}` - Cancel execution

### WebSocket
- `WS /ws/execution/{execution_id}` - Real-time execution updates

## Database-Driven Configuration

### Agent Templates
Create reusable agent configurations with variable substitution:

```json
{
  "template_id": "erp-exception-management",
  "name": "ERP Exception Management Agent",
  "system_prompt_template": "erp-exception-management-prompt",
  "default_model_config": {
    "provider": "bedrock",
    "model_id": "us.anthropic.claude-sonnet-4-20250514-v1:0"
  },
  "template_variables": {
    "system_name": "SAP ERP",
    "analysis_scope": "Comprehensive"
  }
}
```

### System Prompt Templates
Create configurable prompts with Jinja2 templating:

```jinja2
You are analyzing {{system_name|default('ERP System')}}.
Focus on {{focus_areas|default('all business processes')}}.
Analysis scope: {{analysis_scope|default('comprehensive')}}.
```

### MCP Server Registry
Centrally manage MCP server configurations:

```json
{
  "server_id": "sap-abap-adt",
  "name": "SAP ABAP ADT MCP Server",
  "command": "node",
  "possible_locations": [
    "C:\\mcp-abap-abap-adt-api\\dist\\index.js",
    "~/mcp-abap-abap-adt-api/dist/index.js"
  ],
  "auto_detect_enabled": true
}
```

## Dynamic Execution Examples

### Execute with Custom Variables
```bash
curl -X POST "http://localhost:8000/api/v1/dynamic/execute/erp-exception-management-001" \
  -H "Content-Type: application/json" \
  -d '{
    "input_data": {
      "prompt": "Analyze financial exceptions in SAP",
      "system_details": "Production SAP System"
    },
    "variables": {
      "system_name": "SAP Production",
      "focus_areas": "Financial and Procurement Exceptions",
      "analysis_depth": "Deep Analysis with Root Cause"
    },
    "async_execution": true
  }'
```

### Create Agent from Template
```bash
curl -X POST "http://localhost:8000/api/v1/dynamic/agents/from-template" \
  -H "Content-Type: application/json" \
  -d '{
    "template_id": "erp-exception-management",
    "agent_id": "erp-financial-specialist",
    "variables": {
      "system_name": "SAP Financial Module",
      "focus_areas": "Financial Exceptions Only"
    },
    "overrides": {
      "name": "ERP Financial Exception Specialist"
    }
  }'
```

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

# Template System
JINJA2_TEMPLATE_CACHE=true

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
                    │  Database-Driven Services │
                    │  ┌─────────────────────┐  │
                    │  │ Template Service    │  │
                    │  │ Dynamic Agent Svc   │  │
                    │  │ ERP Exception Mgmt  │  │
                    │  │ Agent Builder       │  │
                    │  └─────────────────────┘  │
                    └─────────────┬─────────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          │                      │                      │
    ┌─────┴─────┐         ┌─────┴─────┐         ┌─────┴─────┐
    │ MongoDB   │         │   MCP     │         │  External │
    │ • Configs │         │ Servers   │         │   APIs    │
    │ • Templates│        │ (SAP,     │         │(Perplexity│
    │ • Executions│       │Research)  │         │ etc.)     │
    │ • Results │         │           │         │           │
    └───────────┘         └───────────┘         └───────────┘
```

## Development

### Adding New Agent Templates

1. Create system prompt template in database
2. Create agent template referencing the prompt template
3. Register MCP servers and tools in registry
4. Create agent instances from templates
5. Execute via REST API

### Testing

```bash
# Run tests
pytest

# Test dynamic agent functionality
python -m pytest tests/test_dynamic_agents.py

# Integration tests
python -m pytest tests/test_integration.py
```

### Monitoring

The service includes comprehensive monitoring:

- **Langfuse Integration**: Trace all agent executions
- **Database Storage**: All executions and results stored in MongoDB
- **Structured Results**: Results stored with metadata and metrics
- **WebSocket Updates**: Real-time status updates
- **Error Handling**: Comprehensive error tracking and recovery
- **Template Versioning**: Track template changes and agent versions

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