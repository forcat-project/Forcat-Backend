# 베이스 이미지 설정
FROM python:3.12-slim

# 작업 디렉토리 설정
WORKDIR /app

# Poetry 설치
RUN pip install --no-cache-dir poetry

# Poetry 설정: 가상 환경을 Docker 컨테이너의 루트에서 생성하도록 함
RUN poetry config virtualenvs.create false

# 프로젝트의 의존성 파일들을 컨테이너로 복사
COPY pyproject.toml poetry.lock ./

# 의존성 설치
RUN poetry install --no-root

# 애플리케이션 소스 코드를 컨테이너로 복사
COPY . .

# 포트 설정 (Django의 기본 포트)
EXPOSE 8000

# Django 서버 실행
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
