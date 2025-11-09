# 🌐 Streamlit Cloud 배포 가이드

**강원도 관광 AI 컨시어지 웹 앱**

---

## 🚀 배포 준비

### 필요한 것
- GitHub 계정
- OpenAI API 키
- Streamlit Cloud 계정 (무료)

---

## 📁 1단계: GitHub 레포지토리 생성

### 1-1. GitHub에서 새 레포지토리 만들기

1. [GitHub](https://github.com)에 로그인
2. 우측 상단 `+` → `New repository` 클릭
3. 레포지토리 설정:
   - **이름**: `gangwon-tourism-chatbot` (원하는 이름)
   - **공개 설정**: Public (무료 배포를 위해 필수)
   - **README**: 체크 안 함 (이미 있음)
   - `Create repository` 클릭

### 1-2. 로컬 파일을 GitHub에 업로드

**방법 1: GitHub 웹 인터페이스 (쉬움)**

1. 생성된 레포지토리 페이지에서 `uploading an existing file` 클릭
2. 모든 파일 드래그 앤 드롭:
   - `app.py`
   - `sample_data.py`
   - `enhanced_data.py`
   - `requirements.txt`
   - `.streamlit/config.toml`
   - `.streamlit/secrets.toml.example`
   - `README.md`
3. `Commit changes` 클릭

**방법 2: Git 명령어 (터미널 사용)**

```bash
# 프로젝트 폴더에서
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/your-username/gangwon-tourism-chatbot.git
git push -u origin main
```

⚠️ **주의**: `.streamlit/secrets.toml` 파일은 절대 업로드하지 마세요!

---

## 🔐 2단계: .gitignore 설정

레포지토리에 `.gitignore` 파일 추가:

```
# Secrets
.streamlit/secrets.toml
*.toml
!.streamlit/config.toml

# Python
__pycache__/
*.py[cod]
.Python
venv/
.env

# Streamlit
.streamlit/secrets.toml

# IDE
.vscode/
.idea/
```

---

## ☁️ 3단계: Streamlit Cloud 배포

### 3-1. Streamlit Cloud 가입

1. [Streamlit Cloud](https://streamlit.io/cloud) 접속
2. `Sign up` 클릭
3. GitHub 계정으로 로그인

### 3-2. 앱 배포하기

1. Streamlit Cloud 대시보드에서 `New app` 클릭

2. 앱 설정:
   ```
   Repository: your-username/gangwon-tourism-chatbot
   Branch: main
   Main file path: app.py
   ```

3. `Deploy!` 클릭

### 3-3. Secrets 설정 (중요! ⭐)

1. 앱 배포 중 또는 배포 후, 앱 대시보드에서 `⚙️ Settings` 클릭

2. 왼쪽 메뉴에서 `Secrets` 선택

3. 아래 내용 입력:
   ```toml
   OPENAI_API_KEY = "sk-your-actual-api-key-here"
   ```

4. `Save` 클릭

5. 앱이 자동으로 재시작됩니다

---

## ✅ 4단계: 배포 확인

### 배포 성공 시

- URL 생성: `https://your-app-name.streamlit.app`
- 누구나 접속 가능한 공개 웹앱

### 확인 사항

1. **API 키 작동 확인**:
   - 사이드바에 "✅ API 키가 설정되었습니다" 표시되는지 확인

2. **기능 테스트**:
   - Tab 1: AI 상담 테스트
   - Tab 2: 견적 계산기 작동
   - Tab 3: 일정표 생성
   - Tab 4: 숙소 검색
   - Tab 5: 가격 비교

### 문제 해결

**"API 키가 필요합니다" 오류**:
- Settings → Secrets 확인
- API 키 형식 확인 (`OPENAI_API_KEY = "sk-..."`)
- 앱 재시작 (Reboot app)

**"Module not found" 오류**:
- `requirements.txt` 파일 확인
- GitHub 레포지토리에 올바르게 업로드되었는지 확인

**앱이 느려요**:
- 무료 플랜은 리소스 제한이 있습니다
- 사용하지 않을 때 자동 슬립 모드

---

## 🎨 5단계: 커스터마이징 (선택사항)

### 앱 도메인 변경

Settings → General → Custom subdomain:
```
gangwon-tourism-ai.streamlit.app
```

### 앱 설명 추가

Settings → General → App description:
```
강원도 관광 전문 AI 컨시어지 - 가격 견적, 일정표 생성, 실시간 추천
```

### 비밀번호 보호 (유료 플랜)

Settings → Sharing → Password protection

---

## 📊 6단계: 모니터링

### 사용 통계

- Streamlit Cloud 대시보드에서 확인
- 방문자 수
- 리소스 사용량
- 에러 로그

### API 사용량 확인

- [OpenAI Dashboard](https://platform.openai.com/usage) 에서 확인
- API 키 사용량 모니터링
- 비용 확인

---

## 🔄 7단계: 업데이트

### 코드 수정 시

1. 로컬에서 파일 수정
2. GitHub에 푸시:
   ```bash
   git add .
   git commit -m "Update feature"
   git push
   ```
3. Streamlit Cloud가 자동으로 재배포

### Secrets 변경 시

1. Streamlit Cloud → Settings → Secrets
2. 내용 수정
3. Save → 자동 재시작

---

## 💡 팁 & 모범 사례

### 성능 최적화

1. **캐싱 활용**:
   - `@st.cache_data`, `@st.cache_resource` 사용 (이미 구현됨)

2. **모델 선택**:
   - gpt-4o-mini 권장 (속도 + 비용 최적화)

3. **세션 관리**:
   - 대화 히스토리 제한 (메모리 절약)

### 보안

1. **API 키**:
   - 절대 GitHub에 커밋하지 말 것
   - Streamlit Secrets만 사용

2. **사용량 제한**:
   - OpenAI API 사용량 한도 설정
   - 비용 알림 설정

### 사용자 경험

1. **에러 처리**:
   - 친절한 에러 메시지 (이미 구현됨)
   - 재시도 안내

2. **로딩 시간**:
   - 처음 실행 시 1-2분 소요 (정상)
   - 이후 빠른 응답

---

## 📞 문제 발생 시

### Streamlit 커뮤니티

- [Streamlit Forum](https://discuss.streamlit.io/)
- [Streamlit Docs](https://docs.streamlit.io/)

### 일반적인 문제

1. **앱이 슬립 모드로 들어감**:
   - 무료 플랜의 정상 동작
   - 방문 시 자동으로 깨어남 (1-2분 소요)

2. **리소스 제한 초과**:
   - 무료 플랜: CPU 1 core, RAM 800MB
   - 복잡한 연산 시 타임아웃 가능

3. **API 키 오류**:
   - Secrets 설정 재확인
   - API 키 유효성 확인

---

## 🎉 완료!

축하합니다! 이제 당신의 AI 챗봇이 웹에서 실행 중입니다!

**URL 공유하기**:
```
https://your-app-name.streamlit.app
```

누구나 브라우저에서 바로 사용할 수 있습니다! 🚀

---

## 📋 체크리스트

배포 전 확인:
- [ ] GitHub 레포지토리 생성
- [ ] 모든 파일 업로드
- [ ] `.gitignore` 설정
- [ ] Streamlit Cloud 가입
- [ ] 앱 배포
- [ ] Secrets에 API 키 설정
- [ ] 배포 확인
- [ ] 기능 테스트

배포 후 확인:
- [ ] API 키 작동
- [ ] 모든 탭 정상 작동
- [ ] 에러 없음
- [ ] URL 공유 테스트

---

**설치 없이 어디서나 사용 가능한 웹 앱 완성!** ✅
