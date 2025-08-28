# Multi-tenant Agent Orchestration API Examples

This document provides comprehensive examples for using the multi-tenant agent orchestration API.

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication
Currently, the API doesn't require authentication, but you can add headers for user identification:
```bash
curl -H "X-User-ID: admin" -H "Content-Type: application/json"
```

## Master Data Management

### 1. Project Management

#### Create New Customer Project
```bash
curl -X POST "http://localhost:8000/api/v1/master/projects" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "customer-abc-2024",
    "project_name": "Customer ABC ERP Project",
    "customer_name": "ABC Corporation",
    "description": "ERP analysis and automation project",
    "created_by": "admin"
  }'
```

#### List All Projects
```bash
curl "http://localhost:8000/api/v1/master/projects"
```

#### Get Project Details
```bash
curl "http://localhost:8000/api/v1/master/projects/customer-abc-2024"
```

### 2. Agent Template Management

#### Create Agent Template
```bash
curl -X POST "http://localhost:8000/api/v1/master/agents" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "custom-erp-agent",
    "name": "Custom ERP Analysis Agent",
    "description": "Specialized ERP agent for custom analysis",
    "category": "ERP",
    "system_prompt_template": "erp-exception-management-prompt",
    "default_model_config": {
      "provider": "bedrock",
      "model_id": "us.anthropic.claude-sonnet-4-20250514-v1:0",
      "temperature": 0.7,
      "max_tokens": 4000
    },
    "default_mcp_servers": ["sap-abap-adt"],
    "default_tools": [],
    "default_builtin_tools": ["current_time"],
    "template_variables": {
      "system_name": "Custom ERP System",
      "analysis_scope": "Targeted Analysis"
    },
    "capabilities": [
      "Custom ERP Analysis",
      "Specialized Reporting"
    ],
    "tags": ["erp", "custom", "analysis"]
  }'
```

#### List Agent Templates
```bash
curl "http://localhost:8000/api/v1/master/agents?category=ERP"
```

#### Get Agent Template
```bash
curl "http://localhost:8000/api/v1/master/agents/custom-erp-agent"
```

#### Update Agent Template
```bash
curl -X PUT "http://localhost:8000/api/v1/master/agents/custom-erp-agent" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Updated description for custom ERP agent",
    "capabilities": [
      "Advanced ERP Analysis",
      "Custom Reporting",
      "Automation Recommendations"
    ]
  }'
```

### 3. System Prompt Management

#### Create System Prompt Template
```bash
curl -X POST "http://localhost:8000/api/v1/master/system-prompts" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt_id": "custom-analysis-prompt",
    "name": "Custom Analysis System Prompt",
    "description": "Customizable prompt for various analysis types",
    "template_content": "You are a {{analysis_type|default(\"general\")}} expert analyzing {{system_name|default(\"the system\")}}. Focus on {{focus_areas|default(\"all areas\")}} and provide {{output_format|default(\"detailed\")}} insights.",
    "variables": {
      "analysis_type": {
        "type": "string",
        "default": "general",
        "description": "Type of analysis to perform"
      },
      "system_name": {
        "type": "string", 
        "default": "the system",
        "description": "Name of the system being analyzed"
      },
      "focus_areas": {
        "type": "string",
        "default": "all areas", 
        "description": "Specific areas to focus on"
      },
      "output_format": {
        "type": "string",
        "default": "detailed",
        "description": "Format of the output"
      }
    },
    "category": "Analysis"
  }'
```

#### List System Prompts
```bash
curl "http://localhost:8000/api/v1/master/system-prompts?category=Analysis"
```

### 4. Model Configuration Management

#### Create Model Configuration
```bash
curl -X POST "http://localhost:8000/api/v1/master/model-configs" \
  -H "Content-Type: application/json" \
  -d '{
    "config_id": "anthropic-claude-3",
    "name": "Anthropic Claude 3",
    "description": "Claude 3 configuration for general tasks",
    "provider": "anthropic",
    "model_id": "claude-3-sonnet-20240229",
    "default_temperature": 0.7,
    "default_max_tokens": 3000,
    "client_config": {
      "timeout": 120,
      "max_retries": 3
    },
    "cost_per_token": 0.000015,
    "category": "LLM"
  }'
```

#### List Model Configurations
```bash
curl "http://localhost:8000/api/v1/master/model-configs?provider=anthropic"
```

### 5. Bulk Setup Operations

#### Setup ERP Defaults
```bash
curl -X POST "http://localhost:8000/api/v1/master/setup/erp-defaults"
```

## Project-Specific Operations

### 1. Agent Instance Management

#### Create Agent Instance
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
    "model_config": {
      "provider": "bedrock",
      "model_id": "us.anthropic.claude-sonnet-4-20250514-v1:0",
      "temperature": 0.5,
      "max_tokens": 4000
    },
    "custom_settings": {
      "timeout": 900,
      "enable_detailed_logging": true,
      "cost_tracking": true
    },
    "created_by": "admin"
  }'
```

#### List Agent Instances
```bash
curl "http://localhost:8000/api/v1/projects/customer-abc-2024/agent-instances"
```

#### Get Agent Instance Details
```bash
curl "http://localhost:8000/api/v1/projects/customer-abc-2024/agent-instances/instance-id-here"
```

### 2. Agent Execution

#### Execute Agent Instance (Async)
```bash
curl -X POST "http://localhost:8000/api/v1/projects/customer-abc-2024/executions" \
  -H "Content-Type: application/json" \
  -d '{
    "instance_id": "your-instance-id-here",
    "input_data": {
      "prompt": "Perform comprehensive ERP exception analysis for Q4 2024",
      "system_details": "ABC Corporation SAP Production System",
      "analysis_scope": "All business processes with focus on high-impact exceptions"
    },
    "variables": {
      "system_name": "ABC SAP Production",
      "focus_areas": "Financial, Procurement, and Inventory Exceptions",
      "analysis_depth": "Deep analysis with root cause identification",
      "output_format": "Structured JSON with executive summary"
    },
    "async_execution": true
  }'
```

#### Execute Agent Instance (Sync)
```bash
curl -X POST "http://localhost:8000/api/v1/projects/customer-abc-2024/executions" \
  -H "Content-Type: application/json" \
  -d '{
    "instance_id": "your-instance-id-here",
    "input_data": {
      "prompt": "Quick financial variance analysis",
      "analysis_type": "budget_variance"
    },
    "variables": {
      "analysis_period": "Q4 2024",
      "focus_areas": "Budget vs Actual variances"
    },
    "async_execution": false
  }'
```

#### List Executions
```bash
# All executions for project
curl "http://localhost:8000/api/v1/projects/customer-abc-2024/executions"

# Filter by status
curl "http://localhost:8000/api/v1/projects/customer-abc-2024/executions?status=completed&limit=20"

# Filter by agent instance
curl "http://localhost:8000/api/v1/projects/customer-abc-2024/executions?instance_id=your-instance-id"
```

#### Get Execution Details
```bash
curl "http://localhost:8000/api/v1/projects/customer-abc-2024/executions/execution-id-here"
```

#### Get Execution Result
```bash
curl "http://localhost:8000/api/v1/projects/customer-abc-2024/executions/execution-id-here/result"
```

### 3. Analytics and Monitoring

#### Get Project Dashboard
```bash
curl "http://localhost:8000/api/v1/projects/customer-abc-2024/analytics/dashboard"
```

#### Get Token Usage Analytics
```bash
# All token usage
curl "http://localhost:8000/api/v1/projects/customer-abc-2024/token-usage"

# Filter by date range
curl "http://localhost:8000/api/v1/projects/customer-abc-2024/token-usage?start_date=2024-01-01&end_date=2024-12-31"

# Filter by agent
curl "http://localhost:8000/api/v1/projects/customer-abc-2024/token-usage?agent_id=erp-exception-management"
```

#### Get Audit Log
```bash
# All audit logs
curl "http://localhost:8000/api/v1/projects/customer-abc-2024/audit-log"

# Filter by entity type
curl "http://localhost:8000/api/v1/projects/customer-abc-2024/audit-log?entity_type=execution&limit=50"

# Filter by action
curl "http://localhost:8000/api/v1/projects/customer-abc-2024/audit-log?action=create"
```

## Advanced Usage Examples

### 1. Complete Workflow: Create Project and Execute Agent

```bash
#!/bin/bash

# 1. Create project
PROJECT_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/master/projects" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "demo-project-2024",
    "project_name": "Demo Project 2024",
    "customer_name": "Demo Customer",
    "description": "Demo project for testing",
    "created_by": "api_user"
  }')

echo "Project created: $PROJECT_RESPONSE"

# 2. Create agent instance
INSTANCE_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/projects/demo-project-2024/agent-instances" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "erp-exception-management",
    "name": "Demo ERP Agent",
    "description": "Demo ERP exception analysis agent",
    "system_prompt_variables": {
      "system_name": "Demo SAP System",
      "analysis_scope": "Quick Analysis"
    },
    "created_by": "api_user"
  }')

echo "Agent instance created: $INSTANCE_RESPONSE"

# Extract instance ID
INSTANCE_ID=$(echo $INSTANCE_RESPONSE | jq -r '.instance_id')

# 3. Execute agent
EXECUTION_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/projects/demo-project-2024/executions" \
  -H "Content-Type: application/json" \
  -d "{
    \"instance_id\": \"$INSTANCE_ID\",
    \"input_data\": {
      \"prompt\": \"Perform demo ERP exception analysis\",
      \"system_details\": \"Demo system for testing\"
    },
    \"async_execution\": true
  }")

echo "Execution started: $EXECUTION_RESPONSE"

# Extract execution ID
EXECUTION_ID=$(echo $EXECUTION_RESPONSE | jq -r '.execution_id')

echo "Monitor execution at: http://localhost:8000/api/v1/projects/demo-project-2024/executions/$EXECUTION_ID"
```

### 2. Monitoring Execution Progress

```bash
#!/bin/bash

EXECUTION_ID="your-execution-id-here"
PROJECT_ID="demo-project-2024"

while true; do
  STATUS=$(curl -s "http://localhost:8000/api/v1/projects/$PROJECT_ID/executions/$EXECUTION_ID" | jq -r '.status')
  
  echo "Execution status: $STATUS"
  
  if [ "$STATUS" = "completed" ] || [ "$STATUS" = "failed" ]; then
    echo "Execution finished with status: $STATUS"
    
    # Get result
    curl -s "http://localhost:8000/api/v1/projects/$PROJECT_ID/executions/$EXECUTION_ID/result" | jq '.'
    break
  fi
  
  sleep 10
done
```

### 3. Bulk Token Usage Analysis

```bash
#!/bin/bash

# Get all projects
PROJECTS=$(curl -s "http://localhost:8000/api/v1/master/projects" | jq -r '.projects[].project_id')

echo "Token Usage Report"
echo "=================="

for PROJECT in $PROJECTS; do
  echo "Project: $PROJECT"
  
  USAGE=$(curl -s "http://localhost:8000/api/v1/projects/$PROJECT/token-usage")
  TOTAL_TOKENS=$(echo $USAGE | jq -r '.total_tokens')
  TOTAL_COST=$(echo $USAGE | jq -r '.total_cost')
  
  echo "  Total Tokens: $TOTAL_TOKENS"
  echo "  Total Cost: \$$TOTAL_COST"
  echo "  ---"
done
```

## Error Handling Examples

### Common Error Responses

#### 404 - Resource Not Found
```json
{
  "detail": "Project customer-xyz-2024 not found"
}
```

#### 400 - Bad Request
```json
{
  "detail": "Project customer-abc-2024 already exists"
}
```

#### 500 - Internal Server Error
```json
{
  "detail": "Failed to execute agent: Connection timeout"
}
```

### Error Handling in Scripts

```bash
#!/bin/bash

# Function to handle API calls with error checking
api_call() {
  local method=$1
  local url=$2
  local data=$3
  
  if [ -n "$data" ]; then
    response=$(curl -s -w "%{http_code}" -X $method "$url" -H "Content-Type: application/json" -d "$data")
  else
    response=$(curl -s -w "%{http_code}" -X $method "$url")
  fi
  
  http_code="${response: -3}"
  body="${response%???}"
  
  if [ $http_code -ge 200 ] && [ $http_code -lt 300 ]; then
    echo "$body"
    return 0
  else
    echo "Error: HTTP $http_code - $body" >&2
    return 1
  fi
}

# Usage example
if result=$(api_call "POST" "http://localhost:8000/api/v1/master/projects" '{"project_id":"test","project_name":"Test","customer_name":"Test Customer"}'); then
  echo "Success: $result"
else
  echo "Failed to create project"
  exit 1
fi
```

## WebSocket Examples

### Real-time Execution Monitoring

```javascript
// JavaScript WebSocket example
const executionId = 'your-execution-id-here';
const ws = new WebSocket(`ws://localhost:8000/ws/execution/${executionId}`);

ws.onopen = function(event) {
    console.log('Connected to execution monitoring');
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Execution update:', data);
    
    if (data.status === 'completed') {
        console.log('Execution completed!');
        console.log('Result:', data.output);
        ws.close();
    } else if (data.status === 'failed') {
        console.log('Execution failed:', data.error);
        ws.close();
    }
};

ws.onerror = function(error) {
    console.log('WebSocket error:', error);
};
```

## Health Checks and Monitoring

### Service Health Check
```bash
curl "http://localhost:8000/health"
```

### Master Data Health Check
```bash
curl "http://localhost:8000/api/v1/master/health"
```

### Response Example
```json
{
  "status": "healthy",
  "master_database": "ktern-masterdb",
  "projects_count": 5,
  "agents_count": 12,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## API Documentation

- **Interactive API Docs**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json
- **ReDoc Documentation**: http://localhost:8000/redoc

## Rate Limiting and Best Practices

### Best Practices

1. **Use Async Execution** for long-running tasks
2. **Monitor Token Usage** to control costs
3. **Implement Proper Error Handling** in your applications
4. **Use Project-specific Databases** for data isolation
5. **Track Executions** via audit logs for compliance
6. **Set Appropriate Timeouts** based on task complexity
7. **Use WebSockets** for real-time monitoring

### Rate Limiting (if implemented)
```bash
# Headers to check rate limits
curl -I "http://localhost:8000/api/v1/master/projects"

# Look for headers like:
# X-RateLimit-Limit: 1000
# X-RateLimit-Remaining: 999
# X-RateLimit-Reset: 1642234567
```

This comprehensive guide covers all major API operations for the multi-tenant agent orchestration system. Use these examples as a starting point for integrating with your applications.