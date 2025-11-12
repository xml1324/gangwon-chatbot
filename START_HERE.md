# 🎯 최종 가이드 - Streamlit Cloud 배포

## 📌 사용할 파일 (Streamlit Cloud용)

### ✅ 필수 파일 3개

| 순번 | 파일명 | 크기 | 용도 | 다운로드 |
|------|--------|------|------|----------|
| 1 | **app_cloud.py** | 21KB | 메인 애플리케이션 | [다운로드](computer:///mnt/user-data/outputs/app_cloud.py) |
| 2 | **requirements.txt** | 134B | Python 패키지 목록 | [다운로드](computer:///mnt/user-data/outputs/requirements.txt) |
| 3 | **gitignore** | 406B | Git 설정 파일 | [다운로드](computer:///mnt/user-data/outputs/gitignore) |

> ⚠️ **주의**: `gitignore` 파일을 다운로드 후 `.gitignore`로 이름을 변경하세요!

### 📖 문서 파일 (참고용)

| 파일명 | 내용 | 추천도 |
|--------|------|--------|
| **CLOUD_DEPLOY_SUMMARY.md** | 종합 배포 가이드 | ⭐⭐⭐ 필독! |
| **QUICK_DEPLOY.md** | 5분 빠른 배포 | ⭐⭐⭐ 처음 사용자 |
| **DEPLOY_GUIDE.md** | 상세 배포 및 문제 해결 | ⭐⭐ 문제 발생 시 |

---

## 🚀 3분 배포 가이드

### 1️⃣ GitHub 저장소 준비

현재 상태:
```
your-repo/
└── 리뷰/              ✅ 이미 있음
    ├── 맛집 리뷰/
    ├── 명소 리뷰/
    ├── 병원 리뷰/
    └── 카페 리뷰/
```

추가할 파일:
```
your-repo/
├── app_cloud.py       ⬅️ 추가
├── requirements.txt   ⬅️ 추가
├── .gitignore        ⬅️ 추가 (gitignore → .gitignore로 이름 변경)
└── 리뷰/              ✅ 이미 있음
```

### 2️⃣ 파일 업로드

**방법 A: GitHub 웹 인터페이스**
1. GitHub 저장소 페이지 접속
2. "Add file" → "Upload files" 클릭
3. 3개 파일 드래그 앤 드롭
4. gitignore → .gitignore로 이름 변경
5. Commit changes 클릭

**방법 B: Git 명령어**
```bash
cd /path/to/your-repo

# 파일 복사 (다운로드한 위치에서)
cp /path/to/downloads/app_cloud.py .
cp /path/to/downloads/requirements.txt .
cp /path/to/downloads/gitignore .gitignore

# Git에 추가
git add app_cloud.py requirements.txt .gitignore
git commit -m "Add Streamlit Cloud app"
git push origin main
```

### 3️⃣ Streamlit Cloud 배포

1. **https://share.streamlit.io** 접속
2. GitHub으로 로그인
3. **"New app"** 클릭
4. 설정 입력:
   - Repository: `your-username/your-repo`
   - Branch: `main`
   - Main file path: `app_cloud.py`

5. **Secrets 설정** (중요! ⚠️)
   - **Advanced settings** 클릭
   - **Secrets** 섹션에 입력:
   ```toml
   OPENAI_API_KEY = "sk-your-openai-api-key-here"
   ```

6. **"Deploy!"** 버튼 클릭

### 4️⃣ 완료!

배포 완료 후:
```
✅ Your app is live at:
https://your-app-name.streamlit.app
```

---

## 💡 주요 특징

### Streamlit Cloud 버전 (app_cloud.py)

| 특징 | 설명 |
|------|------|
| **데이터 경로** | `리뷰/` 폴더 (GitHub 저장소) |
| **벡터 스토어** | 메모리 캐싱 (@st.cache_resource) |
| **API 키** | Streamlit Cloud Secrets 사용 |
| **자동 로딩** | 앱 시작 시 리뷰 데이터 자동 로딩 |
| **첫 실행** | 첫 질문 시 벡터 스토어 생성 (1-2분) |
| **이후 실행** | 빠른 응답 (벡터 스토어 재사용) |

### 작동 프로세스

```
앱 시작
  ↓
리뷰 데이터 자동 로딩 (30초)
  ↓
사이드바에 통계 표시
  ↓
사용자가 첫 질문 입력
  ↓
벡터 스토어 생성 (1-2분, 한 번만)
  ↓
AI 답변 생성 (2-3초)
  ↓
이후 질문은 빠르게 응답!
```

---

## 📊 GitHub 저장소 구조

### 최종 구조

```
your-repo/
│
├── app_cloud.py          ✅ 메인 앱
├── requirements.txt      ✅ 패키지 목록
├── .gitignore           ✅ Git 설정
├── README.md            (선택) 프로젝트 설명
│
└── 리뷰/                 ✅ 리뷰 데이터
    │
    ├── 맛집 리뷰/
    │   ├── naver_review_1.5닭갈비_본점.xlsx
    │   ├── naver_review_798삼천동고깃집.xlsx
    │   └── ...
    │
    ├── 명소 리뷰/
    │   ├── naver_review_남이섬.xlsx
    │   └── ...
    │
    ├── 병원 리뷰/
    │   └── ...
    │
    └── 카페 리뷰/
        └── ...
```

### 파일 설명

**app_cloud.py**
- Streamlit Cloud 환경에 최적화
- 리뷰 데이터 자동 로딩
- 벡터 스토어 메모리 캐싱
- 2개 탭: AI 챗봇, 리뷰 분석

**requirements.txt**
```
streamlit>=1.28.0
langchain>=0.1.0
langchain-openai>=0.0.5
langchain-community>=0.0.20
chromadb>=0.4.22
pandas>=2.0.0
openpyxl>=3.1.0
```

**.gitignore**
- Python 캐시 파일 무시
- 로컬 secrets.toml 무시
- IDE 설정 파일 무시

---

## 🔧 Streamlit Cloud Secrets 설정

### Secrets란?

- API 키 등 민감 정보를 안전하게 저장
- GitHub에 올라가지 않음
- 앱에서 `st.secrets`로 접근

### 설정 방법

1. Streamlit Cloud 앱 대시보드
2. Settings → Secrets
3. 다음 내용 입력:

```toml
OPENAI_API_KEY = "sk-proj-..."
```

4. Save 클릭
5. 앱 자동 재시작

### 주의사항

- ✅ 따옴표 포함해서 입력
- ✅ 키 이름 정확히: `OPENAI_API_KEY`
- ✅ 값 앞뒤 공백 없이
- ❌ GitHub에 절대 업로드 금지

---

## 🎯 배포 후 확인

### 1. 앱 접속

```
https://your-app-name.streamlit.app
```

### 2. 사이드바 확인

```
⚙️ 설정
  ✅ API 키가 설정되었습니다
  
📊 리뷰 데이터
  총 리뷰: 1,234개
  
  카테고리별 상세
  - 맛집 리뷰: 456개
  - 명소 리뷰: 234개
  - 병원 리뷰: 123개
  - 카페 리뷰: 421개
```

### 3. 첫 질문

```
춘천에서 재방문율 높은 맛집 추천해줘
```

### 4. 벡터 스토어 생성

```
🤔 답변 생성 중...
(1-2분 소요 - 첫 질문만)
```

### 5. 이후 질문

```
가족 여행으로 좋은 명소 알려줘
(2-3초 빠른 응답!)
```

---

## 🐛 문제 해결

### API 키 오류

**증상:**
```
⚠️ API 키가 필요합니다
```

**해결:**
1. Streamlit Cloud → Settings → Secrets
2. `OPENAI_API_KEY` 확인
3. 올바른 형식으로 입력
4. Save 클릭

### 리뷰 데이터 없음

**증상:**
```
❌ 리뷰 데이터를 찾을 수 없습니다
```

**해결:**
1. GitHub 저장소에 "리뷰" 폴더 확인
2. 폴더 이름 정확한지 확인 (한글)
3. 4개 카테고리 폴더 모두 존재
4. 엑셀 파일 확인

### 앱 시작 안됨

**해결:**
1. Settings → View logs (로그 확인)
2. Settings → Reboot app
3. 파일명 확인: `app_cloud.py`
4. 저장소 권한 확인

### 메모리 부족

**증상:**
```
앱이 느려지거나 멈춤
```

**해결:**
- 리뷰 파일 수 줄이기
- 사이드바에서 검색 결과 수 줄이기 (8 → 5)

---

## 📱 공유하기

배포 완료 후:

### URL 공유
```
https://your-app-name.streamlit.app
```

### SNS 포스팅
```
🏔️ 강원도 관광 AI 컨시어지 오픈!

실제 네이버 리뷰를 분석하여
맛집, 명소, 카페를 추천해드립니다.

지금 바로 체험해보세요!
👉 https://your-app-name.streamlit.app
```

### QR 코드
- https://www.qr-code-generator.com
- URL 입력하여 QR 코드 생성

---

## 🔄 업데이트 방법

### 코드 수정
```bash
# app_cloud.py 수정 후
git add app_cloud.py
git commit -m "Update feature"
git push

# Streamlit Cloud 자동 재배포!
```

### 리뷰 데이터 추가
```bash
# 새 엑셀 파일 추가
git add 리뷰/
git commit -m "Add new reviews"
git push

# 자동 재배포
```

### Secrets 변경
```
Settings → Secrets → 편집 → Save
(앱 자동 재시작)
```

---

## ✅ 최종 체크리스트

### 배포 전
- [ ] app_cloud.py 다운로드
- [ ] requirements.txt 다운로드
- [ ] gitignore 다운로드
- [ ] gitignore → .gitignore 이름 변경
- [ ] GitHub 저장소에 업로드
- [ ] "리뷰" 폴더 구조 확인
- [ ] Git push 완료

### Streamlit Cloud
- [ ] share.streamlit.io 로그인
- [ ] New app 생성
- [ ] Repository 선택
- [ ] Main file: app_cloud.py
- [ ] Secrets 설정: OPENAI_API_KEY
- [ ] Deploy 클릭

### 배포 후
- [ ] 앱 URL 접속
- [ ] API 키 확인
- [ ] 리뷰 데이터 로딩
- [ ] 첫 질문 시도
- [ ] 벡터 스토어 생성
- [ ] 정상 응답 확인
- [ ] URL 공유!

---

## 📚 추가 도움말

| 상황 | 참고 문서 |
|------|-----------|
| 처음 배포 | QUICK_DEPLOY.md |
| 문제 발생 | DEPLOY_GUIDE.md |
| 전체 이해 | CLOUD_DEPLOY_SUMMARY.md |

---

## 🎉 완성!

모든 준비가 끝났습니다!

1. **3개 파일 다운로드**
   - app_cloud.py
   - requirements.txt
   - gitignore

2. **GitHub에 업로드**
   - gitignore → .gitignore 이름 변경

3. **Streamlit Cloud 배포**
   - share.streamlit.io
   - Secrets 설정

4. **완료!**
   - 앱 URL 공유
   - 사용자와 함께 즐기기

---

**배포 성공을 기원합니다!** 🚀✨

강원대학교 학생창의자율과제 7팀

문제가 있으면 DEPLOY_GUIDE.md를 참고하세요!
