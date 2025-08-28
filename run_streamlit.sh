#!/bin/bash

# Streamlit 클라이언트 실행 스크립트

echo "🚀 Claude API MCP Streamlit 클라이언트를 시작합니다..."
echo ""

# 가상환경 활성화 확인
if [ -d "venv" ]; then
    echo "📦 가상환경을 활성화합니다..."
    source venv/bin/activate
else
    echo "⚠️  가상환경을 찾을 수 없습니다. venv 폴더를 먼저 생성하세요."
    exit 1
fi

# 의존성 설치 확인
echo "🔍 의존성을 확인합니다..."
pip install -r requirements.txt

# Streamlit 앱 실행
echo "🌐 Streamlit 앱을 시작합니다..."
echo "📱 브라우저에서 http://localhost:8501 접속하세요"
echo "🔄 중단하려면 Ctrl+C를 누르세요"
echo ""

streamlit run streamlit_client.py --server.port 8501 --server.address localhost
