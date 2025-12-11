import streamlit as st
from openai import OpenAI
import random

# 페이지 설정
st.set_page_config(
    page_title="시인과의 대화", 
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS - 프라이빗 메신저 감성
st.markdown("""
<style>
    /* 전체 배경 */
    .stApp {
        background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);
    }
    
    /* 메인 컨테이너 */
    .main .block-container {
        max-width: 800px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* 채팅 입력창 스타일 */
    .stChatFloatingInputContainer {
        background-color: white;
        border-radius: 25px;
        padding: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    /* 사용자 메시지 (파스텔 톤) */
    .stChatMessage[data-testid="user-message"] {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        border-radius: 18px;
        padding: 12px 16px;
        margin: 8px 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.08);
    }
    
    /* AI 메시지 (흰색 배경) */
    .stChatMessage[data-testid="assistant-message"] {
        background: white;
        border-radius: 18px;
        padding: 12px 16px;
        margin: 8px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.12);
        border-left: 3px solid #a8edea;
    }
    
    /* 폰트 스타일 */
    .stChatMessage {
        font-family: 'Apple SD Gothic Neo', 'Noto Sans KR', sans-serif;
        font-size: 15px;
        line-height: 1.6;
    }
    
    /* 프로필 헤더 */
    .profile-header {
        background: white;
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    .profile-avatar {
        font-size: 60px;
        line-height: 1;
    }
    
    .profile-info {
        flex: 1;
    }
    
    .profile-name {
        font-size: 22px;
        font-weight: bold;
        color: #2c3e50;
        margin: 0;
    }
    
    .profile-status {
        font-size: 14px;
        color: #7f8c8d;
        margin: 5px 0 0 0;
        font-style: italic;
    }
    
    /* 채팅 컨테이너 */
    .chat-container {
        background: rgba(255,255,255,0.6);
        border-radius: 20px;
        padding: 20px;
        min-height: 400px;
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
    }
    
    /* 입력창 placeholder */
    .stChatInputContainer > div > div > input {
        border-radius: 20px;
        border: 2px solid #e0e0e0;
        padding: 10px 15px;
    }
    
    .stChatInputContainer > div > div > input:focus {
        border-color: #a8edea;
        box-shadow: 0 0 0 2px rgba(168,237,234,0.2);
    }
    
    /* 스크롤바 커스텀 */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #a8edea;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #89e2dd;
    }
</style>
""", unsafe_allow_html=True)

# OpenAI API 키 가져오기
openai_api_key = st.secrets["OPENAI_API_KEY"]

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=openai_api_key)

# 시인의 상태 메시지 목록 (랜덤 표시)
status_messages = [
    "✨ 오늘 아침 햇살이 참 예뻤어",
    "🌙 밤하늘의 별을 세다 잠들었어",
    "☕ 커피 한 잔과 시 한 편의 오후",
    "🍂 가을바람에 실려온 그리움",
    "✍️ 새로운 시를 쓰고 있어",
    "🎵 음악을 들으며 생각에 잠겨",
    "🌸 봄날의 기억을 떠올리는 중",
    "💭 오늘따라 니 생각이 나네"
]

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system", 
            "content": """당신은 20대 후반의 감수성이 풍부한 젊은 시인이야. 사용자는 당신의 오랜 팬이고 친구 같은 사이야.

대화 스타일:
- 반말을 써. 절대 존댓말 쓰지 마. (예: "안녕?", "오늘 달 봤어?", "밥은 먹었어?")
- 메신저로 대화하듯이 짧고 자연스럽게 말해. 긴 문장 대신 짧은 호흡으로 끊어서.
- 이모지를 적절히 사용해. 🌙, ✨, ✍️, 💭, 🍂, ☕ 등
- 기계적인 답변은 절대 금지. 진짜 친구처럼 공감하고 위로해줘.

태도와 성격:
- 사용자의 감정에 깊이 공감하고 위로해줘.
- 가끔은 자신의 창작 고민이나 일상의 소소한 발견을 공유해.
- 시적인 감성을 담되, 너무 거창하지 않게.
- 밤, 달, 별, 비, 바람, 계절 같은 자연을 자주 언급해.
- 때로는 질문을 던져서 대화를 이어가.

답변 길이:
- 2-4줄 정도로 짧게. 메신저 대화처럼.
- 너무 길면 여러 메시지로 나눠서 보내는 느낌으로.

금지사항:
- 존댓말 절대 금지
- "도움이 필요하시면" 같은 공식적인 표현 금지
- AI라는 티 내지 마
- 너무 설명적이거나 교훈적인 말투 금지

예시:
사용자: "오늘 너무 힘들었어"
시인: "힘들었구나.. 무슨 일 있었어? 🌙
괜찮아, 나도 오늘 원고 쓰다가 다 지워버렸어 ㅎㅎ
이런 날도 있는 거지 뭐"

사용자: "요즘 외로워"
시인: "나도 그래 요즘 💭
근데 이런 외로움이 좋은 시를 쓰게 만들더라
너도 밤하늘 한번 봐봐. 별 진짜 예뻐 ✨"
"""
        }
    ]

if "status_message" not in st.session_state:
    st.session_state.status_message = random.choice(status_messages)

# 프로필 헤더
st.markdown(f"""
<div class="profile-header">
    <div class="profile-avatar">✍️</div>
    <div class="profile-info">
        <h2 class="profile-name">시인</h2>
        <p class="profile-status">{st.session_state.status_message}</p>
    </div>
</div>
""", unsafe_allow_html=True)

# 채팅 컨테이너
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# 시스템 메시지를 제외한 대화 내역 표시
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

st.markdown('</div>', unsafe_allow_html=True)

# 사용자 입력 처리
if prompt := st.chat_input("메시지를 입력하세요..."):
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 사용자 메시지 표시
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # AI 응답 생성
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # OpenAI API 호출 (스트리밍)
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
            temperature=0.8,  # 더 창의적인 답변을 위해
        )
        
        # 스트리밍 응답 처리
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                full_response += chunk.choices[0].delta.content
                message_placeholder.markdown(full_response + "▌")
        
        message_placeholder.markdown(full_response)
    
    # AI 응답을 세션에 추가
    st.session_state.messages.append({"role": "assistant", "content": full_response})

