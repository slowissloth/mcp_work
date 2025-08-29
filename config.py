"""
Claude API MCP 서버 설정
"""
# Claude API MCP 서버 설정 파일

import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Config:
    """설정 클래스"""
    
    # API 키는 .api_key 파일에서 읽기
    ANTHROPIC_API_KEY = ""
    
    # MCP 서버 설정
    MCP_SERVER_HOST = os.getenv("MCP_SERVER_HOST", "localhost")
    MCP_SERVER_PORT = int(os.getenv("MCP_SERVER_PORT", "8005"))
    
    # 로그 레벨
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def load_api_key(cls) -> str:
        """API 키를 .api_key 파일에서 로드"""
        try:
            api_key_file = os.path.join(os.path.dirname(__file__), ".api_key")
            if os.path.exists(api_key_file):
                with open(api_key_file, 'r', encoding='utf-8') as f:
                    api_key = f.read().strip()
                    if api_key:
                        return api_key
        except Exception as e:
            print(f"API 키 파일 읽기 오류: {e}")
        
        # 환경 변수에서도 확인
        env_api_key = os.getenv("ANTHROPIC_API_KEY")
        if env_api_key:
            return env_api_key
        
        return ""
    
    @classmethod
    def validate(cls) -> bool:
        """설정 유효성 검사"""
        api_key = cls.load_api_key()
        if not api_key:
            print("⚠️  ANTHROPIC_API_KEY가 설정되지 않았습니다.")
            print("   .api_key 파일을 생성하거나 환경 변수로 설정하세요.")
            return False
        
        if not cls.MCP_SERVER_HOST:
            print("⚠️  MCP_SERVER_HOST가 설정되지 않았습니다.")
            return False
        
        if not cls.MCP_SERVER_PORT:
            print("⚠️  MCP_SERVER_PORT가 설정되지 않았습니다.")
            return False
        
        print("✅ 모든 설정이 유효합니다.")
        return True

# 전역 설정 인스턴스
config = Config()
