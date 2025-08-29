#!/bin/bash

# MicroAI DAO Auto-Build Script
# =============================
# Automatically builds all components of the MicroAI DAO project
# Usage: ./auto-build.sh [--watch] [--clean] [--deploy]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

info() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')] $1${NC}"
}

# Parse command line arguments
WATCH_MODE=false
CLEAN_BUILD=false
DEPLOY_MODE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --watch)
            WATCH_MODE=true
            shift
            ;;
        --clean)
            CLEAN_BUILD=true
            shift
            ;;
        --deploy)
            DEPLOY_MODE=true
            shift
            ;;
        *)
            echo "Unknown option $1"
            echo "Usage: $0 [--watch] [--clean] [--deploy]"
            exit 1
            ;;
    esac
done

# Function to build Rust smart contracts
build_smart_contracts() {
    log "Building Solana smart contracts..."
    
    if [ "$CLEAN_BUILD" = true ]; then
        log "Cleaning previous builds..."
        cargo clean 2>/dev/null || true
        rm -rf target/ 2>/dev/null || true
    fi
    
    # Build main governance contract (lib.rs in root)
    if [ -f "lib.rs" ]; then
        log "Building main governance contract..."
        cargo build-bpf || error "Failed to build main governance contract"
    fi
    
    # Build programs directory contracts
    if [ -d "programs" ]; then
        for program_dir in programs/*/; do
            if [ -d "$program_dir" ] && [ -f "${program_dir}Cargo.toml" ]; then
                program_name=$(basename "$program_dir")
                log "Building $program_name program..."
                (cd "$program_dir" && cargo build-bpf) || warn "Failed to build $program_name program"
            fi
        done
    fi
    
    log "✅ Smart contracts build complete"
}

# Function to build React dashboard
build_dashboard() {
    log "Building React dashboard..."
    
    if [ ! -d "microai-dashboard" ]; then
        warn "Dashboard directory not found, skipping..."
        return
    fi
    
    cd microai-dashboard/
    
    if [ "$CLEAN_BUILD" = true ]; then
        log "Cleaning dashboard build..."
        rm -rf node_modules/ dist/ 2>/dev/null || true
        npm install || error "Failed to install dashboard dependencies"
    fi
    
    # Install dependencies if node_modules doesn't exist
    if [ ! -d "node_modules" ]; then
        log "Installing dashboard dependencies..."
        npm install || error "Failed to install dashboard dependencies"
    fi
    
    # Check for environment file
    if [ ! -f ".env.local" ] && [ -f ".env.example" ]; then
        warn "Creating .env.local from .env.example..."
        cp .env.example .env.local
    fi
    
    # Build the dashboard
    log "Building dashboard..."
    npm run build || error "Failed to build dashboard"
    
    cd ..
    log "✅ Dashboard build complete"
}

# Function to setup Python environment (persistent, no venv)
setup_python_env() {
    log "Setting up Python environment (persistent, no venv)..."
    PIP_BREAK_SYSTEM_PACKAGES=1 python3 -m pip install --user --upgrade pip || warn "Could not upgrade pip"
    PIP_BREAK_SYSTEM_PACKAGES=1 python3 -m pip install --user solana anchorpy openai requests pandas numpy beautifulsoup4 selenium webdriver-manager schedule flask stripe google-api-python-client google-auth-oauthlib google-auth-httplib2 pillow opencv-python moviepy pydub python-dotenv || warn "Some Python packages failed to install"
    log "✅ Python environment setup complete"
}

# Function to validate build
validate_build() {
    log "Validating build outputs..."
    
    # Check if smart contract artifacts exist
    if [ -f "target/deploy/microai_governance.so" ]; then
        log "✅ Found governance contract artifact"
    else
        warn "Governance contract artifact not found"
    fi
    
    # Check if dashboard built
    if [ -f "microai-dashboard/dist/index.html" ]; then
        log "✅ Found dashboard build output"
    else
        warn "Dashboard build output not found"
    fi
    
    # Check if Python environment is ready by importing key modules
    python3 - <<'EOF'
mods = ["solana","anchorpy","openai","requests","pandas","numpy","bs4","selenium","webdriver_manager","schedule","flask","stripe"]
missing = []
for m in mods:
    try:
        __import__(m)
    except Exception:
        missing.append(m)
print("✅ Python environment ready" if not missing else f"⚠️  Missing Python packages: {', '.join(missing)}")
EOF
}

# Function to deploy (if requested)
deploy_contracts() {
    if [ "$DEPLOY_MODE" = true ]; then
        log "Deploying smart contracts..."
        if [ -x "./deploy.sh" ]; then
            ./deploy.sh || error "Deployment failed"
            log "✅ Deployment complete"
        else
            error "Deploy script not found or not executable"
        fi
    fi
}

# Function to watch for file changes and auto-rebuild
watch_and_build() {
    if ! command -v inotifywait &> /dev/null; then
        log "Installing inotify-tools for file watching..."
        sudo apt update && sudo apt install -y inotify-tools
    fi
    
    log "Starting watch mode - building on file changes..."
    log "Watching: *.rs, *.toml, *.tsx, *.ts, *.py files"
    log "Press Ctrl+C to stop"
    
    # Initial build
    build_all
    
    # Watch for changes
    while true; do
        inotifywait -r -e modify,create,delete \
            --include '\.(rs|toml|tsx|ts|py|json)$' \
            . microai-dashboard/src/ 2>/dev/null || true
            
        log "File change detected, rebuilding..."
        build_all
    done
}

# Main build function
build_all() {
    local start_time=$(date +%s)
    
    info "🔨 Starting MicroAI DAO auto-build..."
    
    # Build smart contracts
    build_smart_contracts
    
    # Build dashboard
    build_dashboard
    
    # Setup Python environment
    setup_python_env
    
    # Validate build
    validate_build
    
    # Deploy if requested
    deploy_contracts
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    log "🎉 Build complete in ${duration}s"
}

# Main execution
main() {
    echo -e "${BLUE}"
    echo "🚀 MicroAI DAO Auto-Build System"
    echo "================================="
    echo "Building: Smart Contracts + Dashboard + Python Environment"
    echo -e "${NC}"
    
    if [ "$WATCH_MODE" = true ]; then
        watch_and_build
    else
        build_all
    fi
}

# Run main function
main "$@"
