## Context

소규모 팀(3-5인)을 위한 칸반+채팅 MVP. FastAPI 백엔드와 Vanilla JS 프론트엔드를 단일 서버로 제공하며, 로컬은 SQLite, 배포는 Vercel + Neon(PostgreSQL)을 사용한다. SQLAlchemy ORM으로 양쪽 DB를 추상화한다.

## Goals / Non-Goals

**Goals:**
- API 17개 (Auth 4, Team 4, Task 5+PATCH통합, Chat 3) 완전 구현
- DB 5테이블 (users, teams, team_members, tasks, messages)
- 로컬 실행: `uvicorn main:app` 한 명령으로 FE+BE 통합 서빙
- 배포: Vercel Serverless + Neon Pooled Connection 자동 주입

**Non-Goals:**
- WebSocket 실시간 연결 (5초 폴링으로 대체)
- 파일 업로드, 알림, 전문검색
- pytest/jest 자동화 테스트
- 마이크로서비스 분리

## Decisions

### 1. 단일 FastAPI 앱으로 FE+BE 통합

**선택**: `app/static/`에 HTML/JS/CSS를 두고 `StaticFiles`로 서빙.  
**대안**: 별도 프론트엔드 서버 분리.  
**이유**: 로컬 개발 간소화 + Vercel 배포 시 동일 코드 베이스 유지.

### 2. SQLAlchemy + 환경변수로 SQLite/Neon 전환

**선택**: `DATABASE_URL` 환경변수로 DB 결정. 로컬 미설정 시 `sqlite:///./taskflow.db`, Vercel에서는 Neon Pooled URL 자동 주입.  
**이유**: 코드 변경 없이 환경만 다르게 유지.

### 3. team_members 별도 테이블 (문서 4테이블 → 5테이블)

**선택**: `team_members(team_id, user_id, joined_at)` 복합 PK 테이블 추가.  
**대안**: `users.current_team_id` 단일 컬럼.  
**이유**: `GET /teams`가 복수 팀 반환을 요구하므로 N:M 관계 필요.

### 4. PUT 중복 → PATCH /tasks/{id} 통합

**선택**: 단일 `PATCH /tasks/{id}`로 status, title 선택적 수정.  
**이유**: REST 의미론 준수 + 클라이언트 코드 단순화.

### 5. JWT → localStorage (서버 무상태)

**선택**: 서버에 세션 저장 없음. `POST /auth/logout`은 클라이언트 localStorage 삭제 안내만.  
**이유**: Vercel Serverless 환경에서 세션 스토어 불필요.

### 6. 채팅 폴링: GET /teams/{id}/messages?since=

**선택**: `since` 파라미터(ISO 8601 타임스탬프)로 마지막 조회 이후 메시지만 반환.  
**이유**: 전체 메시지 재조회 방지, 5초 폴링 트래픽 최소화.

## Risks / Trade-offs

- **JWT 갱신 없음** → 24h 후 강제 재로그인 필요. MVP 수용 범위.
- **5초 폴링** → 동시 50명 × 5초 = 분당 600 req. Neon Free 티어 한도 내 예상.
- **SQLite 로컬 동시성** → 멀티 워커 환경에서 write lock 충돌 가능. 로컬 단일 워커로 제한.
- **Vercel Serverless 콜드스타트** → FastAPI 초기 응답 지연 가능. Free 티어 수용.
- **초대코드 신뢰** → 코드 유출 시 무단 합류 가능. MVP 범위 외 보안.
