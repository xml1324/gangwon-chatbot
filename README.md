# 🏔️ 강원도 관광 AI 컨시어지 (웹 버전)

> **설치 없이 웹에서 바로 사용하는 AI 관광 챗봇**
> 
> 🌐 **Live Demo**: [여기를 클릭하여 바로 사용하기](#) ← 배포 후 URL 업데이트

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io)
[![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=OpenAI&logoColor=white)](https://openai.com)
[![LangChain](https://img.shields.io/badge/LangChain-121212?style=for-the-badge)](https://langchain.com)

---

## 🎯 프로젝트 소개

**관광업 전문가 18명의 설문 결과를 100% 반영한 실무형 AI 챗봇**

- ✅ 가격 정보 우선 제공 (설문 1위 니즈)
- ✅ 일정표 자동 생성 (반복 업무 1위)
- ✅ 실시간 숙소 필터링
- ✅ 가격 비교 및 견적 계산
- ✅ 청결도 점수 & 최근 예약 건수

---

## 🚀 주요 기능

### 💬 Tab 1: AI 상담
- 빠른 질문 버튼 (가격, 숙소, 일정)
- 가격 정보 우선 제공
- 거리와 이동 시간 자동 포함

### 💰 Tab 2: 견적 계산기
- 여행 기간/인원 입력 → 즉시 견적
- 항목별 비용 분석
- 1인당 비용 자동 계산

### 📋 Tab 3: 일정표 생성
- 패키지 선택 → 원클릭 생성
- 시간대별 상세 일정
- 텍스트 다운로드

### 🏨 Tab 4: 숙소 검색
- 실시간 필터링 (지역, 가격, 타입)
- 청결도 점수 표시
- 최근 예약 건수

### 📊 Tab 5: 가격 비교
- 지역별 가격 비교
- 객실 타입별 평균
- 투명한 가격 정보

---

## 🌐 웹에서 사용하기

### 방법 1: 배포된 앱 사용 (추천)

**바로 접속**: [https://your-app-name.streamlit.app](#)

- 설치 불필요
- 회원가입 불필요
- 브라우저에서 즉시 사용

### 방법 2: 로컬에서 실행

```bash
# 1. 레포지토리 클론
git clone https://github.com/your-username/gangwon-tourism-chatbot.git
cd gangwon-tourism-chatbot

# 2. 패키지 설치
pip install -r requirements.txt

# 3. Secrets 설정
mkdir -p .streamlit
echo 'OPENAI_API_KEY = "sk-your-key-here"' > .streamlit/secrets.toml

# 4. 실행
streamlit run app.py
```

---

## 📊 설문 분석 기반 개발

### 전문가 18명 설문 결과

| 니즈 | 비율 | 구현 기능 |
|------|------|----------|
| 가격 정보 | 83% | ✅ 견적 계산기 |
| 일정표 자동화 | 59% | ✅ 일정표 생성 |
| 위치/거리 | 44% | ✅ 자동 거리 표시 |
| 청결/시설 | 100% | ✅ 청결도 점수 |
| 지역별 추천 | 41% | ✅ 실시간 필터 |

---

## 🛠️ 기술 스택

- **Frontend**: Streamlit
- **AI**: OpenAI GPT-4o-mini / GPT-4o
- **Workflow**: LangGraph
- **Vector DB**: ChromaDB
- **Embeddings**: OpenAI Embeddings

---

## 📁 프로젝트 구조

```
gangwon-tourism-chatbot/
│
├── app.py                    # 메인 Streamlit 앱
├── sample_data.py            # 기본 샘플 데이터
├── enhanced_data.py          # 확장 데이터
├── requirements.txt          # 패키지 의존성
│
├── .streamlit/
│   ├── config.toml           # Streamlit 설정
│   └── secrets.toml.example  # API 키 예시
│
├── .gitignore                # Git 제외 파일
├── README.md                 # 이 파일
└── DEPLOYMENT_GUIDE.md       # 배포 가이드
```

---

## 🔐 API 키 설정

### Streamlit Cloud 배포 시

1. Streamlit Cloud 앱 설정
2. Secrets 섹션 열기
3. 아래 내용 입력:
   ```toml
   OPENAI_API_KEY = "sk-your-api-key-here"
   ```

### 로컬 실행 시

1. `.streamlit/secrets.toml` 파일 생성
2. API 키 입력:
   ```toml
   OPENAI_API_KEY = "sk-your-api-key-here"
   ```

⚠️ **중요**: `secrets.toml` 파일은 절대 GitHub에 커밋하지 마세요!

---

## 📈 데이터 정보

- **숙소**: 5개 (상세 정보 포함)
- **맛집**: 4개 (가격, 운영시간 포함)
- **관광지**: 4개 (입장료, 주차 정보)
- **패키지**: 2개 (상세 일정 + 비용)
- **리뷰**: 20건 (실제 네이버 지도 기반)

---

## 💡 사용 예시

### 가격 문의 (설문 1위 니즈!)

```
Q: "춘천 1박 2일 가족 4명 여행 비용?"

A: 춘천 1박 2일 예상 비용 안내드립니다.

💰 숙박: 150,000원
🍽️ 식비: 360,000원
🎫 입장료: 180,000원
🚗 교통비: 200,000원
━━━━━━━━━━━━━━
총: 890,000원
1인당: 222,500원
```

### 숙소 추천

```
Q: "강릉 바다 보이는 숙소 추천"

A: 강릉씨베이호텔 ⭐ 4.8
📍 강릉시 창해로
💰 오션뷰: 200,000원/박
🧹 청결도: 4.9/5.0
📅 최근 예약: 203건
🍽️ 조식: 포함 (뷔페)
🚗 경포해변: 2km (차로 5분)
```

---

## 🌟 주요 특징

### vs 기존 챗봇

| 항목 | 일반 챗봇 | 본 챗봇 |
|------|----------|---------|
| 가격 정보 | 간단 언급 | 상세 견적 |
| 일정표 | 수동 작성 | 자동 생성 |
| 필터링 | 없음 | 실시간 |
| 청결도 | 언급 없음 | 점수 표시 |
| 예약 사례 | 없음 | 건수 표시 |

### vs ChatGPT

- ✅ 강원도 지역 특화 데이터
- ✅ 실시간 가격 견적
- ✅ 일정표 자동 생성
- ✅ 청결도 & 신뢰도 정보
- ✅ 즉시 사용 가능한 필터

---

## 🚀 Streamlit Cloud 배포

상세한 배포 가이드는 [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)를 참조하세요.

### 빠른 배포 (5분)

1. **GitHub 레포지토리 생성**
2. **파일 업로드** (`.gitignore` 확인!)
3. **Streamlit Cloud 연결**
4. **Secrets 설정** (API 키)
5. **배포 완료!** 🎉

---

## 📞 문의 및 지원

- **개발팀**: 강원대학교 강원지능화혁신센터
- **담당 교수**: 김우주
- **연구원**: 정현철, 안소라, 이래경, 이재명
- **이메일**: brad0702@kangwon.ac.kr

---

## 📝 라이선스

이 프로젝트는 교육 및 연구 목적으로 개발되었습니다.

---

## 🙏 감사의 글

- **설문 참여**: 관광업 전문가 18명
- **기술 지원**: Anthropic Claude, OpenAI
- **플랫폼**: Streamlit Community Cloud

---

## 🔄 업데이트

### v2.0 (2025-11-09)
- ✅ 웹 배포 버전 출시
- ✅ Streamlit Cloud 최적화
- ✅ API 키 관리 개선

### v1.0 (2025-11-08)
- ✅ 설문 기반 고도화
- ✅ 5개 전문 탭 구현
- ✅ 50+ 상세 데이터

---

**설치 없이 웹에서 바로 사용하세요!** 🌐

[👉 지금 바로 사용하기](#) ← 배포 후 URL 업데이트
