import streamlit as st
import os
from typing import TypedDict, Annotated, Sequence, Dict, Any
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.text_splitter import RecursiveCharacterTextSplitter
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
    st.caption("강원대학교 강원지능화혁신센터")

# 헬퍼 함수들
def filter_accommodations(filters):
    """필터 조건에 맞는 숙소 검색"""
    results = []
    
    for acc in ACCOMMODATION_DATA:
        # 지역 필터
        if filters["region"] and "전체" not in filters["region"]:
            location_match = any(region in acc["location"] for region in filters["region"])
            if not location_match:
                continue
        
        # 가격 필터
        min_price = min(acc["price_per_night"].values())
        max_price = max(acc["price_per_night"].values())
        price_min, price_max = filters["price_range"]
        if not (price_min * 10000 <= min_price <= price_max * 10000):
            continue
        
        # 조식 필터
        if filters["meal_included"] and not acc["meals"]["breakfast_included"]:
            continue
        
        # 주차 필터
        if filters["parking"] and "주차장" not in str(acc["facilities"]):
            continue
        
        results.append(acc)
    
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
        for item in day_info['schedule']:
            cost_text = f"{item['cost']:,}원" if item['cost'] > 0 else "무료"
            notes_text = f" ({item['notes']})" if item['notes'] else ""
            text += f"- **{item['time']}** | {item['activity']} - {cost_text}{notes_text}\n"
    
    text += f"\n\n**포함 사항**: {', '.join(package['included'])}\n"
    text += f"**불포함 사항**: {', '.join(package['excluded'])}\n"
    
    return text

# 벡터 스토어 초기화
@st.cache_resource
def initialize_vector_store(_api_key):
    """리뷰 및 모든 데이터를 벡터 스토어에 저장"""
    if not _api_key:
        return None
    
    texts = []
    
    # 리뷰 데이터
    for review in SAMPLE_REVIEWS:
        text = f"장소: {review['place_name']}, 카테고리: {review['category']}, 평점: {review['rating']}/5, 리뷰: {review['review_text']}"
        texts.append(text)
    
    # 인터뷰 데이터
    for interview in SAMPLE_INTERVIEWS:
        text = f"질문: {interview['question']}, 응답: {interview['answer']}"
        texts.append(text)
    
    # 숙소 데이터
    for acc in ACCOMMODATION_DATA:
        price_info = ", ".join([f"{k}: {v:,}원" for k, v in acc['price_per_night'].items()])
        text = f"숙소: {acc['name']}, 위치: {acc['location']}, 가격: {price_info}, 평점: {acc['rating']}, 청결도: {acc['cleanliness_score']}, 시설: {', '.join(acc['facilities'])}"
        texts.append(text)
    
    # 맛집 데이터
    for rest in RESTAURANT_DATA:
        text = f"맛집: {rest['name']}, 전문: {rest['specialty']}, 위치: {rest['location']}, 평균 가격: {rest['average_cost_per_person']:,}원, 평점: {rest['rating']}, 인기 메뉴: {', '.join(rest['popular_menu'])}"
        texts.append(text)
    
    # 관광지 데이터
    for attr in ATTRACTION_DATA:
        text = f"관광지: {attr['name']}, 위치: {attr['location']}, 입장료: {attr['entrance_fee']['adult']}원, 평점: {attr['rating']}, 추천 계절: {', '.join(attr['best_season'])}"
        texts.append(text)
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    splits = text_splitter.create_documents(texts)
    
    embeddings = OpenAIEmbeddings(api_key=_api_key)
    vector_store = Chroma.from_documents(documents=splits, embedding=embeddings)
    
    return vector_store

# LangGraph 워크플로우
def create_workflow(api_key, model_name, temp, filters):
    """고도화된 LangGraph 워크플로우 생성"""
    
    # llm = ChatOpenAI(model=model_name, temperature=temp, api_key=api_key)

        # 🔧 수정: 환경 변수로 API 키 설정
    os.environ["OPENAI_API_KEY"] = api_key
    
    # 🔧 수정: api_key 파라미터 제거
    llm = ChatOpenAI(
        model=model_name,
        temperature=temp
    )
    
    vector_store = initialize_vector_store(api_key)
    
    def retrieve_context(state: AgentState):
        """컨텍스트 검색"""
        query = state["user_query"]
        contexts = []
        
        if vector_store:
            docs = vector_store.similarity_search(query, k=5)
            contexts.extend([doc.page_content for doc in docs])
        
        filtered_accs = filter_accommodations(filters)
        if filtered_accs:
            for acc in filtered_accs[:3]:
                price_info = ", ".join([f"{k}: {v:,}원" for k, v in acc['price_per_night'].items()])
                contexts.append(
                    f"[추천 숙소] {acc['name']} - {acc['location']}, 가격: {price_info}, "
                    f"평점: {acc['rating']}, 최근 예약: {acc['recent_bookings']}건, "
                    f"시설: {', '.join(acc['facilities'][:3])}"
                )
        
        current_month = datetime.now().month
        if 3 <= current_month <= 5:
            season = "spring"
        elif 6 <= current_month <= 8:
            season = "summer"
        elif 9 <= current_month <= 11:
            season = "autumn"
        else:
            season = "winter"
        
        season_info = SEASONAL_RECOMMENDATIONS[season]
        contexts.append(
            f"[계절 추천] 현재는 {season}입니다. "
            f"추천 명소: {', '.join(season_info['attractions'])}, "
            f"날씨 팁: {season_info['weather_tip']}"
        )
        
        return {"context": "\n\n".join(contexts)}
    
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
    
    # 입력
    if hasattr(st.session_state, 'quick_query'):
        prompt = st.session_state.quick_query
        del st.session_state.quick_query
    else:
        prompt = st.chat_input("예: '춘천에서 1박 2일 가족 여행 가격 얼마나 들어? 숙소도 추천해줘'")
    
    if prompt:
        if not API_KEY:
            st.error("⚠️ API 키가 설정되지 않았습니다. 사이드바를 확인해주세요.")
        else:
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("💭 생각 중..."):
                    try:
                        app = create_workflow(
                            API_KEY, 
                            model_choice, 
                            temperature,
                            st.session_state.search_filters
                        )
                        
                        initial_state = {
                            "messages": [HumanMessage(content=prompt)],
                            "user_query": prompt,
                            "context": "",
                            "response": "",
                            "price_estimate": {},
                            "itinerary": {}
                        }
                        
                        result = app.invoke(initial_state)
                        response = result["response"]
                        
                        st.markdown(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                        
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
        with st.expander(f"⭐ {acc['rating']} | {acc['name']} - {acc['location']}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**📍 위치**: {acc['location']}")
                st.markdown(f"**🧹 청결도**: {acc['cleanliness_score']}/5.0")
                st.markdown(f"**📅 최근 예약**: {acc['recent_bookings']}건")
                
                st.markdown("**💰 가격 (1박 기준)**")
                for room_type, price in acc['price_per_night'].items():
                    st.write(f"  - {room_type}: {price:,}원")
                
                st.markdown(f"**🍽️ 조식**: {'포함 (뷔페)' if acc['meals']['breakfast_included'] else f'별도 ({acc['meals']['breakfast_price']:,}원)'}")
                st.markdown(f"**🎯 시설**: {', '.join(acc['facilities'][:5])}")
                
            with col2:
                st.markdown("**🚗 주변 명소**")
                for place, dist in list(acc['distance_to_attractions'].items())[:3]:
                    st.write(f"{place}: {dist}")

with tab5:
    st.subheader("📊 숙소 가격 비교")
    st.info("💡 **설문 결과**: 신뢰를 위해 가격 비교 정보가 중요합니다!")
    
    # 지역별 가격 비교
    regions = {}
    for acc in ACCOMMODATION_DATA:
        location = acc['location'].split()[0]
        if location not in regions:
            regions[location] = []
        min_price = min(acc['price_per_night'].values())
        regions[location].append({
            "name": acc['name'],
            "min_price": min_price,
            "rating": acc['rating']
        })
    
    for region, accs in regions.items():
        st.markdown(f"### 📍 {region}")
        for acc in sorted(accs, key=lambda x: x['min_price']):
            st.write(f"- **{acc['name']}**: {acc['min_price']:,}원/박 (평점 {acc['rating']})")
    
    st.divider()
    
    # 객실 타입별 가격
    st.markdown("### 🛏️ 객실 타입별 평균 가격")
    room_type_prices = {}
    for acc in ACCOMMODATION_DATA:
        for room_type, price in acc['price_per_night'].items():
            if room_type not in room_type_prices:
                room_type_prices[room_type] = []
            room_type_prices[room_type].append(price)
    
    for room_type, prices in room_type_prices.items():
        avg_price = sum(prices) / len(prices)
        st.write(f"- **{room_type}**: 평균 {avg_price:,.0f}원 (최저 {min(prices):,}원 ~ 최고 {max(prices):,}원)")

# 푸터
st.divider()
st.markdown("""
<div style='text-align: center; padding: 20px; background-color: #f8f9fa; border-radius: 10px;'>
    <h4>🎯 설문 기반 고도화 기능</h4>
    <p>✅ 가격 정보 우선 제공 | ✅ 일정표 자동 생성 | ✅ 지역별 필터링 | ✅ 가격 비교 | ✅ 최근 예약 사례</p>
    <p style='color: gray; margin-top: 10px;'>강원대학교 강원지능화혁신센터 | Powered by LangGraph & OpenAI</p>
</div>
""", unsafe_allow_html=True)
