#!/bin/bash
# Detailed API Gateway test - set API_ENDPOINT and ORIGIN in env to avoid committing URLs
# Retries on 504 (API Gateway has a 29s timeout; Bedrock can be slow)

set -e

API_ENDPOINT="${API_ENDPOINT:-https://YOUR_API_ID.execute-api.eu-central-1.amazonaws.com/prod}/generate-question"
ORIGIN="${ORIGIN:-http://YOUR_BUCKET.s3-website.eu-central-1.amazonaws.com}"
MAX_ATTEMPTS=3

echo "Testing API Gateway with detailed output (up to ${MAX_ATTEMPTS} attempts)..."
echo ""

for attempt in $(seq 1 $MAX_ATTEMPTS); do
    echo "Attempt $attempt of $MAX_ATTEMPTS..."
    HTTP_CODE=$(curl -s -o /tmp/api-response.json -w "%{http_code}" -X POST "${API_ENDPOINT}" \
      -H "Content-Type: application/json" \
      -H "Origin: ${ORIGIN}" \
      -d '{
        "topic": "linux",
        "subtopic": "processes",
        "difficulty": "intermediate"
      }')

    if [ "$HTTP_CODE" = "200" ] && grep -q "question" /tmp/api-response.json 2>/dev/null; then
        echo "HTTP Status: $HTTP_CODE"
        echo ""
        echo "Response body:"
        python3 -m json.tool /tmp/api-response.json 2>/dev/null || cat /tmp/api-response.json
        echo ""
        echo "✅ Success! Response contains question"
        exit 0
    fi

    if [ "$HTTP_CODE" = "504" ]; then
        echo "  504 Gateway Timeout (API Gateway 29s limit). Retrying..."
    else
        echo "  HTTP $HTTP_CODE. Retrying..."
    fi
    [ $attempt -lt $MAX_ATTEMPTS ] && sleep 3
done

echo ""
echo "Response body (last attempt):"
cat /tmp/api-response.json | python3 -m json.tool 2>/dev/null || cat /tmp/api-response.json
echo ""

if grep -q "Internal server error" /tmp/api-response.json 2>/dev/null; then
    echo "❌ Got Internal Server Error"
    exit 1
elif grep -q "Endpoint request timed out" /tmp/api-response.json 2>/dev/null; then
    echo "❌ All attempts timed out (504). API Gateway has a 29s limit; Bedrock may be slow."
    exit 1
else
    echo "❌ Unexpected response after $MAX_ATTEMPTS attempts"
    exit 1
fi
