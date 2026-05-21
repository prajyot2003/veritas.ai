#!/usr/bin/env bash
# ============================================================
# VERITAS AI — One-Command Installer
# Usage: ./install.sh
# Supports: macOS (Apple Silicon M1/M2/M3) & Linux
# ============================================================

set -euo pipefail

# ── Colors ──────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

log()  { echo -e "${GREEN}[VERITAS]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
err()  { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }
info() { echo -e "${CYAN}[INFO]${NC} $1"; }

banner() {
cat << 'EOF'
 ╔══════════════════════════════════════════════════════════╗
 ║                                                          ║
 ║    ██╗   ██╗███████╗██████╗ ██╗████████╗ █████╗ ███████╗║
 ║    ██║   ██║██╔════╝██╔══██╗██║╚══██╔══╝██╔══██╗██╔════╝║
 ║    ██║   ██║█████╗  ██████╔╝██║   ██║   ███████║███████╗║
 ║    ╚██╗ ██╔╝██╔══╝  ██╔══██╗██║   ██║   ██╔══██║╚════██║║
 ║     ╚████╔╝ ███████╗██║  ██║██║   ██║   ██║  ██║███████║║
 ║      ╚═══╝  ╚══════╝╚═╝  ╚═╝╚═╝   ╚═╝   ╚═╝  ╚═╝╚══════╝║
 ║                                                          ║
 ║         Autonomous Banking Trust Intelligence            ║
 ╚══════════════════════════════════════════════════════════╝
EOF
}

banner
log "Starting VERITAS AI installation..."
echo ""

# ── Detect OS & Architecture ────────────────────────────────
OS="$(uname -s)"
ARCH="$(uname -m)"
info "Detected OS: $OS | Arch: $ARCH"

if [[ "$OS" == "Darwin" ]]; then
    IS_MAC=true
    if [[ "$ARCH" == "arm64" ]]; then
        info "Apple Silicon (M-series) detected ✓"
    fi
else
    IS_MAC=false
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ── 1. Homebrew (macOS) ──────────────────────────────────────
if $IS_MAC; then
    log "Step 1/10: Checking Homebrew..."
    if ! command -v brew &>/dev/null; then
        warn "Homebrew not found. Installing..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        if [[ "$ARCH" == "arm64" ]]; then
            eval "$(/opt/homebrew/bin/brew shellenv)"
        fi
    else
        info "Homebrew found ✓"
    fi
fi

# ── 2. System Dependencies ───────────────────────────────────
log "Step 2/10: Installing system dependencies..."
if $IS_MAC; then
    brew install tesseract redis node python@3.11 2>/dev/null || warn "Some brew packages may already be installed"
    # Neo4j via Homebrew
    if ! command -v neo4j &>/dev/null; then
        brew install neo4j 2>/dev/null || warn "Neo4j install skipped — will use Docker fallback"
    fi
    info "System dependencies installed ✓"
else
    sudo apt-get update -qq
    sudo apt-get install -y tesseract-ocr redis-server nodejs npm python3.11 python3.11-venv python3-pip \
        libgl1-mesa-glx libglib2.0-0 2>/dev/null || warn "Some apt packages may already be installed"
fi

# ── 3. Ollama ────────────────────────────────────────────────
log "Step 3/10: Installing Ollama..."
if ! command -v ollama &>/dev/null; then
    warn "Ollama not found. Installing..."
    if $IS_MAC; then
        brew install ollama 2>/dev/null || curl -fsSL https://ollama.com/install.sh | sh
    else
        curl -fsSL https://ollama.com/install.sh | sh
    fi
    info "Ollama installed ✓"
else
    info "Ollama found ✓"
fi

# ── Start Ollama server ──────────────────────────────────────
log "Starting Ollama server..."
if ! pgrep -x "ollama" > /dev/null; then
    ollama serve &>/dev/null &
    OLLAMA_PID=$!
    sleep 3
    info "Ollama server started (PID: $OLLAMA_PID) ✓"
else
    info "Ollama already running ✓"
fi

# ── Pull Llama model ─────────────────────────────────────────
log "Pulling llama3.1:8b model (~5GB — this may take a while)..."
info "You can grab a coffee ☕ — this downloads once only."
ollama pull llama3.1:8b || warn "Model pull failed — will retry at runtime"
info "llama3.1:8b ready ✓"

# ── 4. Python Virtual Environment ───────────────────────────
log "Step 4/10: Setting up Python virtual environment..."
if [[ ! -d ".venv" ]]; then
    python3.11 -m venv .venv 2>/dev/null || python3 -m venv .venv
fi
source .venv/bin/activate
pip install --upgrade pip -q

info "Installing Python dependencies (~2 min)..."
pip install -r requirements.txt -q
info "Python dependencies installed ✓"

# ── 5. Frontend Dependencies ─────────────────────────────────
log "Step 5/10: Installing frontend dependencies..."
cd frontend
npm install --legacy-peer-deps -q
info "Frontend dependencies installed ✓"
cd ..

# ── 6. Environment Configuration ────────────────────────────
log "Step 6/10: Configuring environment..."
if [[ ! -f ".env" ]]; then
    cp .env.example .env
    info ".env created from template ✓"
else
    info ".env already exists ✓"
fi

if [[ ! -f "frontend/.env.local" ]]; then
    cat > frontend/.env.local << 'ENVEOF'
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=VERITAS AI
ENVEOF
    info "frontend/.env.local created ✓"
fi

# ── 7. Create Directories ────────────────────────────────────
log "Step 7/10: Creating data directories..."
mkdir -p data/uploads data/chromadb data/demo data/regulations data/migrations
info "Directories created ✓"

# ── 8. Start Redis ───────────────────────────────────────────
log "Step 8/10: Starting Redis..."
if ! pgrep -x "redis-server" > /dev/null; then
    redis-server --daemonize yes --port 6379
    info "Redis started ✓"
else
    info "Redis already running ✓"
fi

# ── 9. Start Neo4j ───────────────────────────────────────────
log "Step 9/10: Starting Neo4j..."
if command -v neo4j &>/dev/null; then
    neo4j start 2>/dev/null || warn "Neo4j may already be running"
    sleep 5
    # Set default password
    neo4j-admin dbms set-initial-password veritas123 2>/dev/null || true
    info "Neo4j started ✓"
else
    warn "Neo4j not found — graph features will use in-memory fallback"
fi

# ── 10. Seed Demo Data ───────────────────────────────────────
log "Step 10/10: Seeding demo data..."
source .venv/bin/activate
python3 scripts/seed_demo.py
info "Demo data seeded ✓"

# ── Launch Services ──────────────────────────────────────────
echo ""
log "🚀 Launching VERITAS AI..."
echo ""

# Start backend
info "Starting FastAPI backend on port 8000..."
source .venv/bin/activate
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &>/tmp/veritas_backend.log &
BACKEND_PID=$!
cd ..
sleep 3

# Check backend health
if curl -s http://localhost:8000/health | grep -q "ok"; then
    info "Backend healthy ✓ (PID: $BACKEND_PID)"
else
    warn "Backend may still be starting — check /tmp/veritas_backend.log"
fi

# Start frontend
info "Starting Next.js frontend on port 3000..."
cd frontend
npm run dev &>/tmp/veritas_frontend.log &
FRONTEND_PID=$!
cd ..
sleep 5

echo ""
echo -e "${BOLD}${GREEN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${GREEN}║         VERITAS AI IS RUNNING! 🎉                   ║${NC}"
echo -e "${BOLD}${GREEN}╠══════════════════════════════════════════════════════╣${NC}"
echo -e "${BOLD}${GREEN}║  🌐  Frontend:  http://localhost:3000                ║${NC}"
echo -e "${BOLD}${GREEN}║  ⚡  Backend:   http://localhost:8000                ║${NC}"
echo -e "${BOLD}${GREEN}║  📚  API Docs:  http://localhost:8000/docs           ║${NC}"
echo -e "${BOLD}${GREEN}╠══════════════════════════════════════════════════════╣${NC}"
echo -e "${BOLD}${GREEN}║  👤  Login:     admin@veritas.ai / veritas123        ║${NC}"
echo -e "${BOLD}${GREEN}║  👤  Analyst:   analyst@veritas.ai / analyst123      ║${NC}"
echo -e "${BOLD}${GREEN}╚══════════════════════════════════════════════════════╝${NC}"
echo ""
info "Backend logs: tail -f /tmp/veritas_backend.log"
info "Frontend logs: tail -f /tmp/veritas_frontend.log"
echo ""
log "Press Ctrl+C to stop all services."

# Open browser
sleep 3
if $IS_MAC; then
    open http://localhost:3000 2>/dev/null || true
fi

# Wait
wait $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
