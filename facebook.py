#!usr/bin/python
import fbconsole
from requests import get
import signal
from sys import exit , stdout
from os import makedirs
from calendar import isleap
from xlwt import Workbook 
from datetime import datetime


def signal_handler(signal, frame):
  book_feed.save('OUTPUT/'+file_name_feed)
  book_comments.save('OUTPUT/'+file_name_comments)
  book_likes.save('OUTPUT/'+file_name_likes)
  print'\n\nWorkbook Saved. Workbook names :\n','wall      : ',file_name_feed, '\ncomments  : ',file_name_comments ,'\nlikes     : ',file_name_likes
  
  fbconsole.logout()
  print '\nLogout Successful.'
  print 'Ctrl+C press event. Exiting Now.'
  exit(0)

def main():
  #ctrl+c interrupt event
  signal.signal(signal.SIGINT, signal_handler)
  
  #authenticating permission
  fbconsole.AUTH_SCOPE=['read_stream']
  fbconsole.authenticate()

  url=fbconsole.graph_url('/me/feed')   #fb graph url for user's wall feed
  req = get(url)               #requests module to get data from the url
  url_me=fbconsole.graph_url('/me')     #fb graph url for user's about me
  req_me=get(url_me)           #fetching user's about me
  global username
  global userid
  global file_name_feed ; global file_name_comments ; global file_name_likes
  username = req_me.json()['name']
  userid = req_me.json()['id']
  date_time_now=str(datetime.now())[:-7]
  file_name_feed = username+'_'+date_time_now+'_wall.xls'
  file_name_comments =  username+'_'+date_time_now+'_comments.xls'
  file_name_likes =  username +'_'+date_time_now+'_likes.xls'
  
  try:
    makedirs('OUTPUT/')
    print 'Output directory created.'
  except:
    pass
  
  #creating workbook 
  global book_comments ; global book_feed ; global book_likes
  book_feed=Workbook()
  book_comments=Workbook()
  book_likes=Workbook()
  
  #Creating excel sheet
  wall_feed_sheet = book_feed.add_sheet('feed')
  wall_comments_sheet = book_comments.add_sheet('comments')
  wall_likes_sheet = book_likes.add_sheet('likes')
  #Setting design for writing
  
  #Lists data to publish as headers
  heading_feed = ['Serial','Account ID','Account name','User ID','User Name','Post ID','Date Created','Time Created','Date Updated','Time Updated','Life','Life (in hours)','Type','Comments','Likes']
  heading_comments = ['Serial','Account ID','Account name','Post ID','Comment ID','comment_by_id','comment_by','date','time','likes']
  heading_likes = ['Serial','Account ID','Account name','Post ID','Created Date','Created Time','like_by_id','like_by']
  #Writing headers
  for i in range(len(heading_feed)): wall_feed_sheet.write(0,i, heading_feed[i])
  for i in range(len(heading_comments)): wall_comments_sheet.write(0,i, heading_comments[i])
  for i in range(len(heading_likes)): wall_likes_sheet.write(0,i, heading_likes[i])
  print 
  row_feed=1 ; row_comments = 1 ; row_likes = 1
  while len(req.json()['data'])!=0:
    #print url
    
    for i in req.json()['data']:
      out = username + '    '+str(i['created_time'][0:10])+'    Posts : '+str(row_feed)+'    Comments : '+str(row_comments-1)+'    Likes : '+str(row_likes-1) 
      stdout.write('\r'+out)
      stdout.flush()
        
      row_feed, wall_feed_sheet = wall_feed(wall_feed_sheet, row_feed, i )
      row_comments, wall_comments_sheet = wall_comments(wall_comments_sheet, row_comments , i)
      row_likes, wall_likes_sheet = wall_likes(wall_likes_sheet, row_likes , i)
      
    
    url=req.json()['paging']['next']
    req = get(url)

  book_feed.save('OUTPUT/'+file_name_feed)
  book_comments.save('OUTPUT/'+file_name_comments)
  book_likes.save('OUTPUT/'+file_name_likes)
  print'\n\nWorkbook Saved. Workbook names :\n','wall      : ',file_name_feed, '\ncomments  : ',file_name_comments ,'\nlikes     : ', file_name_likes

  fbconsole.logout()
  print '\nLog out successful.'
 
def wall_feed(wall_feed_sheet, row, i):
      col = 0
      wall_feed_sheet.write(row,col,row) ; col+=1
      wall_feed_sheet.write(row,col,username) ; col+=1
      wall_feed_sheet.write(row,col,userid) ; col+=1
      wall_feed_sheet.write(row,col,i['from']['id']) ; col+=1
      wall_feed_sheet.write(row,col,i['from']['name']) ; col+=1
      wall_feed_sheet.write(row,col,i['id']) ; col+=1
      wall_feed_sheet.write(row,col,i['created_time'][0:10]) ; col+=1
      wall_feed_sheet.write(row,col,i['created_time'][11:-5]) ; col+=1
      wall_feed_sheet.write(row,col,i['updated_time'][0:10]) ; col+=1  
      wall_feed_sheet.write(row,col,i['updated_time'][11:-5]) ; col+=1
      life,life_round=life_info(i['created_time'], i['updated_time'])
      wall_feed_sheet.write(row,col,life) ; col+=1
      wall_feed_sheet.write(row,col,life_round) ; col+=1

      wall_feed_sheet.write(row,col,i['type']) ; col+=1  
      wall_feed_sheet.write(row,col, i['comments']['count']) ; col+=1  	
      try:
          wall_feed_sheet.write(row,col, i['likes']['count']) ; col+=1
      except:
          wall_feed_sheet.write(row,col,0) ; col+=1
      row+=1
      return row, wall_feed_sheet
      
def wall_comments(wall_comments_sheet, row, i):
    col = 0
    try:
        if i['comments']['count']!=0:
            try:
                for comment in  i['comments']['data']:
                    wall_comments_sheet.write(row,col, row) ; col+=1
                    wall_comments_sheet.write(row,col, userid) ; col+=1
                    wall_comments_sheet.write(row,col, username) ; col+=1
                    wall_comments_sheet.write(row,col, i['id']) ; col+=1
                    wall_comments_sheet.write(row,col, comment['id']) ; col+=1
                    wall_comments_sheet.write(row,col, comment['from']['id']) ; col+=1
                    wall_comments_sheet.write(row,col, comment['from']['name']) ; col+=1
                    wall_comments_sheet.write(row,col, comment['created_time'][0:10]) ; col+=1
                    wall_comments_sheet.write(row,col, comment['created_time'][11:-5]) ; col+=1
                    try:
                        wall_comments_sheet.write(row,col, comment['likes']) ; col+=1
                    except:
                        wall_comments_sheet.write(row,col, 0 ) ; col+=1
                    row+=1
                    col=0
            except:
                pass
    except:
        pass
    return row, wall_comments_sheet
      
def wall_likes(wall_likes_sheet, row, i):
    col = 0
    try:
        if i['likes']['count']!=0:
            try:
    	        for like in  i['likes']['data']:
		    wall_likes_sheet.write(row,col, row) ; col+=1
                    wall_likes_sheet.write(row,col, userid) ; col+=1
                    wall_likes_sheet.write(row,col, username) ; col+=1
                    wall_likes_sheet.write(row,col, i['id']) ; col+=1
                    wall_likes_sheet.write(row,col, i['created_time'][0:10]) ; col+=1
                    wall_likes_sheet.write(row,col, i['created_time'][11:-5]) ; col+=1
                    wall_likes_sheet.write(row,col, like['id']) ; col+=1
                    wall_likes_sheet.write(row,col, like['name']) ; col+=1
    	            row+=1
                    col=0
            except:
                pass
    except:
        pass
    return row, wall_likes_sheet
  
def timecalc(time):
    hours=0 ; time=str(time).split()
    for i in range(len(time)):
        if time[i].find('year')!=-1:	hours += int(time[i-1]) * 8760
        if time[i].find('month')!=-1:	hours += int(time[i-1]) * 720
        if time[i].find('day')!=-1:	hours += int(time[i-1]) * 24
    time = time[-1].split(':')
    try:
	hours += int(time[0])
        if int(time[1]) >= 30 : hours += 1
        return hours
    except:
	if hours>0:
	    return hours  # when time mentioned only as years,months or days
        else:
            return ''	  # in case of a string (the heading)

def life_info(start , end):
    a = [int(start[0:4])]
    for i in range(5,18,3):
        a.append(int(start[i:i+2]))
    b = [int(end[0:4])]
    for i in range(5,18,3):
        b.append(int(end[i:i+2]))
    m = [31,28,31,30,31,30,31,31,30,31,30,31]
    am = 0
    c=[]
    c.append(b[0]-a[0])
    if a[1] > b[1] : 
        c[0] -= 1
        c.append(12 - a[1] + b[1] )
    else:
        c.append( b[1] - a[1] )
   
    if isleap(a[0]) and a[1]==2 :am=1
  
    if a[2] > b[2] : 
        c[1] -= 1
        c.append( m[a[1]-1] + am -a[2] + b[2] )
    else:
        c.append( b[2] - a[2] ) 

    if a[3] > b[3] : 
        c[2] -= 1
        c.append( 24 - a[3] + b[3] )
    else:
        c.append(b[3] - a[3] )

    if a[4] > b[4] :
        c[3] -= 1
        c.append( 60 - a[4] + b[4] )
    else:
        c.append(b[4] - a[4] )
    if a[5] > b[5] :
        c[4] -= 1
        c.append( 60 - a[5] + b[5] )
    else:
        c.append(b[5] - a[5] )

    for i in range(5,0,-1):
        if c[i]==-1:
            c[i]=0
            c[i-1] -= 1
    life=''
    
    if c[0]!=0:  
        life = str(c[0])+' year' 
        if c[0]>1 : life += 's' 
        life+=', '
    if c[1]!=0:
        life +=str(c[1])+' month'
        if c[1]>1 : life += 's'
        life+=', '
    if c[2]!=0:
        life +=str(c[2])+' day'      
        if c[2]>1 : life += 's'
        life+=', '
    if len(str(c[3]))==1: life+='0'
    life += str(c[3])+':'
    if len(str(c[4]))==1: life+='0'
    life += str(c[4])+':'
    if len(str(c[5]))==1: life+='0'
    life += str(c[5])
    return life,timecalc(life)

if __name__ == '__main__':
     main()
