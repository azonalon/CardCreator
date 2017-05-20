import sys, os, platform, re
import requests
from subprocess import run, Popen, PIPE
import urllib.request as request
from lxml import etree
import html
import urllib.parse

def reading(txt, method='kakasi'):
    if method is 'kakasi':
        r = run(["kakasi", "-f",  "-iutf8", "-outf8", "-JH", "-KH"],
        input=txt.encode(), stdout=PIPE)
        return r.stdout.decode('utf-8')
    elif method is 'ruby':
        return rubyReading(txt)

def rubyReading(txt):
    YAHOO_APP_ID="dj0zaiZpPWFpRG1LdFFua1dHbSZzPWNvbnN1bWVyc2VjcmV0Jng9NTk-"
    txt = urllib.parse.quote(txt)
    url = "https://jlp.yahooapis.jp/FuriganaService/V1/furigana?appid=" + YAHOO_APP_ID + "&grade=1&sentence=" + txt
    result = request.urlopen(url)
    tree = etree.parse(result)
    with open("test.xml", 'wb') as f:
        f.write(etree.tostring(tree, pretty_print=True, encoding='utf-8'))
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
                if sw[0].text == sw[1].text:
                    sentence += sw[0].text
                else:
                    sentence += sw[0].text + '[' + sw[1].text + ']'
        elif furigana is not None:
            sentence += surface.text + '[' + furigana.text + ']'
        else:
            sentence += surface.text
    return sentence

if __name__ == "__main__":
    expr = '漢字かな交じり文にふりがなを振ること。'
    print (reading(expr, method='ruby'))
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
