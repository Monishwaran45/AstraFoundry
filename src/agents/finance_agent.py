"""Finance Agent - Creates financial models and projections"""

from typing import Dict, Any
from src.agents.base_agent import BaseAgent
from src.models import AgentOutput
from src.tools.code_execution_adapter import CodeExecutionAdapter


class FinanceAgent(BaseAgent):
    """Agent responsible for financial modeling and projections"""
    
    def __init__(self, code_executor: CodeExecutionAdapter):
        super().__init__('finance_agent')
        self.code_executor = code_executor
    
    def execute(self, context: Dict[str, Any]) -> AgentOutput:
        """
        Create financial model with costs, unit economics, and projections
        
        Args:
            context: Contains outputs from all previous agents
        
        Returns:
            AgentOutput with financial data
        """
        try:
            # Get previous outputs
            idea_output = self._get_agent_output(context, 'idea_agent')
            research_output = self._get_agent_output(context, 'research_agent')
            product_output = self._get_agent_output(context, 'product_agent')
            roadmap_output = self._get_agent_output(context, 'roadmap_agent')
            
            if not idea_output:
                raise ValueError("Missing required idea_agent output")
            
            selected_idea = self._get_selected_idea(idea_output)
            
            # Use research data if available, otherwise use defaults
            if research_output and 'data' in research_output and 'market' in research_output['data']:
                market_data = research_output['data']['market']
            else:
                market_data = {'tam': '3.2B USD', 'growth_rate': '15% CAGR'}
            
            # Generate financial components
            assumptions = self._generate_assumptions(selected_idea, market_data)
            costs = self._calculate_costs(assumptions)
            unit_economics = self._calculate_unit_economics(assumptions)
            projections = self._generate_projections(assumptions, unit_economics)
            runway = self._calculate_runway(assumptions, costs)
            
            output_data = {
                'assumptions': assumptions,
                'costs': costs,
                'unit_economics': unit_economics,
                'projections': projections,
                'runway_months': runway
            }
            
            return AgentOutput(
                agent_name=self.agent_name,
                execution_time_ms=0,
                status='success',
                data=output_data
            )
        
        except Exception as e:
            self.logger.error(f"Finance agent failed: {str(e)}")
            raise
    
    def _get_selected_idea(self, idea_output: Dict[str, Any]) -> Dict[str, Any]:
        """Extract selected idea"""
        selected_id = idea_output['data']['selected_idea']['idea_id']
        ideas = idea_output['data']['ideas']
        return next(idea for idea in ideas if idea['idea_id'] == selected_id)
    
    def _generate_assumptions(
        self,
        idea: Dict[str, Any],
        market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate financial assumptions based on industry and product"""
        # Parse TAM to determine market size category
        tam_str = market_data['tam'].split()[0]
        tam_value = float(tam_str.replace('B', ''))
        
        # Determine pricing model based on idea type
        title_lower = idea['title'].lower()
        if 'marketplace' in title_lower:
            pricing_model = 'Transaction fee (3-5%)'
        elif 'analytics' in title_lower or 'intelligence' in title_lower:
            pricing_model = 'SaaS subscription ($99-$999/month per user)'
        else:
            pricing_model = 'SaaS subscription ($199-$1999/month per organization)'
        
        return {
            'initial_capital': 500000,  # $500K seed funding
            'team_size': 8,  # Initial team
            'avg_salary': 120000,  # Average annual salary
            'pricing_model': pricing_model,
            'target_customers_year1': 50,
            'target_customers_year2': 200,
            'target_customers_year3': 500,
            'avg_contract_value': 12000  # Annual contract value
        }
    
    def _calculate_costs(self, assumptions: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate operational and capital expenses using code execution"""
        # Use code execution for precise calculations
        code = f"""
# Calculate monthly operational expenses
team_size = {assumptions['team_size']}
avg_salary = {assumptions['avg_salary']}
monthly_salaries = (team_size * avg_salary) / 12

# Other operational costs
office_rent = 5000  # Monthly
software_licenses = 3000  # Monthly
marketing = 15000  # Monthly
cloud_infrastructure = 5000  # Monthly
misc_expenses = 5000  # Monthly

opex_monthly = monthly_salaries + office_rent + software_licenses + marketing + cloud_infrastructure + misc_expenses

# Capital expenses (one-time)
equipment = 50000
legal_incorporation = 10000
initial_marketing = 30000
software_development = 100000

capex_initial = equipment + legal_incorporation + initial_marketing + software_development

result = {{
    'opex_monthly': round(opex_monthly, 2),
    'capex_initial': round(capex_initial, 2),
    'monthly_salaries': round(monthly_salaries, 2),
    'monthly_other': round(opex_monthly - monthly_salaries, 2)
}}
"""
        
        exec_result = self.code_executor.execute(code)
        
        if exec_result['error']:
            self.logger.error(f"Cost calculation failed: {exec_result['error']}")
            # Fallback to manual calculation
            monthly_salaries = (assumptions['team_size'] * assumptions['avg_salary']) / 12
            opex_monthly = monthly_salaries + 33000  # Other costs
            capex_initial = 190000
            
            result_data = {
                'opex_monthly': round(opex_monthly, 2),
                'capex_initial': round(capex_initial, 2),
                'monthly_salaries': round(monthly_salaries, 2),
                'monthly_other': 33000
            }
        else:
            result_data = exec_result['variables']['result']
        
        return {
            'opex_monthly': result_data['opex_monthly'],
            'capex_initial': result_data['capex_initial'],
            'breakdown': {
                'salaries': result_data['monthly_salaries'],
                'office': 5000,
                'software': 3000,
                'marketing': 15000,
                'infrastructure': 5000,
                'misc': 5000
            }
        }
    
    def _calculate_unit_economics(
        self,
        assumptions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate CAC, LTV, and related metrics"""
        code = f"""
# Customer Acquisition Cost (CAC)
monthly_marketing = 15000
monthly_sales_salaries = 20000  # 2 sales people
total_acquisition_cost = monthly_marketing + monthly_sales_salaries
customers_acquired_per_month = 5  # Conservative estimate
cac = total_acquisition_cost / customers_acquired_per_month

# Lifetime Value (LTV)
avg_contract_value = {assumptions['avg_contract_value']}
avg_customer_lifetime_years = 3  # Average retention
gross_margin = 0.80  # 80% gross margin
ltv = avg_contract_value * avg_customer_lifetime_years * gross_margin

# Metrics
ltv_cac_ratio = ltv / cac
payback_period_months = (cac / (avg_contract_value / 12))

result = {{
    'cac': round(cac, 2),
    'ltv': round(ltv, 2),
    'ltv_cac_ratio': round(ltv_cac_ratio, 2),
    'payback_period_months': round(payback_period_months, 1)
}}
"""
        
        exec_result = self.code_executor.execute(code)
        
        if exec_result['error']:
            self.logger.error(f"Unit economics calculation failed: {exec_result['error']}")
            # Fallback
            result_data = {
                'cac': 7000,
                'ltv': 28800,
                'ltv_cac_ratio': 4.11,
                'payback_period_months': 7.0
            }
        else:
            result_data = exec_result['variables']['result']
        
        return result_data
    
    def _generate_projections(
        self,
        assumptions: Dict[str, Any],
        unit_economics: Dict[str, Any]
    ) -> Dict[str, Dict[str, float]]:
        """Generate revenue projections for 3 scenarios"""
        acv = assumptions['avg_contract_value']
        
        scenarios = {
            'conservative': {
                'year_1_customers': assumptions['target_customers_year1'] * 0.7,
                'year_2_customers': assumptions['target_customers_year2'] * 0.7,
                'year_3_customers': assumptions['target_customers_year3'] * 0.7
            },
            'base': {
                'year_1_customers': assumptions['target_customers_year1'],
                'year_2_customers': assumptions['target_customers_year2'],
                'year_3_customers': assumptions['target_customers_year3']
            },
            'optimistic': {
                'year_1_customers': assumptions['target_customers_year1'] * 1.5,
                'year_2_customers': assumptions['target_customers_year2'] * 1.5,
                'year_3_customers': assumptions['target_customers_year3'] * 1.5
            }
        }
        
        projections = {}
        
        for scenario_name, scenario_data in scenarios.items():
            code = f"""
acv = {acv}
year_1_customers = {scenario_data['year_1_customers']}
year_2_customers = {scenario_data['year_2_customers']}
year_3_customers = {scenario_data['year_3_customers']}

year_1_revenue = year_1_customers * acv
year_2_revenue = year_2_customers * acv
year_3_revenue = year_3_customers * acv

result = {{
    'year_1_revenue': round(year_1_revenue, 2),
    'year_2_revenue': round(year_2_revenue, 2),
    'year_3_revenue': round(year_3_revenue, 2)
}}
"""
            
            exec_result = self.code_executor.execute(code)
            
            if exec_result['error']:
                # Fallback calculation
                projections[scenario_name] = {
                    'year_1_revenue': round(scenario_data['year_1_customers'] * acv, 2),
                    'year_2_revenue': round(scenario_data['year_2_customers'] * acv, 2),
                    'year_3_revenue': round(scenario_data['year_3_customers'] * acv, 2)
                }
            else:
                projections[scenario_name] = exec_result['variables']['result']
        
        return projections
    
    def _calculate_runway(
        self,
        assumptions: Dict[str, Any],
        costs: Dict[str, Any]
    ) -> int:
        """Calculate runway in months"""
        code = f"""
initial_capital = {assumptions['initial_capital']}
capex = {costs['capex_initial']}
monthly_burn = {costs['opex_monthly']}

remaining_capital = initial_capital - capex
runway_months = remaining_capital / monthly_burn

result = int(runway_months)
"""
        
        exec_result = self.code_executor.execute(code)
        
        if exec_result['error']:
            # Fallback
            remaining = assumptions['initial_capital'] - costs['capex_initial']
            runway = int(remaining / costs['opex_monthly'])
        else:
            runway = exec_result['variables']['result']
        
        return runway
