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
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🏠 대시보드", 
        "🛠️ 도구 테스트", 
        "🖥️ 시스템 정보",
        "⚙️ 프로세스 관리",
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
                
                elif selected_tool == "system_info":
                    info_type = st.selectbox("정보 유형", ["basic", "detailed", "all"])
                    if st.button("시스템 정보 조회", type="primary"):
                        with st.spinner("도구 실행 중..."):
                            result = client.call_tool("system_info", {"info_type": info_type})
                            if result.get("success"):
                                st.success(f"✅ 결과: {result['result']}")
                            else:
                                st.error(f"❌ 오류: {result.get('error', '알 수 없는 오류')}")
                
                elif selected_tool == "process_list":
                    col1, col2 = st.columns(2)
                    with col1:
                        max_processes = st.slider("최대 프로세스 수", 1, 100, 20)
                    with col2:
                        sort_by = st.selectbox("정렬 기준", ["cpu", "memory", "name"])
                    
                    if st.button("프로세스 목록 조회", type="primary"):
                        with st.spinner("도구 실행 중..."):
                            result = client.call_tool("process_list", {
                                "max_processes": max_processes,
                                "sort_by": sort_by
                            })
                            if result.get("success"):
                                st.success(f"✅ 결과: {result['result']}")
                            else:
                                st.error(f"❌ 오류: {result.get('error', '알 수 없는 오류')}")
                
                elif selected_tool == "process_control":
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        action = st.selectbox("작업", ["start", "stop", "restart", "kill"])
                    with col2:
                        process_name = st.text_input("프로세스명")
                    with col3:
                        process_id = st.number_input("PID", min_value=1)
                    
                    if st.button("프로세스 제어", type="primary"):
                        args = {"action": action}
                        if process_name:
                            args["process_name"] = process_name
                        if process_id:
                            args["process_id"] = process_id
                        
                        with st.spinner("도구 실행 중..."):
                            result = client.call_tool("process_control", args)
                            if result.get("success"):
                                st.success(f"✅ 결과: {result['result']}")
                            else:
                                st.error(f"❌ 오류: {result.get('error', '알 수 없는 오류')}")
                
                elif selected_tool == "service_management":
                    col1, col2 = st.columns(2)
                    with col1:
                        action = st.selectbox("작업", ["status", "start", "stop", "restart"])
                    with col2:
                        service_name = st.text_input("서비스명", value="ssh")
                    
                    if st.button("서비스 관리", type="primary"):
                        with st.spinner("도구 실행 중..."):
                            result = client.call_tool("service_management", {
                                "action": action,
                                "service_name": service_name
                            })
                            if result.get("success"):
                                st.success(f"✅ 결과: {result['result']}")
                            else:
                                st.error(f"❌ 오류: {result.get('error', '알 수 없는 오류')}")
        else:
            st.warning("도구 목록을 불러올 수 없습니다.")
    
    # 탭 3: 시스템 정보
    with tab3:
        st.header("🖥️ 시스템 정보 조회")
        st.markdown("시스템의 상세 정보를 조회합니다.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("⚙️ 조회 설정")
            
            # 정보 유형 선택
            info_type = st.selectbox(
                "정보 유형",
                ["basic", "detailed", "all"],
                help="조회할 시스템 정보의 상세 정도를 선택하세요"
            )
            
            # 시스템 정보 조회 버튼
            if st.button("🖥️ 시스템 정보 조회", type="primary", use_container_width=True):
                with st.spinner("시스템 정보를 조회하고 있습니다..."):
                    result = client.call_tool("system_info", {"info_type": info_type})
                    
                    if result.get("success"):
                        st.success("✅ 시스템 정보 조회 완료!")
                        st.session_state.system_info_result = result['result']
                    else:
                        st.error(f"❌ 시스템 정보 조회 실패: {result.get('error', '알 수 없는 오류')}")
        
        with col2:
            st.subheader("📊 시스템 정보 결과")
            
            if "system_info_result" in st.session_state:
                # 결과를 예쁘게 표시
                result_text = st.session_state.system_info_result
                
                # 결과를 섹션별로 분리
                sections = result_text.split('\n\n')
                
                for section in sections:
                    if section.strip():
                        if section.startswith("🖥️"):
                            st.subheader("🖥️ 기본 시스템 정보")
                            st.write(section.replace("🖥️ 기본 시스템 정보:", "").strip())
                        elif section.startswith("📊"):
                            st.subheader("📊 상세 시스템 정보")
                            st.write(section.replace("📊 상세 시스템 정보:", "").strip())
                        else:
                            st.write(section)
                
                # 원본 결과 보기
                with st.expander("📋 원본 결과 보기"):
                    st.text(result_text)
            else:
                st.info("👆 시스템 정보 조회를 실행하면 결과가 여기에 표시됩니다.")
    
    # 탭 4: 프로세스 관리
    with tab4:
        st.header("⚙️ 프로세스 관리")
        st.markdown("실행 중인 프로세스를 조회하고 제어합니다.")
        
        # 프로세스 목록 조회
        st.subheader("📋 프로세스 목록 조회")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            max_processes = st.slider(
                "최대 표시 프로세스 수",
                min_value=1,
                max_value=100,
                value=20,
                help="표시할 최대 프로세스 수를 설정하세요"
            )
        
        with col2:
            sort_by = st.selectbox(
                "정렬 기준",
                ["cpu", "memory", "name"],
                help="프로세스 목록을 정렬할 기준을 선택하세요"
            )
        
        with col3:
            if st.button("📋 프로세스 목록 조회", type="primary", use_container_width=True):
                with st.spinner("프로세스 목록을 조회하고 있습니다..."):
                    result = client.call_tool("process_list", {
                        "max_processes": max_processes,
                        "sort_by": sort_by
                    })
                    
                    if result.get("success"):
                        st.success("✅ 프로세스 목록 조회 완료!")
                        st.session_state.process_list_result = result['result']
                    else:
                        st.error(f"❌ 프로세스 목록 조회 실패: {result.get('error', '알 수 없는 오류')}")
        
        # 프로세스 목록 결과 표시
        if "process_list_result" in st.session_state:
            st.subheader("📊 프로세스 목록")
            result_text = st.session_state.process_list_result
            
            # 결과를 줄별로 분리하여 표 형태로 표시
            lines = result_text.split('\n')
            if len(lines) > 3:  # 헤더와 구분선 이후
                # 헤더 표시
                st.write(f"**{lines[0]}**")
                st.write(f"*{lines[1]}*")
                
                # 프로세스 목록을 표로 표시
                process_data = []
                for line in lines[3:]:
                    if line.strip() and not line.startswith("총"):
                        parts = line.split('\t')
                        if len(parts) >= 5:
                            process_data.append({
                                "PID": parts[0].strip(),
                                "이름": parts[1].strip(),
                                "CPU%": parts[2].strip(),
                                "메모리%": parts[3].strip(),
                                "상태": parts[4].strip()
                            })
                
                if process_data:
                    st.dataframe(process_data, use_container_width=True)
                
                # 요약 정보
                for line in lines:
                    if line.startswith("총"):
                        st.info(line)
            
            # 원본 결과 보기
            with st.expander("📋 원본 결과 보기"):
                st.text(result_text)
        
        # 프로세스 제어
        st.subheader("🎮 프로세스 제어")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            action = st.selectbox(
                "수행할 작업",
                ["start", "stop", "restart", "kill"],
                help="프로세스에 수행할 작업을 선택하세요"
            )
        
        with col2:
            process_name = st.text_input(
                "프로세스명",
                help="제어할 프로세스의 이름을 입력하세요"
            )
        
        with col3:
            process_id = st.number_input(
                "프로세스 ID (PID)",
                min_value=1,
                help="제어할 프로세스의 PID를 입력하세요 (선택사항)"
            )
        
        if st.button("🎮 프로세스 제어 실행", type="primary", use_container_width=True):
            if not process_name and not process_id:
                st.error("프로세스명 또는 PID 중 하나는 반드시 입력해야 합니다.")
            else:
                arguments = {"action": action}
                if process_name:
                    arguments["process_name"] = process_name
                if process_id:
                    arguments["process_id"] = int(process_id)
                
                with st.spinner("프로세스 제어를 실행하고 있습니다..."):
                    result = client.call_tool("process_control", arguments)
                    
                    if result.get("success"):
                        st.success(f"✅ {result['result']}")
                    else:
                        st.error(f"❌ 프로세스 제어 실패: {result.get('error', '알 수 없는 오류')}")
        
        # 서비스 관리
        st.subheader("🔧 서비스 관리")
        
        col1, col2 = st.columns(2)
        
        with col1:
            service_action = st.selectbox(
                "서비스 작업",
                ["status", "start", "stop", "restart"],
                help="서비스에 수행할 작업을 선택하세요"
            )
        
        with col2:
            service_name = st.text_input(
                "서비스명",
                value="ssh",
                help="관리할 서비스의 이름을 입력하세요 (예: ssh, nginx, apache)"
            )
        
        if st.button("🔧 서비스 관리 실행", type="primary", use_container_width=True):
            if not service_name:
                st.error("서비스명을 입력해주세요.")
            else:
                with st.spinner("서비스 관리를 실행하고 있습니다..."):
                    result = client.call_tool("service_management", {
                        "action": service_action,
                        "service_name": service_name
                    })
                    
                    if result.get("success"):
                        st.success(f"✅ {result['result']}")
                    else:
                        st.error(f"❌ 서비스 관리 실패: {result.get('error', '알 수 없는 오류')}")
    
    # 탭 5: Claude 대화
    with tab5:
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
    
    # 탭 6: 도구 연동 대화
    with tab6:
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
                placeholder="예: 현재 시스템 정보를 알려주고, 실행 중인 프로세스 중 CPU 사용률이 높은 것을 찾아줘."
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
                                    "timestamp": time.strftime("%H:%M:%S")
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
        else:
            st.warning("도구 목록을 불러올 수 없습니다.")

if __name__ == "__main__":
    main()
