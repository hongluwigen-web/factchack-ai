
import os, re, json
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify, render_template_string
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

HTML = r"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>팩트체크 | 가짜뉴스 판독기</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#f4f7fb;color:#172033;font-family:system-ui,-apple-system,"Noto Sans KR",sans-serif}
.wrap{max-width:900px;margin:42px auto;padding:0 18px}.brand{font-size:14px;font-weight:800;letter-spacing:2px;color:#3867d6}
h1{font-size:34px;margin:10px 0 8px}.sub{color:#667085;line-height:1.65}
.panel{background:white;border:1px solid #e4e9f1;border-radius:18px;padding:24px;margin-top:24px;box-shadow:0 8px 30px #1720330a}
label{display:block;font-weight:700;margin-bottom:10px}input{width:100%;padding:16px;border:1px solid #cfd7e4;border-radius:10px;font-size:16px}
button{margin-top:14px;background:#2859cf;color:white;border:0;border-radius:10px;padding:14px 22px;font-size:16px;font-weight:700;cursor:pointer}
button:disabled{opacity:.55;cursor:wait}.hint{font-size:13px;color:#667085;margin-top:10px}
.result{display:none}.score{font-size:48px;font-weight:850}.pill{display:inline-block;border-radius:99px;padding:6px 12px;font-weight:800;background:#edf1f7}
.good{color:#087443;background:#e8f7ef}.bad{color:#b42318;background:#fff0ee}.maybe{color:#9a6700;background:#fff6db}
h2{font-size:19px;margin:22px 0 10px}.claim{background:#f6f8fc;padding:14px;border-radius:10px;line-height:1.6}
ul{padding-left:20px;line-height:1.7}.source{border-top:1px solid #edf0f5;padding:12px 0}.source a{color:#2859cf;word-break:break-all}
.small{font-size:12px;color:#778197;line-height:1.6}.error{color:#b42318;margin-top:12px;white-space:pre-wrap}
.spinner{display:none;color:#2859cf;margin-top:14px}
@media(max-width:600px){.wrap{margin:24px auto}h1{font-size:28px}.panel{padding:18px}}
</style></head>
<body><main class="wrap">
<div class="brand">FACTCHECK LAB</div><h1>가짜뉴스 판독기</h1>
<p class="sub">뉴스·문서 링크를 입력하면 핵심 주장을 추출하고, 외부 자료와 비교해 근거를 정리합니다.</p>
<section class="panel">
<label for="url">분석할 뉴스 또는 문서 링크</label>
<input id="url" type="url" placeholder="https://example.com/news..." autocomplete="url">
<button id="go" onclick="analyze()">링크 분석하기</button>
<div class="hint">현재는 웹페이지에서 텍스트를 가져올 수 있는 공개 기사 링크를 우선 지원합니다. 로그인·유료벽·일부 영상 플랫폼은 분석되지 않을 수 있습니다.</div>
<div class="spinner" id="spin">자료를 수집하고 교차 검증하는 중입니다. 잠시 기다려 주세요…</div>
<div class="error" id="err"></div>
</section>
<section class="panel result" id="result">
<div id="verdict" class="pill"></div>
<div style="display:flex;align-items:baseline;gap:8px;margin-top:12px"><div class="score" id="score">--</div><div style="color:#667085">/ 100 신뢰도 점수</div></div>
<p id="summary" class="sub"></p>
<h2>핵심 주장</h2><div id="claims"></div>
<h2>검증 근거</h2><ul id="reasoning"></ul>
<h2>참고한 외부 자료</h2><div id="sources"></div>
<p class="small">주의: 이 결과는 자동 분석에 따른 참고 정보이며 사실 여부를 확정하는 판결이 아닙니다. 출처가 많더라도 서로 독립적이지 않거나 원문을 복제한 자료일 수 있습니다. 중요한 사안은 원문과 공식 발표를 직접 확인하세요.</p>
</section>
</main>
<script>
async function analyze(){
 const url=document.getElementById('url').value.trim(), btn=document.getElementById('go');
 document.getElementById('err').textContent=''; document.getElementById('result').style.display='none';
 if(!url){document.getElementById('err').textContent='링크를 입력해 주세요.';return}
 try{new URL(url)}catch(e){document.getElementById('err').textContent='올바른 URL 형식이 아닙니다.';return}
 btn.disabled=true;document.getElementById('spin').style.display='block';
 try{
  const r=await fetch('/api/analyze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({url})});
  const d=await r.json(); if(!r.ok)throw new Error(d.error||'분석 중 오류가 발생했습니다.');
  document.getElementById('result').style.display='block';
  const v=document.getElementById('verdict');v.textContent=d.verdict;v.className='pill '+(d.verdict==='참'?'good':d.verdict==='거짓'?'bad':'maybe');
  document.getElementById('score').textContent=d.score;
  document.getElementById('summary').textContent=d.summary||'요약 정보가 없습니다.';
  document.getElementById('claims').innerHTML=(d.claims||[]).map(x=>'<div class="claim">'+esc(x)+'</div>').join('');
  document.getElementById('reasoning').innerHTML=(d.reasons||[]).map(x=>'<li>'+esc(x)+'</li>').join('');
  document.getElementById('sources').innerHTML=(d.sources||[]).map(s=>'<div class="source"><b>'+esc(s.title||s.url)+'</b><br><a target="_blank" rel="noopener" href="'+esc(s.url)+'">'+esc(s.url)+'</a><p class="small">'+esc(s.note||'')+'</p></div>').join('')||'<p class="small">외부 자료가 확인되지 않았습니다.</p>';
 }catch(e){document.getElementById('err').textContent=e.message}
 finally{btn.disabled=false;document.getElementById('spin').style.display='none'}
}
function esc(s){return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
</script></body></html>"""

def get_article(url):
    p = urlparse(url)
    if p.scheme not in ("http", "https") or not p.netloc:
        raise ValueError("올바른 http/https 링크를 입력해 주세요.")
    # Avoid local/private network access (basic SSRF protection)
    host = (p.hostname or "").lower()
    if host in ("localhost", "127.0.0.1", "::1") or host.endswith(".local"):
        raise ValueError("내부 네트워크 주소는 분석할 수 없습니다.")
    r = requests.get(url, timeout=18, headers={"User-Agent":"Mozilla/5.0 (compatible; FactCheckStudentProject/1.0)"})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    for tag in soup(["script","style","nav","footer","header","noscript","form"]): tag.decompose()
    title = soup.title.get_text(" ", strip=True) if soup.title else url
    text = re.sub(r"\s+", " ", soup.get_text(" ", strip=True))
    if len(text) < 250:
        raise ValueError("페이지에서 분석할 본문을 충분히 가져오지 못했습니다. 로그인/유료벽/영상 링크일 수 있습니다.")
    return title, text[:14000]

def search_web(query):
    key = os.getenv("TAVILY_API_KEY")
    if not key: raise RuntimeError("TAVILY_API_KEY가 설정되지 않았습니다. .env 파일 설정을 확인해 주세요.")
    res = requests.post("https://api.tavily.com/search", json={
        "api_key":key, "query":query, "search_depth":"advanced",
        "max_results":7, "include_answer":False
    }, timeout=25)
    res.raise_for_status()
    return res.json().get("results", [])

def ai_json(prompt):
    key = os.getenv("OPENAI_API_KEY")
    if not key: raise RuntimeError("OPENAI_API_KEY가 설정되지 않았습니다. .env 파일 설정을 확인해 주세요.")
    model = os.getenv("OPENAI_MODEL","gpt-4.1-mini")
    res = requests.post("https://api.openai.com/v1/chat/completions",
        headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"},
        json={"model":model,"temperature":0.2,
              "response_format":{"type":"json_object"},
              "messages":[{"role":"system","content":"너는 신중한 한국어 팩트체크 보조자다. 근거가 부족하면 거짓으로 단정하지 말고 판단 보류로 분류한다. 검색 결과의 제목과 요약만으로 확인되지 않은 사실을 만들어내지 않는다."},
                          {"role":"user","content":prompt}]}, timeout=60)
    res.raise_for_status()
    return json.loads(res.json()["choices"][0]["message"]["content"])

@app.get("/")
def home(): return render_template_string(HTML)

@app.post("/api/analyze")
def analyze():
    try:
        url = (request.json or {}).get("url","").strip()
        title, article = get_article(url)
        first = ai_json("다음 기사에서 검증 가능한 핵심 사실 주장 2~4개를 뽑고, 각 주장을 검색에 적합한 짧은 문장으로 바꿔라. JSON 형식: {claims:[...],summary:string}\n제목:"+title+"\n본문:"+article)
        claims = first.get("claims",[])[:4]
        if not claims: raise ValueError("검증할 핵심 주장을 추출하지 못했습니다.")
        search_results=[]
        for claim in claims[:3]:
            for item in search_web(claim)[:5]:
                search_results.append({"title":item.get("title",""),"url":item.get("url",""),"content":(item.get("content","") or "")[:1200]})
        prompt = """아래 기사와 검색 결과만 근거로 팩트체크하라.
점수는 사실일 가능성의 확률이 아니라 근거의 강도에 대한 보수적 평가다.
서로 독립적인 출처인지, 원문/공식자료인지, 날짜와 맥락이 일치하는지 평가하라.
같은 보도자료나 기사를 복제한 사이트는 여러 출처로 세지 마라.
MBC/KBS/SBS/YTN 등 유명 언론사라는 이유만으로 자동 참 판정하지 마라.
80~100은 핵심 주장이 독립적인 신뢰 출처 또는 1차 자료로 강하게 뒷받침될 때만 참.
50~79는 판단 보류.
0~49는 반대되는 강한 근거 또는 조작 정황이 확인될 때 거짓. 자료 부족만으로 낮은 점수를 주거나 거짓으로 하지 말고 판단 보류로 한다.
반드시 JSON: {score:정수,verdict:"참|거짓|판단 보류",summary:string,reasons:[...],sources:[{title,url,note}]}
기사 제목: """+title+"\n기사 본문:\n"+article[:9000]+"\n추출 주장:\n"+json.dumps(claims,ensure_ascii=False)+"\n검색 결과:\n"+json.dumps(search_results,ensure_ascii=False)
        out = ai_json(prompt)
        score = max(0,min(100,int(out.get("score",50))))
        verdict = out.get("verdict","판단 보류")
        if verdict not in ("참","거짓","판단 보류"): verdict="판단 보류"
        # Enforce threshold policy
        if score >= 80: verdict="참"
        elif score >= 50: verdict="판단 보류"
        else: verdict="거짓"
        return jsonify({"score":score,"verdict":verdict,"summary":out.get("summary",""),
                        "claims":claims,"reasons":out.get("reasons",[]),
                        "sources":out.get("sources",[])})
    except requests.RequestException:
        return jsonify(error="웹페이지 또는 검색 서비스에 연결하지 못했습니다. 링크 접근 가능 여부와 API 설정을 확인해 주세요."),502
    except Exception as e:
        return jsonify(error=str(e)),400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT","5000")), debug=False)
