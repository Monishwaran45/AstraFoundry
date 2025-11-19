"""Roadmap Agent - Creates engineering roadmap and system architecture"""

from typing import Dict, Any, List, Optional
from src.agents.base_agent import BaseAgent
from src.models import AgentOutput
from src.tools.mcp_tool_adapter import MCPToolAdapter


class RoadmapAgent(BaseAgent):
    """Agent responsible for creating 30/60/90-day engineering roadmap"""
    
    def __init__(self, mcp_tool: Optional[MCPToolAdapter] = None):
        super().__init__('roadmap_agent')
        self.mcp_tool = mcp_tool
    
    def execute(self, context: Dict[str, Any]) -> AgentOutput:
        """
        Create system architecture and 30/60/90-day roadmap
        
        Args:
            context: Contains outputs from idea, research, and product agents
        
        Returns:
            AgentOutput with architecture and milestone plans
        """
        try:
            # Get previous outputs
            idea_output = self._get_agent_output(context, 'idea_agent')
            research_output = self._get_agent_output(context, 'research_agent')
            product_output = self._get_agent_output(context, 'product_agent')
            
            if not idea_output or not product_output:
                raise ValueError("Missing required agent outputs (idea or product)")
            
            selected_idea = self._get_selected_idea(idea_output)
            
            # Safe extraction of MVP features
            product_data = product_output.get('data', {})
            mvp_scope = product_data.get('mvp_scope', {})
            mvp_features = mvp_scope.get('feature_details', [])
            
            # Generate architecture
            architecture = self._design_architecture(selected_idea, mvp_features)
            
            # Generate milestones
            milestones = self._create_milestones(architecture, mvp_features)
            
            # Optional: Enhance with MCP tools
            if self.mcp_tool and self.mcp_tool.enabled:
                self._enhance_with_mcp(architecture, milestones)
            
            output_data = {
                'architecture': architecture,
                'milestones': milestones
            }
            
            return AgentOutput(
                agent_name=self.agent_name,
                execution_time_ms=0,
                status='success',
                data=output_data
            )
        
        except Exception as e:
            self.logger.error(f"Roadmap agent failed: {str(e)}")
            raise
    
    def _get_selected_idea(self, idea_output: Dict[str, Any]) -> Dict[str, Any]:
        """Extract selected idea"""
        selected_id = idea_output['data']['selected_idea']['idea_id']
        ideas = idea_output['data']['ideas']
        return next(idea for idea in ideas if idea['idea_id'] == selected_id)
    
    def _design_architecture(
        self,
        idea: Dict[str, Any],
        features: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Design system architecture"""
        title = idea['title']
        
        # Determine tech stack based on requirements
        tech_stack = {
            'frontend': ['React', 'TypeScript', 'Tailwind CSS'],
            'backend': ['Python', 'FastAPI', 'PostgreSQL'],
            'ai_ml': ['TensorFlow', 'scikit-learn', 'Gemini API'],
            'infrastructure': ['Docker', 'Kubernetes', 'Google Cloud'],
            'monitoring': ['Prometheus', 'Grafana', 'Cloud Logging']
        }
        
        # Define key components
        components = [
            'Web Application (React SPA)',
            'REST API Server (FastAPI)',
            'Database (PostgreSQL)',
            'AI/ML Service (Python)',
            'Authentication Service (OAuth 2.0)',
            'Background Job Queue (Celery)',
            'Cache Layer (Redis)',
            'Object Storage (Cloud Storage)',
            'API Gateway',
            'Load Balancer'
        ]
        
        # Infrastructure requirements
        infrastructure = [
            'Container orchestration (Kubernetes)',
            'CI/CD pipeline (GitHub Actions)',
            'Monitoring and alerting',
            'Backup and disaster recovery',
            'CDN for static assets',
            'Auto-scaling configuration'
        ]
        
        # Generate Mermaid diagram
        diagram = self._generate_architecture_diagram(components)
        
        return {
            'components': components,
            'tech_stack': tech_stack,
            'infrastructure': infrastructure,
            'diagram': diagram
        }
    
    def _generate_architecture_diagram(self, components: List[str]) -> str:
        """Generate Mermaid architecture diagram"""
        diagram = """```mermaid
graph TB
    User[User] --> LB[Load Balancer]
    LB --> Web[Web Application]
    Web --> API[API Gateway]
    API --> Auth[Auth Service]
    API --> Core[Core API Server]
    Core --> DB[(Database)]
    Core --> Cache[(Redis Cache)]
    Core --> ML[AI/ML Service]
    Core --> Queue[Job Queue]
    Queue --> Worker[Background Workers]
    Worker --> Storage[Object Storage]
    
    style User fill:#e1f5ff
    style Web fill:#fff4e1
    style Core fill:#e8f5e9
    style DB fill:#f3e5f5
    style ML fill:#ffe0b2
```"""
        return diagram
    
    def _create_milestones(
        self,
        architecture: Dict[str, Any],
        features: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """Create 30/60/90-day milestone plans"""
        # Organize features by priority
        high_priority = [f for f in features if f['priority'] == 'high']
        medium_priority = [f for f in features if f['priority'] == 'medium']
        
        milestones = {
            '30_day': self._create_30_day_plan(architecture, high_priority),
            '60_day': self._create_60_day_plan(architecture, high_priority, medium_priority),
            '90_day': self._create_90_day_plan(architecture, features)
        }
        
        return milestones
    
    def _create_30_day_plan(
        self,
        architecture: Dict[str, Any],
        high_priority_features: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create 30-day milestone plan"""
        return {
            'deliverables': [
                'Project setup and repository structure',
                'Development environment configuration',
                'Database schema design and migration',
                'Authentication and authorization system',
                'Core API endpoints (CRUD operations)',
                'Basic frontend scaffolding',
                f'Implement: {high_priority_features[0]["name"]}' if high_priority_features else 'Core feature implementation'
            ],
            'dependencies': [
                'Cloud infrastructure provisioning',
                'API key and credential setup',
                'Development team onboarding',
                'Design system and UI components'
            ],
            'risks': [
                'Infrastructure setup delays',
                'Third-party API integration issues',
                'Team ramp-up time',
                'Scope creep on core features'
            ]
        }
    
    def _create_60_day_plan(
        self,
        architecture: Dict[str, Any],
        high_priority_features: List[Dict[str, Any]],
        medium_priority_features: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create 60-day milestone plan"""
        feature_names = [f['name'] for f in (high_priority_features + medium_priority_features)[:4]]
        
        return {
            'deliverables': [
                'Complete all high-priority features',
                'AI/ML model integration',
                'Advanced API endpoints',
                'Frontend feature implementation',
                'User dashboard and analytics',
                'Mobile-responsive design',
                f'Features: {", ".join(feature_names[:3])}'
            ],
            'dependencies': [
                'Completion of 30-day deliverables',
                'ML model training data',
                'UI/UX design finalization',
                'API documentation'
            ],
            'risks': [
                'ML model accuracy issues',
                'Performance bottlenecks',
                'Integration complexity',
                'Feature interdependencies'
            ]
        }
    
    def _create_90_day_plan(
        self,
        architecture: Dict[str, Any],
        all_features: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create 90-day milestone plan"""
        return {
            'deliverables': [
                'Complete MVP feature set',
                'End-to-end testing suite',
                'Performance optimization',
                'Security audit and hardening',
                'Production deployment pipeline',
                'Monitoring and alerting setup',
                'User documentation and guides',
                'Beta launch preparation'
            ],
            'dependencies': [
                'Completion of 60-day deliverables',
                'Security review approval',
                'Load testing results',
                'Beta user recruitment'
            ],
            'risks': [
                'Production deployment issues',
                'Performance under load',
                'Security vulnerabilities',
                'User feedback requiring major changes',
                'Resource constraints for polish'
            ]
        }
    
    def _enhance_with_mcp(
        self,
        architecture: Dict[str, Any],
        milestones: Dict[str, Dict[str, Any]]
    ) -> None:
        """Enhance roadmap with MCP tool data"""
        try:
            # Example: Get additional tech stack recommendations
            result = self.mcp_tool.invoke('tech_recommendations', {
                'components': architecture['components']
            })
            
            if result['success']:
                self.logger.info("Enhanced roadmap with MCP tool data")
        except Exception as e:
            self.logger.warning(f"MCP enhancement failed: {str(e)}")
