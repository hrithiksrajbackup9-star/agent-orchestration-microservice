#!/usr/bin/env python3
"""
Setup Multi-tenant Master Data and Example Project
"""
import asyncio
import aiohttp
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

async def setup_master_data():
    """Setup master data via API"""
    
    async with aiohttp.ClientSession() as session:
        
        # 1. Setup ERP defaults (creates master templates)
        print("🚀 Setting up ERP default master data...")
        async with session.post(f"{BASE_URL}/master/setup/erp-defaults") as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ {result['message']}")
                for component in result['components_created']:
                    print(f"   • {component}")
            else:
                error = await response.text()
                print(f"❌ Failed to setup ERP defaults: {error}")
                return False
        
        # 2. Create additional system prompts
        print("\n📝 Creating additional system prompts...")
        
        financial_prompt = {
            "prompt_id": "financial-analysis-prompt",
            "name": "Financial Analysis System Prompt",
            "description": "Specialized prompt for financial data analysis",
            "template_content": """You are a Financial Analysis Expert specializing in {{analysis_type|default('general financial analysis')}}.

Your focus areas include:
- {{focus_areas|default('Financial reporting, budgeting, and variance analysis')}}
- Compliance with {{compliance_standards|default('GAAP and IFRS standards')}}
- Risk assessment for {{risk_categories|default('credit, market, and operational risks')}}

System Context: {{system_name|default('Financial System')}}
Analysis Period: {{analysis_period|default('Current fiscal year')}}

Provide detailed insights with actionable recommendations.""",
            "variables": {
                "analysis_type": {"type": "string", "default": "general financial analysis"},
                "focus_areas": {"type": "string", "default": "Financial reporting, budgeting, and variance analysis"},
                "compliance_standards": {"type": "string", "default": "GAAP and IFRS standards"},
                "risk_categories": {"type": "string", "default": "credit, market, and operational risks"},
                "system_name": {"type": "string", "default": "Financial System"},
                "analysis_period": {"type": "string", "default": "Current fiscal year"}
            },
            "category": "Finance"
        }
        
        async with session.post(f"{BASE_URL}/master/system-prompts", json=financial_prompt) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ Created: {result['name']}")
            else:
                error = await response.text()
                print(f"❌ Failed to create financial prompt: {error}")
        
        # 3. Create additional model configurations
        print("\n🤖 Creating additional model configurations...")
        
        openai_config = {
            "config_id": "openai-gpt-4",
            "name": "OpenAI GPT-4",
            "description": "OpenAI GPT-4 configuration for general tasks",
            "provider": "openai",
            "model_id": "gpt-4",
            "default_temperature": 0.7,
            "default_max_tokens": 2000,
            "client_config": {
                "timeout": 60,
                "max_retries": 3
            },
            "cost_per_token": 0.00003,
            "category": "LLM"
        }
        
        async with session.post(f"{BASE_URL}/master/model-configs", json=openai_config) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ Created: {result['name']}")
            else:
                error = await response.text()
                print(f"❌ Failed to create OpenAI config: {error}")
        
        # 4. Create additional tools
        print("\n🛠️ Creating additional tools...")
        
        file_write_tool = {
            "tool_id": "file_write",
            "name": "File Write Tool",
            "description": "Write content to files",
            "tool_type": "builtin",
            "parameters_schema": {
                "file_path": {"type": "string", "required": True},
                "content": {"type": "string", "required": True}
            },
            "category": "File Operations"
        }
        
        async with session.post(f"{BASE_URL}/master/tools", json=file_write_tool) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ Created: {result['name']}")
            else:
                error = await response.text()
                print(f"❌ Failed to create file write tool: {error}")
        
        # 5. Create financial analysis agent template
        print("\n🤖 Creating financial analysis agent template...")
        
        financial_agent = {
            "agent_id": "financial-analysis-agent",
            "name": "Financial Analysis Agent",
            "description": "Specialized agent for financial data analysis and reporting",
            "category": "Finance",
            "system_prompt_template": "financial-analysis-prompt",
            "default_model_config": {
                "provider": "bedrock",
                "model_id": "us.anthropic.claude-sonnet-4-20250514-v1:0",
                "temperature": 0.3,
                "max_tokens": 3000
            },
            "default_mcp_servers": ["sap-abap-adt"],
            "default_tools": [],
            "default_builtin_tools": ["current_time", "file_write"],
            "template_variables": {
                "analysis_type": "Financial Exception Analysis",
                "system_name": "SAP Financial Module"
            },
            "capabilities": [
                "Financial Data Analysis",
                "Budget Variance Analysis",
                "Risk Assessment",
                "Compliance Reporting",
                "Financial Forecasting"
            ],
            "tags": ["finance", "analysis", "reporting", "compliance"]
        }
        
        async with session.post(f"{BASE_URL}/master/agents", json=financial_agent) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ Created: {result['name']}")
            else:
                error = await response.text()
                print(f"❌ Failed to create financial agent: {error}")
        
        print("\n✅ Master data setup completed!")
        return True

async def create_example_project():
    """Create example customer project"""
    
    async with aiohttp.ClientSession() as session:
        
        print("\n🏢 Creating example customer project...")
        
        project_data = {
            "project_id": "acme-corp-2024",
            "project_name": "ACME Corporation ERP Analysis",
            "customer_name": "ACME Corporation",
            "description": "ERP exception management and financial analysis for ACME Corp",
            "created_by": "system_admin"
        }
        
        async with session.post(f"{BASE_URL}/master/projects", json=project_data) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ Created project: {result['project']['project_name']}")
                print(f"   Database: {result['project']['database_name']}")
                return result['project']['project_id']
            else:
                error = await response.text()
                print(f"❌ Failed to create project: {error}")
                return None

async def create_agent_instances(project_id: str):
    """Create agent instances for the project"""
    
    async with aiohttp.ClientSession() as session:
        
        print(f"\n🤖 Creating agent instances for project: {project_id}")
        
        # 1. Create ERP Exception Management instance
        erp_instance = {
            "agent_id": "erp-exception-management",
            "name": "ACME ERP Exception Manager",
            "description": "ERP exception analysis for ACME Corporation",
            "system_prompt_variables": {
                "system_name": "ACME SAP Production System",
                "analysis_scope": "Comprehensive Exception Analysis",
                "focus_areas": "Financial, Procurement, and Inventory Exceptions"
            },
            "custom_settings": {
                "timeout": 900,
                "enable_detailed_logging": True
            },
            "created_by": "system_admin"
        }
        
        async with session.post(f"{BASE_URL}/projects/{project_id}/agent-instances", json=erp_instance) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ Created ERP instance: {result['name']}")
                erp_instance_id = result['instance_id']
            else:
                error = await response.text()
                print(f"❌ Failed to create ERP instance: {error}")
                return None, None
        
        # 2. Create Financial Analysis instance
        financial_instance = {
            "agent_id": "financial-analysis-agent",
            "name": "ACME Financial Analyzer",
            "description": "Financial analysis and reporting for ACME Corporation",
            "system_prompt_variables": {
                "analysis_type": "Comprehensive Financial Analysis",
                "system_name": "ACME Financial System",
                "compliance_standards": "SOX and GAAP compliance",
                "analysis_period": "Q4 2024"
            },
            "model_config": {
                "provider": "bedrock",
                "model_id": "us.anthropic.claude-sonnet-4-20250514-v1:0",
                "temperature": 0.2,
                "max_tokens": 4000
            },
            "custom_settings": {
                "timeout": 600,
                "enable_cost_tracking": True
            },
            "created_by": "system_admin"
        }
        
        async with session.post(f"{BASE_URL}/projects/{project_id}/agent-instances", json=financial_instance) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ Created Financial instance: {result['name']}")
                financial_instance_id = result['instance_id']
            else:
                error = await response.text()
                print(f"❌ Failed to create Financial instance: {error}")
                return erp_instance_id, None
        
        return erp_instance_id, financial_instance_id

async def run_example_executions(project_id: str, erp_instance_id: str, financial_instance_id: str):
    """Run example executions"""
    
    async with aiohttp.ClientSession() as session:
        
        print(f"\n⚡ Running example executions for project: {project_id}")
        
        # 1. Execute ERP Exception Analysis
        if erp_instance_id:
            erp_execution = {
                "instance_id": erp_instance_id,
                "input_data": {
                    "prompt": "Perform comprehensive ERP exception analysis for ACME Corporation",
                    "system_details": "ACME SAP Production System - Q4 2024 Analysis"
                },
                "variables": {
                    "focus_areas": "High-priority financial and procurement exceptions",
                    "analysis_depth": "Deep analysis with root cause identification"
                },
                "async_execution": True
            }
            
            async with session.post(f"{BASE_URL}/projects/{project_id}/executions", json=erp_execution) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Started ERP execution: {result['execution_id']}")
                else:
                    error = await response.text()
                    print(f"❌ Failed to start ERP execution: {error}")
        
        # 2. Execute Financial Analysis
        if financial_instance_id:
            financial_execution = {
                "instance_id": financial_instance_id,
                "input_data": {
                    "prompt": "Analyze Q4 2024 financial performance and identify key variances",
                    "analysis_scope": "Budget vs Actual, Cash Flow, and Risk Assessment"
                },
                "variables": {
                    "analysis_period": "Q4 2024",
                    "focus_areas": "Budget variances, cash flow analysis, and compliance review"
                },
                "async_execution": True
            }
            
            async with session.post(f"{BASE_URL}/projects/{project_id}/executions", json=financial_execution) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Started Financial execution: {result['execution_id']}")
                else:
                    error = await response.text()
                    print(f"❌ Failed to start Financial execution: {error}")

async def show_api_examples():
    """Show API usage examples"""
    
    print("\n" + "="*80)
    print("📚 API USAGE EXAMPLES")
    print("="*80)
    
    examples = [
        {
            "title": "1. List All Projects",
            "method": "GET",
            "url": f"{BASE_URL}/master/projects",
            "description": "Get all customer projects"
        },
        {
            "title": "2. Get Project Dashboard",
            "method": "GET", 
            "url": f"{BASE_URL}/projects/acme-corp-2024/analytics/dashboard",
            "description": "Get project analytics and metrics"
        },
        {
            "title": "3. List Agent Instances",
            "method": "GET",
            "url": f"{BASE_URL}/projects/acme-corp-2024/agent-instances",
            "description": "Get all agent instances for a project"
        },
        {
            "title": "4. Execute Agent Instance",
            "method": "POST",
            "url": f"{BASE_URL}/projects/acme-corp-2024/executions",
            "body": {
                "instance_id": "your-instance-id",
                "input_data": {
                    "prompt": "Analyze financial exceptions",
                    "system_details": "Production system"
                },
                "variables": {
                    "focus_areas": "Financial exceptions",
                    "analysis_depth": "Comprehensive"
                },
                "async_execution": True
            },
            "description": "Execute an agent instance"
        },
        {
            "title": "5. Get Token Usage Analytics",
            "method": "GET",
            "url": f"{BASE_URL}/projects/acme-corp-2024/token-usage?start_date=2024-01-01",
            "description": "Get token usage and cost analytics"
        },
        {
            "title": "6. Create New Agent Template",
            "method": "POST",
            "url": f"{BASE_URL}/master/agents",
            "body": {
                "agent_id": "custom-agent",
                "name": "Custom Analysis Agent",
                "description": "Custom agent for specific analysis",
                "category": "Custom",
                "system_prompt_template": "custom-prompt-id",
                "default_model_config": {
                    "provider": "bedrock",
                    "model_id": "us.anthropic.claude-sonnet-4-20250514-v1:0",
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                "capabilities": ["Custom Analysis"],
                "tags": ["custom", "analysis"]
            },
            "description": "Create new master agent template"
        },
        {
            "title": "7. Get Audit Log",
            "method": "GET",
            "url": f"{BASE_URL}/projects/acme-corp-2024/audit-log?entity_type=execution&limit=50",
            "description": "Get audit trail for project activities"
        }
    ]
    
    for example in examples:
        print(f"\n{example['title']}")
        print(f"Description: {example['description']}")
        print(f"{example['method']} {example['url']}")
        
        if 'body' in example:
            print("Request Body:")
            print(json.dumps(example['body'], indent=2))
        
        print("-" * 60)
    
    print(f"\n🌐 API Documentation: {BASE_URL.replace('/api/v1', '')}/docs")
    print(f"🔍 Health Check: {BASE_URL}/master/health")

async def main():
    """Main setup function"""
    
    print("🚀 Setting up Multi-tenant Agent Orchestration System")
    print("="*60)
    
    # 1. Setup master data
    success = await setup_master_data()
    if not success:
        print("❌ Master data setup failed. Exiting.")
        return
    
    # 2. Create example project
    project_id = await create_example_project()
    if not project_id:
        print("❌ Project creation failed. Exiting.")
        return
    
    # 3. Create agent instances
    erp_instance_id, financial_instance_id = await create_agent_instances(project_id)
    
    # 4. Run example executions
    await run_example_executions(project_id, erp_instance_id, financial_instance_id)
    
    # 5. Show API examples
    await show_api_examples()
    
    print("\n" + "="*80)
    print("✅ MULTI-TENANT SETUP COMPLETED SUCCESSFULLY!")
    print("="*80)
    print(f"📊 Master Database: ktern-masterdb")
    print(f"🏢 Example Project: {project_id}")
    print(f"💾 Project Database: ktern-project-{project_id}")
    print(f"🤖 Agent Instances Created: {2 if financial_instance_id else 1}")
    print(f"⚡ Example Executions Started")
    print(f"🌐 API Base URL: {BASE_URL}")
    print(f"📖 Documentation: {BASE_URL.replace('/api/v1', '')}/docs")

if __name__ == "__main__":
    asyncio.run(main())