# Come realizzare un bot telegram

## Intro

**Sono l'ultimo dei primi**, ci sono già tanti *tutorial* con lo stesso titolo, però voglio condividere la mia piccola esperienza, perché mi sembra una modalità comoda e didattica.
Mostrerò come creare un bot Telegram basato su un `microservice`.

Un bot - in questo caso un **chat bot** - è un utente con cui chattare, un po' diverso dai soliti perché fatto di codice. Un po' come se dialogassimo con un robot.

**[Telegram](https://telegram.org/)** è una bella piattaforma di *istant messaging* che la possibilità di creare dei *chat bot* e di interagire con questi.

Per definire un microservizio userò le parole di [Martin Fowler](https://hyp.is/-RlwHihIEeesx780tEKQLw/martinfowler.com/articles/microservices.html):
> Lo stile architetturale a microservizi è un approccio allo sviluppo di una singola applicazione come insieme di piccoli servizi, ciascuno dei quali viene eseguito da un proprio processo e comunica con un meccanismo snello, spesso una HTTP API.

## Bot "pappagallo" in Python

Il bot "pappagallo" fa una cosa sola: risponde ai messaggi che riceve, con le stesse parole che ha ricevuto.

È una cosa che sembra inutile, in realtà è un fondamentale punto di partenza. Perché il *core* di un *chat bot* è fare in modo che riceva dei messaggi e ci faccia qualcosa.

La prima cosa da fare è installare Telegram e usare proprio un bot ([@botfather](https://t.me/botfather)), avviarlo e creare un nuovo bot.

![](./imgs/Screenshot_20170423-111301.png)

Non entro nei dettagli, è semplice e trovate molti articoli sul tema.
Creato il bot, annotate da qualche parte i relativi **nome** e **token**.

Il prossimo passo è quello di creare il microservizio. Useremo una gran bella piattaforma: [hook.io](https://hook.io/).

Questi gli step:

- registratevi;
- create un [nuovo microservizio](https://hook.io/new) e dategli un nome. Ogni microservizio è qui chiamato `Hook`;
- scegliete python come linguaggio;

![](./imgs/2017-04-23_19h41_16.png)

- inserite il codice sottostante e salvate il microservizio.

```python
import requests

# raccolgo nella variabile `testo` ciò che gli utenti scriveranno in chat al bot
testo=Hook['params']['message']['text']

# raccolgo la chat ID
chatID=Hook['params']['message']['chat']['id']

# imposto l'URL per inviare i messaggi indietro al bot
URL='https://api.telegram.org/bot' + Hook['env']['hellomoonparrot_bot_key'] + '/sendMessage'

richiesta=requests.get(URL,verify=False,data={'chat_id':chatID,'text':testo})
```

Il passo successivo è quello di dire al bot di usare il microservizio appena creato. Per farlo chiamate (anche via browser) questo URL inserendo i vostri dati:

    https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://hook.io/<hook-user>/<hook-name>

- `<TOKEN>` è il token del vostro bot;
- `<hook-user>` è il nome utente creato su hook.io;
- `<hook-name>` è il nome del microservizio che avete creato.

Una volta lanciato l'URL, se tutto va bene, avrete in risposta qualcosa come:

    {"ok":true,"result":true,"description":"Webhook was set"}

Questo è un punto chiave: impostando un *Webhook* stiamo dicendo al bot che abbiamo creato di reindirizzare tutto ciò che viene inviato in chat, verso il microservizio che abbiamo creato.

Nel codice del microservizio queste le parti chiave:

- viene importato il modulo python, che consentirà di fare "parlare" il chat bot con gli utenti, facendo delle chiamate in HTTP;
- tutti i parametri HTTP in ingresso - in questo caso i messaggi di chat - vengono raccolti nell'oggetto `Hook.params`, che in python è in `Hook['params']` (il linguaggio consigliato di hook.io è javascript);
- raccogliamo in una variabile il testo che il microservizio riceve;
- in un'altra l'ID della chat in corso. Ogni utente avrà con il bot la sua chatID;
- inviamo indietro alla chatID da cui abbiamo ricevuto il messaggio, la copia dello stesso, tramite il modulo `requests` di python.

Non vi resta che aprire il bot che avete creato e chattare con lui. Io ne ho creato uno di test e potete provarlo qui: [@hellomoonParrot_bot](https://t.me/hellomoonParrot_bot).

![](./imgs/photo_2017-04-23_20-06-09.jpg).

Tutto questo non è straordinario??

## "hellomoon" bot, un bot basato sulle API della NASA

Alcuni giorni fa la **NASA** ha reso pubblico un bel motore di ricerca che consente di cercare nel suo fantastico archivio multimediale: https://images.nasa.gov

L'aspetto molto interessante è che è possibile usarlo anche tramite [**API**](https://images.nasa.gov/docs/images.nasa.gov_api_docs.pdf) e quindi si presta molto bene a creare un bot che data una (o più) parola chiave, mi mostra le immagini correlate trovate in questo catalogo.

Se voglio ad esempio cercare soltanto tra le immagini la stringa "palermo", interrogherò le API con [questo URL](https://images-api.nasa.gov/search?media_type=image&q=palermo):

    https://images-api.nasa.gov/search?media_type=image&q=palermo

La NASA risponde in `JSON`:

![](./imgs/2017-04-23_20h25_04.png)

Per creare questo bot non è necessario fare molto di più di quanto fatto per il "pappagallo":

- studiare un po' le API della NASA, fare qualche query di test e leggerne gli output;
- creare un bot Telegram;
- creare un microservizio in python a cui aggiungere
 - un modulo per leggere dati in formato JSON;
 - il metedo delle API di Telegram per [inviare foto](https://core.telegram.org/bots/api#sendphoto).

Il codice è solo un po' più complesso ed è quello sottostante. Oltre al modulo `json` ho aggiunto altri due moduli: `random` per generare dei numeri casuali, in modo da non ricevere per le stessa query sempre le stesse foto, e il modulo `time` per impostare un intervallo minimo tra una chiamata e un'altra alle API di Telegram.

Lo script fa questo:

- raccoglie in chat la parola (o le parole) inviate dall'utente;
- lancia la query sulle API della NASA e conteggia i risultati;
- se pari a zero lo script si ferma;
- se sono >= 1 ne seleziona non più di 4 in modo random;
- estrae per ogni immagine URL del file a bassa risoluzione, descrizione e ID;
- invia alla chat ID da cui è arrivata la parola da cercare, la foto, con una didascalia che contiene l'URL alla scheda dell'immagine e la sua descrizione.

```python
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
            caption=thref + "\n" + tdescription
            if (len(caption) >= 193):
                captionOk = caption[0:193] + " [...]"
            else:
                captionOk = caption
            data={'chat_id':Hook['params']['message']['chat']['id'],'caption':captionOk,'photo':tthumb,'parse_mode':'Markdown','reply_markup':keyboard_base}
            richiesta=requests.get(URLTF,verify=False,data=data)
            time.sleep(1)

```

Il bot è questo - [@hellomoonbot](https://t.me/hellomoonbot) - e qui sotto le vedete in azione.

![](./imgs/hellomoon.gif)


## Considerazioni finali

Non avrei mai scritto questo post, senza prima aver letto [questo bel post](https://unnikked.ga/how-to-easily-build-a-telegram-bot-with-hook-io-4c144c4abd96) di Nicola Malizia, che ringrazio molto.

Diffidate sempre un po' dalle guide che mostrano come realizzare qualcosa con poco sforzo, poca conoscenza di dominio e senza spese. Quindi fatelo anche con questo tutorial.
Ho usato ad esempio la versione free di **hook.io** che è limitata a 1000 richieste mensili: sono poche per realizzare qualcosa che (si spera) verrà usato da molti utenti. La soluzione è pagare o realizzare un bot in totale autonomia (quindi ci vuole una competenza più "larga").

La gran parte dei bot Telegram sono poco utili. Spesso infatti (come in questo caso), si tratta di poco più di motori di query che restituiscono un risultato all'utente, per i quali sarebbe preferibile un minisito basato su php, python, ecc. e con una interfaccia che si adatti al terminale usato.
Se può bastare un browser, è meglio non aggiungere una dipendenza da un'altra app.

Ciò che utile e "intelligente" dipende in ogni caso anche da noi.
Un po' perché è questione di gusti. Io ho un amico che impazziva per il bot dedicato a Jovanotti, che rimpiazzava tutte le 's' (e anche le 'z') con 'f' in tutte le risposte che dava.
Un po' perché oggi esistono eccellenti librerie e API di analisi (di testi, immagini, audio, video, ecc.), di machine learning, di  Natural language processing, di intelligenza artificiale che consentono di aggiungere molta intelligenza a una buona idea di bot e a una preparazione adeguata per usarle.

Questo tutorial è scritto per mettere soltanto un piede dentro questo spazio, tutto il resto sta a ognuno di noi.

### Letture consigliate

- [How to easily build a Telegram Bot with Hook.io](How to easily build a Telegram Bot with Hook.io);
- [Building a Chatbot using Telegram and Python](https://www.codementor.io/garethdwyer/building-a-telegram-bot-using-python-part-1-goi5fncay);
- [Bots: What you need to know](https://www.oreilly.com/ideas/bots-what-you-need-to-know);
- [Make a Twitter Bot in Python: Iterative Code Examples](https://jitp.commons.gc.cuny.edu/make-a-twitter-bot-in-python-iterative-code-examples/);
- [Microservices a definition of this new architectural term](https://martinfowler.com/articles/microservices.html).
