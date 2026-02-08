

import requests
import json

BASE_URL = "http://localhost:800133333333"


def test_root():
    print("\n" + "=" * 60)
    print("TEST 1: Root Endpoint")
    print("=" * 60)

    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Failed: {e}")
        print("   Make sure backend is running: uvicorn api:app --reload")


def test_health():
    print("\n" + "=" * 60)
    print("TEST 2: Health Check")
    print("=" * 60)

    try:
        response = requests.get(f"{BASE_URL}/api/health")
        data = response.json()
        print(f"Status: {response.status_code}")
        print(f"Components: {data['components']}")
    except Exception as e:
        print(f"Failed: {e}")


def test_samples():
    print("\n" + "=" * 60)
    print("TEST 3: Get Samples")
    print("=" * 60)

    try:
        response = requests.get(f"{BASE_URL}/api/samples")
        data = response.json()
        print(f"Status: {response.status_code}")
        print(f"Found {data['count']} samples:")
        for sample in data['samples']:
            print(f"   - {sample['company']}: {sample['overall_score']}/10")
    except Exception as e:
        print(f"Failed: {e}")


def test_sample_detail():
    print("\n" + "=" * 60)
    print("TEST 4: Get Sample Detail")
    print("=" * 60)

    try:
        response = requests.get(f"{BASE_URL}/api/sample/techcorp_q3_2025")
        data = response.json()
        print(f"Status: {response.status_code}")
        print(f"Company: {data['company']}")
        print(f"Overall Score: {data['consensus']['overall_score']}/10")
        print(f"Verdict: {data['consensus']['verdict']}")
    except Exception as e:
        print(f"Failed: {e}")


def test_analyze_text():
    print("\n" + "=" * 60)
    print("TEST 5: Analyze Text (Full AI Analysis)")
    print("=" * 60)

    sample_transcript = """
    Q3 2025 Earnings Call - Test Company Inc.

    CEO: I'm pleased to report revenue of $3.2 billion, up 18% year-over-year.
    This beat analyst estimates of $3.0 billion. We added 800 new customers.

    CFO: Gross margin came in at 68%, down from 71% last quarter due to 
    infrastructure investments. Operating margin was 15%. Free cash flow 
    was strong at $450 million.

    Q&A: We're confident about Q4 and expect continued growth momentum.
    """

    try:
        print("Sending transcript to backend...")
        response = requests.post(
            f"{BASE_URL}/api/analyze",
            json={"text": sample_transcript},
            timeout=30  # AI analysis can take time
        )

        if response.status_code != 200:
            print(f"❌ Error: {response.status_code}")
            print(f"   {response.text}")
            return

        data = response.json()

        print(f" Status: {response.status_code}")
        print(f"\n RESULTS:")
        print(f"   Overall Score: {data['consensus']['overall_score']}/10")
        print(f"   Verdict: {data['consensus']['verdict']}")
        print(f"   Confidence: {data['consensus']['confidence']}")
        print(f"\n   Agent Scores:")
        print(f"   - Revenue: {data['detailed_analysis']['revenue']['score']}/10")
        print(f"   - Profitability: {data['detailed_analysis']['profitability']['score']}/10")
        print(f"   - Management: {data['detailed_analysis']['management']['score']}/10")

    except requests.exceptions.Timeout:
        print(f"  Timeout: Analysis took too long (>30s)")
        print(f"   This is normal for first Ollama run")
    except Exception as e:
        print(f" Failed: {e}")


def test_invalid_input():
    print("\n" + "=" * 60)
    print("TEST 6: Error Handling")
    print("=" * 60)

    try:
        # Test with too-short text
        response = requests.post(
            f"{BASE_URL}/api/analyze",
            json={"text": "Short"}
        )

        if response.status_code == 400:
            print(f" Correctly rejected short input")
            print(f"   Error: {response.json()['detail']}")
        else:
            print(f"  Expected 400 error, got {response.status_code}")
    except Exception as e:
        print(f" Failed: {e}")


def run_all_tests():
    print("\n" + "=" * 60)
    print("EARNINGS ANALYZER API - TEST SUITE")
    print("=" * 60)
    print(f"\nTesting backend at: {BASE_URL}")
    print("Make sure backend is running first!")
    print("=" * 60)

    # Run tests
    test_root()
    test_health()
    test_samples()
    test_sample_detail()
    test_analyze_text()
    test_invalid_input()

    print("\n" + "=" * 60)
    print(" ALL TESTS COMPLETE")
    print("=" * 60)
    print("\nIf all tests passed, backend is working correctly!")
    print("You can now connect your frontend.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_all_tests()