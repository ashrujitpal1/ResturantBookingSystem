# Deployment Guide - Modular Architecture

## ✅ Updated Files

The following files have been updated to use the new modular structure:

### 1. `.bedrock_agentcore.yaml`
```yaml
# OLD
entrypoint: restaurant_agent_runtime/complete_booking_workflow.py

# NEW
entrypoint: src/workflows/restaurant_workflow.py
```

### 2. `Dockerfile`
```dockerfile
# OLD
COPY restaurant_agent_runtime/requirements.txt restaurant_agent_runtime/requirements.txt
RUN uv pip install -r restaurant_agent_runtime/requirements.txt
CMD ["python", "-m", "restaurant_agent_runtime.complete_booking_workflow"]

# NEW
COPY requirements.txt requirements.txt
RUN uv pip install -r requirements.txt
CMD ["python", "-m", "src.workflows.restaurant_workflow"]
```

## 🚀 Deployment Steps

### 1. Deploy Lambda Functions (SAM)
```bash
# No changes needed - Lambda functions unchanged
sam build
sam deploy --guided
```

### 2. Deploy AgentCore Runtime
```bash
# Build and deploy with new modular structure
bedrock-agentcore deploy
```

Or using your existing deployment script:
```bash
python deploy_restaurant_agent.py
```

### 3. Test the Deployment
```bash
# Test locally first
python -m src.workflows.restaurant_workflow

# Test deployed agent
python test_deployed_agent.py
```

## 📦 What Gets Deployed

### Lambda Functions (SAM)
```
src/lambda/
├── book_a_table.py
├── payment_api.py
├── fetch_restaurant_details.py
└── ... (all Lambda functions)
```

### AgentCore Runtime (Container)
```
src/
├── agents/           # ✅ Deployed
├── tools/            # ✅ Deployed
├── workflows/        # ✅ Deployed (entrypoint)
├── utils/            # ✅ Deployed
└── config/           # ✅ Deployed
```

## 🔍 Verification

After deployment, verify:

1. **Container builds successfully**
   ```bash
   docker build -t restaurant-agent .
   ```

2. **Entrypoint is correct**
   ```bash
   docker run restaurant-agent python -m src.workflows.restaurant_workflow
   ```

3. **All imports work**
   ```bash
   python src/tests/test_modular_architecture.py
   ```

## 🐛 Troubleshooting

### Issue: Module not found
```
ModuleNotFoundError: No module named 'src'
```

**Solution**: Ensure you're running from project root:
```bash
cd /Users/USER/Work/AI/AgentCore/ResturantBookingSystem
python -m src.workflows.restaurant_workflow
```

### Issue: Import errors in container
```
ImportError: cannot import name 'RestaurantBookingState'
```

**Solution**: Verify all `__init__.py` files exist:
```bash
find src -name "__init__.py"
```

### Issue: Old workflow still running
**Solution**: Clear AgentCore cache and redeploy:
```bash
bedrock-agentcore delete
bedrock-agentcore deploy
```

## 📋 Deployment Checklist

- [x] Updated `.bedrock_agentcore.yaml` entrypoint
- [x] Updated `Dockerfile` CMD
- [x] Root `requirements.txt` exists with all dependencies
- [x] All `__init__.py` files created
- [x] Tests passing (`test_modular_architecture.py`)
- [ ] Build Docker image locally
- [ ] Deploy to AgentCore
- [ ] Test deployed agent
- [ ] Update monitoring/logging

## 🔄 Rollback Plan

If issues occur, rollback to old structure:

```bash
# Revert .bedrock_agentcore.yaml
git checkout .bedrock_agentcore.yaml

# Revert Dockerfile
git checkout Dockerfile

# Redeploy
bedrock-agentcore deploy
```

The old `restaurant_agent_runtime/complete_booking_workflow.py` remains unchanged as backup.

## 📊 Deployment Comparison

| Aspect | Old (Monolithic) | New (Modular) |
|--------|------------------|---------------|
| Entrypoint | `restaurant_agent_runtime/complete_booking_workflow.py` | `src/workflows/restaurant_workflow.py` |
| Structure | Single 911-line file | 13 focused modules |
| Testability | Hard to test | Easy unit testing |
| Maintainability | Low | High |
| SOLID Compliance | No | Yes |

## ✅ Ready to Deploy

All files are updated and ready for deployment. Run:

```bash
bedrock-agentcore deploy
```
