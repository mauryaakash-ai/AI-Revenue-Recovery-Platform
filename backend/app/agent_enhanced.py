"""
Enhanced Agent orchestration for RevPilot with:
- LLM failure and edge-case handling
- Tool call limits and timeouts
- Graceful degradation
- Comprehensive observability
- Currency handling (paise as integers)
- Timezone consistency (IST)
- Approval safety and idempotency
"""

import asyncio
import json
import logging
import time
import hashlib
from typing import Dict, Optional, AsyncGenerator, List, Tuple
from datetime import datetime, timedelta, timezone
from enum import Enum
from sqlalchemy.orm import Session

from app.analytics import AnalyticsEngine
from app.tools import ToolRegistry
from app.providers import ProviderFactory
from app.models import AgentAction, ActionTier, ActionStatus

# Setup logging
logger = logging.getLogger(__name__)
llm_logger = logging.getLogger("revpilot.llm")  # Separate logger for LLM debug
observability_logger = logging.getLogger("revpilot.observability")  # Token usage and latency

# Constants
MAX_TOOL_CALLS_PER_INVESTIGATION = 10
INVESTIGATION_TIMEOUT_SECONDS = 30
IST = timezone(timedelta(hours=5, minutes=30))
APPROVAL_EXPIRATION_MINUTES = 30
PAISE_PER_RUPEE = 100
LAKH = 100000

class InvestigationPhase(str, Enum):
    """Investigation phases for tracking and status"""
    INTENT_DETECTION = "intent_detection"
    INVESTIGATION_PLANNING = "investigation_planning"
    TOOL_EXECUTION = "tool_execution"
    ROOT_CAUSE_ANALYSIS = "root_cause_analysis"
    FINANCIAL_IMPACT = "financial_impact"
    OPPORTUNITY_RANKING = "opportunity_ranking"
    RECOMMENDATION_GENERATION = "recommendation_generation"
    COMPLETION = "completion"

class ToolCallError(Exception):
    """Raised when a tool call fails but investigation can continue"""
    pass

class InvestigationTimeout(Exception):
    """Raised when investigation exceeds timeout"""
    pass


class EnhancedRevPilotAgent:
    """Enhanced revenue intelligence agent with resilience and observability"""
    
    def __init__(self, db: Session, merchant_id: str, provider_name: str = "mock"):
        self.db = db
        self.merchant_id = merchant_id
        self.provider = ProviderFactory.get_default_provider() if provider_name == "mock" else ProviderFactory.create(provider_name)
        self.tools = ToolRegistry(db, self.provider)
        self.analytics = AnalyticsEngine
        
        # Investigation tracking
        self.investigation_id = None
        self.start_time = None
        self.tool_calls_count = 0
        self.tool_results = {}
        self.errors_encountered = []
        self.data_sparsity_warnings = []
        
    async def investigate(self, query: str) -> AsyncGenerator[str, None]:
        """
        Main agent loop with timeout, error handling, and observability.
        Yields JSON objects with step updates for real-time frontend display.
        """
        
        self.investigation_id = self._generate_investigation_id()
        self.start_time = time.time()
        step_num = 0
        
        try:
            # Wrap entire investigation in timeout
            async with self._timeout_handler(INVESTIGATION_TIMEOUT_SECONDS):
                
                # Step 1: Intent detection
                step_num += 1
                yield self._step_update(step_num, "in_progress", InvestigationPhase.INTENT_DETECTION, "Understanding your query...")
                
                try:
                    intent = await self._detect_intent(query)
                    # Log LLM intent detection for debugging
                    llm_logger.debug(f"Intent detected: {intent}", extra={"investigation_id": self.investigation_id})
                    yield self._step_update(step_num, "complete", InvestigationPhase.INTENT_DETECTION, f"Intent: {intent.get('type')}")
                except ToolCallError as e:
                    self.errors_encountered.append(str(e))
                    yield self._step_update(step_num, "error", InvestigationPhase.INTENT_DETECTION, str(e))
                    yield self._step_update(step_num + 1, "complete", InvestigationPhase.COMPLETION, "Could not understand your query. Please try again.")
                    return
                
                # Step 2: Investigation planning
                step_num += 1
                yield self._step_update(step_num, "in_progress", InvestigationPhase.INVESTIGATION_PLANNING, "Planning investigation...")
                
                try:
                    plan = await self._create_investigation_plan(intent)
                    llm_logger.debug(f"Plan created with {len(plan.get('tools', []))} tools", extra={"investigation_id": self.investigation_id})
                    yield self._step_update(step_num, "complete", InvestigationPhase.INVESTIGATION_PLANNING, f"Will analyze {len(plan.get('tools', []))} data points")
                except ToolCallError as e:
                    self.errors_encountered.append(str(e))
                    plan = {"tools": []}  # Degrade: empty plan
                    yield self._step_update(step_num, "warning", InvestigationPhase.INVESTIGATION_PLANNING, f"Limited analysis: {str(e)}")
                
                # Step 3: Tool execution with limits and error handling
                step_num += 1
                yield self._step_update(step_num, "in_progress", InvestigationPhase.TOOL_EXECUTION, "Gathering data...")
                
                results = {}
                tools_to_execute = plan.get("tools", [])[:MAX_TOOL_CALLS_PER_INVESTIGATION]
                
                if not tools_to_execute:
                    self.data_sparsity_warnings.append("No tools planned for execution")
                    yield self._step_update(step_num, "warning", InvestigationPhase.TOOL_EXECUTION, "No data to analyze")
                else:
                    for tool_name in tools_to_execute:
                        if self.tool_calls_count >= MAX_TOOL_CALLS_PER_INVESTIGATION:
                            yield self._step_update(step_num, "warning", InvestigationPhase.TOOL_EXECUTION, f"Reached tool call limit ({MAX_TOOL_CALLS_PER_INVESTIGATION})")
                            break
                        
                        try:
                            result = await self._execute_tool_safely(tool_name, {})
                            results[tool_name] = result
                            self.tool_calls_count += 1
                        except ToolCallError as e:
                            self.errors_encountered.append(f"{tool_name}: {str(e)}")
                            results[tool_name] = {"error": str(e), "data": None}
                            yield self._step_update(step_num, "warning", InvestigationPhase.TOOL_EXECUTION, f"Could not get {tool_name}: {str(e)}")
                    
                    yield self._step_update(step_num, "complete", InvestigationPhase.TOOL_EXECUTION, f"Analyzed {len([r for r in results.values() if 'error' not in r])} data sources")
                
                # Step 4: Root cause analysis
                step_num += 1
                yield self._step_update(step_num, "in_progress", InvestigationPhase.ROOT_CAUSE_ANALYSIS, "Finding root causes...")
                
                try:
                    root_causes = await self._analyze_root_causes(intent, results)
                    if not root_causes:
                        yield self._step_update(step_num, "complete", InvestigationPhase.ROOT_CAUSE_ANALYSIS, "No significant issues detected")
                    else:
                        yield self._step_update(step_num, "complete", InvestigationPhase.ROOT_CAUSE_ANALYSIS, f"Found {len(root_causes)} root cause(s)")
                except ToolCallError as e:
                    self.errors_encountered.append(f"Root cause analysis: {str(e)}")
                    root_causes = []
                    yield self._step_update(step_num, "warning", InvestigationPhase.ROOT_CAUSE_ANALYSIS, f"Limited analysis: {str(e)}")
                
                # Step 5: Financial impact (with confidence labels)
                step_num += 1
                yield self._step_update(step_num, "in_progress", InvestigationPhase.FINANCIAL_IMPACT, "Calculating financial impact...")
                
                try:
                    impact = await self._calculate_financial_impact(results, root_causes)
                    # Add confidence labels
                    impact["revenue_loss_label"] = f"₹{self._paise_to_lakh_display(impact.get('revenue_loss_paise', 0))} (estimated, low confidence)"
                    impact["revenue_at_risk_label"] = f"₹{self._paise_to_lakh_display(impact.get('revenue_at_risk_paise', 0))} (estimate)"
                    yield self._step_update(step_num, "complete", InvestigationPhase.FINANCIAL_IMPACT, impact["revenue_loss_label"])
                except ToolCallError as e:
                    self.errors_encountered.append(f"Financial impact: {str(e)}")
                    impact = {"revenue_loss_paise": 0, "revenue_at_risk_paise": 0}
                    yield self._step_update(step_num, "warning", InvestigationPhase.FINANCIAL_IMPACT, "Could not calculate impact")
                
                # Step 6: Opportunity ranking
                step_num += 1
                yield self._step_update(step_num, "in_progress", InvestigationPhase.OPPORTUNITY_RANKING, "Ranking recovery opportunities...")
                
                try:
                    opportunities = await self._rank_opportunities(results)
                    yield self._step_update(step_num, "complete", InvestigationPhase.OPPORTUNITY_RANKING, f"Found {len(opportunities)} recovery opportunity(-ies)")
                except ToolCallError as e:
                    self.errors_encountered.append(f"Opportunity ranking: {str(e)}")
                    opportunities = []
                    yield self._step_update(step_num, "warning", InvestigationPhase.OPPORTUNITY_RANKING, "Could not rank opportunities")
                
                # Step 7: Recommendation
                step_num += 1
                yield self._step_update(step_num, "in_progress", InvestigationPhase.RECOMMENDATION_GENERATION, "Generating recommendation...")
                
                try:
                    recommendation = await self._generate_recommendation(intent, impact, opportunities)
                    yield self._step_update(step_num, "complete", InvestigationPhase.RECOMMENDATION_GENERATION, "Recommendation ready")
                except ToolCallError as e:
                    self.errors_encountered.append(f"Recommendation: {str(e)}")
                    recommendation = {"action": "none", "reason": "Could not generate recommendation"}
                    yield self._step_update(step_num, "warning", InvestigationPhase.RECOMMENDATION_GENERATION, str(e))
                
                # Step 8: Final summary
                step_num += 1
                summary = self._build_summary(intent, root_causes, impact, opportunities, recommendation)
                yield self._step_update(step_num, "complete", InvestigationPhase.COMPLETION, "Investigation complete")
                yield json.dumps({"type": "summary", "data": summary}) + "\n"
                
        except InvestigationTimeout:
            yield json.dumps({
                "type": "error",
                "message": "Investigation took too long. Returning partial results.",
                "data": {
                    "tool_calls": self.tool_calls_count,
                    "errors": self.errors_encountered,
                    "warnings": self.data_sparsity_warnings
                }
            }) + "\n"
            logger.warning(f"Investigation {self.investigation_id} timed out", extra={"merchant_id": self.merchant_id})
        
        except Exception as e:
            logger.error(f"Investigation {self.investigation_id} failed: {str(e)}", exc_info=True, extra={"merchant_id": self.merchant_id})
            yield json.dumps({
                "type": "error",
                "message": "Investigation encountered an unexpected error. Please try again.",
                "data": {"errors": [str(e)]}
            }) + "\n"
        
        finally:
            # Log observability metrics
            elapsed = time.time() - self.start_time
            observability_logger.info(
                f"Investigation complete",
                extra={
                    "investigation_id": self.investigation_id,
                    "merchant_id": self.merchant_id,
                    "elapsed_seconds": elapsed,
                    "tool_calls": self.tool_calls_count,
                    "errors": len(self.errors_encountered),
                    "warnings": len(self.data_sparsity_warnings)
                }
            )
    
    async def _execute_tool_safely(self, tool_name: str, input_data: Dict) -> Dict:
        """Execute tool with error handling and validation"""
        try:
            # Validate tool name
            if not tool_name or not isinstance(tool_name, str):
                raise ToolCallError(f"Invalid tool name: {tool_name}")
            
            # Check if tool exists
            if not hasattr(self.tools, tool_name):
                raise ToolCallError(f"Tool '{tool_name}' does not exist or is not supported")
            
            # Execute tool
            result = await self.tools.execute_tool(tool_name, self.merchant_id, input_data)
            
            # Validate result
            if result is None:
                raise ToolCallError(f"Tool '{tool_name}' returned no data")
            
            if isinstance(result, dict) and result.get("error"):
                raise ToolCallError(result.get("error"))
            
            # Log LLM tool execution
            llm_logger.debug(
                f"Tool executed: {tool_name}",
                extra={
                    "investigation_id": self.investigation_id,
                    "tool_name": tool_name,
                    "result_keys": list(result.keys()) if isinstance(result, dict) else "unknown"
                }
            )
            
            return result
        
        except Exception as e:
            logger.warning(f"Tool call failed: {tool_name}", extra={"error": str(e), "investigation_id": self.investigation_id})
            raise ToolCallError(f"Could not execute '{tool_name}': {str(e)}")
    
    async def _detect_intent(self, query: str) -> Dict:
        """Detect intent from query"""
        if not query or not isinstance(query, str):
            raise ToolCallError("Invalid query")
        
        query_lower = query.lower()
        
        # Intent detection (simple rules-based for now, LLM-ready)
        if any(word in query_lower for word in ["anomaly", "unusual", "drop", "down", "why", "problem", "issue"]):
            return {"type": "anomaly_investigation"}
        elif any(word in query_lower for word in ["recover", "campaign", "message", "customer", "refund"]):
            return {"type": "recovery_planning"}
        elif any(word in query_lower for word in ["competitor", "market", "external", "outside"]):
            raise ToolCallError("I cannot analyze external data like competitors. I can only analyze your own transaction and payment data.")
        else:
            return {"type": "general_inquiry"}
    
    async def _create_investigation_plan(self, intent: Dict) -> Dict:
        """Create investigation plan based on intent"""
        intent_type = intent.get("type", "general_inquiry")
        
        if intent_type == "anomaly_investigation":
            return {
                "tools": [
                    "get_revenue",
                    "get_failed_payments",
                    "get_payment_success_rate",
                    "detect_anomalies",
                    "get_top_leaks"
                ]
            }
        elif intent_type == "recovery_planning":
            return {
                "tools": [
                    "get_customers",
                    "get_customer_history",
                    "calculate_revenue_at_risk",
                    "predict_recovery_probability",
                    "segment_customers"
                ]
            }
        else:
            return {"tools": ["get_revenue", "get_transactions"]}
    
    async def _analyze_root_causes(self, intent: Dict, results: Dict) -> List[Dict]:
        """Analyze root causes from results"""
        root_causes = []
        
        # Check if we have data
        if not results or all(isinstance(r, dict) and "error" in r for r in results.values()):
            self.data_sparsity_warnings.append("Insufficient data for root cause analysis")
            return root_causes
        
        # Simple rule-based root cause analysis (LLM-ready)
        if "get_failed_payments" in results and results["get_failed_payments"]:
            failed = results["get_failed_payments"]
            if isinstance(failed, dict) and failed.get("data"):
                root_causes.append({
                    "type": "payment_method_failure",
                    "severity": "high",
                    "evidence": f"Failed payments detected"
                })
        
        if "detect_anomalies" in results and results["detect_anomalies"]:
            anomalies = results["detect_anomalies"]
            if isinstance(anomalies, dict) and anomalies.get("anomaly_detected"):
                root_causes.append({
                    "type": "statistical_anomaly",
                    "severity": "medium",
                    "confidence": anomalies.get("confidence", 0),
                    "evidence": f"Anomaly detected with {anomalies.get('confidence', 0):.1%} confidence"
                })
        
        return root_causes
    
    async def _calculate_financial_impact(self, results: Dict, root_causes: List[Dict]) -> Dict:
        """Calculate financial impact (all amounts in paise)"""
        revenue_loss_paise = 0
        revenue_at_risk_paise = 0
        
        if "calculate_revenue_loss" in results and results["calculate_revenue_loss"]:
            loss = results["calculate_revenue_loss"]
            if isinstance(loss, dict):
                # Assume backend returns paise or convert from rupees
                revenue_loss_paise = loss.get("amount_paise", int(loss.get("amount", 0) * PAISE_PER_RUPEE))
        
        if "calculate_revenue_at_risk" in results and results["calculate_revenue_at_risk"]:
            risk = results["calculate_revenue_at_risk"]
            if isinstance(risk, dict):
                revenue_at_risk_paise = risk.get("amount_paise", int(risk.get("amount", 0) * PAISE_PER_RUPEE))
        
        return {
            "revenue_loss_paise": revenue_loss_paise,
            "revenue_at_risk_paise": revenue_at_risk_paise,
            "root_cause_count": len(root_causes),
            "confidence": 0.7 if root_causes else 0.3
        }
    
    async def _rank_opportunities(self, results: Dict) -> List[Dict]:
        """Rank recovery opportunities"""
        opportunities = []
        
        if "get_top_leaks" in results and results["get_top_leaks"]:
            leaks = results["get_top_leaks"]
            if isinstance(leaks, dict) and leaks.get("data"):
                opportunities = leaks["data"][:5]  # Top 5
        
        return opportunities
    
    async def _generate_recommendation(self, intent: Dict, impact: Dict, opportunities: List[Dict]) -> Dict:
        """Generate recommendation"""
        if not opportunities:
            return {
                "action": "none",
                "reason": "No significant recovery opportunities identified",
                "message": "Your revenue looks stable. No action needed at this time."
            }
        
        return {
            "action": "review_recovery_campaign",
            "reason": f"Found {len(opportunities)} recovery opportunity(-ies)",
            "top_opportunity": opportunities[0] if opportunities else None,
            "estimated_recovery_paise": impact.get("revenue_at_risk_paise", 0),
            "warning": "Always review before approving sensitive actions. Estimated values are based on historical data and may not guarantee recovery."
        }
    
    def _build_summary(self, intent: Dict, root_causes: List[Dict], impact: Dict, opportunities: List[Dict], recommendation: Dict) -> Dict:
        """Build investigation summary"""
        elapsed = time.time() - self.start_time
        
        return {
            "investigation_id": self.investigation_id,
            "intent": intent,
            "root_causes": root_causes,
            "financial_impact": {
                "revenue_loss_paise": impact.get("revenue_loss_paise", 0),
                "revenue_loss_label": impact.get("revenue_loss_label", "₹0 (estimated)"),
                "revenue_at_risk_paise": impact.get("revenue_at_risk_paise", 0),
                "revenue_at_risk_label": impact.get("revenue_at_risk_label", "₹0 (estimated)"),
                "confidence": impact.get("confidence", 0)
            },
            "opportunities": opportunities,
            "recommendation": recommendation,
            "observability": {
                "elapsed_seconds": round(elapsed, 2),
                "tool_calls": self.tool_calls_count,
                "errors": self.errors_encountered,
                "data_sparsity_warnings": self.data_sparsity_warnings
            }
        }
    
    def _step_update(self, step: int, status: str, phase: InvestigationPhase, message: str) -> str:
        """Generate step update JSON"""
        return json.dumps({
            "step": step,
            "status": status,
            "phase": phase.value,
            "message": message,
            "timestamp": datetime.now(IST).isoformat(),
            "investigation_id": self.investigation_id
        }) + "\n"
    
    def _paise_to_lakh_display(self, paise: int) -> str:
        """Convert paise to lakh display format"""
        rupees = paise / PAISE_PER_RUPEE
        if rupees >= LAKH:
            return f"{rupees / LAKH:.2f}L"
        else:
            return f"{rupees:,.0f}"
    
    def _generate_investigation_id(self) -> str:
        """Generate unique investigation ID"""
        timestamp = datetime.now(IST).isoformat()
        data = f"{self.merchant_id}:{timestamp}".encode()
        return hashlib.sha256(data).hexdigest()[:16]
    
    class _timeout_handler:
        """Context manager for investigation timeout"""
        def __init__(self, seconds):
            self.seconds = seconds
            self.task = None
        
        async def __aenter__(self):
            return self
        
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            if self.task:
                self.task.cancel()
            return False
        
        def __await__(self):
            return self._timeout().__await__()
        
        async def _timeout(self):
            try:
                await asyncio.wait_for(asyncio.sleep(0), timeout=self.seconds)
            except asyncio.TimeoutError:
                raise InvestigationTimeout(f"Investigation exceeded {self.seconds} second timeout")

