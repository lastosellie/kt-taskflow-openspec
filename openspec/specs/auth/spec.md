# auth Specification

## Purpose
TBD - created by archiving change taskflow-mvp. Update Purpose after archive.
## Requirements
### Requirement: 회원가입
시스템은 이메일과 비밀번호로 신규 사용자를 등록해야 한다(MUST). 비밀번호는 bcrypt로 해시 저장하고, 성공 시 JWT를 반환해야 한다. 비밀번호는 8자 이상, 대문자·소문자·특수문자를 모두 포함해야 한다.

#### Scenario: 정상 회원가입
- **WHEN** `POST /auth/signup` { email, password } 요청 시
- **THEN** 201, { token: JWT, user: { id, email } } 반환

#### Scenario: 중복 이메일
- **WHEN** 이미 존재하는 이메일로 가입 시도 시
- **THEN** 409, { code: "EMAIL_EXISTS", message: "이미 사용 중인 이메일입니다" } 반환

#### Scenario: 비밀번호 정책 위반
- **WHEN** password가 아래 규칙을 하나라도 만족하지 않을 시
  - 8자 이상
  - 대문자(A-Z) 1자 이상
  - 소문자(a-z) 1자 이상
  - 특수문자(!@#$%^&* 등) 1자 이상
- **THEN** 422, { code: "INVALID_PASSWORD", message: "비밀번호는 8자 이상, 대문자·소문자·특수문자를 포함해야 합니다" } 반환

#### Scenario: 비밀번호 미입력
- **WHEN** password 필드 없이 요청 시
- **THEN** 422 반환

---

### Requirement: 로그인
시스템은 이메일과 비밀번호로 사용자를 인증하고 JWT를 발급해야 한다(MUST). JWT 유효기간은 24시간이며 갱신(refresh) 없다.

#### Scenario: 정상 로그인
- **WHEN** `POST /auth/login` { email, password } 요청 시 (자격증명 일치)
- **THEN** 200, { token: JWT, user: { id, email } } 반환

#### Scenario: 잘못된 자격증명
- **WHEN** 존재하지 않는 이메일 또는 틀린 비밀번호 요청 시
- **THEN** 401, { code: "INVALID_CREDENTIALS", message: "이메일 또는 비밀번호가 올바르지 않습니다" } 반환

---

### Requirement: 내 정보 조회
시스템은 유효한 JWT를 가진 사용자의 정보를 반환해야 한다(MUST).

#### Scenario: 정상 조회
- **WHEN** `GET /auth/me` Authorization: Bearer {token} 요청 시
- **THEN** 200, { id, email, created_at } 반환

#### Scenario: 토큰 없음 또는 만료
- **WHEN** 토큰 없이 또는 만료된 토큰으로 요청 시
- **THEN** 401, { code: "UNAUTHORIZED" } 반환

---

### Requirement: 로그아웃
시스템은 로그아웃 엔드포인트를 제공해야 한다(MUST). 서버는 무상태이므로 클라이언트의 localStorage 토큰 삭제를 안내한다.

#### Scenario: 로그아웃 요청
- **WHEN** `POST /auth/logout` Authorization: Bearer {token} 요청 시
- **THEN** 200, { message: "로그아웃되었습니다" } 반환 (서버 상태 변경 없음)

