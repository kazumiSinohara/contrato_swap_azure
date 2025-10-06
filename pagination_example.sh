#!/bin/bash

# Contract Pagination Example
# ==========================
#
# This script demonstrates how to paginate through contracts
# even though our current dataset (50 contracts) fits in one page.

echo "📄 CONTRACT PAGINATION EXAMPLE"
echo "=============================="

# Configuration
BASE_URL="https://functions-contratos.azurewebsites.net/api"
FUNCTION_KEY="lYzrDH1uEUjIdH34UmMxFL0SQ64FCd7yHsIoQ8AD7Ye7AzFugo8seg=="

# Function to get one page of contracts
get_contracts_page() {
    local page_size=$1
    local continuation_token=$2

    local url="$BASE_URL/ListContracts?pageSize=$page_size"
    if [ -n "$continuation_token" ]; then
        # URL encode the continuation token (it contains special characters)
        encoded_token=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$continuation_token', safe=''))")
        url="$url&continuationToken=$encoded_token"
    fi

    curl -s -H "x-functions-key: $FUNCTION_KEY" "$url"
}

# Function to paginate through all contracts
paginate_contracts() {
    local page_size=$1
    local continuation_token=""
    local page_number=1
    local total_contracts=0

    echo "🔄 Starting pagination with pageSize=$page_size"
    echo ""

    while true; do
        echo "📄 Fetching page $page_number..."

        # Get the page
        response=$(get_contracts_page "$page_size" "$continuation_token")

        # Extract data
        items_count=$(echo "$response" | jq '.items | length')
        total_contracts=$((total_contracts + items_count))

        echo "   📊 Page $page_number: $items_count contracts (running total: $total_contracts)"

        # Check for continuation token
        next_token=$(echo "$response" | jq -r '.continuationToken // empty')

        if [ -z "$next_token" ] || [ "$next_token" = "null" ]; then
            echo "   ✅ No more pages - pagination complete!"
            break
        else
            echo "   🔗 Next page token available"
            continuation_token="$next_token"
            page_number=$((page_number + 1))
        fi

        echo ""
    done

    echo ""
    echo "🎯 SUMMARY:"
    echo "   📊 Total contracts retrieved: $total_contracts"
    echo "   📄 Total pages: $page_number"
    echo "   📏 Page size: $page_size"
}

# Demonstrate pagination with different page sizes
echo "🧪 DEMONSTRATION:"
echo ""

echo "1️⃣ Testing with pageSize=10 (should create 5 pages with our 50 contracts):"
paginate_contracts 10

echo ""
echo "2️⃣ Testing with pageSize=25 (should create 2 pages):"
paginate_contracts 25

echo ""
echo "3️⃣ Testing with pageSize=50 (should fit all in 1 page):"
paginate_contracts 50

echo ""
echo "🎯 PAGINATION BEST PRACTICES:"
echo "• Use pageSize=100 for bulk operations"
echo "• Use pageSize=20 for user interfaces"
echo "• Always check for continuationToken"
echo "• Handle URL encoding for continuation tokens"
echo "• Stop when continuationToken is null/empty"
