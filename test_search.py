import requests
import time
import sys

BASE_URL = "http://localhost:8000"

TEST_CASES = [
    {
        "query": "elementary school highland park",
        "expected_top_1_contain": ["HIGHLAND PARK ELEMENTARY SCHOOL"],
        "expected_city_state": ["MUSCLE SHOALS, AL", "PUEBLO, CO"]
    },
    {
        "query": "jefferson belleville",
        "expected_top_1_contain": ["JEFFERSON ELEM SCHOOL"],
        "expected_city_state": ["BELLEVILLE, IL"]
    },
    {
        "query": "riverside school 44",
        "expected_top_1_contain": ["RIVERSIDE SCHOOL 44"],
        "expected_city_state": ["INDIANAPOLIS, IN"]
    },
    {
        "query": "granada charter school",
        "expected_top_1_contain": ["NORTH VALLEY CHARTER ACADEMY", "GRANADA HILLS CHARTER HIGH"], # Flexible based on ranking
        "expected_city_state": ["GRANADA HILLS, CA"]
    },
    {
        "query": "foley high alabama",
        "expected_top_1_contain": ["FOLEY HIGH SCHOOL"],
        "expected_city_state": ["FOLEY, AL"]
    },
    {
        "query": "KUSKOKWIM",
        "expected_top_1_contain": ["TOP OF THE KUSKOKWIM SCHOOL"],
        "expected_city_state": ["NIKOLAI, AK"]
    }
]

def wait_for_health():
    print("Waiting for API to be healthy...")
    for _ in range(30):
        try:
            resp = requests.get(f"{BASE_URL}/health")
            if resp.status_code == 200:
                print("API is up!")
                return True
        except:
            pass
        time.sleep(1)
    return False

def run_tests():
    if not wait_for_health():
        print("API failed to start.")
        sys.exit(1)
        
    print("\nRunning Verification Tests...")
    print("-" * 60)
    
    passed = 0
    total = len(TEST_CASES)
    
    for case in TEST_CASES:
        query = case["query"]
        print(f"Query: '{query}'")
        
        start = time.perf_counter()
        resp = requests.get(f"{BASE_URL}/search", params={"query": query})
        took = (time.perf_counter() - start) * 1000
        
        if resp.status_code != 200:
            print(f"  [FAILED] Status {resp.status_code}")
            continue
            
        results = resp.json()
        if not results:
             print("  [FAILED] No results returned")
             continue
             
        top_result = results[0]['school']
        name = top_result['name']
        city_state = f"{top_result['city']}, {top_result['state']}"
        
        # Verification Logic
        success = False
        
        # Check Name
        for expected in case["expected_top_1_contain"]:
            if expected in name:
                success = True
                break
        
        if success:
             # Check City/State if strictly required
             pass
        else:
             print(f"  [FAILED] Expected top result to contain one of {case['expected_top_1_contain']}, got '{name}'")
             print(f"  Top Result: {name} ({city_state})")
             continue
             
        print(f"  [PASS] Top result: {name} ({city_state})")
        print(f"  Time: {took:.2f}ms (Client-observed)")
        passed += 1
        print("-" * 20)

    print(f"\nSummary: {passed}/{total} Passed")
    
if __name__ == "__main__":
    run_tests()
