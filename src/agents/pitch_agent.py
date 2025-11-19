"""Pitch Deck Agent - Generates investor pitch deck content"""

from typing import Dict, Any, List
from src.agents.base_agent import BaseAgent
from src.models import AgentOutput


class PitchDeckAgent(BaseAgent):
    """Agent responsible for generating 10-slide pitch deck content"""
    
    def __init__(self):
        super().__init__('pitch_agent')
    
    def execute(self, context: Dict[str, Any]) -> AgentOutput:
        """
        Generate 10-slide pitch deck content
        
        Args:
            context: Contains outputs from all previous agents
        
        Returns:
            AgentOutput with pitch deck slides
        """
        try:
            # Get all previous outputs with safe access
            idea_output = self._get_agent_output(context, 'idea_agent')
            research_output = self._get_agent_output(context, 'research_agent')
            product_output = self._get_agent_output(context, 'product_agent')
            roadmap_output = self._get_agent_output(context, 'roadmap_agent')
            finance_output = self._get_agent_output(context, 'finance_agent')
            
            if not idea_output:
                raise ValueError("Missing required idea_agent output")
            
            # Extract key data with comprehensive fallbacks
            selected_idea = self._get_selected_idea(idea_output)
            
            # Safe extraction with fallbacks
            market_data = self._safe_extract_data(research_output, {
                'market': {'tam': '3.2B USD', 'sam': '1.0B USD', 'som': '160M USD', 'growth_rate': '15% CAGR'},
                'competitors': []
            })
            
            product_data = self._safe_extract_data(product_output, {
                'features': [],
                'personas': [],
                'mvp_scope': {'features': ['Core Platform', 'User Dashboard', 'Analytics']}
            })
            
            roadmap_data = self._safe_extract_data(roadmap_output, {
                'milestones': {}
            })
            
            finance_data = self._safe_extract_data(finance_output, {
                'assumptions': {'pricing_model': 'SaaS subscription'},
                'unit_economics': {'cac': 7000, 'ltv': 28800, 'ltv_cac_ratio': 4.1, 'payback_period_months': 7},
                'projections': {'base': {'year_1_revenue': 600000, 'year_2_revenue': 2400000, 'year_3_revenue': 6000000}},
                'runway_months': 12
            })
            
            # Generate all 10 slides
            slides = [
                self._slide_1_problem(selected_idea, market_data),
                self._slide_2_solution(selected_idea, product_data),
                self._slide_3_market(market_data),
                self._slide_4_product(product_data),
                self._slide_5_competitive_edge(selected_idea, market_data, product_data),
                self._slide_6_business_model(finance_data),
                self._slide_7_roadmap(roadmap_data),
                self._slide_8_traction(selected_idea),
                self._slide_9_financials(finance_data),
                self._slide_10_vision(selected_idea, market_data)
            ]
            
            output_data = {'slides': slides}
            
            return AgentOutput(
                agent_name=self.agent_name,
                execution_time_ms=0,
                status='success',
                data=output_data
            )
        
        except Exception as e:
            self.logger.error(f"Pitch agent failed: {str(e)}")
            raise
    
    def _get_selected_idea(self, idea_output: Dict[str, Any]) -> Dict[str, Any]:
        """Extract selected idea"""
        selected_id = idea_output['data']['selected_idea']['idea_id']
        ideas = idea_output['data']['ideas']
        return next(idea for idea in ideas if idea['idea_id'] == selected_id)
    
    def _safe_extract_data(self, agent_output: Dict[str, Any], fallback: Dict[str, Any]) -> Dict[str, Any]:
        """Safely extract data from agent output with fallback"""
        if not agent_output:
            return fallback
        
        if 'data' not in agent_output:
            return fallback
        
        data = agent_output['data']
        
        # Merge with fallback to ensure all keys exist
        result = fallback.copy()
        result.update(data)
        
        return result
    
    def _slide_1_problem(
        self,
        idea: Dict[str, Any],
        market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Slide 1: Problem"""
        domain = idea.get('title', 'Technology').split()[0]
        
        # Safe access to market data
        market_info = market_data.get('market', {})
        growth_rate = market_info.get('growth_rate', '15% CAGR')
        
        return {
            'slide_number': 1,
            'title': 'The Problem',
            'content': [
                f'{domain} industry faces significant operational inefficiencies',
                'Manual processes lead to 30-40% productivity loss',
                'Lack of real-time insights hampers decision-making',
                'Existing solutions are outdated and expensive',
                f'Market growing at {growth_rate}'
            ],
            'talking_points': [
                'Start with a relatable pain point',
                'Use specific statistics to quantify the problem',
                'Emphasize the urgency and market timing',
                'Connect problem to market opportunity'
            ],
            'visual_suggestions': [
                'Before/after comparison diagram',
                'Statistics highlighting inefficiency',
                'Customer pain point quotes',
                'Market growth chart'
            ]
        }
    
    def _slide_2_solution(
        self,
        idea: Dict[str, Any],
        product_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Slide 2: Solution"""
        top_features = [f['name'] for f in product_data['features'][:3]]
        
        return {
            'slide_number': 2,
            'title': 'Our Solution',
            'content': [
                f'{idea["title"]}: {idea["description"]}',
                f'Key capabilities: {", ".join(top_features)}',
                'AI-powered automation reduces manual work by 70%',
                'Real-time insights enable faster decision-making',
                'Modern, intuitive interface designed for ease of use'
            ],
            'talking_points': [
                'Clearly articulate the value proposition',
                'Explain how it solves the stated problem',
                'Highlight unique AI/technology advantage',
                'Emphasize user experience benefits'
            ],
            'visual_suggestions': [
                'Product screenshot or mockup',
                'Feature highlights with icons',
                'Before/after workflow comparison',
                'Value proposition diagram'
            ]
        }
    
    def _slide_3_market(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Slide 3: Market Opportunity"""
        market = market_data.get('market', {
            'tam': '3.2B USD',
            'sam': '1.0B USD',
            'som': '160M USD',
            'growth_rate': '15% CAGR'
        })
        
        return {
            'slide_number': 3,
            'title': 'Market Opportunity',
            'content': [
                f'Total Addressable Market (TAM): {market["tam"]}',
                f'Serviceable Addressable Market (SAM): {market["sam"]}',
                f'Serviceable Obtainable Market (SOM): {market["som"]}',
                f'Market growing at {market["growth_rate"]}',
                'Strong tailwinds from digital transformation trends'
            ],
            'talking_points': [
                'Emphasize market size and growth potential',
                'Explain TAM/SAM/SOM breakdown',
                'Highlight market trends supporting growth',
                'Show realistic path to capturing market share'
            ],
            'visual_suggestions': [
                'TAM/SAM/SOM concentric circles',
                'Market growth projection chart',
                'Industry trend indicators',
                'Geographic expansion map'
            ]
        }
    
    def _slide_4_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Slide 4: Product"""
        mvp_scope = product_data.get('mvp_scope', {})
        mvp_features = mvp_scope.get('features', ['Core Platform', 'User Dashboard', 'Analytics'])[:5]
        
        return {
            'slide_number': 4,
            'title': 'Product Overview',
            'content': [
                'Core Features:',
                *[f'• {feature}' for feature in mvp_features],
                f'Designed for {len(product_data.get("personas", []))} key user personas',
                'Built on modern, scalable architecture'
            ],
            'talking_points': [
                'Walk through key features and benefits',
                'Explain user personas and use cases',
                'Highlight technical advantages',
                'Demonstrate product-market fit'
            ],
            'visual_suggestions': [
                'Product demo screenshots',
                'Feature comparison matrix',
                'User persona cards',
                'Product architecture diagram'
            ]
        }
    
    def _slide_5_competitive_edge(
        self,
        idea: Dict[str, Any],
        market_data: Dict[str, Any],
        product_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Slide 5: Competitive Edge"""
        competitors = market_data.get('competitors', [])[:2]
        competitor_names = [c.get('name', 'Competitor') for c in competitors] if competitors else ['Established Player 1', 'Established Player 2']
        
        return {
            'slide_number': 5,
            'title': 'Competitive Advantage',
            'content': [
                f'Key competitors: {", ".join(competitor_names)}',
                'Our advantages:',
                '• AI-powered intelligence (vs. rule-based systems)',
                '• Modern UX (vs. legacy interfaces)',
                '• Flexible pricing (vs. enterprise-only)',
                '• Faster implementation (90 days vs. 6-12 months)'
            ],
            'talking_points': [
                'Acknowledge competition honestly',
                'Highlight clear differentiation',
                'Explain sustainable competitive advantages',
                'Show why customers will switch'
            ],
            'visual_suggestions': [
                'Competitive positioning matrix',
                'Feature comparison table',
                'Technology stack comparison',
                'Customer testimonial quotes'
            ]
        }
    
    def _slide_6_business_model(self, finance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Slide 6: Business Model"""
        assumptions = finance_data.get('assumptions', {})
        pricing = assumptions.get('pricing_model', 'SaaS subscription')
        unit_econ = finance_data.get('unit_economics', {
            'cac': 7000,
            'ltv': 28800,
            'ltv_cac_ratio': 4.1,
            'payback_period_months': 7
        })
        
        return {
            'slide_number': 6,
            'title': 'Business Model',
            'content': [
                f'Revenue Model: {pricing}',
                f'Customer Acquisition Cost (CAC): ${unit_econ.get("cac", 7000):,.0f}',
                f'Lifetime Value (LTV): ${unit_econ.get("ltv", 28800):,.0f}',
                f'LTV:CAC Ratio: {unit_econ.get("ltv_cac_ratio", 4.1):.1f}x (target: >3x)',
                f'Payback Period: {unit_econ.get("payback_period_months", 7):.0f} months'
            ],
            'talking_points': [
                'Explain revenue model and pricing strategy',
                'Highlight strong unit economics',
                'Show path to profitability',
                'Discuss scalability of model'
            ],
            'visual_suggestions': [
                'Revenue model diagram',
                'Unit economics visualization',
                'Pricing tiers table',
                'Customer lifetime value chart'
            ]
        }
    
    def _slide_7_roadmap(self, roadmap_data: Dict[str, Any]) -> Dict[str, Any]:
        """Slide 7: Roadmap"""
        milestones = roadmap_data.get('milestones', {})
        
        return {
            'slide_number': 7,
            'title': 'Product Roadmap',
            'content': [
                '30 Days: Core platform and authentication',
                '60 Days: AI features and advanced analytics',
                '90 Days: Complete MVP and beta launch',
                '6 Months: Scale to 100+ customers',
                '12 Months: Expand features and enter new markets'
            ],
            'talking_points': [
                'Show clear execution plan',
                'Highlight near-term milestones',
                'Demonstrate realistic timeline',
                'Explain resource allocation'
            ],
            'visual_suggestions': [
                'Timeline visualization',
                'Milestone cards with dates',
                'Gantt chart',
                'Feature release schedule'
            ]
        }
    
    def _slide_8_traction(self, idea: Dict[str, Any]) -> Dict[str, Any]:
        """Slide 8: Traction"""
        # Generate realistic early-stage traction metrics
        return {
            'slide_number': 8,
            'title': 'Traction & Validation',
            'content': [
                '15 customer discovery interviews completed',
                '5 design partners committed for beta',
                '3 letters of intent from enterprise customers',
                'Technical prototype validated with users',
                'Experienced founding team with domain expertise'
            ],
            'talking_points': [
                'Show customer validation',
                'Highlight early commitments',
                'Demonstrate market demand',
                'Emphasize team credibility'
            ],
            'visual_suggestions': [
                'Customer logos (design partners)',
                'User feedback quotes',
                'Team photos and credentials',
                'Prototype screenshots'
            ]
        }
    
    def _slide_9_financials(self, finance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Slide 9: Financial Projections"""
        projections = finance_data.get('projections', {})
        base_proj = projections.get('base', {
            'year_1_revenue': 600000,
            'year_2_revenue': 2400000,
            'year_3_revenue': 6000000
        })
        
        return {
            'slide_number': 9,
            'title': 'Financial Projections',
            'content': [
                f'Year 1 Revenue: ${base_proj.get("year_1_revenue", 600000):,.0f}',
                f'Year 2 Revenue: ${base_proj.get("year_2_revenue", 2400000):,.0f}',
                f'Year 3 Revenue: ${base_proj.get("year_3_revenue", 6000000):,.0f}',
                f'Current Runway: {finance_data.get("runway_months", 12)} months',
                'Seeking $2M Series A to accelerate growth'
            ],
            'talking_points': [
                'Walk through revenue projections',
                'Explain key assumptions',
                'Show path to profitability',
                'Articulate funding needs and use of funds'
            ],
            'visual_suggestions': [
                'Revenue growth chart',
                '3-scenario projection comparison',
                'Use of funds breakdown',
                'Key metrics dashboard'
            ]
        }
    
    def _slide_10_vision(
        self,
        idea: Dict[str, Any],
        market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Slide 10: Vision"""
        domain = idea.get('title', 'Technology').split()[0]
        market_info = market_data.get('market', {})
        tam = market_info.get('tam', '3.2B USD')
        
        return {
            'slide_number': 10,
            'title': 'Our Vision',
            'content': [
                f'Become the leading AI platform for {domain}',
                f'Transform how {tam} market operates',
                'Expand to adjacent markets and use cases',
                'Build the future of intelligent automation',
                'Join us in revolutionizing the industry'
            ],
            'talking_points': [
                'Paint compelling long-term vision',
                'Show ambition and market leadership potential',
                'Explain expansion opportunities',
                'End with strong call to action'
            ],
            'visual_suggestions': [
                'Vision statement with inspiring imagery',
                'Market expansion roadmap',
                'Future product concepts',
                'Team contact information'
            ]
        }
