## 1. 프로젝트 초기 설정

- [x] 1.1 프로젝트 디렉토리 구조 생성 (app/, app/static/, app/routers/)
- [x] 1.2 requirements.txt 작성 (fastapi, uvicorn, sqlalchemy, python-jose, passlib[bcrypt], python-dotenv)
- [x] 1.3 DATABASE_URL 환경변수 설정 (.env.local, SQLite 기본값 처리)
- [x] 1.4 SQLAlchemy 엔진 + 세션 설정 (database.py)

## 2. DB 모델 정의 및 마이그레이션

- [x] 2.1 users 모델 정의 (id, email UNIQUE, password_hash, team_id FK → teams NULL, created_at)
- [x] 2.2 teams 모델 정의 (id, name, invite_code UNIQUE, owner_id FK → users)
- [x] 2.3 tasks 모델 정의 (id, team_id FK → teams, title, status ENUM(TODO/DOING/DONE), creator_id FK → users, assignee_id FK → users NULL, created_at)
- [x] 2.4 messages 모델 정의 (id, team_id FK → teams, user_id FK → users, content, created_at)
- [x] 2.5 앱 시작 시 create_all() 자동 마이그레이션 연결

## 3. 인증 API (Auth 4개)

- [x] 3.1 POST /auth/signup — bcrypt 해시, 중복 이메일 409, JWT 반환
- [x] 3.2 POST /auth/login — 자격증명 검증, JWT(24h) 발급
- [x] 3.3 GET /auth/me — Bearer 토큰 검증, 사용자 정보 반환 (team_id 포함)
- [x] 3.4 POST /auth/logout — 200 반환 (서버 무상태)
- [x] 3.5 JWT 의존성 함수 구현 (get_current_user)

## 4. 팀 관리 API (Team 5개)

- [x] 4.1 POST /teams — 팀 생성, ABCD-1234 형식 초대코드 생성, users.team_id = 신규 팀 ID 업데이트, 409 ALREADY_IN_TEAM 처리
- [x] 4.2 GET /teams/{id} — 팀 소속 검증 후 팀 정보 반환 (id, name, invite_code, owner_id)
- [x] 4.3 POST /teams/join — 초대코드 검증, users.team_id 업데이트, 409 ALREADY_IN_TEAM / 404 TEAM_NOT_FOUND 처리
- [x] 4.4 GET /teams/{id}/members — 팀 소속 검증 후 users.team_id 기준 멤버 목록 반환
- [x] 4.5 DELETE /teams/{id}/leave — users.team_id = NULL 업데이트, owner 떠나기 403 처리

## 5. 칸반 태스크 API (Task 6개)

- [x] 5.1 POST /teams/{id}/tasks — 태스크 생성, 기본 status=TODO, assignee_id 선택 입력
- [x] 5.2 GET /teams/{id}/tasks — 팀 전체 태스크 반환, filter=@me|unassigned 쿼리 파라미터 지원
- [x] 5.3 GET /tasks/{id} — 단건 조회, 팀 소속 검증
- [x] 5.4 PATCH /tasks/{id}/status — status(TODO/DOING/DONE) 단독 변경, 드래그 앤 드롭용 경량 API
- [x] 5.5 PUT /tasks/{id} — title + assignee_id 수정, 카드 상세 모달용, owner는 모든 태스크 수정 가능
- [x] 5.6 DELETE /tasks/{id} — owner는 모든 태스크 삭제 가능, 일반 멤버는 creator_id 본인 태스크만 삭제 (403 처리)

## 6. 채팅 API (Chat 3개)

- [x] 6.1 POST /teams/{id}/messages — 메시지 전송, 1000자 제한
- [x] 6.2 GET /teams/{id}/messages?since= — since 이후 메시지, 없으면 최근 50개
- [x] 6.3 DELETE /messages/{id} — 본인 메시지만 삭제 (403 처리)

## 7. 프론트엔드 (Vanilla JS + Tailwind, 9개 화면)

- [x] 7.1 로그인/회원가입 화면 HTML (탭 전환, 이메일/비밀번호 입력, 오류 메시지)
- [x] 7.2 팀 선택 화면 HTML (내 팀 카드, 팀 만들기, 초대코드 입력+합류)
- [x] 7.3 칸반 화면 HTML (3컬럼 TODO/DOING/DONE, 각 컬럼 + 버튼, 태스크 카드, @me/unassigned 필터)
- [x] 7.4 채팅 화면 HTML (메시지 리스트, 입력창, 발신자+시각 표시, 삭제 버튼)
- [x] 7.5 멤버 목록 화면 HTML (팀 멤버 이메일+가입일 목록, 초대코드 표시)
- [ ] 7.6 태스크 상세 모달 (title 수정, assignee_id 드롭다운)
- [ ] 7.7 모바일 칸반 화면 (단일 컬럼 스크롤, 컬럼 탭 전환)
- [ ] 7.8 모바일 채팅 화면 (풀스크린, 하단 고정 입력창)
- [ ] 7.9 팀 떠나기 확인 모달 (owner 불가 안내, 일반 멤버 확인)
- [x] 7.10 JWT localStorage 저장/삭제 유틸리티 구현
- [x] 7.11 API 호출 공통 fetch 래퍼 (Authorization 헤더 자동 주입, 401 시 /login 리다이렉트)
- [x] 7.12 칸반 드래그 앤 드롭 → PATCH /tasks/{id}/status 연동
- [x] 7.13 채팅 5초 폴링 구현 (setInterval + since 타임스탬프 관리, exponential backoff)

## 8. 통합 및 배포

- [x] 8.1 FastAPI StaticFiles로 app/static/ 서빙 연결
- [x] 8.2 CORS 허용 도메인 명시 (로컬 + Vercel 도메인)
- [x] 8.3 vercel.json 작성 (Python 런타임, 라우팅 설정)
- [ ] 8.4 Vercel Storage Neon 연동 확인 (DATABASE_URL 자동 주입)
- [ ] 8.5 Vercel 배포 후 전체 기능 수동 동작 확인
