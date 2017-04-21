# -*- coding: utf-8 -*-
import json
import requests
import time
import random
  
# imposto la tastiera per gli iscritti
keyboard_base = json.dumps({'keyboard': [["Info"]], 
                            'one_time_keyboard': False, 
                            'resize_keyboard': True})

infoText="""🌜 I'm *hellomoon* bot: I use [NASA](https://images.nasa.gov/) serch engine to show you beatiful images of this archive. 
*I'm only a demo bot* and sometimes I may not work.\n
To use me *write one* (or more) *word* below - in example `moon` - and send it to me. I'll give you *back* some related *photos*."""

# imposto URL principali per inviare messaggi
URLT='https://api.telegram.org/bot' + Hook['env']['hellomoon_bot_key'] + '/sendMessage'
URLTF='https://api.telegram.org/bot' + Hook['env']['hellomoon_bot_key'] + '/sendPhoto'
  

testo=Hook['params']['message']['text']
URL="https://images-api.nasa.gov/search?media_type=image&q="+testo

if (testo=="Info" or testo=="/start"):
	richiesta=requests.get(URLT,verify=False,data={'chat_id':Hook['params']['message']['chat']['id'],
            'text':infoText,'parse_mode':'Markdown','reply_markup':keyboard_base})
else:
    r = requests.get(URL, verify=False)
    json_data=json.loads(r.text)

    totale=json_data['collection']['metadata']['total_hits']
    reportText = "*" + str(totale) + " result/s* returned for *" + testo + "*.\nIn a few seconds I will show you some of the photos of the wonderful [NASA](https://images.nasa.gov/) catalog."
    if (totale==0):
        controllo=0
        richiesta=requests.get(URLT,verify=False,data={'chat_id':Hook['params']['message']['chat']['id'],
                'text':"No result, please try with another word",'parse_mode':'Markdown','reply_markup':keyboard_base})
    elif (1 <= totale <= 4):
        controllo=totale
        richiesta=requests.get(URLT,verify=False,data={'chat_id':Hook['params']['message']['chat']['id'],
                'text':reportText,'parse_mode':'Markdown','reply_markup':keyboard_base})
        time.sleep(1)
    else:
        controllo=4
        richiesta=requests.get(URLT,verify=False,data={'chat_id':Hook['params']['message']['chat']['id'],
                "text":reportText,'parse_mode':'Markdown','reply_markup':keyboard_base})
        time.sleep(1)

    URLdetail="https://images.nasa.gov/#/details-"

    if (totale >= 100):
        totRandom=100
    else:
        totRandom=totale
    lista=random.sample(range(totRandom), controllo)


    if (controllo==0):
        print("nulla")
    else:
        for i, elem in enumerate(lista):
            inizio=int(elem)
            tthumb=json_data['collection']['items'][inizio]['links'][0]['href']
            tdescription=json_data['collection']['items'][inizio]['data'][0]['description']
            tnasaID=json_data['collection']['items'][inizio]['data'][0]['nasa_id']
            thref=URLdetail+json_data['collection']['items'][inizio]['data'][0]['nasa_id']+'.html'
            catpion=thref + "\n" + tdescription
            richiesta=requests.get(URLTF,verify=False,data={'chat_id':Hook['params']['message']['chat']['id'],'caption':catpion[0:193]+" [...]",'photo':tthumb,'parse_mode':'Markdown','reply_markup':keyboard_base})
            time.sleep(1)
        
