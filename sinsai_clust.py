#!/usr/bin/env python
# coding: utf-8

import cgi
from datetime import datetime
import generatefeedvector
import clusters


html_body = u"""
<html>
  <head>
    <meta http-equiv="content-type"
          content="text/html;charset=utf-8" />
    %s
    %s

  </head>
  <body>
  <form method="GET" action="/cgi-bin/sinsai_clust.py">
    sinsai.infoから検索する記事の件数、カテゴリを選んで下さい:
    <select name="limit">
      %s
    </select>
    <select name="category">
      %s
    </select>
    <input type="submit" value="検索" />
  </form>
  %s


  </body>
</html>
"""

#google analytics用(略)

tracking_code=u"""<script type="text/javascript">
</script>"""

css_code=u"""
<style type="text/css">
body{
  font:100% sans-serif;
  padding:0px 0 36px 0;
  color:black;
  background:#dee;
  margin:24px;
  position:relative;
  }
a {color:#030ac}
a:visited {color:#91a4d6}
a:hover {color:#ff3300}


#dendrogramFrame{
    position:relative;
    margin:0 0 0 36px;
    font-size:75%;
    border:0px solid white;
}
#dendrogramFrame .leaf{
    position:absolute;
    padding:1px 3px 1px 3px;
    border:1px solid #555555;
    minWidth:20px;
    width:600px;
    text-align:center;
    -webkit-border-radius:6px;
    -moz-border-radius:6px;
    -webkit-box-shadow:2px 2px 3px rgba(0, 0, 0, 0.25);
    -moz-box-shadow:2px 2px 3px rgba(0, 0, 0, 0.25);
}
#dendrogramFrame .cap{
    position:absolute;
    border-left:1px solid #555555; 
}
#dendrogramFrame .drop{
    position:absolute;
    border-top:1px solid #555555;
}
#gFrame{
    margin:16px 20px 32px 20px;
}

</style>

"""


options_limit=''
options_category=''
content=''

cat = {"全カテゴリ":0,  "公式発表・通達":100,   "重要な通達":101,  "公的機関からの情報":102,  "消息":103,  "安否確認・消息":104,  "避難拠点":105,  "避難所、災害支援拠点":106,  "要請":107,  "物資要請":108,  "救助・救援要請":109,  "支援要請":110,  "生活":111,  "ライフラインの状態":112,  "交通機関":113,  "住宅情報":114,  "医療・福祉、健康相談":115,  "学校・教育、育児支援":116,  "店舗、施設、サービス":117,  "生活支援・相談":118,  "雇用情報、就労支援":119,  "企業支援":120,  "情報":121,  "気象・震災関連資料":122,  "防災に役立つ情報":123,  "応急処置・健康法":124,  "震災情報メディア紹介":125,  "復興情報ニュース":126,  "各国語による情報":127,  "ペット・家畜情報":128,  "支援・応援":129,  "被災者受け入れ":130,  "物資提供、寄付":131,  "イベント情報":132,  "ボランティア募集":133,  "支援者に役立つ情報":134,  "被災地状況レポート":135,  "地場産業・物産情報":136,  "連携団体":137,  "助けあいジャパン":138,  "遠野まごころネット":139,  "ふんばろう東日本":140,  "避難生活に役立つ情報":141}    

#検索数
for y in [10,20,30,50,100]:
    if y!=30:
        select=''
    else:
        select=' selected="selected"'
    options_limit+="<option%s>%d</option>" % (select, y)
#カテゴリ
options_category+='<option selected="selected">全カテゴリ</option>'
for k,i in cat.items():
    if i!=0:
        select=''
        options_category+="<option%s>%s</option>" % (select, k)


form=cgi.FieldStorage()
limit_str=form.getvalue('limit', '')
category_key=form.getvalue('category', '')

if limit_str.isdigit():
    category_id=cat[category_key]
    id_str=str(category_id)

    file_name = 'data/blogclust' + limit_str + '-' + id_str + '.txt'
    f = open(file_name, "r")
    t=f.read()
    f.close()

#    feedlist = generatefeedvector.go(limit_str,id_str)
#    t = clusters.go(limit_str,id_str,feedlist)

    content = 'タイトルをクリックすると該当ページに移動します。<br/>（sinsai.infoの「レポート一覧」に未登録だと表示されません）<br/><br/>'
    content += '<div id="dendrogramFrame">%s</div>' % t

    content += "\n"


print "Content-type: text/html;charset=utf-8\n"
print html_body % (css_code, tracking_code, options_limit, options_category, content)
