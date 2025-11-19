"""Idea Agent - Generates and scores startup ideas"""

from typing import Dict, Any, List
from src.agents.base_agent import BaseAgent
from src.models import AgentOutput
from src.tools.google_search_adapter import GoogleSearchAdapter


class IdeaAgent(BaseAgent):
    """Agent responsible for generating and scoring startup ideas"""
    
    def __init__(self, search_tool: GoogleSearchAdapter):
        super().__init__('idea_agent')
        self.search_tool = search_tool
    
    def execute(self, context: Dict[str, Any]) -> AgentOutput:
        """
        Generate 3-5 startup ideas, score them, and select the best one
        
        Args:
            context: Contains 'user_prompt' and optional 'user_preferences'
        
        Returns:
            AgentOutput with ideas and selected idea
        """
        user_prompt = self._get_from_context(context, 'user_prompt', '')
        user_preferences = self._get_from_context(context, 'user_preferences', {})
        
        # Generate ideas
        ideas = self._generate_ideas(user_prompt, user_preferences)
        
        # Score and validate each idea
        for idea in ideas:
            self._score_idea(idea, user_prompt)
            self._validate_with_search(idea)
        
        # Select best idea
        selected_idea = self._select_best_idea(ideas)
        
        # Calculate overall quality score
        quality_score = selected_idea['scores']['novelty'] * 0.4 + \
                       selected_idea['scores']['feasibility'] * 0.3 + \
                       selected_idea['scores']['market_fit'] * 0.3
        
        output_data = {
            'ideas': ideas,
            'selected_idea': {
                'idea_id': selected_idea['idea_id'],
                'rationale': self._generate_selection_rationale(selected_idea)
            }
        }
        
        return AgentOutput(
            agent_name=self.agent_name,
            execution_time_ms=0,  # Will be set by base class
            status='success',
            data=output_data,
            scores={'idea_quality': quality_score}
        )
    
    def _generate_ideas(
        self,
        user_prompt: str,
        user_preferences: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate 3-5 diverse startup ideas based on prompt"""
        # In production, this would use Gemini API
        # For now, generating structured ideas based on prompt
        
        ideas = []
        num_ideas = 4  # Generate 4 ideas
        
        # Parse domain from prompt
        domain = self._extract_domain(user_prompt)
        
        # Generate diverse ideas
        idea_templates = [
            {
                'suffix': 'Analytics Platform',
                'description': f'AI-powered analytics platform for {domain} that provides real-time insights and predictive modeling',
                'novelty_base': 0.75,
                'feasibility_base': 0.80,
                'market_fit_base': 0.70
            },
            {
                'suffix': 'Marketplace',
                'description': f'Two-sided marketplace connecting {domain} providers with customers, featuring smart matching algorithms',
                'novelty_base': 0.65,
                'feasibility_base': 0.85,
                'market_fit_base': 0.75
            },
            {
                'suffix': 'Automation Suite',
                'description': f'Comprehensive automation suite for {domain} operations, reducing manual work by 70%',
                'novelty_base': 0.70,
                'feasibility_base': 0.75,
                'market_fit_base': 0.80
            },
            {
                'suffix': 'Intelligence Network',
                'description': f'Collaborative intelligence network for {domain} professionals to share insights and best practices',
                'novelty_base': 0.80,
                'feasibility_base': 0.70,
                'market_fit_base': 0.65
            }
        ]
        
        for i, template in enumerate(idea_templates[:num_ideas]):
            idea = {
                'idea_id': f'idea_{i+1:03d}',
                'title': f'{domain.title()} {template["suffix"]}',
                'description': template['description'],
                'scores': {
                    'novelty': template['novelty_base'],
                    'feasibility': template['feasibility_base'],
                    'market_fit': template['market_fit_base']
                },
                'evidence': []
            }
            ideas.append(idea)
        
        return ideas
    
    def _extract_domain(self, prompt: str) -> str:
        """Extract domain/industry from user prompt"""
        prompt_lower = prompt.lower()
        
        # Common domain keywords
        domains = {
            'climate': 'climate-tech',
            'health': 'healthcare',
            'finance': 'fintech',
            'education': 'edtech',
            'agriculture': 'agtech',
            'real estate': 'proptech',
            'logistics': 'logistics',
            'energy': 'energy',
            'retail': 'retail-tech',
            'manufacturing': 'manufacturing'
        }
        
        for keyword, domain in domains.items():
            if keyword in prompt_lower:
                return domain
        
        return 'technology'
    
    def _score_idea(self, idea: Dict[str, Any], user_prompt: str) -> None:
        """Score an idea on novelty, feasibility, and market fit"""
        # Scores are already set in _generate_ideas
        # This method can be extended to adjust scores based on additional factors
        
        # Add small random variation to make ideas more distinct
        import random
        for key in idea['scores']:
            variation = random.uniform(-0.05, 0.05)
            idea['scores'][key] = max(0.0, min(1.0, idea['scores'][key] + variation))
    
    def _validate_with_search(self, idea: Dict[str, Any]) -> None:
        """Use Google Search to validate trend relevance"""
        try:
            # Search for market trends related to the idea
            query = f"{idea['title']} market trends 2024 2025"
            results = self.search_tool.search(query, num_results=3)
            
            # Add search results as evidence
            for result in results:
                idea['evidence'].append({
                    'source': 'search',
                    'url': result['url'],
                    'snippet': result['snippet']
                })
            
            # Adjust market_fit score based on search results
            if len(results) > 0:
                # Boost market_fit slightly if we found relevant results
                idea['scores']['market_fit'] = min(1.0, idea['scores']['market_fit'] + 0.05)
        
        except Exception as e:
            self.logger.warning(f"Search validation failed for {idea['idea_id']}: {str(e)}")
    
    def _select_best_idea(self, ideas: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Select the highest-scoring idea using weighted formula"""
        best_idea = None
        best_score = -1
        
        for idea in ideas:
            # Weighted formula: 0.4*novelty + 0.3*feasibility + 0.3*market_fit
            score = (
                idea['scores']['novelty'] * 0.4 +
                idea['scores']['feasibility'] * 0.3 +
                idea['scores']['market_fit'] * 0.3
            )
            
            if score > best_score:
                best_score = score
                best_idea = idea
        
        return best_idea
    
    def _generate_selection_rationale(self, idea: Dict[str, Any]) -> str:
        """Generate rationale for why this idea was selected"""
        scores = idea['scores']
        
        strengths = []
        if scores['novelty'] > 0.75:
            strengths.append('high novelty')
        if scores['feasibility'] > 0.75:
            strengths.append('strong feasibility')
        if scores['market_fit'] > 0.75:
            strengths.append('excellent market fit')
        
        if not strengths:
            strengths.append('balanced scores across all dimensions')
        
        return f"Selected for {' and '.join(strengths)}. " \
               f"Novelty: {scores['novelty']:.2f}, " \
               f"Feasibility: {scores['feasibility']:.2f}, " \
               f"Market Fit: {scores['market_fit']:.2f}"
