"""
Simple test script for LMS Backend API
"""
import requests
import json
import time


def test_basic_endpoints():
    """Test basic API endpoints"""
    base_url = "http://localhost:8000"
    
    print("Testing LMS Backend API...")
    print("=" * 50)
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/")
        print(f"✓ Root endpoint: {response.status_code}")
        print(f"  Response: {response.json()}")
    except Exception as e:
        print(f"✗ Root endpoint failed: {e}")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✓ Health endpoint: {response.status_code}")
        print(f"  Response: {response.json()}")
    except Exception as e:
        print(f"✗ Health endpoint failed: {e}")
    
    # Test API v1 health endpoint
    try:
        response = requests.get(f"{base_url}/api/v1/health")
        print(f"✓ API v1 health endpoint: {response.status_code}")
        print(f"  Response: {response.json()}")
    except Exception as e:
        print(f"✗ API v1 health endpoint failed: {e}")
    
    # Test OpenAPI docs
    try:
        response = requests.get(f"{base_url}/openapi.json")
        print(f"✓ OpenAPI docs: {response.status_code}")
        print(f"  OpenAPI title: {response.json().get('info', {}).get('title', 'N/A')}")
    except Exception as e:
        print(f"✗ OpenAPI docs failed: {e}")
    
    print("=" * 50)
    print("Basic API testing completed!")


if __name__ == "__main__":
    test_basic_endpoints()

