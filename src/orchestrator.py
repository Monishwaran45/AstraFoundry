"""Orchestrator - Central controller for the multi-agent pipeline"""

import uuid
import time
from typing import Dict, Any, Optional, List
from datetime import datetime

from src.models import BlueprintOutput
from src.memory.session_service import get_session_service
from src.memory.memory_bank import get_memory_bank
from src.utils.logger import get_logger
from src.utils.metrics import MetricsCollector, get_metrics_store
from src.utils.config import get_config

# Import all agents
from src.agents.idea_agent import IdeaAgent
from src.agents.research_agent import ResearchAgent
from src.agents.product_agent import ProductDesignerAgent
from src.agents.roadmap_agent import RoadmapAgent
from src.agents.finance_agent import FinanceAgent
from src.agents.pitch_agent import PitchDeckAgent

# Import tools
from src.tools.google_search_adapter import GoogleSearchAdapter
from src.tools.code_execution_adapter import CodeExecutionAdapter
from src.tools.mcp_tool_adapter import MCPToolAdapter


class Orchestrator:
    """Central controller that manages the entire pipeline execution"""
    
    def __init__(self):
        from src.utils.logger import AgentLogger
        self.logger = AgentLogger("Orchestrator")
        self.config = get_config()
        self.session_service = get_session_service()
        self.memory_bank = get_memory_bank()
        self.metrics_store = get_metrics_store()
        
        # Initialize tools
        self.search_tool = GoogleSearchAdapter(
            api_key=self.config.google_search_api_key,
            engine_id=self.config.google_search_engine_id
        )
        self.code_executor = CodeExecutionAdapter()
        self.mcp_tool = MCPToolAdapter()
        
        # Initialize agents
        self.agents = {
            'idea_agent': IdeaAgent(self.search_tool),
            'research_agent': ResearchAgent(self.search_tool),
            'product_agent': ProductDesignerAgent(),
            'roadmap_agent': RoadmapAgent(self.mcp_tool),
            'finance_agent': FinanceAgent(self.code_executor),
            'pitch_agent': PitchDeckAgent()
        }
    
    def execute_pipeline(
        self,
        user_prompt: str,
        user_id: str = "default_user",
        timeout_seconds: Optional[int] = None
    ) -> BlueprintOutput:
        """
        Execute the complete multi-agent pipeline
        
        Args:
            user_prompt: User's startup domain prompt
            user_id: User identifier for memory personalization
            timeout_seconds: Optional timeout override
        
        Returns:
            BlueprintOutput with complete startup blueprint
        """
        run_id = str(uuid.uuid4())
        timeout = timeout_seconds or self.config.timeout_seconds
        start_time = time.time()
        
        self.logger.info(f"Starting pipeline execution: {run_id}")
        self.logger.info(f"User prompt: {user_prompt}")
        
        # Initialize session and metrics
        session = self.initialize_session(user_id)
        metrics = MetricsCollector(run_id)
        
        try:
            # Build context
            context = {
                'user_prompt': user_prompt,
                'user_id': user_id,
                'run_id': run_id,
                'agent_outputs': {}
            }
            
            # Load user preferences if memory enabled
            if self.config.enable_memory:
                context['user_preferences'] = self.memory_bank.get_preferences(user_id)
            
            # Execute agents sequentially
            agent_sequence = [
                'idea_agent',
                'research_agent',
                'product_agent',
                'roadmap_agent',
                'finance_agent',
                'pitch_agent'
            ]
            
            for agent_name in agent_sequence:
                # Check timeout
                elapsed = time.time() - start_time
                if elapsed > timeout:
                    raise TimeoutError(f"Pipeline exceeded timeout of {timeout} seconds")
                
                # Execute agent
                try:
                    agent_output = self._execute_agent(
                        agent_name,
                        context,
                        session.session_id,
                        metrics
                    )
                    
                    # Store output in context for next agents
                    context['agent_outputs'][agent_name] = agent_output.to_dict()
                    
                    # Check if critical agent failed
                    if agent_output.status == 'failed' and agent_name in ['idea_agent']:
                        # Stop pipeline if critical agent fails
                        self.logger.error(f"Critical agent {agent_name} failed, stopping pipeline")
                        raise ValueError(f"Critical agent {agent_name} failed")
                    
                except Exception as agent_error:
                    # Log error
                    self.logger.error(f"Agent {agent_name} failed: {str(agent_error)}")
                    metrics.add_error(f"{agent_name}: {str(agent_error)}")
                    
                    # Store fallback output so downstream agents can handle it
                    context['agent_outputs'][agent_name] = {
                        'agent_name': agent_name,
                        'status': 'failed',
                        'data': self._get_fallback_data(agent_name),
                        'error': str(agent_error)
                    }
                    
                    # Stop if critical agent fails
                    if agent_name in ['idea_agent']:
                        raise
            
            # Finalize output - determine if successful or partial
            has_errors = len(metrics.errors) > 0
            
            # Validate content completeness
            content_issues = self._validate_content_completeness(context['agent_outputs'])
            if content_issues:
                self.logger.warning(f"Content completeness issues: {', '.join(content_issues)}")
                has_errors = True
            
            final_status = 'partial' if has_errors else 'success'
            
            blueprint = self.finalize_output(session, run_id, metrics, final_status)
            
            # Store in memory if enabled
            if self.config.enable_memory:
                self._store_in_memory(user_id, run_id, blueprint)
            
            # Cleanup session on success
            if final_status == 'success':
                self.session_service.cleanup_session(session.session_id)
            
            status_msg = "completed successfully" if final_status == 'success' else "completed with partial results"
            self.logger.info(f"Pipeline {status_msg}: {run_id}")
            
            return blueprint
        
        except TimeoutError as e:
            self.logger.error(f"Pipeline timeout: {str(e)}")
            self.session_service.update_session_status(session.session_id, 'failed')
            
            # Return partial results
            return self._create_partial_output(
                session,
                run_id,
                metrics,
                str(e)
            )
        
        except Exception as e:
            self.logger.error(f"Pipeline failed: {str(e)}")
            self.session_service.update_session_status(session.session_id, 'failed')
            
            # Return partial results
            return self._create_partial_output(
                session,
                run_id,
                metrics,
                str(e)
            )
    
    def initialize_session(self, user_id: str):
        """Initialize session and load user preferences"""
        session = self.session_service.create_session(user_id)
        self.logger.info(f"Created session: {session.session_id}")
        return session
    
    def _execute_agent(
        self,
        agent_name: str,
        context: Dict[str, Any],
        session_id: str,
        metrics: MetricsCollector
    ):
        """Execute a single agent with error handling"""
        self.logger.info(f"Executing agent: {agent_name}")
        
        agent = self.agents[agent_name]
        agent_start = time.time()
        
        try:
            # Run agent
            output = agent.run(context, run_id=context['run_id'])
            
            # Record metrics
            duration_ms = int((time.time() - agent_start) * 1000)
            quality_score = output.scores.get(
                list(output.scores.keys())[0] if output.scores else None
            )
            
            metrics.record_agent_execution(
                agent_name=agent_name,
                duration_ms=duration_ms,
                status=output.status,
                quality_score=quality_score
            )
            
            # Store in session
            self.session_service.store_agent_output(
                session_id,
                agent_name,
                output.to_dict()
            )
            
            self.logger.info(f"Agent completed: {agent_name} in {duration_ms}ms with status {output.status}")
            
            return output
        
        except Exception as e:
            duration_ms = int((time.time() - agent_start) * 1000)
            error_msg = f"{type(e).__name__}: {str(e)}"
            
            self.logger.error(f"Agent failed: {agent_name} - {error_msg}")
            
            metrics.record_agent_execution(
                agent_name=agent_name,
                duration_ms=duration_ms,
                status='failed',
                error=error_msg
            )
            
            # Re-raise to be handled by pipeline
            raise
    
    def handle_agent_failure(
        self,
        agent_name: str,
        error: Exception
    ) -> Dict[str, Any]:
        """Handle agent failure and return partial result"""
        error_msg = f"{type(error).__name__}: {str(error)}"
        self.logger.error(f"Handling failure for {agent_name}: {error_msg}")
        
        return {
            'agent_name': agent_name,
            'status': 'failed',
            'error': error_msg,
            'data': {}
        }
    
    def finalize_output(
        self,
        session,
        run_id: str,
        metrics: MetricsCollector,
        status: str = 'success'
    ) -> BlueprintOutput:
        """Generate final blueprint output with summary"""
        # Get all agent outputs
        agent_outputs = self.session_service.get_full_context(session.session_id)
        
        # Extract key data
        idea_data = agent_outputs.get('idea_agent', {}).get('data', {})
        research_data = agent_outputs.get('research_agent', {}).get('data', {})
        product_data = agent_outputs.get('product_agent', {}).get('data', {})
        roadmap_data = agent_outputs.get('roadmap_agent', {}).get('data', {})
        finance_data = agent_outputs.get('finance_agent', {}).get('data', {})
        pitch_data = agent_outputs.get('pitch_agent', {}).get('data', {})
        
        # Generate summary
        summary = self._generate_summary(
            idea_data,
            research_data,
            product_data,
            roadmap_data,
            finance_data
        )
        
        # Finalize metrics
        run_metrics = metrics.finalize(status)
        self.metrics_store.store(run_metrics)
        
        # Update session status
        session_status = 'completed' if status == 'success' else 'partial'
        self.session_service.update_session_status(session.session_id, session_status)
        
        return BlueprintOutput(
            run_id=run_id,
            status=status,
            blueprint={
                'idea': idea_data,
                'research': research_data,
                'product': product_data,
                'roadmap': roadmap_data,
                'finance': finance_data,
                'pitch_deck': pitch_data
            },
            summary=summary,
            metrics=run_metrics.to_dict(),
            errors=[]
        )
    
    def _create_partial_output(
        self,
        session,
        run_id: str,
        metrics: MetricsCollector,
        error: str
    ) -> BlueprintOutput:
        """Create partial output when pipeline fails"""
        agent_outputs = self.session_service.get_full_context(session.session_id)
        
        # Extract whatever data is available
        blueprint = {}
        for agent_name in ['idea_agent', 'research_agent', 'product_agent', 
                          'roadmap_agent', 'finance_agent', 'pitch_agent']:
            output = agent_outputs.get(agent_name, {})
            if output:
                key = agent_name.replace('_agent', '')
                blueprint[key] = output.get('data', {})
        
        # Generate partial summary
        summary = "Pipeline execution incomplete. Partial results available."
        
        # Finalize metrics
        run_metrics = metrics.finalize('partial')
        self.metrics_store.store(run_metrics)
        
        return BlueprintOutput(
            run_id=run_id,
            status='partial',
            blueprint=blueprint,
            summary=summary,
            metrics=run_metrics.to_dict(),
            errors=[error]
        )
    
    def _generate_summary(
        self,
        idea_data: Dict[str, Any],
        research_data: Dict[str, Any],
        product_data: Dict[str, Any],
        roadmap_data: Dict[str, Any],
        finance_data: Dict[str, Any]
    ) -> str:
        """Generate text summary of the startup blueprint"""
        # Extract key information
        selected_idea_id = idea_data.get('selected_idea', {}).get('idea_id', '')
        ideas = idea_data.get('ideas', [])
        selected_idea = next(
            (idea for idea in ideas if idea['idea_id'] == selected_idea_id),
            ideas[0] if ideas else {}
        )
        
        title = selected_idea.get('title', 'Startup')
        description = selected_idea.get('description', '')
        
        market = research_data.get('market', {})
        tam = market.get('tam', 'N/A')
        
        mvp_features = product_data.get('mvp_scope', {}).get('features', [])
        
        projections = finance_data.get('projections', {}).get('base', {})
        year_1_revenue = projections.get('year_1_revenue', 0)
        
        runway = finance_data.get('runway_months', 0)
        
        summary = f"""
Startup Blueprint: {title}

Description: {description}

Market Opportunity:
- Total Addressable Market: {tam}
- Market is growing with strong demand

Product:
- MVP includes {len(mvp_features)} core features
- 90-day development timeline
- Focus on user experience and AI capabilities

Financial Projections:
- Year 1 Revenue: ${year_1_revenue:,.0f}
- Runway: {runway} months
- Strong unit economics with positive LTV:CAC ratio

Next Steps:
- Complete 30-day milestone: Core platform development
- Secure design partners for beta testing
- Prepare for seed/Series A fundraising

This blueprint provides a comprehensive foundation for launching and scaling the startup.
        """.strip()
        
        return summary
    
    def _validate_content_completeness(self, agent_outputs: Dict[str, Any]) -> List[str]:
        """
        Validate that agents produced complete content
        
        Returns:
            List of validation issues (empty if all valid)
        """
        issues = []
        
        # Check research agent
        research = agent_outputs.get('research_agent', {})
        if research.get('status') == 'success':
            research_data = research.get('data', {})
            market = research_data.get('market', {})
            if not market.get('tam'):
                issues.append("Research: Missing TAM")
            if not research_data.get('competitors'):
                issues.append("Research: No competitors identified")
        
        # Check product agent
        product = agent_outputs.get('product_agent', {})
        if product.get('status') == 'success':
            product_data = product.get('data', {})
            if len(product_data.get('personas', [])) < 2:
                issues.append("Product: Less than 2 personas")
            if len(product_data.get('features', [])) < 5:
                issues.append("Product: Less than 5 features")
        
        # Check roadmap agent
        roadmap = agent_outputs.get('roadmap_agent', {})
        if roadmap.get('status') == 'success':
            roadmap_data = roadmap.get('data', {})
            milestones = roadmap_data.get('milestones', {})
            if not all(k in milestones for k in ['30_day', '60_day', '90_day']):
                issues.append("Roadmap: Missing milestone phases")
        
        # Check finance agent
        finance = agent_outputs.get('finance_agent', {})
        if finance.get('status') == 'success':
            finance_data = finance.get('data', {})
            if not finance_data.get('projections'):
                issues.append("Finance: Missing projections")
            if not finance_data.get('unit_economics'):
                issues.append("Finance: Missing unit economics")
        
        # Check pitch agent
        pitch = agent_outputs.get('pitch_agent', {})
        if pitch.get('status') == 'success':
            pitch_data = pitch.get('data', {})
            slides = pitch_data.get('slides', [])
            if len(slides) < 10:
                issues.append(f"Pitch: Only {len(slides)}/10 slides generated")
        
        return issues
    
    def _get_fallback_data(self, agent_name: str) -> Dict[str, Any]:
        """Get fallback data for failed agents"""
        fallbacks = {
            'research_agent': {
                'market': {
                    'tam': '3.2B USD',
                    'sam': '1.0B USD',
                    'som': '160M USD',
                    'growth_rate': '15% CAGR',
                    'evidence': []
                },
                'competitors': [],
                'swot': {
                    'strengths': ['AI-powered technology'],
                    'weaknesses': ['New market entrant'],
                    'opportunities': ['Growing market'],
                    'threats': ['Established competitors']
                },
                'market_score': 0.65
            },
            'product_agent': {
                'personas': [],
                'features': [],
                'ux_flows': [],
                'mvp_scope': {'features': ['Core Platform', 'User Dashboard', 'Analytics']},
                'viability_score': 0.5
            },
            'roadmap_agent': {
                'architecture': {'components': [], 'tech_stack': {}, 'infrastructure': []},
                'milestones': {}
            },
            'finance_agent': {
                'assumptions': {'pricing_model': 'SaaS subscription'},
                'costs': {'opex_monthly': 0, 'capex_initial': 0},
                'unit_economics': {'cac': 7000, 'ltv': 28800, 'ltv_cac_ratio': 4.1, 'payback_period_months': 7},
                'projections': {'base': {'year_1_revenue': 600000, 'year_2_revenue': 2400000, 'year_3_revenue': 6000000}},
                'runway_months': 12
            },
            'pitch_agent': {
                'slides': []
            }
        }
        
        return fallbacks.get(agent_name, {})
    
    def _store_in_memory(
        self,
        user_id: str,
        run_id: str,
        blueprint: BlueprintOutput
    ) -> None:
        """Store blueprint summary in memory bank"""
        try:
            idea_data = blueprint.blueprint.get('idea', {})
            ideas = idea_data.get('ideas', [])
            selected_id = idea_data.get('selected_idea', {}).get('idea_id', '')
            selected_idea = next(
                (idea for idea in ideas if idea['idea_id'] == selected_id),
                ideas[0] if ideas else {}
            )
            
            title = selected_idea.get('title', 'Untitled Startup')
            
            self.memory_bank.store_blueprint_summary(
                user_id=user_id,
                run_id=run_id,
                idea_title=title,
                summary=blueprint.summary
            )
            
            self.logger.info(f"Stored blueprint in memory for user: {user_id}")
        
        except Exception as e:
            self.logger.warning(f"Failed to store in memory: {str(e)}")
