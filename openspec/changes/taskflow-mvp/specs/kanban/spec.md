## ADDED Requirements

### Requirement: 태스크 생성
시스템은 팀 소속 멤버가 팀에 새 태스크를 추가할 수 있어야 한다. 생성 시 기본 status는 TODO이다.

#### Scenario: 정상 생성
- **WHEN** `POST /teams/{id}/tasks` { title } 요청 시 (인증됨, 해당 팀 소속)
- **THEN** 201, { id, team_id, title, status: "TODO", creator_id } 반환

#### Scenario: 제목 미입력
- **WHEN** title 필드 없이 요청 시
- **THEN** 422 반환

#### Scenario: 팀 비소속자 접근
- **WHEN** 해당 팀에 속하지 않은 사용자가 요청 시
- **THEN** 403, { code: "FORBIDDEN" } 반환

---

### Requirement: 팀 태스크 목록 조회
시스템은 특정 팀의 전체 태스크를 반환해야 한다. 칸반 3컬럼(TODO/DOING/DONE)으로 클라이언트에서 분류한다.

#### Scenario: 정상 조회
- **WHEN** `GET /teams/{id}/tasks` 요청 시 (인증됨, 해당 팀 소속)
- **THEN** 200, [{ id, team_id, title, status, creator_id }] 반환 (전체)

---

### Requirement: 태스크 단건 조회
시스템은 특정 태스크의 상세 정보를 반환해야 한다.

#### Scenario: 정상 조회
- **WHEN** `GET /tasks/{id}` 요청 시 (인증됨, 해당 태스크의 팀 소속)
- **THEN** 200, { id, team_id, title, status, creator_id } 반환

#### Scenario: 존재하지 않는 태스크
- **WHEN** 없는 태스크 ID로 요청 시
- **THEN** 404, { code: "TASK_NOT_FOUND" } 반환

---

### Requirement: 태스크 수정 (status + title 통합)
시스템은 태스크의 status 또는 title을 선택적으로 수정할 수 있어야 한다. status는 TODO/DOING/DONE 중 하나여야 한다.

#### Scenario: status 변경
- **WHEN** `PATCH /tasks/{id}` { status: "DOING" } 요청 시 (인증됨, 해당 팀 소속)
- **THEN** 200, 수정된 태스크 전체 반환

#### Scenario: title 변경
- **WHEN** `PATCH /tasks/{id}` { title: "새 제목" } 요청 시
- **THEN** 200, 수정된 태스크 전체 반환

#### Scenario: 유효하지 않은 status 값
- **WHEN** status에 TODO/DOING/DONE 외의 값 요청 시
- **THEN** 422 반환

---

### Requirement: 태스크 삭제
시스템은 팀 소속 멤버가 태스크를 삭제할 수 있어야 한다.

#### Scenario: 정상 삭제
- **WHEN** `DELETE /tasks/{id}` 요청 시 (인증됨, 해당 팀 소속)
- **THEN** 200, { message: "삭제되었습니다" } 반환

#### Scenario: 존재하지 않는 태스크
- **WHEN** 없는 태스크 ID로 요청 시
- **THEN** 404, { code: "TASK_NOT_FOUND" } 반환
