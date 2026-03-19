import streamlit as st
import anthropic
from datetime import datetime

# ── 페이지 설정 ──────────────────────────────────────────────
st.set_page_config(
    page_title="중1 수학 AI 선생님",
    page_icon="📐",
    layout="wide"
)

# ── CSS 스타일 ────────────────────────────────────────────────
st.markdown("""
<style>
    /* 전체 배경 */
    .stApp {
        background-color: #f0f4ff;
    }

    /* 사이드바 배경 */
    [data-testid="stSidebar"] {
        background-color: #1a237e;
    }

    /* 사이드바 일반 텍스트 */
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown {
        color: white !important;
    }

    /* ====================================================
       사이드바 버튼 — 흰 배경 + 남색 글씨
    ==================================================== */
    [data-testid="stSidebar"] button,
    [data-testid="stSidebar"] button[kind="secondary"],
    [data-testid="stSidebar"] button[kind="primary"],
    [data-testid="stSidebar"] .stButton button,
    [data-testid="stSidebar"] .stButton > button,
    [data-testid="stSidebar"] div[data-testid="stButton"] button {
        background-color: #ffffff !important;
        color: #1a237e !important;
        border: 2px solid #c5cae9 !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        padding: 8px 16px !important;
        width: 100% !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.15) !important;
    }

    /* 버튼 내부 p 태그 (Streamlit 구조상 필수) */
    [data-testid="stSidebar"] button p,
    [data-testid="stSidebar"] .stButton button p,
    [data-testid="stSidebar"] .stButton > button p {
        color: #1a237e !important;
        font-weight: 700 !important;
    }

    /* 호버 */
    [data-testid="stSidebar"] button:hover,
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #e8eaf6 !important;
        color: #1a237e !important;
        border-color: #9fa8da !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
    }
    [data-testid="stSidebar"] button:hover p,
    [data-testid="stSidebar"] .stButton > button:hover p {
        color: #1a237e !important;
    }

    /* 클릭 */
    [data-testid="stSidebar"] button:active,
    [data-testid="stSidebar"] .stButton > button:active {
        background-color: #c5cae9 !important;
        color: #1a237e !important;
    }

    /* 포커스 */
    [data-testid="stSidebar"] button:focus,
    [data-testid="stSidebar"] .stButton > button:focus {
        background-color: #ffffff !important;
        color: #1a237e !important;
        outline: none !important;
        box-shadow: 0 0 0 3px rgba(57,73,171,0.3) !important;
    }

    /* ====================================================
       사이드바 selectbox — 흰 배경 + 남색 글씨
    ==================================================== */
    [data-testid="stSidebar"] .stSelectbox > div > div {
        background-color: white !important;
        color: #1a237e !important;
        border-radius: 8px !important;
        border: none !important;
    }

    /* selectbox 선택된 값 텍스트 */
    [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] div,
    [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] span,
    [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] input {
        color: #1a237e !important;
        background-color: white !important;
    }

    /* placeholder 텍스트 색상 (회색으로 구분) */
    [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] [data-testid="stMarkdownContainer"] p {
        color: #9e9e9e !important;
    }

    /* 드롭다운 화살표 영역 */
    [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] svg {
        fill: #1a237e !important;
    }

    /* 사이드바 radio 텍스트 */
    [data-testid="stSidebar"] .stRadio label span {
        color: white !important;
        font-size: 0.95rem !important;
    }

    /* 사이드바 text_input */
    [data-testid="stSidebar"] .stTextInput > div > div > input {
        background-color: white !important;
        color: #1a237e !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 500 !important;
    }

    /* 사이드바 구분선 */
    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.3) !important;
    }

    /* 사이드바 알림 박스 */
    [data-testid="stSidebar"] .stAlert p {
        color: inherit !important;
    }

    /* 헤더 카드 */
    .header-card {
        background: linear-gradient(135deg, #1a237e 0%, #3949ab 100%);
        color: white;
        padding: 20px 28px;
        border-radius: 16px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(26,35,126,0.3);
    }
    .header-card h1 { margin: 0; font-size: 1.8rem; }
    .header-card p  { margin: 6px 0 0; opacity: 0.85; font-size: 0.95rem; }

    /* 학습 카드 */
    .lesson-card {
        background: white;
        border-left: 5px solid #3949ab;
        border-radius: 12px;
        padding: 18px 22px;
        margin-bottom: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    .lesson-card h3 { color: #1a237e; margin: 0 0 8px; }

    /* 채팅 — 학생 */
    .chat-user {
        background: #3949ab;
        color: white;
        border-radius: 18px 18px 4px 18px;
        padding: 12px 16px;
        margin: 8px 0;
        max-width: 80%;
        margin-left: auto;
        word-break: keep-all;
    }

    /* 채팅 — AI */
    .chat-ai {
        background: white;
        color: #212121;
        border-radius: 18px 18px 18px 4px;
        padding: 12px 16px;
        margin: 8px 0;
        max-width: 85%;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        word-break: keep-all;
    }

    /* 뱃지 */
    .badge {
        display: inline-block;
        background: #e8eaf6;
        color: #3949ab;
        border-radius: 20px;
        padding: 3px 12px;
        font-size: 0.8rem;
        font-weight: bold;
        margin-right: 6px;
    }

    /* 메인 버튼 */
    .stButton > button {
        border-radius: 10px;
        font-weight: bold;
    }

    /* 입력창 */
    .stTextInput > div > input,
    .stTextArea > div > textarea {
        border-radius: 10px;
    }

    /* 구분선 */
    hr { border: none; border-top: 2px solid #e8eaf6; margin: 16px 0; }
</style>
""", unsafe_allow_html=True)

# ── 중1 수학 단원 데이터 ──────────────────────────────────────
UNITS = {
    "1단원: 소인수분해": {
        "icon": "🔢",
        "topics": [
            {"day": 1, "title": "소수와 합성수"},
            {"day": 2, "title": "거듭제곱"},
            {"day": 3, "title": "소인수분해 방법"},
            {"day": 4, "title": "최대공약수"},
            {"day": 5, "title": "최소공배수"},
            {"day": 6, "title": "최대공약수와 최소공배수 활용"},
        ]
    },
    "2단원: 정수와 유리수": {
        "icon": "➕",
        "topics": [
            {"day": 1, "title": "양수와 음수"},
            {"day": 2, "title": "정수와 유리수"},
            {"day": 3, "title": "수직선과 절댓값"},
            {"day": 4, "title": "정수의 덧셈과 뺄셈"},
            {"day": 5, "title": "정수의 곱셈과 나눗셈"},
            {"day": 6, "title": "유리수의 사칙연산"},
        ]
    },
    "3단원: 문자와 식": {
        "icon": "🔡",
        "topics": [
            {"day": 1, "title": "문자의 사용과 식의 값"},
            {"day": 2, "title": "일차식과 수의 곱셈·나눗셈"},
            {"day": 3, "title": "일차식의 덧셈과 뺄셈"},
            {"day": 4, "title": "방정식과 항등식"},
            {"day": 5, "title": "일차방정식 풀기"},
            {"day": 6, "title": "일차방정식의 활용"},
        ]
    },
    "4단원: 좌표와 그래프": {
        "icon": "📊",
        "topics": [
            {"day": 1, "title": "순서쌍과 좌표"},
            {"day": 2, "title": "사분면"},
            {"day": 3, "title": "그래프 읽기"},
            {"day": 4, "title": "정비례 관계"},
            {"day": 5, "title": "반비례 관계"},
            {"day": 6, "title": "정비례·반비례 활용"},
        ]
    },
    "5단원: 기본 도형": {
        "icon": "📐",
        "topics": [
            {"day": 1, "title": "점, 선, 면, 각"},
            {"day": 2, "title": "직선, 반직선, 선분"},
            {"day": 3, "title": "각도와 맞꼭지각"},
            {"day": 4, "title": "평행선과 동위각·엇각"},
            {"day": 5, "title": "위치 관계"},
            {"day": 6, "title": "작도와 합동"},
        ]
    },
    "6단원: 평면도형": {
        "icon": "🔷",
        "topics": [
            {"day": 1, "title": "다각형의 내각과 외각"},
            {"day": 2, "title": "삼각형의 내각의 합"},
            {"day": 3, "title": "원과 부채꼴"},
            {"day": 4, "title": "부채꼴의 호와 넓이"},
            {"day": 5, "title": "다각형의 넓이"},
            {"day": 6, "title": "평면도형 활용 문제"},
        ]
    },
    "7단원: 입체도형": {
        "icon": "🧊",
        "topics": [
            {"day": 1, "title": "다면체"},
            {"day": 2, "title": "정다면체"},
            {"day": 3, "title": "회전체"},
            {"day": 4, "title": "기둥의 겉넓이와 부피"},
            {"day": 5, "title": "뿔의 겉넓이와 부피"},
            {"day": 6, "title": "구의 겉넓이와 부피"},
        ]
    },
    "8단원: 통계": {
        "icon": "📈",
        "topics": [
            {"day": 1, "title": "줄기와 잎 그림"},
            {"day": 2, "title": "도수분포표"},
            {"day": 3, "title": "히스토그램"},
            {"day": 4, "title": "도수분포다각형"},
            {"day": 5, "title": "상대도수"},
            {"day": 6, "title": "통계 자료 해석"},
        ]
    },
}

# placeholder 역할을 할 상수
UNIT_PLACEHOLDER = "📚 단원을 선택해주세요."
DAY_PLACEHOLDER  = "📆 일차를 선택해주세요."

# ── 시스템 프롬프트 ───────────────────────────────────────────
def get_system_prompt(mode: str, unit: str = "", topic: str = "") -> str:
    base = """당신은 중학교 1학년 수학 선생님입니다.
규칙:
- 반드시 한국어로만 답하세요.
- 학생들이 글 읽기를 싫어하므로 짧고 간결하게 답하세요.
- 이모지를 적절히 사용해 친근하게 설명하세요.
- 어려운 용어는 쉽게 풀어 설명하세요.
- 틀린 답에는 격려와 함께 힌트를 주세요.
- 수식은 알아보기 쉽게 표현하세요.
- 답변은 최대 150자 이내로 짧게 유지하세요."""

    if mode == "daily":
        return f"""{base}

지금 모드: 오늘의 학습
단원: {unit}
오늘 주제: {topic}

학습 시작 시 다음 순서로 진행하세요:
1. 핵심 개념을 3~4줄 이내로 초간단 설명
2. 예시 1개
3. 확인 문제 2개 제시 (번호 매기기)
학생이 답을 입력하면 맞고 틀림을 알려주고 해설은 1~2줄로만 하세요."""

    else:
        return f"""{base}

지금 모드: 자유 질문
중학교 1학년 수학 전 범위에 대해 질문에 답하세요.
모르는 내용이나 헷갈리는 개념 모두 편하게 질문받으세요."""


# ── 세션 상태 초기화 ──────────────────────────────────────────
def init_session():
    defaults = {
        "api_key": "",
        "messages": [],
        "mode": "daily",
        # None = 아직 선택 안 함 (placeholder 표시)
        "selected_unit": None,
        "selected_day":  None,
        "lesson_started": False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_session()

# ── Anthropic 클라이언트 ──────────────────────────────────────
def get_client():
    if st.session_state.api_key:
        return anthropic.Anthropic(api_key=st.session_state.api_key)
    return None

# ── AI 응답 생성 ──────────────────────────────────────────────
def get_ai_response(user_message: str, system_prompt: str) -> str:
    client = get_client()
    if not client:
        return "⚠️ API 키를 먼저 입력해 주세요!"

    history  = st.session_state.messages[-10:]
    messages = [{"role": m["role"], "content": m["content"]} for m in history]
    messages.append({"role": "user", "content": user_message})

    try:
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=600,
            system=system_prompt,
            messages=messages
        )
        return response.content[0].text
    except anthropic.AuthenticationError:
        return "❌ API 키가 올바르지 않습니다. 다시 확인해 주세요."
    except anthropic.RateLimitError:
        return "⏳ 잠시 후 다시 시도해 주세요. (요청 한도 초과)"
    except Exception as e:
        return f"❌ 오류 발생: {str(e)}"

# ── 오늘의 학습 자동 시작 ────────────────────────────────────
def start_daily_lesson(unit: str, day: int):
    topic   = UNITS[unit]["topics"][day - 1]["title"]
    system  = get_system_prompt("daily", unit, topic)
    trigger = f"{unit} {day}일차 '{topic}' 학습을 시작해주세요."

    with st.spinner("선생님이 준비 중이에요... ✏️"):
        ai_msg = get_ai_response(trigger, system)

    st.session_state.messages = []
    st.session_state.messages.append({"role": "user",      "content": trigger})
    st.session_state.messages.append({"role": "assistant", "content": ai_msg})
    st.session_state.lesson_started = True
    st.rerun()


# ════════════════════════════════════════════════════════════
# 사이드바
# ════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 📐 중1 수학 AI 선생님")
    st.markdown("---")

    # ── API 키 ───────────────────────────────────────────────
    st.markdown("### 🔑 API 키")
    api_key_input = st.text_input(
        "Anthropic API Key",
        type="password",
        value=st.session_state.api_key,
        placeholder="sk-ant-...",
        label_visibility="collapsed"
    )
    if api_key_input:
        st.session_state.api_key = api_key_input
        if api_key_input.startswith("sk-ant"):
            st.success("✅ API 키 입력됨")
        else:
            st.warning("⚠️ 키 형식을 확인하세요")

    st.markdown("---")

    # ── 모드 선택 ────────────────────────────────────────────
    st.markdown("### 📚 학습 모드 선택")
    mode_options = {"📅 오늘의 학습": "daily", "❓ 자유 질문": "free"}
    selected_mode_label = st.radio(
        "모드", list(mode_options.keys()), label_visibility="collapsed"
    )
    new_mode = mode_options[selected_mode_label]
    if new_mode != st.session_state.mode:
        st.session_state.mode          = new_mode
        st.session_state.messages      = []
        st.session_state.lesson_started = False

    st.markdown("---")

    # ── 단원 + 일차 선택 (오늘의 학습 모드) ─────────────────
    if st.session_state.mode == "daily":

        # ── 단원 선택 ─────────────────────────────────────────
        st.markdown("### 📖 단원 선택")

        # 첫 번째 항목을 placeholder 문자열로 설정
        unit_options = [UNIT_PLACEHOLDER] + list(UNITS.keys())

        # 현재 선택값의 index 계산
        if st.session_state.selected_unit is None:
            unit_index = 0                                      # placeholder
        else:
            unit_index = unit_options.index(st.session_state.selected_unit)

        selected_unit_raw = st.selectbox(
            "단원",
            unit_options,
            index=unit_index,
            label_visibility="collapsed",
            key="sb_unit"
        )

        # placeholder가 선택된 경우 None 처리
        if selected_unit_raw == UNIT_PLACEHOLDER:
            new_unit = None
        else:
            new_unit = selected_unit_raw

        # 단원이 바뀌면 일차 초기화
        if new_unit != st.session_state.selected_unit:
            st.session_state.selected_unit  = new_unit
            st.session_state.selected_day   = None   # 일차도 초기화
            st.session_state.messages       = []
            st.session_state.lesson_started = False

        # ── 일차 선택 ─────────────────────────────────────────
        st.markdown("### 📆 일차 선택")

        # 단원이 선택된 경우에만 실제 일차 목록 생성
        if st.session_state.selected_unit is not None:
            topics   = UNITS[st.session_state.selected_unit]["topics"]
            max_day  = len(topics)
            day_options = [DAY_PLACEHOLDER] + [
                f"{d}일차 - {topics[d-1]['title']}" for d in range(1, max_day + 1)
            ]

            if st.session_state.selected_day is None:
                day_index = 0
            else:
                day_index = st.session_state.selected_day  # 1-based → index 1~

            selected_day_raw = st.selectbox(
                "일차",
                day_options,
                index=day_index,
                label_visibility="collapsed",
                key="sb_day"
            )

            if selected_day_raw == DAY_PLACEHOLDER:
                new_day = None
            else:
                # "N일차 - 제목" 에서 N 추출
                new_day = int(selected_day_raw.split("일차")[0])

            if new_day != st.session_state.selected_day:
                st.session_state.selected_day   = new_day
                st.session_state.messages       = []
                st.session_state.lesson_started = False

        else:
            # 단원 미선택 시 일차 selectbox는 placeholder만 표시
            st.selectbox(
                "일차",
                [DAY_PLACEHOLDER],
                index=0,
                label_visibility="collapsed",
                key="sb_day_disabled"
            )

        st.markdown("---")

        # ── 선택 요약 + 학습 시작 버튼 ───────────────────────
        if st.session_state.selected_unit and st.session_state.selected_day:
            unit_icon  = UNITS[st.session_state.selected_unit]["icon"]
            topic_name = UNITS[st.session_state.selected_unit]["topics"][
                st.session_state.selected_day - 1]["title"]
            st.markdown(f"**{unit_icon} {topic_name}**")

            if st.button("🚀 학습 시작!", use_container_width=True, key="btn_start"):
                if not st.session_state.api_key:
                    st.error("API 키를 먼저 입력해 주세요!")
                else:
                    start_daily_lesson(
                        st.session_state.selected_unit,
                        st.session_state.selected_day
                    )
        else:
            # 선택 미완료 시 버튼 비활성화처럼 표시
            st.markdown(
                "<div style='background:#3949ab;border-radius:10px;padding:9px 16px;"
                "text-align:center;color:rgba(255,255,255,0.45);font-weight:700;"
                "font-size:0.95rem;cursor:not-allowed;'>🚀 학습 시작!</div>",
                unsafe_allow_html=True
            )
            st.caption("단원과 일차를 먼저 선택해주세요.")

    st.markdown("---")

    if st.button("🗑️ 대화 초기화", use_container_width=True, key="btn_clear"):
        st.session_state.messages       = []
        st.session_state.lesson_started = False
        st.rerun()

    st.markdown("---")
    st.markdown(
        "<small style='opacity:0.8;'>Made with ❤️ for 중1 students<br>"
        "Model: claude-sonnet-4-5</small>",
        unsafe_allow_html=True
    )


# ════════════════════════════════════════════════════════════
# 메인 화면
# ════════════════════════════════════════════════════════════

# ── 헤더 ────────────────────────────────────────────────────
if st.session_state.mode == "daily" and st.session_state.selected_unit and st.session_state.selected_day:
    unit      = st.session_state.selected_unit
    day       = st.session_state.selected_day
    topic     = UNITS[unit]["topics"][day - 1]["title"]
    unit_icon = UNITS[unit]["icon"]
    today     = datetime.now().strftime("%Y년 %m월 %d일")
    st.markdown(f"""
    <div class="header-card">
        <h1>{unit_icon} 오늘의 수학 학습</h1>
        <p>📅 {today} &nbsp;|&nbsp; 📖 {unit} &nbsp;|&nbsp; 🗓️ {day}일차: {topic}</p>
    </div>
    """, unsafe_allow_html=True)

elif st.session_state.mode == "daily":
    today = datetime.now().strftime("%Y년 %m월 %d일")
    st.markdown(f"""
    <div class="header-card">
        <h1>📐 오늘의 수학 학습</h1>
        <p>📅 {today} &nbsp;|&nbsp; 👈 단원과 일차를 선택하고 학습을 시작하세요!</p>
    </div>
    """, unsafe_allow_html=True)

else:
    st.markdown("""
    <div class="header-card">
        <h1>💬 자유 질문 코너</h1>
        <p>중1 수학 어떤 것이든 물어보세요! 선생님이 답해드려요 😊</p>
    </div>
    """, unsafe_allow_html=True)

# ── 오늘의 학습 — 단원·일차 미선택 시 안내 ──────────────────
if st.session_state.mode == "daily" and (
    st.session_state.selected_unit is None or st.session_state.selected_day is None
):
    st.markdown("""
    <div class="lesson-card">
        <h3>👈 학습을 시작하려면?</h3>
        <p>① 왼쪽에서 <b>단원</b>을 선택하세요.<br>
           ② <b>일차</b>를 선택하세요.<br>
           ③ <b>🚀 학습 시작!</b> 버튼을 누르세요.</p>
    </div>
    """, unsafe_allow_html=True)

    # 단원 카드 미리보기
    cols = st.columns(4)
    for i, (unit_name, unit_data) in enumerate(UNITS.items()):
        with cols[i % 4]:
            st.markdown(f"""
            <div style="background:white;border-radius:10px;padding:12px 14px;
                        margin:4px 0;box-shadow:0 1px 4px rgba(0,0,0,0.08);
                        text-align:center;">
                <div style="font-size:1.6rem;">{unit_data['icon']}</div>
                <div style="font-size:0.8rem;color:#1a237e;font-weight:bold;
                            margin-top:4px;">{unit_name}</div>
            </div>
            """, unsafe_allow_html=True)

# ── 오늘의 학습 — 단원·일차 선택 후, 학습 시작 전 안내 ───────
elif st.session_state.mode == "daily" and not st.session_state.lesson_started:
    unit      = st.session_state.selected_unit
    day       = st.session_state.selected_day
    topics    = UNITS[unit]["topics"]
    unit_icon = UNITS[unit]["icon"]

    st.markdown(f"""
    <div class="lesson-card">
        <h3>{unit_icon} {unit}</h3>
        <p>오늘은 <b>{day}일차</b> 학습입니다! 사이드바의 🚀 버튼을 눌러 시작하세요.</p>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(3)
    for i, t in enumerate(topics):
        with cols[i % 3]:
            is_today = (t["day"] == day)
            border   = "border: 2px solid #3949ab;" if is_today else ""
            bg       = "background:#e8eaf6;"         if is_today else "background:white;"
            badge    = '<span class="badge">오늘</span>' if is_today else ""
            st.markdown(f"""
            <div style="{bg}{border}border-radius:10px;padding:10px 14px;margin:4px 0;
                         box-shadow:0 1px 4px rgba(0,0,0,0.08);">
                <b style="color:#1a237e;">{t['day']}일차</b> {badge}<br>
                <span style="font-size:0.9rem;">{t['title']}</span>
            </div>
            """, unsafe_allow_html=True)

# ── 자유 질문 — 예시 ─────────────────────────────────────────
if st.session_state.mode == "free" and not st.session_state.messages:
    col1, col2, col3 = st.columns(3)
    examples = [
        ("🔢", "소인수분해가 뭐예요?"),
        ("➕", "음수 × 음수는 왜 양수예요?"),
        ("📐", "맞꼭지각이 뭐예요?"),
    ]
    for col, (icon, text) in zip([col1, col2, col3], examples):
        with col:
            st.markdown(f"""
            <div class="lesson-card" style="text-align:center;">
                <div style="font-size:2rem;">{icon}</div>
                <p style="margin:4px 0;font-size:0.9rem;color:#3949ab;"><b>예시 질문</b></p>
                <p style="margin:0;font-size:0.85rem;">"{text}"</p>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

# ── 채팅 히스토리 ────────────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        if "학습을 시작해주세요" in msg["content"]:
            continue
        st.markdown(f"""
        <div style="display:flex;justify-content:flex-end;margin:6px 0;">
            <div class="chat-user">🙋 {msg['content']}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="display:flex;justify-content:flex-start;margin:6px 0;align-items:flex-start;">
            <div style="font-size:1.5rem;margin-right:8px;">👩‍🏫</div>
            <div class="chat-ai">{msg['content']}</div>
        </div>
        """, unsafe_allow_html=True)

# ── 채팅 입력 ─────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
placeholder_text = (
    "답을 입력하거나, 모르는 부분을 물어보세요! 💬"
    if st.session_state.mode == "daily"
    else "중1 수학 궁금한 것 뭐든지 물어보세요! 💬"
)

with st.form(key="chat_form", clear_on_submit=True):
    col_input, col_btn = st.columns([5, 1])
    with col_input:
        user_input = st.text_input(
            "메시지", placeholder=placeholder_text, label_visibility="collapsed"
        )
    with col_btn:
        submitted = st.form_submit_button("전송 ✈️", use_container_width=True)

if submitted and user_input.strip():
    if not st.session_state.api_key:
        st.error("⚠️ 먼저 API 키를 입력해 주세요!")
    elif st.session_state.mode == "daily" and (
        not st.session_state.selected_unit or not st.session_state.selected_day
    ):
        st.warning("👈 먼저 단원과 일차를 선택해 주세요!")
    else:
        if st.session_state.mode == "daily":
            unit   = st.session_state.selected_unit
            topic  = UNITS[unit]["topics"][st.session_state.selected_day - 1]["title"]
            system = get_system_prompt("daily", unit, topic)
        else:
            system = get_system_prompt("free")

        st.session_state.messages.append({"role": "user", "content": user_input.strip()})

        with st.spinner("선생님이 답변 중... ✏️"):
            ai_response = get_ai_response(user_input.strip(), system)

        st.session_state.messages.append({"role": "assistant", "content": ai_response})
        st.rerun()

# ── 진행 상황 바 ──────────────────────────────────────────────
if (st.session_state.mode == "daily"
        and st.session_state.lesson_started
        and st.session_state.selected_unit
        and st.session_state.selected_day):
    st.markdown("---")
    unit       = st.session_state.selected_unit
    total_days = len(UNITS[unit]["topics"])
    progress   = st.session_state.selected_day / total_days
    msg_count  = len([m for m in st.session_state.messages if m["role"] == "user"])

    st.markdown(f"**{unit} 진행도** ({st.session_state.selected_day}/{total_days}일차)")
    st.progress(progress)
    st.caption(f"💬 이번 학습 대화 수: {msg_count}회")
