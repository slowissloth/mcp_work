# Claude API MCP Server

Claude API를 통한 Model Context Protocol (MCP) 구현 서버입니다.

## 🚀 주요 특징

- **Claude API 연동**: Anthropic Claude API를 통한 AI 대화
- **MCP 도구 지원**: 사용자 정의 도구들을 Claude와 연동
- **웹 API**: RESTful API로 쉽게 통합 가능
- **실시간 도구 실행**: Claude의 요청에 따른 즉시 도구 실행
- **Streamlit 클라이언트**: 인터랙티브한 웹 UI로 쉬운 테스트

## 📋 사전 요구사항

### 1. Claude API 키
- [Anthropic Console](https://console.anthropic.com/)에서 API 키 발급
- 환경 변수로 설정: `export ANTHROPIC_API_KEY="your_api_key_here"`

### 2. Python 환경
- Python 3.8 이상
- 가상환경 권장

## 🛠️ 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정
```bash
export ANTHROPIC_API_KEY="your_api_key_here"
export MCP_SERVER_HOST="localhost"
export MCP_SERVER_PORT="8005"
```

### 3. 서버 실행
```bash
python claude_api_mcp_server.py
```

### 4. 접속 확인
- 서버: http://localhost:8005
- API 문서: http://localhost:8005/docs
- 대화형 API: http://localhost:8005/redoc

## 🌐 Streamlit 클라이언트

### 1. Streamlit 클라이언트 실행
```bash
# 방법 1: 직접 실행
streamlit run streamlit_client.py

# 방법 2: 스크립트 실행
./run_streamlit.sh
```

### 2. Streamlit 접속
- 브라우저에서 http://localhost:8501 접속
- 자동으로 웹 UI가 열립니다

### 3. Streamlit 기능
- **🏠 대시보드**: MCP 서버 상태 및 도구 목록
- **🛠️ 도구 테스트**: 개별 도구 실행 및 테스트
- **💬 Claude 대화**: Claude와 일반 대화
- **🔧 도구 연동 대화**: Claude와 도구를 연동한 대화

## 🔧 API 엔드포인트

### 기본 정보
- `GET /` - 서버 상태 확인
- `GET /tools` - 사용 가능한 도구 목록

### 도구 실행
- `POST /tools/call` - 도구 실행
  ```json
  {
    "tool_name": "hello_world",
    "arguments": {"name": "홍길동"}
  }
  ```

### Claude 연동
- `POST /claude/message` - Claude와 일반 대화
- `POST /claude/message-with-tools` - 도구 연동 대화

## 🛠️ 사용 가능한 도구

### 1. hello_world
- **설명**: 인사말 생성
- **입력**: `name` (문자열)
- **예시**: `{"name": "홍길동"}`

### 2. get_current_time
- **설명**: 현재 시간 반환
- **입력**: 없음
- **예시**: `{}`

### 3. calculate
- **설명**: 수학 계산
- **입력**: `expression` (문자열)
- **예시**: `{"expression": "2+3*4"}`

## 📱 클라이언트 사용 예제

### Python 클라이언트
```python
from client_example import ClaudeAPIMCPClient

# 클라이언트 생성
client = ClaudeAPIMCPClient()

# 도구 목록 조회
tools = client.list_tools()

# 도구 실행
result = client.call_tool("hello_world", {"name": "홍길동"})

# Claude와 대화
response = client.send_message_to_claude("안녕하세요!")
```

### Streamlit 클라이언트
```bash
# Streamlit 앱 실행
streamlit run streamlit_client.py

# 브라우저에서 http://localhost:8501 접속
# 직관적인 웹 UI로 모든 기능 테스트 가능
```

### cURL 예제
```bash
# 도구 목록 조회
curl http://localhost:8005/tools

# 도구 실행
curl -X POST http://localhost:8005/tools/call \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "hello_world", "arguments": {"name": "홍길동"}}'

# Claude와 대화
curl -X POST http://localhost:8005/claude/message \
  -H "Content-Type: application/json" \
  -d '{"message": "안녕하세요!"}'
```

## 🔍 문제 해결

### API 키 오류
```
⚠️  ANTHROPIC_API_KEY가 설정되지 않았습니다.
   환경 변수로 설정하거나 .env 파일을 생성하세요.
```
**해결방법**: `export ANTHROPIC_API_KEY="your_key"`

### 포트 충돌
```
Error: [Errno 48] Address already in use
```
**해결방법**: 다른 포트 사용 또는 기존 프로세스 종료

### Claude API 오류
```
Claude API 호출 실패: 401 Unauthorized
```
**해결방법**: API 키 확인 및 권한 확인

### Streamlit 실행 오류
```
ModuleNotFoundError: No module named 'streamlit'
```
**해결방법**: `pip install streamlit` 실행

## 🚀 확장 방법

### 새로운 도구 추가
1. `MCPServer` 클래스의 `tools` 리스트에 도구 추가
2. `execute_tool` 메서드에 도구 실행 로직 구현

```python
{
    "name": "new_tool",
    "description": "새로운 도구 설명",
    "inputSchema": {
        "type": "object",
        "properties": {
            "param": {"type": "string"}
        },
        "required": ["param"]
    }
}
```

### 커스텀 모델 사용
```python
response = claude_client.messages.create(
    model="claude-3-haiku-20240307",  # 다른 모델 사용
    max_tokens=1000,
    messages=[{"role": "user", "content": message}]
)
```

### Streamlit UI 커스터마이징
- `streamlit_client.py`에서 UI 레이아웃 수정
- 새로운 탭 추가
- 차트 및 시각화 추가

## 📚 추가 정보

- [Anthropic Claude API 문서](https://docs.anthropic.com/)
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Streamlit 공식 문서](https://docs.streamlit.io/)
- [MCP 프로토콜 스펙](https://modelcontextprotocol.io/)

## 🤝 기여하기

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## �� 라이선스

MIT License
