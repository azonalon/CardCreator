import sys, os, platform, re
from subprocess import run, Popen, PIPE
import urllib.request as request
from lxml import etree
import html
import urllib.parse
import http.cookiejar

def reading(txt, method='kakasi', infolog=print):
    if method is 'kakasi':
        r = run(["kakasi", "-f",  "-iutf8", "-outf8", "-JH", "-KH"],
        input=txt.encode(), stdout=PIPE)
        return r.stdout.decode('utf-8')
    elif method is 'ruby':
        try:
            return rubyReading(txt)
        except Exception as e:
            infolog("Could not use ruby api:", e)
            return reading(txt, method='kakasi', infolog=infolog)

header={'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36" }
surfaceSeparator = " "
wordSeparator = "\u200c" # &zwnj;
def rubyReading(txt):
    # word boundaries are marked by \ufeff
    if txt is "":
        return ""
    YAHOO_APP_ID="dj0zaiZpPWFpRG1LdFFua1dHbSZzPWNvbnN1bWVyc2VjcmV0Jng9NTk-"
    txt = urllib.parse.quote(txt)
    url = "http://jlp.yahooapis.jp/FuriganaService/V1/furigana?appid=" + YAHOO_APP_ID + "&grade=1&sentence=" + txt
    r = request.Request(url,headers=header)
    result = request.urlopen(r, timeout=1.0)
    tree = etree.parse(result)
    # with open("test.xml", 'wb') as f:
        # f.write(etree.tostring(tree, pretty_print=True, encoding='utf-8'))
    root = tree.getroot()
    ns = "{" + root.nsmap[None]  + "}"
    wordList = root[0][0]
    sentence = ""
    for w in wordList:
        subwordList = w.find(ns + "SubWordList")
        furigana = w.find(ns + "Furigana")
        surface = w.find(ns + "Surface")
        if subwordList is not None:
            for sw in subwordList:
                if len(sw) > 1:
                    if sw[0].text == sw[1].text:
                        sentence += sw[0].text + surfaceSeparator
                    else:
                        sentence += sw[0].text + '[' + sw[1].text + ']' + surfaceSeparator
                else:
                    sentence += sw[0].text
        elif furigana is not None:
            sentence += surface.text + '[' + furigana.text + ']' + surfaceSeparator
        else:
            sentence += surface.text + surfaceSeparator
        sentence += wordSeparator
    sentence = sentence[:-2] if sentence[-1] == " " else sentence
    return sentence

if __name__ == "__main__":
    print("Testing ruby reading api...")
    expr = '漢字かな交じり文にふりがなを振ること。'
    print (reading(expr))
    expr = "カリン、自分でまいた種は自分で刈り取れ"
    print (reading(expr, method='ruby'))
    expr = "昨日、林檎を2個買った。"
    print (reading(expr, method='ruby'))
    expr = "真莉、大好きだよん＾＾"
    print (reading(expr, method='ruby'))
    expr = "彼２０００万も使った。"
    print (reading(expr, method='ruby'))
    expr = "彼二千三百六十円も使った。"
    print (reading(expr, method='ruby'))
    expr = "千葉"
    print (reading(expr, method='ruby'))
