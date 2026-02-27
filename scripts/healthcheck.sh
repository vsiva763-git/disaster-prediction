#!/bin/bash
set -e

# Healthcheck script for Tsunami Early Warning System
# Used by Docker to verify container health

# Get port from environment variable with fallback
PORT=${PORT:-5000}
HOST=${HOST:-127.0.0.1}
TIMEOUT=${TIMEOUT:-10}
MAX_RETRIES=${MAX_RETRIES:-3}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Retry counter
RETRY=0

echo "[HEALTHCHECK] Starting health check on http://$HOST:$PORT/health"
echo "[HEALTHCHECK] Timeout: ${TIMEOUT}s, Max retries: ${MAX_RETRIES}"

# Function to perform health check
check_health() {
    RETRY=$((RETRY + 1))
    
    echo "[HEALTHCHECK] Attempt #$RETRY of $MAX_RETRIES..."
    
    # Try to curl the health endpoint
    if curl -sf --connect-timeout $TIMEOUT --max-time $TIMEOUT -w "\n%{http_code}" \
            "http://$HOST:$PORT/health" > /dev/null 2>&1; then
        
        echo -e "${GREEN}[HEALTHCHECK] ✓ Health check passed!${NC}"
        echo "[HEALTHCHECK] Application is healthy"
        exit 0
        
    else
        EXIT_CODE=$?
        
        if [ $RETRY -lt $MAX_RETRIES ]; then
            echo -e "${YELLOW}[HEALTHCHECK] ✗ Attempt #$RETRY failed (exit code: $EXIT_CODE)${NC}"
            echo "[HEALTHCHECK] Retrying in 2 seconds..."
            sleep 2
            check_health
        else
            echo -e "${RED}[HEALTHCHECK] ✗ Health check failed after $MAX_RETRIES attempts!${NC}"
            echo "[HEALTHCHECK] Application is not responding to health checks"
            exit 1
        fi
    fi
}

# Start health check
check_health
