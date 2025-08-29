# MicroAI DAO Makefile
# ====================
# Convenient build commands for the entire MicroAI DAO project

.PHONY: all build clean install test watch deploy help contracts dashboard python setup

# Default target
all: build

# Help target
help:
	@echo "🚀 MicroAI DAO Build System"
	@echo "=========================="
	@echo ""
	@echo "Available targets:"
	@echo "  make build       - Build all components (smart contracts + dashboard + python)"
	@echo "  make clean       - Clean all build artifacts"
	@echo "  make install     - Install all dependencies"
	@echo "  make test        - Run all tests"
	@echo "  make watch       - Watch for file changes and auto-rebuild"
	@echo "  make deploy      - Build and deploy smart contracts"
	@echo "  make setup       - Complete automated setup"
	@echo ""
	@echo "Component-specific targets:"
	@echo "  make contracts   - Build only smart contracts"
	@echo "  make dashboard   - Build only React dashboard"
	@echo "  make python      - Setup only Python environment"
	@echo ""
	@echo "Quick commands:"
	@echo "  make dev         - Start dashboard in development mode"
	@echo "  make serve       - Preview built dashboard"

# Build all components
build:
	@echo "🔨 Building all MicroAI DAO components..."
	./auto-build.sh

# Clean build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
	./auto-build.sh --clean

# Install dependencies
install:
	@echo "📦 Installing dependencies (persistent, no venv)..."
	@if [ ! -d "microai-dashboard/node_modules" ]; then \
		cd microai-dashboard && npm install; \
	fi
	@PIP_BREAK_SYSTEM_PACKAGES=1 /usr/bin/python3 -m pip install --user --upgrade pip
	@PIP_BREAK_SYSTEM_PACKAGES=1 /usr/bin/python3 -m pip install --user solana anchorpy openai requests pandas numpy beautifulsoup4 selenium webdriver-manager schedule flask stripe google-api-python-client google-auth-oauthlib google-auth-httplib2 pillow opencv-python moviepy pydub python-dotenv

# Setup complete environment
setup:
	@echo "⚙️ Running complete automated setup..."
	./automated_execai_setup.sh

# Build and deploy
deploy:
	@echo "🚀 Building and deploying..."
	./auto-build.sh --deploy

# Watch mode
watch:
	@echo "👀 Starting watch mode..."
	./auto-build.sh --watch

# Test everything
test:
	@echo "🧪 Running tests..."
	@if [ -x "./test_setup.sh" ]; then \
		./test_setup.sh; \
	else \
		echo "⚠️  No test script found"; \
	fi
	@cd microai-dashboard && npm run build

# Build only smart contracts
contracts:
	@echo "🦀 Building Rust smart contracts..."
	@if [ -f "lib.rs" ]; then \
		cargo build-bpf; \
	fi
	@if [ -d "programs" ]; then \
		for dir in programs/*/; do \
			if [ -f "$$dir/Cargo.toml" ]; then \
				echo "Building $$(basename $$dir)..."; \
				cd "$$dir" && cargo build-bpf && cd ../..; \
			fi; \
		done; \
	fi

# Build only dashboard
dashboard:
	@echo "⚛️ Building React dashboard..."
	@cd microai-dashboard && npm install && npm run build

# Setup only Python environment (persistent, no venv)
python:
	@echo "🐍 Setting up Python environment (persistent, no venv)..."
	@PIP_BREAK_SYSTEM_PACKAGES=1 /usr/bin/python3 -m pip install --user --upgrade pip
	@PIP_BREAK_SYSTEM_PACKAGES=1 /usr/bin/python3 -m pip install --user solana anchorpy openai requests pandas numpy beautifulsoup4 selenium webdriver-manager schedule flask stripe google-api-python-client google-auth-oauthlib google-auth-httplib2 pillow opencv-python moviepy pydub python-dotenv

# Development mode - start dashboard dev server
dev:
	@echo "🔥 Starting dashboard development server..."
	@cd microai-dashboard && npm run dev

# Preview built dashboard
serve:
	@echo "📡 Starting dashboard preview server..."
	@cd microai-dashboard && npm run preview

# Quick status check
status:
	@echo "📊 MicroAI DAO Project Status"
	@echo "============================"
	@echo -n "Rust: "; rustc --version 2>/dev/null || echo "❌ Not installed"
	@echo -n "Solana CLI: "; solana --version 2>/dev/null || echo "❌ Not installed"
	@echo -n "Node.js: "; node --version 2>/dev/null || echo "❌ Not installed"
	@echo -n "Python: "; python3 --version 2>/dev/null || echo "❌ Not installed"
	@echo ""
	@echo "Build artifacts:"
	@if [ -f "target/deploy/microai_governance.so" ]; then echo "✅ Smart contracts built"; else echo "❌ Smart contracts not built"; fi
	@if [ -f "microai-dashboard/dist/index.html" ]; then echo "✅ Dashboard built"; else echo "❌ Dashboard not built"; fi
	@python3 -c "import pkgutil;mods=['solana','anchorpy','openai','requests','pandas','numpy','bs4','selenium','webdriver_manager','schedule','flask','stripe'];missing=[m for m in mods if pkgutil.find_loader(m) is None];print('✅ Python environment ready' if not missing else '❌ Missing Python packages: '+', '.join(missing))"

# Solana-specific commands
solana-setup:
	@echo "⚙️ Setting up Solana environment..."
	@mkdir -p ~/.config/solana
	@if [ ! -f ~/.config/solana/id.json ]; then \
		solana-keygen new --outfile ~/.config/solana/id.json; \
	fi
	@if [ ! -f ~/.config/solana/execai.json ]; then \
		solana-keygen new --outfile ~/.config/solana/execai.json; \
	fi
	@solana config set --url devnet
	@echo "🪙 Getting test SOL..."
	@solana airdrop 2

# Start all automation systems (no venv)
start-automation:
	@echo "🤖 Starting automation systems (persistent env, no venv)..."
	@python3 revenue_generation_system.py --auto & \
		python3 youtube_content_generator.py --auto & \
		python3 client_acquisition_bot.py --auto & \
		python3 execai_client.py &
	@echo "✅ All automation systems started in background"

# Stop all automation systems
stop-automation:
	@echo "🛑 Stopping automation systems..."
	@pkill -f "revenue_generation_system.py" || true
	@pkill -f "youtube_content_generator.py" || true
	@pkill -f "client_acquisition_bot.py" || true
	@pkill -f "execai_client.py" || true
	@echo "✅ All automation systems stopped"
