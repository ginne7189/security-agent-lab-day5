"""대시보드 공용 렌더 모듈 — 키 없이 동작 · 외부 API 호출 없음."""
import importlib.util
import json
import os
import random
import sys

import streamlit as st

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
os.chdir(ROOT)


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod



from agents import sast_agent, secret_agent, dependency_agent, llm_client  # noqa: E402

def render_overview():
    st.subheader("👋 이 대시보드는 '데모 실행기'예요")
    st.markdown(
        "AI 에이전트로 **코드·보안 취약점 점검을 자동화**하는 5일 실습을, "
        "터미널 없이 **버튼 클릭**으로 직접 돌려봅니다."
    )

    st.markdown("#### 🧭 사용법 — 딱 3단계")
    s1, s2, s3 = st.columns(3)
    s1.info("**① 위 탭 선택**\n\n🤔 왜 만드나 · Day 1~5 중 하나 클릭")
    s2.info("**② 버튼 누르기**\n\n각 탭의 파란 버튼(🔍 🧰 🐞 🚀 …)을 클릭")
    s3.info("**③ 결과 확인**\n\n표·차트·메시지가 화면에 바로 나타남")

    st.markdown("#### ✨ '뭐가 바뀌는지' 눈으로 보이는 곳 (먼저 가보세요)")
    st.markdown(
        "- **🤔 왜 만드나?** 탭 → 버튼 여러 번 클릭 → *왼쪽(그냥 LLM)은 숫자가 흔들리고 비밀이 새고, "
        "오른쪽(에이전트)은 항상 똑같고 안전* 한 게 **나란히** 보여요.\n"
        "- **Day 1** 탭 → 정책 **체크박스를 껐다 켜면** 결과 리포트가 **즉시** 바뀝니다.\n"
        "- **Day 1** 탭 → SAST 정책을 `CLAUDE_base` ↔ `CLAUDE` 로 바꾸면 차량모듈이 **High → Critical** 로 올라가요."
    )
    st.success("👆 위 두 곳이 '에이전트가 무엇을, 어떻게 바꾸는지' 가장 빨리 체감되는 지점이에요.")

    st.markdown("#### 🤖 어떤 에이전트가 'AI(LLM)를 부르나'?")
    key_on = bool(os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY"))
    st.dataframe([
        {"구성요소": "SAST · Secret · Dependency · Threat · Report", "종류": "⚙️ 규칙(결정론)", "AI 호출": "❌ (키 없이 항상 동작)"},
        {"구성요소": "llm_client · run_llm_interpret", "종류": "🧠 AI 해석(선택)", "AI 호출": "✅ 키 있을 때만 (없으면 규칙 fallback)"},
    ], width="stretch", hide_index=True)
    if key_on:
        st.info("🧠 현재 **AI 키 감지됨** → 해석 레이어가 LLM을 부릅니다.")
    else:
        st.warning("⚙️ 현재 **AI 키 없음** → 5개 에이전트는 전부 **규칙(LLM 없이)** 으로 동작합니다. "
                   "그래도 모든 실습이 끝까지 돌아가요. (키를 넣으면 🧠 해석만 추가됨)")
    st.caption("흐름: ⚙️ 규칙 에이전트가 '발견' → (선택) 🧠 AI가 그 발견을 자연어로 '해석'.")

    with st.expander("📐 전체 구조 그림 보기"):
        arch = os.path.join(ROOT, "docs/diagrams/01_architecture.png")
        if os.path.exists(arch):
            st.image(arch, caption="전체 아키텍처", width="stretch")


def render_why():
    st.subheader("🤔 왜 'LLM 그냥 쓰기'가 아니라 '에이전트를 만드나'?")
    st.markdown(
        "**LLM = 엄청 똑똑한 신입사원** 🧑‍💻\n\n"
        "그냥 \"보안 점검해줘\" 하고 맡기는 것 vs **매뉴얼·검수·결재선·기록을 붙인 것**.\n\n"
        "아래 버튼으로 **같은 일을 두 방식으로** 시켜보세요 👇 (여러 번 눌러보세요!)"
    )
    if st.button("🎬 같은 일, 두 방식으로 시켜보기!", key="why_btn"):
        full = sast_agent.run("sample_app/", "policies/CLAUDE.md")
        raw_secret = next(
            (l.strip() for l in open("sample_app/vulnerability.py", encoding="utf-8")
             if "API_TOKEN" in l and '"' in l and not l.strip().startswith("#")),
            'API_TOKEN = "..."')
        left, right = st.columns(2)
        with left:
            st.markdown("### 😱 그냥 LLM한테 시킴")
            wobble = random.randint(max(1, len(full) - 4), len(full))
            st.error(f"이번엔 **{wobble}건** 찾았대요 🎲 (또 누르면 숫자 바뀜)")
            st.markdown("**비밀값도 그대로 뱉음:**")
            st.code(raw_secret, language="python")
            st.markdown("📋 감사 기록 **없음**  ·  🤥 틀려도 **그냥 통과**")
            st.caption("→ 매번 답이 달라서 못 믿어요.")
        with right:
            st.markdown("### 😎 울타리 친 에이전트 (이 repo)")
            st.success(f"항상 **{len(full)}건** ✅ (몇 번 눌러도 똑같음)")
            st.markdown("**비밀값은 자동 마스킹:**")
            masked = next((r["evidence"] for r in full if "CWE-798" in r["cwe"]), 'API_TOKEN = "****"')
            st.code(masked, language="python")
            st.markdown("📋 감사 로그 1줄 자동 생성:")
            st.code('{"agent":"sast","action":"scan","outcome":"9 findings"}', language="json")
            st.caption("→ 정책·마스킹·검증·감사가 보장돼요.")
        st.info("**핵심**: 실무 AI는 LLM을 '쓰는' 게 아니라 **'울타리로 가둬 믿게 만드는'** 일! "
                "그 울타리를 만드는 게 = **에이전트 엔지니어링** (이 과정의 진짜 주제) 🎯")
    st.markdown("---")
    st.markdown(
        "| | 😱 그냥 LLM | 😎 에이전트 |\n|---|---|---|\n"
        "| 결과 | 매번 다름 🎲 | 항상 같음 ✅ |\n"
        "| 비밀값 | 줄줄 샘 🔓 | 마스킹 🔒 |\n"
        "| 틀리면 | 그냥 통과 | 재시도/차단 🛡️ |\n"
        "| 위험 행동 | 막 실행 | 사람 승인 ✋ |\n"
        "| 기록 | 없음 | 감사 로그 📋 |"
    )


def render_day5():
    st.subheader("Day 5 · 통합 — 전체 에이전트 한 번에")
    if st.button("🚀 전체 점검 실행", key="d5"):
        sast = sast_agent.run("sample_app/", "policies/CLAUDE.md")
        sec = secret_agent.run("sample_app/")
        dep = dependency_agent.run("sample_app/")
        total = len(sast) + len(sec) + len(dep)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("SAST", len(sast))
        m2.metric("Secret", len(sec))
        m3.metric("Dependency", len(dep))
        m4.metric("총 발견", total)
        allrows = ([{"에이전트": "SAST", "심각도": r["severity"], "근거": r["title"]} for r in sast]
                   + [{"에이전트": "Secret", "심각도": r["severity"], "근거": r["title"]} for r in sec]
                   + [{"에이전트": "Dependency", "심각도": r["severity"], "근거": r["cve"]} for r in dep])
        st.dataframe(allrows, width="stretch", hide_index=True)
        st.success(f"통합 점검 완료 — 총 {total}건. 실제 파이프라인은 검증·HITL·감사·리포트까지 이어집니다.")
    st.divider()
    st.markdown("#### 현업 적용 캔버스")
    canvas = os.path.join(ROOT, "course/department_adoption_canvas.md")
    if os.path.exists(canvas):
        with st.expander("Department Adoption Canvas 보기"):
            st.markdown(open(canvas, encoding="utf-8").read())

    st.divider()
    st.markdown("#### 🧠 (보너스) AI 경영진 보고서 — 전체 발견을 한 장으로")
    st.caption(f"규칙 에이전트가 모은 발견을 AI가 경영진용 요약 + 즉시 대응 Top3 로. 현재 모드: {llm_client.mode_label()}")
    if st.button("🧠 AI 경영진 보고서 생성", key="d5_ai"):
        fnd = (sast_agent.run("sample_app/", "policies/CLAUDE.md")
               + secret_agent.run("sample_app/") + dependency_agent.run("sample_app/"))
        st.markdown(llm_client.interpret(fnd))   # 키 없으면 결정론적 fallback 자동
    with st.expander("🎯 개선 과제 (직접 해보기)"):
        st.markdown(
            "- `course/department_adoption_canvas.md` 를 우리 팀 버전으로 직접 채워보기\n"
            "- `policies/CLAUDE.md` 에 사내 규칙 1줄 추가 → 전체 결과가 어떻게 바뀌는지 확인\n"
            "- (도전) `orchestrator/supervisor_graph.py` 의 `review()` 에 새 BLOCK 조건 1개 추가"
        )
