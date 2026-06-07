"""
대시보드 공용 렌더 모듈 (dashboard_lib.py)

app.py(전체 1개)와 apps/day1~5.py(개별)가 이 함수들을 공유한다.
키 없이 동작 · 외부 API 호출 없음.
"""
import importlib.util
import json
import os
import random
import sys

import streamlit as st

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
# 어디서 `streamlit run` 하든 상대경로(sample_app/ · policies/ · reports/)가 맞도록 작업 폴더 고정
os.chdir(ROOT)


_CACHE = {}


def _load(path, name):
    """미니랩 모듈을 '필요할 때만' 로드(캐시). Day별 저장소에서 다른 Day 파일이 없어도
    import 시점에 깨지지 않도록 — 각 render 함수 안에서 호출한다."""
    if name in _CACHE:
        return _CACHE[name]
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _CACHE[name] = mod
    return mod

# Day 1 'AI 하네스' 데모용 — 정책(시스템 프롬프트) 프리셋
AI_POLICIES = {
    "📋 액션 비서": "당신은 회의록 정리 비서입니다. 회의 내용에서 'Action Items'만 골라 "
                   "담당자와 마감일을 포함해 불릿(-)으로만 출력하세요. 그 외 설명은 쓰지 마세요.",
    "⚠️ 리스크 분석가": "당신은 리스크 분석가입니다. 회의 내용에서 위험요소(Risks)만 최대 3개, "
                      "한 줄씩 불릿(-)으로 출력하세요. 그 외 내용은 쓰지 마세요.",
    "✏️ 한 줄 요약가": "당신은 요약 전문가입니다. 이 회의의 핵심을 정확히 한 문장으로만 요약하세요.",
}


# ─────────────────────────── 개요 ───────────────────────────
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


# ─────────────────────────── 왜 만드나? ───────────────────────────
def render_why():
    from agents import sast_agent
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


# ─────────────────────────── Day 1 ───────────────────────────
def render_day1():
    ma = _load("course/mini_labs/day01_single_agent/meeting_agent.py", "ma")
    from agents import sast_agent, llm_client
    st.subheader("Day 1 · 정책이 결과를 바꾼다")
    st.markdown("#### ① Mini Lab — 회의 메모 정리 (정책 체크박스를 켜고 꺼보세요!)")
    notes_path = os.path.join(ROOT, "course/mini_labs/day01_single_agent/meeting_notes.txt")
    if not os.path.exists(notes_path):
        st.error("meeting_notes.txt 가 없습니다. 터미널에서 `git checkout .` 으로 복구하세요.")
    else:
        notes = open(notes_path, encoding="utf-8").read()
        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown("**정책: 어떤 섹션을 출력할까?**")
            picked = {}
            for key, kw, title in ma.SECTIONS:
                picked[key] = st.checkbox(title, value=True, key=f"sec_{key}")
            with st.expander("회의 메모 원문 보기"):
                st.code(notes)
        with c2:
            data = ma._parse_notes(notes)
            enabled = [(k, t) for k, kw, t in ma.SECTIONS if picked[k]]
            st.markdown("**📄 결과 (체크 즉시 바뀝니다)**")
            st.markdown(ma.build_report(data, enabled))
            if not picked.get("risks"):
                st.info("👈 'Risks' 체크를 껐더니 결과에서 Risks 섹션이 사라졌죠? "
                        "→ 이게 **정책이 에이전트 출력을 통제**하는 핵심입니다.")
    st.divider()
    st.markdown("#### ② Main Lab — 정책 기반 SAST (같은 코드, 정책만 바꿔보기)")
    pol = st.radio("정책 선택", ["policies/CLAUDE_base.md (가중 없음)", "policies/CLAUDE.md (차량 모듈 가중)"],
                   horizontal=True)
    pol_path = "policies/CLAUDE.md" if "CLAUDE.md (차량" in pol else "policies/CLAUDE_base.md"
    if st.button("🔍 SAST 실행", key="d1_sast"):
        res = sast_agent.run("sample_app/", pol_path)
        rows = [{"심각도": r["severity"], "CWE": r["cwe"],
                 "파일": os.path.basename(r["file"]), "줄": r["line"], "내용": r["title"]} for r in res]
        st.dataframe(rows, width="stretch", hide_index=True)
        ctrl = [r for r in res if "control" in r["file"]]
        if ctrl:
            sev = ctrl[0]["severity"]
            st.success(f"차량 제어 모듈(control/) 발견 심각도 = **{sev}** "
                       + ("→ 정책 가중으로 Critical 상향! 🚨" if sev == "Critical" else "(기본 정책: High)"))

    st.divider()
    st.markdown("#### ③ (보너스) 🧠 AI 하네스 — 같은 회의록, '시스템 프롬프트(정책)'만 바꾸면?")
    st.caption("Day 1 핵심: **정책이 출력을 통제**. ②는 규칙으로, ③은 진짜 AI로 같은 원리를 보여줍니다. "
               "AI 키가 없으면 규칙 fallback 으로 안전하게 동작해요.")
    notes_path2 = os.path.join(ROOT, "course/mini_labs/day01_single_agent/meeting_notes.txt")
    if os.path.exists(notes_path2):
        pick = st.radio("AI 정책(시스템 프롬프트) 고르기", list(AI_POLICIES), horizontal=True, key="d1_ai_pick")
        system = st.text_area("시스템 프롬프트 (직접 고쳐도 됩니다)", value=AI_POLICIES[pick], height=90, key="d1_ai_sys")
        st.caption(f"현재 모드: {llm_client.mode_label()}")
        if st.button("🧠 AI 하네스 실행", key="d1_ai_run"):
            notes2 = open(notes_path2, encoding="utf-8").read()
            out = llm_client.complete(system, notes2)
            if out:
                st.markdown("**🧠 AI 출력 (정책대로):**")
                st.markdown(out)
                st.success(f"정책을 바꾸면 같은 회의록인데도 AI 출력이 통째로 바뀝니다 — 이게 '하네스'. ({llm_client.mode_label()})")
            else:
                st.warning("AI 키가 없어 **규칙 fallback** 으로 보여줍니다. (키를 넣으면 위 정책대로 진짜 LLM이 작성해요)")
                data2 = ma._parse_notes(notes2)
                fb = {"📋 액션 비서": ("action_items", "Action Items"),
                      "⚠️ 리스크 분석가": ("risks", "Risks"),
                      "✏️ 한 줄 요약가": ("summary", "Summary")}[pick]
                items = data2.get(fb[0], [])
                st.markdown(f"**{fb[1]} (규칙 추출):**")
                st.markdown("\n".join(f"- {x}" for x in items) or "- (없음)")
    with st.expander("🎯 이 Day 과제 (직접 해보기)"):
        st.markdown("기본 + 생성형(보일러플레이트) + 도전 과제 → **`course/exercises/Day01_exercises.md`**")


# ─────────────────────────── Day 2 ───────────────────────────
def render_day2():
    toy = _load("course/mini_labs/day02_tool_calling/toy_tools.py", "toy")
    from agents import sast_agent, secret_agent, dependency_agent, llm_client
    st.subheader("Day 2 · 도구 호출 & 결과 분리")
    st.markdown("#### ① Mini Lab — Toy Tool (Raw JSON ↔ 사람용 결과)")
    fb_path = os.path.join(ROOT, "course/mini_labs/day02_tool_calling/sample_feedback.txt")
    if st.button("🧰 도구 4종 실행", key="d2_toy") and os.path.exists(fb_path):
        text = open(fb_path, encoding="utf-8").read()
        cw = toy.count_words(text)
        kw = toy.extract_keywords(text)
        fb = toy.summarize_feedback(text)
        m1, m2, m3 = st.columns(3)
        m1.metric("단어 수", cw["word_count"])
        m2.metric("긍정 문장", fb["positive_count"])
        m3.metric("부정 문장", fb["negative_count"])
        st.markdown("**키워드 Top 5**")
        st.dataframe(kw, width="stretch", hide_index=True)
        with st.expander("🔧 Raw JSON (기계용) — 사람용 화면과 분리"):
            st.json({"count_words": cw, "extract_keywords": kw, "summarize_feedback": fb})
    st.divider()
    st.markdown("#### ② Main Lab — 보안 도구 (Secret / Dependency)")
    cc1, cc2 = st.columns(2)
    if cc1.button("🔑 Secret 점검", key="d2_sec"):
        res = secret_agent.run("sample_app/")
        st.dataframe([{"파일": os.path.basename(r["file"]), "줄": r["line"],
                       "내용": r["title"], "근거(마스킹됨)": r["evidence"]} for r in res],
                     width="stretch", hide_index=True)
    if cc2.button("📦 Dependency(CVE) 점검", key="d2_dep"):
        res = dependency_agent.run("sample_app/")
        st.dataframe([{"심각도": r["severity"], "CVE": r["cve"], "근거": r["evidence"]} for r in res],
                     width="stretch", hide_index=True)

    st.divider()
    st.markdown("#### 🧠 (보너스) AI 로 'Raw 발견 → 사람용 리포트'")
    st.caption(f"도구가 찾은 Raw 발견을 AI가 사람 말로 해석합니다. 현재 모드: {llm_client.mode_label()}")
    if st.button("🧠 AI 리포트 생성", key="d2_ai"):
        fnd = (sast_agent.run("sample_app/", "policies/CLAUDE.md")
               + secret_agent.run("sample_app/") + dependency_agent.run("sample_app/"))
        st.markdown(llm_client.interpret(fnd))   # 키 없으면 결정론적 fallback 자동
    with st.expander("🎯 이 Day 과제 (직접 해보기)"):
        st.markdown("기본 + 생성형(보일러플레이트) + 도전 과제 → **`course/exercises/Day02_exercises.md`**")


# ─────────────────────────── Day 3 ───────────────────────────
def render_day3():
    bug = _load("course/mini_labs/day03_multi_agent_game/run_bug_hunt_game.py", "bug")
    from agents import llm_client
    st.subheader("Day 3 · 멀티에이전트 = 역할 분리")
    st.markdown("#### Mini Lab — Bug Hunt Game (Planner → Hunter → Reviewer → Reporter)")
    if st.button("🐞 버그 헌트 실행", key="d3"):
        src = open(bug.SNIPPET, encoding="utf-8").read()
        lines = src.splitlines()
        plan = bug.planner()
        cands = bug.hunter(plan, lines)
        confirmed, rejected = bug.reviewer(cands, src, lines)
        colp, colh, colr = st.columns(3)
        with colp:
            st.markdown("**🧭 Planner — 계획**")
            for p in plan:
                st.write(f"- {p['관점']}")
        with colh:
            st.markdown(f"**🔎 Hunter — 후보 {len(cands)}**")
            for c in cands:
                st.write(f"- L{c['line']} `{c['code']}`")
        with colr:
            st.markdown(f"**✅ Reviewer — 확정 {len(confirmed)} / 기각 {len(rejected)}**")
            for c in confirmed:
                st.success(f"L{c['line']} [{c['id']}] {c['사유']}")
            for c in rejected:
                st.warning(f"L{c['line']} [{c['id']}] (기각) {c['사유']}")
        st.info("모델을 여러 개 쓴 게 아니라 **역할/책임을 나눈 것**이 멀티에이전트의 핵심입니다.")

    st.divider()
    st.markdown("#### 🧠 (보너스) AI Reviewer — '역할'을 시스템 프롬프트로 부여")
    st.caption(f"규칙 Reviewer 대신 AI에게 'reviewer 역할'을 줘서 후보를 재검증. 현재 모드: {llm_client.mode_label()}")
    if st.button("🧠 AI Reviewer 실행", key="d3_ai"):
        src = open(bug.SNIPPET, encoding="utf-8").read()
        lines = src.splitlines()
        cands = bug.hunter(bug.planner(), lines)
        user = "\n".join(f"L{c['line']}: {c['code']}" for c in cands)
        out = llm_client.complete(
            "당신은 시니어 파이썬 코드 리뷰어입니다. 아래 각 코드 줄이 '진짜 버그'인지 '오탐'인지 "
            "판정하고 한 줄 이유를 붙여 불릿으로 답하세요.", user)
        if out:
            st.markdown(out)
            st.success(f"같은 후보라도 '리뷰어 역할'을 주면 AI가 검증자처럼 행동합니다. ({llm_client.mode_label()})")
        else:
            st.warning("AI 키 없음 → 규칙 Reviewer 결과로 표시 (키 넣으면 진짜 AI 검증)")
            cf, rj = bug.reviewer(cands, src, lines)
            for c in cf:
                st.write(f"✅ L{c['line']} [{c['id']}] {c['사유']}")
            for c in rj:
                st.write(f"❌ L{c['line']} [{c['id']}] {c['사유']}")
    with st.expander("🎯 이 Day 과제 (직접 해보기)"):
        st.markdown("기본 + 생성형(보일러플레이트) + 도전 과제 → **`course/exercises/Day03_exercises.md`**")


# ─────────────────────────── Day 4 ───────────────────────────
def render_day4():
    risk = _load("course/mini_labs/day04_risk_game/run_risk_sorting_game.py", "risk")
    from agents import threat_agent, llm_client
    st.subheader("Day 4 · 위험도 점수화 — High라고 항상 1순위 아님")
    cards = json.load(open(risk.CARDS, encoding="utf-8"))["cards"]
    for c in cards:
        c["risk_score"] = risk.risk_score(c)
    ranked = sorted(cards, key=lambda x: x["risk_score"], reverse=True)
    for i, c in enumerate(ranked, 1):
        c["계산순위"] = i
    st.markdown("**계산 순위 vs 사람 직관 순위**")
    st.dataframe([{"계산순위": c["계산순위"], "카드": c["title"], "심각도": c["severity"],
                   "KEV": "✔" if c["kev"] else "-", "EPSS": c["epss"],
                   "모듈": c["control_module"], "risk_score": c["risk_score"],
                   "사람추측": c["human_guess_rank"]} for c in ranked],
                 width="stretch", hide_index=True)
    st.bar_chart({c["title"]: c["risk_score"] for c in ranked})
    crit = next((c for c in cards if c["severity"] == "Critical"), None)
    if crit and crit["계산순위"] > 1:
        st.warning(f"⚠️ '{crit['title']}' 는 **Critical** 인데도 KEV 미등재·EPSS 낮음·내부망이라 "
                   f"계산순위 **{crit['계산순위']}위**로 밀렸습니다. → severity 라벨만으로 줄세우면 위험!")
    st.divider()
    if st.button("🛰️ Threat Intel (CVE→KEV/EPSS)", key="d4_threat"):
        ctx = threat_agent.run(["CVE-2020-14343", "CVE-2023-30861", "CVE-2024-22195"])
        st.dataframe([{"CVE": k, "심각도": v["severity"],
                       "KEV": "등재" if v["kev"] else "-", "EPSS": v["epss"]} for k, v in ctx.items()],
                     width="stretch", hide_index=True)

    st.divider()
    st.markdown("#### 🧠 (보너스) AI 보안책임자(CISO) — 우선순위 설명")
    st.caption(f"점수를 근거로 AI가 'Top 3 대응 순서'를 설명합니다. 현재 모드: {llm_client.mode_label()}")
    if st.button("🧠 AI 우선순위 설명", key="d4_ai"):
        user = json.dumps([{k: c[k] for k in ("title", "severity", "kev", "epss",
                                              "control_module", "risk_score")} for c in ranked],
                          ensure_ascii=False, indent=2)
        out = llm_client.complete(
            "당신은 보안책임자(CISO)입니다. 아래 위험 카드(JSON, risk_score 포함)에서 가장 먼저 "
            "대응할 Top 3 를 고르고 각 한 줄 이유를 쓰세요. severity 라벨이 아니라 risk_score·KEV·노출을 "
            "근거로 판단하세요.", user)
        if out:
            st.markdown(out)
        else:
            st.warning("AI 키 없음 → 점수 기반 Top 3 (키 넣으면 진짜 AI 설명)")
            for c in ranked[:3]:
                st.write(f"**{c['계산순위']}. {c['title']}** — score {c['risk_score']}, "
                         f"KEV {'O' if c['kev'] else 'X'}, EPSS {c['epss']}, {c['control_module']}")
    with st.expander("🎯 이 Day 과제 (직접 해보기)"):
        st.markdown("기본 + 생성형(보일러플레이트) + 도전 과제 → **`course/exercises/Day04_exercises.md`**")


# ─────────────────────────── Day 5 ───────────────────────────
def render_day5():
    from agents import sast_agent, secret_agent, dependency_agent, llm_client
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
    with st.expander("🎯 이 Day 과제 (직접 해보기)"):
        st.markdown("기본 + 생성형(보일러플레이트) + 도전 과제 → **`course/exercises/Day05_exercises.md`**")
