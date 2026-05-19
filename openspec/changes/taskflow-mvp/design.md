## Context

소규모 팀(3-5인)을 위한 칸반+채팅 MVP. FastAPI 백엔드와 Vanilla JS 프론트엔드를 단일 서버로 제공하며, 로컬은 SQLite, 배포는 Vercel + Neon(PostgreSQL)을 사용한다. SQLAlchemy ORM으로 양쪽 DB를 추상화한다.

스토리보드 v2의 결정 8건을 반영한 통합본 기준으로 설계한다.

## Goals / Non-Goals

**Goals:**
- API 18개 (Auth 4, Team 5, Task 6, Chat 3) 완전 구현
- DB 4테이블 (users, teams, tasks, messages) — 스토리보드 결정 #1
- 로컬 실행: `uvicorn main:app` 한 명령으로 FE+BE 통합 서빙
- 배포: Vercel Serverless + Neon Pooled Connection 자동 주입
- 프론트엔드 9개 화면 (로그인·회원가입·팀선택·칸반·채팅·멤버·모바일 등)

**Non-Goals:**
- WebSocket 실시간 연결 (5초 폴링으로 대체)
- 파일 업로드, 알림, 전문검색
- pytest/jest 자동화 테스트
- 마이크로서비스 분리
- JWT 갱신 토큰 (24h 고정)

## Decisions

### 1. 단일 FastAPI 앱으로 FE+BE 통합

**선택**: `app/static/`에 HTML/JS/CSS를 두고 `StaticFiles`로 서빙.  
**대안**: 별도 프론트엔드 서버 분리.  
**이유**: 로컬 개발 간소화 + Vercel 배포 시 동일 코드 베이스 유지.

### 2. SQLAlchemy + 환경변수로 SQLite/Neon 전환

**선택**: `DATABASE_URL` 환경변수로 DB 결정. 로컬 미설정 시 `sqlite:///./taskflow.db`, Vercel에서는 Neon Pooled URL 자동 주입.  
**이유**: 코드 변경 없이 환경만 다르게 유지.

### 3. users.team_id로 멤버십 관리 (스토리보드 결정 #1)

**선택**: `users.team_id FK → teams` 단일 컬럼으로 소속 팀 관리. 1인 1팀 제약.  
**대안**: `team_members` 별도 테이블 (N:M).  
**이유**: "DB 4테이블 제약 유지". 1인 1팀이 MVP 전제조건. `GET /teams`는 제거하고 현재 팀 정보는 `GET /auth/me` 또는 `GET /teams/{id}`로 조회.

### 4. PATCH /tasks/{id}/status + PUT /tasks/{id} 분리 (스토리보드 결정 #3)

**선택**: 드래그 드롭 → `PATCH /tasks/{id}/status { status }`, 카드 상세 수정 → `PUT /tasks/{id} { title, assignee_id }` 별도 엔드포인트.  
**이유**: 칸반 드래그는 status만 바꾸는 경량 호출 필요. 카드 상세 모달에서 title/assignee 수정은 별도 UI + API.

### 5. tasks.assignee_id 추가 (스토리보드 결정 #4)

**선택**: `tasks.assignee_id FK → users NULL`. '내 태스크' 필터 = `assignee_id = current_user_id` (creator_id 아님).  
**이유**: "내가 만든 태스크 ≠ 내 태스크". 칸반 @me 필터 + 미할당 필터 지원.

### 6. Team API 5개 (결정 #8 반영)

**선택**: `GET /teams/{id}` (팀 정보 조회) + `DELETE /teams/{id}/leave` (팀 떠나기) 추가.  
**이유**: 스토리보드 통합 매핑표에서 확인. 팀 정보 직접 조회 필요 + 이미 다른 팀 소속 시 409 처리 위해 떠나기 API 필요.

### 7. JWT → localStorage (서버 무상태) (스토리보드 결정 #5)

**선택**: 서버에 세션 저장 없음. `POST /auth/logout`은 200만 반환.  
**이유**: Vercel Serverless 환경에서 블랙리스트 불필요.

### 8. 채팅 폴링: GET /teams/{id}/messages?since=

**선택**: `since` 파라미터(ISO 8601)로 마지막 조회 이후 메시지만 반환. 초기 로드는 최근 50개.  
**이유**: 전체 메시지 재조회 방지. 폴링 실패 시 exponential backoff 재시도.

## Risks / Trade-offs

- **1인 1팀 제약** → 팀 전환 시 기존 팀 떠나야 함. `DELETE /teams/{id}/leave` API로 처리.
- **JWT 갱신 없음** → 24h 후 강제 재로그인. 만료 시 401 → localStorage 삭제 → /login redirect.
- **5초 폴링** → 동시 50명 기준 분당 600 req. Neon Free 티어 한도 내 예상.
- **SQLite 로컬 동시성** → 멀티 워커 환경에서 write lock 충돌 가능. 로컬 단일 워커로 제한.
- **Vercel Serverless 콜드스타트** → FastAPI 초기 응답 지연 가능. Free 티어 수용.
