import streamlit as st
import os
from typing import TypedDict, Annotated, Sequence, Dict, Any
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import StateGraph, END
import operator
from datetime import datetime
import json

# 데이터 임포트
from sample_data import SAMPLE_REVIEWS, SAMPLE_INTERVIEWS, TOURISM_INFO
from enhanced_data import (
    ACCOMMODATION_DATA, RESTAURANT_DATA, ATTRACTION_DATA,
    PACKAGE_TEMPLATES, SEASONAL_RECOMMENDATIONS
)

# 페이지 설정
st.set_page_config(
    page_title="강원도 관광 AI 컨시어지",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API 키 가져오기 (Streamlit Cloud secrets 또는 환경 변수)
def get_api_key():
    """API 키를 Streamlit secrets 또는 환경 변수에서 가져오기"""
    try:
        # Streamlit Cloud secrets 시도
        return st.secrets["OPENAI_API_KEY"]
    except:
        # 환경 변수 시도
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if api_key:
            return api_key
        return None

# 커스텀 CSS
st.markdown("""
<style>
.stButton>button {
    width: 100%;
}
.price-box {
    background-color: #f0f2f6;
    padding: 20px;
    border-radius: 10px;
    margin: 10px 0;
}
.recommendation-card {
    border: 1px solid #ddd;
    padding: 15px;
    border-radius: 8px;
    margin: 10px 0;
    background-color: white;
}
.info-banner {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
    text-align: center;
}
.metric-card {
    background-color: #f8f9fa;
    padding: 15px;
    border-radius: 8px;
    border-left: 4px solid #667eea;
}
</style>
""", unsafe_allow_html=True)

# 상태 정의
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    user_query: str
    context: str
    response: str
    price_estimate: Dict[str, Any]
    itinerary: Dict[str, Any]

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
if "search_filters" not in st.session_state:
    st.session_state.search_filters = {}
if "generated_itinerary" not in st.session_state:
    st.session_state.generated_itinerary = None
if "price_comparison" not in st.session_state:
    st.session_state.price_comparison = None

# API 키 확인
API_KEY = get_api_key()

# 상단 배너
st.markdown("""
<div class='info-banner'>
    <h1>🏔️ 강원도 관광 AI 컨시어지</h1>
    <p>관광업 전문가 설문 기반 · 가격 견적 · 일정표 생성 · 실시간 필터링</p>
</div>
""", unsafe_allow_html=True)

# 사이드바
with st.sidebar:
    st.title("⚙️ 설정")
    
    # API 키 상태 표시
    if API_KEY:
        st.success("✅ API 키가 설정되었습니다")
    else:
        st.error("⚠️ API 키가 필요합니다")
        st.info("""
        **로컬 테스트용**
        
        1. `.streamlit/secrets.toml` 파일 생성
        2. 아래 내용 추가:
        ```
        OPENAI_API_KEY = "your-key-here"
        ```
        
        **Streamlit Cloud 배포 시**
        
        앱 설정 → Secrets에서 설정
        """)
    
    st.divider()
    
    # 모델 설정
    model_choice = st.selectbox(
        "AI 모델",
        ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
        index=0,
        help="gpt-4o-mini 권장 (속도와 비용 최적화)"
    )
    
    temperature = st.slider(
        "응답 창의성",
        0.0, 1.0, 0.7, 0.1,
        help="낮을수록 일관적, 높을수록 창의적"
    )
    
    st.divider()
    
    # 검색 필터
    st.subheader("🔍 검색 필터")
    
    region_filter = st.multiselect(
        "지역",
        ["춘천", "강릉", "속초", "평창", "전체"],
        default=["전체"]
    )
    
    price_range = st.slider(
        "1박 가격대 (만원)",
        0, 50, (0, 50),
        help="숙박 시설 가격 범위"
    )
    
    room_type_filter = st.multiselect(
        "객실 타입",
        ["스탠다드", "디럭스", "스위트", "패밀리", "오션뷰"],
        help="원하는 객실 타입 선택"
    )
    
    meal_filter = st.checkbox("조식 포함만", value=False)
    parking_filter = st.checkbox("주차 가능만", value=False)
    
    st.session_state.search_filters = {
        "region": region_filter,
        "price_range": price_range,
        "room_type": room_type_filter,
        "meal_included": meal_filter,
        "parking": parking_filter
    }
    
    st.divider()
    
    # 통계 정보
    st.subheader("📊 데이터 정보")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("숙소", f"{len(ACCOMMODATION_DATA)}개")
        st.metric("맛집", f"{len(RESTAURANT_DATA)}개")
    with col2:
        st.metric("관광지", f"{len(ATTRACTION_DATA)}개")
        st.metric("패키지", f"{len(PACKAGE_TEMPLATES)}개")
    
    st.divider()
    st.caption("강원대학교 학생창의자율과제 7팀")

# 헬퍼 함수들
def filter_accommodations(filters):
    """필터 조건에 맞는 숙소 검색"""
    results = []
    
    for acc in ACCOMMODATION_DATA:
        try:
            # 지역 필터
            if filters["region"] and "전체" not in filters["region"]:
                location = acc.get("location", "")
                location_match = any(region in location for region in filters["region"])
                if not location_match:
                    continue
            
            # 가격 필터
            price_per_night = acc.get("price_per_night", {})
            if not price_per_night:
                continue
            min_price = min(price_per_night.values())
            max_price = max(price_per_night.values())
            price_min, price_max = filters["price_range"]
            if not (price_min * 10000 <= min_price <= price_max * 10000):
                continue
            
            # 조식 필터
            if filters["meal_included"]:
                meals = acc.get("meals", {})
                if not meals.get("breakfast_included", False):
                    continue
            
            # 주차 필터
            if filters["parking"]:
                facilities = acc.get("facilities", [])
                if "주차장" not in str(facilities):
                    continue
            
            results.append(acc)
        except Exception as e:
            # 데이터 오류가 있는 항목은 건너뜀
            continue
    
    return results

def calculate_trip_cost(duration, num_people, accommodation_type="standard"):
    """여행 비용 견적 계산"""
    costs = {
        "accommodation": 0,
        "meals": 0,
        "attractions": 0,
        "transportation": 0,
        "total": 0
    }
    
    nights = int(duration.split("박")[0]) if "박" in duration else 1
    
    if accommodation_type == "budget":
        costs["accommodation"] = 80000 * nights
    elif accommodation_type == "standard":
        costs["accommodation"] = 150000 * nights
    elif accommodation_type == "luxury":
        costs["accommodation"] = 300000 * nights
    
    days = nights + 1
    costs["meals"] = 30000 * num_people * days
    costs["attractions"] = 15000 * num_people * days
    costs["transportation"] = 50000 * num_people
    
    costs["total"] = sum(costs.values())
    costs["per_person"] = costs["total"] / num_people if num_people > 0 else 0
    
    return costs

def generate_itinerary_text(package):
    """일정표 텍스트 생성"""
    text = f"## {package['name']}\n\n"
    text += f"**기간**: {package['duration']} | **인원**: {package['group_size']}명\n\n"
    text += f"**총 비용**: {package['total_cost']:,}원 (1인당 {package['cost_per_person']:,}원)\n\n"
    
    for day_info in package['itinerary']:
        text += f"\n### Day {day_info['day']}\n\n"
        # 'activities' 대신 'schedule'을 사용하고, 내부 키들도 수정합니다.
        for item in day_info['schedule']:
            cost_text = f"{item['cost']:,}원" if item['cost'] > 0 else "무료"
            notes_text = f" ({item['notes']})" if item['notes'] else ""
            text += f"- **{item['time']}** | {item['activity']} - {cost_text}{notes_text}\n"
    
    # 구분선 스타일도 통일합니다.
    text += f"\n\n**포함 사항**: {', '.join(package['included'])}\n"
    text += f"**불포함 사항**: {', '.join(package['excluded'])}\n"
    
    return text

def create_workflow(api_key, model_name, temp, filters):
    """LangGraph 워크플로우 생성 - proxies 오류 수정 버전"""
    
    # 🔧 수정: 환경 변수로 API 키 설정 (전역)
    os.environ["OPENAI_API_KEY"] = api_key
    
    # 🔧 수정: 파라미터 없이 초기화 (환경 변수 자동 사용)
    llm = ChatOpenAI(
        model_name=model_name,
        temperature=temp
    )
    
    # 🔧 수정: OpenAIEmbeddings도 파라미터 최소화
    embeddings = OpenAIEmbeddings()
    
    # 컨텍스트 데이터 준비
    all_docs = []
    
    # 숙소 데이터
    filtered_accs = filter_accommodations(filters)
    for acc in filtered_accs:
        # 가격 정보 안전하게 처리
        price_info = acc.get('price_per_night', {})
        price_text = chr(10).join([f'- {rt}: {p:,}원' for rt, p in price_info.items()]) if price_info else '가격 정보 없음'
        
        # 식사 정보 안전하게 처리
        meals = acc.get('meals', {})
        meal_text = '포함 (뷔페)' if meals.get('breakfast_included', False) else f'별도 ({meals.get("breakfast_price", 0):,}원)'
        
        # 시설 정보 안전하게 처리
        facilities_text = ', '.join(acc.get('facilities', []))
        
        # 주변 명소 안전하게 처리
        attractions = acc.get('distance_to_attractions', {})
        attractions_text = chr(10).join([f'- {place}: {dist}' for place, dist in attractions.items()]) if attractions else '정보 없음'
        
        doc_text = f"""
숙소명: {acc.get('name', '이름 없음')}
위치: {acc.get('location', '위치 정보 없음')}
평점: {acc.get('rating', 'N/A')}
청결도: {acc.get('cleanliness_score', 'N/A')}/5.0
최근 예약: {acc.get('recent_bookings', 0)}건

가격 (1박):
{price_text}

조식: {meal_text}

시설: {facilities_text}

주변 명소:
{attractions_text}
"""
        all_docs.append(doc_text)
    
    # 맛집 데이터
    for rest in RESTAURANT_DATA:
        doc_text = f"""
맛집: {rest.get('name', '이름 없음')}
위치: {rest.get('location', '위치 정보 없음')}
평점: {rest.get('rating', 'N/A')}
영업시간: {rest.get('hours', '영업시간 정보 없음')}
가격대: {rest.get('price_range', '가격 정보 없음')}
주차: {'가능' if rest.get('parking', False) else '불가'}
인기메뉴: {', '.join(rest.get('popular_dishes', []))}
분위기: {rest.get('atmosphere', '정보 없음')}
"""
        all_docs.append(doc_text)
    
    # 관광지 데이터
    for attr in ATTRACTION_DATA:
        doc_text = f"""
관광지: {attr.get('name', '이름 없음')}
위치: {attr.get('location', '위치 정보 없음')}
평점: {attr.get('rating', 'N/A')}
입장료: {attr.get('entry_fee', '정보 없음')}
운영시간: {attr.get('hours', '운영시간 정보 없음')}
소요시간: {attr.get('time_needed', '정보 없음')}
계절추천: {', '.join(attr.get('best_seasons', []))}
"""
        all_docs.append(doc_text)
    
    # 벡터스토어 생성
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    splits = text_splitter.create_documents(all_docs)
    
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embeddings
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    
    def retrieve_context(state: AgentState):
        """컨텍스트 검색"""
        query = state["user_query"]
        docs = retriever.get_relevant_documents(query)
        context = "\n\n".join([doc.page_content for doc in docs])
        return {"context": context}
    
    def generate_response(state: AgentState):
        """응답 생성"""
        context = state.get("context", "")
        messages = state["messages"]
        
        system_prompt = f"""당신은 강원도 관광 및 숙박 전문 AI 컨시어지입니다.

**설문 결과 반영 - 반드시 포함해야 할 정보:**
1. 가격 정보 (가장 중요!)
2. 위치 및 거리 정보
3. 객실 타입 및 수용 인원
4. 식사 포함 여부
5. 주차 가능 여부
6. 청결도 및 시설 정보
7. 최근 예약 사례

**컨텍스트:**
{context}

**답변 가이드라인:**
- 숙소 추천 시: 가격(필수), 위치, 객실 타입, 식사, 주차, 청결도 점수를 모두 포함
- 맛집 추천 시: 가격대, 위치, 주차 정보, 운영 시간, 인기 메뉴 포함
- 여행 코스: 동선을 고려한 효율적인 일정, 이동 거리와 시간 명시
- 견적: 구체적인 금액과 항목별 비용 분석
- 출처: 리뷰 데이터 또는 실제 예약 사례 기반임을 명시

**응답 형식:**
- 요청에 맞는 구체적 정보 제공
- 가격은 반드시 명시 (예: 120,000원/박)
- 거리는 km + 이동 시간 표시 (예: 5km, 차로 10분)
- 신뢰도 향상을 위해 최근 예약 건수나 리뷰 점수 언급"""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages")
        ])
        
        chain = prompt | llm
        response = chain.invoke({"messages": messages})
        
        return {
            "response": response.content,
            "messages": [AIMessage(content=response.content)]
        }
    
    workflow = StateGraph(AgentState)
    workflow.add_node("retrieve", retrieve_context)
    workflow.add_node("generate", generate_response)
    workflow.set_entry_point("retrieve")
    workflow.add_edge("retrieve", "generate")
    workflow.add_edge("generate", END)
    
    return workflow.compile()

# 메인 UI - 탭 구성
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💬 AI 상담", 
    "💰 견적 계산기", 
    "📋 일정표 생성", 
    "🏨 숙소 검색",
    "📊 가격 비교"
])

with tab1:
    st.subheader("💬 AI 채팅 상담")
    
    # 빠른 질문 버튼
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("💰 가격 문의", use_container_width=True):
            st.session_state.quick_query = "춘천 1박 2일 가족 여행 예상 비용 알려줘"
    with col2:
        if st.button("🏨 숙소 추천", use_container_width=True):
            st.session_state.quick_query = "강릉에서 바다 보이는 숙소 추천해줘. 가격과 시설 정보도 알려줘"
    with col3:
        if st.button("📅 일정 짜기", use_container_width=True):
            st.session_state.quick_query = "춘천 1박 2일 여행 일정 짜줘. 가격도 함께 알려줘"
    
    # 대화 내역
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # ----------------- ⬇️ 로직 수정 ⬇️ -----------------

    # 1. st.chat_input을 항상 렌더링하여 화면 하단에 고정시킵니다.
    chat_prompt = st.chat_input("예: '춘천에서 1박 2일 가족 여행 가격 얼마나 들어? 숙소도 추천해줘'")
    
    # 2. 버튼 클릭(빠른 질문)을 별도로 처리합니다.
    button_prompt = None
    if hasattr(st.session_state, 'quick_query'):
        button_prompt = st.session_state.quick_query
        del st.session_state.quick_query # 처리 후 즉시 삭제

    # 3. 버튼 입력(button_prompt) 또는 채팅 입력(chat_prompt) 중 하나를 실제 프롬프트로 사용합니다.
    prompt = button_prompt or chat_prompt

    # ----------------- ⬆️ 로직 수정 ⬆️ -----------------

    if prompt:
        if not API_KEY:
            st.error("⚠️ API 키가 설정되지 않았습니다. 사이드바를 확인해주세요.")
        else:
            # 4. (중요) 어떤 입력이든(버튼/채팅) 사용자 메시지를 화면과 기록에 추가
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                # RAG 검색 및 컨텍스트 생성 중 스피너 표시
                with st.spinner("💭 관련 정보를 검색 중..."):
                    try:
                        # (이전 답변의 스트리밍 로직과 동일)
                        
                        # 1. LLM 및 임베딩 초기화
                        os.environ["OPENAI_API_KEY"] = API_KEY
                        llm = ChatOpenAI(model_name=model_choice, temperature=temperature)
                        embeddings = OpenAIEmbeddings()

                        # 2. Retriever 생성 (필터링된 데이터 기반)
                        all_docs = []
                        
                        # 숙소 데이터 (필터링됨)
                        filtered_accs = filter_accommodations(st.session_state.search_filters)
                        for acc in filtered_accs:
                            price_info = acc.get('price_per_night', {})
                            price_text = chr(10).join([f'- {rt}: {p:,}원' for rt, p in price_info.items()]) if price_info else '가격 정보 없음'
                            meals = acc.get('meals', {})
                            meal_text = '포함 (뷔페)' if meals.get('breakfast_included', False) else f'별도 ({meals.get("breakfast_price", 0):,}원)'
                            facilities_text = ', '.join(acc.get('facilities', []))
                            attractions = acc.get('distance_to_attractions', {})
                            attractions_text = chr(10).join([f'- {place}: {dist}' for place, dist in attractions.items()]) if attractions else '정보 없음'
                            
                            all_docs.append(f"""
숙소명: {acc.get('name', '이름 없음')}
위치: {acc.get('location', '위치 정보 없음')}
평점: {acc.get('rating', 'N/A')}
청결도: {acc.get('cleanliness_score', 'N/A')}/5.0
최근 예약: {acc.get('recent_bookings', 0)}건
가격 (1박):
{price_text}
조식: {meal_text}
시설: {facilities_text}
주변 명소:
{attractions_text}
""")
                        
                        # 맛집 데이터
                        for rest in RESTAURANT_DATA:
                            all_docs.append(f"""
맛집: {rest.get('name', '이름 없음')}
위치: {rest.get('location', '위치 정보 없음')}
평점: {rest.get('rating', 'N/A')}
영업시간: {rest.get('hours', '영업시간 정보 없음')}
가격대: {rest.get('price_range', '가격 정보 없음')}
주차: {'가능' if rest.get('parking', False) else '불가'}
인기메뉴: {', '.join(rest.get('popular_dishes', []))}
분위기: {rest.get('atmosphere', '정보 없음')}
""")
                        
                        # 관광지 데이터
                        for attr in ATTRACTION_DATA:
                            all_docs.append(f"""
관광지: {attr.get('name', '이름 없음')}
위치: {attr.get('location', '위치 정보 없음')}
평점: {attr.get('rating', 'N/A')}
입장료: {attr.get('entry_fee', '정보 없음')}
운영시간: {attr.get('hours', '운영시간 정보 없음')}
소요시간: {attr.get('time_needed', '정보 없음')}
계절추천: {', '.join(attr.get('best_seasons', []))}
""")
                        
                        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                        splits = text_splitter.create_documents(all_docs)
                        vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
                        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

                        # 3. 컨텍스트 검색
                        docs = retriever.get_relevant_documents(prompt)
                        context = "\n\n".join([doc.page_content for doc in docs])

                        # 4. 프롬프트 생성
                        system_prompt = f"""당신은 강원도 관광 및 숙박 전문 AI 컨시어지입니다.

**설문 결과 반영 - 반드시 포함해야 할 정보:**
1. 가격 정보 (가장 중요!)
2. 위치 및 거리 정보
3. 객실 타입 및 수용 인원
4. 식사 포함 여부
5. 주차 가능 여부
6. 청결도 및 시설 정보
7. 최근 예약 사례

**컨텍스트:**
{context}

**답변 가이드라인:**
- 숙소 추천 시: 가격(필수), 위치, 객실 타입, 식사, 주차, 청결도 점수를 모두 포함
- 맛집 추천 시: 가격대, 위치, 주차 정보, 운영 시간, 인기 메뉴 포함
- 여행 코스: 동선을 고려한 효율적인 일정, 이동 거리와 시간 명시
- 견적: 구체적인 금액과 항목별 비용 분석
- 출처: 리뷰 데이터 또는 실제 예약 사례 기반임을 명시

**응답 형식:**
- 요청에 맞는 구체적 정보 제공
- 가격은 반드시 명시 (예: 120,000원/박)
- 거리는 km + 이동 시간 표시 (예: 5km, 차로 10분)
- 신뢰도 향상을 위해 최근 예약 건수나 리뷰 점수 언급"""

                        prompt_template = ChatPromptTemplate.from_messages([
                            ("system", system_prompt),
                            MessagesPlaceholder(variable_name="messages")
                        ])
                        
                        chain = prompt_template | llm

                        # 5. 대화 기록 준비
                        chat_history = []
                        for msg in st.session_state.messages:
                            if msg["role"] == "user":
                                chat_history.append(HumanMessage(content=msg["content"]))
                            else:
                                chat_history.append(AIMessage(content=msg["content"]))

                        # 6. 🚀 st.write_stream을 사용하여 스트리밍 실행 (스피너는 여기서 사라짐)
                        response_stream = chain.stream({"messages": chat_history})
                        full_response = st.write_stream(response_stream)
                        
                        # 7. 스트리밍 완료 후 전체 응답을 세션 상태에 저장
                        st.session_state.messages.append({"role": "assistant", "content": full_response})
                        
                    except Exception as e:
                        st.error(f"❌ 오류: {str(e)}")
                        st.info("잠시 후 다시 시도해주세요.")

with tab2:
    st.subheader("💰 여행 비용 견적 계산기")
    st.info("💡 **설문 결과**: 가격 문의가 83%로 가장 많습니다. 자동 견적을 확인하세요!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        duration = st.selectbox("여행 기간", ["1박 2일", "2박 3일", "3박 4일"])
        num_people = st.number_input("인원 수", 1, 10, 4)
        acc_type = st.selectbox(
            "숙박 등급",
            ["budget", "standard", "luxury"],
            format_func=lambda x: {"budget": "저렴 (8만원대)", "standard": "일반 (15만원대)", "luxury": "고급 (30만원대)"}[x]
        )
    
    with col2:
        if st.button("💵 견적 계산하기", use_container_width=True):
            costs = calculate_trip_cost(duration, num_people, acc_type)
            st.session_state.price_comparison = costs
            
            st.markdown(f"""
            <div class='price-box'>
            <h3>📊 예상 비용</h3>
            <ul>
            <li><strong>숙박비</strong>: {costs['accommodation']:,}원</li>
            <li><strong>식비</strong>: {costs['meals']:,}원</li>
            <li><strong>입장료</strong>: {costs['attractions']:,}원</li>
            <li><strong>교통비</strong>: {costs['transportation']:,}원</li>
            </ul>
            <hr>
            <h2>총 {costs['total']:,}원</h2>
            <p>1인당 약 {costs['per_person']:,}원</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.success("✅ 견적이 계산되었습니다!")

with tab3:
    st.subheader("📋 맞춤 일정표 자동 생성")
    st.info("💡 **설문 결과**: 일정표 자동 작성이 59%로 가장 필요한 기능입니다!")
    
    package_choice = st.selectbox(
        "패키지 선택",
        range(len(PACKAGE_TEMPLATES)),
        format_func=lambda x: PACKAGE_TEMPLATES[x]['name']
    )
    
    if st.button("📄 일정표 생성", use_container_width=True):
        package = PACKAGE_TEMPLATES[package_choice]
        st.session_state.generated_itinerary = package
        
        itinerary_text = generate_itinerary_text(package)
        
        st.markdown(itinerary_text)
        
        st.download_button(
            label="📥 일정표 다운로드 (텍스트)",
            data=itinerary_text,
            file_name=f"{package['name']}_일정표.txt",
            mime="text/plain",
            use_container_width=True
        )
        
        st.success("✅ 일정표가 생성되었습니다!")

with tab4:
    st.subheader("🏨 숙소 실시간 검색")
    st.info("💡 **설문 결과**: 가격, 위치, 객실 타입, 식사 정보가 필수입니다!")
    
    filtered_results = filter_accommodations(st.session_state.search_filters)
    
    st.write(f"**검색 결과: {len(filtered_results)}개**")
    
    for acc in filtered_results:
        try:
            rating = acc.get('rating', 'N/A')
            name = acc.get('name', '이름 없음')
            location = acc.get('location', '위치 정보 없음')
            
            with st.expander(f"⭐ {rating} | {name} - {location}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**📍 위치**: {location}")
                    st.markdown(f"**🧹 청결도**: {acc.get('cleanliness_score', 'N/A')}/5.0")
                    st.markdown(f"**📅 최근 예약**: {acc.get('recent_bookings', 0)}건")
                    
                    st.markdown("**💰 가격 (1박 기준)**")
                    price_per_night = acc.get('price_per_night', {})
                    for room_type, price in price_per_night.items():
                        st.write(f"  - {room_type}: {price:,}원")
                    
                    meals = acc.get('meals', {})
                    breakfast_text = '포함 (뷔페)' if meals.get('breakfast_included', False) else f'별도 ({meals.get("breakfast_price", 0):,}원)'
                    st.markdown(f"**🍽️ 조식**: {breakfast_text}")
                    
                    facilities = acc.get('facilities', [])
                    st.markdown(f"**🎯 시설**: {', '.join(facilities[:5])}")
                    
                with col2:
                    st.markdown("**🚗 주변 명소**")
                    attractions = acc.get('distance_to_attractions', {})
                    for place, dist in list(attractions.items())[:3]:
                        st.write(f"{place}: {dist}")
        except Exception as e:
            st.error(f"숙소 정보 표시 오류: {str(e)}")

with tab5:
    st.subheader("📊 숙소 가격 비교")
    st.info("💡 **설문 결과**: 신뢰를 위해 가격 비교 정보가 중요합니다!")
    
    # 지역별 가격 비교
    regions = {}
    for acc in ACCOMMODATION_DATA:
        try:
            location = acc.get('location', '정보 없음')
            location_key = location.split()[0] if location else '기타'
            if location_key not in regions:
                regions[location_key] = []
            
            price_per_night = acc.get('price_per_night', {})
            if not price_per_night:
                continue
                
            min_price = min(price_per_night.values())
            regions[location_key].append({
                "name": acc.get('name', '이름 없음'),
                "min_price": min_price,
                "rating": acc.get('rating', 'N/A')
            })
        except Exception as e:
            continue
    
    for region, accs in regions.items():
        st.markdown(f"### 📍 {region}")
        for acc in sorted(accs, key=lambda x: x['min_price']):
            st.write(f"- **{acc['name']}**: {acc['min_price']:,}원/박 (평점 {acc['rating']})")
    
    st.divider()
    
    # 객실 타입별 가격
    st.markdown("### 🛏️ 객실 타입별 평균 가격")
    room_type_prices = {}
    for acc in ACCOMMODATION_DATA:
        try:
            price_per_night = acc.get('price_per_night', {})
            for room_type, price in price_per_night.items():
                if room_type not in room_type_prices:
                    room_type_prices[room_type] = []
                room_type_prices[room_type].append(price)
        except Exception as e:
            continue
    
    for room_type, prices in room_type_prices.items():
        if prices:
            avg_price = sum(prices) / len(prices)
            st.write(f"- **{room_type}**: 평균 {avg_price:,.0f}원 (최저 {min(prices):,}원 ~ 최고 {max(prices):,}원)")

# 푸터
st.divider()
st.markdown("""
<div style='text-align: center; padding: 20px; background-color: #f8f9fa; border-radius: 10px;'>
    <h4>🎯 설문 기반 고도화 기능</h4>
    <p>✅ 가격 정보 우선 제공 | ✅ 일정표 자동 생성 | ✅ 지역별 필터링 | ✅ 가격 비교 | ✅ 최근 예약 사례</p>
    <p style='color: gray; margin-top: 10px;'>강원대학교 학생창의자율과제 7팀 | Powered by LangGraph & OpenAI</p>
</div>
""", unsafe_allow_html=True)
