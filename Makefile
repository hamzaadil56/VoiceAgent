.PHONY: help install setup run clean test format lint

# Default target
help:
	@echo "VoiceAgent - Available commands:"
	@echo ""
	@echo "  make install    - Install dependencies with UV"
	@echo "  make setup      - Run full setup (install + configure)"
	@echo "  make run        - Run the voice agent"
	@echo "  make clean      - Clean up generated files"
	@echo "  make test       - Run tests (if available)"
	@echo "  make format     - Format code with black"
	@echo "  make lint       - Lint code with ruff"
	@echo ""

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	uv pip install -e .
	@echo "✅ Installation complete!"

# Full setup
setup:
	@echo "🚀 Running setup script..."
	@chmod +x setup.sh
	@./setup.sh

# Run the voice agent
run:
	@echo "🎙️ Starting VoiceAgent..."
	@python main.py

# Run in voice mode
voice:
	@echo "🎙️ Starting voice conversation..."
	@python main.py --mode voice

# Run examples
example-simple:
	@python examples/simple_usage.py

example-custom:
	@python examples/custom_agent_example.py

example-programmatic:
	@python examples/programmatic_usage.py

# Clean up
clean:
	@echo "🧹 Cleaning up..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf build/ dist/ 2>/dev/null || true
	@echo "✅ Cleanup complete!"

# Format code
format:
	@echo "🎨 Formatting code..."
	@black src/ examples/ main.py
	@echo "✅ Formatting complete!"

# Lint code
lint:
	@echo "🔍 Linting code..."
	@ruff check src/ examples/ main.py
	@echo "✅ Linting complete!"

# Test (placeholder)
test:
	@echo "🧪 Running tests..."
	@pytest tests/ -v
	@echo "✅ Tests complete!"

