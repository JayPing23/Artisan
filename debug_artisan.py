#!/usr/bin/env python3
"""
Comprehensive debugging script for Artisan AI Text-to-3D Generator
"""

import os
import sys
import requests
import json
import subprocess
from datetime import datetime

def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_section(title):
    print(f"\n{'-'*40}")
    print(f"  {title}")
    print(f"{'-'*40}")

def test_docker_services():
    """Test if Docker services are running"""
    print_section("Docker Services Status")
    
    try:
        result = subprocess.run(['docker-compose', 'ps'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker Compose is working")
            print(result.stdout)
        else:
            print("❌ Docker Compose failed")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Docker test failed: {e}")
        return False
    return True

def test_web_service():
    """Test if web service is responding"""
    print_section("Web Service Test")
    
    try:
        response = requests.get("http://localhost:8000", timeout=10)
        if response.status_code == 200:
            print("✅ Web service is responding")
            return True
        else:
            print(f"❌ Web service returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Web service test failed: {e}")
        return False

def test_ollama_connection():
    """Test Ollama connection from host"""
    print_section("Ollama Connection Test (Host)")
    
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        if response.status_code == 200:
            print("✅ Ollama is accessible from host")
            data = response.json()
            models = [model['name'] for model in data.get('models', [])]
            print(f"Available models: {models}")
            return True
        else:
            print(f"❌ Ollama returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ollama connection test failed: {e}")
        return False

def test_redis_connection():
    """Test Redis connection"""
    print_section("Redis Connection Test")
    
    try:
        result = subprocess.run(['docker-compose', 'exec', '-T', 'redis', 'redis-cli', 'ping'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and 'PONG' in result.stdout:
            print("✅ Redis is responding")
            return True
        else:
            print("❌ Redis test failed")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Redis test failed: {e}")
        return False

def test_worker_container():
    """Test worker container functionality"""
    print_section("Worker Container Test")
    
    try:
        # Test if worker container is running
        result = subprocess.run(['docker-compose', 'exec', '-T', 'worker', 'echo', 'Worker container is accessible'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Worker container is accessible")
            
            # Test Blender installation
            result = subprocess.run(['docker-compose', 'exec', '-T', 'worker', 'ls', '/usr/local/blender/blender'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("✅ Blender is installed")
            else:
                print("❌ Blender not found")
                return False
                
            # Test models directory
            result = subprocess.run(['docker-compose', 'exec', '-T', 'worker', 'ls', '-la', '/app/models'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("✅ Models directory exists")
                print(f"Directory contents:\n{result.stdout}")
            else:
                print("❌ Models directory not accessible")
                return False
                
            return True
        else:
            print("❌ Worker container not accessible")
            return False
    except Exception as e:
        print(f"❌ Worker container test failed: {e}")
        return False

def test_celery_worker():
    """Test Celery worker functionality"""
    print_section("Celery Worker Test")
    
    try:
        # Check if Celery worker is running
        result = subprocess.run(['docker-compose', 'exec', '-T', 'worker', 'celery', '-A', 'worker', 'inspect', 'active'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Celery worker is running")
            return True
        else:
            print("❌ Celery worker not responding")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Celery worker test failed: {e}")
        return False

def test_full_generation():
    """Test a complete generation workflow"""
    print_section("Full Generation Test")
    
    try:
        # Submit a test generation request
        test_data = {
            "prompt": "a simple red cube",
            "quality": "low"
        }
        
        print("Submitting test generation request...")
        response = requests.post("http://localhost:8000/generate", json=test_data, timeout=30)
        
        if response.status_code == 200:
            task_data = response.json()
            task_id = task_data.get('task_id')
            print(f"✅ Generation request submitted successfully")
            print(f"Task ID: {task_id}")
            
            # Poll for status
            print("Polling for status...")
            for i in range(10):  # Poll for up to 10 times
                status_response = requests.get(f"http://localhost:8000/status/{task_id}", timeout=10)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get('status')
                    print(f"Status: {status}")
                    
                    if status == 'SUCCESS':
                        print("✅ Generation completed successfully!")
                        return True
                    elif status == 'FAILED':
                        error = status_data.get('error', 'Unknown error')
                        print(f"❌ Generation failed: {error}")
                        return False
                    elif status == 'PENDING':
                        print("⏳ Still pending...")
                        import time
                        time.sleep(5)  # Wait 5 seconds before next poll
                    else:
                        print(f"❌ Unknown status: {status}")
                        return False
                else:
                    print(f"❌ Status request failed: {status_response.status_code}")
                    return False
            
            print("❌ Generation timed out")
            return False
        else:
            print(f"❌ Generation request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Full generation test failed: {e}")
        return False

def main():
    print_header("Artisan AI Text-to-3D Generator - Debug Report")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Docker Services", test_docker_services),
        ("Web Service", test_web_service),
        ("Ollama Connection", test_ollama_connection),
        ("Redis Connection", test_redis_connection),
        ("Worker Container", test_worker_container),
        ("Celery Worker", test_celery_worker),
        ("Full Generation", test_full_generation),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    print_header("Test Summary")
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    if passed == total:
        print("\n🎉 All tests passed! Your Artisan system is working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the output above for details.")
    
    print_header("Next Steps")
    if not results.get("Docker Services", False):
        print("1. Start Docker Desktop")
        print("2. Run: docker-compose up -d")
    elif not results.get("Ollama Connection", False):
        print("1. Start Ollama: ollama serve")
        print("2. Pull model: ollama pull codellama:7b")
    elif not results.get("Full Generation", False):
        print("1. Check worker logs: docker-compose logs worker")
        print("2. Check web logs: docker-compose logs web")
    else:
        print("Your system appears to be working correctly!")

if __name__ == "__main__":
    main() 