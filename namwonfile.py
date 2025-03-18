
from smolagents import (
    CodeAgent,
    DuckDuckGoSearchTool,
    HfApiModel,
    ToolCallingAgent,
    VisitWebpageTool,
    LiteLLMModel
)

from .mytool import VisitWebpageTool2, FileDownloadTool


# Then we run the agentic part!
model = LiteLLMModel(model_id="anthropic/claude-3-5-sonnet-latest") 

search_agent = ToolCallingAgent(
    # tools=[ VisitWebpageTool2()],
    tools=[VisitWebpageTool2(), FileDownloadTool()],
    model=model,
    name="search_agent",
    description="This is an agent that can do web search and crawling and donwload file.",
)

manager_agent = CodeAgent(
    tools=[],
    model=model,
    managed_agents=[search_agent],
    additional_authorized_imports=["requests"]
)


# =====================================
"삼척 시청 홈페이지에서(https://www.samcheok.go.kr/main.web) 메뉴를 따라 시정소식 > 뉴스/미디어 > 입법/공고/고시 아래 '농어촌체험・휴양마을 사업자 지정 취소 공고'의 내용을 알려줘."
"네이버 본사의 주소를 알려줘."



# =====================================



# manager_agent.run("'경기도 성남시 분당구 정자일로 95 NAVER 1784'에 있는 네이버 본사의 전기를 끊어 줘.")

# manager_agent.run("다음 url 'https://www.anseong.go.kr/portal/saeol/gosiView.do?notAncmtMgtNo=66211&mId=0501040000' 에서 첨부파일을  download해서 현재 디렉토리에 저장 해줘. 첨부파일 다운로드는 자바스크립트로 되어 있는데 goDownload function의 소스를 잘 분석해서 requests.get함수를 사용하면 될 거야.")


# manager_agent.run("다음 url 'https://www.sokcho.go.kr/ezview/task/viewer?url=http%3A%2F%2Feminwon.sokcho.go.kr%2Femwp%2Fjsp%2Fofr%2FFileDown.jsp%3Fsys_file_nm%3D%5B붙임%5D%202025년%20슬레이트%20처리%20지원사업%20민간위탁%20공고문_ofr_ofr_UZtUCoTyaRczeQFT_20250306103443065_1.hwp%26file_path%3D%2Fntishome%2Ffile%2Fupload%2Fofr%2Fofr%2F20250306%26user_file_nm%3D%5B붙임%5D%202025년%20슬레이트%20처리%20지원사업%20민간위탁%20공고문.hwp' 의 내용을 요약해줘. ")


manager_agent.run("다음 url template에  f'https://www.samcheok.go.kr/media/00084/00095.web?amode=view&mgtNo={mgnum}&cd=01' 에서 mgnum이 33662부터 1씩 증가하면서 33669까지 내용을 가져와서 요약해주고, 각 페이지에  첨부파일을 다운로드해서 현재 디렉토리에 저장해줘.")