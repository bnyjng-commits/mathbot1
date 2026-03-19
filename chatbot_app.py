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
    /* 사이드바 */
    [data-testid="stSidebar"] {
        background-color: #1a237e;
        color: white;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stRadio label {
        color: white !important;
        font-weight: bold;
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
    .header-card h1 {
        margin: 0;
        font-size: 1.8rem;
    }
    .header-card p {
        margin: 6px 0 0;
        opacity: 0.85;
        font-size: 0.95rem;
    }
    /* 오늘의 학습 카드 */
    .lesson-card {
        background: white;
        border-left: 5px solid #3949ab;
        border-radius: 12px;
        padding: 18px 22px;
        margin-bottom: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    .lesson-card h3 {
        color: #1a237e;
        margin: 0 0 8px;
    }
    /* 채팅 메시지 */
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
    /* 태그 뱃지 */
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
    /* 버튼 커스텀 */
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
    hr {
        border: none;
        border-top: 2px solid #e8eaf6;
        margin: 16px 0;
    }
    /* 문제 박스 */
    .quiz-box {
        background: #fffde7;
        border: 2px solid #f9a825;
        border-radius: 12px;
        padding: 16px 20px;
        margin: 10px 0;
    }
    .quiz-box h4 {
        color: #e65100;
        margin: 0 0 8px;
    }
</style>
""", unsafe_allow_html=True)

# ── 중1 수학 단원 데이터 ──────────────────────────────────────
UNITS = {
    "1단원: 소인수분해": {
        "icon": "🔢",
        "topics": [
            {"day": 1, "title": "소수와 합성수", "emoji": "📌"},
            {"day": 2, "title": "거듭제곱", "emoji": "📌"},
            {"day": 3, "title": "소인수분해 방법", "emoji": "📌"},
            {"day": 4, "title": "최대공약수", "emoji": "📌"},
            {"day": 5, "title": "최소공배수", "emoji": "📌"},
            {"day": 6, "title": "최대공약수와 최소공배수 활용", "emoji": "📌"},
        ]
    },
    "2단원: 정수와 유리수": {
        "icon": "➕",
        "topics": [
            {"day": 1, "title": "양수와 음수", "emoji": "📌"},
            {"day": 2, "title": "정수와 유리수", "emoji": "📌"},
            {"day": 3, "title": "수직선과 절댓값", "emoji": "📌"},
            {"day": 4, "title": "정수의 덧셈과 뺄셈", "emoji": "📌"},
            {"day": 5, "title": "정수의 곱셈과 나눗셈", "emoji": "📌"},
            {"day": 6, "title": "유리수의 사칙연산", "emoji": "📌"},
        ]
    },
    "3단원: 문자와 식": {
        "icon": "🔡",
        "topics": [
            {"day": 1, "title": "문자의 사용과 식의 값", "emoji": "📌"},
            {"day": 2, "title": "일차식과 수의 곱셈·나눗셈", "emoji": "📌"},
            {"day": 3, "title": "일차식의 덧셈과 뺄셈", "emoji": "📌"},
            {"day": 4, "title": "방정식과 항등식", "emoji": "📌"},
            {"day": 5, "title": "일차방정식 풀기", "emoji": "📌"},
            {"day": 6, "title": "일차방정식의 활용", "emoji": "📌"},
        ]
    },
    "4단원: 좌표와 그래프": {
        "icon": "📊",
        "topics": [
            {"day": 1, "title": "순서쌍과 좌표", "emoji": "📌"},
            {"day": 2, "title": "사분면", "emoji": "📌"},
            {"day": 3, "title": "그래프 읽기", "emoji": "📌"},
            {"day": 4, "title": "정비례 관계", "emoji": "📌"},
            {"day": 5, "title": "반비례 관계", "emoji": "📌"},
            {"day": 6, "title": "정비례·반비례 활용", "emoji": "📌"},
        ]
    },
    "5단원: 기본 도형": {
        "icon": "📐",
        "topics": [
            {"day": 1, "title": "점, 선, 면, 각", "emoji": "📌"},
            {"day": 2, "title": "직선, 반직선, 선분", "emoji": "📌"},
            {"day": 3, "title": "각도와 맞꼭지각", "emoji": "📌"},
            {"day": 4, "title": "평행선과 동위각·엇각", "emoji": "📌"},
            {"day": 5, "title": "위치 관계", "emoji": "📌"},
            {"day": 6, "title": "작도와 합동", "emoji": "📌"},
        ]
    },
    "6단원: 평면도형": {
        "icon": "🔷",
        "topics": [
            {"day": 1, "title": "다각형의 내각과 외각", "emoji": "📌"},
            {"day": 2, "title": "삼각형의 내각의 합", "emoji": "📌"},
            {"day": 3, "title": "원과 부채꼴", "emoji": "📌"},
            {"day": 4, "title": "부채꼴의 호와 넓이", "emoji": "📌"},
            {"day": 5, "title": "다각형의 넓이", "emoji": "📌"},
            {"day": 6, "title": "평면도형 활용 문제", "emoji": "📌"},
        ]
    },
    "7단원: 입체도형": {
        "icon": "🧊",
        "topics": [
            {"day": 1, "title": "다면체", "emoji": "📌"},
            {"day": 2, "title": "정다면체", "emoji": "📌"},
            {"day": 3, "title": "회전체", "emoji": "📌"},
            {"day": 4, "title": "기둥의 겉넓이와 부피", "emoji": "📌"},
            {"day": 5, "title": "뿔의 겉넓이와 부피", "emoji": "📌"},
            {"day": 6, "title": "구의 겉넓이와 부피", "emoji": "📌"},
        ]
    },
    "8단원: 통계": {
        "icon": "📈",
        "topics": [
            {"day": 1, "title": "줄기와 잎 그림", "emoji": "📌"},
            {"day": 2, "title": "도수분포표", "emoji": "📌"},
            {"day": 3, "title": "히스토그램", "emoji": "📌"},
            {"day": 4, "title": "도수분포다각형", "emoji": "📌"},
            {"day": 5, "title": "상대도수", "emoji": "📌"},
            {"day": 6, "title": "통계 자료 해석", "emoji": "📌"},
        ]
    },
}

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

    elif mode == "quiz":
        return f"""{base}

지금 모드: 확인 문제 풀기
단원: {unit}
주제: {topic}

학생이 문제 풀다가 막힐 때 힌트를 주세요.
- 힌트는 단계별로 조금씩 알려주세요.
- 정답을 바로 알려주지 말고 스스로 풀도록 유도하세요."""

    else:  # free
        return f"""{base}

지금 모드: 자유 질문
중학교 1학년 수학 전 범위에 대해 질문에 답하세요.
모르는 내용이나 헷갈리는 개념 모두 편하게 질문받으세요."""


# ── 세션 상태 초기화 ──────────────────────────────────────────
def init_session():
    defaults = {
        "api_key": "",
        "messages": [],          # 채팅 히스토리
        "mode": "daily",         # daily / quiz / free
        "selected_unit": list(UNITS.keys())[0],
        "selected_day": 1,
        "lesson_started": False,
        "client": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_session()

# ── Anthropic 클라이언트 생성 ─────────────────────────────────
def get_client():
    if st.session_state.api_key:
        return anthropic.Anthropic(api_key=st.session_state.api_key)
    return None

# ── AI 응답 생성 ──────────────────────────────────────────────
def get_ai_response(user_message: str, system_prompt: str) -> str:
    client = get_client()
    if not client:
        return "⚠️ API 키를 먼저 입력해 주세요!"

    # 메시지 히스토리 구성 (최근 10개만)
    history = st.session_state.messages[-10:]
    messages = []
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})
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


# ── 오늘의 학습 자동 시작 메시지 ─────────────────────────────
def start_daily_lesson(unit: str, day: int):
    unit_data = UNITS[unit]
    topic_data = unit_data["topics"][day - 1]
    topic = topic_data["title"]

    system_prompt = get_system_prompt("daily", unit, topic)
    trigger = f"{unit} {day}일차 '{topic}' 학습을 시작해주세요."

    with st.spinner("선생님이 준비 중이에요... ✏️"):
        ai_msg = get_ai_response(trigger, system_prompt)

    st.session_state.messages = []  # 새 학습 시작 시 초기화
    st.session_state.messages.append({"role": "user", "content": trigger})
    st.session_state.messages.append({"role": "assistant", "content": ai_msg})
    st.session_state.lesson_started = True
    st.rerun()


# ════════════════════════════════════════════════════════════
# ── 사이드바 ─────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 📐 중1 수학 AI 선생님")
    st.markdown("---")

    # API 키 입력
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

    # 모드 선택
    st.markdown("### 📚 학습 모드 선택")
    mode_options = {
        "📅 오늘의 학습": "daily",
        "❓ 자유 질문": "free"
    }
    selected_mode_label = st.radio(
        "모드",
        list(mode_options.keys()),
        label_visibility="collapsed"
    )
    new_mode = mode_options[selected_mode_label]
    if new_mode != st.session_state.mode:
        st.session_state.mode = new_mode
        st.session_state.messages = []
        st.session_state.lesson_started = False

    st.markdown("---")

    # 단원 + 일차 선택 (오늘의 학습 모드일 때만)
    if st.session_state.mode == "daily":
        st.markdown("### 📖 단원 선택")
        selected_unit = st.selectbox(
            "단원",
            list(UNITS.keys()),
            index=list(UNITS.keys()).index(st.session_state.selected_unit),
            label_visibility="collapsed"
        )
        if selected_unit != st.session_state.selected_unit:
            st.session_state.selected_unit = selected_unit
            st.session_state.messages = []
            st.session_state.lesson_started = False

        st.markdown("### 📆 일차 선택")
        max_day = len(UNITS[st.session_state.selected_unit]["topics"])
        selected_day = st.selectbox(
            "일차",
            list(range(1, max_day + 1)),
            index=st.session_state.selected_day - 1,
            format_func=lambda d: f"{d}일차 - {UNITS[st.session_state.selected_unit]['topics'][d-1]['title']}",
            label_visibility="collapsed"
        )
        if selected_day != st.session_state.selected_day:
            st.session_state.selected_day = selected_day
            st.session_state.messages = []
            st.session_state.lesson_started = False

        st.markdown("---")

        # 학습 시작 버튼
        unit_icon = UNITS[st.session_state.selected_unit]["icon"]
        topic_name = UNITS[st.session_state.selected_unit]["topics"][st.session_state.selected_day - 1]["title"]
        st.markdown(f"**{unit_icon} {topic_name}**")

        if st.button("🚀 학습 시작!", use_container_width=True):
            if not st.session_state.api_key:
                st.error("API 키를 먼저 입력해 주세요!")
            else:
                start_daily_lesson(
                    st.session_state.selected_unit,
                    st.session_state.selected_day
                )

    st.markdown("---")

    # 대화 초기화 버튼
    if st.button("🗑️ 대화 초기화", use_container_width=True):
        st.session_state.messages = []
        st.session_state.lesson_started = False
        st.rerun()

    st.markdown("---")
    st.markdown(
        "<small style='opacity:0.7'>Made with ❤️ for 중1 students<br>Model: claude-sonnet-4-5</small>",
        unsafe_allow_html=True
    )


# ════════════════════════════════════════════════════════════
# ── 메인 화면 ─────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════

# 헤더
if st.session_state.mode == "daily":
    unit = st.session_state.selected_unit
    day = st.session_state.selected_day
    topic = UNITS[unit]["topics"][day - 1]["title"]
    unit_icon = UNITS[unit]["icon"]
    today = datetime.now().strftime("%Y년 %m월 %d일")
    st.markdown(f"""
    <div class="header-card">
        <h1>{unit_icon} 오늘의 수학 학습</h1>
        <p>📅 {today} &nbsp;|&nbsp; 📖 {unit} &nbsp;|&nbsp; 🗓️ {day}일차: {topic}</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="header-card">
        <h1>💬 자유 질문 코너</h1>
        <p>중1 수학 어떤 것이든 물어보세요! 선생님이 답해드려요 😊</p>
    </div>
    """, unsafe_allow_html=True)


# ── 오늘의 학습 모드: 시작 전 안내 ───────────────────────────
if st.session_state.mode == "daily" and not st.session_state.lesson_started:
    unit = st.session_state.selected_unit
    day = st.session_state.selected_day
    topics = UNITS[unit]["topics"]
    unit_icon = UNITS[unit]["icon"]

    st.markdown(f"""
    <div class="lesson-card">
        <h3>{unit_icon} {unit}</h3>
        <p>오늘은 <b>{day}일차</b> 학습입니다!</p>
    </div>
    """, unsafe_allow_html=True)

    # 전체 커리큘럼 미리보기
    cols = st.columns(3)
    for i, t in enumerate(topics):
        with cols[i % 3]:
            is_today = (t["day"] == day)
            border = "border: 2px solid #3949ab;" if is_today else ""
            bg = "background:#e8eaf6;" if is_today else "background:white;"
            st.markdown(f"""
            <div style="{bg}{border}border-radius:10px;padding:10px 14px;margin:4px 0;
                         box-shadow:0 1px 4px rgba(0,0,0,0.08);">
                <b style="color:#1a237e;">{t['day']}일차</b>
                {'<span class="badge">오늘</span>' if is_today else ''}<br>
                <span style="font-size:0.9rem;">{t['title']}</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.info("👈 왼쪽 사이드바에서 **🚀 학습 시작!** 버튼을 눌러 시작하세요!")


# ── 자유 질문 모드: 안내 문구 ─────────────────────────────────
if st.session_state.mode == "free" and not st.session_state.messages:
    col1, col2, col3 = st.columns(3)
    examples = [
        ("🔢", "소인수분해가 뭐예요?"),
        ("➕", "음수 곱하기 음수는 왜 양수예요?"),
        ("📐", "맞꼭지각이 뭐예요?"),
    ]
    for col, (icon, text) in zip([col1, col2, col3], examples):
        with col:
            st.markdown(f"""
            <div class="lesson-card" style="text-align:center;cursor:pointer;">
                <div style="font-size:2rem;">{icon}</div>
                <p style="margin:4px 0;font-size:0.9rem;color:#3949ab;"><b>예시 질문</b></p>
                <p style="margin:0;font-size:0.85rem;">"{text}"</p>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)


# ── 채팅 히스토리 출력 ────────────────────────────────────────
chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            # 학습 시작 트리거 메시지는 숨김
            if "학습을 시작해주세요" in msg["content"]:
                continue
            st.markdown(f"""
            <div style="display:flex;justify-content:flex-end;margin:6px 0;">
                <div class="chat-user">🙋 {msg['content']}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="display:flex;justify-content:flex-start;margin:6px 0;">
                <div style="font-size:1.5rem;margin-right:8px;">👩‍🏫</div>
                <div class="chat-ai">{msg['content']}</div>
            </div>
            """, unsafe_allow_html=True)


# ── 채팅 입력 ─────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)

# 모드별 placeholder
if st.session_state.mode == "daily":
    placeholder = "답을 입력하거나, 모르는 부분을 물어보세요! 💬"
else:
    placeholder = "중1 수학 궁금한 것 뭐든지 물어보세요! 💬"

# 입력폼 (Enter로 전송)
with st.form(key="chat_form", clear_on_submit=True):
    col_input, col_btn = st.columns([5, 1])
    with col_input:
        user_input = st.text_input(
            "메시지",
            placeholder=placeholder,
            label_visibility="collapsed"
        )
    with col_btn:
        submitted = st.form_submit_button("전송 ✈️", use_container_width=True)

if submitted and user_input.strip():
    if not st.session_state.api_key:
        st.error("⚠️ 먼저 API 키를 입력해 주세요!")
    else:
        # 시스템 프롬프트 결정
        if st.session_state.mode == "daily":
            unit = st.session_state.selected_unit
            topic = UNITS[unit]["topics"][st.session_state.selected_day - 1]["title"]
            system_prompt = get_system_prompt("daily", unit, topic)
        else:
            system_prompt = get_system_prompt("free")

        # 유저 메시지 저장
        st.session_state.messages.append({
            "role": "user",
            "content": user_input.strip()
        })

        # AI 응답
        with st.spinner("선생님이 답변 중... ✏️"):
            ai_response = get_ai_response(user_input.strip(), system_prompt)

        st.session_state.messages.append({
            "role": "assistant",
            "content": ai_response
        })
        st.rerun()


# ── 하단 진행 상황 (오늘의 학습 모드) ────────────────────────
if st.session_state.mode == "daily" and st.session_state.lesson_started:
    st.markdown("---")
    msg_count = len([m for m in st.session_state.messages if m["role"] == "user"])
    unit = st.session_state.selected_unit
    total_days = len(UNITS[unit]["topics"])
    progress = st.session_state.selected_day / total_days

    st.markdown(f"**{unit} 진행도** ({st.session_state.selected_day}/{total_days}일차)")
    st.progress(progress)
    st.caption(f"💬 이번 학습 대화 수: {msg_count}회")