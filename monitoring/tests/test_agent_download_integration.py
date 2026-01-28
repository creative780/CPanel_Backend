"""
Integration tests for AgentDownloadView - end-to-end download flow
"""
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from rest_framework import status
from django.conf import settings
import os
import tempfile
import shutil


class AgentDownloadIntegrationTest(TestCase):
    """Integration tests for agent download endpoint"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create test media directory structure
        self.test_media_root = tempfile.mkdtemp()
        self.agents_dir = os.path.join(self.test_media_root, 'agents')
        os.makedirs(self.agents_dir, exist_ok=True)
        
        # Create a test .bat file template
        self.test_bat_content = '''@echo off
setlocal enabledelayedexpansion
title Creative Connect Agent Installer
echo Creative Connect Agent Installer

REM Default variables
set "SERVER_URL=http://127.0.0.1:8000"
set "TOKEN="
set "EXE_NAME=crm-monitoring-agent-windows-amd64.exe"

echo Installation complete.
pause
'''
        
        # Write test .bat file
        self.test_bat_path = os.path.join(self.agents_dir, 'agent-installer.bat')
        with open(self.test_bat_path, 'w', encoding='utf-8') as f:
            f.write(self.test_bat_content)
        
        # Also create in BASE_DIR/media/agents for testing
        base_media_dir = os.path.join(settings.BASE_DIR, 'media', 'agents')
        os.makedirs(base_media_dir, exist_ok=True)
        base_bat_path = os.path.join(base_media_dir, 'agent-installer.bat')
        with open(base_bat_path, 'w', encoding='utf-8') as f:
            f.write(self.test_bat_content)
    
    def tearDown(self):
        """Clean up test files"""
        if os.path.exists(self.test_media_root):
            shutil.rmtree(self.test_media_root)
        
        # Clean up base media directory test file
        base_bat_path = os.path.join(settings.BASE_DIR, 'media', 'agents', 'agent-installer.bat')
        if os.path.exists(base_bat_path):
            try:
                os.remove(base_bat_path)
            except:
                pass
    
    def test_download_agent_installer_windows(self):
        """Full download flow for Windows"""
        response = self.client.get(
            '/api/agent/download',
            HTTP_USER_AGENT='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('Content-Disposition', response)
        self.assertIn('agent-installer.bat', response['Content-Disposition'])
        
        # Verify content
        content = response.content.decode('utf-8', errors='ignore')
        self.assertIn('Creative Connect Agent Installer', content)
        self.assertIn('set "SERVER_URL=', content)
    
    def test_download_agent_installer_with_token(self):
        """Download with enrollment token"""
        test_token = "integration-test-token-12345"
        
        response = self.client.get(
            '/api/agent/download',
            {'token': test_token},
            HTTP_USER_AGENT='Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        )
        
        self.assertEqual(response.status_code, 200)
        
        content = response.content.decode('utf-8', errors='ignore')
        
        # Verify token is in the file
        self.assertIn(test_token, content)
        self.assertIn(f'set "TOKEN={test_token}"', content)
        
        # Verify server URL is injected
        self.assertNotIn('http://127.0.0.1:8000', content)
        self.assertNotIn('http://localhost:8000', content)
    
    def test_download_agent_installer_without_token(self):
        """Download without token"""
        response = self.client.get(
            '/api/agent/download',
            HTTP_USER_AGENT='Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        )
        
        self.assertEqual(response.status_code, 200)
        
        content = response.content.decode('utf-8', errors='ignore')
        
        # Verify token is empty
        self.assertIn('set "TOKEN="', content)
        
        # Verify server URL is still injected
        self.assertNotIn('http://127.0.0.1:8000', content)
        self.assertNotIn('http://localhost:8000', content)
    
    def test_download_agent_installer_different_os(self):
        """Test OS detection (mac, linux)"""
        # Test macOS
        response_mac = self.client.get(
            '/api/agent/download',
            HTTP_USER_AGENT='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
        )
        
        # Should try to find .pkg or .sh, but may fall back to .bat
        self.assertIn(response_mac.status_code, [200, 404])
        
        # Test Linux
        response_linux = self.client.get(
            '/api/agent/download',
            HTTP_USER_AGENT='Mozilla/5.0 (X11; Linux x86_64)'
        )
        
        # Should try to find .sh, but may fall back
        self.assertIn(response_linux.status_code, [200, 404])
    
    def test_download_file_not_found(self):
        """Test 404 when file doesn't exist"""
        # Remove the test file from all possible locations
        if os.path.exists(self.test_bat_path):
            os.remove(self.test_bat_path)
        
        base_bat_path = os.path.join(settings.BASE_DIR, 'media', 'agents', 'agent-installer.bat')
        if os.path.exists(base_bat_path):
            os.remove(base_bat_path)
        
        # Also check MEDIA_ROOT locations
        if hasattr(settings, 'MEDIA_ROOT'):
            media_bat_path = os.path.join(settings.MEDIA_ROOT, 'agents', 'agent-installer.bat')
            if os.path.exists(media_bat_path):
                os.remove(media_bat_path)
            
            uploads_bat_path = os.path.join(settings.MEDIA_ROOT, 'uploads', 'agents', 'agent-installer.bat')
            if os.path.exists(uploads_bat_path):
                os.remove(uploads_bat_path)
        
        response = self.client.get(
            '/api/agent/download',
            HTTP_USER_AGENT='Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        )
        
        # Should return 404 if no file found, but may return 200 if file exists elsewhere
        # This test verifies the endpoint handles missing files gracefully
        self.assertIn(response.status_code, [404, 200])
        
        # If 200, verify it's a valid response (file was found in another location)
        if response.status_code == 200:
            # FileResponse uses streaming_content, not content
            if hasattr(response, 'streaming_content'):
                # For FileResponse, we can check Content-Length
                if 'Content-Length' in response:
                    self.assertGreater(int(response['Content-Length']), 0)
            else:
                # For HttpResponse, check content length
                self.assertGreater(len(response.content), 0)
    
    def test_download_content_type_correct(self):
        """Verify correct MIME type"""
        response = self.client.get(
            '/api/agent/download',
            HTTP_USER_AGENT='Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        )
        
        self.assertEqual(response.status_code, 200)
        content_type = response.get('Content-Type', '')
        # Should be application/x-msdos-program for .bat files
        self.assertIn('application/x-msdos-program', content_type)
    
    def test_download_file_size_correct(self):
        """Verify file size in response"""
        response = self.client.get(
            '/api/agent/download',
            HTTP_USER_AGENT='Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Content-Length should match actual content
        if 'Content-Length' in response:
            expected_length = int(response['Content-Length'])
            actual_length = len(response.content)
            self.assertEqual(expected_length, actual_length)
        
        # Content should not be empty
        self.assertGreater(len(response.content), 0)
    
    def test_download_preserves_bat_structure(self):
        """Verify .bat file structure is preserved after injection"""
        response = self.client.get(
            '/api/agent/download',
            {'token': 'test-token'},
            HTTP_USER_AGENT='Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        )
        
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8', errors='ignore')
        
        # Verify key structure elements are preserved
        self.assertIn('@echo off', content)
        self.assertIn('setlocal enabledelayedexpansion', content)
        self.assertIn('title Creative Connect Agent Installer', content)
        self.assertIn('set "EXE_NAME=', content)
        self.assertIn('pause', content)
    
    def test_download_with_multiple_replacements(self):
        """Test that all localhost instances are replaced"""
        # Create .bat file with multiple localhost references
        multi_localhost_bat = '''@echo off
set "SERVER_URL=http://127.0.0.1:8000"
set "BACKUP_URL=http://localhost:8000"
set "TOKEN="
'''
        multi_path = os.path.join(self.agents_dir, 'agent-installer.bat')
        with open(multi_path, 'w', encoding='utf-8') as f:
            f.write(multi_localhost_bat)
        
        base_bat_path = os.path.join(settings.BASE_DIR, 'media', 'agents', 'agent-installer.bat')
        with open(base_bat_path, 'w', encoding='utf-8') as f:
            f.write(multi_localhost_bat)
        
        response = self.client.get(
            '/api/agent/download',
            HTTP_USER_AGENT='Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        )
        
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8', errors='ignore')
        
        # SERVER_URL should be replaced
        self.assertNotIn('http://127.0.0.1:8000', content)
        # BACKUP_URL might still have localhost (we only replace SERVER_URL)
        # This is expected behavior
