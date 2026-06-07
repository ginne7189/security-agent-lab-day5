# Day 5 과제 — 통합 PoC (Quality Gate · Review Loop · Operationalization)
> PPT 개념: Quality Gate · Review Loop · Operationalization

## 🎬 시나리오
PoC를 현업에 올린다.
**명세 → 생성 → 테스트 → 문서 → 품질 게이트** 를 한 흐름(plan-run-sync)으로 끝내라.

## 🏗 생성형 과제 — plan-run-sync 미니 파이프라인 (20~30분)
1. **plan→run**: 새 에이전트 보일러플레이트 생성
   ```bash
   python scripts/new_agent.py myteam --cwe CWE-200 --title "정보 노출" --pattern "(?i)debug|traceback"
   ```
2. **test**: `python -m pytest tests/test_myteam_agent.py`
3. **sync(문서)**: README/문서에 새 에이전트 한 줄 추가.
4. **품질 게이트**: `python scripts/run_light_review_loop.py` → `verdict=PASS`(비밀 누출 0) 확인.

## 🟢 기본 과제 (Operationalization)
1. `course/department_adoption_canvas.md` 를 **우리 팀 버전**으로 직접 작성
   (정책 위치 / MCP 래핑 / HITL 기준 / Audit 저장 / 승인자 / 첫 적용 업무 / 확장 리스크).
2. `policies/CLAUDE.md` 에 사내 규칙 1줄 추가 → 전체 점검 결과가 어떻게 바뀌는지 확인.

## 🔥 도전 과제
`orchestrator/supervisor_graph.py` 의 `review()` 에 **새 BLOCK 조건** 1개 추가
(예: 'Critical 발견인데 근거(evidence) 비어 있으면 BLOCK').

## ✅ 완료 체크
- [ ] 새 에이전트 생성 → 테스트 → 문서 반영(plan-run-sync)
- [ ] 품질 게이트 PASS(누출 0)
- [ ] 적용 캔버스 작성
