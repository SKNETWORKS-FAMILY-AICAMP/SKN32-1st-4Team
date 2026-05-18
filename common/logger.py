import logging
import os
from datetime import datetime

# 1. 프로젝트 루트 경로 계산
# 현재 파일(common/logger.py) 기준 두 단계 위가 루트
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 2. 로그 폴더 경로
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")
os.makedirs(LOG_DIR, exist_ok=True)  # 없으면 생성

# 3. 로그 파일 이름 (날짜별)
log_file = os.path.join(LOG_DIR, f"{datetime.now().strftime('%Y-%m-%d')}.log")

# 4. 로거 생성
logger = logging.getLogger("project_logger")
logger.setLevel(logging.INFO)  # INFO 이상 기록

# 5. 파일 핸들러
file_handler = logging.FileHandler(log_file, encoding="utf-8")
file_handler.setLevel(logging.INFO)

# 6. 콘솔 출력 핸들러
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# 7. 로그 포맷 설정
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# 8. 핸들러 등록 (중복 방지)
if not logger.hasHandlers():
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)