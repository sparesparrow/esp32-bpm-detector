#!/bin/bash
# Development Loop Orchestrator
# Uses cursor-agent CLI with MCP servers for automated development workflow
#
# This script implements a build-deploy-test-iterate loop using cursor-agent
# with MCP servers for ESP32 BPM Detector development.

set -e

# Configuration
PROJECT_DIR="/home/sparrow/projects/embedded-systems/esp32-bpm-detector"
LOG_DIR="${PROJECT_DIR}/dev-logs"
PROMPT_FILE="${PROJECT_DIR}/scripts/dev_loop_prompt.md"
ITERATION=0
MAX_ITERATIONS=${MAX_ITERATIONS:-10}
SUCCESS_MARKER="All tests passed"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create log directory
mkdir -p "$LOG_DIR"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_banner() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║         ESP32 BPM Detector - Development Loop Orchestrator       ║"
    echo "╠══════════════════════════════════════════════════════════════════╣"
    echo "║  Project: ${PROJECT_DIR}  ║"
    echo "║  Max Iterations: ${MAX_ITERATIONS}                                              ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo ""
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check cursor-agent CLI
    if ! command -v cursor-agent &> /dev/null; then
        log_error "cursor-agent CLI not found. Please install it first."
        exit 1
    fi
    
    # Check PlatformIO
    if ! command -v pio &> /dev/null; then
        log_warning "PlatformIO not found. Build/deploy may fail."
    fi
    
    # Check project directory
    if [ ! -d "$PROJECT_DIR" ]; then
        log_error "Project directory not found: $PROJECT_DIR"
        exit 1
    fi
    
    # Check for MCP configuration
    if [ ! -f "${PROJECT_DIR}/.cursor/mcp.json" ]; then
        log_warning "MCP configuration not found. Creating default..."
    fi
    
    log_success "Prerequisites check passed"
}

read_prompt() {
    if [ -f "$PROMPT_FILE" ]; then
        cat "$PROMPT_FILE"
    else
        # Default prompt if file not found
        echo "Execute full development pipeline: build, deploy to ESP32-S3, run all tests (unit, component with mocks, integration with real hardware and Android via ADB), analyze results, and fix any failures. Report detailed results."
    fi
}

run_iteration() {
    local iteration=$1
    local log_file="$LOG_DIR/iteration_${iteration}.log"
    local prompt=$(read_prompt)
    
    log_info "Starting Development Iteration $iteration..."
    echo "Log file: $log_file"
    
    # Timestamp
    echo "=== Iteration $iteration started at $(date -Iseconds) ===" | tee -a "$log_file"
    
    # Run cursor-agent with MCP servers
    # --workspace: Set workspace directory
    # --print: Print responses (headless mode, required for --approve-mcps)
    # --force: Force allow commands
    # --approve-mcps: Auto-approve MCP tool invocations (only works with --print)
    cursor-agent \
        --workspace "$PROJECT_DIR" \
        --print \
        --force \
        --approve-mcps \
        "$prompt" \
        2>&1 | tee -a "$log_file"
    
    local exit_code=$?
    
    # Check result
    echo "=== Iteration $iteration completed at $(date -Iseconds) ===" | tee -a "$log_file"
    echo "Exit code: $exit_code" | tee -a "$log_file"
    
    return $exit_code
}

check_success() {
    local log_file=$1
    
    if grep -q "$SUCCESS_MARKER" "$log_file"; then
        return 0
    else
        return 1
    fi
}

generate_summary() {
    log_info "Generating summary..."
    
    local summary_file="$LOG_DIR/summary.md"
    
    echo "# Development Loop Summary" > "$summary_file"
    echo "" >> "$summary_file"
    echo "Generated: $(date -Iseconds)" >> "$summary_file"
    echo "" >> "$summary_file"
    echo "## Iterations" >> "$summary_file"
    echo "" >> "$summary_file"
    
    for log in "$LOG_DIR"/iteration_*.log; do
        if [ -f "$log" ]; then
            local iter=$(basename "$log" .log | sed 's/iteration_//')
            local status="❓"
            
            if check_success "$log"; then
                status="✅"
            else
                status="❌"
            fi
            
            echo "- Iteration $iter: $status" >> "$summary_file"
        fi
    done
    
    echo "" >> "$summary_file"
    echo "## Final Status" >> "$summary_file"
    echo "" >> "$summary_file"
    
    if [ "$FINAL_STATUS" = "success" ]; then
        echo "✅ **All tests passed** after $ITERATION iteration(s)" >> "$summary_file"
    else
        echo "❌ **Tests failed** after $ITERATION iteration(s)" >> "$summary_file"
    fi
    
    log_success "Summary saved to: $summary_file"
}

# Main execution
main() {
    print_banner
    check_prerequisites
    
    log_info "Starting development loop (max $MAX_ITERATIONS iterations)..."
    
    FINAL_STATUS="failed"
    
    while [ $ITERATION -lt $MAX_ITERATIONS ]; do
        ITERATION=$((ITERATION + 1))
        
        echo ""
        echo "╔════════════════════════════════════════════════════╗"
        echo "║        DEVELOPMENT ITERATION $ITERATION of $MAX_ITERATIONS              ║"
        echo "╚════════════════════════════════════════════════════╝"
        echo ""
        
        # Run the iteration
        run_iteration $ITERATION
        
        # Check if all tests passed
        local log_file="$LOG_DIR/iteration_${ITERATION}.log"
        
        if check_success "$log_file"; then
            log_success "All tests passed on iteration $ITERATION!"
            FINAL_STATUS="success"
            break
        fi
        
        log_warning "Tests did not pass on iteration $ITERATION, continuing..."
        
        # Brief pause between iterations
        if [ $ITERATION -lt $MAX_ITERATIONS ]; then
            log_info "Waiting 5 seconds before next iteration..."
            sleep 5
        fi
    done
    
    # Generate summary
    generate_summary
    
    # Final output
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    if [ "$FINAL_STATUS" = "success" ]; then
        echo "║   ✅ SUCCESS: Development loop completed successfully!    ║"
    else
        echo "║   ❌ FAILED: Max iterations reached without success        ║"
    fi
    echo "╠════════════════════════════════════════════════════════════╣"
    echo "║   Total iterations: $ITERATION                                      ║"
    echo "║   Logs: $LOG_DIR                       ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    
    if [ "$FINAL_STATUS" = "success" ]; then
        exit 0
    else
        exit 1
    fi
}

# Handle command line arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --max N        Set maximum iterations (default: 10)"
        echo "  --clean        Clean log directory before starting"
        echo ""
        echo "Environment variables:"
        echo "  MAX_ITERATIONS  Maximum number of iterations"
        echo "  PROJECT_DIR     Project directory path"
        exit 0
        ;;
    --max)
        MAX_ITERATIONS=$2
        shift 2
        ;;
    --clean)
        rm -rf "$LOG_DIR"
        mkdir -p "$LOG_DIR"
        log_info "Log directory cleaned"
        shift
        ;;
esac

# Run main
main
