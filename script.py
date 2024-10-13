import os,sys,subprocess,requests,sys,feedparser,json,smtplib,logging,time, getpass
from redis import StrictRedis

adress='D:\\Temp\\'
#adress='/home/farnood/Desktop/myProject/'
email,Epassword,emailTo = ("","","")

#if it is the 8th time running it send an email of whole time and average time
#the 8th time running would be 9 pm if we start at 00 am 
#tries 5 times
def isNinePM(wholeTime):
    global email, Epassword,emailTo
    tries=0
    while tries<5:  
        try:
            #connectint to redis
            myRedisUrl='redis://localhost:6379/0'
            myRedis=StrictRedis.from_url(myRedisUrl,decode_responses=True)
            #if this the first time ever running program 
            #it sets everything 0
            if myRedis.get('turn')!='0' and myRedis.get('turn')!='1' and myRedis.get('turn')!='2' and myRedis.get('turn')!='3' and myRedis.get('turn')!='4' and myRedis.get('turn')!='5' and myRedis.get('turn')!='6' and myRedis.get('turn')!='7':
                myRedis.set('turn','0')
                myRedis.set('whole',str(wholeTime))
                return
            #if it isn't 9 pm these should happen:
            #1- turn is added one more to get closer to 9 pm
            #2- and whole  time is added with this running time
            if myRedis.get('turn')!='7':
                myRedis.set('turn',str(int(myRedis.get('turn'))+1))
                myRedis.set('whole',str('{:.2f}'.format(float(myRedis.get('whole'))+float(wholeTime ))))
                return
            #if this is 9 pm these should happen:
            #1- turn is set 0 again
            #2- whole time and average time send to email
            #3- whole time sets 0 again
            myRedis.set('turn','0')
            wholeTime=float(myRedis.get('whole'))+float(wholeTime)
            myRedis.set('whole','0.0')
            #connecting to gmail:
            server=smtplib.SMTP("smtp.gmail.com",587)
            server.starttls()
            
            
            server.login(email,Epassword)
            server.sendmail(email,emailTo, ('Hello there'+'\n'+'Whole time was: '+str(wholeTime)+' s\nAverage time was: '+str("{:.2f}".format(wholeTime/8))+' s').encode('utf-8'))
            server.quit()
            break
        except Exception as err:
            tries+=1
            print("couldn't send Email at nine pm: ",tries,"tries")
            myErr="couldn't send Email at nine pm"
            myLog.logThis(myErr)


#does everything about logging:
#1- takes the beggining time and ending time and calculates the whole time 
#2- logs strings in the log file
#3- creates the log file
class logDealer:
    def __init__(self,firstTime):
        self.firstTime=firstTime
        self.secondTime=0
        myResult=time.localtime(firstTime)
        #saves name of our file:
        self.logName=str(myResult.tm_year)+str('{:02d}'.format(myResult.tm_mon))+str('{:02d}'.format(myResult.tm_mday))+str('{:02d}'.format(myResult.tm_hour))+str('{:02d}'.format(myResult.tm_min))+str('{:02d}'.format(myResult.tm_sec))+'.log'
        self.logAdress=adress+'py_log/'+self.logName
    def setSecondTime(self,secondTime):#takes whole time and log it:
        self.wholeTime=secondTime-self.firstTime
        logging.basicConfig(filename=self.logAdress,filemode='a',format='%(message)s')
        logging.warning('The whole time of proccess was: '+str(self.wholeTime))
        isNinePM('{:.2f}'.format(self.wholeTime))
    def logThis(self, myString):#takes a string an logs it:
        logging.basicConfig(filename=self.logAdress,filemode='a',format='%(message)s')
        logging.warning(myString)



#change month name to month number:
def monthNumber(month):
    if month=='Jan':return'01'
    if month=='Feb':return'02'
    if month=='Mar':return'03'
    if month=='Apr':return'04'
    if month=='May':return'05'
    if month=='Jun':return'06'
    if month=='Jul':return'07'
    if month=='Aug':return'08'
    if month=='Sep':return'09'
    if month=='Oct':return'10'
    if month=='Nov':return'11'
    if month=='Dec':return'12'
    return month


#if the necessary directories in py_report don't exist it makes them:
def makingUnexistedDirectory(year,month,day):
    try:
        os.mkdir(adress+"py_report/"+year)
    except:
        pass
    try:
        os.mkdir(adress+"py_report/"+year+'/'+month)
    except:
        pass
    try:
        os.mkdir(adress+"py_report/"+year+'/'+month+'/'+day)
    except:
        pass



#open and write all file with guid.json name
def writeFile(mydict):
    done=0
    try:
        myGuid=str(mydict['id'])
        pubDateRaw=mydict['published']
        pubDate=list(pubDateRaw.split())
        year,month,day=pubDate[3],monthNumber(pubDate[2]),pubDate[1]
        makingUnexistedDirectory(year,month,day)
        newAdress=adress+'py_report/'+year+'/'+month+'/'+day+'/'
        f=open(newAdress+myGuid+".json",'w')
        f.close()
        with open(newAdress+myGuid+'.json', 'a', encoding='utf8') as json_file:
            json.dump('# title: '+mydict['title']+'\n    ',json_file,ensure_ascii=False)
            json.dump('# link: '+mydict['link']+'\n    ',json_file,ensure_ascii=False)
            json.dump('# guid: '+mydict['id']+'\n    ',json_file,ensure_ascii=False)
            # json.dump('# category: '+mydict['tags'][0]['term']+'\n    ',json_file,ensure_ascii=False)
            json.dump('# description: '+mydict['summary']+'\n    ',json_file,ensure_ascii=False)
            json.dump('# pubDate: '+pubDateRaw+'\n    ',json_file,ensure_ascii=False)
        done=1
        print("%2d"%(x+1),str(mydict['id']),"Completed!")
    except Exception as err:
        myErr="Couldn't open file"
        myLog.logThis(myErr)
        print("Couldn't open file:",str(err))
    finally:
        return done
        json_file.close()



#check if guid is new or not returns 0 if new
def checkGuid(myGuid):
    myRedisUrl='redis://localhost:6379/0'
    myRedis=StrictRedis.from_url(myRedisUrl,decode_responses=True)
    if myRedis.get(myGuid)=='1':
        return 1
    myRedis.set(myGuid,'1')
    return 0



#sends the title, the link and description to my gmail and tries 5 times
def sendMail(mydict):
    global email, Epassword,emailTo
    attempts=0
    while attempts<5:
        try:
            server=smtplib.SMTP("smtp.gmail.com",587)
            server.starttls()
            server.login(email,Epassword)
            server.sendmail(emailTo,emailTo,('Hello there'+'\n'+'# Title: '+str(mydict['title'])+'\n'+'# Link: '+str(mydict['link'])+'\n'+'# Description: '+str(mydict['summary'])+'\n').encode('utf-8'))
            server.quit()
            break
        except Exception as err:
            attempts+=1
            myErr="couldn't send Email"
            myLog.logThis(myErr)
            print("couldn't send Email with",attempts,'Attempt(s):',err)




if os.geteuid() == 0:#root access is activated
# if getpass.getuser() != 0:
    print(getpass.getuser())
    firstTime=time.time()
    myLog=logDealer(firstTime)
    print("We're root!")
    
    #the following part makes a py_report directory if it doesn't exist
    try:
        # os.mkdir(adress+"py_report")
        if not os.path.exists(adress+"py_report"):
            os.makedirs(adress+"py_report")
    except:
        print("Couldn't make directory py_report! Run with admin permision.")
        exit()

    #the following part makes a py_log directory if it doesn't exist
    try:
        # os.mkdir(adress+"py_log")
        if not os.path.exists(adress+"py_log"):
            os.makedirs(adress+"py_log")
        #creats an empty log file:
        lof=open(myLog.logAdress,'w')
        lof.close()
    except:
        print("Couldn't make directory py_log! Run with admin permision.")
        exit()
    


    #the following part tries 5 times to get the  whole text from rss
    attempts=0
    done=0
    print("Enter one Email and the password of that email to receive news from this email (\"Sender\"): ")
    email = input("Email: ")
    Epassword = input("Password: ")
    emailTo = input ("Enter the Email you want to receive the news (\"Receiver\"): ")
    while attempts<5:
        try:
            response=requests.get("https://feeds.bbci.co.uk/news/rss.xml")
            # response=requests.get("https://feeds.bbci.co.uk/news/world/rss.xml")
            wholeText=response.text
            done=1
            break
        except:
            attempts+=1
            myErr="coudn't connect to website."
            myLog.logThis(myErr)
            print(attempts,'Attempt(s) for connecting to website.')
    if done==0:
        #end of program calls setSecond and calculates whole time
        secondTime=time.time()
        myLog.setSecondTime(secondTime)
        sys.exit()



    #making dict out of text 
    try:
        mydict=feedparser.parse(wholeText)
    except:
        myLog.logThis("Couldn't make dict")
        print("Couldn't make dict")



    #checking if guid is new then call writeFile func
    #then changes dict to json and sends Email
    for x in range(20):
        try:
            #takes guid
            myGuid=str(mydict['items'][x]['id'])
            #checks if guid is new
            if checkGuid(myGuid)==1:break
            #writes the json files
            if writeFile(mydict['items'][x])==0:raise 'Error'
            #send the mail about new title
            sendMail(mydict['items'][x])
        except Exception as err:
            myErr="Couldn't make all jsons!"
            myLog.logThis(myErr)
            print("Couldn't make all jsons!",err)

    #end of program calls setSecond and calculates whole time
    secondTime=time.time()
    myLog.setSecondTime(secondTime)
    

else:#root access isn't activated
    print("We're not root.")
    #the following line calls the program itself with root access activated
    subprocess.call(['sudo', 'python3'] + sys.argv) 
