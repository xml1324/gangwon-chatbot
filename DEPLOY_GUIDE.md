# 🚀 Streamlit Cloud 배포 가이드

## 📋 필요한 파일 목록

GitHub 저장소에 다음 파일들이 있어야 합니다:

```
your-repo/
├── app_cloud.py          ✅ 메인 앱 파일
├── requirements.txt      ✅ 패키지 목록
├── .gitignore           ✅ Git 무시 파일
├── README.md            📖 프로젝트 설명 (선택)
│
└── 리뷰/                 📊 리뷰 데이터 폴더
    ├── 맛집 리뷰/
    │   ├── naver_review_1.5닭갈비_본점.xlsx
    │   └── ...
    ├── 명소 리뷰/
    ├── 병원 리뷰/
    └── 카페 리뷰/
```

## 🔧 1단계: GitHub 저장소 준비

### 1-1. 저장소 생성
1. GitHub에서 새 저장소 생성
2. 저장소를 로컬에 clone

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

### 1-2. 파일 업로드

```bash
# 필수 파일 복사
cp app_cloud.py your-repo/
cp requirements.txt your-repo/
cp .gitignore your-repo/

# 리뷰 데이터는 이미 "리뷰" 폴더에 있다고 하셨으므로 생략
```

### 1-3. Git에 푸시

```bash
git add .
git commit -m "Initial commit: Streamlit app with review data"
git push origin main
```

## ☁️ 2단계: Streamlit Cloud 배포

### 2-1. Streamlit Cloud 계정 설정

1. https://share.streamlit.io 방문
2. GitHub 계정으로 로그인
3. "New app" 클릭

### 2-2. 앱 설정

**Repository 설정:**
- Repository: `your-username/your-repo`
- Branch: `main`
- Main file path: `app_cloud.py`

### 2-3. Secrets 설정 (중요! ⚠️)

**Settings → Secrets** 섹션에서 다음 내용 입력:

```toml
OPENAI_API_KEY = "sk-your-openai-api-key-here"
```

**주의사항:**
- API 키는 반드시 Secrets에 설정 (코드에 하드코딩 금지)
- 따옴표 포함해서 입력
- 저장 후 앱이 자동으로 재시작됨

### 2-4. Deploy!

"Deploy!" 버튼 클릭하면 자동으로 배포가 시작됩니다.

## ⏱️ 3단계: 배포 프로세스

### 배포 시간
```
1. 저장소 Clone         (~30초)
2. 패키지 설치           (~2-3분)
3. 앱 시작              (~30초)
4. 리뷰 데이터 로딩      (~30초-1분)
5. 벡터 스토어 생성      (첫 사용자가 질문할 때)
```

**총 소요 시간:** 약 4-5분

### 배포 로그 확인

배포 중 다음과 같은 로그를 확인할 수 있습니다:
```
Cloning repository...
Installing requirements...
Starting app...
App is live!
```

## 🎯 4단계: 앱 사용

### 4-1. 앱 URL
배포 완료 후 다음과 같은 URL이 생성됩니다:
```
https://your-app-name.streamlit.app
```

### 4-2. 첫 실행
1. URL 접속
2. 리뷰 데이터가 자동으로 로딩됨 (사이드바에서 확인)
3. AI 챗봇 탭에서 질문 입력
4. 첫 질문 시 벡터 스토어가 자동 생성됨 (1-2분 소요)
5. 이후 질문은 빠르게 응답!

## 💡 중요 사항

### Streamlit Cloud의 특징

#### 1. **읽기 전용 파일 시스템**
- GitHub 저장소의 파일은 읽기만 가능
- 벡터 스토어는 메모리에 캐싱 (`@st.cache_resource`)
- 앱 재시작 시 벡터 스토어 재생성 필요

#### 2. **메모리 캐싱**
```python
@st.cache_resource  # 모든 사용자가 공유
def create_vector_store(...):
    # 벡터 스토어 생성
    # 앱 재시작 전까지 메모리에 유지
```

#### 3. **무료 플랜 제한**
- CPU: 공유 리소스
- RAM: 1GB
- 앱 수: 무제한
- 수면 모드: 7일 미사용 시

#### 4. **수면 모드 해제**
- 7일 미사용 시 자동 수면
- 다시 접속하면 자동 wake-up
- wake-up 시 벡터 스토어 재생성 필요

## 🔄 업데이트 방법

### 코드 업데이트
```bash
# 코드 수정 후
git add .
git commit -m "Update: feature description"
git push origin main

# Streamlit Cloud에서 자동으로 감지하여 재배포
```

### 리뷰 데이터 업데이트
```bash
# 새 리뷰 파일 추가
cp new-review.xlsx 리뷰/맛집\ 리뷰/

git add 리뷰/
git commit -m "Add new review data"
git push origin main

# 앱이 자동으로 재시작되어 새 데이터 로딩
```

## 🐛 문제 해결

### 1. 앱이 시작되지 않음

**확인 사항:**
- [ ] `requirements.txt` 파일 존재
- [ ] `app_cloud.py` 파일 경로 정확
- [ ] GitHub 저장소가 public 또는 권한 설정됨

**해결:**
- 배포 로그 확인
- Settings → Reboot app

### 2. API 키 오류

**증상:**
```
OpenAI API key not found
```

**해결:**
1. Settings → Secrets
2. `OPENAI_API_KEY` 확인
3. 올바른 형식인지 확인:
   ```toml
   OPENAI_API_KEY = "sk-..."
   ```
4. Save 클릭

### 3. 리뷰 데이터를 찾을 수 없음

**증상:**
```
❌ 리뷰 데이터를 찾을 수 없습니다
```

**확인:**
- GitHub 저장소에 "리뷰" 폴더 존재
- 폴더 구조가 올바른지 확인:
  ```
  리뷰/
  ├── 맛집 리뷰/
  ├── 명소 리뷰/
  ├── 병원 리뷰/
  └── 카페 리뷰/
  ```

### 4. 메모리 부족

**증상:**
```
MemoryError or app becomes slow
```

**해결:**
- 리뷰 데이터 양 줄이기
- `search_k` 값 줄이기 (8 → 5)
- 청크 크기 줄이기

### 5. 벡터 스토어 생성 오류

**증상:**
```
Error creating vector store
```

**확인:**
- API 키가 유효한지
- 충분한 API 크레딧이 있는지
- 네트워크 연결 확인

**해결:**
- 앱 재시작 (Settings → Reboot)
- 로그에서 상세 오류 확인

## 📊 성능 최적화

### 1. 리뷰 데이터 최적화
```python
# 문서당 최대 리뷰 수 조정
top_reviews = sorted_reviews[:10]  # 10 → 5
```

### 2. 검색 결과 수 조정
```python
# 사이드바 슬라이더에서 조정
search_k = 8  # 기본값
# 메모리 부족 시: 5
# 더 상세한 답변: 10-15
```

### 3. 청크 크기 조정
```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,    # 메모리 부족 시: 500
    chunk_overlap=200   # 메모리 부족 시: 100
)
```

## 🎯 배포 체크리스트

배포 전 확인:

- [ ] `app_cloud.py` 파일 준비
- [ ] `requirements.txt` 파일 준비
- [ ] `.gitignore` 파일 준비
- [ ] "리뷰" 폴더 구조 확인
- [ ] 4개 카테고리 폴더 모두 존재
- [ ] 엑셀 파일 업로드 완료
- [ ] GitHub에 푸시 완료

Streamlit Cloud 설정:

- [ ] Streamlit Cloud 계정 생성
- [ ] Repository 연결
- [ ] Main file path: `app_cloud.py`
- [ ] Secrets에 API 키 설정
- [ ] Deploy 클릭

배포 후 확인:

- [ ] 앱 URL 접속 가능
- [ ] 리뷰 데이터 로딩 확인
- [ ] API 키 정상 작동
- [ ] 첫 질문 시 벡터 스토어 생성
- [ ] 이후 질문 빠른 응답

## 📱 공유하기

배포 완료 후:

1. **앱 URL 공유**
   ```
   https://your-app-name.streamlit.app
   ```

2. **QR 코드 생성** (선택)
   - https://www.qr-code-generator.com
   - 앱 URL 입력
   - QR 코드 다운로드

3. **SNS 공유**
   - 앱 URL과 함께 설명 추가
   - 스크린샷 첨부

## 🆘 추가 도움말

### 공식 문서
- Streamlit Cloud: https://docs.streamlit.io/streamlit-community-cloud
- LangChain: https://python.langchain.com
- Chroma: https://docs.trychroma.com

### 커뮤니티
- Streamlit Forum: https://discuss.streamlit.io
- GitHub Issues: 저장소 이슈 페이지

---

**배포 성공을 기원합니다!** 🎉

문제가 발생하면 배포 로그를 확인하고, 위 문제 해결 섹션을 참고하세요.
