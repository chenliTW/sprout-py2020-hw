import discord
from discord.ext import commands
from discord.voice_client import VoiceClient
import requests
from bs4 import BeautifulSoup
import os
import json
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
import math 
import base64
import hashlib
import whois
import pdfkit
import pypinyin
import qrcode as qrcodegen
import zbarlight
import bs4
from subprocess import check_output
import ffmpeg
import shutil

bot = commands.Bot(command_prefix='$')

tag_dict={}
date_dict={}
judge_cookie=""

@bot.event
async def on_ready():
    print(bot.user.name)
    print(bot.user.id)
    
@bot.command()
async def upload_pic(ctx,date,tag):
    res=requests.get(ctx.message.attachments[0].url)

    filename="./image/"+ctx.message.attachments[0].url.split("/")[-1]

    img=open(filename,"wb+")
    
    if tag in tag_dict:
        tag_dict[tag].append(filename)
    else:
        tag_dict[tag]=[filename]

    if date in date_dict:
        date_dict[date].append(filename)
    else:
        date_dict[date]=[filename]
    
    tag_db=open("tag.db","w+")
    tag_db.write(json.dumps(tag_dict))
    tag_db.close()
    date_db=open("date.db","w+")
    date_db.write(json.dumps(date_dict))
    date_db.close()

    img.write(res.content)
    img.close()
    await ctx.send("ok")

@bot.command()
async def search_pic_bytag(ctx,tag):
    if tag in tag_dict:
        for img in tag_dict[tag]:
            with open(img, 'rb') as f:
                picture = discord.File(f)
                await ctx.send(file = picture)
    else:
        await ctx.send("404 not found")

@bot.command()
async def search_pic_bydate(ctx,date):
    if date in date_dict:
        for img in date_dict[date]:
            with open(img, 'rb') as f:
                picture = discord.File(f)
                await ctx.send(file = picture)
    else:
        await ctx.send("404 not found") 

'''
    1. Google text to speech
'''
@bot.command()
async def say(ctx,lang,text):
    tts = gTTS(text, lang=lang)
    tts.save('tmp.mp3')
    with open("tmp.mp3",'rb') as f:
        audio=discord.File(f)
    await ctx.send(file=audio)
    os.remove('tmp.mp3')

'''
    2. generate image by text
'''
@bot.command()
async def draw(ctx,text):
    text=text.replace('\n','')
    text_len=len(text)
    img_len=int(math.sqrt(text_len))+3
    img = Image.new('RGB', (20+(50*img_len), 20+(50*img_len)), color = (0, 0, 0))
    try:
        fnt = ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', 50)
    except:
        raise "請修改ttc檔位置"
    text = '\n'.join([text[i:i+img_len] if i+img_len<=len(text) else text[i:] for i in range(0,len(text),img_len)])
    d = ImageDraw.Draw(img)
    d.text((10,10), text, font=fnt, fill=(255,255,255))
    img.save("tmp.png")
    with open("tmp.png", 'rb') as f:
        picture = discord.File(f)
        await ctx.send(file = picture)

'''
    3. convert
'''
@bot.command()
async def convert(ctx,method,inp):
    s_inp=inp.encode("UTF-8")
    if method=="base64encode":
        await ctx.send(str(base64.b64encode(s_inp))[2:-1])
    elif method=="base64decode":
        try:
            await ctx.send(str(base64.b64decode(s_inp))[2:-1])
        except Exception as e:
            await ctx.send("error {}".format(e))
    elif method=="toupper":
        await ctx.send(inp.upper())
    elif method=="tolower":
        await ctx.send(inp.lower())
    elif method=="rot13":
        out=""
        for i in inp:
            if i.isalpha():
                if i.isupper():
                    out+=chr((ord(i)-ord('A')+13)%26+ord('A'))
                else:
                    out+=chr((ord(i)-ord('a')+13)%26+ord('a'))
            else:
                out+=i
        await ctx.send(out)
    else:
        await ctx.send("convert method not found")

'''
4.hash
'''
@bot.command()
async def hash(ctx,method,inp):
    inp=inp.encode("UTF-8")
    if method=="md5":
        obj=hashlib.md5()
        obj.update(inp)
        await ctx.send(obj.hexdigest())
    elif method=="sha1":
        obj=hashlib.sha1()
        obj.update(inp)
        await ctx.send(obj.hexdigest())
    elif method=="sha256":
        obj=hashlib.sha256()
        obj.update(inp)
        await ctx.send(obj.hexdigest())
    elif method=="sha384":
        obj=hashlib.sha384()
        obj.update(inp)
        await ctx.send(obj.hexdigest())
    else:
        await ctx.send("hash method not found")

'''
    5. webtools
'''
@bot.command()
async def nettools(ctx,method,inp):
    if method=="whois":
        res=whois.query(inp)
        await ctx.send(vars(res))
    elif method=="traceroute":
        res = check_output(["traceroute", inp]) # RCE here QAQ
        res=res.decode("UTF-8")
        await ctx.send(res)
    elif method=="nslookup":
        res = check_output(["nslookup", inp]) # RCE here QAQ
        res=res.decode("UTF-8")
        await ctx.send(res)
    elif method=="ping":
        res = check_output(["ping", inp]) # RCE here QAQ
        res=res.decode("UTF-8")
        await ctx.send(res)        
    else:
        await ctx.send("nettools method not found")

'''
    6. osint
'''
@bot.command()
async def osint(ctx,username):
    def check_by_status_code_200(url,username,suffix):
        return requests.get(url+username+suffix).status_code==200
    site={
        'Github':{'url':'https://github.com/','check':check_by_status_code_200},
        'Instergram ':{'url':'https://www.instagram.com/','check':check_by_status_code_200},
        #'Twitter':{'url':'https://twitter.com/','check':check_by_status_code_200},
        'Pinterest':{'url':'https://www.pinterest.it/','check':check_by_status_code_200},
        'Vk':{'url':'https://vk.com/','check':check_by_status_code_200}
    }
    found=False
    for i in site:
        if site[i]['check'](site[i]['url'],username,""):
            found=True
            await ctx.send("[+]User Present in "+i)
            await ctx.send("    "+site[i]['url']+username)
    if not found:
        await ctx.send("[-]User not found in our site list")

'''
    7. judge
'''
@bot.command()
async def judge(ctx,method,inp,inp2=""):
    if method=="get":
        pdfkit.from_url('https://neoj.sprout.tw/api/problem/{}/static/cont.html'.format(inp), "./prob/{}.pdf".format(inp))
        file=discord.File(open("./prob/{}.pdf".format(inp),"rb"), filename="{}.pdf".format(inp), spoiler=False)
        await ctx.send(file=file)
    elif method=="login":
        res=requests.post("https://neoj.sprout.tw/api/user/login",json={"mail":inp,"password":inp2})
        global judge_cookie
        if "Success" in res.text:
            judge_cookie=res.cookies['token']
            await ctx.send("登入成功 cookie:{}".format(judge_cookie))
        else:
            await ctx.send("帳密錯誤")
    elif method=="submit":
        codefile=requests.get(ctx.message.attachments[0].url)
        code=codefile.content.decode("UTF-8")
        res=requests.post("https://neoj.sprout.tw/api/problem/{}/submit".format(inp),json={"code":code,"lang":inp2},cookies={"token":judge_cookie})
        if "Error" not in res.text:
            await ctx.send("https://neoj.sprout.tw/challenge/{}".format(res.text))
        else:
            await ctx.send("error")
    else:
        await ctx.send("judge method not found")

@bot.command()
async def howhowsay(ctx,inp):
    symbol=pypinyin.pinyin(inp, style=pypinyin.Style.TONE3, heteronym=True)
    filename="./howhowvoice/"+symbol[0][0]+".mp4"
    outfile="./genhowvoice/"+base64.b64encode(inp.encode("UTF-8")).decode("UTF-8")+".mp4"
    shutil.copyfile(filename, outfile)
    symbol=symbol[1:]
    for i in symbol:
        filename="./howhowvoice/"+i[0]+".mp4"
        tmp="./genhowvoice/"+base64.b64encode(inp.encode("UTF-8")).decode("UTF-8")+"-tmp.mp4"
        os.system("echo \"file '{}'\nfile '{}'\" > recipe.txt".format(outfile,filename))
        os.system("ffmpeg -f concat -safe 0 -i recipe.txt -c copy {}".format(tmp))
        os.remove(outfile)
        shutil.move(tmp,outfile)
    with open(outfile, 'rb') as f:
        video = discord.File(f)
        await ctx.send(file = video)

@bot.command()
async def qrcode(ctx,method,inp=""):
    if method=="gen":
        img = qrcodegen.make(inp)
        filename=base64.b64encode(inp.encode("UTF-8"))
        img.save("./qrimage/{}.jpg".format(filename))
        with open("./qrimage/{}.jpg".format(filename), 'rb') as f:
            picture = discord.File(f)
            await ctx.send(file = picture)
        os.remove("./qrimage/{}.jpg".format(filename))
    elif method=="decode":
        try:
            res=requests.get(ctx.message.attachments[0].url)
            filename="./qrimage/"+ctx.message.attachments[0].url.split("/")[-1]
            img=open(filename,"wb+")
            img.write(res.content)
            img.close()
            IMG=Image.open(filename)
            codes = zbarlight.scan_codes(['qrcode'], IMG)
            await ctx.send(codes)
        except Exception as e:
            await ctx.send(e)
    else:
        await ctx.send("qrcode method not found")

@bot.command()
async def crawlschoolcal(ctx):
    def crawl_tomorrow_calendar():
        res = requests.get('http://www.yphs.tp.edu.tw/yphs/gr2.aspx')
        soup = BeautifulSoup(res.text, "html.parser")
        calendar='明日行事曆:\n 全校:'+soup.find_all(color="#404040")[16].text
        print(soup.find_all(color="#404040")[16].text)
        if(soup.find_all(color="#404040")[16].text==' '):
            calendar+='N/A'
        calendar=calendar+'\n 高一:'+soup.find_all(color="#404040")[21].text
        if(soup.find_all(color="#404040")[21].text==' '):
            calendar+='N/A'
        calendar=calendar+'\n 高二:'+soup.find_all(color="#404040")[21].text
        if(soup.find_all(color="#404040")[22].text==' '):
            calendar+='N/A'
        calendar=calendar+'\n 高三:'+soup.find_all(color="#404040")[21].text
        if(soup.find_all(color="#404040")[23].text==' '):
            calendar+='N/A'
        return calendar
    recv=crawl_tomorrow_calendar()
    await ctx.send(recv)

@bot.command()
async def crawlschoolann(ctx,num):
    def crawl_index():
        res=requests.get('https://www.yphs.tp.edu.tw/yphs.aspx')
        soup = bs4.BeautifulSoup(res.text, 'html.parser')
        VIEWSTATE=soup.find(id="__VIEWSTATE").get('value')
        VIEWSTATEGENERATOR=soup.find(id="__VIEWSTATEGENERATOR").get('value')
        EVENTVALIDATION=soup.find(id="__EVENTVALIDATION").get('value')
        index_table=list()
        for x in  soup.find_all('table')[1].find_all('tr')[1:-1]:
            tds=x.find_all('td')
            title,date,department=tds[2].text,tds[0].text,tds[1].text
            href=x.find('a')["href"][25:-5]
            index_table.append([title,date,department,href])
        return index_table,VIEWSTATE,VIEWSTATEGENERATOR,EVENTVALIDATION

    def crawl_info(index_table,VIEWSTATE,VIEWSTATEGENERATOR,EVENTVALIDATION):
        message_list=list()
        for index in index_table:
            cookies={"AspxAutoDetectCookieSupport":"1"}
            data={"__EVENTTARGET":index[3],"__VIEWSTATE":VIEWSTATE,"__VIEWSTATEGENERATOR":VIEWSTATEGENERATOR,"__EVENTVALIDATION":EVENTVALIDATION,"DL1":"不分","DL2":"不分","DL3":"全部","__LASTFOCUS":"","__EVENTARGUMENT":""}
            res=requests.post('https://www.yphs.tp.edu.tw//yphs.aspx?AspxAutoDetectCookieSupport=1',allow_redirects=False,cookies=cookies,data=data)
            soup=bs4.BeautifulSoup(res.text,'html.parser')
            info_table=soup.find_all('table')[0].find_all('td')
            message_list.append([info_table[7].text,info_table[1].text,info_table[5].text,info_table[3].text,info_table[9].text,info_table[11].text])
        return message_list

    index_table,VIEWSTATE,VIEWSTATEGENERATOR,EVENTVALIDATION=crawl_index()
    message_list=crawl_info(index_table,VIEWSTATE,VIEWSTATEGENERATOR,EVENTVALIDATION)
    cnt=0
    for message in message_list:
        cnt+=1
        if cnt>int(num):
            break
        await ctx.send("[主旨:"+message[0]+"]\n"+message[4]+"\n附件:\n"+message[5]+"\n發布時間:"+message[1]+"\n發布人:"+message[2]+"\n發布身份:"+message[3])


if __name__=="__main__":

    try:
        date_dict=json.loads(open("date.db","r").read())
        tag_dict=json.loads(open("tag.db","r").read())
    except:
        print("detected first run")


    bot.run('secret')
