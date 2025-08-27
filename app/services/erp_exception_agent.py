import os
import json
import logging
import subprocess
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from contextlib import contextmanager
import threading
import asyncio
from strands import Agent, tool
from strands.models import BedrockModel
from strands_tools import current_time, file_write
from app.config import settings

logger = logging.getLogger(__name__)

class ERPExceptionManagementService:
    """
    ERP Exception Management Service integrated with the microservice framework
    """

    def __init__(self):
        """Initialize the ERP Exception Management Service."""
        self.sap_mcp_server_path = None
        self.perplexity_docker_available = False
        self.perplexity_api_key = settings.perplexity_api_key
        self._connection_lock = threading.Lock()
        
        # Initialize paths and connections
        self._initialize_service()

    def _initialize_service(self):
        """Initialize the service with proper error handling."""
        try:
            # Auto-detect SAP MCP server path
            self.sap_mcp_server_path = self._find_mcp_server_path()
            
            # Check Perplexity Docker setup
            self.perplexity_docker_available = self._check_perplexity_docker_setup()
            
            if not self.sap_mcp_server_path:
                logger.warning("SAP MCP server not found - some features will be limited")
            
            # Verify dependencies
            self._verify_nodejs()
            
            if self.perplexity_docker_available:
                self._verify_docker()
            
            # Test the MCP servers
            if self.sap_mcp_server_path:
                self._test_mcp_server(self.sap_mcp_server_path, "SAP ABAP")
            
            if self.perplexity_docker_available:
                self._test_perplexity_docker()
            
            logger.info("ERP Exception Management Service initialized successfully")
           
        except Exception as e:
            logger.error(f"Failed to initialize ERP Exception Management Service: {str(e)}")
            # Don't raise exception - allow service to start with limited functionality

    def _find_mcp_server_path(self) -> Optional[str]:
        """Auto-detect the MCP server path."""
        possible_locations = [
            # Most likely locations
            r"C:\mcp-abap-abap-adt-api\dist\index.js",
            r"C:\Development Space\GenAI\New folder\mcp-abap-abap-adt-api\dist\index.js",
            
            # Relative to current working directory
            os.path.join(os.getcwd(), "mcp-abap-abap-adt-api", "dist", "index.js"),
            os.path.join(os.getcwd(), "..", "mcp-abap-abap-adt-api", "dist", "index.js"),
            
            # Common development locations
            os.path.expanduser("~/mcp-abap-abap-adt-api/dist/index.js"),
            os.path.expanduser("~/Development/mcp-abap-abap-idt-api/dist/index.js"),
            
            # Check environment variable
            os.environ.get("MCP_ABAP_SERVER_PATH", ""),
        ]
        
        for path in possible_locations:
            if path and os.path.exists(path):
                logger.info(f"✅ Found SAP MCP server at: {path}")
                return path
        
        return None

    def _check_perplexity_docker_setup(self) -> bool:
        """Check if Perplexity MCP Docker setup is available."""
        try:
            # Check if Docker is available
            result = subprocess.run(["docker", "--version"], capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                logger.warning("⚠️ Docker not available - Perplexity research features will be limited")
                return False
                
            # Check if PERPLEXITY_API_KEY is set
            if not self.perplexity_api_key:
                logger.warning("⚠️ PERPLEXITY_API_KEY not set - Perplexity research features will be limited")
                return False
                
            # Try to pull/check the Docker image
            logger.info("🐳 Checking Perplexity MCP Docker image...")
            result = subprocess.run(
                ["docker", "images", "mcp/perplexity-ask", "--format", "{{.Repository}}:{{.Tag}}"],
                capture_output=True, text=True, timeout=30
            )
            
            if "mcp/perplexity-ask" not in result.stdout:
                logger.info("🐳 Pulling Perplexity MCP Docker image...")
                pull_result = subprocess.run(
                    ["docker", "pull", "mcp/perplexity-ask"],
                    capture_output=True, text=True, timeout=300
                )
                if pull_result.returncode != 0:
                    logger.error(f"❌ Failed to pull Docker image: {pull_result.stderr}")
                    return False
            
            logger.info("✅ Perplexity MCP Docker setup is ready")
            return True
            
        except subprocess.TimeoutExpired:
            logger.error("❌ Docker command timed out")
            return False
        except FileNotFoundError:
            logger.warning("⚠️ Docker not found in PATH")
            return False
        except Exception as e:
            logger.warning(f"⚠️ Docker setup check failed: {e}")
            return False

    def _verify_docker(self):
        """Verify Docker installation."""
        try:
            result = subprocess.run(["docker", "--version"], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                logger.info(f"Docker version: {result.stdout.strip()}")
            else:
                raise Exception("Docker not working properly")
        except subprocess.TimeoutExpired:
            raise Exception("Docker command timed out - check Docker installation")
        except FileNotFoundError:
            raise Exception("Docker not found in PATH")

    def _verify_nodejs(self):
        """Verify Node.js installation."""
        try:
            result = subprocess.run(["node", "--version"], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                logger.info(f"Node.js version: {result.stdout.strip()}")
            else:
                raise Exception("Node.js not working properly")
        except subprocess.TimeoutExpired:
            raise Exception("Node.js command timed out - check Node.js installation")
        except FileNotFoundError:
            raise Exception("Node.js not found in PATH")

    def _test_mcp_server(self, server_path: str, server_name: str):
        """Test MCP server execution."""
        try:
            logger.info(f"Testing {server_name} MCP server execution...")
            result = subprocess.run(
                ["node", server_path], 
                input="", 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            logger.info(f"{server_name} MCP server execution test completed")
        except subprocess.TimeoutExpired:
            logger.info(f"{server_name} MCP server is responsive (timeout expected for stdio server)")
        except Exception as e:
            logger.warning(f"{server_name} MCP server test had issues: {e}")

    def _test_perplexity_docker(self):
        """Test Perplexity Docker MCP server."""
        try:
            logger.info("Testing Perplexity Docker MCP server...")
            result = subprocess.run([
                "docker", "run", "--rm", 
                "-e", f"PERPLEXITY_API_KEY={self.perplexity_api_key}",
                "mcp/perplexity-ask", "--help"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 or "perplexity" in result.stdout.lower():
                logger.info("✅ Perplexity Docker MCP server is functional")
            else:
                logger.warning(f"⚠️ Perplexity Docker test had issues: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            logger.info("⚠️ Perplexity Docker test timed out (may be normal)")
        except Exception as e:
            logger.warning(f"⚠️ Perplexity Docker test had issues: {e}")

    @contextmanager
    def get_mcp_connections(self):
        """Context manager for both MCP connections with proper cleanup."""
        sap_connection = None
        perplexity_connection = None
        sap_tools = []
        perplexity_tools = []
        
        with self._connection_lock:
            try:
                from mcp import stdio_client, StdioServerParameters
                from strands.tools.mcp import MCPClient
                
                logger.info("Creating MCP connections...")
                
                # Create SAP MCP connection
                if self.sap_mcp_server_path:
                    def create_sap_mcp_connection():
                        return stdio_client(
                            StdioServerParameters(
                                command="node",
                                args=[self.sap_mcp_server_path],
                                env={**os.environ}
                            )
                        )
                    
                    sap_mcp_client = MCPClient(create_sap_mcp_connection)
                    
                    # Test SAP connection
                    with sap_mcp_client as active_sap_client:
                        sap_tools_result = active_sap_client.list_tools_sync()
                        sap_tools = sap_tools_result if sap_tools_result else []
                        logger.info(f"✅ SAP MCP connection successful. Found {len(sap_tools)} tools.")
                    
                    sap_connection = sap_mcp_client
                
                # Create Perplexity MCP connection via Docker if available
                perplexity_mcp_client = None
                if self.perplexity_docker_available and self.perplexity_api_key:
                    def create_perplexity_mcp_connection():
                        return stdio_client(
                            StdioServerParameters(
                                command="docker",
                                args=[
                                    "run",
                                    "-i",
                                    "--rm",
                                    "-e",
                                    "PERPLEXITY_API_KEY",
                                    "mcp/perplexity-ask",
                                ],
                                env={"PERPLEXITY_API_KEY": self.perplexity_api_key},
                            )
                        )
                    perplexity_mcp_client = MCPClient(create_perplexity_mcp_connection)
                    
                    try:
                        with perplexity_mcp_client as active_perplexity_client:
                            perplexity_tools_result = active_perplexity_client.list_tools_sync()
                            perplexity_tools = perplexity_tools_result if perplexity_tools_result else []
                            logger.info(f"✅ Perplexity Docker MCP connection successful. Found {len(perplexity_tools)} tools.")
                    except Exception as e:
                        logger.warning(f"⚠️ Perplexity Docker MCP connection failed: {e}")
                        perplexity_mcp_client = None
                        perplexity_tools = []
                
                perplexity_connection = perplexity_mcp_client
                
                yield sap_connection, perplexity_connection, sap_tools, perplexity_tools
                
            except Exception as e:
                logger.error(f"Failed to establish MCP connections: {str(e)}")
                raise
            finally:
                logger.info("MCP connections cleanup completed")

    def _get_erp_exception_system_prompt(self) -> str:
        """Define the system prompt for ERP Exception Management analysis."""
        return """You are a specialized ERP Exception Management Expert with comprehensive knowledge of all business process exceptions.

Your responsibility is to perform comprehensive exception detection and analysis across all ERP modules and business processes, with research-backed insights from authoritative sources.

You have access to:

1. SAP SYSTEM DATA via ABAP ADT MCP tools:
   - Financial tables: BKPF, BSEG, FAGLFLEXA, SKA1, etc.
   - Procurement tables: EKKO, EKPO, EBAN, MARA, MAKT, etc.
   - Inventory tables: MCHB, MARD, MSEG, MKPF, etc.
   - Production tables: AFKO, AFPO, PLKO, CRHD, etc.
   - Sales tables: VBAK, VBAP, LIKP, LIPS, VBRK, etc.
   - HR tables: PA0001, PA0002, PA0008, etc.
   - System tables: TBTCO, SM37, etc.

2. WEB RESEARCH via Perplexity MCP tools:
   - Search SAP documentation for exception handling best practices
   - Research industry-specific exception management strategies
   - Find automated exception resolution techniques
   - Look up compliance requirements for exception handling

CRITICAL ERP EXCEPTION CATEGORIES TO DETECT:

🔴 FINANCIAL EXCEPTIONS:
1. Budget overruns and variance analysis
2. Unusual account balances and reconciliation issues
3. Unreconciled transactions and aging
4. Currency conversion discrepancies
5. Tax calculation errors and compliance issues

🟡 PROCUREMENT EXCEPTIONS:
1. Unapproved vendors and compliance violations
2. Exceeded budget limits and spending analysis
3. Missing required approvals and authorization
4. Expired contracts and renewal management
5. Price variance and market analysis

🟠 INVENTORY EXCEPTIONS:
1. Stock-outs and availability issues
2. Overstock situations and slow-moving inventory
3. Expired or soon-to-expire items
4. Inventory count discrepancies
5. Negative stock and system errors

🔵 ORDER FULFILLMENT EXCEPTIONS:
1. Insufficient inventory for orders
2. Partial shipments and backorders
3. Delivery delays and customer impact
4. Overselling situations (e-commerce integration)
5. Customer credit limit exceeded

🟢 PRODUCTION EXCEPTIONS:
1. Material shortages and supply chain issues
2. Quality control failures and rework
3. Machine breakdowns and capacity constraints
4. Capacity constraints and resource allocation
5. Production delays and schedule conflicts

🟣 INVOICE/PO/GOODS RECEIPT MATCHING EXCEPTIONS:
1. Price discrepancies and negotiation tracking
2. Quantity discrepancies and receiving errors
3. Unit of measure mismatches
4. Missing goods receipts and delivery confirmation
5. Missing purchase orders and authorization
6. Duplicate invoices and payment processing

REQUIRED OUTPUT FORMAT (JSON ONLY):

{
  "exception_analysis": {
    "analysis_timestamp": "ISO datetime",
    "system_analyzed": "System ID",
    "analysis_type": "Comprehensive ERP Exception Management Analysis",
    "research_sources_used": ["source1", "source2", ...]
  },
  "exceptions": [
    {
      "category": "FINANCIAL|PROCUREMENT|INVENTORY|ORDER_FULFILLMENT|PRODUCTION|INVOICE_MATCHING|HR|COMPLIANCE|LOGISTICS|CUSTOMER_MANAGEMENT|SYSTEM_DATA|QUALITY_MANAGEMENT|PROJECT_MANAGEMENT|MAINTENANCE",
      "exception_name": "Specific exception name",
      "exception_root_cause": "Technical and business explanation of the exception cause",
      "affected_entities": {
        "customers": ["customer1", "customer2"],
        "vendors": ["vendor1", "vendor2"],
        "materials": ["material1", "material2"],
        "orders": ["order1", "order2"],
        "documents": ["doc1", "doc2"]
      },
      "business_impact": {
        "severity": "HIGH|MEDIUM|LOW",
        "financial_impact": "Estimated cost or revenue impact",
        "operational_impact": "Description of operational disruption",
        "compliance_risk": "Regulatory or compliance implications"
      },
      "fix_insight": {
        "immediate_action": "What to do right now to resolve",
        "root_cause_fix": "Long-term solution to prevent recurrence",
        "preventive_measures": ["measure1", "measure2"],
        "automation_opportunities": "How to automate detection/resolution",
        "best_practice_reference": "Industry best practice or SAP recommendation"
      },
      "detection_details": {
        "detection_query": "SQL/ABAP query used to detect this exception",
        "frequency": "How often this exception occurs",
        "trend_analysis": "Is this increasing/decreasing over time",
        "related_exceptions": ["related_exception1", "related_exception2"]
      },
      "resolution_priority": "1-10 scale based on impact and urgency"
    }
  ],
  "research_insights": [
    {
      "source_type": "SAP_OFFICIAL|INDUSTRY_BEST_PRACTICE|ACADEMIC|VENDOR_SOLUTION",
      "source_url": "URL of reference",
      "insight_category": "AUTOMATION|PREVENTION|RESOLUTION|COMPLIANCE",
      "key_finding": "Main insight from research",
      "applicability": "How this applies to current exceptions"
    }
  ],
  "exception_summary": {
    "total_exceptions": 0,
    "high_severity_count": 0,
    "medium_severity_count": 0,
    "low_severity_count": 0,
    "exceptions_by_category": {
      "financial": 0,
      "procurement": 0,
      "inventory": 0,
      "order_fulfillment": 0,
      "production": 0,
      "invoice_matching": 0
    },
    "estimated_total_impact": "Financial estimate of all exceptions",
    "automation_opportunities": 0,
    "immediate_actions_required": 0,
    "key_recommendations": ["rec1", "rec2", "rec3"]
  }
}

RESEARCH STRATEGY:
1. For each exception category, research industry best practices
2. Find SAP-specific exception handling techniques
3. Look up automation and AI solutions for exception management
4. Research compliance requirements for exception documentation
5. Identify preventive measures and root cause analysis techniques

Focus on providing actionable, research-backed insights that can be immediately implemented by ERP administrators and business users."""

    def _ensure_reports_directory_exists(self):
        """Ensure the reports directory exists."""
        reports_dir = 'erp_exception_reports'
        if not os.path.exists(reports_dir):
            try:
                os.makedirs(reports_dir)
                logger.info(f"Created ERP Exception reports directory: {os.path.abspath(reports_dir)}")
            except Exception as e:
                logger.error(f"Failed to create ERP Exception reports directory: {str(e)}")

    def _get_report_file_path(self, system_id: str = "SAP_SYSTEM") -> str:
        """Construct the file path for the ERP Exception report."""
        import re
        
        # Sanitize system ID for file name
        sanitized_id = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', system_id)
        sanitized_id = sanitized_id.replace('..', '_')
        
        # Add timestamp to filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f'ERP_Exception_Analysis_{sanitized_id}_{timestamp}.json'
        
        file_path = os.path.join('erp_exception_reports', file_name)
        return file_path

    def _save_json_report(self, analysis_result: str, report_file_path: str) -> str:
        """Save the final JSON report with proper formatting and validation."""
        try:
            # Clean the analysis result
            json_content = str(analysis_result).strip()
            
            # Remove any markdown formatting or extra text that might be present
            if "```json" in json_content:
                json_start = json_content.find("```json") + 7
                json_end = json_content.rfind("```")
                if json_end > json_start:
                    json_content = json_content[json_start:json_end].strip()
            elif "```" in json_content:
                json_start = json_content.find("```") + 3
                json_end = json_content.rfind("```")
                if json_end > json_start:
                    json_content = json_content[json_start:json_end].strip()
            
            # Try to find JSON content if mixed with other text
            json_start_markers = ['{', '[']
            
            for start_marker in json_start_markers:
                if start_marker in json_content:
                    start_idx = json_content.find(start_marker)
                    if start_marker == '{':
                        end_marker = '}'
                    else:
                        end_marker = ']'
                    
                    end_idx = json_content.rfind(end_marker)
                    if end_idx > start_idx:
                        json_content = json_content[start_idx:end_idx + 1]
                        break
            
            # Try to parse and validate JSON
            try:
                parsed_json = json.loads(json_content)
                
                if not isinstance(parsed_json, dict):
                    raise ValueError("Root element must be a JSON object")
                
                # Add metadata if missing
                if "exception_analysis" not in parsed_json:
                    parsed_json["exception_analysis"] = {
                        "analysis_timestamp": datetime.now().isoformat(),
                        "system_analyzed": "SAP_SYSTEM",
                        "analysis_type": "Comprehensive ERP Exception Management Analysis",
                        "research_sources_used": []
                    }
                
                # Ensure required sections exist
                if "exceptions" not in parsed_json:
                    parsed_json["exceptions"] = []
                
                if "research_insights" not in parsed_json:
                    parsed_json["research_insights"] = []
                
                if "exception_summary" not in parsed_json:
                    exceptions = parsed_json.get("exceptions", [])
                    parsed_json["exception_summary"] = {
                        "total_exceptions": len(exceptions),
                        "high_severity_count": len([e for e in exceptions if e.get("business_impact", {}).get("severity") == "HIGH"]),
                        "medium_severity_count": len([e for e in exceptions if e.get("business_impact", {}).get("severity") == "MEDIUM"]),
                        "low_severity_count": len([e for e in exceptions if e.get("business_impact", {}).get("severity") == "LOW"]),
                        "exceptions_by_category": {
                            "financial": len([e for e in exceptions if e.get("category") == "FINANCIAL"]),
                            "procurement": len([e for e in exceptions if e.get("category") == "PROCUREMENT"]),
                            "inventory": len([e for e in exceptions if e.get("category") == "INVENTORY"]),
                            "order_fulfillment": len([e for e in exceptions if e.get("category") == "ORDER_FULFILLMENT"]),
                            "production": len([e for e in exceptions if e.get("category") == "PRODUCTION"]),
                            "invoice_matching": len([e for e in exceptions if e.get("category") == "INVOICE_MATCHING"])
                        },
                        "estimated_total_impact": "To be calculated based on individual impacts",
                        "automation_opportunities": len([e for e in exceptions if e.get("fix_insight", {}).get("automation_opportunities")]),
                        "immediate_actions_required": len([e for e in exceptions if e.get("business_impact", {}).get("severity") == "HIGH"]),
                        "key_recommendations": ["Implement automated exception monitoring", "Address high-severity exceptions first", "Establish preventive measures"]
                    }
                
                # Format and save the JSON
                formatted_json = json.dumps(parsed_json, indent=2, ensure_ascii=False, sort_keys=True)
                
                with open(report_file_path, 'w', encoding='utf-8') as f:
                    f.write(formatted_json)
                
                logger.info(f"✅ ERP Exception Analysis JSON report successfully saved: {report_file_path}")
                
                return report_file_path
                
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"❌ JSON parsing failed: {e}")
                
                # Create a fallback structured JSON report
                fallback_report = {
                    "exception_analysis": {
                        "analysis_timestamp": datetime.now().isoformat(),
                        "system_analyzed": "SAP_SYSTEM",
                        "analysis_type": "Comprehensive ERP Exception Management Analysis - PARSING_ERROR",
                        "error": f"JSON parsing failed: {str(e)}",
                        "research_sources_used": []
                    },
                    "exceptions": [],
                    "research_insights": [],
                    "exception_summary": {
                        "total_exceptions": 0,
                        "high_severity_count": 0,
                        "medium_severity_count": 0,
                        "low_severity_count": 0,
                        "exceptions_by_category": {
                            "financial": 0,
                            "procurement": 0,
                            "inventory": 0,
                            "order_fulfillment": 0,
                            "production": 0,
                            "invoice_matching": 0
                        },
                        "estimated_total_impact": "Analysis incomplete due to parsing error",
                        "automation_opportunities": 0,
                        "immediate_actions_required": 1,
                        "key_recommendations": ["Fix JSON parsing issue", "Retry exception analysis", "Review system configuration"]
                    },
                    "raw_response": json_content[:2000]
                }
                
                formatted_fallback = json.dumps(fallback_report, indent=2, ensure_ascii=False)
                
                with open(report_file_path, 'w', encoding='utf-8') as f:
                    f.write(formatted_fallback)
                
                raw_file_path = report_file_path.replace('.json', '_raw_response.txt')
                with open(raw_file_path, 'w', encoding='utf-8') as f:
                    f.write(json_content)
                
                logger.info(f"⚠️ Fallback JSON report saved: {report_file_path}")
                
                return report_file_path
                
        except Exception as e:
            logger.error(f"❌ Failed to save JSON report: {e}")
            
            error_report = {
                "exception_analysis": {
                    "analysis_timestamp": datetime.now().isoformat(),
                    "system_analyzed": "SAP_SYSTEM",
                    "analysis_type": "Comprehensive ERP Exception Management Analysis - CRITICAL_ERROR",
                    "error": str(e)
                },
                "status": "FAILED",
                "error_details": f"Critical error in report generation: {str(e)}",
                "recommendation": "Check system configuration and retry analysis"
            }
            
            try:
                with open(report_file_path, 'w', encoding='utf-8') as f:
                    json.dump(error_report, f, indent=2)
                return report_file_path
            except:
                return f"❌ Complete failure to save report: {str(e)}"

    async def perform_comprehensive_exception_analysis(self, system_details: str = "", execution_id: str = None) -> Dict[str, Any]:
        """Perform comprehensive ERP exception analysis with web research."""
        try:
            logger.info("Starting comprehensive ERP Exception Management analysis...")
            
            self._ensure_reports_directory_exists()
            
            with self.get_mcp_connections() as (sap_client, perplexity_client, sap_tools, perplexity_tools):
                # Configure Bedrock with extended timeouts
                bedrock_model = BedrockModel(
                    model_id="us.anthropic.claude-sonnet-4-20250514-v1:0",
                    client_config={
                        'read_timeout': 300,
                        'connect_timeout': 60,
                        'retries': {
                            'max_attempts': 2,
                            'mode': 'adaptive'
                        }
                    }
                )
                
                # Combine all available tools
                all_tools = [current_time] + sap_tools
                if perplexity_tools:
                    all_tools.extend(perplexity_tools)
                
                erp_exception_agent = Agent(
                    model=bedrock_model,
                    tools=all_tools,
                    system_prompt=self._get_erp_exception_system_prompt()
                )
                
                # Phase 1: Extract comprehensive ERP data
                logger.info("Phase 1: Extracting comprehensive ERP data...")
                data_extraction_prompt = """
                Extract comprehensive exception-relevant data from all ERP modules:
                
                1. FINANCIAL EXCEPTIONS DATA:
                   - Query BKPF/BSEG for unreconciled transactions and aging analysis
                   - Check FAGLFLEXA for unusual account balances and variances
                   - Analyze SKA1 for GL account setup issues
                   - Look for budget vs actual variances in financial reports
                   - Check for currency conversion discrepancies
                
                2. PROCUREMENT EXCEPTIONS DATA:
                   - Query EKKO/EKPO for purchase orders with issues
                   - Check EBAN for purchase requisitions requiring attention
                   - Analyze LFB1/LFA1 for vendor master data issues
                   - Look for exceeded budget limits and unauthorized spending
                   - Check for expired contracts and missing approvals
                
                3. INVENTORY EXCEPTIONS DATA:
                   - Query MCHB/MARD for stock levels and availability issues
                   - Check MSEG/MKPF for inventory movement discrepancies
                   - Analyze slow-moving and obsolete inventory
                   - Look for negative stock situations
                   - Check for expired or soon-to-expire materials
                
                4. ORDER FULFILLMENT EXCEPTIONS DATA:
                   - Query VBAK/VBAP for sales order issues
                   - Check LIKP/LIPS for delivery problems
                   - Analyze customer credit limit situations
                   - Look for backorders and partial shipments
                   - Check for overselling situations
                
                5. PRODUCTION EXCEPTIONS DATA:
                   - Query AFKO/AFPO for production order issues
                   - Check PLKO for BOM and routing problems
                   - Analyze material shortages affecting production
                   - Look for capacity constraints and bottlenecks
                   - Check for quality control failures
                
                6. INVOICE/PO/GR MATCHING EXCEPTIONS:
                   - Three-way matching discrepancies (PO vs GR vs Invoice)
                   - Price variances and quantity discrepancies
                   - Missing documents in the process flow
                   - Duplicate invoices and payment issues
                
                Provide detailed technical data with specific examples and counts. Keep response focused on actionable data.
                """
                
                # Phase 2: Research exception management best practices
                research_data = ""
                if perplexity_client:
                    logger.info("Phase 2: Researching exception management best practices...")
                    research_prompt = """
                    Research comprehensive ERP exception management information:
                    
                    1. SAP EXCEPTION HANDLING BEST PRACTICES:
                       - Search for "SAP exception management automation"
                       - Find SAP standard exception handling procedures
                       - Look for SAP Notes on common ERP exceptions
                       - Research SAP Fiori apps for exception management
                    
                    2. INDUSTRY BEST PRACTICES:
                       - Research automated exception detection and resolution
                       - Find AI and ML approaches to exception management
                       - Look for exception handling in different industries
                       - Research preventive measures and root cause analysis
                    
                    3. COMPLIANCE AND GOVERNANCE:
                       - Research exception documentation requirements
                       - Find audit trail and compliance considerations
                       - Look for regulatory requirements for exception handling
                       - Research exception escalation procedures
                    
                    4. AUTOMATION AND TECHNOLOGY:
                       - Research RPA solutions for exception handling
                       - Find AI-powered exception resolution techniques
                       - Look for exception management platforms and tools
                       - Research integration patterns for exception workflows
                    
                    Focus on actionable insights that can guide technical implementation.
                    Include specific tools, techniques, and methodologies.
                    """
                
                # Execute phases
                with sap_client, perplexity_client if perplexity_client else sap_client:
                    try:
                        # Extract ERP data
                        erp_data = erp_exception_agent(data_extraction_prompt)
                        logger.info("Phase 1 completed - ERP data extracted")
                        
                        # Research best practices if available
                        if perplexity_client:
                            try:
                                research_data = erp_exception_agent(research_prompt)
                                logger.info("Phase 2 completed - Research data gathered")
                            except Exception as e:
                                logger.warning(f"Research phase failed: {e}")
                                research_data = "Research data unavailable due to connection issues"
                        
                        # Phase 3: Comprehensive exception analysis
                        logger.info("Phase 3: Performing comprehensive exception analysis...")
                        analysis_prompt = f"""
                        Based on the extracted ERP data and research insights, perform comprehensive exception analysis:
                        
                        ERP SYSTEM DATA:
                        {str(erp_data)[:4000]}
                        
                        RESEARCH INSIGHTS:
                        {str(research_data)[:3000]}
                        
                        ANALYSIS REQUIREMENTS:
                        1. Identify ALL types of exceptions across ALL business processes
                        2. For each exception, provide:
                           - Specific affected entities (customers, vendors, materials, orders, documents)
                           - Detailed business impact assessment with severity rating
                           - Root cause analysis with technical details
                           - Comprehensive fix insights including immediate actions and long-term solutions
                           - Automation opportunities and preventive measures
                           - Priority scoring based on business impact and urgency
                        
                        3. Research-backed insights:
                           - Reference industry best practices where found
                           - Include automation and AI solution recommendations
                           - Provide compliance and governance considerations
                           - Suggest technology platforms and integration approaches
                        
                        4. Executive summary with:
                           - Total exception counts by severity and category
                           - Financial impact estimation where possible
                           - Priority recommendations for immediate action
                           - Automation opportunities assessment
                        
                        OUTPUT MUST BE VALID JSON following the exact structure defined in the system prompt.
                        Do not include any text outside the JSON structure.
                        Ensure all JSON is properly formatted and escaped.
                        Focus on real, actionable exceptions that require business attention.
                        """
                        
                        final_analysis = erp_exception_agent(analysis_prompt)
                        
                        # Save the JSON report
                        report_file_path = self._get_report_file_path()
                        
                        # Process and save the final JSON report
                        saved_report_path = self._save_json_report(final_analysis, report_file_path)
                        
                        # Return structured response
                        return {
                            "status": "completed",
                            "report_path": saved_report_path,
                            "analysis_timestamp": datetime.now().isoformat(),
                            "system_analyzed": system_details or "SAP_SYSTEM",
                            "mcp_connections": {
                                "sap_tools_count": len(sap_tools),
                                "perplexity_tools_count": len(perplexity_tools),
                                "research_available": perplexity_client is not None
                            }
                        }
                        
                    except Exception as e:
                        logger.error(f"Analysis phase failed: {e}")
                        return {
                            "status": "failed",
                            "error": str(e),
                            "analysis_timestamp": datetime.now().isoformat(),
                            "recommendation": "Check MCP connections and retry analysis"
                        }
                
        except Exception as e:
            error_message = f"Complete ERP exception analysis failure: {str(e)}"
            logger.error(error_message)
            return {
                "status": "failed",
                "error": error_message,
                "analysis_timestamp": datetime.now().isoformat()
            }

    def get_service_status(self) -> Dict[str, Any]:
        """Get the current status of the ERP Exception Management Service."""
        return {
            "service_name": "ERP Exception Management Service",
            "status": "active",
            "sap_mcp_server": {
                "available": self.sap_mcp_server_path is not None,
                "path": self.sap_mcp_server_path
            },
            "perplexity_docker": {
                "available": self.perplexity_docker_available,
                "api_key_configured": bool(self.perplexity_api_key)
            },
            "capabilities": [
                "Financial Exception Analysis",
                "Procurement Exception Management",
                "Inventory Exception Detection",
                "Order Fulfillment Exception Handling",
                "Production Exception Analysis",
                "Invoice Matching Exception Detection",
                "Research-backed Insights",
                "Automation Recommendations"
            ]
        }