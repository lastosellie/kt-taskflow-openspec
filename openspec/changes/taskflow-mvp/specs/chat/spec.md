## ADDED Requirements

### Requirement: 메시지 전송
시스템은 팀 소속 멤버가 텍스트 메시지를 전송할 수 있어야 한다. 메시지는 최대 1000자이며, 발신자 ID와 ISO 8601 타임스탬프가 기록된다.

#### Scenario: 정상 전송
- **WHEN** `POST /teams/{id}/messages` { content } 요청 시 (인증됨, 해당 팀 소속)
- **THEN** 201, { id, team_id, user_id, content, created_at (ISO 8601) } 반환

#### Scenario: 1000자 초과
- **WHEN** content가 1000자를 초과하는 요청 시
- **THEN** 422, { code: "MESSAGE_TOO_LONG" } 반환

#### Scenario: 빈 메시지
- **WHEN** content가 빈 문자열이거나 없는 요청 시
- **THEN** 422 반환

---

### Requirement: 메시지 목록 조회 (폴링)
시스템은 특정 시각 이후의 메시지를 반환해야 한다. since 파라미터(ISO 8601)가 없으면 최근 50개를 반환한다. 클라이언트는 5초마다 폴링한다.

#### Scenario: since 파라미터로 신규 메시지 조회
- **WHEN** `GET /teams/{id}/messages?since=2024-01-01T00:00:00Z` 요청 시 (인증됨, 해당 팀 소속)
- **THEN** 200, 해당 시각 이후 메시지 배열 반환 (발신자 email 포함)

#### Scenario: since 없이 초기 로드
- **WHEN** `GET /teams/{id}/messages` (since 파라미터 없음) 요청 시
- **THEN** 200, 최근 50개 메시지 반환 (오래된 순)

#### Scenario: 신규 메시지 없음
- **WHEN** since 이후 새 메시지 없을 때 요청 시
- **THEN** 200, [] 반환

---

### Requirement: 메시지 삭제
시스템은 메시지 발신자 본인만 메시지를 삭제할 수 있어야 한다.

#### Scenario: 정상 삭제 (본인)
- **WHEN** `DELETE /messages/{id}` 요청 시 (인증됨, 메시지 발신자 본인)
- **THEN** 200, { message: "삭제되었습니다" } 반환

#### Scenario: 타인의 메시지 삭제 시도
- **WHEN** 본인이 아닌 메시지 삭제 요청 시
- **THEN** 403, { code: "FORBIDDEN" } 반환
