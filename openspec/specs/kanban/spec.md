# kanban Specification

## Purpose
TBD - created by archiving change taskflow-mvp. Update Purpose after archive.
## Requirements
### Requirement: 태스크 생성
시스템은 팀 소속 멤버가 팀에 새 태스크를 추가할 수 있어야 한다(MUST). 생성 시 기본 status는 TODO이며, assignee_id는 선택 입력이다.

#### Scenario: 정상 생성
- **WHEN** `POST /teams/{id}/tasks` { title, assignee_id? } 요청 시 (인증됨, 해당 팀 소속)
- **THEN** 201, { id, team_id, title, status: "TODO", creator_id, assignee_id, created_at } 반환

#### Scenario: 제목 미입력
- **WHEN** title 필드 없이 요청 시
- **THEN** 422 반환

#### Scenario: 팀 비소속자 접근
- **WHEN** 해당 팀에 속하지 않은 사용자가 요청 시
- **THEN** 403, { code: "FORBIDDEN" } 반환

---

### Requirement: 팀 태스크 목록 조회
시스템은 특정 팀의 전체 태스크를 반환해야 한다(MUST). 칸반 3컬럼(TODO/DOING/DONE)으로 클라이언트에서 분류한다. `filter` 쿼리 파라미터로 @me(내 담당) 또는 unassigned(미할당) 필터링을 지원한다.

#### Scenario: 전체 조회
- **WHEN** `GET /teams/{id}/tasks` 요청 시 (인증됨, 해당 팀 소속)
- **THEN** 200, [{ id, team_id, title, status, creator_id, assignee_id, created_at }] 반환 (전체)

#### Scenario: @me 필터 조회
- **WHEN** `GET /teams/{id}/tasks?filter=@me` 요청 시
- **THEN** 200, assignee_id = current_user_id인 태스크만 반환

#### Scenario: unassigned 필터 조회
- **WHEN** `GET /teams/{id}/tasks?filter=unassigned` 요청 시
- **THEN** 200, assignee_id = NULL인 태스크만 반환

---

### Requirement: 태스크 단건 조회
시스템은 특정 태스크의 상세 정보를 반환해야 한다(MUST).

#### Scenario: 정상 조회
- **WHEN** `GET /tasks/{id}` 요청 시 (인증됨, 해당 태스크의 팀 소속)
- **THEN** 200, { id, team_id, title, status, creator_id, assignee_id, created_at } 반환

#### Scenario: 존재하지 않는 태스크
- **WHEN** 없는 태스크 ID로 요청 시
- **THEN** 404, { code: "TASK_NOT_FOUND" } 반환

---

### Requirement: 태스크 상태 변경 (드래그 앤 드롭)
시스템은 태스크의 status만 경량으로 변경할 수 있어야 한다(MUST). 칸반 드래그 앤 드롭 시 호출되는 전용 엔드포인트다.

#### Scenario: status 변경 성공
- **WHEN** `PATCH /tasks/{id}/status` { status: "DOING" } 요청 시 (인증됨, 해당 팀 소속)
- **THEN** 200, { id, team_id, title, status, creator_id, assignee_id, created_at } 반환

#### Scenario: 유효하지 않은 status 값
- **WHEN** status에 TODO/DOING/DONE 외의 값 요청 시
- **THEN** 422 반환

---

### Requirement: 태스크 상세 수정 (카드 모달)
시스템은 태스크의 title과 assignee_id를 수정할 수 있어야 한다(MUST). 카드 상세 모달에서 호출되는 전용 엔드포인트다.

#### Scenario: title 변경
- **WHEN** `PUT /tasks/{id}` { title: "새 제목" } 요청 시 (인증됨, 해당 팀 소속)
- **THEN** 200, { id, team_id, title, status, creator_id, assignee_id, created_at } 반환

#### Scenario: assignee_id 변경
- **WHEN** `PUT /tasks/{id}` { assignee_id: 2 } 요청 시 (인증됨, 해당 팀 소속)
- **THEN** 200, 수정된 태스크 전체 반환

#### Scenario: assignee_id 미할당 처리
- **WHEN** `PUT /tasks/{id}` { assignee_id: null } 요청 시
- **THEN** 200, assignee_id = null인 태스크 반환

---

### Requirement: 태스크 삭제
시스템은 팀 소속 멤버가 태스크를 삭제할 수 있어야 한다(MUST). owner는 모든 태스크를 삭제할 수 있고, 일반 멤버는 본인이 생성한 태스크만 삭제할 수 있다.

#### Scenario: owner가 임의 태스크 삭제
- **WHEN** `DELETE /tasks/{id}` 요청 시 (인증됨, 팀 owner)
- **THEN** 200, { message: "삭제되었습니다" } 반환

#### Scenario: 본인 태스크 삭제 (일반 멤버)
- **WHEN** `DELETE /tasks/{id}` 요청 시 (인증됨, creator_id = current_user_id)
- **THEN** 200, { message: "삭제되었습니다" } 반환

#### Scenario: 타인 태스크 삭제 시도 (일반 멤버)
- **WHEN** creator_id ≠ current_user_id이고 owner가 아닌 사용자가 요청 시
- **THEN** 403, { code: "FORBIDDEN", message: "본인이 생성한 태스크만 삭제할 수 있습니다" } 반환

#### Scenario: 존재하지 않는 태스크
- **WHEN** 없는 태스크 ID로 요청 시
- **THEN** 404, { code: "TASK_NOT_FOUND" } 반환

