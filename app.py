import streamlit as st
import os
import pandas as pd
import glob
from typing import Dict, List
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 페이지 설정
st.set_page_config(
    page_title="강원도 관광 AI 컨시어지",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# 설정 및 경로 (Streamlit Cloud용)
# ============================================

REVIEWS_BASE_PATH = "리뷰"  # GitHub 저장소의 리뷰 폴더
CATEGORIES = ['맛집 리뷰', '명소 리뷰', '병원 리뷰', '카페 리뷰']

# ============================================
# 네이버 리뷰 데이터 로딩 함수
# ============================================

@st.cache_data(show_spinner=False)
def load_naver_reviews(base_path: str = REVIEWS_BASE_PATH) -> tuple:
    """
    4개 카테고리 폴더에서 모든 네이버 리뷰 엑셀 파일을 읽어옵니다.
    
    Returns:
        (reviews_data, total_reviews) 튜플
    """
    all_reviews = {}
    total_reviews = 0
    
    for category in CATEGORIES:
        category_path = os.path.join(base_path, category)
        category_reviews = []
        
        if not os.path.exists(category_path):
            st.warning(f"⚠️ '{category}' 폴더를 찾을 수 없습니다: {category_path}")
            all_reviews[category] = []
            continue
        
        # 폴더 내의 모든 엑셀 파일 찾기
        excel_files = glob.glob(os.path.join(category_path, "*.xlsx"))
        excel_files.extend(glob.glob(os.path.join(category_path, "*.xls")))
        
        # 각 엑셀 파일 읽기
        for file_path in excel_files:
            try:
                df = pd.read_excel(file_path)
                
                # 파일명에서 장소명 추출
                file_name = os.path.basename(file_path)
                place_name = file_name.replace('naver_review_', '').replace('.xlsx', '').replace('.xls', '').replace('_', ' ')
                
                # 각 리뷰를 딕셔너리로 변환
                for _, row in df.iterrows():
                    review = {
                        'category': category,
                        'place_name': row.get('store', place_name),
                        'date': str(row.get('date', '')),
                        'nickname': str(row.get('nickname', '익명')),
                        'content': str(row.get('content', '')),
                        'revisit': str(row.get('revisit', '')),
                        'reply_date': str(row.get('reply_date', '')) if pd.notna(row.get('reply_date')) else '',
                        'reply_txt': str(row.get('reply_txt', '')) if pd.notna(row.get('reply_txt')) else '',
                        'file_source': file_name
                    }
                    
                    # 내용이 있는 리뷰만 추가
                    if review['content'] and review['content'] != 'nan':
                        category_reviews.append(review)
                        total_reviews += 1
                
            except Exception as e:
                st.error(f"❌ 파일 로딩 실패: {file_path} - {str(e)}")
                continue
        
        all_reviews[category] = category_reviews
    
    return all_reviews, total_reviews


def prepare_review_documents(reviews_data: Dict[str, List[Dict]]) -> List[str]:
    """
    네이버 리뷰 데이터를 RAG용 문서로 변환합니다.
    """
    documents = []
    
    for category, reviews in reviews_data.items():
        # 장소별로 리뷰 그룹화
        place_reviews = {}
        for review in reviews:
            place_name = review['place_name']
            if place_name not in place_reviews:
                place_reviews[place_name] = []
            place_reviews[place_name].append(review)
        
        # 각 장소에 대한 문서 생성
        for place_name, place_review_list in place_reviews.items():
            total_reviews = len(place_review_list)
            revisit_count = sum(1 for r in place_review_list if '재방문' in r.get('revisit', '') or '번째' in r.get('revisit', ''))
            revisit_rate = (revisit_count / total_reviews * 100) if total_reviews > 0 else 0
            
            # 긍정적 키워드 카운트
            positive_keywords = ['맛있', '좋', '추천', '최고', '훌륭', '친절', '깨끗', '만족']
            positive_count = sum(1 for r in place_review_list 
                                for keyword in positive_keywords 
                                if keyword in r.get('content', ''))
            
            # 대표 리뷰 선택 (긴 리뷰 우선, 최대 10개)
            sorted_reviews = sorted(place_review_list, key=lambda x: len(x.get('content', '')), reverse=True)
            top_reviews = sorted_reviews[:10]
            
            # 문서 생성
            doc = f"""
카테고리: {category}
장소명: {place_name}

[통계 정보]
- 총 리뷰 수: {total_reviews}개
- 재방문 리뷰: {revisit_count}개 ({revisit_rate:.1f}%)
- 긍정 평가: {positive_count}회 언급

[주요 리뷰 내용]
"""
            for idx, review in enumerate(top_reviews, 1):
                content = review.get('content', '')[:400]
                doc += f"\n리뷰 #{idx}\n"
                doc += f"작성일: {review.get('date', '')}\n"
                doc += f"작성자: {review.get('nickname', '익명')}\n"
                if review.get('revisit'):
                    doc += f"방문: {review['revisit']}\n"
                doc += f"내용: {content}\n"
                doc += "-" * 40 + "\n"
            
            documents.append(doc)
    
    return documents


# ============================================
# 벡터 스토어 관리 (Streamlit Cloud용 - 메모리 캐싱)
# ============================================

@st.cache_resource(show_spinner=False)
def create_vector_store(reviews_data: Dict[str, List[Dict]], _api_key: str):
    """
    리뷰 데이터로부터 벡터 스토어를 생성합니다.
    Streamlit Cloud에서는 메모리에 캐싱되어 앱 재시작 전까지 유지됩니다.
    """
    # 문서 준비
    documents = prepare_review_documents(reviews_data)
    
    # 텍스트 분할
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    splits = text_splitter.create_documents(documents)
    
    # 임베딩 및 벡터 스토어 생성
    embeddings = OpenAIEmbeddings(api_key=_api_key)
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embeddings
    )
    
    return vectorstore


# ============================================
# API 키 관리 (Streamlit Cloud Secrets 사용)
# ============================================

def get_api_key():
    """Streamlit Cloud Secrets에서 API 키 가져오기"""
    try:
        return st.secrets["OPENAI_API_KEY"]
    except Exception as e:
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
if "total_reviews" not in st.session_state:
    st.session_state.total_reviews = 0

# API 키 확인
API_KEY = get_api_key()

# ============================================
# 커스텀 CSS
# ============================================

st.markdown("""
<style>
.stButton>button {
    width: 100%;
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
    margin: 10px 0;
}
.cache-info {
    background-color: #e8f4f8;
    padding: 15px;
    border-radius: 8px;
    border-left: 4px solid #2196F3;
}
</style>
""", unsafe_allow_html=True)

# ============================================
# 상단 배너
# ============================================

st.markdown("""
<div class='info-banner'>
    <h1>🏔️ 강원도 관광 AI 컨시어지</h1>
    <p>네이버 리뷰 기반 · 실시간 답변 · Streamlit Cloud 최적화</p>
</div>
""", unsafe_allow_html=True)

# ============================================
# 사이드바
# ============================================

with st.sidebar:
    st.title("⚙️ 설정")
    
    # API 키 상태 표시
    if API_KEY:
        st.success("✅ API 키가 설정되었습니다")
    else:
        st.error("⚠️ API 키가 필요합니다")
        st.info("""
        **Streamlit Cloud에서 API 키 설정:**
        
        1. 앱 대시보드 → Settings
        2. Secrets 섹션 클릭
        3. 아래 내용 입력:
        ```
        OPENAI_API_KEY = "sk-your-key-here"
        ```
        4. Save 클릭
        """)
    
    st.divider()
    
    # 리뷰 데이터 자동 로딩
    if not st.session_state.reviews_loaded:
        with st.spinner("📂 리뷰 데이터 로딩 중..."):
            try:
                reviews_data, total_reviews = load_naver_reviews(REVIEWS_BASE_PATH)
                
                if total_reviews == 0:
                    st.error(f"❌ 리뷰 데이터를 찾을 수 없습니다.")
                    st.info(f"GitHub 저장소의 '{REVIEWS_BASE_PATH}' 폴더를 확인해주세요.")
                else:
                    st.session_state.reviews_data = reviews_data
                    st.session_state.total_reviews = total_reviews
                    st.session_state.reviews_loaded = True
                    st.success(f"✅ {total_reviews:,}개의 리뷰를 로딩했습니다!")
                    
            except Exception as e:
                st.error(f"❌ 리뷰 로딩 실패: {str(e)}")
    
    # 리뷰 데이터 통계
    if st.session_state.reviews_loaded:
        st.subheader("📊 리뷰 데이터")
        st.metric("총 리뷰", f"{st.session_state.total_reviews:,}개")
        
        with st.expander("카테고리별 상세"):
            for category, reviews in st.session_state.reviews_data.items():
                if reviews:
                    st.write(f"**{category}**: {len(reviews):,}개")
    
    st.divider()
    
    # 모델 설정
    st.subheader("🤖 AI 모델 설정")
    model_choice = st.selectbox(
        "모델",
        ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
        index=0,
        help="gpt-4o-mini 권장"
    )
    
    temperature = st.slider(
        "창의성",
        0.0, 1.0, 0.7, 0.1,
        help="낮을수록 일관적, 높을수록 창의적"
    )
    
    search_k = st.slider(
        "검색 결과 수",
        3, 15, 8, 1,
        help="더 많은 관련 문서 검색"
    )
    
    st.divider()
    
    # 캐싱 정보
    st.markdown("""
    <div class='cache-info'>
    <strong>💡 Streamlit Cloud 캐싱</strong><br>
    벡터 스토어가 메모리에 캐싱되어<br>
    앱 재시작 전까지 빠르게 사용됩니다.
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    st.caption("강원대학교 학생창의자율과제 7팀")

# ============================================
# 메인 탭
# ============================================

tab1, tab2 = st.tabs(["💬 AI 챗봇", "📊 리뷰 분석"])

with tab1:
    st.subheader("💬 AI 관광 컨시어지")
    
    if not st.session_state.reviews_loaded:
        st.warning("⚠️ 리뷰 데이터를 로딩하는 중입니다...")
    elif not API_KEY:
        st.error("⚠️ API 키를 설정해주세요. (사이드바 참고)")
    else:
        st.info("💡 실제 방문객 리뷰를 기반으로 답변합니다!")
        
        # 대화 히스토리 표시
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # 사용자 입력
        if prompt := st.chat_input("예: 춘천에서 재방문율 높은 맛집 추천해줘"):
            # 사용자 메시지 추가
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # AI 응답 생성
            with st.chat_message("assistant"):
                try:
                    with st.spinner("🤔 답변 생성 중..."):
                        # 벡터 스토어 생성 또는 로드 (캐싱됨)
                        vectorstore = create_vector_store(
                            st.session_state.reviews_data,
                            API_KEY
                        )
                        
                        # LLM 초기화
                        llm = ChatOpenAI(
                            model=model_choice,
                            temperature=temperature,
                            api_key=API_KEY,
                            streaming=True
                        )
                        
                        # 벡터 스토어에서 검색
                        retriever = vectorstore.as_retriever(
                            search_kwargs={"k": search_k}
                        )
                        docs = retriever.get_relevant_documents(prompt)
                        context = "\n\n".join([doc.page_content for doc in docs])
                        
                        # 프롬프트 생성
                        system_prompt = """당신은 강원도 관광 전문 AI 컨시어지입니다.

**역할:**
실제 방문객들의 네이버 리뷰를 분석하여 신뢰할 수 있는 여행 정보를 제공합니다.

**답변 원칙:**
1. 실제 리뷰 데이터에 기반한 객관적 정보 제공
2. 재방문율이 높은 장소 우선 추천
3. 긍정적/부정적 의견 균형있게 전달
4. 구체적인 정보 포함 (위치, 가격, 영업시간 등)
5. 리뷰에서 자주 언급되는 특징 강조

**컨텍스트 (실제 리뷰 데이터):**
{context}

**답변 형식:**
- 간결하고 명확하게
- 필요시 장소별로 구분하여 설명
- 리뷰 통계 정보 활용 (총 리뷰 수, 재방문율)
- 실제 방문객 의견 요약 제공

**주의사항:**
- 리뷰에 없는 내용은 추측하지 않기
- 가격, 영업시간 등은 리뷰에 명시된 경우만 언급
- 최신 정보는 직접 확인 권장"""

                        prompt_template = ChatPromptTemplate.from_messages([
                            ("system", system_prompt),
                            MessagesPlaceholder(variable_name="messages")
                        ])
                        
                        chain = prompt_template | llm
                        
                        # 대화 기록 준비
                        chat_history = []
                        for msg in st.session_state.messages:
                            if msg["role"] == "user":
                                chat_history.append(HumanMessage(content=msg["content"]))
                            else:
                                chat_history.append(AIMessage(content=msg["content"]))
                        
                        # 스트리밍 실행
                        response_stream = chain.stream({
                            "context": context,
                            "messages": chat_history
                        })
                        full_response = st.write_stream(response_stream)
                        
                        # 응답 저장
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": full_response
                        })
                        
                except Exception as e:
                    st.error(f"❌ 오류: {str(e)}")
                    st.info("잠시 후 다시 시도해주세요.")

with tab2:
    st.subheader("📊 리뷰 분석")
    
    if not st.session_state.reviews_loaded:
        st.warning("⚠️ 리뷰 데이터를 로딩하는 중입니다...")
    else:
        # 전체 통계
        total_reviews = st.session_state.total_reviews
        total_places = sum(len(set(r['place_name'] for r in reviews)) 
                          for reviews in st.session_state.reviews_data.values())
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("총 리뷰", f"{total_reviews:,}개")
        with col2:
            st.metric("총 장소", f"{total_places}곳")
        with col3:
            st.metric("카테고리", f"{len(CATEGORIES)}개")
        
        st.divider()
        
        # 카테고리 선택
        category_choice = st.selectbox(
            "카테고리 선택",
            list(st.session_state.reviews_data.keys())
        )
        
        category_reviews = st.session_state.reviews_data[category_choice]
        
        if not category_reviews:
            st.info("해당 카테고리에 리뷰 데이터가 없습니다.")
        else:
            # 장소별 통계 계산
            place_stats = {}
            for review in category_reviews:
                place_name = review['place_name']
                if place_name not in place_stats:
                    place_stats[place_name] = {
                        'total': 0,
                        'revisit': 0,
                        'recent_reviews': []
                    }
                place_stats[place_name]['total'] += 1
                if '재방문' in review.get('revisit', '') or '번째' in review.get('revisit', ''):
                    place_stats[place_name]['revisit'] += 1
                place_stats[place_name]['recent_reviews'].append(review)
            
            # 재방문율 계산 및 정렬
            for place_name, stats in place_stats.items():
                stats['revisit_rate'] = (stats['revisit'] / stats['total'] * 100) if stats['total'] > 0 else 0
            
            sorted_places = sorted(place_stats.items(), 
                                 key=lambda x: (x[1]['revisit_rate'], x[1]['total']), 
                                 reverse=True)
            
            # 카테고리 통계
            st.markdown(f"### 📊 {category_choice} 통계")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("장소 수", f"{len(sorted_places)}곳")
            with col2:
                st.metric("리뷰 수", f"{len(category_reviews):,}개")
            
            st.divider()
            
            # TOP 10 장소 (재방문율 순)
            st.markdown("### 🏆 재방문율 높은 TOP 10")
            
            for idx, (place_name, stats) in enumerate(sorted_places[:10], 1):
                with st.expander(
                    f"{idx}. {place_name} - 재방문율 {stats['revisit_rate']:.1f}% (리뷰 {stats['total']}개)"
                ):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("총 리뷰", f"{stats['total']}개")
                    with col2:
                        st.metric("재방문 리뷰", f"{stats['revisit']}개")
                    with col3:
                        st.metric("재방문율", f"{stats['revisit_rate']:.1f}%")
                    
                    # 최근 리뷰 3개
                    st.markdown("**최근 리뷰:**")
                    for review in stats['recent_reviews'][:3]:
                        content = review.get('content', '')[:150]
                        revisit_info = f" ({review.get('revisit', '')})" if review.get('revisit') else ""
                        st.write(f"• `{review.get('date', '')}` {review.get('nickname', '익명')}{revisit_info}")
                        st.caption(f"{content}...")

# ============================================
# 푸터
# ============================================

st.divider()
st.markdown("""
<div style='text-align: center; padding: 20px; background-color: #f8f9fa; border-radius: 10px;'>
    <h4>🎯 네이버 리뷰 기반 AI 컨시어지</h4>
    <p>✅ 실제 방문객 리뷰 분석 | ✅ Streamlit Cloud 최적화 | ✅ 빠른 응답</p>
    <p style='color: gray; margin-top: 10px;'>강원대학교 학생창의자율과제 7팀 | Powered by LangChain & OpenAI</p>
</div>
""", unsafe_allow_html=True)
