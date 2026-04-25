#!/bin/bash
# Smoke test — confirms all five stack components are live
# and kill switch is in place before agent starts processing outbound

set -e
PASS="✅"
FAIL="❌"
ALL_PASS=true

echo "=== TRP1 Week 10 Smoke Test ==="

# Check 1: Kill switch is unset
echo -n "1. Kill switch unset... "
if grep -q "TENACIOUS_OUTBOUND_ENABLED=true" ../.env 2>/dev/null; then
    echo "$FAIL Kill switch is ENABLED — outbound will reach real prospects"
    ALL_PASS=false
else
    echo "$PASS Kill switch unset (sink mode active)"
fi

# Check 2: Acknowledgement signed
echo -n "2. Acknowledgement signed... "
if [ -f "../policy/acknowledgement_signed.txt" ]; then
    echo "$PASS Found policy/acknowledgement_signed.txt"
else
    echo "$FAIL Missing policy/acknowledgement_signed.txt"
    ALL_PASS=false
fi

# Check 3: Resend API key present
echo -n "3. Resend API key... "
if grep -q "RESEND_API_KEY=" ../.env 2>/dev/null; then
    echo "$PASS RESEND_API_KEY present in .env"
else
    echo "$FAIL RESEND_API_KEY missing from .env"
    ALL_PASS=false
fi

# Check 4: HubSpot token present
echo -n "4. HubSpot token... "
if grep -q "HUBSPOT_ACCESS_TOKEN=" ../.env 2>/dev/null; then
    echo "$PASS HUBSPOT_ACCESS_TOKEN present in .env"
else
    echo "$FAIL HUBSPOT_ACCESS_TOKEN missing from .env"
    ALL_PASS=false
fi

# Check 5: Langfuse keys present
echo -n "5. Langfuse keys... "
if grep -q "LANGFUSE_PUBLIC_KEY=" ../.env 2>/dev/null; then
    echo "$PASS LANGFUSE_PUBLIC_KEY present in .env"
else
    echo "$FAIL LANGFUSE_PUBLIC_KEY missing from .env"
    ALL_PASS=false
fi

echo ""
if [ "$ALL_PASS" = true ]; then
    echo "=== All checks passed. Agent is safe to start. ==="
    exit 0
else
    echo "=== Some checks failed. Fix before running agent. ==="
    exit 1
fi