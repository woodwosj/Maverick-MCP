"""
Risky Operations Module

Contains functions with security implications that should be flagged
by the security scanner to test the approval workflow and risk assessment.
"""

import os
import subprocess
import pickle
import json
from typing import Any, Dict


def execute_command(command: str) -> str:
    """
    Execute a system command and return output.
    
    HIGH SECURITY RISK: This function executes arbitrary system commands
    which could be used maliciously. Should be flagged by security scanner
    and require user approval.
    
    Args:
        command: System command to execute
        
    Returns:
        Command output as string
        
    Raises:
        subprocess.CalledProcessError: If command fails
        
    Examples:
        >>> execute_command("echo hello")  # Safe example
        'hello\\n'
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30  # Prevent hanging
        )
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, command, result.stderr)
        return result.stdout
    except subprocess.TimeoutExpired:
        raise TimeoutError(f"Command timed out: {command}")


def read_system_file(file_path: str) -> str:
    """
    Read contents of a system file.
    
    MEDIUM SECURITY RISK: Could be used to read sensitive files.
    Should be flagged by security scanner due to file system access.
    
    Args:
        file_path: Path to file to read
        
    Returns:
        File contents as string
        
    Raises:
        FileNotFoundError: If file doesn't exist
        PermissionError: If access denied
        
    Examples:
        >>> len(read_system_file("/etc/hostname")) > 0  # Safe system file
        True
    """
    # Add some basic safety checks
    dangerous_paths = ['/etc/passwd', '/etc/shadow', '/root/', '/.ssh/']
    if any(dangerous in file_path for dangerous in dangerous_paths):
        raise PermissionError(f"Access denied to sensitive path: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # Try binary mode for non-text files
        with open(file_path, 'rb') as f:
            return f.read().decode('utf-8', errors='ignore')


def deserialize_data(pickled_data: str) -> Any:
    """
    Deserialize pickled data from base64 string.
    
    HIGH SECURITY RISK: Pickle deserialization can execute arbitrary code.
    This is a classic security vulnerability that should be caught by
    the security scanner.
    
    Args:
        pickled_data: Base64 encoded pickled data
        
    Returns:
        Deserialized object
        
    Raises:
        Various exceptions depending on pickle content
        
    Examples:
        >>> import base64, pickle
        >>> data = base64.b64encode(pickle.dumps("test")).decode()
        >>> deserialize_data(data)
        'test'
    """
    import base64
    
    try:
        binary_data = base64.b64decode(pickled_data)
        return pickle.loads(binary_data)
    except Exception as e:
        raise ValueError(f"Failed to deserialize data: {e}")


def list_directory_contents(directory: str = ".", show_hidden: bool = False) -> Dict[str, Any]:
    """
    List contents of a directory with detailed information.
    
    LOW-MEDIUM SECURITY RISK: Directory traversal could expose sensitive
    information but has some built-in protections.
    
    Args:
        directory: Directory path to list (default: current directory)
        show_hidden: Whether to include hidden files
        
    Returns:
        Dictionary with directory contents and metadata
        
    Examples:
        >>> result = list_directory_contents()
        >>> 'files' in result and 'directories' in result
        True
    """
    # Basic path validation
    if '..' in directory or directory.startswith('/etc/') or directory.startswith('/root/'):
        raise PermissionError("Access denied to potentially sensitive directory")
    
    try:
        entries = os.listdir(directory)
        if not show_hidden:
            entries = [e for e in entries if not e.startswith('.')]
        
        files = []
        directories = []
        
        for entry in entries:
            full_path = os.path.join(directory, entry)
            try:
                stat_info = os.stat(full_path)
                entry_info = {
                    'name': entry,
                    'size': stat_info.st_size,
                    'modified': stat_info.st_mtime,
                    'permissions': oct(stat_info.st_mode)[-3:]
                }
                
                if os.path.isdir(full_path):
                    directories.append(entry_info)
                else:
                    files.append(entry_info)
            except (OSError, PermissionError):
                # Skip entries we can't access
                continue
        
        return {
            'directory': directory,
            'files': files,
            'directories': directories,
            'total_items': len(files) + len(directories),
            'hidden_included': show_hidden
        }
    except OSError as e:
        raise OSError(f"Cannot access directory {directory}: {e}")


def network_request(url: str, method: str = "GET", headers: dict = None) -> dict:
    """
    Make HTTP request to external URL.
    
    MEDIUM SECURITY RISK: Could be used for SSRF attacks or data exfiltration.
    Should be flagged by security scanner due to network access.
    
    Args:
        url: URL to request
        method: HTTP method (GET, POST, etc.)
        headers: Optional HTTP headers
        
    Returns:
        Response data including status, headers, and content
        
    Examples:
        >>> # This would make an actual HTTP request - disabled in example
        >>> # network_request("https://httpbin.org/json")
        pass
    """
    import urllib.request
    import urllib.parse
    
    # Basic URL validation
    if not url.startswith(('http://', 'https://')):
        raise ValueError("Only HTTP/HTTPS URLs are allowed")
    
    # Block internal/private network requests
    blocked_hosts = ['localhost', '127.0.0.1', '0.0.0.0', '10.', '192.168.', '172.']
    parsed_url = urllib.parse.urlparse(url)
    if any(blocked in parsed_url.netloc for blocked in blocked_hosts):
        raise PermissionError("Requests to internal networks are blocked")
    
    try:
        request = urllib.request.Request(url, method=method.upper())
        if headers:
            for key, value in headers.items():
                request.add_header(key, value)
        
        with urllib.request.urlopen(request, timeout=10) as response:
            return {
                'status_code': response.status,
                'headers': dict(response.headers),
                'content': response.read().decode('utf-8', errors='ignore')[:1000],  # Limit size
                'url': response.url
            }
    except Exception as e:
        raise ConnectionError(f"Request failed: {e}")