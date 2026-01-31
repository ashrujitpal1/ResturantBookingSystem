#!/bin/bash
# Fix agentcore dev error - Install uv

echo "🔧 Fixing agentcore dev error..."
echo ""

# Check if uv is already installed
if command -v uv &> /dev/null; then
    echo "✅ uv is already installed: $(uv --version)"
else
    echo "📦 Installing uv..."
    
    # Try official installer first
    if curl -LsSf https://astral.sh/uv/install.sh | sh; then
        echo "✅ uv installed successfully via official installer"
    else
        # Fallback to pip
        echo "⚠️  Official installer failed, trying pip..."
        pip install uv
        echo "✅ uv installed successfully via pip"
    fi
fi

echo ""
echo "🔍 Verifying installation..."
uv --version

echo ""
echo "✅ Setup complete! You can now run:"
echo "   agentcore dev"
echo ""
echo "💡 Test your agent with:"
echo "   agentcore invoke --dev \"Find Italian restaurants in New York\""
