#!/usr/bin/env python3
"""
Voice Agent Platform - Initialization Script

This script initializes the database and creates sample agents.
Run this after installing dependencies and configuring .env
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from database import init_db, get_db_session, create_agent
from agent_system import create_template_agent, get_available_templates


def main():
    """Initialize the Voice Agent Platform."""
    
    print("🎙️  Voice Agent Platform - Initialization")
    print("=" * 50)
    print()
    
    # Step 1: Initialize database
    print("📦 Step 1: Initializing database...")
    try:
        init_db()
        print("   ✅ Database initialized successfully")
    except Exception as e:
        print(f"   ❌ Error initializing database: {str(e)}")
        return False
    
    # Step 2: Check if agents already exist
    print("\n📋 Step 2: Checking for existing agents...")
    try:
        with get_db_session() as session:
            from database.models import Agent
            existing_agents = session.query(Agent).count()
            
            if existing_agents > 0:
                print(f"   ℹ️  Found {existing_agents} existing agent(s)")
                response = input("   Create sample agents anyway? (y/n): ")
                if response.lower() != 'y':
                    print("   ⏭️  Skipping sample agent creation")
                    print("\n✅ Platform is ready!")
                    return True
    except Exception as e:
        print(f"   ⚠️  Could not check existing agents: {str(e)}")
    
    # Step 3: Create sample agents from templates
    print("\n🤖 Step 3: Creating sample agents...")
    
    templates = get_available_templates()
    created_count = 0
    
    for template in templates:
        try:
            print(f"   Creating: {template['name']}...", end=" ")
            
            # Get template config
            config = create_template_agent(template['id'])
            
            # Create agent in database
            with get_db_session() as session:
                agent = create_agent(
                    session,
                    name=config["name"],
                    description=config["description"],
                    instructions=config["instructions"],
                    llm_model=config["llm_model"],
                    stt_model=config["stt_model"],
                    tts_voice=config["tts_voice"],
                    temperature=config["temperature"],
                    max_tokens=config["max_tokens"],
                    category=config["category"],
                    is_active=True,
                )
            
            print("✅")
            created_count += 1
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print(f"\n   Created {created_count} sample agent(s)")
    
    # Step 4: Summary
    print("\n" + "=" * 50)
    print("✅ Voice Agent Platform is ready!")
    print("\n📚 Next Steps:")
    print("   1. Start the platform: streamlit run app.py")
    print("   2. Access at: http://localhost:8501")
    print("\n💡 Tips:")
    print("   - Browse agents in the Marketplace")
    print("   - Create custom agents in Create Agent")
    print("   - Start conversations in Chat Interface")
    print("   - Export data in View Data")
    print()
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Initialization cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

