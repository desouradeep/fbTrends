#!usr/bin/python
import fbconsole
from requests import get
import signal
from sys import exit , stdout
from os import makedirs,path
from shutil import copyfile
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
  print '\nfbconsole logout Successful.'
  print 'Ctrl+C press event. Exiting Now.\n'
  exit(0)

def main():
  #ctrl+c interrupt event
  try:
      fbconsole.logout()
  except:
      pass
  global file_name
  file_name = 'fb_data.db'
  try:
      current_dir = path.abspath('.')
      src = path.join(current_dir,file_name)
      backup_file_name = file_name+'.backup'
      dest = path.join(current_dir,backup_file_name)
      copyfile(src,dest)
      print '\nDatabase backedup. Backup file name : %s.\n' % (backup_file_name)
  except:
      print '\nNo database to backup.\n'

      
  signal.signal(signal.SIGINT, signal_handler)
  
  #authenticating permission
  fbconsole.AUTH_SCOPE=['read_stream']
  fbconsole.authenticate()

  url=fbconsole.graph_url('/me/feed')   #fb graph url for user's wall feed
  req = get(url)                   #requests module to get data from the url
  #except ConnectionError: network_error()
  url_me=fbconsole.graph_url('/me')     #fb graph url for user's about me
  me=get(url_me).json()            #fetching user's about me
  print url_me
  #except ConnectionError: network_error()
  global name
  global userid
  
  name = me['name']
  userid = me['id']
  now = str(datetime.now())[:-7]
  global conn
  
  conn = sqlite3.connect(file_name)
  c = conn.cursor() 

  
  #Creating tables
  try:
      c.execute('''CREATE TABLE posts
               ('Account name','Account_ID','User ID','User Name','Post ID','Date Created','Time Created','Date Updated','Time Updated','Life','Life (in hours)','Type','Comments','Likes')''' )
      c.execute('''CREATE TABLE comments
               ('Account_ID','Account name','Post ID','Comment ID','comment_by_id','comment_by','date','time','likes')''')
      c.execute('''CREATE TABLE likes
               ('Account_ID','Account name','Post ID','Created Date','Created Time','like_by_id','like_by')''')
      c.execute('''CREATE TABLE profile
               ('Account_ID', 'Account Name', 'username', 'gender', 'location')''')  
      print '\nTables created. Adding data to the tables.'
  except:
      print '\nTables already exist. Adding data to the tables.'
  print 
  row_feed=1 ; row_comments = 1 ; row_likes = 1
  
  
  c.execute('DELETE FROM profile WHERE Account_ID=?',(userid,))
  c.execute('DELETE FROM posts WHERE Account_ID=?',(userid,))
  c.execute('DELETE FROM comments WHERE Account_ID=?',(userid,))
  c.execute('DELETE FROM likes WHERE Account_ID=?',(userid,))
  try:
    username = me['username']
  except: 
    username = 'N/A'
    print 'Username is not accesible.\n'
    
  profile_list = [userid, name, username, me['gender']]

  current_city = False ; home_town = False
  try :
    profile_list.append(me['location']['name'])
    current_city = True
  except :
    pass
 
  if current_city == False:
    try: 
        profile_list.append(me['hometown']['name'])
        home_town = True
    except: 
        pass
  
  if current_city is False:
      print 'Current City not accesible.\n'
      if home_town is False : print 'Home Town not accesible.\n'
  if current_city is False and home_town is False: profile_list.append('N/A')

  c.execute('INSERT INTO profile VALUES (?,?,?,?,?)', profile_list)
  while len(req.json()['data'])!=0:
    #print url
    for post in req.json()['data']:
      #printing status in the terminal
      out = name + '    '+str(post['created_time'][0:10])+'    Posts : '+str(row_feed)+'    Comments : '+str(row_comments-1)+'    Likes : '+str(row_likes-1) 
      stdout.write('\r'+out)
      stdout.flush()
      
      #Sending a post to wall_posts , wall_comments , wall_likes which filters out the required data and writes them to the corresponding tables
      row_feed, c = wall_posts(c, row_feed, post )
      row_comments, c = wall_comments(c, row_comments , post)
      row_likes, c = wall_likes(c, row_likes , post)

    #Moving over to the next page
    url=req.json()['paging']['next']
    req = get(url)
    #except ConnectionError: network_error()
  
  #Saving the database after fetching all data
  
  conn.commit()
  print'\n\nDatabase Saved. Database name : ',file_name
  
  #logging out of fbconsole
  fbconsole.logout()
  print '\nfbconsole log out successful.\n'
 
def wall_posts(c, row, post):
    #print row
    lifeinfo = life_info(post['created_time'], post['updated_time'])
    hours = timecalc(lifeinfo)
    posts_list=[name, userid, post['from']['id'], post['from']['name'], post['id'], post['created_time'][0:10], post['created_time'][11:-5], post['updated_time'][0:10], post['updated_time'][11:-5], lifeinfo , hours , post['type'], post['comments']['count']]
    try: posts_list.append(post['likes']['count'])    
    except : posts_list.append(0)
    #posts_list.insert(12,timecalc(posts_list[10]))
    c.execute("INSERT INTO posts VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", posts_list)
    return row+1, c


def wall_comments(c, row, post):
    
    if post['comments']['count']!=0: 
        try:
	        for comment in post['comments']['data']:
	            comment_list=[userid, name, post['id'], comment['id'], comment['from']['id'], comment['from']['name'], comment['created_time'][0:10], comment['created_time'][11:-5]]
	            try: comment_list.append(comment['likes'])
	            except: comment_list.append(0)
	  
                c.execute("INSERT INTO comments VALUES (?,?,?,?,?,?,?,?,?)",comment_list)
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
                    like_list = [userid, name, post['id'], post['created_time'][0:10], post['created_time'][11:-5], like['id'], like['name']]
                    
                    c.execute("INSERT INTO likes VALUES (?,?,?,?,?,?,?)",like_list)
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
	    return hours  # when time mentioned only as years,months or days

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
