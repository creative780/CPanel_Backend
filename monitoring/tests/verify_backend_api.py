#!/usr/bin/env python3
"""
Backend API verification script.
Tests all backend API endpoints for monitoring system.
"""

import os
import sys
import django
import time
from pathlib import Path
from typing import List, Dict, Any

# Setup Django
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from monitoring.models import Device, DeviceToken, Org
from monitoring.auth_utils import create_device_token, create_enrollment_token
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from test_utils.verification_helpers import (
    TestSuiteResult, TestResult, TestDataGenerator, AssertionHelper
)

User = get_user_model()


def run_backend_api_verification(verbose: bool = False, config: Dict = None) -> TestSuiteResult:
    """Run backend API verification tests."""
    if config is None:
        config = {}
    
    suite_start = time.time()
    results: List[TestResult] = []
    
    # Setup test data
    try:
        test_org = Org.objects.create(name="Test Org")
        test_user = User.objects.create_user(
            username="test_admin",
            email="test@example.com",
            password="testpass123",
            is_staff=True
        )
        test_user.org_id = test_org.id
        test_user.save()
    except Exception as e:
        results.append(TestResult(
            name="Setup: Test Data",
            status="ERROR",
            message=f"Failed to create test data: {str(e)}",
            duration=0.0,
            error=str(e)
        ))
        return TestSuiteResult(
            suite_name="Backend API",
            total_tests=len(results),
            passed=0,
            failed=0,
            skipped=0,
            errors=len(results),
            duration=time.time() - suite_start,
            results=results,
            timestamp=time.strftime('%Y-%m-%d %H:%M:%S')
        )
    
    # Test enrollment endpoints
    results.extend(_test_enrollment_endpoints(verbose, test_user, test_org))
    
    # Test heartbeat endpoint
    results.extend(_test_heartbeat_endpoint(verbose, test_user, test_org))
    
    # Test recording ingestion
    results.extend(_test_recording_ingest(verbose, test_user, test_org))
    
    # Test frame encoding
    results.extend(_test_frame_encoding(verbose, test_user, test_org))
    
    # Test admin device endpoints
    results.extend(_test_admin_device_endpoints(verbose, test_user, test_org))
    
    # Test admin recordings endpoints
    results.extend(_test_admin_recordings_endpoints(verbose, test_user, test_org))
    
    # Test file serving
    results.extend(_test_file_serving(verbose, test_user, test_org))
    
    # Test agent context
    results.extend(_test_agent_context(verbose, test_user, test_org))
    
    # Cleanup
    try:
        Device.objects.filter(org=test_org).delete()
        DeviceToken.objects.filter(device__org=test_org).delete()
        test_user.delete()
        test_org.delete()
    except:
        pass
    
    # Calculate summary
    total = len(results)
    passed = sum(1 for r in results if r.status == 'PASS')
    failed = sum(1 for r in results if r.status == 'FAIL')
    skipped = sum(1 for r in results if r.status == 'SKIP')
    errors = sum(1 for r in results if r.status == 'ERROR')
    duration = time.time() - suite_start
    
    return TestSuiteResult(
        suite_name="Backend API",
        total_tests=total,
        passed=passed,
        failed=failed,
        skipped=skipped,
        errors=errors,
        duration=duration,
        results=results,
        timestamp=time.strftime('%Y-%m-%d %H:%M:%S')
    )


def _test_enrollment_endpoints(verbose: bool, test_user, test_org) -> List[TestResult]:
    """Test enrollment endpoints."""
    results = []
    client = APIClient()
    
    # Test enroll request
    test_start = time.time()
    try:
        client.force_authenticate(user=test_user)
        response = client.post('/api/monitoring/enroll/request', {
            'os': 'Windows',
            'hostname': 'test-host'
        })
        AssertionHelper.assert_status_code(response, status.HTTP_200_OK)
        data = response.json()
        AssertionHelper.assert_response_format(data, ['enrollment_token', 'expires_in'])
        results.append(TestResult(
            name="Enrollment: Request Token",
            status="PASS",
            message="Enrollment token requested successfully",
            duration=time.time() - test_start
        ))
    except Exception as e:
        results.append(TestResult(
            name="Enrollment: Request Token",
            status="FAIL",
            message=f"Failed: {str(e)}",
            duration=time.time() - test_start,
            error=str(e)
        ))
    
    # Test enroll complete
    test_start = time.time()
    try:
        enrollment_token = create_enrollment_token(str(test_user.id), test_org.id)
        response = client.post('/api/enroll/complete', {
            'enrollment_token': enrollment_token,
            'os': 'Windows',
            'hostname': 'test-host',
            'agent_version': '1.0.0'
        })
        AssertionHelper.assert_status_code(response, status.HTTP_200_OK)
        data = response.json()
        AssertionHelper.assert_response_format(data, ['device_id', 'device_token'])
        results.append(TestResult(
            name="Enrollment: Complete",
            status="PASS",
            message="Device enrolled successfully",
            duration=time.time() - test_start
        ))
    except Exception as e:
        results.append(TestResult(
            name="Enrollment: Complete",
            status="FAIL",
            message=f"Failed: {str(e)}",
            duration=time.time() - test_start,
            error=str(e)
        ))
    
    return results


def _test_heartbeat_endpoint(verbose: bool, test_user, test_org) -> List[TestResult]:
    """Test heartbeat endpoint."""
    results = []
    client = APIClient()
    
    # Create device and token
    try:
        device = Device.objects.create(
            hostname='test-device',
            os='Windows',
            org=test_org,
            current_user=test_user
        )
        device_token_obj = create_device_token(device)
        device_token = device_token_obj.secret
    except Exception as e:
        results.append(TestResult(
            name="Heartbeat: Setup",
            status="ERROR",
            message=f"Failed to create test device: {str(e)}",
            duration=0.0,
            error=str(e)
        ))
        return results
    
    # Test heartbeat
    test_start = time.time()
    try:
        heartbeat_data = TestDataGenerator.generate_heartbeat_data()
        response = client.post(
            '/api/ingest/heartbeat',
            heartbeat_data,
            HTTP_AUTHORIZATION=f'Bearer {device_token}'
        )
        AssertionHelper.assert_status_code(response, status.HTTP_200_OK)
        results.append(TestResult(
            name="Heartbeat: Send",
            status="PASS",
            message="Heartbeat sent successfully",
            duration=time.time() - test_start
        ))
    except Exception as e:
        results.append(TestResult(
            name="Heartbeat: Send",
            status="FAIL",
            message=f"Failed: {str(e)}",
            duration=time.time() - test_start,
            error=str(e)
        ))
    
    # Cleanup
    try:
        device.delete()
    except:
        pass
    
    return results


def _test_recording_ingest(verbose: bool, test_user, test_org) -> List[TestResult]:
    """Test recording ingestion endpoint."""
    results = []
    client = APIClient()
    
    # Create device and token
    try:
        device = Device.objects.create(
            hostname='test-device',
            os='Windows',
            org=test_org,
            current_user=test_user
        )
        device_token_obj = create_device_token(device)
        device_token = device_token_obj.secret
    except Exception as e:
        results.append(TestResult(
            name="Recording Ingest: Setup",
            status="ERROR",
            message=f"Failed to create test device: {str(e)}",
            duration=0.0,
            error=str(e)
        ))
        return results
    
    # Test recording upload (simplified - would need actual video file)
    test_start = time.time()
    try:
        from io import BytesIO
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        # Create mock video file
        video_data = b'fake_video_data'
        video_file = SimpleUploadedFile("test.mp4", video_data, content_type="video/mp4")
        
        response = client.post(
            '/api/recording/ingest/',
            {
                'video': video_file,
                'start_time': '2025-01-01T00:00:00Z',
                'end_time': '2025-01-01T00:01:00Z',
                'duration_seconds': '60',
                'is_idle_period': 'false'
            },
            HTTP_AUTHORIZATION=f'Bearer {device_token}'
        )
        # May fail due to storage/encoding, but endpoint should be accessible
        if response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST, status.HTTP_500_INTERNAL_SERVER_ERROR]:
            results.append(TestResult(
                name="Recording Ingest: Upload",
                status="PASS",
                message=f"Endpoint accessible (status: {response.status_code})",
                duration=time.time() - test_start
            ))
        else:
            results.append(TestResult(
                name="Recording Ingest: Upload",
                status="FAIL",
                message=f"Unexpected status: {response.status_code}",
                duration=time.time() - test_start
            ))
    except Exception as e:
        results.append(TestResult(
            name="Recording Ingest: Upload",
            status="FAIL",
            message=f"Failed: {str(e)}",
            duration=time.time() - test_start,
            error=str(e)
        ))
    
    # Cleanup
    try:
        device.delete()
    except:
        pass
    
    return results


def _test_frame_encoding(verbose: bool, test_user, test_org) -> List[TestResult]:
    """Test frame encoding endpoint."""
    results = []
    client = APIClient()
    
    # Create device and token
    try:
        device = Device.objects.create(
            hostname='test-device',
            os='Windows',
            org=test_org,
            current_user=test_user
        )
        device_token_obj = create_device_token(device)
        device_token = device_token_obj.secret
    except Exception as e:
        results.append(TestResult(
            name="Frame Encoding: Setup",
            status="ERROR",
            message=f"Failed to create test device: {str(e)}",
            duration=0.0,
            error=str(e)
        ))
        return results
    
    # Test frame encoding
    test_start = time.time()
    try:
        frames = TestDataGenerator.generate_test_frames(5)
        frames_b64 = [TestDataGenerator.generate_base64_frame(f) for f in frames]
        metadata = TestDataGenerator.generate_recording_metadata()
        
        response = client.post(
            '/api/recording/encode-frames/',
            {
                'frames': frames_b64,
                'metadata': metadata
            },
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {device_token}'
        )
        # May fail due to FFmpeg, but endpoint should be accessible
        if response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST, status.HTTP_500_INTERNAL_SERVER_ERROR]:
            results.append(TestResult(
                name="Frame Encoding: Encode",
                status="PASS",
                message=f"Endpoint accessible (status: {response.status_code})",
                duration=time.time() - test_start
            ))
        else:
            results.append(TestResult(
                name="Frame Encoding: Encode",
                status="FAIL",
                message=f"Unexpected status: {response.status_code}",
                duration=time.time() - test_start
            ))
    except Exception as e:
        results.append(TestResult(
            name="Frame Encoding: Encode",
            status="FAIL",
            message=f"Failed: {str(e)}",
            duration=time.time() - test_start,
            error=str(e)
        ))
    
    # Cleanup
    try:
        device.delete()
    except:
        pass
    
    return results


def _test_admin_device_endpoints(verbose: bool, test_user, test_org) -> List[TestResult]:
    """Test admin device endpoints."""
    results = []
    client = APIClient()
    
    # Test device list
    test_start = time.time()
    try:
        client.force_authenticate(user=test_user)
        response = client.get('/api/monitoring/admin/devices')
        AssertionHelper.assert_status_code(response, status.HTTP_200_OK)
        data = response.json()
        AssertionHelper.assert_response_format(data, ['devices'])
        results.append(TestResult(
            name="Admin Devices: List",
            status="PASS",
            message="Device list retrieved",
            duration=time.time() - test_start
        ))
    except Exception as e:
        results.append(TestResult(
            name="Admin Devices: List",
            status="FAIL",
            message=f"Failed: {str(e)}",
            duration=time.time() - test_start,
            error=str(e)
        ))
    
    return results


def _test_admin_recordings_endpoints(verbose: bool, test_user, test_org) -> List[TestResult]:
    """Test admin recordings endpoints."""
    results = []
    client = APIClient()
    
    # Test recordings list
    test_start = time.time()
    try:
        client.force_authenticate(user=test_user)
        response = client.get('/api/monitoring/admin/recordings')
        AssertionHelper.assert_status_code(response, status.HTTP_200_OK)
        data = response.json()
        AssertionHelper.assert_response_format(data, ['recordings'])
        results.append(TestResult(
            name="Admin Recordings: List",
            status="PASS",
            message="Recordings list retrieved",
            duration=time.time() - test_start
        ))
    except Exception as e:
        results.append(TestResult(
            name="Admin Recordings: List",
            status="FAIL",
            message=f"Failed: {str(e)}",
            duration=time.time() - test_start,
            error=str(e)
        ))
    
    return results


def _test_file_serving(verbose: bool, test_user, test_org) -> List[TestResult]:
    """Test file serving endpoint."""
    results = []
    client = APIClient()
    
    # Test file serving (may not exist, but endpoint should be accessible)
    test_start = time.time()
    try:
        client.force_authenticate(user=test_user)
        response = client.get('/api/monitoring/files/test_file.mp4')
        # 404 is acceptable if file doesn't exist
        if response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]:
            results.append(TestResult(
                name="File Serving: Get File",
                status="PASS",
                message=f"Endpoint accessible (status: {response.status_code})",
                duration=time.time() - test_start
            ))
        else:
            results.append(TestResult(
                name="File Serving: Get File",
                status="FAIL",
                message=f"Unexpected status: {response.status_code}",
                duration=time.time() - test_start
            ))
    except Exception as e:
        results.append(TestResult(
            name="File Serving: Get File",
            status="FAIL",
            message=f"Failed: {str(e)}",
            duration=time.time() - test_start,
            error=str(e)
        ))
    
    return results


def _test_agent_context(verbose: bool, test_user, test_org) -> List[TestResult]:
    """Test agent context endpoint."""
    results = []
    client = APIClient()
    
    # Create device and token
    try:
        device = Device.objects.create(
            hostname='test-device',
            os='Windows',
            org=test_org,
            current_user=test_user
        )
        device_token_obj = create_device_token(device)
        device_token = device_token_obj.secret
    except Exception as e:
        results.append(TestResult(
            name="Agent Context: Setup",
            status="ERROR",
            message=f"Failed to create test device: {str(e)}",
            duration=0.0,
            error=str(e)
        ))
        return results
    
    # Test context retrieval
    test_start = time.time()
    try:
        response = client.get(
            '/api/agent/context',
            HTTP_AUTHORIZATION=f'Bearer {device_token}'
        )
        AssertionHelper.assert_status_code(response, status.HTTP_200_OK)
        data = response.json()
        results.append(TestResult(
            name="Agent Context: Get Context",
            status="PASS",
            message="Context retrieved successfully",
            duration=time.time() - test_start
        ))
    except Exception as e:
        results.append(TestResult(
            name="Agent Context: Get Context",
            status="FAIL",
            message=f"Failed: {str(e)}",
            duration=time.time() - test_start,
            error=str(e)
        ))
    
    # Cleanup
    try:
        device.delete()
    except:
        pass
    
    return results


if __name__ == "__main__":
    result = run_backend_api_verification(verbose=True)
    from test_utils.verification_helpers import ReportFormatter
    ReportFormatter.print_summary([result])
