#!/usr/bin/env python3
"""
Dynamic ERP Exception Management Client
Database-driven agent execution via REST API
"""

import asyncio
import aiohttp
import json
import sys
import argparse
from typing import Dict, Any, Optional
from datetime import datetime
import time

class DynamicERPClient:
    """Client for database-driven ERP Exception Management API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1/dynamic"
    
    async def execute_agent(
        self, 
        agent_id: str, 
        input_data: Dict[str, Any],
        variables: Dict[str, Any] = None,
        async_execution: bool = True
    ) -> Dict[str, Any]:
        """Execute agent by ID"""
        payload = {
            "input_data": input_data,
            "variables": variables or {},
            "async_execution": async_execution
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.api_base}/execute/{agent_id}", json=payload) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to execute agent: {response.status} - {error_text}")
    
    async def get_execution_status(self, execution_id: str) -> Dict[str, Any]:
        """Get execution status"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.api_base}/execution/{execution_id}/status") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to get status: {response.status} - {error_text}")
    
    async def get_execution_result(self, execution_id: str) -> Dict[str, Any]:
        """Get execution result"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.api_base}/execution/{execution_id}/result") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to get result: {response.status} - {error_text}")
    
    async def list_executions(
        self, 
        agent_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """List executions"""
        params = {"limit": limit}
        if agent_id:
            params["agent_id"] = agent_id
        if status:
            params["status"] = status
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.api_base}/executions", params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to list executions: {response.status} - {error_text}")
    
    async def list_templates(self, category: Optional[str] = None) -> Dict[str, Any]:
        """List available agent templates"""
        params = {}
        if category:
            params["category"] = category
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.api_base}/templates", params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to list templates: {response.status} - {error_text}")
    
    async def create_agent_from_template(
        self,
        template_id: str,
        agent_id: str,
        variables: Dict[str, Any] = None,
        overrides: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create agent from template"""
        payload = {
            "template_id": template_id,
            "agent_id": agent_id,
            "variables": variables or {},
            "overrides": overrides or {}
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.api_base}/agents/from-template", json=payload) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to create agent: {response.status} - {error_text}")
    
    async def wait_for_completion(self, execution_id: str, timeout: int = 600) -> Dict[str, Any]:
        """Wait for execution completion with polling"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = await self.get_execution_status(execution_id)
            
            if status.get("status") in ["completed", "failed"]:
                if status.get("status") == "completed":
                    return await self.get_execution_result(execution_id)
                else:
                    return status
            
            print(f"Status: {status.get('status')} - waiting...")
            await asyncio.sleep(10)  # Poll every 10 seconds
        
        raise Exception(f"Execution timed out after {timeout} seconds")

def print_execution_result(result: Dict[str, Any]):
    """Print execution result in a formatted way"""
    print("=" * 80)
    print("📊 DYNAMIC ERP EXCEPTION ANALYSIS RESULT")
    print("=" * 80)
    
    print(f"🆔 Result ID: {result.get('result_id')}")
    print(f"⚡ Execution ID: {result.get('execution_id')}")
    print(f"🤖 Agent ID: {result.get('agent_id')}")
    print(f"📋 Result Type: {result.get('result_type')}")
    print(f"🕐 Created: {result.get('created_at')}")
    
    if result.get('summary'):
        print(f"\n📝 Summary:")
        print(f"   {result.get('summary')}")
    
    if result.get('metrics'):
        print(f"\n📊 Metrics:")
        for key, value in result.get('metrics', {}).items():
            print(f"   • {key}: {value}")
    
    # Try to parse and display structured result
    result_data = result.get('result_data', {})
    response = result_data.get('response', '')
    
    if response and isinstance(response, str) and response.strip().startswith('{'):
        try:
            parsed = json.loads(response)
            if 'exception_summary' in parsed:
                summary = parsed['exception_summary']
                print(f"\n🚨 Exception Analysis Summary:")
                print(f"   • Total Exceptions: {summary.get('total_exceptions', 0)}")
                print(f"   • High Severity: {summary.get('high_severity_count', 0)}")
                print(f"   • Medium Severity: {summary.get('medium_severity_count', 0)}")
                print(f"   • Low Severity: {summary.get('low_severity_count', 0)}")
                print(f"   • Automation Opportunities: {summary.get('automation_opportunities', 0)}")
        except:
            pass
    
    print("=" * 80)

def print_templates(templates: Dict[str, Any]):
    """Print available templates"""
    print("=" * 80)
    print("📋 AVAILABLE AGENT TEMPLATES")
    print("=" * 80)
    
    for template in templates.get('templates', []):
        print(f"\n🤖 {template.get('name')}")
        print(f"   ID: {template.get('template_id')}")
        print(f"   Category: {template.get('category')}")
        print(f"   Description: {template.get('description')}")
        
        if template.get('capabilities'):
            print(f"   Capabilities:")
            for cap in template.get('capabilities', [])[:5]:  # Show first 5
                print(f"     • {cap}")
        
        if template.get('tags'):
            print(f"   Tags: {', '.join(template.get('tags', []))}")
    
    print("=" * 80)

async def main():
    parser = argparse.ArgumentParser(description="Dynamic ERP Exception Management Client")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL of the service")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Execute command
    execute_parser = subparsers.add_parser("execute", help="Execute agent")
    execute_parser.add_argument("agent_id", help="Agent ID to execute")
    execute_parser.add_argument("--prompt", default="Perform comprehensive ERP exception analysis", help="Analysis prompt")
    execute_parser.add_argument("--system", default="", help="System details")
    execute_parser.add_argument("--sync", action="store_true", help="Run synchronously")
    execute_parser.add_argument("--wait", action="store_true", help="Wait for completion")
    execute_parser.add_argument("--variables", help="JSON string of template variables")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Get execution status")
    status_parser.add_argument("execution_id", help="Execution ID")
    
    # Result command
    result_parser = subparsers.add_parser("result", help="Get execution result")
    result_parser.add_argument("execution_id", help="Execution ID")
    
    # List executions command
    list_parser = subparsers.add_parser("list", help="List executions")
    list_parser.add_argument("--agent", help="Filter by agent ID")
    list_parser.add_argument("--status", help="Filter by status")
    list_parser.add_argument("--limit", type=int, default=10, help="Limit results")
    
    # Templates command
    templates_parser = subparsers.add_parser("templates", help="List available templates")
    templates_parser.add_argument("--category", help="Filter by category")
    
    # Create agent command
    create_parser = subparsers.add_parser("create", help="Create agent from template")
    create_parser.add_argument("template_id", help="Template ID")
    create_parser.add_argument("agent_id", help="New agent ID")
    create_parser.add_argument("--variables", help="JSON string of template variables")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    client = DynamicERPClient(args.url)
    
    try:
        if args.command == "execute":
            variables = {}
            if args.variables:
                variables = json.loads(args.variables)
            
            input_data = {
                "prompt": args.prompt,
                "system_details": args.system
            }
            
            print(f"🚀 Executing agent: {args.agent_id}")
            result = await client.execute_agent(
                agent_id=args.agent_id,
                input_data=input_data,
                variables=variables,
                async_execution=not args.sync
            )
            
            execution_id = result.get('execution_id')
            print(f"✅ Execution started: {execution_id}")
            
            if args.sync or args.wait:
                print("⏳ Waiting for completion...")
                final_result = await client.wait_for_completion(execution_id)
                print_execution_result(final_result)
            else:
                print(f"💡 Use 'python client/dynamic_erp_client.py result {execution_id}' to check result")
        
        elif args.command == "status":
            status = await client.get_execution_status(args.execution_id)
            print(f"Status: {status.get('status')}")
            print(f"Started: {status.get('started_at')}")
            if status.get('completed_at'):
                print(f"Completed: {status.get('completed_at')}")
            if status.get('duration_ms'):
                print(f"Duration: {status.get('duration_ms')}ms")
            if status.get('error_message'):
                print(f"Error: {status.get('error_message')}")
        
        elif args.command == "result":
            result = await client.get_execution_result(args.execution_id)
            print_execution_result(result)
        
        elif args.command == "list":
            executions = await client.list_executions(
                agent_id=args.agent,
                status=args.status,
                limit=args.limit
            )
            
            print("Recent Executions:")
            for exec in executions.get('executions', []):
                print(f"  {exec.get('execution_id')} | {exec.get('agent_id')} | {exec.get('status')} | {exec.get('started_at')}")
        
        elif args.command == "templates":
            templates = await client.list_templates(category=args.category)
            print_templates(templates)
        
        elif args.command == "create":
            variables = {}
            if args.variables:
                variables = json.loads(args.variables)
            
            result = await client.create_agent_from_template(
                template_id=args.template_id,
                agent_id=args.agent_id,
                variables=variables
            )
            
            print(f"✅ Agent created: {result.get('agent_id')}")
            print(f"From template: {result.get('template_id')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())