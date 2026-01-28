#!/usr/bin/env python3
"""
WebSocket verification script.
Tests WebSocket connections and message handling.
"""

import os
import sys
import django
import time
import asyncio
from pathlib import Path
from typing import List, Dict, Any

# Setup Django
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from django.contrib.auth import get_user_model
from monitoring.models import Device, DeviceToken, Org
from monitoring.auth_utils import create_device_token
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from test_utils.verification_helpers import (
    TestSuiteResult, TestResult, TestDataGenerator
)

User = get_user_model()


def run_websocket_verification(verbose: bool = False, config: Dict = None) -> TestSuiteResult:
    """Run WebSocket verification tests."""
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
            name="Setup: Test Data",
            status="ERROR",
            message=f"Failed to create test data: {str(e)}",
            duration=0.0,
            error=str(e)
        ))
        return TestSuiteResult(
            suite_name="WebSocket",
            total_tests=len(results),
            passed=0,
            failed=0,
            skipped=0,
            errors=len(results),
            duration=time.time() - suite_start,
            results=results,
            timestamp=time.strftime('%Y-%m-%d %H:%M:%S')
        )
    
    # Test WebSocket consumers exist
    results.extend(_test_websocket_consumers(verbose))
    
    # Test WebSocket routing
    results.extend(_test_websocket_routing(verbose))
    
    # Test authentication
    results.extend(_test_websocket_authentication(verbose, device, device_token, test_user))
    
    # Cleanup
    try:
        device.delete()
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
        suite_name="WebSocket",
        total_tests=total,
        passed=passed,
        failed=failed,
        skipped=skipped,
        errors=errors,
        duration=duration,
        results=results,
        timestamp=time.strftime('%Y-%m-%d %H:%M:%S')
    )


def _test_websocket_consumers(verbose: bool) -> List[TestResult]:
    """Test WebSocket consumer classes exist."""
    results = []
    
    # Test MonitoringConsumer
    test_start = time.time()
    try:
        from monitoring.consumers import MonitoringConsumer
        assert MonitoringConsumer is not None
        results.append(TestResult(
            name="WebSocket: MonitoringConsumer",
            status="PASS",
            message="MonitoringConsumer class exists",
            duration=time.time() - test_start
        ))
    except Exception as e:
        results.append(TestResult(
            name="WebSocket: MonitoringConsumer",
            status="FAIL",
            message=f"Failed: {str(e)}",
            duration=time.time() - test_start,
            error=str(e)
        ))
    
    # Test DeviceConsumer
    test_start = time.time()
    try:
        from monitoring.consumers import DeviceConsumer
        assert DeviceConsumer is not None
        results.append(TestResult(
            name="WebSocket: DeviceConsumer",
            status="PASS",
            message="DeviceConsumer class exists",
            duration=time.time() - test_start
        ))
    except Exception as e:
        results.append(TestResult(
            name="WebSocket: DeviceConsumer",
            status="FAIL",
            message=f"Failed: {str(e)}",
            duration=time.time() - test_start,
            error=str(e)
        ))
    
    # Test AgentStreamConsumer
    test_start = time.time()
    try:
        from monitoring.consumers import AgentStreamConsumer
        assert AgentStreamConsumer is not None
        results.append(TestResult(
            name="WebSocket: AgentStreamConsumer",
            status="PASS",
            message="AgentStreamConsumer class exists",
            duration=time.time() - test_start
        ))
    except Exception as e:
        results.append(TestResult(
            name="WebSocket: AgentStreamConsumer",
            status="FAIL",
            message=f"Failed: {str(e)}",
            duration=time.time() - test_start,
            error=str(e)
        ))
    
    # Test StreamViewerConsumer
    test_start = time.time()
    try:
        from monitoring.consumers import StreamViewerConsumer
        assert StreamViewerConsumer is not None
        results.append(TestResult(
            name="WebSocket: StreamViewerConsumer",
            status="PASS",
            message="StreamViewerConsumer class exists",
            duration=time.time() - test_start
        ))
    except Exception as e:
        results.append(TestResult(
            name="WebSocket: StreamViewerConsumer",
            status="FAIL",
            message=f"Failed: {str(e)}",
            duration=time.time() - test_start,
            error=str(e)
        ))
    
    return results


def _test_websocket_routing(verbose: bool) -> List[TestResult]:
    """Test WebSocket routing configuration."""
    results = []
    
    # Test routing exists
    test_start = time.time()
    try:
        from monitoring.routing import websocket_urlpatterns
        assert websocket_urlpatterns is not None
        assert len(websocket_urlpatterns) > 0
        results.append(TestResult(
            name="WebSocket: Routing",
            status="PASS",
            message=f"WebSocket routes configured: {len(websocket_urlpatterns)}",
            duration=time.time() - test_start
        ))
    except Exception as e:
        results.append(TestResult(
            name="WebSocket: Routing",
            status="FAIL",
            message=f"Failed: {str(e)}",
            duration=time.time() - test_start,
            error=str(e)
        ))
    
    return results


def _test_websocket_authentication(verbose: bool, device, device_token, test_user) -> List[TestResult]:
    """Test WebSocket authentication."""
    results = []
    
    # Test device token authentication (code structure check)
    test_start = time.time()
    try:
        from monitoring.consumers import AgentStreamConsumer
        # Check that verify_device_token method exists
        assert hasattr(AgentStreamConsumer, 'verify_device_token')
        results.append(TestResult(
            name="WebSocket: Device Token Auth",
            status="PASS",
            message="Device token authentication method exists",
            duration=time.time() - test_start
        ))
    except Exception as e:
        results.append(TestResult(
            name="WebSocket: Device Token Auth",
            status="FAIL",
            message=f"Failed: {str(e)}",
            duration=time.time() - test_start,
            error=str(e)
        ))
    
    # Test JWT token authentication (code structure check)
    test_start = time.time()
    try:
        from monitoring.consumers import StreamViewerConsumer
        # Check that verify_token method exists
        assert hasattr(StreamViewerConsumer, 'verify_token')
        results.append(TestResult(
            name="WebSocket: JWT Token Auth",
            status="PASS",
            message="JWT token authentication method exists",
            duration=time.time() - test_start
        ))
    except Exception as e:
        results.append(TestResult(
            name="WebSocket: JWT Token Auth",
            status="FAIL",
            message=f"Failed: {str(e)}",
            duration=time.time() - test_start,
            error=str(e)
        ))
    
    return results


if __name__ == "__main__":
    result = run_websocket_verification(verbose=True)
    from test_utils.verification_helpers import ReportFormatter
    ReportFormatter.print_summary([result])
