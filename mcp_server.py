#!/usr/bin/env python3
"""
Model Context Protocol (MCP) Server
클로드 데스크탑과 연동하는 MCP 서버
"""

import asyncio
import json
import logging
import sys
import os
import platform
from typing import Any, Dict, List, Optional

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPServer:
    def __init__(self):
        self.tools = [
            {
                "name": "hello_world",
                "description": "간단한 인사말을 반환하는 도구",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "인사할 사람의 이름"
                        }
                    },
                    "required": ["name"]
                }
            },
            {
                "name": "get_current_time",
                "description": "현재 시간을 반환하는 도구",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]
    
    def handle_list_tools(self, request_id: Any) -> Dict[str, Any]:
        """사용 가능한 도구 목록을 반환합니다."""
        logger.info(f"도구 목록 요청: {request_id}")
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": self.tools
            }
        }
    
    def handle_call_tool(self, request_id: Any, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """도구를 실행합니다."""
        logger.info(f"도구 실행 요청: {tool_name}, 인수: {arguments}")
        
        if tool_name == "hello_world":
            name = arguments.get("name", "세계")
            result = f"안녕하세요, {name}님! MCP 서버에 오신 것을 환영합니다."
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [{"type": "text", "text": result}]
                }
            }
        
        elif tool_name == "get_current_time":
            import datetime
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            result = f"현재 시간: {current_time}"
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [{"type": "text", "text": result}]
                }
            }
        
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"알 수 없는 도구: {tool_name}"
                }
            }
    
    def handle_initialize(self, request_id: Any) -> Dict[str, Any]:
        """초기화 요청을 처리합니다."""
        logger.info(f"초기화 요청: {request_id}")
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "claude-desktop-mcp-server",
                    "version": "1.0.0"
                }
            }
        }

async def handle_stdio():
    """표준 입출력으로 MCP 프로토콜 처리"""
    server = MCPServer()
    logger.info("MCP 서버가 시작되었습니다.")
    
    while True:
        try:
            # 표준 입력에서 JSON-RPC 요청 읽기
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            
            if not line:
                break
            
            line = line.strip()
            if not line:
                continue
            
            logger.info(f"수신된 요청: {line}")
            
            try:
                request = json.loads(line)
                method = request.get("method")
                params = request.get("params", {})
                request_id = request.get("id")
                
                # 요청 처리
                if method == "initialize":
                    response = server.handle_initialize(request_id)
                elif method == "tools/list":
                    response = server.handle_list_tools(request_id)
                elif method == "tools/call":
                    tool_name = params.get("name")
                    arguments = params.get("arguments", {})
                    response = server.handle_call_tool(request_id, tool_name, arguments)
                else:
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32601,
                            "message": f"지원하지 않는 메서드: {method}"
                        }
                    }
                
                # 응답 전송
                response_json = json.dumps(response, ensure_ascii=False)
                print(response_json)
                sys.stdout.flush()
                logger.info(f"응답 전송: {response_json}")
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON 파싱 오류: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": f"JSON 파싱 오류: {e}"
                    }
                }
                print(json.dumps(error_response))
                sys.stdout.flush()
                
        except KeyboardInterrupt:
            logger.info("서버 종료...")
            break
        except Exception as e:
            logger.error(f"처리 중 오류: {e}")
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": f"내부 오류: {e}"
                }
            }
            print(json.dumps(error_response))
            sys.stdout.flush()

if __name__ == "__main__":
    try:
        asyncio.run(handle_stdio())
    except Exception as e:
        logger.error(f"서버 실행 중 오류: {e}")
        sys.exit(1)
