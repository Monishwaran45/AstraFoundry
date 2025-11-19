"""Product Designer Agent - Creates user personas, features, and UX flows"""

from typing import Dict, Any, List
from src.agents.base_agent import BaseAgent
from src.models import AgentOutput


class ProductDesignerAgent(BaseAgent):
    """Agent responsible for product design and feature prioritization"""
    
    def __init__(self):
        super().__init__('product_agent')
    
    def execute(self, context: Dict[str, Any]) -> AgentOutput:
        """
        Create product design with personas, features, and UX flows
        
        Args:
            context: Contains idea_agent and research_agent outputs
        
        Returns:
            AgentOutput with personas, features, UX flows, and MVP scope
        """
        try:
            # Get previous outputs
            idea_output = self._get_agent_output(context, 'idea_agent')
            research_output = self._get_agent_output(context, 'research_agent')
            
            if not idea_output:
                raise ValueError("Missing required idea_agent output")
            
            selected_idea = self._get_selected_idea(idea_output)
            
            # Generate product design components (use research if available)
            research_data = research_output.get('data', {}) if research_output else {}
            personas = self._create_personas(selected_idea, research_data)
            features = self._brainstorm_features(selected_idea, personas)
            features = self._score_features_rice(features)
            features = self._prioritize_features(features)
            ux_flows = self._design_ux_flows(selected_idea, personas, features)
            mvp_scope = self._define_mvp(features)
            viability_score = self._calculate_viability(features, personas)
            
            output_data = {
                'personas': personas,
                'features': features,
                'ux_flows': ux_flows,
                'mvp_scope': mvp_scope,
                'viability_score': viability_score
            }
            
            return AgentOutput(
                agent_name=self.agent_name,
                execution_time_ms=0,
                status='success',
                data=output_data,
                scores={'product_viability': viability_score}
            )
        
        except Exception as e:
            self.logger.error(f"Product agent failed: {str(e)}")
            raise
    
    def _get_selected_idea(self, idea_output: Dict[str, Any]) -> Dict[str, Any]:
        """Extract selected idea from idea agent output"""
        selected_id = idea_output['data']['selected_idea']['idea_id']
        ideas = idea_output['data']['ideas']
        return next(idea for idea in ideas if idea['idea_id'] == selected_id)
    
    def _create_personas(
        self,
        idea: Dict[str, Any],
        research_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Create at least 2 user personas"""
        title = idea['title']
        domain = title.split()[0].lower()
        
        personas = [
            {
                'name': 'Enterprise Decision Maker',
                'demographics': {
                    'age_range': '35-50',
                    'role': 'VP/Director level',
                    'industry': domain,
                    'company_size': '500-5000 employees'
                },
                'pain_points': [
                    'Inefficient manual processes',
                    'Lack of real-time insights',
                    'High operational costs',
                    'Difficulty scaling operations'
                ],
                'goals': [
                    'Reduce operational costs by 30%',
                    'Improve decision-making speed',
                    'Scale operations efficiently',
                    'Gain competitive advantage'
                ],
                'behaviors': [
                    'Data-driven decision maker',
                    'Values ROI and proven results',
                    'Prefers enterprise-grade solutions',
                    'Requires strong security and compliance'
                ]
            },
            {
                'name': 'Operations Manager',
                'demographics': {
                    'age_range': '28-40',
                    'role': 'Manager/Team Lead',
                    'industry': domain,
                    'company_size': '50-500 employees'
                },
                'pain_points': [
                    'Time-consuming manual tasks',
                    'Limited visibility into operations',
                    'Coordination challenges across teams',
                    'Reporting overhead'
                ],
                'goals': [
                    'Automate repetitive tasks',
                    'Improve team productivity',
                    'Better track performance metrics',
                    'Simplify reporting processes'
                ],
                'behaviors': [
                    'Hands-on and detail-oriented',
                    'Values ease of use',
                    'Needs quick implementation',
                    'Prefers intuitive interfaces'
                ]
            },
            {
                'name': 'Technical Implementer',
                'demographics': {
                    'age_range': '25-35',
                    'role': 'Engineer/Technical Lead',
                    'industry': domain,
                    'company_size': '100-1000 employees'
                },
                'pain_points': [
                    'Integration complexity',
                    'Legacy system constraints',
                    'Limited API documentation',
                    'Maintenance burden'
                ],
                'goals': [
                    'Seamless system integration',
                    'Reliable and scalable solution',
                    'Good developer experience',
                    'Minimal maintenance overhead'
                ],
                'behaviors': [
                    'Values technical excellence',
                    'Prefers well-documented APIs',
                    'Active in developer communities',
                    'Evaluates multiple solutions'
                ]
            }
        ]
        
        return personas[:2]  # Return at least 2 personas
    
    def _brainstorm_features(
        self,
        idea: Dict[str, Any],
        personas: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Brainstorm 10-15 features"""
        title = idea['title']
        
        features = [
            {
                'feature_id': 'f001',
                'name': 'Real-time Dashboard',
                'description': 'Interactive dashboard with real-time metrics and KPIs',
                'target_personas': ['Enterprise Decision Maker', 'Operations Manager']
            },
            {
                'feature_id': 'f002',
                'name': 'AI-Powered Analytics',
                'description': 'Machine learning models for predictive insights and recommendations',
                'target_personas': ['Enterprise Decision Maker']
            },
            {
                'feature_id': 'f003',
                'name': 'Automated Workflows',
                'description': 'Configurable automation for repetitive tasks and processes',
                'target_personas': ['Operations Manager']
            },
            {
                'feature_id': 'f004',
                'name': 'REST API',
                'description': 'Comprehensive REST API for system integration',
                'target_personas': ['Technical Implementer']
            },
            {
                'feature_id': 'f005',
                'name': 'Custom Reports',
                'description': 'Flexible reporting engine with export capabilities',
                'target_personas': ['Enterprise Decision Maker', 'Operations Manager']
            },
            {
                'feature_id': 'f006',
                'name': 'Role-Based Access Control',
                'description': 'Granular permissions and access management',
                'target_personas': ['Enterprise Decision Maker', 'Technical Implementer']
            },
            {
                'feature_id': 'f007',
                'name': 'Mobile App',
                'description': 'Native mobile applications for iOS and Android',
                'target_personas': ['Operations Manager']
            },
            {
                'feature_id': 'f008',
                'name': 'Collaboration Tools',
                'description': 'Team collaboration features with comments and notifications',
                'target_personas': ['Operations Manager']
            },
            {
                'feature_id': 'f009',
                'name': 'Data Import/Export',
                'description': 'Bulk data import and export with multiple format support',
                'target_personas': ['Technical Implementer', 'Operations Manager']
            },
            {
                'feature_id': 'f010',
                'name': 'Audit Logging',
                'description': 'Comprehensive audit trail for compliance and security',
                'target_personas': ['Enterprise Decision Maker', 'Technical Implementer']
            }
        ]
        
        return features
    
    def _score_features_rice(
        self,
        features: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Calculate RICE scores for features"""
        # RICE = (Reach * Impact * Confidence) / Effort
        
        rice_params = {
            'f001': {'reach': 1000, 'impact': 3, 'confidence': 0.9, 'effort': 4},
            'f002': {'reach': 800, 'impact': 3, 'confidence': 0.7, 'effort': 8},
            'f003': {'reach': 1200, 'impact': 3, 'confidence': 0.8, 'effort': 6},
            'f004': {'reach': 500, 'impact': 2, 'confidence': 0.9, 'effort': 3},
            'f005': {'reach': 900, 'impact': 2, 'confidence': 0.85, 'effort': 4},
            'f006': {'reach': 1000, 'impact': 3, 'confidence': 0.95, 'effort': 5},
            'f007': {'reach': 700, 'impact': 2, 'confidence': 0.7, 'effort': 10},
            'f008': {'reach': 600, 'impact': 2, 'confidence': 0.8, 'effort': 3},
            'f009': {'reach': 400, 'impact': 2, 'confidence': 0.9, 'effort': 2},
            'f010': {'reach': 800, 'impact': 2, 'confidence': 0.9, 'effort': 3}
        }
        
        for feature in features:
            fid = feature['feature_id']
            params = rice_params.get(fid, {'reach': 500, 'impact': 2, 'confidence': 0.7, 'effort': 4})
            
            rice_total = (params['reach'] * params['impact'] * params['confidence']) / params['effort']
            
            feature['rice_score'] = {
                'reach': params['reach'],
                'impact': params['impact'],
                'confidence': params['confidence'],
                'effort': params['effort'],
                'total': round(rice_total, 1)
            }
        
        return features
    
    def _prioritize_features(
        self,
        features: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Prioritize features based on RICE scores"""
        # Sort by RICE score
        features.sort(key=lambda f: f['rice_score']['total'], reverse=True)
        
        # Assign priority levels
        for i, feature in enumerate(features):
            if i < 3:
                feature['priority'] = 'high'
            elif i < 7:
                feature['priority'] = 'medium'
            else:
                feature['priority'] = 'low'
        
        return features
    
    def _design_ux_flows(
        self,
        idea: Dict[str, Any],
        personas: List[Dict[str, Any]],
        features: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Design 2-3 core UX flows"""
        flows = [
            {
                'flow_name': 'Onboarding Flow',
                'persona': personas[0]['name'],
                'steps': [
                    'User signs up with email/SSO',
                    'Complete profile setup',
                    'Connect data sources',
                    'Configure initial settings',
                    'View guided tour',
                    'Access main dashboard'
                ]
            },
            {
                'flow_name': 'Core Workflow',
                'persona': personas[1]['name'] if len(personas) > 1 else personas[0]['name'],
                'steps': [
                    'Login to platform',
                    'View real-time dashboard',
                    'Identify key insights',
                    'Configure automated workflow',
                    'Review and approve',
                    'Monitor execution'
                ]
            },
            {
                'flow_name': 'Reporting Flow',
                'persona': personas[0]['name'],
                'steps': [
                    'Navigate to reports section',
                    'Select report template',
                    'Customize parameters',
                    'Generate report',
                    'Review visualizations',
                    'Export and share'
                ]
            }
        ]
        
        return flows[:3]
    
    def _define_mvp(self, features: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Define MVP scope with top 5-7 features"""
        mvp_features = [f for f in features if f['priority'] in ['high', 'medium']][:7]
        
        return {
            'features': [f['name'] for f in mvp_features],
            'timeline': '90 days',
            'feature_details': mvp_features
        }
    
    def _calculate_viability(
        self,
        features: List[Dict[str, Any]],
        personas: List[Dict[str, Any]]
    ) -> float:
        """Calculate product viability score (0-1)"""
        # Average RICE score (normalized)
        avg_rice = sum(f['rice_score']['total'] for f in features) / len(features)
        rice_score = min(1.0, avg_rice / 500)  # Normalize to 0-1
        
        # Persona coverage (more personas = better)
        persona_score = min(1.0, len(personas) / 3)
        
        # Feature quality (high priority features)
        high_priority_count = sum(1 for f in features if f['priority'] == 'high')
        feature_score = min(1.0, high_priority_count / 5)
        
        # Weighted average
        viability = (rice_score * 0.5 + persona_score * 0.2 + feature_score * 0.3)
        
        return round(viability, 2)
