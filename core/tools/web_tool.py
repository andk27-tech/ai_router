#!/usr/bin/env python3
"""
Web Tool Module
웹 툴 - HTTP 요청, API 호출, 웹 스크래핑, 응답 파싱, 오류 처리
"""

import requests
import json
import re
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from urllib.parse import urlparse, urljoin
import time


class HTTPMethod(Enum):
    """HTTP 메서드"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"


class ResponseFormat(Enum):
    """응답 형식"""
    JSON = "json"
    TEXT = "text"
    HTML = "html"
    BINARY = "binary"


@dataclass
class HTTPRequest:
    """HTTP 요청 데이터 클래스"""
    url: str
    method: HTTPMethod = HTTPMethod.GET
    headers: Dict[str, str] = field(default_factory=dict)
    params: Dict[str, Any] = field(default_factory=dict)
    data: Optional[Union[Dict[str, Any], str, bytes]] = None
    json_data: Optional[Dict[str, Any]] = None
    timeout: int = 30
    allow_redirects: bool = True
    verify_ssl: bool = True


@dataclass
class HTTPResponse:
    """HTTP 응답 데이터 클래스"""
    status_code: int
    status_text: str
    headers: Dict[str, str]
    content: Union[str, bytes, Dict[str, Any]]
    encoding: str
    elapsed_time: float
    url: str
    success: bool
    error: Optional[str] = None


class WebTool:
    """웹 툴 클래스"""
    
    def __init__(self):
        self.default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.request_cache = {}
        self.cache_ttl = 300
    
    def call_api(self, url: str, method: str = "GET", 
                 params: Optional[Dict[str, Any]] = None,
                 data: Optional[Union[Dict[str, Any], str]] = None,
                 json_data: Optional[Dict[str, Any]] = None,
                 headers: Optional[Dict[str, str]] = None,
                 timeout: int = 30) -> Dict[str, Any]:
        """API 호출"""
        try:
            method_enum = HTTPMethod(method.upper())
            
            headers = {**self.default_headers, **(headers or {})}
            
            start_time = time.time()
            
            if method_enum == HTTPMethod.GET:
                response = self.session.get(url, params=params, headers=headers, timeout=timeout)
            elif method_enum == HTTPMethod.POST:
                response = self.session.post(url, params=params, data=data, json=json_data, headers=headers, timeout=timeout)
            elif method_enum == HTTPMethod.PUT:
                response = self.session.put(url, params=params, data=data, json=json_data, headers=headers, timeout=timeout)
            elif method_enum == HTTPMethod.DELETE:
                response = self.session.delete(url, params=params, data=data, json=json_data, headers=headers, timeout=timeout)
            elif method_enum == HTTPMethod.PATCH:
                response = self.session.patch(url, params=params, data=data, json=json_data, headers=headers, timeout=timeout)
            elif method_enum == HTTPMethod.HEAD:
                response = self.session.head(url, params=params, headers=headers, timeout=timeout)
            else:
                return {'success': False, 'error': f'Invalid HTTP method: {method}'}
            
            elapsed_time = time.time() - start_time
            
            # 응답 처리
            content_type = response.headers.get('Content-Type', '')
            if 'application/json' in content_type:
                try:
                    content = response.json()
                except:
                    content = response.text
            else:
                content = response.text
            
            return {
                'success': response.status_code < 400,
                'status_code': response.status_code,
                'status_text': response.reason,
                'data': content,
                'headers': dict(response.headers),
                'elapsed_time': elapsed_time,
                'url': response.url,
                'error': None
            }
            
        except requests.exceptions.Timeout:
            return {'success': False, 'error': 'Request timeout', 'status_code': 0}
        except requests.exceptions.ConnectionError as e:
            return {'success': False, 'error': f'Connection error: {str(e)}', 'status_code': 0}
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': f'Request error: {str(e)}', 'status_code': 0}
        except Exception as e:
            return {'success': False, 'error': str(e), 'status_code': 0}
    
    def validate_url(self, url: str) -> Dict[str, Any]:
        """URL 유효성 검사"""
        try:
            parsed = urlparse(url)
            
            if not parsed.scheme or not parsed.netloc:
                return {'valid': False, 'error': 'Invalid URL format'}
            
            if parsed.scheme not in ['http', 'https']:
                return {'valid': False, 'error': 'Only HTTP and HTTPS schemes are supported'}
            
            return {
                'valid': True,
                'scheme': parsed.scheme,
                'netloc': parsed.netloc,
                'path': parsed.path,
                'query': parsed.query
            }
        except Exception as e:
            return {'valid': False, 'error': str(e)}
    
    def close(self) -> None:
        """세션 종료"""
        self.session.close()


def quick_get(url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """빠른 GET 요청"""
    tool = WebTool()
    result = tool.call_api(url, method='GET', params=params)
    tool.close()
    return result
