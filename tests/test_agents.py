"""Unit tests for agent implementations"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.product_agent import ProductDesignerAgent
from src.agents.roadmap_agent import RoadmapAgent
from src.agents.finance_agent import FinanceAgent
from src.agents.pitch_agent import PitchDeckAgent
from src.tools.code_execution_adapter import CodeExecutionAdapter


@pytest.fixture
def mock_context():
    """Create mock context with idea agent output"""
    return {
        'user_prompt': 'AI-powered climate tech solution',
        'user_id': 'test_user',
        'run_id': 'test_run_123',
        'agent_outputs': {
            'idea_agent': {
                'agent_name': 'idea_agent',
                'status': 'success',
                'data': {
                    'ideas': [
                        {
                            'idea_id': 'idea_001',
                            'title': 'Climate-Tech AI Platform',
                            'description': 'AI-powered platform for carbon tracking',
                            'score': 0.85
                        }
                    ],
                    'selected_idea': {'idea_id': 'idea_001'}
                }
            }
        }
    }


class TestProductAgent:
    """Test ProductDesignerAgent"""
    
    def test_execute_success(self, mock_context):
        """Test successful execution"""
        agent = ProductDesignerAgent()
        output = agent.execute(mock_context)
        
        assert output.status == 'success'
        assert output.agent_name == 'product_agent'
        assert 'personas' in output.data
        assert 'features' in output.data
        assert 'mvp_scope' in output.data
    
    def test_generates_personas(self, mock_context):
        """Test persona generation"""
        agent = ProductDesignerAgent()
        output = agent.execute(mock_context)
        
        personas = output.data['personas']
        assert len(personas) >= 2
        assert all('name' in p for p in personas)
        assert all('demographics' in p for p in personas)
        assert all('pain_points' in p for p in personas)
    
    def test_generates_features(self, mock_context):
        """Test feature generation"""
        agent = ProductDesignerAgent()
        output = agent.execute(mock_context)
        
        features = output.data['features']
        assert len(features) >= 5
        assert all('feature_id' in f for f in features)
        assert all('name' in f for f in features)
        assert all('rice_score' in f for f in features)
        assert all('priority' in f for f in features)
    
    def test_rice_scoring(self, mock_context):
        """Test RICE scoring"""
        agent = ProductDesignerAgent()
        output = agent.execute(mock_context)
        
        features = output.data['features']
        for feature in features:
            rice = feature['rice_score']
            assert 'reach' in rice
            assert 'impact' in rice
            assert 'confidence' in rice
            assert 'effort' in rice
            assert 'total' in rice
            assert rice['total'] > 0
    
    def test_mvp_scope(self, mock_context):
        """Test MVP scope definition"""
        agent = ProductDesignerAgent()
        output = agent.execute(mock_context)
        
        mvp = output.data['mvp_scope']
        assert 'features' in mvp
        assert 'timeline' in mvp
        assert len(mvp['features']) >= 5
        assert len(mvp['features']) <= 7


class TestRoadmapAgent:
    """Test RoadmapAgent"""
    
    def test_execute_success(self, mock_context):
        """Test successful execution"""
        # Add product output
        mock_context['agent_outputs']['product_agent'] = {
            'agent_name': 'product_agent',
            'status': 'success',
            'data': {
                'mvp_scope': {
                    'feature_details': [
                        {'name': 'Feature 1', 'priority': 'high'},
                        {'name': 'Feature 2', 'priority': 'high'}
                    ]
                }
            }
        }
        
        agent = RoadmapAgent()
        output = agent.execute(mock_context)
        
        assert output.status == 'success'
        assert 'architecture' in output.data
        assert 'milestones' in output.data
    
    def test_architecture_components(self, mock_context):
        """Test architecture generation"""
        mock_context['agent_outputs']['product_agent'] = {
            'agent_name': 'product_agent',
            'status': 'success',
            'data': {'mvp_scope': {'feature_details': []}}
        }
        
        agent = RoadmapAgent()
        output = agent.execute(mock_context)
        
        arch = output.data['architecture']
        assert 'components' in arch
        assert 'tech_stack' in arch
        assert 'infrastructure' in arch
        assert len(arch['components']) > 0
    
    def test_milestone_phases(self, mock_context):
        """Test milestone generation"""
        mock_context['agent_outputs']['product_agent'] = {
            'agent_name': 'product_agent',
            'status': 'success',
            'data': {'mvp_scope': {'feature_details': []}}
        }
        
        agent = RoadmapAgent()
        output = agent.execute(mock_context)
        
        milestones = output.data['milestones']
        assert '30_day' in milestones
        assert '60_day' in milestones
        assert '90_day' in milestones
        
        for phase in ['30_day', '60_day', '90_day']:
            assert 'deliverables' in milestones[phase]
            assert 'dependencies' in milestones[phase]
            assert 'risks' in milestones[phase]


class TestFinanceAgent:
    """Test FinanceAgent"""
    
    def test_execute_success(self, mock_context):
        """Test successful execution"""
        code_executor = CodeExecutionAdapter()
        agent = FinanceAgent(code_executor)
        output = agent.execute(mock_context)
        
        assert output.status == 'success'
        assert 'assumptions' in output.data
        assert 'costs' in output.data
        assert 'unit_economics' in output.data
        assert 'projections' in output.data
    
    def test_unit_economics(self, mock_context):
        """Test unit economics calculation"""
        code_executor = CodeExecutionAdapter()
        agent = FinanceAgent(code_executor)
        output = agent.execute(mock_context)
        
        unit_econ = output.data['unit_economics']
        assert 'cac' in unit_econ
        assert 'ltv' in unit_econ
        assert 'ltv_cac_ratio' in unit_econ
        assert 'payback_period_months' in unit_econ
        assert unit_econ['cac'] > 0
        assert unit_econ['ltv'] > 0
    
    def test_projections(self, mock_context):
        """Test revenue projections"""
        code_executor = CodeExecutionAdapter()
        agent = FinanceAgent(code_executor)
        output = agent.execute(mock_context)
        
        projections = output.data['projections']
        assert 'conservative' in projections
        assert 'base' in projections
        assert 'optimistic' in projections
        
        for scenario in ['conservative', 'base', 'optimistic']:
            assert 'year_1_revenue' in projections[scenario]
            assert 'year_2_revenue' in projections[scenario]
            assert 'year_3_revenue' in projections[scenario]


class TestPitchAgent:
    """Test PitchDeckAgent"""
    
    def test_execute_success(self, mock_context):
        """Test successful execution"""
        agent = PitchDeckAgent()
        output = agent.execute(mock_context)
        
        assert output.status == 'success'
        assert 'slides' in output.data
    
    def test_generates_10_slides(self, mock_context):
        """Test 10 slides generation"""
        agent = PitchDeckAgent()
        output = agent.execute(mock_context)
        
        slides = output.data['slides']
        assert len(slides) == 10
    
    def test_slide_structure(self, mock_context):
        """Test slide structure"""
        agent = PitchDeckAgent()
        output = agent.execute(mock_context)
        
        slides = output.data['slides']
        for slide in slides:
            assert 'slide_number' in slide
            assert 'title' in slide
            assert 'content' in slide
            assert 'talking_points' in slide
            assert 'visual_suggestions' in slide
    
    def test_handles_missing_data(self, mock_context):
        """Test handling of missing upstream data"""
        # Don't add research/product/etc outputs
        agent = PitchDeckAgent()
        output = agent.execute(mock_context)
        
        # Should still generate 10 slides with fallback data
        assert output.status == 'success'
        assert len(output.data['slides']) == 10


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
