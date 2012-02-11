# -*- coding: utf-8 -*-
import re
import urllib2
import xml.dom.minidom
import sys
import datetime
from urllib import urlopen, quote_plus
import MeCab
import os



# Returns title and dictionary of word counts
def getwordcounts(url):
  feedlist={}                                     #titleとidの組み合わせ
  apcount={}                                      #単語の出現回数title通算で集計
  wordcounts={}                                   #単語の出現回数titleごとに集計
  # Parse the feed
  try:
    r = urllib2.urlopen(url).read()
    doc=xml.dom.minidom.parseString(r)
  except:
    print "error@", url, "!!"
    return feedlist,apcount, {}
  incidents=doc.getElementsByTagName('incident') #incidentごとに

  for incident in incidents:
    wc={}

    id = incident.childNodes[0].firstChild.data    #id
    title = incident.childNodes[1].firstChild.data #title
    title = title.strip()                          #空白は取り除く
    description = incident.childNodes[2].firstChild.data #description

    feedlist[title]=id

    # Extract a list of words
    words=split(title+' '+ description)
    for word in words:
      wc.setdefault(word,0)
      wc[word]+=1
      
    wordcounts[title]=wc                            #titleごとのwc
    for word,count in wc.items():
      apcount.setdefault(word,0)
      if count>1:
        apcount[word]+=1
  return feedlist,apcount,wordcounts



def split(sentence):
    mecab = MeCab.Tagger("mecabrc")
    data=[]
    data.append(str(sentence))


    node=mecab.parseToNode("\n".join(data))
    ret=[]
    while node:
        word=node.surface
        #名詞・形容詞・副詞・連体詞・動詞なら
        if (node.posid >= 36 and node.posid <= 67) \
                or (node.posid >= 10 and node.posid <= 12) \
                or (node.posid >= 34 and node.posid <= 35) \
                or (node.posid == 68) \
                or (node.posid >= 31 and node.posid <= 33):
            ret.append(word)
        node=node.next
    return ret 



def go(num, id):
  feedurl='http://www.sinsai.info/api?task=incidents&by=all&resp=xml&limit='
  feedurl += num
  if id!='0':
    feedurl += '&by=catid&id='
    feedurl += id
  print feedurl
  feedlist,apcount,wordcounts=getwordcounts(feedurl)

  wordlist=[]                     #１行目に表示する単語
  for w,bc in apcount.items():
    frac=float(bc)/len(feedlist)  #デバッグ中は消したほうがいいかも
    if frac>0.1 and frac<0.6:
      wordlist.append(w)

  d = datetime.datetime.today()
  out_file='/var/www/cgi-bin/data/'+'blogdata'+num+"-"+id+".txt"
  out=file(out_file,'w')
  out.write('Blog')
  for word in wordlist: 
    tmp=word.strip()
    out.write('\t%s' % tmp)
  out.write('\n')

  for blog,wc in wordcounts.items():
    out.write(blog)
    for word in wordlist:
      if word in wc : out.write('\t%d' % wc[word])
      else: out.write('\t0')
    out.write('\n')
  out.close()

  return feedlist

if __name__=='__main__':
  print sys.argv[1]
  go(sys.argv[1])


