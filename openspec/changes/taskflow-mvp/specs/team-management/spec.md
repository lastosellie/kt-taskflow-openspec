## ADDED Requirements

### Requirement: 팀 생성
시스템은 로그인한 사용자가 팀을 생성할 수 있어야 한다. 팀 생성 시 ABCD-1234 형식의 초대코드를 자동 발급하며, 생성자는 owner이자 team_members에 자동 등록된다.

#### Scenario: 정상 팀 생성
- **WHEN** `POST /teams` { name } 요청 시 (인증됨)
- **THEN** 201, { id, name, invite_code, owner_id } 반환, team_members에 owner 자동 등록

#### Scenario: 팀 이름 미입력
- **WHEN** name 필드 없이 요청 시
- **THEN** 422 반환

---

### Requirement: 내 팀 목록 조회
시스템은 로그인한 사용자가 소속된 모든 팀 목록을 반환해야 한다. team_members 테이블 기준으로 조회한다.

#### Scenario: 소속 팀 있음
- **WHEN** `GET /teams` 요청 시 (인증됨)
- **THEN** 200, [{ id, name, invite_code, owner_id }] 반환 (소속 팀 전체)

#### Scenario: 소속 팀 없음
- **WHEN** 아직 어떤 팀에도 속하지 않은 사용자 요청 시
- **THEN** 200, [] 반환

---

### Requirement: 초대코드로 팀 합류
시스템은 유효한 초대코드로 사용자가 팀에 합류할 수 있어야 한다. 합류 시 team_members에 기록한다.

#### Scenario: 정상 합류
- **WHEN** `POST /teams/join` { invite_code: "ABCD-1234" } 요청 시 (인증됨, 유효한 코드)
- **THEN** 200, { id, name, invite_code, owner_id } 반환, team_members 신규 레코드 생성

#### Scenario: 이미 소속된 팀
- **WHEN** 이미 합류한 팀의 초대코드로 재요청 시
- **THEN** 200, 해당 팀 정보 반환 (중복 등록 없음)

#### Scenario: 유효하지 않은 초대코드
- **WHEN** 존재하지 않는 invite_code로 요청 시
- **THEN** 404, { code: "TEAM_NOT_FOUND", message: "유효하지 않은 초대코드입니다" } 반환

---

### Requirement: 팀 멤버 목록 조회
시스템은 특정 팀의 모든 멤버 목록을 반환해야 한다. 요청자는 해당 팀의 멤버여야 한다.

#### Scenario: 정상 조회
- **WHEN** `GET /teams/{id}/members` 요청 시 (인증됨, 해당 팀 소속)
- **THEN** 200, [{ id, email, joined_at }] 반환

#### Scenario: 팀 비소속자 접근
- **WHEN** 해당 팀에 속하지 않은 사용자가 요청 시
- **THEN** 403, { code: "FORBIDDEN" } 반환
