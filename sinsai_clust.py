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
  </head>
  <body>
  <form method="GET" action="/cgi-bin/sinsai_clust.py">
    sinsai.infoから検索する記事の件数を選んで下さい:
    <select name="limit">
      %s
    </select>
    <input type="submit" value="検索" />
  </form>
  %s
  </body>
</html>"""



options_limit=''
content=''

    

for y in range(10, 110, 10):
    if y!=30:
        select=''
    else:
        select=' selected="selected"'
    options_limit+="<option%s>%d</option>" % (select, y)


form=cgi.FieldStorage()
limit_str=form.getvalue('limit', '')
if limit_str.isdigit():
    feedlist,d_str = generatefeedvector.go(limit_str)
    coords,h,w,jpg_name = clusters.go(d_str)
    content = 'タイトルをクリックすると該当ページに移動します。<br/>（sinsai.infoの「レポート一覧」に未登録だと表示されません）<br/>'
    content += '<img src="%s" usemap="#sample" alt="サンプル" width="%d" height="%d">' % (jpg_name,w,h)
    content += '<map name="sample">'
    content += "\n"
    for k in coords.keys():
        content += '<area href="http://www.sinsai.info/reports/view/%s" shape="rect" alt="四角形" coords="%d, %d, %d, %d">' % (feedlist[k], coords[k][0],coords[k][1],coords[k][2],coords[k][3],)
        content += "\n"
    content += '</map>'
    content += "\n"

print "Content-type: text/html;charset=utf-8\n"
print html_body % (options_limit, content)
