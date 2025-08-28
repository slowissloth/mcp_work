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
            
            else:
                return f"알 수 없는 도구: {tool_name}"
                
        except Exception as e:
            logger.error(f"도구 실행 오류: {e}")
            return f"도구 실행 중 오류가 발생했습니다: {str(e)}"

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
