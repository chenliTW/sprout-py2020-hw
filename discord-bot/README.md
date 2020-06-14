
## 2020 資訊之芽 py 班 二階小作業 一 圖片管理系統

> 學校: 延平中學  
> 學員: 陳立

注意事項:
 - 我import了太多東西了XD,所以開了一個pipenv
 - 因為我有使用 [pdfkit,zbarlight] ,所以麻煩講師大大安裝 [wkhtmltopdf,[libzbar0,libzbar-dev]]
	https://wkhtmltopdf.org/downloads.html
	apt install libzbar0 libzbar-dev
 - 在第 [105] 行有使用 "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc" 字體,若講師大大的系統
 	沒有可能要麻煩自行調配(抱歉Orz)
 - HowHow聲音來源 : https://github.com/EarlySpringCommitee/HowHow-parser
 - 電腦必須安裝 ffmpeg
 - 一定要在linux上跑(?

bot 指令用法 (指令使用前綴 '$') :

	1. say [lang] [text] (O) => Google text to speech生成聲音

	2. draw [text] (O) => 依輸入的文字生成文字

	3. convert [method] (O) => 各種encode/decode
		- base64encode [string]
		- base64decode [string]
		- toupper [string]
		- tolower [string]
		- rot13 [string]

	4. hash [method]  (O) => 各種hash生成
		- md5 [string]
		- sha1 [string]
		- sha256 [string]
		- sha384 [string]

	5. nettools [method] (O) => 網路工具
		- whois [domain]
		- traceroute [domain]
		- ping [domain]

	6. osint [username] (O) => 找帳號出現在那個平臺

	7. judge [method] (O) => 資牙judge小工具
		- login [username] [password]
		- submit [problemid] [lang] (query must contain an attachment)
		- get [problemid]

	8. howhowsay [中文] => how 哥聲成器

	9. qrcode [method] (O) => qrcode 工具
		- gen [inp]
		- decode (query must contain a photo attachment)

	10. crawlschoolcal (O) => 抓明日學校行事曆

	11. crawlschoolann [num] (O) => 佈告欄
