"""Unit tests for number parser utility"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.number_parser import parse_market_number, parse_percentage, safe_float


class TestParseMarketNumber:
    """Test parse_market_number function"""
    
    def test_billions(self):
        """Test parsing billions"""
        assert parse_market_number('3.2B') == 3.2
        assert parse_market_number('5.0B') == 5.0
        assert parse_market_number('10B') == 10.0
    
    def test_millions(self):
        """Test parsing millions"""
        assert parse_market_number('450M') == 450.0
        assert parse_market_number('1.5M') == 1.5
        assert parse_market_number('100M') == 100.0
    
    def test_thousands(self):
        """Test parsing thousands"""
        assert parse_market_number('22K') == 22.0
        assert parse_market_number('500K') == 500.0
        assert parse_market_number('1.2K') == 1.2
    
    def test_with_currency_symbols(self):
        """Test parsing with currency symbols"""
        assert parse_market_number('$5.2B') == 5.2
        assert parse_market_number('€1.4B') == 1.4
        assert parse_market_number('USD 430M') == 430.0
        assert parse_market_number('EUR 2.5B') == 2.5
    
    def test_with_usd_suffix(self):
        """Test parsing with USD suffix"""
        assert parse_market_number('3.2B USD') == 3.2
        assert parse_market_number('450M USD') == 450.0
    
    def test_edge_cases(self):
        """Test edge cases"""
        assert parse_market_number('N/A') == 0.0
        assert parse_market_number('') == 0.0
        assert parse_market_number(None) == 0.0
        assert parse_market_number('invalid') == 0.0
    
    def test_plain_numbers(self):
        """Test plain numbers without suffix"""
        assert parse_market_number('3.2') == 3.2
        assert parse_market_number('100') == 100.0


class TestParsePercentage:
    """Test parse_percentage function"""
    
    def test_basic_percentage(self):
        """Test basic percentage parsing"""
        assert parse_percentage('15%') == 15.0
        assert parse_percentage('18%') == 18.0
        assert parse_percentage('22.5%') == 22.5
    
    def test_with_cagr(self):
        """Test percentage with CAGR"""
        assert parse_percentage('18% CAGR') == 18.0
        assert parse_percentage('15% cagr') == 15.0
    
    def test_without_percent_sign(self):
        """Test numbers without percent sign"""
        assert parse_percentage('15') == 15.0
        assert parse_percentage('22.5') == 22.5
    
    def test_edge_cases(self):
        """Test edge cases"""
        assert parse_percentage('') == 0.0
        assert parse_percentage(None) == 0.0
        assert parse_percentage('N/A') == 0.0


class TestSafeFloat:
    """Test safe_float function"""
    
    def test_numeric_types(self):
        """Test with numeric types"""
        assert safe_float(3.2) == 3.2
        assert safe_float(5) == 5.0
        assert safe_float(10.5) == 10.5
    
    def test_string_conversion(self):
        """Test string conversion"""
        assert safe_float('3.2B') == 3.2
        assert safe_float('450M') == 450.0
        assert safe_float('15%') == 15.0
    
    def test_with_default(self):
        """Test default value"""
        assert safe_float(None, default=10.0) == 10.0
        assert safe_float('invalid', default=5.0) == 0.0  # Uses parser, returns 0
        assert safe_float([], default=7.0) == 7.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
