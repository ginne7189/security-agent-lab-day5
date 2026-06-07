# Day 5 — Integrated Security PoC · 최종 리뷰

> ⚠️ **이 가이드는 전체 모노레포(security-agent-lab) 기준 CLI 실습 설명입니다.**
> 단독 Day 저장소에서는 README의 `streamlit run app.py`(버튼 클릭 실습)만 쓰면 됩니다.
> `check_env.py`·`scripts/`·`orchestrator/`·`mcp_servers/` 는 모노레포에만 있습니다(이 저장소에는 없음).
> `agents/`·`course/mini_labs/`·`policies/`·`sample_app/` 명령은 이 저장소에서도 그대로 동작합니다.


## 오늘의 목표
- Day 1~4 의 정책 · 도구(MCP) · 역할 분리(HITL) · 위험도 점수화를 하나로 통합한다.
- 통합 PoC 결과를 우리 부서 도입 계획(Adoption Canvas)으로 정리한다.

> Day 5 는 새 Mini Lab 대신 **Department Adoption Canvas** 로 마무리합니다.

---

## Department Adoption Canvas (Mini Lab 대체)
- **목적**: 통합 PoC 이후 현업 적용 방안을 한 장으로 정리
- **실행 명령**
  ```bash
  cp course/department_adoption_canvas.md reports/adoption_canvas_<our_team>.md
  ```
- **산출물**: `reports/adoption_canvas_<our_team>.md`
- **확인 포인트**: 정책 위치 / MCP 래핑 / HITL 기준 / Audit 저장 / 승인자 / 첫 적용 업무 / 확장 리스크 7칸을 채웠는가?
- 자세히: `course/experiments/day05_adoption_canvas.md`

---

## Main Lab — 통합 Security PoC
- **목적**: 전체 파이프라인(SAST→Secret→Dependency→Threat→Report)을 HITL·위협정보와 함께 통합 실행
- **실행 명령**
  ```bash
  python orchestrator/supervisor_graph.py --target sample_app/ --hitl --threat-intel --report final
  python scripts/run_light_review_loop.py   # LLM 없이 산출물 품질 게이트 확인
  ```
- **산출물**: `reports/final_report.md`, `reports/light_review_result.json`, `memory/audit_log.jsonl`
- **확인 포인트**: final_report 에 모든 Agent 결과와 위험도 점수가 통합됐는가? 비밀값 원문 누출이 0건인가(light review)?

---

## 선택 보조: Claude/GPT 저토큰 활용
- 전체 코드베이스를 넣지 않는다.
- `python scripts/make_light_context_pack.py --day 5` 로 `reports/context_pack_day5.md` 만 생성해 복사한다.
- "이 final_report.md 에서 경영진 보고용으로 빠진 요약 3줄만 제안해줘" 정도로 가볍게 사용한다.

---

## 완료 체크리스트
- [ ] `reports/final_report.md` 생성
- [ ] `reports/light_review_result.json` verdict=PASS · leaks=0 확인
- [ ] Adoption Canvas 7칸 작성
- [ ] Day 1~5 흐름(정책→도구→역할분리→위험도→통합·도입) 정리
