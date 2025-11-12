# 🎯 Streamlit Cloud 배포 - 최종 가이드

## 📦 제공 파일 (Streamlit Cloud용)

### ✅ 필수 파일 (GitHub 저장소에 업로드)

| 파일명 | 크기 | 용도 | 위치 |
|--------|------|------|------|
| **app_cloud.py** | 21KB | 메인 애플리케이션 | 저장소 루트 |
| **requirements.txt** | 134B | 패키지 목록 | 저장소 루트 |
| **gitignore** | 406B | Git 설정 (.gitignore로 이름 변경) | 저장소 루트 |

### 📖 문서 파일 (참고용)

| 파일명 | 내용 |
|--------|------|
| **QUICK_DEPLOY.md** | ⚡ 5분 빠른 배포 가이드 |
| **DEPLOY_GUIDE.md** | 📚 상세 배포 및 문제 해결 |

---

## 🚀 빠른 시작 (5분!)

### 1️⃣ GitHub 저장소 구조 확인

```
your-repo/               (GitHub 저장소)
├── app_cloud.py         ✅ 이 파일 추가
├── requirements.txt     ✅ 이 파일 추가
├── .gitignore          ✅ gitignore 파일을 .gitignore로 이름 변경
├── README.md           (선택)
│
└── 리뷰/                ✅ 이미 있음
    ├── 맛집 리뷰/
    │   ├── naver_review_1.5닭갈비_본점.xlsx
    │   └── ...
    ├── 명소 리뷰/
    ├── 병원 리뷰/
    └── 카페 리뷰/
```

### 2️⃣ 파일 업로드

```bash
# 저장소 위치로 이동
cd /path/to/your-repo

# 제공된 파일 복사
# - app_cloud.py
# - requirements.txt
# - gitignore → .gitignore로 이름 변경

# Git에 추가
git add app_cloud.py requirements.txt .gitignore
git commit -m "Add Streamlit Cloud app"
git push origin main
```

### 3️⃣ Streamlit Cloud 배포

1. **https://share.streamlit.io** 접속
2. GitHub 계정으로 로그인
3. **"New app"** 클릭
4. 설정:
   - Repository: `your-username/your-repo`
   - Branch: `main`
   - Main file: `app_cloud.py`
5. **Advanced settings → Secrets**:
   ```toml
   OPENAI_API_KEY = "sk-your-openai-api-key-here"
   ```
6. **"Deploy!"** 클릭

### 4️⃣ 완료!

앱이 배포되면:
```
✅ Your app is live at:
https://your-app-name.streamlit.app
```

---

## 🎯 주요 차이점 (로컬 vs Cloud)

| 항목 | 로컬 버전 (app_final.py) | Cloud 버전 (app_cloud.py) |
|------|-------------------------|---------------------------|
| 데이터 경로 | `naver_reviews/` | `리뷰/` |
| 벡터 스토어 | 디스크 저장 (`chroma_db/`) | 메모리 캐싱 |
| API 키 | `.streamlit/secrets.toml` | Streamlit Cloud Secrets |
| 시작 속도 | 즉시 (캐시 사용) | 첫 질문 시 생성 |
| 재시작 | 빠름 (캐시 재사용) | 벡터 스토어 재생성 |

---

## 💡 Streamlit Cloud 특징

### ✅ 장점
- 무료 호스팅
- 자동 배포 (Git push → 재배포)
- HTTPS 기본 제공
- 쉬운 공유 (URL만 전달)
- Secrets 관리 기능

### ⚠️ 제약사항
- 읽기 전용 파일 시스템
- RAM: 1GB (무료 플랜)
- 7일 미사용 시 수면 모드
- 벡터 스토어 재생성 필요 (재시작 시)

### 🔄 작동 방식

1. **앱 시작**
   - GitHub에서 코드 가져오기
   - 패키지 설치
   - 앱 실행

2. **리뷰 데이터 로딩**
   - `리뷰/` 폴더에서 자동 로딩
   - `@st.cache_data`로 캐싱

3. **벡터 스토어**
   - 첫 질문 시 생성
   - `@st.cache_resource`로 메모리 캐싱
   - 모든 사용자가 공유

4. **재시작 시**
   - 리뷰 데이터: 캐시에서 로드 (빠름)
   - 벡터 스토어: 재생성 필요 (1-2분)

---

## 📊 성능 고려사항

### 메모리 사용

| 항목 | 예상 메모리 |
|------|------------|
| 앱 기본 | ~100MB |
| 리뷰 데이터 | ~50-100MB |
| 벡터 스토어 | ~200-400MB |
| **총합** | **~350-600MB** |

**무료 플랜 1GB로 충분합니다!** ✅

### 최적화 방법

리뷰 데이터가 너무 많으면:

```python
# app_cloud.py에서 조정 가능

# 1. 문서당 리뷰 수 줄이기
top_reviews = sorted_reviews[:10]  # → [:5]

# 2. 청크 크기 줄이기
chunk_size=1000  # → 500

# 3. 검색 결과 수 줄이기
search_k = 8  # → 5
```

---

## 🐛 문제 해결

### 배포 실패

**확인:**
```
✅ app_cloud.py 파일명 정확
✅ requirements.txt 존재
✅ 리뷰 폴더 구조 정확
✅ GitHub에 푸시 완료
```

**해결:**
- 배포 로그 확인
- Settings → Reboot app

### API 키 오류

**증상:**
```
⚠️ API 키가 필요합니다
```

**해결:**
1. Settings → Secrets
2. 다음 내용 입력:
   ```toml
   OPENAI_API_KEY = "sk-..."
   ```
3. Save 클릭
4. 앱 자동 재시작

### 리뷰 데이터 없음

**증상:**
```
⚠️ '맛집 리뷰' 폴더를 찾을 수 없습니다
```

**확인:**
- GitHub 저장소에 "리뷰" 폴더 존재
- 폴더 이름 정확 (한글 주의)
- 4개 카테고리 폴더 모두 존재

### 메모리 부족

**증상:**
```
앱이 느려지거나 멈춤
```

**해결:**
1. 리뷰 파일 수 줄이기
2. 위의 최적화 방법 적용
3. 청크 크기/검색 결과 수 조정

---

## 🔄 업데이트 방법

### 코드 수정

```bash
# app_cloud.py 수정 후
git add app_cloud.py
git commit -m "Update feature"
git push

# Streamlit Cloud가 자동 감지
# → 자동 재배포 (1-2분)
```

### 리뷰 데이터 추가

```bash
# 새 엑셀 파일 추가
git add 리뷰/
git commit -m "Add new review data"
git push

# 자동 재배포
```

### Secrets 수정

```
Settings → Secrets → 편집 → Save
앱 자동 재시작
```

---

## 📱 공유하기

배포 완료 후:

1. **URL 공유**
   ```
   https://your-app-name.streamlit.app
   ```

2. **SNS 공유**
   - 앱 설명 추가
   - 스크린샷 첨부

3. **임베딩** (선택)
   ```html
   <iframe src="https://your-app-name.streamlit.app" 
           width="100%" height="800px">
   </iframe>
   ```

---

## ✅ 배포 체크리스트

### GitHub 준비
- [ ] app_cloud.py 업로드
- [ ] requirements.txt 업로드
- [ ] .gitignore 업로드 (gitignore → .gitignore)
- [ ] 리뷰/ 폴더 확인
- [ ] 4개 카테고리 폴더 확인
- [ ] 엑셀 파일 확인
- [ ] Git push 완료

### Streamlit Cloud 설정
- [ ] 계정 생성/로그인
- [ ] Repository 선택
- [ ] Branch: main
- [ ] Main file: app_cloud.py
- [ ] Secrets 입력: OPENAI_API_KEY
- [ ] Deploy 클릭

### 배포 확인
- [ ] 앱 URL 접속
- [ ] 사이드바: API 키 확인
- [ ] 사이드바: 리뷰 데이터 로딩
- [ ] 리뷰 통계 표시
- [ ] 첫 질문 시도
- [ ] 벡터 스토어 생성
- [ ] 정상 응답 확인

---

## 🎓 다음 단계

배포 성공 후:

1. **앱 커스터마이징**
   - 배너 수정
   - 프롬프트 개선
   - UI 조정

2. **데이터 확장**
   - 더 많은 리뷰 추가
   - 새로운 카테고리
   - 정기 업데이트

3. **고급 기능**
   - 분석 기능 추가
   - 필터링 강화
   - 시각화 추가

---

## 📚 추가 자료

| 문서 | 내용 |
|------|------|
| QUICK_DEPLOY.md | 5분 빠른 배포 |
| DEPLOY_GUIDE.md | 상세 가이드 |
| [Streamlit Docs](https://docs.streamlit.io) | 공식 문서 |

---

## 🎉 완료!

이제 Streamlit Cloud에서 여러분의 AI 컨시어지가 작동합니다!

**앱 URL:**
```
https://your-app-name.streamlit.app
```

**문제가 있나요?**
- DEPLOY_GUIDE.md의 문제 해결 섹션 참고
- Streamlit Community Forum 방문

---

**배포 성공을 기원합니다!** 🚀✨

강원대학교 학생창의자율과제 7팀
