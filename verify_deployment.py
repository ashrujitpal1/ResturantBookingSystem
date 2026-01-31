#!/usr/bin/env python3
"""Pre-deployment verification for modular architecture."""
import sys
from pathlib import Path

def check_files():
    """Verify all required files exist."""
    print("🔍 Checking required files...")
    
    required_files = [
        "src/workflows/restaurant_workflow.py",
        "src/agents/restaurant_finder.py",
        "src/agents/booking_agent.py",
        "src/agents/memory_agent.py",
        "src/tools/restaurant_tools.py",
        "src/tools/user_tools.py",
        "src/tools/booking_tools.py",
        "src/utils/llm_providers.py",
        "src/utils/circuit_breaker.py",
        "src/utils/cost_tracker.py",
        "src/config/models.py",
        ".bedrock_agentcore.yaml",
        "Dockerfile",
        "requirements.txt"
    ]
    
    missing = []
    for file in required_files:
        if not Path(file).exists():
            missing.append(file)
            print(f"  ❌ Missing: {file}")
        else:
            print(f"  ✅ Found: {file}")
    
    if missing:
        print(f"\n❌ {len(missing)} files missing!")
        return False
    
    print(f"\n✅ All {len(required_files)} required files found!")
    return True


def check_config():
    """Verify configuration files are updated."""
    print("\n🔍 Checking configuration files...")
    
    # Check .bedrock_agentcore.yaml
    with open(".bedrock_agentcore.yaml") as f:
        content = f.read()
        if "src/workflows/restaurant_workflow.py" in content:
            print("  ✅ .bedrock_agentcore.yaml: Updated entrypoint")
        else:
            print("  ❌ .bedrock_agentcore.yaml: Old entrypoint still present")
            return False
    
    # Check Dockerfile
    with open("Dockerfile") as f:
        content = f.read()
        if "src.workflows.restaurant_workflow" in content:
            print("  ✅ Dockerfile: Updated CMD")
        else:
            print("  ❌ Dockerfile: Old CMD still present")
            return False
    
    print("\n✅ Configuration files updated correctly!")
    return True


def check_imports():
    """Test that imports work."""
    print("\n🔍 Testing imports...")
    
    try:
        sys.path.insert(0, str(Path.cwd()))
        
        from src.config.models import RestaurantBookingState
        print("  ✅ Config imports work")
        
        from src.utils.llm_providers import get_llm_provider
        print("  ✅ Utils imports work")
        
        from src.tools.restaurant_tools import fetch_restaurants_tool
        print("  ✅ Tools imports work")
        
        from src.agents.restaurant_finder import restaurant_finder_node
        print("  ✅ Agent imports work")
        
        from src.workflows.restaurant_workflow import create_restaurant_booking_workflow
        print("  ✅ Workflow imports work")
        
        print("\n✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Import error: {e}")
        return False


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("Pre-Deployment Verification - Modular Architecture")
    print("=" * 60)
    
    checks = [
        ("Files", check_files),
        ("Configuration", check_config),
        ("Imports", check_imports)
    ]
    
    results = []
    for name, check_fn in checks:
        try:
            result = check_fn()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} check failed: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("Verification Summary")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n" + "=" * 60)
        print("✅ ALL CHECKS PASSED - READY TO DEPLOY!")
        print("=" * 60)
        print("\nNext steps:")
        print("  1. bedrock-agentcore deploy")
        print("  2. python test_deployed_agent.py")
        return 0
    else:
        print("\n" + "=" * 60)
        print("❌ SOME CHECKS FAILED - FIX ISSUES BEFORE DEPLOYING")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
