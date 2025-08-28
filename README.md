# Claude Desktop MCP Server

클로드 데스크탑과 연동하는 Model Context Protocol (MCP) 서버입니다.

## 🚀 시작하기

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. MCP 서버 실행

```bash
python mcp_server.py
```

## 🔧 클로드 데스크탑 설정

### 1. 클로드 데스크탑 열기

### 2. 설정 메뉴로 이동
- `Cmd + ,` (Mac) 또는 `Ctrl + ,` (Windows/Linux)

### 3. MCP 서버 추가
- "Model Context Protocol" 섹션에서 "Add Server" 클릭
- 서버 이름: `claude-desktop-mcp-server`
- 명령어: `python /path/to/your/mcp_server.py`
- 작업 디렉토리: 프로젝트 폴더 경로

### 4. 서버 활성화
- 추가한 서버를 활성화 상태로 변경

## 🛠️ 사용 가능한 도구

### 1. hello_world
- **설명**: 간단한 인사말을 반환
- **입력**: `name` (문자열) - 인사할 사람의 이름
- **사용 예**: "안녕하세요, 홍길동님! MCP 서버에 오신 것을 환영합니다."

### 2. get_current_time
- **설명**: 현재 시간을 반환
- **입력**: 없음
- **사용 예**: "현재 시간: 2024-08-28 14:30:00"

## 📁 프로젝트 구조

```
mcp_work/
├── mcp_server.py      # MCP 서버 메인 파일
├── requirements.txt   # Python 의존성
├── README.md         # 이 파일
└── venv/            # 가상환경 (선택사항)
```

## 🔍 문제 해결

### 서버 연결 안됨
1. Python 경로 확인
2. 의존성 설치 확인
3. 파일 권한 확인

### 도구 실행 오류
1. 로그 확인
2. 입력 형식 확인
3. 서버 재시작

## 📚 추가 정보

- [MCP 공식 문서](https://modelcontextprotocol.io/)
- [Claude Desktop MCP 가이드](https://docs.anthropic.com/claude/docs/model-context-protocol-mcp)

## 🤝 기여하기

이슈나 개선사항이 있으시면 GitHub에 PR을 보내주세요!
