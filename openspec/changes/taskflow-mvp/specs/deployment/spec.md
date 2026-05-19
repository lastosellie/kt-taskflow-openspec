## ADDED Requirements

### Requirement: 로컬 개발 환경 실행
시스템은 단일 명령으로 FE+BE를 동시에 실행할 수 있어야 한다. 로컬에서는 SQLite를 사용하며, FastAPI가 정적 파일을 함께 서빙한다.

#### Scenario: 로컬 서버 시작
- **WHEN** `uvicorn main:app --reload` 실행 시
- **THEN** http://localhost:8000 에서 FE(HTML/JS/CSS)와 API 모두 접근 가능

#### Scenario: 로컬 DB 자동 생성
- **WHEN** DATABASE_URL 환경변수 미설정 상태로 서버 시작 시
- **THEN** 프로젝트 루트에 taskflow.db(SQLite) 자동 생성, 테이블 자동 마이그레이션

---

### Requirement: Vercel 배포
시스템은 Vercel에 FE+BE를 단일 배포로 올릴 수 있어야 한다. Vercel Storage Neon의 DATABASE_URL이 자동 주입된다.

#### Scenario: 배포 성공
- **WHEN** `vercel deploy` (또는 Vercel MCP) 실행 시
- **THEN** 5분 이내에 배포 URL 발급, 해당 URL에서 전체 기능 동작

#### Scenario: Neon DB 자동 연결
- **WHEN** Vercel 환경에서 DATABASE_URL(Neon Pooled) 자동 주입 시
- **THEN** 앱이 코드 변경 없이 Neon PostgreSQL에 연결

---

### Requirement: DB 스키마 자동 마이그레이션
시스템은 앱 시작 시 DB 테이블을 자동으로 생성/확인해야 한다.

#### Scenario: 최초 실행
- **WHEN** 빈 DB에서 앱 시작 시
- **THEN** users, teams, team_members, tasks, messages 5개 테이블 자동 생성

#### Scenario: 이미 테이블 존재
- **WHEN** 기존 데이터가 있는 DB에서 앱 재시작 시
- **THEN** 기존 데이터 보존, 테이블 재생성 없음
