#!/usr/bin/env python3
"""
ERP Exception Management Client
A command-line client for interacting with the ERP Exception Management microservice
"""

import asyncio
import aiohttp
import json
import sys
import argparse
from typing import Dict, Any, Optional
from datetime import datetime
import time

class ERPExceptionClient:
    """Client for ERP Exception Management API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1/erp"
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Get ERP service status"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.api_base}/status") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Failed to get status: {response.status}")
    
    async def start_comprehensive_analysis(self, system_details: str = "", async_execution: bool = True) -> Dict[str, Any]:
        """Start comprehensive ERP exception analysis"""
        payload = {
            "system_details": system_details,
            "async_execution": async_execution
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.api_base}/analyze", json=payload) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to start analysis: {response.status} - {error_text}")
    
    async def get_analysis_result(self, execution_id: str) -> Dict[str, Any]:
        """Get analysis result by execution ID"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.api_base}/analyze/{execution_id}") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to get result: {response.status} - {error_text}")
    
    async def quick_analysis(self, query: str) -> Dict[str, Any]:
        """Perform quick ERP exception analysis"""
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.api_base}/quick-analysis", params={"query": query}) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to perform quick analysis: {response.status} - {error_text}")
    
    async def wait_for_completion(self, execution_id: str, timeout: int = 600) -> Dict[str, Any]:
        """Wait for analysis completion with polling"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            result = await self.get_analysis_result(execution_id)
            status = result.get("status")
            
            if status in ["completed", "failed"]:
                return result
            
            print(f"Status: {status} - waiting...")
            await asyncio.sleep(10)  # Poll every 10 seconds
        
        raise Exception(f"Analysis timed out after {timeout} seconds")

def print_status(status: Dict[str, Any]):
    """Print service status in a formatted way"""
    print("=" * 60)
    print("🚨 ERP EXCEPTION MANAGEMENT SERVICE STATUS 🚨")
    print("=" * 60)
    print(f"Service: {status.get('service_name', 'Unknown')}")
    print(f"Status: {status.get('status', 'Unknown')}")
    print()
    
    sap_mcp = status.get('sap_mcp_server', {})
    print(f"📡 SAP MCP Server: {'✅ Available' if sap_mcp.get('available') else '❌ Not Available'}")
    if sap_mcp.get('path'):
        print(f"   Path: {sap_mcp['path']}")
    
    perplexity = status.get('perplexity_docker', {})
    print(f"🐳 Perplexity Docker: {'✅ Available' if perplexity.get('available') else '❌ Not Available'}")
    print(f"🔑 API Key Configured: {'✅ Yes' if perplexity.get('api_key_configured') else '❌ No'}")
    
    print()
    print("🛠️ Capabilities:")
    for capability in status.get('capabilities', []):
        print(f"   • {capability}")
    print("=" * 60)

def print_analysis_result(result: Dict[str, Any]):
    """Print analysis result in a formatted way"""
    print("=" * 60)
    print("📊 ERP EXCEPTION ANALYSIS RESULT")
    print("=" * 60)
    
    if result.get('status') == 'completed':
        analysis_result = result.get('result', {})
        print(f"✅ Status: {result.get('status')}")
        print(f"⏱️ Duration: {result.get('duration_ms', 0)}ms")
        print(f"📄 Report Path: {analysis_result.get('report_path', 'N/A')}")
        print(f"🕐 Analysis Time: {analysis_result.get('analysis_timestamp', 'N/A')}")
        print(f"🖥️ System: {analysis_result.get('system_analyzed', 'N/A')}")
        
        mcp_info = analysis_result.get('mcp_connections', {})
        print(f"🔧 SAP Tools: {mcp_info.get('sap_tools_count', 0)}")
        print(f"🔍 Research Tools: {mcp_info.get('perplexity_tools_count', 0)}")
        print(f"📚 Research Available: {'✅ Yes' if mcp_info.get('research_available') else '❌ No'}")
        
    elif result.get('status') == 'failed':
        print(f"❌ Status: {result.get('status')}")
        print(f"💥 Error: {result.get('error', 'Unknown error')}")
        
    else:
        print(f"⏳ Status: {result.get('status')}")
        if result.get('started_at'):
            print(f"🕐 Started: {result.get('started_at')}")
    
    print("=" * 60)

async def main():
    parser = argparse.ArgumentParser(description="ERP Exception Management Client")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL of the service")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Status command
    subparsers.add_parser("status", help="Get service status")
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Start comprehensive analysis")
    analyze_parser.add_argument("--system", default="", help="System details")
    analyze_parser.add_argument("--sync", action="store_true", help="Run synchronously")
    analyze_parser.add_argument("--wait", action="store_true", help="Wait for completion")
    
    # Quick analysis command
    quick_parser = subparsers.add_parser("quick", help="Quick analysis")
    quick_parser.add_argument("query", help="Analysis query")
    
    # Get result command
    result_parser = subparsers.add_parser("result", help="Get analysis result")
    result_parser.add_argument("execution_id", help="Execution ID")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    client = ERPExceptionClient(args.url)
    
    try:
        if args.command == "status":
            status = await client.get_service_status()
            print_status(status)
            
        elif args.command == "analyze":
            print("🚀 Starting ERP Exception Analysis...")
            result = await client.start_comprehensive_analysis(
                system_details=args.system,
                async_execution=not args.sync
            )
            
            if args.sync or not result.get('execution_id'):
                print_analysis_result(result)
            else:
                execution_id = result['execution_id']
                print(f"✅ Analysis started with ID: {execution_id}")
                
                if args.wait:
                    print("⏳ Waiting for completion...")
                    final_result = await client.wait_for_completion(execution_id)
                    print_analysis_result(final_result)
                else:
                    print(f"💡 Use 'python client/erp_client.py result {execution_id}' to check status")
            
        elif args.command == "quick":
            print(f"🔍 Quick Analysis: {args.query}")
            result = await client.quick_analysis(args.query)
            print_analysis_result(result)
            
        elif args.command == "result":
            result = await client.get_analysis_result(args.execution_id)
            print_analysis_result(result)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())