#!/usr/bin/env python3
"""Identify irrelevant files in the workspace."""

# Files that can be safely deleted (now superseded by modular structure)
IRRELEVANT_FILES = {
    # Old monolithic workflow (superseded by src/workflows/)
    "restaurant_agent_runtime/complete_booking_workflow.py": "Superseded by modular src/workflows/restaurant_workflow.py",
    "restaurant_agent_runtime/restaurant_workflow.py": "Superseded by modular src/workflows/restaurant_workflow.py",
    "restaurant_agent_runtime/requirements.txt": "Use root requirements.txt instead",
    
    # Duplicate/old test files
    "restaurant_agent_runtime/test_complete_booking.py": "Old tests for monolithic structure",
    "restaurant_agent_runtime/test_workflow.py": "Old tests for monolithic structure",
    "restaurant_agent_runtime/test_integration_e2e.py": "Duplicate - use src/tests/",
    "restaurant_agent_runtime/test_phase3_memory.py": "Old phase-specific tests",
    "restaurant_agent_runtime/test_production_fixes.py": "Old phase-specific tests",
    
    # Archived documentation (reference only)
    "docs/archieve/COMPLETE_IMPLEMENTATION.md": "Archived - reference only",
    "docs/archieve/DEPLOYMENT_PLAN.md": "Archived - use DEPLOYMENT_GUIDE.md",
    "docs/archieve/DEPLOYMENT_SUMMARY.md": "Archived - use DEPLOYMENT_CHANGES.md",
    "docs/archieve/GOVERNANCE_POLICIES_COMPLETE.md": "Archived - implemented in code",
    "docs/archieve/IMPLEMENTATION_SUMMARY.md": "Archived - use REFACTORING_SUMMARY.md",
    "docs/archieve/LANGGRAPH_WORKFLOW_DIAGRAM.md": "Archived - reference only",
    "docs/archieve/LLM_PROVIDER_ABSTRACTION_COMPLETE.md": "Archived - implemented in src/utils/llm_providers.py",
    "docs/archieve/MODEL_SELECTION_COMPLETE.md": "Archived - implemented in src/config/models.py",
    "docs/archieve/PHASE2_PRODUCTION_READY.md": "Archived - reference only",
    "docs/archieve/PHASE2_SPECIFICATION_VERIFICATION.md": "Archived - reference only",
    "docs/archieve/PHASE2_SUMMARY.md": "Archived - reference only",
    "docs/archieve/PHASE3_COMPLETE.md": "Archived - reference only",
    "docs/archieve/PRODUCTION_FIXES_COMPLETE.md": "Archived - reference only",
    "docs/archieve/PROMPT_INJECTION_DEFENSE_COMPLETE.md": "Archived - implemented in src/utils/circuit_breaker.py",
    "docs/archieve/PROMPT_VERSIONING_COMPLETE.md": "Archived - implemented in src/utils/circuit_breaker.py",
    "docs/archieve/QUICK_REFERENCE.md": "Archived - use QUICK_START.md",
    "docs/archieve/README_DEPLOYMENT.md": "Archived - use DEPLOYMENT_GUIDE.md",
    "docs/archieve/STEP_BY_STEP_GUIDE.md": "Archived - use QUICK_START.md",
    "docs/archieve/setup-agentcore-gateway.py": "Archived - reference only",
    
    # Duplicate deployment docs
    "CHANGES_SUMMARY.md": "Duplicate - covered in REFACTORING_SUMMARY.md",
    "DEPLOYMENT_ASSESSMENT.md": "Old assessment - use DEPLOYMENT_GUIDE.md",
    "DEPLOYMENT_STATUS.md": "Old status - use DEPLOYMENT_CHANGES.md",
    "DEPLOY_NOW.md": "Duplicate - use DEPLOYMENT_GUIDE.md",
    "ENABLE_MEMORY.md": "Old memory setup - covered in docs/",
    
    # Duplicate test files
    "test_simple.py": "Duplicate - use src/tests/test_modular_architecture.py",
    "test-direct.py": "Old test - use test_deployed_agent.py",
    "test-local-agent.py": "Old test - use src/tests/",
    "test-local.sh": "Old test script",
    
    # Duplicate deployment scripts
    "deploy-agent.py": "Duplicate - use deploy_restaurant_agent.py",
    "deploy-complete-workflow.sh": "Old deployment - use bedrock-agentcore deploy",
    "deploy-complete.sh": "Old deployment - use bedrock-agentcore deploy",
    "deploy-full-system.sh": "Old deployment - use bedrock-agentcore deploy",
    "deploy-production.sh": "Old deployment - use bedrock-agentcore deploy",
    "deploy.sh": "Old deployment - use bedrock-agentcore deploy",
    
    # Old notebooks (archived)
    "docs/_archive_01_plant_advisor_gateway.ipynb": "Archived notebook - not relevant",
    "docs/_archive_02_plant_advisor_runtime_mem.ipynb": "Archived notebook - not relevant",
}

# Files to keep
KEEP_FILES = {
    # Core modular structure
    "src/": "New modular architecture",
    
    # Lambda functions (still needed)
    "src/lambda/": "Lambda functions for MCP",
    
    # Configuration
    ".bedrock_agentcore.yaml": "AgentCore config (updated)",
    "Dockerfile": "Container config (updated)",
    "template.yaml": "SAM template for Lambda",
    "requirements.txt": "Root dependencies",
    
    # Deployment
    "deploy_restaurant_agent.py": "Main deployment script",
    "verify_deployment.py": "Pre-deployment verification",
    "test_deployed_agent.py": "Post-deployment testing",
    
    # Infrastructure
    "create-dynamodb-tables.sh": "DynamoDB setup",
    "insert_restaurant_records.py": "Data seeding",
    "setup-fresh-infrastructure.sh": "Infrastructure setup",
    "cleanup-infrastructure.sh": "Infrastructure cleanup",
    
    # Documentation (current)
    "DEPLOYMENT_GUIDE.md": "Deployment instructions",
    "DEPLOYMENT_CHANGES.md": "Summary of changes",
    "REFACTORING_SUMMARY.md": "Refactoring details",
    "QUICK_START.md": "Quick start guide",
    "src/README.md": "Architecture documentation",
    "DynamoDB-Schema.md": "Database schema",
    "TODO.md": "Project todos",
    
    # Configuration files
    "agentcore-gateway-config.json": "Gateway config",
    "bedrock-policy.json": "IAM policy",
    "gateway-targets.json": "Gateway targets",
    "lambda-arns.json": "Lambda ARNs",
    "mcp-tool-definitions.json": "MCP tool definitions",
    "restaurant_gateway_config.json": "Restaurant gateway config",
    
    # Prompts
    "prompts/": "Versioned prompts",
    
    # Utilities
    "register-mcp-tools.py": "MCP tool registration",
    "upload_prompts_to_s3.py": "Prompt upload utility",
    "check_restaurant_data.py": "Data verification",
    "enable_memory.py": "Memory enablement",
    "simple-cleanup.py": "Simple cleanup utility",
    
    # Project rules
    ".amazonq/": "Amazon Q project rules",
}

def main():
    print("=" * 70)
    print("IRRELEVANT FILES ANALYSIS")
    print("=" * 70)
    
    print("\n📁 FILES THAT CAN BE DELETED (Superseded by Modular Structure)")
    print("-" * 70)
    
    total_size = 0
    for file, reason in sorted(IRRELEVANT_FILES.items()):
        print(f"\n❌ {file}")
        print(f"   Reason: {reason}")
    
    print(f"\n\nTotal: {len(IRRELEVANT_FILES)} files can be safely deleted")
    
    print("\n\n✅ FILES TO KEEP")
    print("-" * 70)
    for file, reason in sorted(KEEP_FILES.items()):
        print(f"✓ {file:50s} - {reason}")
    
    print("\n\n" + "=" * 70)
    print("CLEANUP COMMAND")
    print("=" * 70)
    print("\n# To delete irrelevant files, run:")
    print("rm -rf restaurant_agent_runtime/complete_booking_workflow.py \\")
    print("       restaurant_agent_runtime/restaurant_workflow.py \\")
    print("       restaurant_agent_runtime/requirements.txt \\")
    print("       restaurant_agent_runtime/test_*.py \\")
    print("       docs/archieve/ \\")
    print("       CHANGES_SUMMARY.md DEPLOYMENT_ASSESSMENT.md \\")
    print("       DEPLOYMENT_STATUS.md DEPLOY_NOW.md ENABLE_MEMORY.md \\")
    print("       test_simple.py test-direct.py test-local-agent.py test-local.sh \\")
    print("       deploy-agent.py deploy-complete*.sh deploy-full-system.sh \\")
    print("       deploy-production.sh deploy.sh")
    
    print("\n\n⚠️  BACKUP RECOMMENDATION")
    print("-" * 70)
    print("Before deleting, create a backup:")
    print("tar -czf backup_old_files_$(date +%Y%m%d).tar.gz \\")
    print("    restaurant_agent_runtime/ docs/archieve/ \\")
    print("    test_simple.py test-*.py deploy-*.sh")

if __name__ == "__main__":
    main()
