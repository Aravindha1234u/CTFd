import os
import discord
from dotenv import load_dotenv
import time
import datetime
import requests
import json
import threading
import sys
import asyncio
import sqlite3

start_time = time.time()

secret="kHLKALybV7qJmlYCsvAr5URdFl1jh4F2"
clientid="704010814356455508"
token="NzA0MDEwODE0MzU2NDU1NTA4.XuHiCA.yUovbiDadWc6sh44_I50F-aD7lk"
scope="https://discord.com/api/oauth2/authorize?client_id=704010814356455508&permissions=0&scope=bot"

url = None
pages=1
session_cookie = None
channel_id = None
prevsolve=""
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

def scoreboard():
  global url,session_cookie
  headers = {
      'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Language': 'en-US,en;q=0.5',
      'Connection': 'keep-alive',
      'Upgrade-Insecure-Requests': '1',
  }
  cookies =  {
    'session': str(session_cookie)
  }
  response = requests.get(url+"/api/v1/scoreboard", headers=headers, cookies=cookies)
  data = response.json()['data']
  message="```"
  message+="\n"
  for i in data[:20]:
    message+="#"+str(i['pos'])+" : "+str(i['name'])+" ==> "+str(i['score'])+" points"+"\n"
  message+="```"
  return message

def descchall(challname):
  global url,session_cookie
  headers = {
      'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Language': 'en-US,en;q=0.5',
      'Connection': 'keep-alive',
      'Upgrade-Insecure-Requests': '1',
  }
  cookies =  {
    'session': str(session_cookie)
  }
  response = requests.get(url+"/api/v1/challenges", headers=headers, cookies=cookies)
  data = response.json()['data']
  category = []
  for i in data :
    category.append(i['category'])
    if i['name'].lower() == challname.lower():
      return {"name":i['name'],'points':i['value'],'type':i['type'],'category':i['category']}
  
  if challname in category:
    challs=[]
    for i in data :
      if i['category'].lower() == challname.lower():
        challs.append(i['name'])
    return challs

  return {"Error":"Challenge or Category Name Not found"}

def challenge():
  global url,session_cookie
  headers = {
      'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Language': 'en-US,en;q=0.5',
      'Connection': 'keep-alive',
      'Upgrade-Insecure-Requests': '1',
  }
  cookies =  {
    'session': str(session_cookie)
  }
  response = requests.get(url+"/api/v1/challenges", headers=headers, cookies=cookies)
  data = response.json()['data']
  chall={i['id']:i['name'] for i in data}
  return chall

def submission():
  global session_cookie,url,pages
  headers = {
      'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Language': 'en-US,en;q=0.5',
      'Connection': 'keep-alive',
      'Upgrade-Insecure-Requests': '1',
  }
  cookies =  {
    'session': str(session_cookie)
  }
  response = requests.get(url+'/api/v1/submissions?page={}'.format(pages), headers=headers, cookies=cookies)
  data = response.json()['data']
  data = data[len(data)-1]
  pages=response.json()['meta']['pagination']['pages']
  if data['type'] !="incorrect":
    response = requests.get(url+'/api/v1/users', headers=headers, cookies=cookies)
    users = {i["id"]:i["name"] for i in response.json()['data']}
    return [users[data["user_id"]],data['challenge_id'],data['date']]
  else:
    return []

def position(user):
  global session_cookie,url
  headers = {
      'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Language': 'en-US,en;q=0.5',
      'Connection': 'keep-alive',
      'Upgrade-Insecure-Requests': '1',
  }
  cookies =  {
    'session': str(session_cookie)
  }
  response = requests.get(url+"/api/v1/scoreboard", headers=headers, cookies=cookies)
  data = response.json()['data']
  for i in data:
    for j in i['members']:
      if j['name']==user:
        return i['pos'],i['score']
  
  return {"Error":"User not Found"}

@client.event
async def on_ready():
  global channel_id,prevsolve
  await client.change_presence(activity=discord.Game(name="Type /help for help"))
  await client.wait_until_ready()

  print('{} is connected\n'.format(client.user))
  await client.get_channel(channel_id).send("""```bash
"Hey forks!, This is **Secarmy CTFd Bot** who joined your channel. Bot will keep you updated on live scoreboard and Live valid submission and their respective rank with score of the player who solved the challenge recently. For More info and help Type /help Do Support us at secarmy.org"
```""")
  
  while 1:
    score=scoreboard()
    chall = challenge()
    try:
      check = submission()
      temp = " ".join(str(v) for v in check)
      if check!= None and temp!=prevsolve:
        prevsolve=temp
        pos,score=position(check[0])
        check = "**"+check[0]+"**"+" Has Solved Challenge "+"**"+chall[int(check[1])]+"**" +" (Current Rank: "+str(pos)+", Total score: "+str(score)+")" +" Solved at " + datetime.datetime.strptime(check[2],"%Y-%m-%dT%H:%M:%S.%f%z").strftime("%b %d %Y %H:%M:%S") #+ time.strftime("%H:%M:%S", time.localtime())
        channel = client.get_channel(channel_id)
        em1 = discord.Embed(title="Kudos",description=check,colour=0x27b24e)
        await channel.send(embed=em1)
      
      hours, rem = divmod(time.time()-start_time, 3600)
      minutes, seconds = divmod(rem, 60)

      if hours%12 == 0 and minutes%1 == 0 and int(seconds)==0 and (seconds-int(seconds))<=1:
        channel = client.get_channel(channel_id)
        em2 = discord.Embed(title="ScoreBoard",description=score,colour=0x040404)
        await channel.send(embed=em2)
    except Exception as e:
      #print(e)
      pass
    await asyncio.sleep(0.5)
  client.logout()
  client.close()

@client.event
async def on_message(message):
  channel = message.channel

  if "Secarmy CTF Bot#5160" != str(message.author):
    if message.content.startswith('/'):
      cmd=message.content.replace("/","").split(" ",1)
      if cmd[0].lower() == "help":
        embed=discord.Embed(
          title="Help",
          description="CTFd bot is capable of monitor **real-time solves and submission** and filter out valid once, sends notifications on each solves with beautiful and __colorful embeds__ with current rank and score of the person who solved with a __timestamp__ in it. We have a live scoreboard that notifies the people on a repeated schedule of 1 minute with ranks of the __**top 20 players**__. It has custom commands to get information or detail from CTFd framework and notify with handly flost messages",
          colour=0x27b24e
          )
        embed.set_author(name="Secarmy CTFd Bot", url="https://secarmy-ctfd-bot.herokuapp.com")
        embed.set_thumbnail(url="https://ctf.secarmy.org/images/logo.png")
        embed.add_field(name="/mystat", value="Will display the score and position", inline=False)
        embed.add_field(name="/challenge list", value="List out all active challenges ", inline=False)
        embed.add_field(name="/challenge challenge_name", value="Challenge Complete Info ", inline=False)
        embed.add_field(name="/challenge category", value="Challenge all under category ", inline=False)
        embed.add_field(name="/scoreboard", value="Scoreboard with Top 20 Users ", inline=False)
        await channel.send(embed=embed)

      elif cmd[0].lower() == "mystat":
        data = position(message.author)
        if type(data) == type({}):
          conn = sqlite3.connect("./CTFd/ctfd.db")
          c = conn.cursor()
          c.execute("SELECT name FROM users WHERE oauth_id='{}';".format(message.author.id))
          data = position(c.fetchall()[0][0])
          mention = "<@{}>".format(message.author.id)
        else:
          mention = "@{}".format(message.author)
        
        if type(data) != type({}):
          pos,score=data
          msg="""```ini
  -{} Current Rank: {} and Total score: {}
  ```""".format(mention,str(pos),str(score))
          await channel.send(msg)
        else:
          await channel.send(data['Error'])

      elif cmd[0].lower() == "challenge":
        challenges=challenge()
        chall = [name for id,name in challenges.items()]
        msg="List of Active challenge"+"\n"
        if cmd[1] == "list":
          for i in range(len(chall)):
            msg+="> "+str(i+1)+". "+chall[i] +"\n"
          await channel.send(msg)
        else:
          chall = descchall(cmd[1])
          if type(chall) == type(list()):
            msg="List of "+cmd[1]+" Challenges \n"
            for i in range(len(chall)):
              msg+="> "+str(i+1)+". "+chall[i] +"\n"
            await channel.send(msg)

          elif "Error" not in chall.keys():
            embed=discord.Embed(title="Challenge Description")
            embed.add_field(name="Name", value=chall['name'], inline=True)
            embed.add_field(name="Category", value=chall['category'], inline=True)
            embed.add_field(name="Points", value=chall['points'], inline=True)
            embed.add_field(name="Type", value=chall['type'], inline=True)
            await channel.send(embed=embed)
          else:
            await channel.send(chall['Error'])
      
      elif cmd[0].lower() == "scoreboard":
        score = scoreboard()
        em2 = discord.Embed(title="ScoreBoard",description=score,colour=0x040404)
        await channel.send(embed=em2)

channel_id = int(sys.argv[3].strip())
url = sys.argv[2].strip()
session_cookie = sys.argv[1].strip()
client.run(TOKEN)