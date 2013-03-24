#!usr/bin/python
import fbconsole
from requests import get
import signal
from sys import exit , stdout
from os import makedirs
from calendar import isleap
from datetime import datetime
import sqlite3

def signal_handler(signal, frame):
  try:
      conn.commit()
      print'\n\nDB Saved. DB name: ',file_name
  except:
      print '\nDB not saved.'
  
  fbconsole.logout()
  print '\nLogout Successful.'
  print 'Ctrl+C press event. Exiting Now.\n'
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
  me=get(url_me).json()           #fetching user's about me
  global username
  global userid
  global file_name
  username = me['name']
  userid = me['id']
  now=str(datetime.now())[:-7]
  global conn
  
  try:
    makedirs('OUTPUT/')
    print 'Output directory created.'
  except:
    pass
  
  file_name='OUTPUT/'+username+'_'+now.split()[0]+'_'+now.split()[1]+'.db'
  conn = sqlite3.connect(file_name)
  c = conn.cursor() 

  
  #Creating tables
  c.execute('''CREATE TABLE posts
               ('Serial','Account ID','Account name','User ID','User Name','P    ost ID','Date Created','Time Created','Date Updated','Time Updated','Life','Lif    e (in hours)','Type','Comments','Likes')''' )
  c.execute('''CREATE TABLE comments
               ('Serial','Account ID','Account name','Post ID','Comment ID','comment_by_id','comment_by','date','time','likes')''')
  c.execute('''CREATE TABLE likes
               ('Serial','Account ID','Account name','Post ID','Created Date    ','Created Time','like_by_id','like_by')''')
  c.execute('''CREATE TABLE profile
               ('Account ID', 'Account Name', 'username', 'gender', 'current location')''')  
  print 
  row_feed=1 ; row_comments = 1 ; row_likes = 1
  
  profile_list = [userid,username,me['username'],me['gender']]
  try : profile_list.append(me['location']['name'])
  except: profile_list.append(me['hometown']['name'])
  c.execute('INSERT INTO profile VALUES (?,?,?,?,?)', profile_list)
  
  while len(req.json()['data'])!=0:
    #print url
    for post in req.json()['data']:
      #printing status in the terminal
      out = username + '    '+str(post['created_time'][0:10])+'    Posts : '+str(row_feed)+'    Comments : '+str(row_comments-1)+'    Likes : '+str(row_likes-1) 
      stdout.write('\r'+out)
      stdout.flush()
      
      #Sending a post to wall_posts , wall_comments , wall_likes which filters out the required data and writes them to the corresponding tables
      row_feed, c = wall_posts(c, row_feed, post )
      row_comments, c = wall_comments(c, row_comments , post)
      row_likes, c = wall_likes(c, row_likes , post)
    

    #Moving over to the next page
    url=req.json()['paging']['next']
    req = get(url)
  
  #Saving the database after fetching all data
  
  conn.commit()
  print'\n\nDatabase Saved. Database name : ',file_name

  #logging out of fbconsole
  fbconsole.logout()
  print '\nfbconsole log out successful.\n'
 
def wall_posts(c, row, post):
    #print row
    posts_list=[row, username, userid, post['from']['id'], post['from']['name'], post['id'], post['created_time'][0:10], post['created_time'][11:-5], post['updated_time'][0:10], post['updated_time'][11:-5], life_info(post['created_time'], post['updated_time']), post['type'], post['comments']['count']]
    try: posts_list.append(post['likes']['count'])    
    except : posts_list.append(0)
    posts_list.insert(12,timecalc(posts_list[10]))
    
    c.execute("INSERT INTO posts VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", posts_list)
    return row+1, c


def wall_comments(c, row, post):
    
    if post['comments']['count']!=0: 
        try:
	        for comment in post['comments']['data']:
	            comment_list=[row, userid, username, post['id'], comment['id'], comment['from']['id'], comment['from']['name'], comment['created_time'][0:10], comment['created_time'][11:-5]]
	            try: comment_list.append(comment['likes'])
	            except: comment_list.append(0)
	  
                c.execute("INSERT INTO comments VALUES (?,?,?,?,?,?,?,?,?,?)",comment_list)
        except:
            pass
        row+=1
    return row, c
    
    
      
def wall_likes(c, row, post):
    #filtering data and writing them to the wall_feed_sheet
    col = 0
    try:
        if post['likes']['count']!=0:
            try:
    	        for like in  post['likes']['data']:
                    like_list = [row, userid, username, post['id'], post['created_time'][0:10], post['created_time'][11:-5], like['id'], like['name']]
                    
                    c.execute("INSERT INTO likes VALUES (?,?,?,?,?,?,?,?)",like_list)
    	            row+=1
            except:
                pass
    except:
        pass
    return row, c
  
def timecalc(time):
    #this method returns the lifetime of the post (in hours) 
    #time is a string of the format YY years, MM months, DD days, hh:mm:ss or simply hh:mm:ss as the case may be
    hours=0 ; time=time.split()
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
    #This method returns to values. 
    #First is the total time difference between start and end in the format YY years, MM months, DD days, hh:mm:ss or simply hh:mm:ss as the case may be
    #Second is the duration in hours
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
    return life

if __name__ == '__main__':
     main()
