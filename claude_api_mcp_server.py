#!/usr/bin/env python3
"""
Claude API를 통한 Model Context Protocol (MCP) 서버
웹 API로 Claude와 MCP 도구들을 연동
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import anthropic
import psutil
import platform
import os
import subprocess
import signal
import time
from datetime import datetime
from config import config

# 로깅 설정
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="Claude API MCP Server",
    description="Claude API를 통한 MCP 도구 실행 서버",
    version="1.0.0"
)

# Claude 클라이언트 초기화
claude_client = None

class ToolCallRequest(BaseModel):
    """도구 실행 요청 모델"""
    tool_name: str
    arguments: Dict[str, Any]
    user_message: Optional[str] = None

class ToolCallResponse(BaseModel):
    """도구 실행 응답 모델"""
    success: bool
    result: str
    error: Optional[str] = None

class ClaudeMessageRequest(BaseModel):
    """Claude 메시지 요청 모델"""
    message: str
    tools: Optional[List[str]] = None

class ClaudeMessageResponse(BaseModel):
    """Claude 메시지 응답 모델"""
    response: str
    tools_used: List[str] = []

class MCPServer:
    """MCP 서버 클래스"""
    
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
            },
            {
                "name": "calculate",
                "description": "수학 계산을 수행하는 도구",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "계산할 수식 (예: 2+3*4)"
                        }
                    },
                    "required": ["expression"]
                }
            },
            {
                "name": "system_info",
                "description": "시스템 정보를 조회하는 도구",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "info_type": {
                            "type": "string",
                            "description": "조회할 정보 유형 (basic, detailed, all)",
                            "enum": ["basic", "detailed", "all"]
                        }
                    },
                    "required": ["info_type"]
                }
            },
            {
                "name": "process_list",
                "description": "실행 중인 프로세스 목록을 조회하는 도구",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "max_processes": {
                            "type": "integer",
                            "description": "최대 표시할 프로세스 수",
                            "minimum": 1,
                            "maximum": 100
                        },
                        "sort_by": {
                            "type": "string",
                            "description": "정렬 기준",
                            "enum": ["cpu", "memory", "name"]
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "process_control",
                "description": "프로세스를 제어하는 도구",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "description": "수행할 작업",
                            "enum": ["start", "stop", "restart", "kill"]
                        },
                        "process_name": {
                            "type": "string",
                            "description": "제어할 프로세스 이름"
                        },
                        "process_id": {
                            "type": "integer",
                            "description": "제어할 프로세스 ID (PID)"
                        }
                    },
                    "required": ["action"]
                }
            },
            {
                "name": "service_management",
                "description": "시스템 서비스를 관리하는 도구",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "description": "수행할 작업",
                            "enum": ["status", "start", "stop", "restart"]
                        },
                        "service_name": {
                            "type": "string",
                            "description": "관리할 서비스 이름"
                        }
                    },
                    "required": ["action", "service_name"]
                }
            }
        ]
    
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """도구를 실행합니다."""
        logger.info(f"도구 실행: {tool_name}, 인수: {arguments}")
        
        try:
            if tool_name == "hello_world":
                name = arguments.get("name", "세계")
                return f"안녕하세요, {name}님! Claude API MCP 서버에 오신 것을 환영합니다."
            
            elif tool_name == "get_current_time":
                import datetime
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                return f"현재 시간: {current_time}"
            
            elif tool_name == "calculate":
                expression = arguments.get("expression", "")
                # 보안을 위해 제한된 수학 표현식만 허용
                allowed_chars = set("0123456789+-*/.() ")
                if not all(c in allowed_chars for c in expression):
                    return "오류: 허용되지 않는 문자가 포함되어 있습니다."
                
                try:
                    result = eval(expression)
                    return f"계산 결과: {expression} = {result}"
                except Exception as e:
                    return f"계산 오류: {str(e)}"
            
            elif tool_name == "system_info":
                return self._get_system_info(arguments.get("info_type", "basic"))
            
            elif tool_name == "process_list":
                return self._get_process_list(
                    arguments.get("max_processes", 20),
                    arguments.get("sort_by", "cpu")
                )
            
            elif tool_name == "process_control":
                return self._control_process(
                    arguments.get("action"),
                    arguments.get("process_name"),
                    arguments.get("process_id")
                )
            
            elif tool_name == "service_management":
                return self._manage_service(
                    arguments.get("action"),
                    arguments.get("service_name")
                )
            
            else:
                return f"알 수 없는 도구: {tool_name}"
                
        except Exception as e:
            logger.error(f"도구 실행 오류: {e}")
            return f"도구 실행 중 오류가 발생했습니다: {str(e)}"
    
    def _get_system_info(self, info_type: str = "basic") -> str:
        """시스템 정보를 조회합니다."""
        try:
            if info_type == "basic":
                return f"""🖥️ 기본 시스템 정보:
OS: {platform.system()} {platform.release()}
Python: {platform.python_version()}
프로세서: {platform.processor()}
시스템 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
            
            elif info_type == "detailed":
                # CPU 정보
                cpu_count = psutil.cpu_count()
                cpu_percent = psutil.cpu_percent(interval=1)
                
                # 메모리 정보
                memory = psutil.virtual_memory()
                memory_total = self._format_bytes(memory.total)
                memory_available = self._format_bytes(memory.available)
                memory_percent = memory.percent
                
                # 디스크 정보
                disk = psutil.disk_usage('/')
                disk_total = self._format_bytes(disk.total)
                disk_free = self._format_bytes(disk.free)
                disk_percent = (disk.used / disk.total) * 100
                
                return f"""📊 상세 시스템 정보:
CPU: {cpu_count} 코어, 사용률: {cpu_percent}%
메모리: 총 {memory_total}, 사용 가능: {memory_available}, 사용률: {memory_percent}%
디스크: 총 {disk_total}, 여유: {disk_free}, 사용률: {disk_percent:.1f}%"""
            
            else:  # all
                basic_info = self._get_system_info("basic")
                detailed_info = self._get_system_info("detailed")
                return f"{basic_info}\n\n{detailed_info}"
                
        except Exception as e:
            logger.error(f"시스템 정보 조회 오류: {e}")
            return f"시스템 정보 조회 중 오류가 발생했습니다: {str(e)}"
    
    def _get_process_list(self, max_processes: int = 20, sort_by: str = "cpu") -> str:
        """실행 중인 프로세스 목록을 조회합니다."""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    processes.append({
                        'pid': proc.info['pid'] or 0,
                        'name': proc.info['name'] or 'Unknown',
                        'cpu_percent': proc.info['cpu_percent'] or 0.0,
                        'memory_percent': proc.info['memory_percent'] or 0.0,
                        'status': proc.info['status'] or 'Unknown'
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # 정렬 (None 값 처리)
            if sort_by == "cpu":
                processes.sort(key=lambda x: x['cpu_percent'] or 0.0, reverse=True)
            elif sort_by == "memory":
                processes.sort(key=lambda x: x['memory_percent'] or 0.0, reverse=True)
            elif sort_by == "name":
                processes.sort(key=lambda x: (x['name'] or '').lower())
            
            # 상위 프로세스만 선택
            processes = processes[:max_processes]
            
            # 결과 포맷팅
            result = f"PID\t이름\tCPU%\t메모리%\t상태\n"
            result += "-" * 50 + "\n"
            
            for proc in processes:
                cpu_percent = proc['cpu_percent'] or 0.0
                memory_percent = proc['memory_percent'] or 0.0
                result += f"{proc['pid']}\t{proc['name']}\t{cpu_percent:.1f}\t{memory_percent:.1f}\t{proc['status']}\n"
            
            result += f"\n총 {len(processes)}개 프로세스 표시됨"
            return result
            
        except Exception as e:
            logger.error(f"프로세스 목록 조회 오류: {e}")
            return f"프로세스 목록 조회 중 오류가 발생했습니다: {str(e)}"
    
    def _control_process(self, action: str, process_name: str = None, process_id: int = None) -> str:
        """프로세스를 제어합니다."""
        try:
            if not process_name and not process_id:
                return "오류: 프로세스명 또는 PID 중 하나는 반드시 지정해야 합니다."
            
            if action == "start":
                if not process_name:
                    return "오류: 프로세스 시작 시에는 프로세스명이 필요합니다."
                # 프로세스 시작 로직 (실제 구현에서는 더 안전한 방법 사용)
                return f"프로세스 '{process_name}' 시작을 시도합니다. (보안상 실제 실행은 제한됨)"
            
            elif action == "stop":
                if process_id:
                    try:
                        proc = psutil.Process(process_id)
                        proc.terminate()
                        return f"프로세스 PID {process_id} 종료 신호를 보냈습니다."
                    except psutil.NoSuchProcess:
                        return f"오류: PID {process_id}인 프로세스를 찾을 수 없습니다."
                else:
                    return f"프로세스 '{process_name}' 종료를 시도합니다. (PID 지정 권장)"
            
            elif action == "restart":
                if process_id:
                    try:
                        proc = psutil.Process(process_id)
                        proc.terminate()
                        time.sleep(1)
                        # 재시작 로직 (실제 구현에서는 더 복잡)
                        return f"프로세스 PID {process_id} 재시작을 시도합니다."
                    except psutil.NoSuchProcess:
                        return f"오류: PID {process_id}인 프로세스를 찾을 수 없습니다."
                else:
                    return f"프로세스 '{process_name}' 재시작을 시도합니다. (PID 지정 권장)"
            
            elif action == "kill":
                if process_id:
                    try:
                        proc = psutil.Process(process_id)
                        proc.kill()
                        return f"프로세스 PID {process_id}를 강제 종료했습니다."
                    except psutil.NoSuchProcess:
                        return f"오류: PID {process_id}인 프로세스를 찾을 수 없습니다."
                else:
                    return f"프로세스 '{process_name}' 강제 종료를 시도합니다. (PID 지정 권장)"
            
            else:
                return f"알 수 없는 작업: {action}"
                
        except Exception as e:
            logger.error(f"프로세스 제어 오류: {e}")
            return f"프로세스 제어 중 오류가 발생했습니다: {str(e)}"
    
    def _manage_service(self, action: str, service_name: str) -> str:
        """시스템 서비스를 관리합니다."""
        try:
            if not service_name:
                return "오류: 서비스명을 지정해야 합니다."
            
            # macOS/Linux용 systemctl 명령어
            if platform.system() in ["Darwin", "Linux"]:
                if action == "status":
                    result = subprocess.run(['systemctl', 'status', service_name], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        return f"서비스 '{service_name}' 상태:\n{result.stdout}"
                    else:
                        return f"서비스 '{service_name}' 상태 조회 실패: {result.stderr}"
                
                elif action == "start":
                    result = subprocess.run(['systemctl', 'start', service_name], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        return f"서비스 '{service_name}' 시작 성공"
                    else:
                        return f"서비스 '{service_name}' 시작 실패: {result.stderr}"
                
                elif action == "stop":
                    result = subprocess.run(['systemctl', 'stop', service_name], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        return f"서비스 '{service_name}' 중지 성공"
                    else:
                        return f"서비스 '{service_name}' 중지 실패: {result.stderr}"
                
                elif action == "restart":
                    result = subprocess.run(['systemctl', 'restart', service_name], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        return f"서비스 '{service_name}' 재시작 성공"
                    else:
                        return f"서비스 '{service_name}' 재시작 실패: {result.stderr}"
                
                else:
                    return f"알 수 없는 작업: {action}"
            
            # Windows용 sc 명령어
            elif platform.system() == "Windows":
                if action == "status":
                    result = subprocess.run(['sc', 'query', service_name], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        return f"서비스 '{service_name}' 상태:\n{result.stdout}"
                    else:
                        return f"서비스 '{service_name}' 상태 조회 실패: {result.stderr}"
                
                elif action == "start":
                    result = subprocess.run(['sc', 'start', service_name], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        return f"서비스 '{service_name}' 시작 성공"
                    else:
                        return f"서비스 '{service_name}' 시작 실패: {result.stderr}"
                
                elif action == "stop":
                    result = subprocess.run(['sc', 'stop', service_name], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        return f"서비스 '{service_name}' 중지 성공"
                    else:
                        return f"서비스 '{service_name}' 중지 실패: {result.stderr}"
                
                elif action == "restart":
                    result = subprocess.run(['sc', 'stop', service_name], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        subprocess.run(['sc', 'start', service_name], 
                                     capture_output=True, text=True, timeout=10)
                        return f"서비스 '{service_name}' 재시작 성공"
                    else:
                        return f"서비스 '{service_name}' 재시작 실패: {result.stderr}"
                
                else:
                    return f"알 수 없는 작업: {action}"
            
            else:
                return f"지원되지 않는 운영체제: {platform.system()}"
                
        except Exception as e:
            logger.error(f"서비스 관리 오류: {e}")
            return f"서비스 관리 중 오류가 발생했습니다: {str(e)}"
    
    def _format_bytes(self, bytes_value: int) -> str:
        """바이트 값을 읽기 쉬운 형태로 변환합니다."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"

# MCP 서버 인스턴스
mcp_server = MCPServer()

@app.on_event("startup")
async def startup_event():
    """서버 시작 시 실행"""
    global claude_client
    
    # 설정 검증
    if not config.validate():
        logger.error("설정이 유효하지 않습니다.")
        return
    
    # Claude 클라이언트 초기화
    try:
        claude_client = anthropic.Anthropic(api_key=config.load_api_key())
        logger.info("Claude API 클라이언트가 초기화되었습니다.")
    except Exception as e:
        logger.error(f"Claude API 클라이언트 초기화 실패: {e}")

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "Claude API MCP Server",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/tools")
async def list_tools():
    """사용 가능한 도구 목록 반환"""
    return {
        "tools": mcp_server.tools,
        "count": len(mcp_server.tools)
    }

@app.post("/tools/call", response_model=ToolCallResponse)
async def call_tool(request: ToolCallRequest):
    """도구 실행"""
    try:
        result = mcp_server.execute_tool(request.tool_name, request.arguments)
        return ToolCallResponse(
            success=True,
            result=result
        )
    except Exception as e:
        logger.error(f"도구 실행 오류: {e}")
        return ToolCallResponse(
            success=False,
            result="",
            error=str(e)
        )

@app.post("/claude/message", response_model=ClaudeMessageResponse)
async def send_message_to_claude(request: ClaudeMessageRequest):
    """Claude API로 메시지 전송"""
    if not claude_client:
        raise HTTPException(status_code=500, detail="Claude API 클라이언트가 초기화되지 않았습니다.")
    
    try:
        # Claude에 메시지 전송
        response = claude_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": request.message
                }
            ]
        )
        
        return ClaudeMessageResponse(
            response=response.content[0].text,
            tools_used=[]
        )
        
    except Exception as e:
        logger.error(f"Claude API 호출 오류: {e}")
        raise HTTPException(status_code=500, detail=f"Claude API 호출 실패: {str(e)}")

@app.post("/claude/message-with-tools")
async def send_message_with_tools(request: ClaudeMessageRequest):
    """도구를 사용하여 Claude와 대화"""
    if not claude_client:
        raise HTTPException(status_code=500, detail="Claude API 클라이언트가 초기화되지 않았습니다.")
    
    try:
        # 사용자가 요청한 도구들 확인
        available_tools = []
        if request.tools:
            available_tools = [tool for tool in mcp_server.tools if tool["name"] in request.tools]
        else:
            available_tools = mcp_server.tools
        
        # Claude에게 도구 정보와 함께 메시지 전송
        tools_description = "\n".join([
            f"- {tool['name']}: {tool['description']}" 
            for tool in available_tools
        ])
        
        enhanced_message = f"""
{request.message}

사용 가능한 도구들:
{tools_description}

필요한 도구가 있다면 언급해주세요.
"""
        
        response = claude_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": enhanced_message
                }
            ]
        )
        
        return {
            "response": response.content[0].text,
            "available_tools": [tool["name"] for tool in available_tools],
            "message": "도구 사용을 원하시면 /tools/call 엔드포인트를 사용하세요."
        }
        
    except Exception as e:
        logger.error(f"Claude API 도구 연동 오류: {e}")
        raise HTTPException(status_code=500, detail=f"Claude API 도구 연동 실패: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Claude API MCP 서버를 시작합니다...")
    print("📝 사용법:")
    print("   1. ANTHROPIC_API_KEY 환경 변수 설정")
    print("   2. 서버 실행: python claude_api_mcp_server.py")
    print("   3. 웹 브라우저에서 http://localhost:8000 접속")
    print("   4. API 문서: http://localhost:8000/docs")
    
    uvicorn.run(
        "claude_api_mcp_server:app",
        host=config.MCP_SERVER_HOST,
        port=config.MCP_SERVER_PORT,
        reload=True
    )
