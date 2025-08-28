# Multi-tenant Agent Orchestration Service with ERP Exception Management

A comprehensive multi-tenant microservice framework for AI agent orchestration with database-driven configuration, customer-specific project isolation, and specialized ERP Exception Management capabilities.

## Features

### Core Framework
- **Multi-tenant Architecture**: Complete customer isolation with project-specific databases
- **Master Data Management**: Centralized templates, tools, and configurations
- **Database-Driven Configuration**: All configurations stored in MongoDB with proper isolation
- **Template System**: Create agents from configurable templates with variable substitution
- **Dynamic Agent Registration**: Register and manage AI agents with full configuration
- **Project-specific Execution**: Customer-isolated execution tracking and results
- **Token Usage Tracking**: Comprehensive cost tracking per project and agent
- **Audit Logging**: Complete audit trail for all project activities
- **WebSocket Support**: Real-time execution updates via WebSocket connections
- **MCP Integration**: Model Context Protocol support for external tool integration
- **Multiple Model Providers**: Support for Bedrock, OpenAI, Anthropic, and Perplexity
- **Analytics Dashboard**: Project-specific analytics and monitoring

### ERP Exception Management
- **Comprehensive Analysis**: Full ERP exception detection across all business processes
- **SAP Integration**: Direct SAP system access via MCP ABAP ADT API
- **Research Integration**: Web research capabilities via Perplexity MCP
- **Multi-Category Detection**: Financial, Procurement, Inventory, Production, and more
- **Automated Reporting**: JSON reports with business impact analysis
- **Real-time Monitoring**: Background execution with status tracking

### Multi-tenant Database Architecture

```
📊 Master Database (ktern-masterdb)
├── kt_m_agents          # Master agent templates
├── kt_m_tools           # Master tool registry  
├── kt_m_mcps            # Master MCP server registry
├── kt_m_system_prompts  # Master system prompt templates
├── kt_m_projects        # Project registry
└── kt_m_model_configs   # Master model configurations

🏢 Project Databases (ktern-project-{project_id})
├── kt_p_agent_instances # Customer-specific agent instances
├── kt_p_executions      # Execution history and tracking
├── kt_p_results         # Execution results and outputs
├── kt_p_token_usage     # Token usage and cost tracking
└── kt_p_audit_log       # Complete audit trail
```

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
# Start MongoDB locally, then:
python -m app.main
```

### 3. Setup Master Data and Create Project

```bash
# Setup master data and create example project
python scripts/setup_multi_tenant_data.py
```

### 4. Use the API

```bash
# List all projects
curl "http://localhost:8000/api/v1/master/projects"

# List agent templates
curl "http://localhost:8000/api/v1/master/agents"

# Get project dashboard
curl "http://localhost:8000/api/v1/projects/acme-corp-2024/analytics/dashboard"

# List agent instances for a project
curl "http://localhost:8000/api/v1/projects/acme-corp-2024/agent-instances"

# Execute agent instance
curl -X POST "http://localhost:8000/api/v1/projects/acme-corp-2024/executions" \
  -H "Content-Type: application/json" \
  -d '{"instance_id": "your-instance-id", "input_data": {"prompt": "Analyze ERP exceptions"}, "async_execution": true}'
```

## API Endpoints

### Master Data Management
- `POST /api/v1/master/projects` - Create customer project
- `GET /api/v1/master/projects` - List all projects
- `GET /api/v1/master/projects/{project_id}` - Get project details
- `POST /api/v1/master/agents` - Create agent template
- `GET /api/v1/master/agents` - List agent templates
- `GET /api/v1/master/agents/{agent_id}` - Get agent template
- `PUT /api/v1/master/agents/{agent_id}` - Update agent template
- `POST /api/v1/master/system-prompts` - Create system prompt template
- `GET /api/v1/master/system-prompts` - List system prompt templates
- `POST /api/v1/master/model-configs` - Create model configuration
- `GET /api/v1/master/model-configs` - List model configurations
- `POST /api/v1/master/tools` - Create tool configuration
- `GET /api/v1/master/tools` - List tools
- `POST /api/v1/master/mcp-servers` - Create MCP server configuration
- `GET /api/v1/master/mcp-servers` - List MCP servers
- `POST /api/v1/master/setup/erp-defaults` - Setup default ERP master data
- `GET /api/v1/master/health` - Master data health check

### Project-Specific Operations
- `POST /api/v1/projects/{project_id}/agent-instances` - Create agent instance
- `GET /api/v1/projects/{project_id}/agent-instances` - List agent instances
- `GET /api/v1/projects/{project_id}/agent-instances/{instance_id}` - Get agent instance
- `POST /api/v1/projects/{project_id}/executions` - Execute agent instance
- `GET /api/v1/projects/{project_id}/executions` - List executions
- `GET /api/v1/projects/{project_id}/executions/{execution_id}` - Get execution details
- `GET /api/v1/projects/{project_id}/executions/{execution_id}/result` - Get execution result
- `GET /api/v1/projects/{project_id}/token-usage` - Get token usage analytics
- `GET /api/v1/projects/{project_id}/analytics/dashboard` - Get project dashboard
- `GET /api/v1/projects/{project_id}/audit-log` - Get audit log

### Legacy ERP Exception Management
- `GET /api/v1/erp/status` - Get ERP service status
- `POST /api/v1/erp/analyze` - Start comprehensive analysis
- `GET /api/v1/erp/analyze/{execution_id}` - Get analysis result
- `POST /api/v1/erp/quick-analysis` - Quick analysis

### Legacy Dynamic Agents (Deprecated)
- `POST /api/v1/dynamic/execute/{agent_id}` - Execute agent by ID
- `GET /api/v1/dynamic/execution/{execution_id}/status` - Get execution status
- `GET /api/v1/dynamic/execution/{execution_id}/result` - Get execution result
- `GET /api/v1/dynamic/executions` - List executions
- `GET /api/v1/dynamic/templates` - List agent templates

### WebSocket
- `WS /ws/execution/{execution_id}` - Real-time execution updates

## Multi-tenant Usage Examples

### 1. Create Customer Project
```bash
curl -X POST "http://localhost:8000/api/v1/master/projects" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "customer-abc-2024",
    "project_name": "Customer ABC ERP Project", 
    "customer_name": "ABC Corporation",
    "description": "ERP analysis project for ABC Corp",
    "created_by": "admin"
  }'
```

### 2. Create Agent Instance for Customer
```bash
curl -X POST "http://localhost:8000/api/v1/projects/customer-abc-2024/agent-instances" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "erp-exception-management",
    "name": "ABC Corp ERP Exception Manager",
    "description": "ERP exception analysis for ABC Corporation",
    "system_prompt_variables": {
      "system_name": "ABC SAP Production System",
      "analysis_scope": "Comprehensive Exception Analysis",
      "focus_areas": "Financial and Procurement Exceptions"
    },
    "custom_settings": {
      "timeout": 900,
      "enable_detailed_logging": true
    },
    "created_by": "admin"
  }'
```

### 3. Execute Agent Instance
```bash
curl -X POST "http://localhost:8000/api/v1/projects/customer-abc-2024/executions" \
  -H "Content-Type: application/json" \
  -d '{
    "instance_id": "your-instance-id-here",
    "input_data": {
      "prompt": "Perform comprehensive ERP exception analysis for Q4 2024",
      "system_details": "ABC Corporation SAP Production System"
    },
    "variables": {
      "focus_areas": "High-priority financial and procurement exceptions",
      "analysis_depth": "Deep analysis with root cause identification"
    },
    "async_execution": true
  }'
```

### 4. Monitor Token Usage and Costs
```bash
# Get token usage analytics for the project
curl "http://localhost:8000/api/v1/projects/customer-abc-2024/token-usage?start_date=2024-01-01"

# Get project dashboard with analytics
curl "http://localhost:8000/api/v1/projects/customer-abc-2024/analytics/dashboard"
```

## Database Configuration

### Environment Variables

```bash
# Master Database
MONGODB_URL=mongodb://localhost:27017
MASTER_DATABASE_NAME=ktern-masterdb

# Project Database Pattern  
PROJECT_DATABASE_PREFIX=ktern-project-

# Multi-tenant Settings
ENABLE_MULTI_TENANT=true
DEFAULT_PROJECT_ID=default

# Model API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
PERPLEXITY_API_KEY=your_perplexity_key

# AWS (for Bedrock)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# Monitoring
LANGFUSE_PUBLIC_KEY=your_public_key
LANGFUSE_SECRET_KEY=your_secret_key
LANGFUSE_HOST=https://cloud.langfuse.com
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
                    │  (Multi-tenant Router)   │
                    └─────────────┬─────────────┘
                                 │
                    ┌─────────────┴─────────────┐
                    │   Database Manager       │
                    │  ┌─────────────────────┐  │
                    │  │ Master Data Service │  │
                    │  │ Project Data Service│  │
                    │  │ Multi-tenant Agent  │  │
                    │  │ Template Service    │  │
                    │  └─────────────────────┘  │
                    └─────────────┬─────────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          │                      │                      │
    ┌─────┴─────┐         ┌─────┴─────┐         ┌─────┴─────┐
    │ Master DB │         │ Project   │         │  External │
    │(Templates,│         │Databases  │         │   APIs    │
    │ Projects, │         │(Customer  │         │(MCP, LLM  │
    │ Registry) │         │ Isolated) │         │ Providers)│
    └───────────┘         └───────────┘         └───────────┘
```

## Key Features

### 🏢 Multi-tenant Architecture
- **Complete Customer Isolation**: Each customer gets their own database
- **Shared Master Data**: Common templates and configurations
- **Project-based Organization**: Organize work by customer projects
- **Scalable Design**: Add customers without affecting others

### 📊 Comprehensive Tracking
- **Token Usage**: Track costs per project, agent, and execution
- **Audit Logging**: Complete audit trail for compliance
- **Performance Metrics**: Execution times, success rates, error tracking
- **Business Analytics**: Project dashboards and reporting

### 🔧 Template-based Configuration
- **Master Templates**: Reusable agent configurations
- **Variable Substitution**: Customize prompts per customer
- **Version Control**: Track template changes and updates
- **Inheritance**: Instance-level customization of master templates

### 🚀 Production Ready
- **Error Handling**: Comprehensive error tracking and recovery
- **Monitoring**: Health checks and service monitoring
- **Scalability**: Horizontal scaling support
- **Security**: Data isolation and audit trails

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
MASTER_DATABASE_NAME=ktern-masterdb
PROJECT_DATABASE_PREFIX=ktern-project-

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

# Multi-tenant Settings
ENABLE_MULTI_TENANT=true
DEFAULT_PROJECT_ID=default

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

### Legacy Architecture (Deprecated)
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

### New Multi-tenant Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                      │
├─────────────────────────────────────────────────────────────┤
│  Master Data APIs  │  Project Data APIs  │  Legacy APIs    │
├─────────────────────────────────────────────────────────────┤
│              Database Manager (Multi-tenant)               │
├─────────────────────────────────────────────────────────────┤
│                        MongoDB                              │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │   Master DB     │  │  Project DBs    │                  │
│  │ ┌─────────────┐ │  │ ┌─────────────┐ │                  │
│  │ │kt_m_agents  │ │  │ │kt_p_instances│ │                  │
│  │ │kt_m_tools   │ │  │ │kt_p_executions│ │                  │
│  │ │kt_m_mcps    │ │  │ │kt_p_results  │ │                  │
│  │ │kt_m_prompts │ │  │ │kt_p_tokens   │ │                  │
│  │ │kt_m_projects│ │  │ │kt_p_audit    │ │                  │
│  │ │kt_m_models  │ │  │ └─────────────┘ │                  │
│  │ └─────────────┘ │  │     (Per        │                  │
│  │                 │  │    Customer)    │                  │
│  └─────────────────┘  └─────────────────┘                  │
└─────────────────────────────────────────────────────────────┘
```

## Migration Guide

If you're using the legacy single-tenant version, see the [Migration Guide](docs/migration.md) for upgrading to the multi-tenant architecture.

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
python -m pytest tests/test_multi_tenant.py

# Test master data functionality  
python -m pytest tests/test_master_data.py

# Integration tests
python -m pytest tests/test_integration.py
```

### Monitoring

The service includes comprehensive monitoring:

- **Multi-tenant Isolation**: Complete data separation between customers
- **Langfuse Integration**: Trace all agent executions
- **Project-specific Storage**: All executions and results stored per project
- **Structured Results**: Results stored with metadata and metrics
- **WebSocket Updates**: Real-time status updates
- **Error Handling**: Comprehensive error tracking and recovery
- **Audit Logging**: Complete audit trail for compliance
- **Token Usage Tracking**: Detailed cost tracking per project
- **Analytics Dashboards**: Project-specific monitoring and reporting

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

### Multi-tenant Considerations

1. **Database Scaling**: Monitor database connections as projects grow
2. **Resource Isolation**: Consider resource limits per project
3. **Backup Strategy**: Implement per-project backup policies
4. **Monitoring**: Set up project-specific monitoring and alerting
5. **Cost Allocation**: Track costs per customer/project

### Security Best Practices

1. **Data Isolation**: Ensure complete separation between customer data
2. **Access Control**: Implement proper authentication and authorization
3. **Audit Logging**: Maintain comprehensive audit trails
4. **Encryption**: Encrypt data at rest and in transit

## Troubleshooting

### Common Issues

1. **MCP Server Not Found**
   ```bash
   # Check path and permissions
   ls -la /path/to/mcp-server
   node /path/to/mcp-server/dist/index.js
   ```

2. **Project Database Issues**
   ```bash
   # Check project exists
   curl "http://localhost:8000/api/v1/master/projects/your-project-id"
   
   # Check database connections
   curl "http://localhost:8000/api/v1/master/health"
   ```

3. **Docker Issues**
   ```bash
   # Check Docker status
   docker --version
   docker images | grep mcp
   ```

4. **Database Connection**
   ```bash
   # Test MongoDB connection
   mongosh mongodb://localhost:27017
   
   # List databases
   show dbs
   
   # Check master database
   use ktern-masterdb
   show collections
   ```

### Logs

```bash
# View service logs
docker-compose logs -f app

# View project-specific logs
grep "project_id=customer-abc-2024" logs/app.log

# View specific execution logs
tail -f logs/executions.log
```

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

Please ensure all new features support the multi-tenant architecture and include appropriate tests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the documentation in `/docs`
- Review the API examples in `/examples`
- Review the API documentation at `http://localhost:8000/docs`