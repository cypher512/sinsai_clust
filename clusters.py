# -*- coding: utf-8 -*-
import datetime
import sys
from PIL import Image,ImageDraw
import ImageFont
import os

def readfile(filename):
  lines=[line for line in file(filename)]
  
  # First line is the column titles
  colnames=lines[0].strip().split('\t')[1:]
  rownames=[]
  data=[]

  try:
    for line in lines[1:]:
      p=line.strip().split('\t')
    # First column in each row is the rowname
      rownames.append(p[0])
    # The data for this row is the remainder of the row
      data.append([float(x) for x in p[1:]])
  except:
    print p[1:]
    for x in p[0:]:
      print x,
  return rownames,colnames,data


from math import sqrt

def pearson(v1,v2):
  # Simple sums
  sum1=sum(v1)
  sum2=sum(v2)
  
  # Sums of the squares
  sum1Sq=sum([pow(v,2) for v in v1])
  sum2Sq=sum([pow(v,2) for v in v2])	
  
  # Sum of the products
  pSum=sum([v1[i]*v2[i] for i in range(len(v1))])
  
  # Calculate r (Pearson score)
  if len(v1)==0: return 0
  num=pSum-(sum1*sum2/len(v1))
  den=sqrt((sum1Sq-pow(sum1,2)/len(v1))*(sum2Sq-pow(sum2,2)/len(v1)))
  if den==0: return 0

  return 1.0-num/den

class bicluster:
  def __init__(self,vec,left=None,right=None,distance=0.0,id=None):
    self.left=left
    self.right=right
    self.vec=vec
    self.id=id
    self.distance=distance

def hcluster(rows,distance=pearson):
  distances={}
  currentclustid=-1

  # Clusters are initially just the rows
  clust=[bicluster(rows[i],id=i) for i in range(len(rows))]

  while len(clust)>1:
    lowestpair=(0,1)
    closest=distance(clust[0].vec,clust[1].vec)

    # loop through every pair looking for the smallest distance
    for i in range(len(clust)):
      for j in range(i+1,len(clust)):
        # distances is the cache of distance calculations
        if (clust[i].id,clust[j].id) not in distances: 
          distances[(clust[i].id,clust[j].id)]=distance(clust[i].vec,clust[j].vec)

        d=distances[(clust[i].id,clust[j].id)]

        if d<closest:
          closest=d
          lowestpair=(i,j)

    # calculate the average of the two clusters
    mergevec=[
    (clust[lowestpair[0]].vec[i]+clust[lowestpair[1]].vec[i])/2.0 
    for i in range(len(clust[0].vec))]

    # create the new cluster
    newcluster=bicluster(mergevec,left=clust[lowestpair[0]],
                         right=clust[lowestpair[1]],
                         distance=closest,id=currentclustid)

    # cluster ids that weren't in the original set are negative
    currentclustid-=1
    del clust[lowestpair[1]]
    del clust[lowestpair[0]]
    clust.append(newcluster)

  return clust[0]

def printclust(clust,labels=None,n=0):
  # indent to make a hierarchy layout
  for i in range(n): print ' ',
  if clust.id<0:
    # negative id means that this is branch
    print '-'
  else:
    # positive id means that this is an endpoint
    if labels==None: print clust.id
    else: print labels[clust.id]

  # now print the right and left branches
  if clust.left!=None: printclust(clust.left,labels=labels,n=n+1)
  if clust.right!=None: printclust(clust.right,labels=labels,n=n+1)

def getheight(clust):
  # Is this an endpoint? Then the height is just 1
  if clust.left==None and clust.right==None: return 1

  # Otherwise the height is the same of the heights of
  # each branch
  return getheight(clust.left)+getheight(clust.right)

def getdepth(clust):
  # The distance of an endpoint is 0.0
  if clust.left==None and clust.right==None: return 0

  # The distance of a branch is the greater of its two sides
  # plus its own distance
  return max(getdepth(clust.left),getdepth(clust.right))+clust.distance

H_SCALE=28 #縦の幅

def drawdendrogram(clust,labels,id_str,limit_str,feedlist):
  # height and width
  h=getheight(clust)*H_SCALE
  w=1200
  depth=getdepth(clust)

  # width is fixed, so scale distances accordingly
  if depth==0: 
    scaling=0
  else:
    scaling=float(w-600)/depth

  # Draw the first node
  t = ""
  t = drawnode(clust,10,(h/2),scaling,labels,feedlist)
  return t

def drawnode(clust,x,y,scaling,labels,feedlist):
  coords = {}
  

  t=''

  if clust.id<0:
    h1=getheight(clust.left)*H_SCALE
    h2=getheight(clust.right)*H_SCALE
    top=y-(h1+h2)/2
    bottom=y+(h1+h2)/2
    # Line length
    ll=clust.distance*scaling

    # Vertical line from this cluster to children    
    t+='<div class="cap"  style="top:'+str(top+h1/2)+"px;left:"+str(x)+"px;height:"+str(h1/2 + h2/2)+'px;"></div>';        
    # Horizontal line to left item
    t+='<div class="drop" style="top:'+str(top+h1/2)+"px;left:"+str(x)+"px;width:"+str(ll)+'px;">&nbsp;</div>';     
    # Horizontal line to right item
    t+='<div class="drop" style="top:'+str(bottom-h2/2)+"px;left:"+str(x)+"px;width:"+str(ll)+'px;">&nbsp;</div>';        

    # Call the function to draw the left and right nodes
    t += drawnode(clust.left,x+ll,top+h1/2,scaling,labels,feedlist)
    t += drawnode(clust.right,x+ll,bottom-h2/2,scaling,labels,feedlist)

  else:   
    # If this is an endpoint, draw the item label
    title = unicode(labels[clust.id],"utf-8")

    #y 　縦 x 　 横
    #top 縦 left 横
    color = "#f0f0f0"
    t+='<div class="leaf" style="background:'+color+";top:"+str(y-7)+"px;left:"+str(x+5)+'px;"><b>'+'<a href="http://www.sinsai.info/reports/view/'+feedlist[title]+'">'+ title+'</a></b></div>';

  return t


def go(limit_str,id_str,feedlist):
    in_file='/var/www/cgi-bin/data/blogdata' + limit_str + "-" + id_str + ".txt"
    out_file = '/var/www/cgi-bin/data/blogclust' + limit_str + '-' + id_str + '.txt'
    blognames,words,data=readfile(in_file)
    if len(data)==0:
#  print t
      t = '<h1>Dataがありません</h1>'

      f = open(out_file, "w")
      f.write(t)
      f.close()
      return t 
      
    clust=hcluster(data)
    t = drawdendrogram(clust,blognames,id_str,limit_str,feedlist)
#  print t
    f = open(out_file, "w")
    f.write(t)
    f.close()
    return t
    
if __name__=='__main__':
  go(sys.argv[1])

