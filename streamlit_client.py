#!/usr/bin/env python3
"""
Streamlit을 사용한 Claude API MCP 클라이언트
"""

import streamlit as st
import requests
import json
from typing import Dict, Any
import time

# 페이지 설정
st.set_page_config(
    page_title="Claude API MCP Client",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

class ClaudeAPIMCPClient:
    """Claude API MCP 서버 클라이언트"""
    
    def __init__(self, base_url: str = "http://localhost:8005"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def list_tools(self) -> Dict[str, Any]:
        """사용 가능한 도구 목록 조회"""
        try:
            response = self.session.get(f"{self.base_url}/tools")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"도구 목록 조회 실패: {e}")
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
            st.error(f"도구 실행 실패: {e}")
            return {"success": False, "error": str(e)}
    
    def send_message_to_claude(self, message: str) -> Dict[str, Any]:
        """Claude API로 메시지 전송"""
        try:
            payload = {"message": message}
            response = self.session.post(f"{self.base_url}/claude/message", json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Claude 메시지 전송 실패: {e}")
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
            st.error(f"Claude 도구 연동 메시지 전송 실패: {e}")
            return {"error": str(e)}

def main():
    """메인 Streamlit 앱"""
    
    # 헤더
    st.title("🤖 Claude API MCP Client")
    st.markdown("Claude API와 MCP 도구들을 Streamlit으로 테스트해보세요!")
    
    # 사이드바 설정
    with st.sidebar:
        st.header("⚙️ 설정")
        
        # 서버 URL 설정
        server_url = st.text_input(
            "서버 URL",
            value="http://localhost:8005",
            help="MCP 서버의 기본 URL을 입력하세요"
        )
        
        # 새로고침 버튼
        if st.button("🔄 새로고침", use_container_width=True):
            st.rerun()
        
        st.divider()
        
        # 서버 상태 확인
        st.subheader("📊 서버 상태")
        try:
            response = requests.get(f"{server_url}/", timeout=5)
            if response.status_code == 200:
                st.success("🟢 서버 연결됨")
                server_info = response.json()
                st.json(server_info)
            else:
                st.error("🔴 서버 응답 오류")
        except Exception as e:
            st.error(f"🔴 서버 연결 실패: {e}")
    
    # 클라이언트 생성
    client = ClaudeAPIMCPClient(server_url)
    
    # 탭 생성
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏠 대시보드", 
        "🛠️ 도구 테스트", 
        "💬 Claude 대화", 
        "🔧 도구 연동 대화"
    ])
    
    # 탭 1: 대시보드
    with tab1:
        st.header("📊 MCP 서버 대시보드")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 사용 가능한 도구")
            tools = client.list_tools()
            
            if tools and "tools" in tools:
                for i, tool in enumerate(tools["tools"]):
                    with st.expander(f"🔧 {tool['name']}", expanded=True):
                        st.write(f"**설명**: {tool['description']}")
                        st.json(tool['inputSchema'])
                        
                        # 도구 실행 버튼
                        if st.button(f"실행하기", key=f"run_{i}"):
                            st.session_state[f"run_tool_{i}"] = True
                            st.rerun()
            else:
                st.warning("도구 목록을 불러올 수 없습니다.")
        
        with col2:
            st.subheader("📈 서버 정보")
            try:
                response = requests.get(f"{server_url}/")
                if response.status_code == 200:
                    server_info = response.json()
                    st.json(server_info)
                else:
                    st.error("서버 정보를 불러올 수 없습니다.")
            except Exception as e:
                st.error(f"서버 정보 조회 실패: {e}")
    
    # 탭 2: 도구 테스트
    with tab2:
        st.header("🛠️ MCP 도구 테스트")
        
        # 도구 선택
        tools = client.list_tools()
        if tools and "tools" in tools:
            tool_names = [tool["name"] for tool in tools["tools"]]
            selected_tool = st.selectbox("도구 선택", tool_names)
            
            # 선택된 도구 정보 표시
            selected_tool_info = next((tool for tool in tools["tools"] if tool["name"] == selected_tool), None)
            
            if selected_tool_info:
                st.write(f"**도구**: {selected_tool_info['name']}")
                st.write(f"**설명**: {selected_tool_info['description']}")
                
                # 도구별 입력 폼
                if selected_tool == "hello_world":
                    name = st.text_input("이름", value="홍길동")
                    if st.button("인사말 생성", type="primary"):
                        with st.spinner("도구 실행 중..."):
                            result = client.call_tool("hello_world", {"name": name})
                            if result.get("success"):
                                st.success(f"✅ 결과: {result['result']}")
                            else:
                                st.error(f"❌ 오류: {result.get('error', '알 수 없는 오류')}")
                
                elif selected_tool == "get_current_time":
                    if st.button("현재 시간 조회", type="primary"):
                        with st.spinner("도구 실행 중..."):
                            result = client.call_tool("get_current_time", {})
                            if result.get("success"):
                                st.success(f"✅ 결과: {result['result']}")
                            else:
                                st.error(f"❌ 오류: {result.get('error', '알 수 없는 오류')}")
                
                elif selected_tool == "calculate":
                    expression = st.text_input("수식", value="2+3*4", help="계산할 수식을 입력하세요 (예: 2+3*4)")
                    if st.button("계산하기", type="primary"):
                        with st.spinner("도구 실행 중..."):
                            result = client.call_tool("calculate", {"expression": expression})
                            if result.get("success"):
                                st.success(f"✅ 결과: {result['result']}")
                            else:
                                st.error(f"❌ 오류: {result.get('error', '알 수 없는 오류')}")
        else:
            st.warning("도구 목록을 불러올 수 없습니다.")
    
    # 탭 3: Claude 대화
    with tab3:
        st.header("💬 Claude와 대화")
        
        # 대화 히스토리 초기화
        if "claude_messages" not in st.session_state:
            st.session_state.claude_messages = []
        
        # 메시지 입력
        user_message = st.text_area(
            "메시지를 입력하세요",
            height=100,
            placeholder="Claude에게 보낼 메시지를 입력하세요..."
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("전송", type="primary"):
                if user_message.strip():
                    # 사용자 메시지 추가
                    st.session_state.claude_messages.append({
                        "role": "user",
                        "content": user_message,
                        "timestamp": time.strftime("%H:%M:%S")
                    })
                    
                    # Claude 응답 받기
                    with st.spinner("Claude가 응답하고 있습니다..."):
                        response = client.send_message_to_claude(user_message)
                        
                        if "response" in response:
                            st.session_state.claude_messages.append({
                                "role": "assistant",
                                "content": response["response"],
                                "timestamp": time.strftime("%H:%M:%S")
                            })
                        else:
                            st.error(f"Claude 응답 오류: {response.get('error', '알 수 없는 오류')}")
                    
                    st.rerun()
        
        with col2:
            if st.button("대화 초기화"):
                st.session_state.claude_messages = []
                st.rerun()
        
        # 대화 히스토리 표시
        st.subheader("💭 대화 히스토리")
        for message in st.session_state.claude_messages:
            if message["role"] == "user":
                st.chat_message("user").write(f"**{message['timestamp']}** - {message['content']}")
            else:
                st.chat_message("assistant").write(f"**{message['timestamp']}** - {message['content']}")
    
    # 탭 4: 도구 연동 대화
    with tab4:
        st.header("🔧 Claude와 도구 연동 대화")
        
        # 도구 선택
        tools = client.list_tools()
        if tools and "tools" in tools:
            tool_names = [tool["name"] for tool in tools["tools"]]
            selected_tools = st.multiselect(
                "사용할 도구 선택",
                tool_names,
                default=tool_names,
                help="Claude가 사용할 수 있는 도구들을 선택하세요"
            )
            
            # 대화 히스토리 초기화
            if "tool_messages" not in st.session_state:
                st.session_state.tool_messages = []
            
            # 메시지 입력
            tool_user_message = st.text_area(
                "도구를 사용한 메시지를 입력하세요",
                height=100,
                placeholder="예: 현재 시간을 알려주고, '김철수'에게 인사말을 해주세요."
            )
            
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("도구와 함께 전송", type="primary"):
                    if tool_user_message.strip():
                        # 사용자 메시지 추가
                        st.session_state.tool_messages.append({
                            "role": "user",
                            "content": tool_user_message,
                            "timestamp": time.strftime("%H:%M:%S")
                        })
                        
                        # Claude 응답 받기 (도구 정보 포함)
                        with st.spinner("Claude가 도구를 고려하여 응답하고 있습니다..."):
                            response = client.send_message_with_tools(tool_user_message, selected_tools)
                            
                            if "response" in response:
                                st.session_state.tool_messages.append({
                                    "role": "assistant",
                                    "content": response["response"],
                                    "timestamp": time.strftime("%H:%M:%S"),
                                    "available_tools": response.get("available_tools", [])
                                })
                            else:
                                st.error(f"Claude 응답 오류: {response.get('error', '알 수 없는 오류')}")
                        
                        st.rerun()
            
            with col2:
                if st.button("대화 초기화", key="tool_reset"):
                    st.session_state.tool_messages = []
                    st.rerun()
            
            # 도구 연동 대화 히스토리 표시
            st.subheader("🔧 도구 연동 대화 히스토리")
            for message in st.session_state.tool_messages:
                if message["role"] == "user":
                    st.chat_message("user").write(f"**{message['timestamp']}** - {message['content']}")
                else:
                    st.chat_message("assistant").write(f"**{message['timestamp']}** - {message['content']}")
                    if "available_tools" in message and message["available_tools"]:
                        st.info(f"📋 사용 가능한 도구: {', '.join(message['available_tools'])}")
        else:
            st.warning("도구 목록을 불러올 수 없습니다.")

if __name__ == "__main__":
    main()
