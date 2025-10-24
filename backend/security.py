import re
import json
from typing import Dict, Any, List
from fastapi import Request
import logging

logger = logging.getLogger(__name__)

class SecurityInspector:
    """Main security inspection class for WAF functionality"""
    
    def __init__(self):
        self.sql_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|SCRIPT)\b)",
            r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
            r"(\b(OR|AND)\s+['\"]?\w+['\"]?\s*=\s*['\"]?\w+['\"]?)",
            r"(\bUNION\s+SELECT\b)",
            r"(\bDROP\s+TABLE\b)",
            r"(\bDELETE\s+FROM\b)",
            r"(\bINSERT\s+INTO\b)",
            r"(\bUPDATE\s+SET\b)",
            r"(\bEXEC\s*\()",
            r"(\bSCRIPT\b)",
            r"(\bEVAL\b)",
            r"(\bEXPR\b)",
        ]
        
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>",
            r"<link[^>]*>",
            r"<meta[^>]*>",
            r"<style[^>]*>.*?</style>",
            r"expression\s*\(",
            r"url\s*\(",
            r"@import",
            r"vbscript:",
            r"data:text/html",
            r"data:application/javascript",
        ]
        
        self.command_injection_patterns = [
            r"(\||;|\$\(|\`|\$\{)",
            r"(\b(cat|ls|pwd|whoami|id|uname|ps|netstat|ifconfig)\b)",
            r"(\b(rm|mv|cp|chmod|chown|kill|killall)\b)",
            r"(\b(wget|curl|nc|netcat|telnet|ssh|ftp)\b)",
            r"(\b(bash|sh|cmd|powershell|python|perl|ruby)\b)",
            r"(\b(echo|print|printf|sprintf)\b)",
            r"(\b(exec|system|shell_exec|passthru|eval)\b)",
            r"(\b(import|require|include|load)\b)",
        ]
        
        self.path_traversal_patterns = [
            r"\.\./",
            r"\.\.\\",
            r"\.\.%2f",
            r"\.\.%5c",
            r"\.\.%252f",
            r"\.\.%255c",
            r"\.\.%c0%af",
            r"\.\.%c1%9c",
            r"\.\.%c0%2f",
            r"\.\.%c1%9c",
            r"\.\.%252e%252e%252f",
            r"\.\.%252e%252e%255c",
        ]
        
        self.suspicious_headers = [
            "x-forwarded-for",
            "x-real-ip",
            "x-originating-ip",
            "x-remote-ip",
            "x-remote-addr",
            "x-client-ip",
            "x-cluster-client-ip",
            "x-forwarded",
            "forwarded-for",
            "forwarded",
        ]
        
        self.blocked_extensions = [
            ".php", ".asp", ".aspx", ".jsp", ".py", ".pl", ".sh", ".bat", ".cmd",
            ".exe", ".dll", ".so", ".dylib", ".jar", ".war", ".ear", ".class"
        ]

    async def inspect_request(self, request: Request) -> Dict[str, Any]:
        """Main inspection method that checks all security aspects"""
        
        # Get request data
        url = str(request.url)
        method = request.method
        headers = dict(request.headers)
        client_ip = request.client.host
        
        # Check request size
        content_length = int(headers.get("content-length", 0))
        if content_length > 10485760:  # 10MB limit
            return {
                "allowed": False,
                "reason": "Request too large",
                "details": {"size": content_length, "limit": 10485760}
            }
        
        # Check for SQL injection
        sql_result = await self._check_sql_injection(url, headers)
        if not sql_result["allowed"]:
            return sql_result
        
        # Check for XSS
        xss_result = await self._check_xss(url, headers)
        if not xss_result["allowed"]:
            return xss_result
        
        # Check for command injection
        cmd_result = await self._check_command_injection(url, headers)
        if not cmd_result["allowed"]:
            return cmd_result
        
        # Check for path traversal
        path_result = await self._check_path_traversal(url)
        if not path_result["allowed"]:
            return path_result
        
        # Check for suspicious headers
        header_result = await self._check_suspicious_headers(headers)
        if not header_result["allowed"]:
            return header_result
        
        # Check for blocked file extensions
        ext_result = await self._check_file_extensions(url)
        if not ext_result["allowed"]:
            return ext_result
        
        # Check for malformed requests
        malformed_result = await self._check_malformed_request(request)
        if not malformed_result["allowed"]:
            return malformed_result
        
        return {"allowed": True, "reason": "allowed", "details": {}}

    async def _check_sql_injection(self, url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Check for SQL injection patterns"""
        text_to_check = url.lower()
        
        for pattern in self.sql_patterns:
            if re.search(pattern, text_to_check, re.IGNORECASE):
                return {
                    "allowed": False,
                    "reason": "SQL Injection",
                    "details": {"pattern": pattern, "matched_text": text_to_check}
                }
        
        return {"allowed": True, "reason": "allowed", "details": {}}

    async def _check_xss(self, url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Check for XSS patterns"""
        text_to_check = url.lower()
        
        for pattern in self.xss_patterns:
            if re.search(pattern, text_to_check, re.IGNORECASE):
                return {
                    "allowed": False,
                    "reason": "XSS Attack",
                    "details": {"pattern": pattern, "matched_text": text_to_check}
                }
        
        return {"allowed": True, "reason": "allowed", "details": {}}

    async def _check_command_injection(self, url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Check for command injection patterns"""
        text_to_check = url.lower()
        
        for pattern in self.command_injection_patterns:
            if re.search(pattern, text_to_check, re.IGNORECASE):
                return {
                    "allowed": False,
                    "reason": "Command Injection",
                    "details": {"pattern": pattern, "matched_text": text_to_check}
                }
        
        return {"allowed": True, "reason": "allowed", "details": {}}

    async def _check_path_traversal(self, url: str) -> Dict[str, Any]:
        """Check for path traversal attempts"""
        text_to_check = url.lower()
        
        for pattern in self.path_traversal_patterns:
            if re.search(pattern, text_to_check, re.IGNORECASE):
                return {
                    "allowed": False,
                    "reason": "Path Traversal",
                    "details": {"pattern": pattern, "matched_text": text_to_check}
                }
        
        return {"allowed": True, "reason": "allowed", "details": {}}

    async def _check_suspicious_headers(self, headers: Dict[str, str]) -> Dict[str, Any]:
        """Check for suspicious headers"""
        for header_name in headers:
            if header_name.lower() in self.suspicious_headers:
                # Check if the header value contains suspicious content
                header_value = headers[header_name].lower()
                if any(pattern in header_value for pattern in ["<script", "javascript:", "onload="]):
                    return {
                        "allowed": False,
                        "reason": "Suspicious Header",
                        "details": {"header": header_name, "value": header_value}
                    }
        
        return {"allowed": True, "reason": "allowed", "details": {}}

    async def _check_file_extensions(self, url: str) -> Dict[str, Any]:
        """Check for blocked file extensions"""
        for ext in self.blocked_extensions:
            if ext in url.lower():
                return {
                    "allowed": False,
                    "reason": "Blocked File Extension",
                    "details": {"extension": ext, "url": url}
                }
        
        return {"allowed": True, "reason": "allowed", "details": {}}

    async def _check_malformed_request(self, request: Request) -> Dict[str, Any]:
        """Check for malformed requests"""
        # Check for null bytes
        if "\x00" in str(request.url):
            return {
                "allowed": False,
                "reason": "Malformed Request",
                "details": {"issue": "null_byte_in_url"}
            }
        
        # Check for extremely long URLs
        if len(str(request.url)) > 2048:
            return {
                "allowed": False,
                "reason": "Malformed Request",
                "details": {"issue": "url_too_long", "length": len(str(request.url))}
            }
        
        # Check for suspicious user agents
        user_agent = request.headers.get("user-agent", "").lower()
        suspicious_agents = ["sqlmap", "nikto", "nmap", "masscan", "zap", "burp"]
        if any(agent in user_agent for agent in suspicious_agents):
            return {
                "allowed": False,
                "reason": "Suspicious User Agent",
                "details": {"user_agent": user_agent}
            }
        
        return {"allowed": True, "reason": "allowed", "details": {}}
