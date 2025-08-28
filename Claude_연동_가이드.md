# Claude Desktop MCP 서버 연동 가이드

## 🎯 목표
클로드 데스크탑에서 우리가 만든 MCP 서버를 연동하여 추가 기능을 사용할 수 있도록 설정합니다.

## 📋 사전 준비사항

### 1. Python 환경 확인
```bash
# 가상환경 활성화
source venv/bin/activate

# Python 버전 확인 (3.11 이상 필요)
python --version

# MCP 서버 테스트 실행
python mcp_server.py
```

### 2. 파일 경로 확인
현재 프로젝트의 절대 경로를 확인하세요:
```bash
pwd
# 예시: /Users/1113183 (삭제됨)/Github/mcp_work
```

## 🔧 Claude Desktop 설정 단계

### 1단계: Claude Desktop 열기
- 클로드 데스크탑 애플리케이션을 실행합니다.

### 2단계: 설정 메뉴 접근
- **Mac**: `Cmd + ,` (커맨드 + 콤마)
- **Windows/Linux**: `Ctrl + ,` (컨트롤 + 콤마)

### 3단계: MCP 서버 추가
1. 설정 창에서 **"Model Context Protocol"** 섹션을 찾습니다.
2. **"Add Server"** 버튼을 클릭합니다.
3. 다음 정보를 입력합니다:

   **서버 이름**: `claude-desktop-mcp-server`
   
   **명령어**: 
   ```bash
   /Users/1113183\ \(삭제됨\)/Github/mcp_work/venv/bin/python /Users/1113183\ \(삭제됨\)/Github/mcp_work/mcp_server.py
   ```
   
   **작업 디렉토리**: 
   ```
   /Users/1113183 (삭제됨)/Github/mcp_work
   ```

### 4단계: 서버 활성화
- 추가한 서버 옆의 토글 스위치를 **ON** 상태로 변경합니다.
- **"Save"** 버튼을 클릭하여 설정을 저장합니다.

### 5단계: 연결 확인
- 설정 창을 닫고 클로드 데스크탑으로 돌아갑니다.
- 새로운 채팅을 시작하고 MCP 서버가 연결되었는지 확인합니다.

## 🧪 테스트 방법

### 1. 기본 연결 테스트
클로드에게 다음과 같이 질문해보세요:
```
"사용 가능한 도구들을 알려줘"
```

### 2. 도구 실행 테스트
```
"hello_world 도구를 사용해서 '홍길동'에게 인사해줘"
```

```
"현재 시간을 알려줘"
```

## ❗ 문제 해결

### 문제 1: 서버 연결 실패
**증상**: MCP 서버가 연결되지 않음
**해결방법**:
1. Python 경로 확인: `which python`
2. 파일 권한 확인: `ls -la mcp_server.py`
3. 가상환경 재활성화: `source venv/bin/activate`

### 문제 2: 도구 실행 오류
**증상**: 도구는 보이지만 실행 시 오류 발생
**해결방법**:
1. 서버 로그 확인
2. 입력 형식 검증
3. 서버 재시작

### 문제 3: 경로 문제
**증상**: 파일을 찾을 수 없다는 오류
**해결방법**:
1. 절대 경로 사용
2. 공백이 포함된 경로는 이스케이프 처리
3. 작업 디렉토리 설정 확인

## 🔍 고급 설정

### 환경 변수 설정
`.env` 파일을 생성하여 환경 변수를 설정할 수 있습니다:
```bash
# .env 파일 생성
touch .env

# 환경 변수 추가
echo "MCP_SERVER_NAME=claude-desktop-mcp-server" >> .env
echo "MCP_SERVER_VERSION=1.0.0" >> .env
```

### 로그 레벨 조정
`mcp_server.py`에서 로깅 레벨을 조정할 수 있습니다:
```python
logging.basicConfig(level=logging.DEBUG)  # 더 자세한 로그
```

## 📚 추가 리소스

- [MCP 공식 문서](https://modelcontextprotocol.io/)
- [Claude Desktop MCP 가이드](https://docs.anthropic.com/claude/docs/model-context-protocol-mcp)
- [Python MCP 라이브러리](https://github.com/modelcontextprotocol/python-mcp)

## 🎉 성공 확인

모든 설정이 완료되면:
1. 클로드가 MCP 도구들을 인식합니다
2. `hello_world`와 `get_current_time` 도구를 사용할 수 있습니다
3. 클로드가 도구 실행 결과를 표시합니다

축하합니다! 🎊 MCP 서버가 성공적으로 연동되었습니다.
