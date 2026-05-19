# team-management Specification

## Purpose
TBD - created by archiving change taskflow-mvp. Update Purpose after archive.
## Requirements
### Requirement: 팀 생성
시스템은 로그인한 사용자가 팀을 생성할 수 있어야 한다(MUST). 팀 생성 시 ABCD-1234 형식의 초대코드를 자동 발급하며, 생성자는 owner로 등록되고 users.team_id가 신규 팀 ID로 업데이트된다.

#### Scenario: 정상 팀 생성
- **WHEN** `POST /teams` { name } 요청 시 (인증됨, 현재 팀 없음)
- **THEN** 201, { id, name, invite_code, owner_id } 반환, users.team_id = 신규 팀 ID로 업데이트

#### Scenario: 이미 다른 팀 소속
- **WHEN** 이미 team_id가 설정된 사용자가 요청 시
- **THEN** 409, { code: "ALREADY_IN_TEAM", message: "이미 다른 팀에 소속되어 있습니다. 먼저 팀을 떠나세요." } 반환

#### Scenario: 팀 이름 미입력
- **WHEN** name 필드 없이 요청 시
- **THEN** 422 반환

---

### Requirement: 팀 정보 조회
시스템은 특정 팀의 정보를 반환해야 한다(MUST). 요청자는 해당 팀의 멤버여야 한다.

#### Scenario: 정상 조회
- **WHEN** `GET /teams/{id}` 요청 시 (인증됨, 해당 팀 소속)
- **THEN** 200, { id, name, invite_code, owner_id } 반환

#### Scenario: 팀 비소속자 접근
- **WHEN** 해당 팀에 속하지 않은 사용자가 요청 시
- **THEN** 403, { code: "FORBIDDEN" } 반환

---

### Requirement: 초대코드로 팀 합류
시스템은 유효한 초대코드로 사용자가 팀에 합류할 수 있어야 한다(MUST). 합류 시 users.team_id를 해당 팀 ID로 업데이트한다. 1인 1팀 제약으로, 이미 다른 팀에 소속된 경우 409를 반환한다.

#### Scenario: 정상 합류
- **WHEN** `POST /teams/join` { invite_code: "ABCD-1234" } 요청 시 (인증됨, 유효한 코드, 현재 팀 없음)
- **THEN** 200, { id, name, invite_code, owner_id } 반환, users.team_id = 해당 팀 ID로 업데이트

#### Scenario: 이미 다른 팀 소속
- **WHEN** users.team_id가 이미 설정된 사용자가 합류 요청 시
- **THEN** 409, { code: "ALREADY_IN_TEAM", message: "이미 다른 팀에 소속되어 있습니다. 먼저 팀을 떠나세요." } 반환

#### Scenario: 이미 해당 팀 소속
- **WHEN** users.team_id가 이미 해당 팀인 사용자가 요청 시
- **THEN** 200, 해당 팀 정보 반환 (중복 처리 없음)

#### Scenario: 유효하지 않은 초대코드
- **WHEN** 존재하지 않는 invite_code로 요청 시
- **THEN** 404, { code: "TEAM_NOT_FOUND", message: "유효하지 않은 초대코드입니다" } 반환

---

### Requirement: 팀 멤버 목록 조회
시스템은 특정 팀의 모든 멤버 목록을 반환해야 한다(MUST). users.team_id 기준으로 조회한다. 요청자는 해당 팀의 멤버여야 한다.

#### Scenario: 정상 조회
- **WHEN** `GET /teams/{id}/members` 요청 시 (인증됨, 해당 팀 소속)
- **THEN** 200, [{ id, email, created_at }] 반환

#### Scenario: 팀 비소속자 접근
- **WHEN** 해당 팀에 속하지 않은 사용자가 요청 시
- **THEN** 403, { code: "FORBIDDEN" } 반환

---

### Requirement: 팀 떠나기
시스템은 팀 소속 멤버가 팀을 떠날 수 있어야 한다(MUST). 떠나기 시 users.team_id를 NULL로 업데이트한다. owner는 팀을 떠날 수 없다.

#### Scenario: 정상 팀 떠나기 (일반 멤버)
- **WHEN** `DELETE /teams/{id}/leave` 요청 시 (인증됨, 해당 팀 소속, owner 아님)
- **THEN** 200, { message: "팀을 떠났습니다" } 반환, users.team_id = NULL로 업데이트

#### Scenario: owner가 팀 떠나기 시도
- **WHEN** teams.owner_id와 동일한 사용자가 요청 시
- **THEN** 403, { code: "OWNER_CANNOT_LEAVE", message: "팀 owner는 팀을 떠날 수 없습니다" } 반환

#### Scenario: 팀 비소속자 요청
- **WHEN** 해당 팀에 속하지 않은 사용자가 요청 시
- **THEN** 403, { code: "FORBIDDEN" } 반환

