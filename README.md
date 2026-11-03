# FACTCHECK LAB | 가짜뉴스 판독기

뉴스·문서 URL을 입력하면 본문을 추출하고, 핵심 주장을 뽑아 외부 검색 결과와 비교하는 학교 프로젝트용 웹앱입니다.

## 1. 준비물
- Python 3.10 이상
- OpenAI API 키
- Tavily 검색 API 키

API 키는 코드나 브라우저 화면에 공개하지 말고 서버의 환경변수로만 보관하세요.

## 2. 내 컴퓨터에서 실행하기

### Windows
```powershell
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

`.env` 파일을 열어 실제 API 키를 입력합니다.
```env
OPENAI_API_KEY=본인의_OpenAI_API_키
TAVILY_API_KEY=본인의_Tavily_API_키
OPENAI_MODEL=gpt-4.1-mini
```

실행:
```bash
python app.py
```
브라우저에서 `http://127.0.0.1:5000`에 접속합니다.

## 3. 공개 링크 만들기
이 프로젝트 폴더를 GitHub 저장소에 올린 뒤 Render 같은 Python 호스팅 서비스에서 새 Web Service로 연결합니다.

- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app`
- Environment Variables: `OPENAI_API_KEY`, `TAVILY_API_KEY`, `OPENAI_MODEL`

배포 서비스가 발급한 주소가 다른 사람에게 공유할 공개 링크입니다. API 키는 저장소에 올리지 말고 호스팅 서비스의 환경변수 메뉴에만 입력하세요.

## 4. 현재 지원 및 한계
- 공개 HTML 기사/문서의 텍스트 추출 및 요약
- 추출한 주장을 Tavily 검색 결과와 대조
- AI가 근거의 독립성·출처·맥락을 고려해 참/거짓/판단 보류로 분류
- 검증에 참고한 외부 자료 링크 표시

로그인/유료벽/동적 페이지는 본문 추출에 실패할 수 있습니다. YouTube 등 영상 URL은 영상 자막을 가져오는 별도 연동이 없어 현재 직접 분석하지 못합니다. 영상은 자막 또는 대본을 제공하는 기능을 추가해야 합니다.

## 5. 판정 원칙
- 80~100점: 강한 근거로 뒷받침됨 → 참
- 50~79점: 근거가 불충분하거나 엇갈림 → 판단 보류
- 0~49점: 강한 반대 근거 또는 조작 정황 확인 → 거짓

점수는 검증 근거의 강도에 대한 자동 평가이지, 통계적으로 보정된 진실 확률이 아닙니다. 검색 결과가 적다는 이유만으로 거짓 판정하지 않습니다. 유명 언론사라는 이유만으로 자동 참 판정하지 않습니다.

## 6. 학교 발표 시 주의
자동 팩트체크 결과는 참고 자료입니다. 중요한 주장은 원문, 공식 발표, 독립적인 복수 출처를 직접 확인하세요. 개인 정보가 포함된 링크는 입력하지 마세요.
