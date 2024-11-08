# Forcat-Backend

## 프로젝트 개요
Forcat-Backend는 반려동물을 위한 쇼핑몰 서비스의 백엔드로, 상품 관리, 소셜 로그인, 장바구니, 결제 기능 등을 지원합니다. **Python 3.12**와 **Django 5.1.2**를 기반으로 구축되었으며, API 서버는 `Docker`와 `docker-compose`로 구성하여 배포했습니다. 데이터베이스로는 초기 개발 속도를 고려하여 **SQLite**를 사용하고 있습니다.

### 프로젝트 환경
- **프로그래밍 언어**: Python 3.12
- **프레임워크**: Django 5.1.2, Django REST Framework (DRF) 3.15.2
- **인프라**: Docker, Docker Compose
- **데이터베이스**: SQLite

## 기술 스택 및 선택 이유
`Python` 및 `Django`는 빠른 프로토타이핑에 적합하며, 특히 CRUD 중심의 기능 개발에 강점이 있습니다. 이번 프로젝트는 3주 내의 빠른 개발 완료가 요구되어, 효율적인 API 개발을 지원하는 Django 프레임워크가 적합하다고 판단했습니다.

## 주요 구현 특징
### 1. RESTful API 설계
RESTful 아키텍처 원칙을 준수하여 API를 설계했습니다. 
예를 들어, 사용자의 고양이라는 리소스는 사용자와 종속적인 관계이므로, URI를 `/api/users/{user_id}/cats`와 같이 구조화하여 가독성과 의미를 명확히 했습니다.

### 2. 테스트 코드 작성
API의 안정성과 신뢰성을 보장하기 위해, 모든 주요 엔드포인트에 대한 테스트 코드를 작성하고 있습니다. 이를 통해 프론트엔드 팀이 API를 사용하기 전에 최소한의 기능 검증을 수행합니다.

## 주요 구현 사항 (기능별 Sprint)
### SPRINT_1: 상품 관리 기능
- **[완료]** 상품 CRUD

### SPRINT_2: 사용자 인증 및 고양이 관리 기능
- **[완료]** JWT 인증 및 소셜 로그인 (카카오, 구글, 네이버) 구현
- **[완료]** 사용자의 고양이 정보 CRUD
- **[완료]** 장바구니 기능 구현

### SPRINT_3: 상품 주문 및 결제 연동
- **[완료]** 주문 내역 및 결제 트랜잭션 구현
- **[완료]** 결제 게이트웨이(PG) 연동

### SPRINT_4: 부가 기능 및 추천 서비스
- **[완료]** 이벤트 기능 추가 (예: 특가, 할인)
- **[완료]** 추천 상품 서비스 구현

## 시작하기 (Getting Started)
   ```bash
   git clone https://github.com/your-repo/forcat-backend.git
   cd forcat-backend
   docker-compose up -d