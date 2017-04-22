# -*- coding: utf-8 -*-
import json
import requests
import time
import random

# predispongo una minitastiera, con il solo tasto Info
keyboard_base = json.dumps({'keyboard': [["Info"]],
                            'one_time_keyboard': False,
                            'resize_keyboard': True})

# URL di base delle pagine di dettaglio dell'archivio NASA
URLdetail="https://images.nasa.gov/#/details-"

# imposto il testo che da le info sul bot
infoText="""🌜 I'm *hellomoon* bot: I use [NASA](https://images.nasa.gov/) serch engine to show you beatiful images of this archive.
*I'm only a demo bot* and sometimes I may not work.\n
To use me *write one* (or more) *word* below - in example `moon` - and send it to me. I'll give you *back* some related *photos*."""

# imposto URL principali per inviare messaggi (quello per i messaggi e quello per le foto)
URLT='https://api.telegram.org/bot' + Hook['env']['hellomoon_bot_key'] + '/sendMessage'
URLTF='https://api.telegram.org/bot' + Hook['env']['hellomoon_bot_key'] + '/sendPhoto'

# raccolgo nella variabile `testo` ciò che gli utenti scriveranno in chat al bot
testo=Hook['params']['message']['text']

# URL per interrogare le API della NASA, usando le keyword inserite dall'utente
URL="https://images-api.nasa.gov/search?media_type=image&q="+testo

# se l'utente chiede info con il tasto Info o se si iscrive con `/start` avrà inviato le info sul bot
if (testo=="Info" or testo=="/start"):
	richiesta=requests.get(URLT,verify=False,data={'chat_id':Hook['params']['message']['chat']['id'],
            'text':infoText,'parse_mode':'Markdown','reply_markup':keyboard_base})
# altrimenti il bot inizierà a elaborare ciò che l'utente ha scritto
else:
    # vengono interrogate le API della NASA con la stringa inviata dall'utente in chat e si raccoglie l'output JSON in una variabile
    r = requests.get(URL, verify=False)
    json_data=json.loads(r.text)

    # viene estratto il totale dei risultati della query
    totale=json_data['collection']['metadata']['total_hits']

    # creo una variabile per un messaggio di testo che da all'utente un mini report sui risultati della query
    reportText = "*" + str(totale) + " result/s* returned for *" + testo + "*.\nIn a few seconds I will show you some of the photos of the wonderful [NASA](https://images.nasa.gov/) catalog."

    # se non ci sono risultati viene avvisato l'utente
    if (totale==0):
        controllo=0
        richiesta=requests.get(URLT,verify=False,data={'chat_id':Hook['params']['message']['chat']['id'],
                'text':"No result, please try with another word",'parse_mode':'Markdown','reply_markup':keyboard_base})

    # altrimenti gli viene restituito un messaggio con il numero di risultati
    # creo la variabile `controllo`, in cui inserisco il numero massimo di foto da restituire. In questo caso, 4.
    # Se avrò meno di 4 risultati, sarà uguale al numero di risultati
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

    # Le API della NASA restituiscono al massimo 100 record di output, paginati di 100 in 100.
    # A partire dai primi 100 risultati voglio estrarre in modo random alcuni record, in modo di non avere sempre le prime n foto
    if (totale >= 100):
        totRandom=100
    else:
        totRandom=totale
    lista=random.sample(range(totRandom), controllo)

    # se non ho risultati non avviene nulla
    if (controllo==0):
        print("nulla")
    # altrimenti estraggo dal json, per ogni foto, thumbnail, ID, e descrizione, e invio indietro all'utente un'immagine con
    # una didascalia che contiene URL di dettaglio e descrizione
    else:
        for i, elem in enumerate(lista):
            inizio=int(elem)
            tthumb=json_data['collection']['items'][inizio]['links'][0]['href']
            tdescription=json_data['collection']['items'][inizio]['data'][0]['description']
            tnasaID=json_data['collection']['items'][inizio]['data'][0]['nasa_id']
            thref=URLdetail+tnasaID+'.html'
            catpion=thref + "\n" + tdescription
            data={'chat_id':Hook['params']['message']['chat']['id'],'caption':catpion[0:193]+" [...]",'photo':tthumb,'parse_mode':'Markdown','reply_markup':keyboard_base}
            richiesta=requests.get(URLTF,verify=False,data=data)
            time.sleep(1)
