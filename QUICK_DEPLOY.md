# ⚡ 빠른 배포 가이드 (5분!)

Streamlit Cloud에 5분 만에 배포하는 방법입니다.

## 📦 1단계: 파일 준비 (1분)

GitHub 저장소에 다음 파일들이 있어야 합니다:

```
✅ app_cloud.py          (메인 앱)
✅ requirements.txt      (패키지 목록)
✅ .gitignore           (Git 설정)
✅ 리뷰/                 (이미 있음)
   ├── 맛집 리뷰/
   ├── 명소 리뷰/
   ├── 병원 리뷰/
   └── 카페 리뷰/
```

### 파일 복사

제공된 파일들을 저장소에 복사:

```bash
# 저장소 위치로 이동
cd /path/to/your-repo

# 파일 복사 (이미 리뷰 폴더는 있다고 가정)
# app_cloud.py, requirements.txt, .gitignore 복사
```

## 🚀 2단계: GitHub에 푸시 (1분)

```bash
git add app_cloud.py requirements.txt .gitignore
git commit -m "Add Streamlit app"
git push origin main
```

## ☁️ 3단계: Streamlit Cloud 배포 (2분)

### 3-1. Streamlit Cloud 접속
1. https://share.streamlit.io 접속
2. GitHub 계정으로 로그인
3. **"New app"** 클릭

### 3-2. 앱 설정
- **Repository:** `your-username/your-repo` 선택
- **Branch:** `main`
- **Main file path:** `app_cloud.py` 입력

### 3-3. Secrets 설정 ⚠️ 중요!
**Advanced settings → Secrets**에 다음 입력:

```toml
OPENAI_API_KEY = "sk-your-openai-api-key-here"
```

### 3-4. Deploy!
**"Deploy!"** 버튼 클릭

## ⏱️ 4단계: 배포 대기 (1분)

배포 프로세스:
```
Installing requirements... ████████░░ 80%
Starting app...           ██████████ 100%
```

완료되면:
```
✅ Your app is live at:
https://your-app-name.streamlit.app
```

## 🎉 5단계: 확인 및 사용!

1. **앱 URL 접속**
   ```
   https://your-app-name.streamlit.app
   ```

2. **사이드바 확인**
   - ✅ API 키 설정됨
   - ✅ 리뷰 데이터 로딩 중...
   - ✅ 리뷰 통계 표시

3. **첫 질문!**
   ```
   춘천에서 재방문율 높은 맛집 추천해줘
   ```

4. **벡터 스토어 생성**
   - 첫 질문 시 자동 생성 (1-2분)
   - 이후 질문은 빠르게 응답!

---

## 🔥 완료!

이제 다음을 할 수 있습니다:

- ✅ AI 챗봇으로 여행 정보 질문
- ✅ 리뷰 분석 탭에서 통계 확인
- ✅ 앱 URL 공유
- ✅ 언제든 업데이트 가능

---

## 📝 체크리스트

배포 전:
- [ ] app_cloud.py 파일 있음
- [ ] requirements.txt 파일 있음
- [ ] .gitignore 파일 있음
- [ ] 리뷰 폴더 구조 정확
- [ ] GitHub에 푸시 완료

Streamlit Cloud:
- [ ] 로그인 완료
- [ ] Repository 선택
- [ ] Main file: app_cloud.py
- [ ] Secrets에 API 키 입력
- [ ] Deploy 클릭

배포 후:
- [ ] 앱 접속 가능
- [ ] 리뷰 데이터 로딩 확인
- [ ] 첫 질문 시도
- [ ] 정상 작동 확인

---

## 🐛 문제 발생 시

### API 키 오류
```
Settings → Secrets → OPENAI_API_KEY 확인
```

### 리뷰 데이터 없음
```
GitHub 저장소의 "리뷰" 폴더 확인
```

### 앱 시작 안됨
```
Settings → Reboot app
```

### 상세 가이드
```
DEPLOY_GUIDE.md 참고
```

---

## 🎯 다음 단계

배포 완료 후:

1. **URL 공유**
   - 팀원들에게 공유
   - SNS에 공유

2. **데이터 업데이트**
   ```bash
   # 새 리뷰 추가
   git add 리뷰/
   git commit -m "Add new reviews"
   git push
   # 자동 재배포됨!
   ```

3. **커스터마이징**
   - 프롬프트 수정
   - UI 개선
   - 기능 추가

---

**배포 성공을 기원합니다!** 🚀

문제가 있으면 DEPLOY_GUIDE.md의 상세 가이드를 참고하세요.
