## 1. 프로젝트 초기 설정

- [ ] 1.1 프로젝트 디렉토리 구조 생성 (app/, app/static/, app/routers/)
- [ ] 1.2 requirements.txt 작성 (fastapi, uvicorn, sqlalchemy, python-jose, passlib[bcrypt], python-dotenv)
- [ ] 1.3 DATABASE_URL 환경변수 설정 (.env.local, SQLite 기본값 처리)
- [ ] 1.4 SQLAlchemy 엔진 + 세션 설정 (database.py)

## 2. DB 모델 정의 및 마이그레이션

- [ ] 2.1 users 모델 정의 (id, email UNIQUE, password_hash, created_at)
- [ ] 2.2 teams 모델 정의 (id, name, invite_code UNIQUE, owner_id FK)
- [ ] 2.3 team_members 모델 정의 (team_id + user_id 복합 PK, joined_at)
- [ ] 2.4 tasks 모델 정의 (id, team_id FK, title, status, creator_id FK)
- [ ] 2.5 messages 모델 정의 (id, team_id FK, user_id FK, content, created_at)
- [ ] 2.6 앱 시작 시 create_all() 자동 마이그레이션 연결

## 3. 인증 API (Auth 4개)

- [ ] 3.1 POST /auth/signup — bcrypt 해시, 중복 이메일 409, JWT 반환
- [ ] 3.2 POST /auth/login — 자격증명 검증, JWT(24h) 발급
- [ ] 3.3 GET /auth/me — Bearer 토큰 검증, 사용자 정보 반환
- [ ] 3.4 POST /auth/logout — 200 반환 (서버 무상태)
- [ ] 3.5 JWT 의존성 함수 구현 (get_current_user)

## 4. 팀 관리 API (Team 4개)

- [ ] 4.1 POST /teams — 팀 생성, ABCD-1234 형식 초대코드 생성, team_members owner 자동 등록
- [ ] 4.2 GET /teams — team_members 기준 내 팀 목록 반환
- [ ] 4.3 POST /teams/join — 초대코드 검증, team_members 등록 (중복 무시)
- [ ] 4.4 GET /teams/{id}/members — 팀 소속 검증 후 멤버 목록 반환

## 5. 칸반 태스크 API (Task 5개)

- [ ] 5.1 POST /teams/{id}/tasks — 태스크 생성, 기본 status=TODO
- [ ] 5.2 GET /teams/{id}/tasks — 팀 전체 태스크 반환
- [ ] 5.3 GET /tasks/{id} — 단건 조회, 팀 소속 검증
- [ ] 5.4 PATCH /tasks/{id} — status(TODO/DOING/DONE) 또는 title 선택적 수정
- [ ] 5.5 DELETE /tasks/{id} — 삭제, 팀 소속 검증

## 6. 채팅 API (Chat 3개)

- [ ] 6.1 POST /teams/{id}/messages — 메시지 전송, 1000자 제한
- [ ] 6.2 GET /teams/{id}/messages?since= — since 이후 메시지, 없으면 최근 50개
- [ ] 6.3 DELETE /messages/{id} — 본인 메시지만 삭제 (403 처리)

## 7. 프론트엔드 (Vanilla JS + Tailwind)

- [ ] 7.1 로그인/회원가입 화면 HTML (상단 로고, 이메일/비밀번호 입력, 버튼)
- [ ] 7.2 팀 선택 화면 HTML (내 팀 목록, 팀 만들기 버튼, 초대코드 입력+합류)
- [ ] 7.3 칸반 화면 HTML (3컬럼 TODO/DOING/DONE, 각 컬럼 + 버튼, 태스크 카드)
- [ ] 7.4 채팅 화면 HTML (메시지 리스트, 입력창, 발신자+시각 표시)
- [ ] 7.5 JWT localStorage 저장/삭제 유틸리티 구현
- [ ] 7.6 API 호출 공통 fetch 래퍼 (Authorization 헤더 자동 주입)
- [ ] 7.7 칸반 드래그 앤 드롭 → PATCH /tasks/{id} 연동
- [ ] 7.8 채팅 5초 폴링 구현 (setInterval + since 타임스탬프 관리)

## 8. 통합 및 배포

- [ ] 8.1 FastAPI StaticFiles로 app/static/ 서빙 연결
- [ ] 8.2 CORS 허용 도메인 명시 (로컬 + Vercel 도메인)
- [ ] 8.3 vercel.json 작성 (Python 런타임, 라우팅 설정)
- [ ] 8.4 Vercel Storage Neon 연동 확인 (DATABASE_URL 자동 주입)
- [ ] 8.5 Vercel 배포 후 전체 기능 수동 동작 확인
