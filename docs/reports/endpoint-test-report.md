# TaskFlow API 엔드포인트 테스트 보고서

**테스트 일시**: 2026-05-19  
**환경**: 로컬 (Windows 10, Python 3.14, SQLite, uvicorn 0.0.0.0:8001)  
**테스트 방법**: 엔드포인트별 10회 반복 호출 (PowerShell Invoke-RestMethod, Stopwatch 측정)  
**총 결과**: 18/18 엔드포인트 PASS · 180/180 호출 성공

---

## 1. 결과 요약

| # | 엔드포인트 | 결과 | 성공 | 평균(ms) | 최소(ms) | 최대(ms) |
|---|-----------|------|------|----------|----------|----------|
| 1 | POST /auth/signup | ✅ PASS | 10/10 | 573.5 | 346.6 | 2459.5 |
| 2 | POST /auth/login | ✅ PASS | 10/10 | 208.8 | 203.9 | 216.0 |
| 3 | GET /auth/me | ✅ PASS | 10/10 | 6.1 | 2.6 | 9.1 |
| 4 | POST /auth/logout | ✅ PASS | 10/10 | 4.2 | 1.6 | 12.8 |
| 5 | POST /teams | ✅ PASS | 10/10 | 541.4 | 489.5 | 597.0 |
| 6 | GET /teams/{id} | ✅ PASS | 10/10 | 5.8 | 3.4 | 11.9 |
| 7 | POST /teams/join | ✅ PASS | 10/10 | 541.4 | 495.9 | 565.5 |
| 8 | GET /teams/{id}/members | ✅ PASS | 10/10 | 5.1 | 3.8 | 10.4 |
| 9 | DELETE /teams/{id}/leave | ✅ PASS | 10/10 | 195.8 | 143.9 | 267.4 |
| 10 | POST /teams/{id}/tasks | ✅ PASS | 10/10 | 195.2 | 153.5 | 302.6 |
| 11 | GET /teams/{id}/tasks | ✅ PASS | 10/10 | 6.1 | 4.0 | 8.1 |
| 12 | GET /tasks/{id} | ✅ PASS | 10/10 | 6.3 | 3.7 | 7.7 |
| 13 | PATCH /tasks/{id}/status | ✅ PASS | 10/10 | 163.0 | 138.6 | 228.9 |
| 14 | PUT /tasks/{id} | ✅ PASS | 10/10 | 209.4 | 157.8 | 299.2 |
| 15 | DELETE /tasks/{id} | ✅ PASS | 10/10 | 181.2 | 140.3 | 269.4 |
| 16 | POST /teams/{id}/messages | ✅ PASS | 10/10 | 171.3 | 146.8 | 214.9 |
| 17 | GET /teams/{id}/messages | ✅ PASS | 10/10 | 5.1 | 4.0 | 7.7 |
| 18 | DELETE /messages/{id} | ✅ PASS | 10/10 | 200.5 | 152.7 | 257.3 |

---

## 2. 응답 속도 분석

### 2-1. 분류별 평균

| 분류 | 해당 엔드포인트 | 평균 응답시간 |
|------|----------------|--------------|
| **GET (조회)** | /auth/me, /teams/{id}, /teams/{id}/members, /teams/{id}/tasks, /tasks/{id}, /teams/{id}/messages | **5 ~ 7ms** |
| **일반 쓰기** | DELETE /leave, POST /tasks, PATCH /status, PUT /tasks, DELETE /tasks, POST /messages, DELETE /messages | **163 ~ 210ms** |
| **bcrypt 연산** | POST /signup, POST /login, POST /teams, POST /teams/join | **209 ~ 574ms** |
| **무상태 응답** | POST /auth/logout | **4ms** |

### 2-2. SRS 목표 대비

| 목표 | 기준 | 결과 | 판정 |
|------|------|------|------|
| API 응답 100ms 이내 | GET 조회 | 5~7ms | ✅ 달성 |
| API 응답 100ms 이내 | 일반 쓰기 (DB commit) | 163~210ms | ⚠️ 로컬 SQLite 특성 (Neon PostgreSQL 배포 후 재측정 필요) |
| bcrypt 응답 | 회원가입·로그인 | 210~574ms | ℹ️ bcrypt cost=12 의도적 지연 (보안 요구사항 충족) |
| 칸반 드래그 50ms 반응 | PATCH /tasks/{id}/status | 163ms 평균 | ⚠️ 네트워크 레이턴시 감안 시 브라우저→서버 왕복 포함 재측정 필요 |

> **비고**: 로컬 SQLite는 파일 I/O 락 오버헤드가 있어 PostgreSQL(Neon) 배포 환경과 응답시간이 다를 수 있음.  
> bcrypt는 보안상 의도적으로 느리게 설계된 알고리즘이며, `cost=12` (기본값) 기준 약 200~500ms 소요는 정상 동작.

---

## 3. 오류 처리 검증

아래 케이스를 별도 확인하여 정상 동작을 검증함:

| 시나리오 | 기대 상태코드 | 결과 |
|---------|-------------|------|
| 중복 이메일 회원가입 | 409 ALREADY_EXISTS | ✅ |
| 잘못된 비밀번호 로그인 | 401 INVALID_CREDENTIALS | ✅ |
| 비밀번호 정책 미충족 (대문자 없음) | 422 INVALID_PASSWORD | ✅ |
| 비밀번호 정책 미충족 (소문자 없음) | 422 INVALID_PASSWORD | ✅ |
| 비밀번호 정책 미충족 (특수문자 없음) | 422 INVALID_PASSWORD | ✅ |
| 이미 팀 소속인 사용자 팀 생성 | 409 ALREADY_IN_TEAM | ✅ |
| owner가 팀 탈퇴 시도 | 403 OWNER_CANNOT_LEAVE | ✅ |
| 유효하지 않은 JWT | 401 UNAUTHORIZED | ✅ |

---

## 4. 수정 이력

| 일시 | 내용 |
|------|------|
| 2026-05-19 | `passlib[bcrypt]==1.7.4` → `bcrypt>=4.0.0` 직접 사용으로 교체. Python 3.14에서 `bcrypt 4.x+`가 `__about__` 속성을 제거하여 passlib이 bcrypt 백엔드 초기화 실패, 모든 인증 엔드포인트 500 에러 발생. |
| 2026-05-19 | `psycopg2-binary` 를 `requirements-prod.txt`로 분리. Python 3.14 로컬 환경에서 pg_config 미설치로 빌드 실패. |

---

## 5. 환경 정보

```
Python     : 3.14
FastAPI    : 0.115.x
uvicorn    : 0.30.x
SQLAlchemy : 2.0.x
bcrypt     : 5.0.0
python-jose: 3.3.0
pydantic   : 2.13.x
DB (로컬)  : SQLite 3 (taskflow.db)
OS         : Windows 10 Pro 10.0.19045
```
