#!/usr/bin/env python3
"""
Claude API MCP 서버 클라이언트 예제
"""

import requests
import json
from typing import Dict, Any

class ClaudeAPIMCPClient:
    """Claude API MCP 서버 클라이언트"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def list_tools(self) -> Dict[str, Any]:
        """사용 가능한 도구 목록 조회"""
        try:
            response = self.session.get(f"{self.base_url}/tools")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"도구 목록 조회 실패: {e}")
            return {}
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """도구 실행"""
        try:
            payload = {
                "tool_name": tool_name,
                "arguments": arguments
            }
            response = self.session.post(f"{self.base_url}/tools/call", json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"도구 실행 실패: {e}")
            return {"success": False, "error": str(e)}
    
    def send_message_to_claude(self, message: str) -> Dict[str, Any]:
        """Claude API로 메시지 전송"""
        try:
            payload = {"message": message}
            response = self.session.post(f"{self.base_url}/claude/message", json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Claude 메시지 전송 실패: {e}")
            return {"error": str(e)}
    
    def send_message_with_tools(self, message: str, tools: list = None) -> Dict[str, Any]:
        """도구를 사용하여 Claude와 대화"""
        try:
            payload = {"message": message}
            if tools:
                payload["tools"] = tools
            
            response = self.session.post(f"{self.base_url}/claude/message-with-tools", json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Claude 도구 연동 메시지 전송 실패: {e}")
            return {"error": str(e)}

def main():
    """메인 함수 - 사용 예제"""
    print("🚀 Claude API MCP 클라이언트 예제")
    print("=" * 50)
    
    # 클라이언트 생성
    client = ClaudeAPIMCPClient()
    
    # 1. 도구 목록 조회
    print("\n1️⃣ 사용 가능한 도구 목록:")
    tools = client.list_tools()
    if tools:
        for tool in tools.get("tools", []):
            print(f"   - {tool['name']}: {tool['description']}")
    
    # 2. 도구 직접 실행
    print("\n2️⃣ 도구 직접 실행:")
    
    # hello_world 도구
    result = client.call_tool("hello_world", {"name": "홍길동"})
    if result.get("success"):
        print(f"   hello_world: {result['result']}")
    
    # get_current_time 도구
    result = client.call_tool("get_current_time", {})
    if result.get("success"):
        print(f"   get_current_time: {result['result']}")
    
    # calculate 도구
    result = client.call_tool("calculate", {"expression": "2+3*4"})
    if result.get("success"):
        print(f"   calculate: {result['result']}")
    
    # 3. Claude와 대화 (도구 없이)
    print("\n3️⃣ Claude와 대화 (도구 없이):")
    response = client.send_message_to_claude("안녕하세요! 간단한 인사말을 해주세요.")
    if "response" in response:
        print(f"   Claude: {response['response']}")
    
    # 4. Claude와 대화 (도구 연동)
    print("\n4️⃣ Claude와 대화 (도구 연동):")
    response = client.send_message_with_tools(
        "안녕하세요! 현재 시간을 알려주고, '김철수'에게 인사말을 해주세요."
    )
    if "response" in response:
        print(f"   Claude: {response['response']}")
        print(f"   사용 가능한 도구: {response.get('available_tools', [])}")
    
    print("\n✅ 예제 실행 완료!")

if __name__ == "__main__":
    main()
