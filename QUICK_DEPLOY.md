# 🚀 5분 안에 웹 배포하기

**강원도 관광 AI 컨시어지를 웹에 배포하는 가장 빠른 방법**

---

## ⚡ 준비물

- [ ] GitHub 계정
- [ ] OpenAI API 키 ([발급받기](https://platform.openai.com/api-keys))
- [ ] 인터넷 연결

---

## 📋 5단계 배포

### 1️⃣ GitHub 레포지토리 만들기 (1분)

1. [GitHub](https://github.com/new) 접속
2. Repository name: `gangwon-chatbot` (원하는 이름)
3. Public 선택
4. **Create repository** 클릭

### 2️⃣ 파일 업로드 (2분)

1. 방금 만든 레포지토리 페이지에서 **uploading an existing file** 클릭

2. 다음 파일들을 드래그 앤 드롭:
   ```
   ✅ app.py
   ✅ sample_data.py
   ✅ enhanced_data.py
   ✅ requirements.txt
   ✅ README.md
   ✅ .gitignore
   ```

3. `.streamlit` 폴더도 업로드:
   ```
   ✅ .streamlit/config.toml
   ✅ .streamlit/secrets.toml.example
   ```

4. **Commit changes** 클릭

⚠️ **중요**: `.streamlit/secrets.toml` 파일은 업로드하지 마세요!

### 3️⃣ Streamlit Cloud 가입 (30초)

1. [Streamlit Cloud](https://share.streamlit.io/) 접속
2. **Sign up with GitHub** 클릭
3. GitHub 계정 연결

### 4️⃣ 앱 배포 (1분)

1. **New app** 클릭

2. 정보 입력:
   ```
   Repository: your-username/gangwon-chatbot
   Branch: main
   Main file path: app.py
   ```

3. **Deploy!** 클릭

### 5️⃣ API 키 설정 (30초)

1. 앱 페이지 우측 하단 **⚙️** 클릭

2. **Secrets** 선택

3. 아래 내용 붙여넣기:
   ```toml
   OPENAI_API_KEY = "sk-your-actual-api-key-here"
   ```
   
   ⚠️ `sk-your-actual-api-key-here` 부분을 실제 API 키로 교체!

4. **Save** 클릭

---

## ✅ 완료!

**배포 완료!** 🎉

당신의 앱 URL:
```
https://your-app-name.streamlit.app
```

브라우저에서 바로 확인해보세요!

---

## 🧪 테스트

### 1. API 키 확인
- 사이드바에 "✅ API 키가 설정되었습니다" 표시되어야 함

### 2. 기능 테스트
- [ ] Tab 1: AI 상담 (빠른 질문 버튼 클릭)
- [ ] Tab 2: 견적 계산 (계산하기 버튼)
- [ ] Tab 3: 일정표 생성 (생성 버튼)
- [ ] Tab 4: 숙소 검색 (필터 조절)
- [ ] Tab 5: 가격 비교 (자동 표시)

---

## ❓ 문제 해결

### "API 키가 필요합니다" 표시
→ Secrets 설정 다시 확인
→ API 키 형식: `OPENAI_API_KEY = "sk-..."`
→ 앱 재시작 (Settings → Reboot app)

### "Module not found" 오류
→ `requirements.txt` 파일 확인
→ GitHub에 올바르게 업로드되었는지 확인

### 앱이 느려요
→ 첫 실행은 1-2분 소요 (정상)
→ 무료 플랜은 리소스 제한 있음

---

## 💡 팁

### URL 커스터마이징
Settings → General → Custom subdomain:
```
gangwon-tourism.streamlit.app
```

### 앱 업데이트
GitHub에 파일 수정 → 자동 재배포!

### 비용 관리
- OpenAI API 사용량 확인
- 비용 한도 설정 권장

---

## 📱 공유하기

이제 당신의 AI 챗봇을 누구에게나 공유할 수 있습니다!

```
친구에게: "https://your-app-name.streamlit.app 여기 들어가봐!"
SNS에: "강원도 여행 계획은 AI가 도와줍니다 🏔️ [링크]"
```

---

## 🎉 축하합니다!

**5분 만에 AI 웹 앱 배포 완료!**

설치 없이 어디서나 사용 가능한 웹 앱이 만들어졌습니다! ✨

---

더 자세한 내용은 [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)를 참조하세요.

문의: brad0702@kangwon.ac.kr
