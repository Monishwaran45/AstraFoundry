"""Unit tests for orchestrator"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.orchestrator import Orchestrator


class TestOrchestrator:
    """Test Orchestrator class"""
    
    def test_initialization(self):
        """Test orchestrator initialization"""
        orch = Orchestrator()
        
        assert orch.agents is not None
        assert 'idea_agent' in orch.agents
        assert 'research_agent' in orch.agents
        assert 'product_agent' in orch.agents
        assert 'roadmap_agent' in orch.agents
        assert 'finance_agent' in orch.agents
        assert 'pitch_agent' in orch.agents
    
    def test_fallback_data_exists(self):
        """Test fallback data for all agents"""
        orch = Orchestrator()
        
        agents = ['research_agent', 'product_agent', 'roadmap_agent', 
                  'finance_agent', 'pitch_agent']
        
        for agent_name in agents:
            fallback = orch._get_fallback_data(agent_name)
            assert fallback is not None
            assert isinstance(fallback, dict)
    
    def test_content_validation_empty(self):
        """Test content validation with empty outputs"""
        orch = Orchestrator()
        
        agent_outputs = {
            'research_agent': {
                'status': 'success',
                'data': {}
            }
        }
        
        issues = orch._validate_content_completeness(agent_outputs)
        assert len(issues) > 0
        assert any('TAM' in issue for issue in issues)
    
    def test_content_validation_complete(self):
        """Test content validation with complete outputs"""
        orch = Orchestrator()
        
        agent_outputs = {
            'research_agent': {
                'status': 'success',
                'data': {
                    'market': {'tam': '3.2B USD'},
                    'competitors': [{'name': 'Competitor 1'}]
                }
            },
            'product_agent': {
                'status': 'success',
                'data': {
                    'personas': [{'name': 'P1'}, {'name': 'P2'}],
                    'features': [{'name': f'F{i}'} for i in range(10)]
                }
            },
            'roadmap_agent': {
                'status': 'success',
                'data': {
                    'milestones': {
                        '30_day': {},
                        '60_day': {},
                        '90_day': {}
                    }
                }
            },
            'finance_agent': {
                'status': 'success',
                'data': {
                    'projections': {'base': {}},
                    'unit_economics': {'cac': 7000}
                }
            },
            'pitch_agent': {
                'status': 'success',
                'data': {
                    'slides': [{'slide_number': i} for i in range(1, 11)]
                }
            }
        }
        
        issues = orch._validate_content_completeness(agent_outputs)
        assert len(issues) == 0
    
    def test_content_validation_pitch_incomplete(self):
        """Test content validation with incomplete pitch"""
        orch = Orchestrator()
        
        agent_outputs = {
            'pitch_agent': {
                'status': 'success',
                'data': {
                    'slides': [{'slide_number': i} for i in range(1, 6)]  # Only 5 slides
                }
            }
        }
        
        issues = orch._validate_content_completeness(agent_outputs)
        assert len(issues) > 0
        assert any('5/10 slides' in issue for issue in issues)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
