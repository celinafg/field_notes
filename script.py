from telethon import TelegramClient, events # pip install telethon
from datetime import datetime
from pymongo import MongoClient # pip install pymongo[srv]
from bson.objectid import ObjectId # pip install bson
import re
from dotenv import load_dotenv
import os

load_dotenv()

### Initializing Configuration
print("Initializing configuration...")


# Read values for Telethon and set session name
API_ID = os.getenv('api_id') 
API_HASH = os.getenv('api_hash')
BOT_TOKEN = os.getenv('bot_token')
session_name = "sessions/Bot"

NOTE = 'note'
MEDIA = 'media'
PROJECT = 'project'

# Read values for MySQLdb
USERNAME =os.getenv('username')
PASSWORD = os.getenv('password')
DATABASE_NAME = os.getenv('db_name')
COLLECTION_NAME = os.getenv('collection_name')

# Telethon
client = TelegramClient(session_name, API_ID, API_HASH).start(BOT_TOKEN)

# MongoDB
url = "mongodb+srv://"+USERNAME+":"+PASSWORD+"@clusterbot.zndrbka.mongodb.net/?retryWrites=true&w=majority"
cluster = MongoClient(url)

## helper functions
def clean_text(event, type):
    # do not include space before description text
    rep = {f"/{type} ":"", f"/{type}": "" }
    rep = dict((re.escape(k), v) for k, v in rep.items()) 
    pattern = re.compile("|".join(rep.keys()))
    words = pattern.sub(lambda m: rep[re.escape(m.group(0))], event.message.text)

    split_words = words.split(" #")
    tags=[i[1:] for i in event.message.text.split() if i.startswith("#") ]
    dt_string = datetime.now().strftime("%d-%m-%y") 

    post_dict = {"type": type, 
                 "text": split_words[0], 
                 "tags": tags if tags and len(tags)>= 1 else None, 
                 "LAST_UPDATE": dt_string}

    return post_dict

def get_notif(post):
    tags = post['tags']
    post_type = post['type']
   
    if post['text'] and tags:
        text = f"{post_type} entry logged with tags: {tags}"
    elif post['text'] and not tags:
        text=f"{post_type} entry logged"

    return text


### START COMMAND
@client.on(events.NewMessage(pattern="(?i)/start"))
async def start(event):
    sender = await event.get_sender()
    SENDER = sender.id
    text = "Hello! Log down any thought and I will publish it to your field notes website!"

    await client.send_message(SENDER, text)


# create /note
@client.on(events.NewMessage(pattern="(?i)/note"))
async def insert(event):
    sender = await event.get_sender()
    SENDER = sender.id

    post_dict = clean_text(event, NOTE)
    if not post_dict['text']:
        return
    
    notif = get_notif(post_dict)
    collection.insert_one(post_dict)

    await client.send_message(SENDER, notif, parse_mode='html')

@client.on(events.NewMessage(pattern="(?i)/media"))
async def insert(event):
    sender = await event.get_sender()
    SENDER = sender.id

    post_dict = clean_text(event, MEDIA)
    if not post_dict['text']:
        return
    
    notif = get_notif(post_dict)
    collection.insert_one(post_dict)

    await client.send_message(SENDER, notif, parse_mode='html')

@client.on(events.NewMessage(pattern="(?i)/project"))
async def insert(event):
    sender = await event.get_sender()
    SENDER = sender.id

    post_dict = clean_text(event, PROJECT)
    if not post_dict['text']:
        return
    
    notif = get_notif(post_dict)
    collection.insert_one(post_dict)

    await client.send_message(SENDER, notif, parse_mode='html')


##### MAIN
if __name__ == '__main__':
    try:
        print("Initializing Database...")
        # Define the Database using Database name
        db = cluster["ClusterBotTest"]
        # Define collection
        collection = db['field_notes']
        print("Bot Started...")
        client.run_until_disconnected()


    except Exception as error:
        print('Cause: {}'.format(error))