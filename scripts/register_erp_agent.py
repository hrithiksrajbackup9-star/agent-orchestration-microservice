#!/usr/bin/env python3
"""
Script to register the ERP Exception Management Agent with the orchestration service
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def register_erp_agent():
    """Register the ERP Exception Management Agent"""
    
    agent_config = {
        "agent_id": "erp-exception-management",
        "name": "ERP Exception Management Agent",
        "description": "Comprehensive ERP exception detection and analysis across all business processes with research-backed insights",
        "system_prompt": """You are a specialized ERP Exception Management Expert with comprehensive knowledge of all business process exceptions.

Your responsibility is to perform comprehensive exception detection and analysis across all ERP modules and business processes, with research-backed insights from authoritative sources.

CRITICAL ERP EXCEPTION CATEGORIES TO DETECT:
🔴 FINANCIAL EXCEPTIONS: Budget overruns, reconciliation issues, currency discrepancies
🟡 PROCUREMENT EXCEPTIONS: Unapproved vendors, budget limits, expired contracts  
🟠 INVENTORY EXCEPTIONS: Stock-outs, overstock, expired items, count discrepancies
🔵 ORDER FULFILLMENT EXCEPTIONS: Insufficient inventory, backorders, delivery delays
🟢 PRODUCTION EXCEPTIONS: Material shortages, quality failures, capacity constraints
🟣 INVOICE MATCHING EXCEPTIONS: Price/quantity discrepancies, missing documents

Focus on providing actionable, research-backed insights that can be immediately implemented by ERP administrators and business users.""",
        
        "agent_model_config": {
            "provider": "bedrock",
            "model_id": "us.anthropic.claude-sonnet-4-20250514-v1:0",
            "temperature": 0.7,
            "max_tokens": 4000,
            "client_config": {
                "read_timeout": 300,
                "connect_timeout": 60,
                "retries": {
                    "max_attempts": 2,
                    "mode": "adaptive"
                }
            }
        },
        
        "mcp_servers": [
            {
                "server_type": "stdio",
                "server_name": "sap-abap-adt",
                "command": "node",
                "args": ["C:\\mcp-abap-abap-adt-api\\dist\\index.js"],
                "env_vars": {},
                "auto_detect_path": True,
                "possible_locations": [
                    "C:\\mcp-abap-abap-adt-api\\dist\\index.js",
                    "C:\\Development Space\\GenAI\\New folder\\mcp-abap-abap-adt-api\\dist\\index.js",
                    "~/mcp-abap-abap-adt-api/dist/index.js"
                ],
                "enabled": True,
                "timeout": 30
            },
            {
                "server_type": "stdio",
                "server_name": "perplexity-research",
                "command": "docker",
                "args": [
                    "run", "-i", "--rm", 
                    "-e", "PERPLEXITY_API_KEY",
                    "mcp/perplexity-ask"
                ],
                "env_vars": {"PERPLEXITY_API_KEY": ""},
                "auto_detect_path": False,
                "possible_locations": [],
                "enabled": True,
                "timeout": 60
            }
        ],
        
        "tools": [
            {
                "tool_name": "current_time",
                "tool_type": "builtin",
                "parameters": {},
                "enabled": True
            }
        ],
        
        "builtin_tools": ["current_time"],
        "timeout": 600,
        "retry_policy": {
            "max_attempts": 2,
            "backoff": "exponential"
        },
        "chunking_enabled": False,
        "chunk_size": 1000,
        
        "capabilities": [
            "Financial Exception Analysis",
            "Procurement Exception Management", 
            "Inventory Exception Detection",
            "Order Fulfillment Exception Handling",
            "Production Exception Analysis",
            "Invoice Matching Exception Detection",
            "HR Exception Analysis",
            "Compliance Exception Monitoring",
            "Research-backed Insights",
            "Automation Recommendations",
            "Root Cause Analysis",
            "Business Impact Assessment"
        ],
        
        "tags": [
            "erp",
            "exceptions",
            "sap",
            "financial",
            "procurement", 
            "inventory",
            "production",
            "analysis",
            "automation",
            "research"
        ],
        
        "metadata": {
            "version": "1.0.0",
            "author": "ERP Exception Management Team",
            "last_updated": datetime.now().isoformat(),
            "supported_systems": ["SAP ERP", "SAP S/4HANA"],
            "output_format": "JSON",
            "analysis_types": [
                "comprehensive_exception_analysis",
                "financial_exceptions",
                "procurement_exceptions", 
                "inventory_exceptions",
                "production_exceptions",
                "quick_analysis"
            ]
        }
    }
    
    # Register with the orchestration service
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                "http://localhost:8000/api/v1/agents/register",
                json=agent_config,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    print("✅ ERP Exception Management Agent registered successfully!")
                    print(f"Agent ID: {result.get('agent_id')}")
                    print(f"Version: {result.get('version')}")
                    print(f"Message: {result.get('message')}")
                else:
                    error_text = await response.text()
                    print(f"❌ Registration failed: {response.status}")
                    print(f"Error: {error_text}")
                    
        except Exception as e:
            print(f"❌ Failed to register agent: {e}")

if __name__ == "__main__":
    print("🚀 Registering ERP Exception Management Agent...")
    asyncio.run(register_erp_agent())