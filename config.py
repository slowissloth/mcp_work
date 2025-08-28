"""
Claude API MCP 서버 설정
"""

import os
from typing import Optional

class Config:
    """설정 클래스"""
    
    # Claude API 설정
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "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")
    
    # MCP 서버 설정
    MCP_SERVER_HOST: str = os.getenv("MCP_SERVER_HOST", "localhost")
    MCP_SERVER_PORT: int = int(os.getenv("MCP_SERVER_PORT", "8005"))
    
    # 로깅 설정
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls) -> bool:
        """설정 유효성 검사"""
        if not cls.ANTHROPIC_API_KEY:
            print("⚠️  ANTHROPIC_API_KEY가 설정되지 않았습니다.")
            print("   환경 변수로 설정하거나 .env 파일을 생성하세요.")
            return False
        return True

# 전역 설정 인스턴스
config = Config()
