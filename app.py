import streamlit as st
import os
import pandas as pd
import glob
from typing import Dict, List, Tuple
from collections import Counter
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_text_splitters import RecursiveCharacterTextSplitter
import re

# 페이지 설정
st.set_page_config(
    page_title="강원도 관광 AI 컨시어지",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# 설정 및 경로
# ============================================

REVIEWS_BASE_PATH = "리뷰"
CATEGORIES = ['맛집 리뷰', '명소 리뷰', '병원 리뷰', '카페 리뷰']

# ============================================
# 네이버 리뷰 데이터 로딩
# ============================================

@st.cache_data(show_spinner=False)
def load_naver_reviews(base_path: str = REVIEWS_BASE_PATH) -> tuple:
    """네이버 리뷰 데이터 로딩"""
    all_reviews = {}
    total_reviews = 0
    
    for category in CATEGORIES:
        category_path = os.path.join(base_path, category)
        category_reviews = []
        
        if not os.path.exists(category_path):
            all_reviews[category] = []
            continue
        
        excel_files = glob.glob(os.path.join(category_path, "*.xlsx"))
        excel_files.extend(glob.glob(os.path.join(category_path, "*.xls")))
        
        for file_path in excel_files:
            try:
                df = pd.read_excel(file_path)
                file_name = os.path.basename(file_path)
                place_name = file_name.replace('naver_review_', '').replace('.xlsx', '').replace('.xls', '').replace('_', ' ')
                
                for _, row in df.iterrows():
                    review = {
                        'category': category,
                        'place_name': row.get('store', place_name),
                        'date': str(row.get('date', '')),
                        'nickname': str(row.get('nickname', '익명')),
                        'content': str(row.get('content', '')),
                        'revisit': str(row.get('revisit', '')),
                        'file_source': file_name
                    }
                    
                    if review['content'] and review['content'] != 'nan':
                        category_reviews.append(review)
                        total_reviews += 1
                
            except Exception as e:
                continue
        
        all_reviews[category] = category_reviews
    
    return all_reviews, total_reviews


# ============================================
# 리뷰 분석 함수들
# ============================================

@st.cache_data
def analyze_reviews_by_place(reviews_data: Dict[str, List[Dict]]) -> Dict:
    """장소별 리뷰 분석"""
    place_analysis = {}
    
    for category, reviews in reviews_data.items():
        for review in reviews:
            place_name = review['place_name']
            if place_name not in place_analysis:
                place_analysis[place_name] = {
                    'category': category,
                    'total_reviews': 0,
                    'revisit_count': 0,
                    'keywords': [],
                    'recent_reviews': [],
                    'positive_count': 0,
                    'negative_count': 0,
                    'avg_visit_count': 1.0
                }
            
            place_analysis[place_name]['total_reviews'] += 1
            place_analysis[place_name]['recent_reviews'].append(review)
            
            # 재방문 확인 (2번째 이상만 재방문으로 카운트)
            revisit_text = review.get('revisit', '')
            # "2번째", "3번째" 등만 재방문으로 인정
            if any(f"{i}번째" in revisit_text for i in range(2, 100)):
                place_analysis[place_name]['revisit_count'] += 1
            
            # 키워드 추출
            content = review.get('content', '')
            positive_keywords = ['맛있', '좋', '추천', '최고', '훌륭', '친절', '깨끗', '만족', '재방문']
            negative_keywords = ['별로', '아쉽', '실망', '불친절', '더럽', '비싸', '맛없']
            
            for keyword in positive_keywords:
                if keyword in content:
                    place_analysis[place_name]['positive_count'] += 1
                    break
            
            for keyword in negative_keywords:
                if keyword in content:
                    place_analysis[place_name]['negative_count'] += 1
                    break
    
    # 재방문율 계산 및 평균 재방문 횟수
    for place_name, data in place_analysis.items():
        if data['total_reviews'] > 0:
            # 재방문율: 2번째 이상 방문한 리뷰 비율
            data['revisit_rate'] = (data['revisit_count'] / data['total_reviews']) * 100
            data['positive_rate'] = (data['positive_count'] / data['total_reviews']) * 100
            
            # 평균 재방문 횟수 계산
            visit_counts = []
            for review in data['recent_reviews']:
                revisit_text = review.get('revisit', '')
                # "N번째 방문"에서 N 추출
                import re
                match = re.search(r'(\d+)번째', revisit_text)
                if match:
                    visit_counts.append(int(match.group(1)))
                elif revisit_text:  # 형식이 다른 경우 1로 간주
                    visit_counts.append(1)
            
            if visit_counts:
                data['avg_visit_count'] = sum(visit_counts) / len(visit_counts)
            else:
                data['avg_visit_count'] = 1.0
        else:
            data['revisit_rate'] = 0
            data['positive_rate'] = 0
            data['avg_visit_count'] = 0
        
        # 최근 리뷰만 유지
        data['recent_reviews'] = data['recent_reviews'][:3]
    
    return place_analysis


def extract_price_mentions(content: str) -> List[str]:
    """리뷰에서 가격 언급 추출"""
    price_patterns = [
        r'(\d+)만원',
        r'(\d+),(\d+)원',
        r'(\d+)천원'
    ]
    
    prices = []
    for pattern in price_patterns:
        matches = re.findall(pattern, content)
        if matches:
            prices.extend([str(m) for m in matches])
    
    return prices


def get_top_places(place_analysis: Dict, category: str = None, 
                   sort_by: str = 'revisit_rate', limit: int = 10) -> List[Tuple]:
    """상위 장소 추출"""
    filtered = place_analysis
    
    if category:
        filtered = {k: v for k, v in place_analysis.items() 
                   if v['category'] == category}
    
    # 최소 리뷰 수 필터링 (신뢰도)
    filtered = {k: v for k, v in filtered.items() 
               if v['total_reviews'] >= 3}
    
    sorted_places = sorted(
        filtered.items(),
        key=lambda x: x[1].get(sort_by, 0),
        reverse=True
    )
    
    return sorted_places[:limit]


# ============================================
# 토큰 최적화된 RAG 문서 준비
# ============================================

def prepare_review_documents_optimized(
    reviews_data: Dict[str, List[Dict]], 
    user_query: str = ""
) -> List[str]:
    """
    토큰 최적화: 사용자 쿼리와 관련성 높은 장소만 선택
    """
    documents = []
    place_analysis = analyze_reviews_by_place(reviews_data)
    
    # 쿼리 키워드 추출
    query_keywords = ['재방문', '맛집', '명소', '카페', '병원', '추천', '좋은', '인기']
    
    # 카테고리 필터링
    target_categories = CATEGORIES
    if '맛집' in user_query or '음식' in user_query or '먹' in user_query:
        target_categories = ['맛집 리뷰']
    elif '명소' in user_query or '관광' in user_query or '구경' in user_query:
        target_categories = ['명소 리뷰']
    elif '카페' in user_query or '커피' in user_query:
        target_categories = ['카페 리뷰']
    
    # 상위 장소만 선택 (토큰 절약)
    for category in target_categories:
        top_places = get_top_places(place_analysis, category, 'revisit_rate', limit=15)
        
        for place_name, stats in top_places:
            # 간결한 문서 생성
            doc = f"""{category.replace(' 리뷰', '')} | {place_name}
리뷰:{stats['total_reviews']}개 재방문율:{stats['revisit_rate']:.0f}% 긍정:{stats['positive_rate']:.0f}%

주요리뷰:
"""
            for idx, review in enumerate(stats['recent_reviews'][:2], 1):  # 2개만
                content = review.get('content', '')[:150]  # 150자로 제한
                doc += f"{idx}.{content}\n"
            
            documents.append(doc)
    
    return documents


# ============================================
# 벡터 스토어 (토큰 최적화)
# ============================================

@st.cache_resource(show_spinner=False)
def create_vector_store_optimized(reviews_data: Dict[str, List[Dict]], _api_key: str):
    """토큰 최적화된 벡터 스토어 생성"""
    # 문서 준비 (쿼리 없이 전체 데이터의 대표 샘플만)
    documents = prepare_review_documents_optimized(reviews_data)
    
    # 작은 청크로 분할
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,  # 더 작게
        chunk_overlap=50
    )
    splits = text_splitter.create_documents(documents)
    
    # 임베딩
    embeddings = OpenAIEmbeddings(api_key=_api_key)
    
    # 배치 처리
    batch_size = 30
    first_batch = splits[:batch_size]
    vectorstore = Chroma.from_documents(
        documents=first_batch,
        embedding=embeddings
    )
    
    # 나머지 배치
    for i in range(1, len(splits) // batch_size + 1):
        start_idx = i * batch_size
        end_idx = min((i + 1) * batch_size, len(splits))
        batch = splits[start_idx:end_idx]
        if batch:
            vectorstore.add_documents(batch)
    
    return vectorstore


# ============================================
# 일정 생성 함수
# ============================================

def generate_itinerary(
    place_analysis: Dict,
    duration: str = "1박 2일",
    categories: List[str] = None,
    priorities: str = "재방문율"
) -> Dict:
    """리뷰 기반 똑똑한 일정 생성"""
    import random
    
    nights = int(duration[0]) if duration else 1
    days = nights + 1
    
    if not categories:
        categories = ['맛집 리뷰', '명소 리뷰', '카페 리뷰']
    
    sort_key = 'revisit_rate' if priorities == '재방문율' else 'positive_rate'
    
    # 카테고리별로 장소 풀 준비 (상위 30개, 다양성 확보)
    place_pools = {}
    for category in categories:
        top_places = get_top_places(place_analysis, category, sort_key, limit=30)
        place_pools[category] = [p for p in top_places]
    
    itinerary = {'duration': duration, 'days': []}
    used_places = set()  # 이미 사용한 장소 추적
    
    def select_place(category, used_places, pool, prefer_high_score=True):
        """똑똑한 장소 선택 - 중복 방지 + 다양성"""
        available = [p for p in pool if p[0] not in used_places]
        if not available:
            return None
        
        if prefer_high_score:
            # 상위권에서 랜덤 선택 (상위 30% 중)
            top_n = max(1, len(available) // 3)
            selected = random.choice(available[:top_n])
        else:
            # 전체에서 랜덤 (다양성)
            selected = random.choice(available)
        
        used_places.add(selected[0])
        return selected
    
    for day in range(1, days + 1):
        day_plan = {'day': day, 'activities': []}
        
        # 아침 - 카페 (1일차 제외, 2일차부터)
        if day > 1 and '카페 리뷰' in place_pools:
            cafe = select_place('카페 리뷰', used_places, place_pools['카페 리뷰'])
            if cafe:
                day_plan['activities'].append({
                    'time': '09:00',
                    'type': '카페',
                    'place': cafe[0],
                    'stats': cafe[1]
                })
        
        # 오전 - 명소 (실내/실외 다양하게)
        if '명소 리뷰' in place_pools:
            # 날씨 좋은 날 가정 - 실외 명소 선호
            attraction = select_place('명소 리뷰', used_places, place_pools['명소 리뷰'], prefer_high_score=True)
            if attraction:
                day_plan['activities'].append({
                    'time': '10:30' if day > 1 else '10:00',
                    'type': '명소',
                    'place': attraction[0],
                    'stats': attraction[1]
                })
        
        # 점심 - 맛집 (현지 맛집 우선)
        if '맛집 리뷰' in place_pools:
            restaurant_lunch = select_place('맛집 리뷰', used_places, place_pools['맛집 리뷰'], prefer_high_score=True)
            if restaurant_lunch:
                day_plan['activities'].append({
                    'time': '12:30',
                    'type': '맛집',
                    'place': restaurant_lunch[0],
                    'stats': restaurant_lunch[1]
                })
        
        # 오후 - 명소 또는 체험 (마지막 날 제외)
        if day < days and '명소 리뷰' in place_pools:
            # 다양성을 위해 덜 유명한 곳도 선택 가능
            attraction2 = select_place('명소 리뷰', used_places, place_pools['명소 리뷰'], prefer_high_score=(day == 1))
            if attraction2:
                day_plan['activities'].append({
                    'time': '14:30',
                    'type': '명소',
                    'place': attraction2[0],
                    'stats': attraction2[1]
                })
        
        # 카페 타임 (오후, 50% 확률로 추가)
        if random.random() > 0.5 and '카페 리뷰' in place_pools and day < days:
            cafe2 = select_place('카페 리뷰', used_places, place_pools['카페 리뷰'], prefer_high_score=False)
            if cafe2:
                day_plan['activities'].append({
                    'time': '16:00',
                    'type': '카페',
                    'place': cafe2[0],
                    'stats': cafe2[1]
                })
        
        # 저녁 - 맛집 (분위기 좋은 곳)
        if '맛집 리뷰' in place_pools:
            restaurant_dinner = select_place('맛집 리뷰', used_places, place_pools['맛집 리뷰'], prefer_high_score=True)
            if restaurant_dinner:
                day_plan['activities'].append({
                    'time': '18:30',
                    'type': '맛집',
                    'place': restaurant_dinner[0],
                    'stats': restaurant_dinner[1]
                })
        
        itinerary['days'].append(day_plan)
    
    return itinerary


# ============================================
# API 키 관리
# ============================================

def get_api_key():
    try:
        return st.secrets["OPENAI_API_KEY"]
    except:
        return None


# ============================================
# 세션 상태 초기화
# ============================================

if "messages" not in st.session_state:
    st.session_state.messages = []
if "reviews_loaded" not in st.session_state:
    st.session_state.reviews_loaded = False
if "reviews_data" not in st.session_state:
    st.session_state.reviews_data = {}
if "place_analysis" not in st.session_state:
    st.session_state.place_analysis = {}

API_KEY = get_api_key()

# ============================================
# CSS
# ============================================

st.markdown("""
<style>
.stButton>button {width: 100%;}
.info-banner {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    color: white; padding: 20px; border-radius: 10px;
    margin-bottom: 20px; text-align: center;
}
.place-card {
    border: 1px solid #e0e0e0; padding: 15px;
    border-radius: 8px; margin: 10px 0;
    background: white;
}
.metric-badge {
    display: inline-block; padding: 5px 10px;
    border-radius: 5px; margin: 5px;
    font-size: 0.9em; font-weight: bold;
}
.high {background: #4CAF50; color: white;}
.medium {background: #FFC107; color: black;}
.low {background: #f44336; color: white;}
</style>
""", unsafe_allow_html=True)

# ============================================
# 상단 배너
# ============================================

st.markdown("""
<div class='info-banner'>
    <h1>🏔️ 강원도 관광 AI 컨시어지</h1>
    <p>실제 리뷰 기반 · 일정 자동 생성 · 맞춤 추천 · 가격 비교</p>
</div>
""", unsafe_allow_html=True)

# ============================================
# 사이드바
# ============================================

with st.sidebar:
    st.title("⚙️ 설정")
    
    if API_KEY:
        st.success("✅ API 키 설정됨")
    else:
        st.error("⚠️ API 키 필요")
    
    st.divider()
    
    # 리뷰 데이터 자동 로딩
    if not st.session_state.reviews_loaded:
        with st.spinner("📂 리뷰 데이터 로딩..."):
            try:
                reviews_data, total_reviews = load_naver_reviews(REVIEWS_BASE_PATH)
                
                if total_reviews > 0:
                    st.session_state.reviews_data = reviews_data
                    st.session_state.place_analysis = analyze_reviews_by_place(reviews_data)
                    st.session_state.reviews_loaded = True
                    st.success(f"✅ {total_reviews:,}개 리뷰 로딩!")
            except Exception as e:
                st.error(f"❌ 로딩 실패: {str(e)}")
    
    # 통계
    if st.session_state.reviews_loaded:
        st.subheader("📊 데이터")
        total = sum(len(r) for r in st.session_state.reviews_data.values())
        places = len(st.session_state.place_analysis)
        st.metric("총 리뷰", f"{total:,}개")
        st.metric("장소 수", f"{places}곳")
    
    st.divider()
    
    # AI 설정
    st.subheader("🤖 AI 설정")
    model_choice = st.selectbox(
        "모델", 
        ["gpt-4o-mini", "gpt-5-nano", "gpt-5-mini"],
        index=0
    )
    temperature = st.slider("창의성", 0.0, 1.0, 0.7, 0.1)
    search_k = st.slider("검색 결과", 3, 10, 5, 1)

# ============================================
# 메인 탭
# ============================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💬 AI 챗봇",
    "📋 일정 생성기", 
    "🏆 TOP 추천",
    "📊 비교 분석",
    "⭐ 리뷰 통계"
])

# TAB 1: AI 챗봇
with tab1:
    st.subheader("💬 AI 관광 컨시어지")
    
    if not st.session_state.reviews_loaded:
        st.warning("⚠️ 리뷰 데이터 로딩 중...")
    elif not API_KEY:
        st.error("⚠️ API 키를 설정해주세요")
    else:
        st.info("💡 실제 리뷰를 기반으로 답변합니다!")
        
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        if prompt := st.chat_input("예: 재방문율 높은 춘천 맛집 추천해줘"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                try:
                    with st.spinner("🔄 데이터 준비 중..."):
                        vectorstore = create_vector_store_optimized(
                            st.session_state.reviews_data,
                            API_KEY
                        )
                    
                    with st.spinner("🤔 답변 생성 중..."):
                        llm = ChatOpenAI(
                            model=model_choice,
                            temperature=temperature,
                            api_key=API_KEY,
                            streaming=True
                        )
                        
                        retriever = vectorstore.as_retriever(search_kwargs={"k": search_k})
                        docs = retriever.invoke(prompt)  # get_relevant_documents 대신 invoke 사용
                        context = "\n\n".join([doc.page_content for doc in docs])
                        
                        system_prompt = """강원도 관광 AI 컨시어지입니다.

**역할**: 실제 방문객 리뷰 기반 신뢰할 수 있는 정보 제공

**답변 원칙**:
1. 재방문율과 긍정 평가 높은 장소 우선 추천
2. 리뷰 통계 명시 (총 리뷰 수, 재방문율, 긍정률)
3. 실제 방문객 의견 요약
4. 간결하고 명확하게

**컨텍스트**:
{context}

**형식**: 장소명, 통계, 특징을 포함하여 간결하게 작성"""

                        prompt_template = ChatPromptTemplate.from_messages([
                            ("system", system_prompt),
                            MessagesPlaceholder(variable_name="messages")
                        ])
                        
                        chain = prompt_template | llm
                        
                        chat_history = []
                        for msg in st.session_state.messages:
                            if msg["role"] == "user":
                                chat_history.append(HumanMessage(content=msg["content"]))
                            else:
                                chat_history.append(AIMessage(content=msg["content"]))
                        
                        response_stream = chain.stream({
                            "context": context,
                            "messages": chat_history
                        })
                        full_response = st.write_stream(response_stream)
                        
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": full_response
                        })
                        
                except Exception as e:
                    st.error(f"❌ 오류: {str(e)}")

# TAB 2: 일정 생성기
with tab2:
    st.subheader("📋 자동 일정 생성기")
    st.info("💡 AI 알고리즘이 중복 없이 다양한 장소로 매번 새로운 일정을 생성합니다!")
    st.caption("🔄 같은 조건으로 여러 번 생성하면 다양한 조합의 일정을 받을 수 있습니다.")
    
    if not st.session_state.reviews_loaded:
        st.warning("⚠️ 리뷰 데이터를 먼저 로딩해주세요")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            duration = st.selectbox("여행 기간", ["1박 2일", "2박 3일", "3박 4일"])
            categories = st.multiselect(
                "포함할 카테고리",
                ['맛집 리뷰', '명소 리뷰', '카페 리뷰'],
                default=['맛집 리뷰', '명소 리뷰', '카페 리뷰']
            )
        
        with col2:
            priority = st.radio(
                "우선순위",
                ["재방문율", "긍정 평가"],
                help="어떤 기준으로 장소를 선택할지"
            )
        
        if st.button("🎯 일정 생성 (매번 새로운 조합)", use_container_width=True):
            with st.spinner("똑똑한 알고리즘으로 일정 생성 중..."):
                itinerary = generate_itinerary(
                    st.session_state.place_analysis,
                    duration,
                    categories,
                    priority
                )
                
                st.success("✅ 일정이 생성되었습니다!")
                
                for day_plan in itinerary['days']:
                    st.markdown(f"### 📅 Day {day_plan['day']}")
                    
                    for activity in day_plan['activities']:
                        with st.container():
                            col1, col2, col3 = st.columns([1, 3, 2])
                            
                            with col1:
                                st.write(f"**{activity['time']}**")
                            
                            with col2:
                                st.write(f"**{activity['place']}**")
                                st.caption(f"{activity['type']}")
                            
                            with col3:
                                stats = activity['stats']
                                st.write(f"재방문율: {stats['revisit_rate']:.0f}%")
                                st.write(f"평균: {stats.get('avg_visit_count', 1):.1f}번")
                    
                    st.divider()
                
                # 다운로드
                itinerary_text = f"# {duration} 강원도 여행 일정\n\n"
                for day_plan in itinerary['days']:
                    itinerary_text += f"## Day {day_plan['day']}\n\n"
                    for activity in day_plan['activities']:
                        stats = activity['stats']
                        itinerary_text += f"- {activity['time']} | {activity['place']} ({activity['type']})\n"
                        itinerary_text += f"  재방문율: {stats['revisit_rate']:.0f}%, 평균 방문: {stats.get('avg_visit_count', 1):.1f}번, 리뷰: {stats['total_reviews']}개\n\n"
                
                st.download_button(
                    "📥 일정표 다운로드",
                    itinerary_text,
                    file_name="강원도_여행_일정.txt",
                    mime="text/plain",
                    use_container_width=True
                )

# TAB 3: TOP 추천
with tab3:
    st.subheader("🏆 TOP 추천 장소")
    
    if not st.session_state.reviews_loaded:
        st.warning("⚠️ 리뷰 데이터를 먼저 로딩해주세요")
    else:
        category_filter = st.selectbox(
            "카테고리 선택",
            ["전체"] + CATEGORIES
        )
        
        sort_option = st.radio(
            "정렬 기준",
            ["재방문율", "긍정 평가", "리뷰 수"],
            horizontal=True
        )
        
        sort_map = {
            "재방문율": "revisit_rate",
            "긍정 평가": "positive_rate",
            "리뷰 수": "total_reviews"
        }
        
        category = None if category_filter == "전체" else category_filter
        top_places = get_top_places(
            st.session_state.place_analysis,
            category,
            sort_map[sort_option],
            limit=20
        )
        
        for idx, (place_name, stats) in enumerate(top_places, 1):
            with st.container():
                st.markdown(f"""
                <div class='place-card'>
                    <h4>{idx}. {place_name}</h4>
                    <p><strong>{stats['category'].replace(' 리뷰', '')}</strong></p>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("리뷰 수", f"{stats['total_reviews']}개")
                with col2:
                    st.metric("재방문율", f"{stats['revisit_rate']:.1f}%")
                with col3:
                    st.metric("평균 방문", f"{stats.get('avg_visit_count', 1):.1f}번")
                with col4:
                    st.metric("긍정 평가", f"{stats['positive_rate']:.1f}%")
                
                if stats['recent_reviews']:
                    with st.expander("최근 리뷰 보기"):
                        for review in stats['recent_reviews'][:2]:
                            st.write(f"• {review['content'][:100]}...")

# TAB 4: 비교 분석
with tab4:
    st.subheader("📊 장소 비교 분석")
    
    if not st.session_state.reviews_loaded:
        st.warning("⚠️ 리뷰 데이터를 먼저 로딩해주세요")
    else:
        all_places = list(st.session_state.place_analysis.keys())
        
        col1, col2 = st.columns(2)
        with col1:
            place1 = st.selectbox("장소 1", all_places, key="place1")
        with col2:
            place2 = st.selectbox("장소 2", all_places, key="place2", index=min(1, len(all_places)-1))
        
        if st.button("⚖️ 비교하기", use_container_width=True):
            stats1 = st.session_state.place_analysis[place1]
            stats2 = st.session_state.place_analysis[place2]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"### {place1}")
                st.write(f"**카테고리**: {stats1['category']}")
                st.metric("총 리뷰", f"{stats1['total_reviews']}개")
                st.metric("재방문율", f"{stats1['revisit_rate']:.1f}%")
                st.metric("평균 방문", f"{stats1.get('avg_visit_count', 1):.1f}번")
                st.metric("긍정 평가", f"{stats1['positive_rate']:.1f}%")
            
            with col2:
                st.markdown(f"### {place2}")
                st.write(f"**카테고리**: {stats2['category']}")
                st.metric("총 리뷰", f"{stats2['total_reviews']}개")
                st.metric("재방문율", f"{stats2['revisit_rate']:.1f}%")
                st.metric("평균 방문", f"{stats2.get('avg_visit_count', 1):.1f}번")
                st.metric("긍정 평가", f"{stats2['positive_rate']:.1f}%")
            
            st.divider()
            
            # 승자 판정 (4개 지표)
            scores = {place1: 0, place2: 0}
            
            if stats1['revisit_rate'] > stats2['revisit_rate']:
                scores[place1] += 1
            else:
                scores[place2] += 1
            
            if stats1['positive_rate'] > stats2['positive_rate']:
                scores[place1] += 1
            else:
                scores[place2] += 1
            
            if stats1.get('avg_visit_count', 1) > stats2.get('avg_visit_count', 1):
                scores[place1] += 1
            else:
                scores[place2] += 1
            
            if stats1['total_reviews'] > stats2['total_reviews']:
                scores[place1] += 1
            else:
                scores[place2] += 1
            
            winner = place1 if scores[place1] > scores[place2] else place2
            st.success(f"🏆 종합 우승: **{winner}** ({scores[winner]}:{scores[place1 if winner == place2 else place2]})")

# TAB 5: 리뷰 통계
with tab5:
    st.subheader("⭐ 리뷰 통계 대시보드")
    
    if not st.session_state.reviews_loaded:
        st.warning("⚠️ 리뷰 데이터를 먼저 로딩해주세요")
    else:
        # 전체 통계
        total_reviews = sum(len(r) for r in st.session_state.reviews_data.values())
        total_places = len(st.session_state.place_analysis)
        total_revisits = sum(p['revisit_count'] for p in st.session_state.place_analysis.values())
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("총 리뷰", f"{total_reviews:,}개")
        with col2:
            st.metric("총 장소", f"{total_places}곳")
        with col3:
            st.metric("재방문 리뷰", f"{total_revisits:,}개")
        
        st.divider()
        
        # 카테고리별 통계
        st.markdown("### 📈 카테고리별 통계")
        
        for category in CATEGORIES:
            if category in st.session_state.reviews_data:
                reviews = st.session_state.reviews_data[category]
                category_places = [p for p in st.session_state.place_analysis.values() 
                                  if p['category'] == category]
                
                if category_places:
                    avg_revisit = sum(p['revisit_rate'] for p in category_places) / len(category_places)
                    avg_positive = sum(p['positive_rate'] for p in category_places) / len(category_places)
                    
                    with st.expander(f"{category} ({len(reviews)}개 리뷰, {len(category_places)}개 장소)"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("평균 재방문율", f"{avg_revisit:.1f}%")
                        with col2:
                            st.metric("평균 긍정 평가", f"{avg_positive:.1f}%")

# ============================================
# 푸터
# ============================================

st.divider()
st.markdown("""
<div style='text-align: center; padding: 20px; background-color: #f8f9fa; border-radius: 10px;'>
    <h4>🎯 설문 기반 실용 기능</h4>
    <p>✅ 리뷰 기반 추천 | ✅ 자동 일정 생성 | ✅ 장소 비교 | ✅ TOP 순위 | ✅ 통계 분석</p>
    <p style='color: gray; margin-top: 10px;'>강원대학교 학생창의자율과제 7팀</p>
</div>
""", unsafe_allow_html=True)
