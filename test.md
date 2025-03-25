
##code-oss에서 엑스텐션이 안보일때.

code-oss   /data/data/com.termux/files/usr/lib/code-oss/resources/app/product.json

https://stackoverflow.com/questions/64463768/cant-find-certain-extensions-in-code-ossopen-source-variant-of-visual-studio-c



##termux native chromium & code-oss

```
pkg install tur-repo
pkg install chromium
```

If you want to install VS Code: 
```
pkg install tur-repo
pkg install code-oss
```

---  


##mapify.so  youtube등 어떤 컨텐츠라도 마인드맵으로 바꿔줌.

https://mapify.so/    


##SubmitDirs  내 제품을 제출하면 100개이상의 웹 디렉토리에 등재해 준다.


## supametas
# 비정형데이터를 훑어보고 메타 데이터와 태그를 자동 생성해준다.

https://supametas.ai/

Supametas.AI specializes in automated field extraction from complex web pages using natural language prompts or predefined fields

https://www.youtube.com/watch?v=3fejFAQ9wAM





안성시청 goDownload

	function goDownload(de_user_file_nm, de_sys_file_nm, de_file_path) {
		var enc_de_user_file_nm = encodeURI(de_user_file_nm);
		var enc_de_sys_file_nm = encodeURI(de_sys_file_nm);
		var enc_de_file_path = encodeURI(de_file_path);
		var url = "https://eminwon.anseong.go.kr/emwp/jsp/ofr/FileDown.jsp?user_file_nm="+enc_de_user_file_nm+"&sys_file_nm="+enc_de_sys_file_nm+"&file_path="+enc_de_file_path;
		window.location.assign(url);
		//window.open(url, "fileDown", "width=410, height=450, resizable=0, scrollbars=no, status=0, titlebar=0, toolbar=0, left=300, top=200");
		//sleep(2*1000);
		//window.open("/common/close.jsp", "fileDown", "width=410, height=450, resizable=0, scrollbars=no, status=0, titlebar=0, toolbar=0, left=300, top=200");
	}


송파구청은 gourl자바스크립트 함수에 url이 들어 있음.


도봉구청


<div class='file_list'>
<a href='javascript:filedown(13542020, 1600);' title='공고문.hwp 다운로드' class="hwp file_name">
공고문.hwp (144 KB)</a>
<a href="javascript:attach_docview_unitsvc('1600','13542020','12');" class="file_icon" title='새창열림'>
<img src="/WDB_common/images/common/btn_file_view.jpg" alt="미리보기" /></a>
</div>
<div class='file_list mt10'>
<a href='javascript:filedown(13542021, 1600);' title='응시원서 등 신청자 작성서류 각 1부.hwp 다운로드' class="hwp file_name">
응시원서 등 신청자 작성서류 각 1부.hwp (104 KB)</a>
<a href="javascript:attach_docview_unitsvc('1600','13542021','12');" class="file_icon" title='새창열림'>
<img src="/WDB_common/images/common/btn_file_view.jpg" alt="미리보기" /></a>
</div>


    function filedown(fcode, idx) {
		$.ajax({
			async:false,
			data:{
				idx       : idx
			},
			dataType:"text",
			type:"post",
			url:"ajax_user_attach.asp",
			success:function(data) {
				switch (data) { 
                    case "OK" :  location.href = "/WDB_common/include/download_unitsvc_gosing.asp?fcode=" +  fcode + "&bcode=" + idx; break;
                    case "nodata" : alert("다운 받을 화일이 없습니다."); return; break;
                    case "error" : alert("문제가 발생 하였습니다"); return; break;
//					case "ok": doc_preview(data.fn, data.path); break;
				}
			},
			error:function(request, status, error) {
				//alert("Error Code : "+request.status+"\nStatus : "+request.responseText);
				alert("미리보기 서버에서 응답이 없습니다.");
			},
			complete:function() { $("#loadingBg").hide(); }
		});
    }
펑션이 복잡해 보이나 실제로는 
https://www.dobong.go.kr/WDB_common/include/download_unitsvc_gosing.asp?fcode=13542020&bcode=1600
이렇게 GET방식으로 보내면 됩니다.



web crawling scraping

https://apify.com/?utm_source=aiagentsdirectory.com

https://aiagentsdirectory.com/category/web-scraping

https://scrape.do/blog/web-scraping-with-playwright/
