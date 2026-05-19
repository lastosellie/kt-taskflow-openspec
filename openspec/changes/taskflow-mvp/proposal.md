## Why

소규모 팀(3-5인)이 업무 진행 상황을 칸반 보드와 실시간 채팅으로 한 화면에서 추적할 수 있는 MVP가 없다. 팀 리더·팀원·신규 합류자 모두 별도 도구 없이 초대코드 하나로 즉시 합류하고, 태스크 상태와 대화를 동시에 볼 수 있어야 한다.

## What Changes

- **새 서비스 구축**: FastAPI 백엔드 + Vanilla JS + Tailwind CSS 프론트엔드
- **인증**: 이메일/비밀번호 회원가입·로그인, JWT(24h) 발급, bcrypt 해시
- **팀 관리**: 팀 생성, 초대코드(ABCD-1234 형식) 발급·합류, 멤버 목록 조회
- **칸반 보드**: TODO/DOING/DONE 3컬럼 태스크 추가·상태이동·삭제, 드래그 지원
- **채팅**: 팀 단위 텍스트 채팅, 5초 폴링, 발신자+시각 표시
- **배포**: Vercel(FE+BE 일체형) + Vercel Storage Neon(PostgreSQL) 자동 주입

## Capabilities

### New Capabilities

- `auth`: 회원가입, 로그인, JWT 발급, 내 정보 조회, 로그아웃
- `team-management`: 팀 생성, 초대코드 발급·합류, 멤버 목록 (team_members 테이블 포함)
- `kanban`: 태스크 생성·조회·상태/제목 수정(PATCH)·삭제
- `chat`: 메시지 송수신(5초 폴링), 메시지 삭제
- `deployment`: 로컬 SQLite → 배포 Neon 전환, Vercel 배포 설정

### Modified Capabilities

<!-- 신규 프로젝트이므로 해당 없음 -->

## Impact

- **API**: 17개 엔드포인트 신규 (Auth 4, Team 4, Task 6→5+PATCH 통합, Chat 3)
- **DB**: 5테이블 (users, teams, team_members, tasks, messages)
- **외부 의존성**: Vercel Storage Neon (Free 티어), JWT, bcrypt
- **브라우저**: 최신 Chrome + Safari (모바일 포함)
- **범위 외**: WebSocket, 파일첨부, 전문검색, 알림, 다국어, 테스트 자동화
