import fbconsole
import requests
import signal
import sys
import calendar
import xlwt 
from datetime import datetime
book=xlwt.Workbook()
file_name='temp.xls'
def signal_handler(signal, frame):
  print file_name
  book.save(file_name)
  if file_name=='temp.xls':
     print '\nTemporary workbook saved. Look for temp.xls .'
  
  else: 
     
     print'\nWorkbook Saved. Workbook name : '+file_name
  print 'Ctrl+C press event. Exiting Now.'
  fbconsole.logout()
  sys.exit(0)

def main():
  signal.signal(signal.SIGINT, signal_handler)
  fbconsole.AUTH_SCOPE=['read_stream']
  fbconsole.authenticate()
  url=fbconsole.graph_url('/me/feed')
  req = requests.get(url)
  url_me=fbconsole.graph_url('/me')
  req_me=requests.get(url_me)
  file_name=req_me.json['name']+'_'+str(datetime.now())[0:10]+'.xls'
  row=1
  print file_name  
  sheet1 = book.add_sheet('Facebook')
  font = xlwt.Font() ; font.bold = True
  style = xlwt.XFStyle() ; style.font = font
  align = xlwt.Alignment()
  align.horz = xlwt.Alignment.HORZ_CENTER ; style.alignment = align
  #for x,y in req.json.iteritems():
  #    print x
  heading = ['Sl. No. ','User ID', 'User Name', 'Post ID', 'Date Created', 'Time Created', 'Date Updated','Time Updated', 'Life', 'Life (in hours)', 'Type', 'Comments', 'Likes']
  width   = [0.64,1.29,2.00,2.28,1.08,1.08,1.08,1.08,2.51,1.09,0.68,0.83,0.48]
  for i in range(len(heading)):
    sheet1.write(0,i, heading[i], style)
    sheet1.col(i).width=3333*width[i]
  while len(req.json['data'])!=0:
    print url
    
    for i in req.json['data']:
      col = 0
      sheet1.write(row,col,row) ; col+=1
      sheet1.write(row,col,i['from']['id']) ; col+=1
      sheet1.write(row,col,i['from']['name']) ; col+=1
      sheet1.write(row,col,i['id']) ; col+=1
      
      #try: sheet1.write(row,col,i['story']) ; col+=1
      #except: sheet1.write(row,col,i['message']) ; col+=1
      sheet1.write(row,col,i['created_time'][0:10]) ; col+=1
      sheet1.write(row,col,i['created_time'][11:-5]) ; col+=1
      sheet1.write(row,col,i['updated_time'][0:10]) ; col+=1  
      sheet1.write(row,col,i['updated_time'][11:-5]) ; col+=1
      print row,'\t',i['created_time'][0:10]+', '+i['created_time'][12:-5],'\t',i['type'],'\t'+i['from']['name']
      life,life_round=life_info(i['created_time'], i['updated_time'])
      sheet1.write(row,col,life) ; col+=1
      sheet1.write(row,col,life_round) ; col+=1

      sheet1.write(row,col,i['type']) ; col+=1  
      sheet1.write(row,col, i['comments']['count']) ; col+=1  	
      try:
          sheet1.write(row,col, i['likes']['count']) ; col+=1
      except:
          sheet1.write(row,col,0) ; col+=1
      
      row+=1
    
    url=req.json['paging']['next']
    req = requests.get(url)

  print 'Saving Workbook...'
  book.save(file_name)
  fbconsole.logout()
  print 'Log out successful.'
 
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
   
    if calendar.isleap(a[0]) and a[1]==2 :am=1
  
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
