"""Research Agent - Performs market and competitor research"""

from typing import Dict, Any, List
from src.agents.base_agent import BaseAgent
from src.models import AgentOutput
from src.tools.google_search_adapter import GoogleSearchAdapter
from src.utils.number_parser import parse_market_number, parse_percentage


class ResearchAgent(BaseAgent):
    """Agent responsible for market analysis and competitor research"""
    
    def __init__(self, search_tool: GoogleSearchAdapter):
        super().__init__('research_agent')
        self.search_tool = search_tool
    
    def execute(self, context: Dict[str, Any]) -> AgentOutput:
        """
        Perform comprehensive market and competitor research
        
        Args:
            context: Contains idea_agent output with selected idea
        
        Returns:
            AgentOutput with market data, competitors, and SWOT analysis
        """
        try:
            # Get selected idea from previous agent
            idea_output = self._get_agent_output(context, 'idea_agent')
            if not idea_output:
                raise ValueError("No idea_agent output found in context")
            
            selected_idea_id = idea_output['data']['selected_idea']['idea_id']
            ideas = idea_output['data']['ideas']
            selected_idea = next(
                (idea for idea in ideas if idea['idea_id'] == selected_idea_id),
                ideas[0]
            )
            
            # Perform research with error handling
            market_data = self._research_market(selected_idea)
            competitors = self._research_competitors(selected_idea)
            swot = self._generate_swot(selected_idea, market_data, competitors)
            
            # Calculate market score
            market_score = self._calculate_market_score(market_data, competitors)
            
            output_data = {
                'market': market_data,
                'competitors': competitors,
                'swot': swot,
                'market_score': market_score
            }
            
            return AgentOutput(
                agent_name=self.agent_name,
                execution_time_ms=0,
                status='success',
                data=output_data,
                scores={'market_strength': market_score}
            )
        
        except Exception as e:
            self.logger.error(f"Research agent failed: {str(e)}")
            # Return fallback data instead of failing
            return AgentOutput(
                agent_name=self.agent_name,
                execution_time_ms=0,
                status='failed',
                data={
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
                scores={'market_strength': 0.65}
            )
    
    def _research_market(self, idea: Dict[str, Any]) -> Dict[str, Any]:
        """Research market size and growth"""
        title = idea['title']
        
        # Search for market size information
        query = f"{title} market size TAM 2024"
        results = self.search_tool.search(query, num_results=5)
        
        # Extract domain for market estimation
        domain = title.split()[0].lower()
        
        # Generate market estimates (in production, would parse from search results)
        market_estimates = self._estimate_market_size(domain, results)
        
        evidence = [
            {
                'source': 'search',
                'query': query,
                'url': result['url'],
                'snippet': result['snippet']
            }
            for result in results
        ]
        
        return {
            'tam': market_estimates['tam'],
            'sam': market_estimates['sam'],
            'som': market_estimates['som'],
            'growth_rate': market_estimates['growth_rate'],
            'evidence': evidence
        }
    
    def _estimate_market_size(
        self,
        domain: str,
        search_results: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        """Estimate market size based on domain and search results"""
        # Market size estimates by domain (simplified)
        market_data = {
            'climate-tech': {'tam': '3.2B USD', 'growth': '18%'},
            'healthcare': {'tam': '8.5B USD', 'growth': '12%'},
            'fintech': {'tam': '5.1B USD', 'growth': '22%'},
            'edtech': {'tam': '4.3B USD', 'growth': '16%'},
            'logistics': {'tam': '6.7B USD', 'growth': '14%'},
            'energy': {'tam': '7.2B USD', 'growth': '15%'},
            'default': {'tam': '2.5B USD', 'growth': '10%'}
        }
        
        data = market_data.get(domain, market_data['default'])
        
        # Use number parser to safely extract TAM value
        tam_value = parse_market_number(data['tam'])
        
        return {
            'tam': data['tam'],
            'sam': f"{tam_value * 0.3:.1f}B USD",
            'som': f"{tam_value * 0.05:.1f}B USD",
            'growth_rate': f"{data['growth']} CAGR"
        }
    
    def _research_competitors(self, idea: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Research and identify competitors"""
        title = idea['title']
        
        # Search for competitors
        query = f"{title} competitors alternatives"
        results = self.search_tool.search(query, num_results=5)
        
        # Generate competitor profiles
        competitors = []
        competitor_names = self._extract_competitor_names(title, results)
        
        for i, name in enumerate(competitor_names[:3]):  # Top 3 competitors
            competitor = {
                'name': name,
                'description': f"{name} is a leading player in the {title.split()[0].lower()} space",
                'strengths': self._generate_competitor_strengths(name),
                'weaknesses': self._generate_competitor_weaknesses(name),
                'url': results[i]['url'] if i < len(results) else f"https://example.com/{name.lower().replace(' ', '')}"
            }
            competitors.append(competitor)
        
        return competitors
    
    def _extract_competitor_names(
        self,
        title: str,
        search_results: List[Dict[str, Any]]
    ) -> List[str]:
        """Extract competitor names from search results"""
        # In production, would use NLP to extract company names
        # For now, generating plausible competitor names
        domain = title.split()[0]
        suffixes = ['AI', 'Pro', 'Hub', 'Sense', 'IQ', 'Labs']
        
        competitors = []
        for i, suffix in enumerate(suffixes[:3]):
            competitors.append(f"{domain}{suffix}")
        
        return competitors
    
    def _generate_competitor_strengths(self, name: str) -> List[str]:
        """Generate competitor strengths"""
        return [
            'Established market presence',
            'Strong brand recognition',
            'Large customer base'
        ]
    
    def _generate_competitor_weaknesses(self, name: str) -> List[str]:
        """Generate competitor weaknesses"""
        return [
            'Legacy technology stack',
            'Higher pricing',
            'Limited innovation'
        ]
    
    def _generate_swot(
        self,
        idea: Dict[str, Any],
        market_data: Dict[str, Any],
        competitors: List[Dict[str, Any]]
    ) -> Dict[str, List[str]]:
        """Generate SWOT analysis"""
        title = idea['title']
        domain = title.split()[0].lower()
        
        swot = {
            'strengths': [
                'AI-powered technology advantage',
                'Modern, scalable architecture',
                'Focus on user experience',
                'Agile development approach'
            ],
            'weaknesses': [
                'New market entrant',
                'Limited brand awareness',
                'Need to build customer trust',
                'Resource constraints'
            ],
            'opportunities': [
                f"Growing {domain} market with {market_data['growth_rate']}",
                'Increasing demand for digital solutions',
                'Gaps in competitor offerings',
                'Potential for strategic partnerships'
            ],
            'threats': [
                'Established competitors with market share',
                'Rapid technology changes',
                'Regulatory challenges',
                'Economic uncertainty'
            ]
        }
        
        return swot
    
    def _calculate_market_score(
        self,
        market_data: Dict[str, Any],
        competitors: List[Dict[str, Any]]
    ) -> float:
        """Calculate overall market strength score (0-1)"""
        # Parse TAM value using number parser
        tam_value = parse_market_number(market_data.get('tam', '3.2B'))
        
        # Parse growth rate using percentage parser
        growth_value = parse_percentage(market_data.get('growth_rate', '15%'))
        
        # Score based on market size (normalized to 0-1)
        size_score = min(1.0, tam_value / 10.0)  # 10B+ = 1.0
        
        # Score based on growth rate (normalized to 0-1)
        growth_score = min(1.0, growth_value / 25.0)  # 25%+ = 1.0
        
        # Score based on competition (fewer competitors = higher score)
        competition_score = max(0.3, 1.0 - (len(competitors) * 0.15))
        
        # Weighted average
        market_score = (size_score * 0.4 + growth_score * 0.4 + competition_score * 0.2)
        
        return round(market_score, 2)
