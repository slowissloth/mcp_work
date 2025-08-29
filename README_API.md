# Claude API MCP Server & Streamlit Client

Claude API를 통한 Model Context Protocol (MCP) 서버와 Streamlit 기반 클라이언트입니다.

## 🏗️ 프로젝트 구조

```
mcp_work/
├── claude_api_mcp_server.py    # FastAPI 기반 MCP 서버
├── streamlit_client.py         # Streamlit 기반 클라이언트
├── config.py                   # 설정 관리
├── requirements.txt            # Python 의존성
├── run_streamlit.sh           # Streamlit 실행 스크립트
├── .api_key                   # Anthropic API 키 (Git 제외)
├── .gitignore                 # Git 제외 파일 목록
└── venv/                      # Python 가상환경
```

## 🚀 주요 기능

### MCP 서버 (claude_api_mcp_server.py)
- **기본 도구**: hello_world, get_current_time, calculate
- **시스템 모니터링**: system_info, process_list, process_control, service_management
- **Claude API 연동**: 메시지 전송 및 도구 연동 대화
- **FastAPI 기반**: RESTful API 엔드포인트 제공

### Streamlit 클라이언트 (streamlit_client.py)
- **📊 대시보드**: 서버 상태 및 도구 정보
- **🛠️ 도구 테스트**: 개별 도구 실행 및 결과 확인
- **💬 Claude 채팅**: Claude API와 직접 대화
- **🔧 도구 연동 채팅**: Claude와 MCP 도구를 함께 사용
- **🖥️ 시스템 정보**: 시스템 상태 모니터링
- **⚙️ 프로세스 관리**: 프로세스 및 서비스 제어

## 📋 요구사항

- Python 3.8+
- Anthropic API 키

## 🛠️ 설치 및 설정

### 1. 저장소 클론
```bash
git clone <repository-url>
cd mcp_work
```

### 2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate     # Windows
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. API 키 설정
`.api_key` 파일을 생성하고 Anthropic API 키를 입력하세요:
```bash
echo "your-api-key-here" > .api_key
```

## 🚀 실행 방법

### MCP 서버 실행
```bash
python claude_api_mcp_server.py
```
서버는 기본적으로 `http://localhost:8005`에서 실행됩니다.

### Streamlit 클라이언트 실행
```bash
# 방법 1: 직접 실행
streamlit run streamlit_client.py

# 방법 2: 스크립트 사용
chmod +x run_streamlit.sh
./run_streamlit.sh
```

클라이언트는 `http://localhost:8501`에서 실행됩니다.

## 🔧 사용 가능한 도구

### 기본 도구
- **hello_world**: 인사말 생성
- **get_current_time**: 현재 시간 조회
- **calculate**: 수학 계산 수행

### 시스템 도구
- **system_info**: 시스템 정보 조회 (기본/상세/전체)
- **process_list**: 실행 중인 프로세스 목록
- **process_control**: 프로세스 제어 (시작/중지/재시작/종료)
- **service_management**: 시스템 서비스 관리

## 📡 API 엔드포인트

### 도구 관련
- `GET /tools` - 사용 가능한 도구 목록
- `POST /tools/call` - 도구 실행

### Claude 연동
- `POST /claude/message` - Claude와 직접 대화
- `POST /claude/message-with-tools` - 도구를 사용한 Claude 대화

## 💡 사용 예시

### 도구 실행
```python
import requests

# 도구 목록 조회
tools = requests.get("http://localhost:8005/tools").json()

# 도구 실행
result = requests.post("http://localhost:8005/tools/call", json={
    "tool_name": "system_info",
    "arguments": {"info_type": "basic"}
}).json()
```

### Claude와 도구 연동
```python
response = requests.post("http://localhost:8005/claude/message-with-tools", json={
    "message": "시스템 정보를 알려주고 CPU 사용량이 높은 프로세스를 찾아줘",
    "tools": ["system_info", "process_list"]
})
```

## 🔒 보안 주의사항

- `.api_key` 파일은 절대 Git에 커밋하지 마세요
- 프로세스 제어 도구는 시스템에 영향을 줄 수 있으므로 주의해서 사용하세요
- 서비스 관리 도구는 관리자 권한이 필요할 수 있습니다

## 🐛 문제 해결

### 일반적인 문제
1. **API 키 오류**: `.api_key` 파일이 올바르게 설정되었는지 확인
2. **포트 충돌**: 8005번 포트가 사용 중인지 확인
3. **의존성 오류**: `pip install -r requirements.txt` 재실행

### 로그 확인
서버 실행 시 상세한 로그를 확인할 수 있습니다. `config.py`에서 로그 레벨을 조정할 수 있습니다.

## 📚 추가 문서

- `Claude_연동_가이드.md`: Claude Desktop 연동 방법
- `run_streamlit.sh`: Streamlit 실행 스크립트

## 🤝 기여

이슈나 개선사항이 있으면 GitHub Issues에 등록해 주세요.

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.
