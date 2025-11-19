"""Main entry point for AstraFoundry - CLI interface"""

import sys
import os
import argparse
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.orchestrator import Orchestrator
from src.utils.config import get_config, ConfigurationError, validate_config
from src.utils.logger import get_logger


def print_banner():
    """Print AstraFoundry banner"""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║              ✨ AstraFoundry™ ✨                          ║
║         The Autonomous AI Startup Builder                ║
║                                                           ║
║  Generate investor-ready startup blueprints in minutes   ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def get_user_prompt(args) -> str:
    """Get user prompt from args or interactive input"""
    if args.prompt:
        return args.prompt
    
    print("\n📝 Enter your startup idea or domain:")
    print("   (e.g., 'Build a climate-tech startup for India')")
    print("   (e.g., 'Create a healthcare AI platform')")
    print()
    
    prompt = input("Your idea: ").strip()
    
    if not prompt:
        print("❌ Error: Prompt cannot be empty")
        sys.exit(1)
    
    return prompt


def save_output(blueprint, output_dir: str = "output"):
    """Save blueprint to JSON and text files"""
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_id_short = blueprint.run_id[:8]
    base_filename = f"blueprint_{timestamp}_{run_id_short}"
    
    # Save JSON
    json_path = Path(output_dir) / f"{base_filename}.json"
    with open(json_path, 'w') as f:
        f.write(blueprint.to_json())
    
    # Save text summary
    txt_path = Path(output_dir) / f"{base_filename}_summary.txt"
    with open(txt_path, 'w') as f:
        f.write("=" * 70 + "\n")
        f.write("ASTRA FOUNDRY - STARTUP BLUEPRINT\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Run ID: {blueprint.run_id}\n")
        f.write(f"Status: {blueprint.status}\n")
        f.write(f"Generated: {timestamp}\n\n")
        f.write("=" * 70 + "\n")
        f.write("SUMMARY\n")
        f.write("=" * 70 + "\n\n")
        f.write(blueprint.summary)
        f.write("\n\n")
        
        if blueprint.errors:
            f.write("=" * 70 + "\n")
            f.write("ERRORS\n")
            f.write("=" * 70 + "\n\n")
            for error in blueprint.errors:
                f.write(f"- {error}\n")
    
    return json_path, txt_path


def print_progress(message: str):
    """Print progress message"""
    print(f"⏳ {message}...")


def print_success(message: str):
    """Print success message"""
    print(f"✅ {message}")


def print_error(message: str):
    """Print error message"""
    print(f"❌ {message}")


def display_results(blueprint):
    """Display key results from blueprint"""
    print("\n" + "=" * 70)
    print("📊 BLUEPRINT RESULTS")
    print("=" * 70 + "\n")
    
    # Extract key data
    idea_data = blueprint.blueprint.get('idea', {})
    research_data = blueprint.blueprint.get('research', {})
    finance_data = blueprint.blueprint.get('finance', {})
    
    # Display idea
    if idea_data:
        ideas = idea_data.get('ideas', [])
        selected_id = idea_data.get('selected_idea', {}).get('idea_id', '')
        selected_idea = next(
            (idea for idea in ideas if idea['idea_id'] == selected_id),
            ideas[0] if ideas else {}
        )
        
        if selected_idea:
            print(f"💡 Startup Idea: {selected_idea.get('title', 'N/A')}")
            print(f"   {selected_idea.get('description', 'N/A')}\n")
    
    # Display market
    if research_data:
        market = research_data.get('market', {})
        print(f"📈 Market Size: {market.get('tam', 'N/A')}")
        print(f"   Growth Rate: {market.get('growth_rate', 'N/A')}\n")
    
    # Display financials
    if finance_data:
        projections = finance_data.get('projections', {}).get('base', {})
        runway = finance_data.get('runway_months', 0)
        
        print(f"💰 Year 1 Revenue: ${projections.get('year_1_revenue', 0):,.0f}")
        print(f"   Runway: {runway} months\n")
    
    # Display metrics
    metrics = blueprint.metrics
    if metrics:
        total_duration = metrics.get('total_duration_ms', 0) / 1000
        print(f"⚡ Execution Time: {total_duration:.1f} seconds")
        print(f"   Status: {blueprint.status.upper()}\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='AstraFoundry - Generate startup blueprints with AI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/main.py --prompt "Build a climate-tech startup for India"
  python src/main.py --user-id john_doe
  python src/main.py --output my_blueprints/
        """
    )
    
    parser.add_argument(
        '--prompt',
        type=str,
        help='Startup idea or domain prompt'
    )
    
    parser.add_argument(
        '--user-id',
        type=str,
        default='default_user',
        help='User ID for memory personalization (default: default_user)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='output',
        help='Output directory for blueprint files (default: output/)'
    )
    
    parser.add_argument(
        '--timeout',
        type=int,
        help='Pipeline timeout in seconds (default: 300)'
    )
    
    parser.add_argument(
        '--no-banner',
        action='store_true',
        help='Skip banner display'
    )
    
    args = parser.parse_args()
    
    # Print banner
    if not args.no_banner:
        print_banner()
    
    try:
        # Validate configuration
        print_progress("Validating configuration")
        
        if not validate_config():
            print_error("Configuration validation failed")
            print("\n💡 Make sure you have:")
            print("   1. Created a .env file (copy from .env.example)")
            print("   2. Set GOOGLE_API_KEY in your .env file")
            print("   3. Optionally set Google Search API credentials")
            sys.exit(1)
        
        config = get_config()
        print_success("Configuration validated")
        
        # Get user prompt
        user_prompt = get_user_prompt(args)
        print(f"\n🎯 Generating blueprint for: '{user_prompt}'")
        print(f"👤 User ID: {args.user_id}\n")
        
        # Initialize orchestrator
        print_progress("Initializing AstraFoundry")
        orchestrator = Orchestrator()
        print_success("Orchestrator ready")
        
        # Execute pipeline
        print("\n" + "=" * 70)
        print("🚀 EXECUTING MULTI-AGENT PIPELINE")
        print("=" * 70 + "\n")
        
        print_progress("Agent 1/6: Generating startup ideas")
        print_progress("Agent 2/6: Researching market and competitors")
        print_progress("Agent 3/6: Designing product and features")
        print_progress("Agent 4/6: Creating engineering roadmap")
        print_progress("Agent 5/6: Building financial model")
        print_progress("Agent 6/6: Generating pitch deck")
        
        blueprint = orchestrator.execute_pipeline(
            user_prompt=user_prompt,
            user_id=args.user_id,
            timeout_seconds=args.timeout
        )
        
        print_success("Pipeline execution complete!")
        
        # Display results
        display_results(blueprint)
        
        # Save output
        print_progress("Saving blueprint files")
        json_path, txt_path = save_output(blueprint, args.output)
        
        print_success(f"JSON saved to: {json_path}")
        print_success(f"Summary saved to: {txt_path}")
        
        # Final message
        print("\n" + "=" * 70)
        if blueprint.status == 'success':
            print("🎉 SUCCESS! Your startup blueprint is ready.")
        elif blueprint.status == 'partial':
            print("⚠️  PARTIAL SUCCESS. Some agents failed but results are available.")
        else:
            print("❌ FAILED. Check the error messages above.")
        print("=" * 70 + "\n")
        
        # Exit with appropriate code
        sys.exit(0 if blueprint.status == 'success' else 1)
    
    except ConfigurationError as e:
        print_error(f"Configuration error: {str(e)}")
        sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(130)
    
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
