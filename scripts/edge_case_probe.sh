#!/usr/bin/env bash
# Exploratory probe — Phase 7 edge case audit.
# Run against the live API (docker-compose up). Does NOT assert anything;
# just prints raw responses so we can decide, case by case, whether current
# behavior is a bug or acceptable.

API="http://localhost:8080"

echo "=== 1. Negative / zero ID ==="
curl -s -w "\nHTTP %{http_code}\n" -X POST "$API/departments" \
  -H "Content-Type: application/json" \
  -d '[{"id": -1, "department": "Negative ID Test"}]'
echo "---"
curl -s -w "\nHTTP %{http_code}\n" -X POST "$API/departments" \
  -H "Content-Type: application/json" \
  -d '[{"id": 0, "department": "Zero ID Test"}]'

echo -e "\n=== 2. Whitespace-only name ==="
curl -s -w "\nHTTP %{http_code}\n" -X POST "$API/departments" \
  -H "Content-Type: application/json" \
  -d '[{"id": 601, "department": "   "}]'

echo -e "\n=== 3. ISO datetime with +00:00 offset (not literal Z) ==="
curl -s -w "\nHTTP %{http_code}\n" -X POST "$API/employees" \
  -H "Content-Type: application/json" \
  -d '[{"id": 9010, "name": "Offset Test", "hire_datetime": "2021-05-10T10:00:00+00:00", "department_id": 1, "job_id": 1}]'

echo -e "\n=== 4. Extra/unexpected field in body ==="
curl -s -w "\nHTTP %{http_code}\n" -X POST "$API/departments" \
  -H "Content-Type: application/json" \
  -d '[{"id": 602, "department": "Extra Field Test", "unexpected_field": "should this be rejected?"}]'

echo -e "\n=== 5. Type coercion — id as numeric string ==="
curl -s -w "\nHTTP %{http_code}\n" -X POST "$API/departments" \
  -H "Content-Type: application/json" \
  -d '[{"id": "603", "department": "String ID Test"}]'

echo -e "\n=== 6a. Batch size = 0 (empty array) ==="
curl -s -w "\nHTTP %{http_code}\n" -X POST "$API/departments" \
  -H "Content-Type: application/json" \
  -d '[]'

echo -e "\n=== 6b. Batch size = 1001 ==="
python3 -c "
import json
records = [{'id': 10000 + i, 'department': f'Dept {i}'} for i in range(1001)]
print(json.dumps(records))
" > /tmp/batch_1001.json
curl -s -w "\nHTTP %{http_code}\n" -X POST "$API/departments" \
  -H "Content-Type: application/json" \
  --data @/tmp/batch_1001.json