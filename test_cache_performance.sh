#!/bin/bash
# Test script to verify POST /analysis caching is working

echo "=============================================="
echo "Testing Tenable.sc MCP Cache Performance"
echo "=============================================="
echo ""

# MCP server endpoint
MCP_URL="http://localhost:8000/mcp"

# Test query - identical for both runs
QUERY='{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "tsc_analyze",
    "arguments": {
      "query": {
        "tool": "sumip",
        "sourceType": "cumulative",
        "type": "vuln"
      }
    }
  }
}'

echo "Query 1 (Cache MISS expected)..."
echo "Start time: $(date +%s.%N)"
START1=$(date +%s.%N)

# First query
RESULT1=$(curl -s -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -d "$QUERY")

END1=$(date +%s.%N)
TIME1=$(echo "$END1 - $START1" | bc)
echo "End time: $(date +%s.%N)"
echo "Duration: ${TIME1}s"
echo ""

# Wait a moment
sleep 2

echo "Query 2 (Cache HIT expected - same query)..."
echo "Start time: $(date +%s.%N)"
START2=$(date +%s.%N)

# Second identical query
RESULT2=$(curl -s -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -d "$QUERY")

END2=$(date +%s.%N)
TIME2=$(echo "$END2 - $START2" | bc)
echo "End time: $(date +%s.%N)"
echo "Duration: ${TIME2}s"
echo ""

# Calculate speedup
SPEEDUP=$(echo "scale=2; $TIME1 / $TIME2" | bc)

echo "=============================================="
echo "Results:"
echo "=============================================="
echo "Query 1 (cache miss): ${TIME1}s"
echo "Query 2 (cache hit):  ${TIME2}s"
echo "Speedup:              ${SPEEDUP}x"
echo ""

# Check if results are identical
if [ "$RESULT1" = "$RESULT2" ]; then
    echo "✓ Results are identical (cache working correctly)"
else
    echo "✗ Results differ (unexpected)"
fi

echo ""
echo "Now check cache stats with:"
echo "  Ask Claude: 'show me cache statistics from tenable-sc'"
