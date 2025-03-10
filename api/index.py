from flask import Flask, request, jsonify
import requests, json, random
from flask_cors import CORS
loaded = False
data = dict()
query = []
cname = 'https://hitokoto.ludan.space'
def load():
    global loaded, data
    if not loaded:
        try:
            with open('./cat.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            loaded = True
        except:
            url = requests.get(cname+"/cat.json", verify=False)
            url.encoding = 'utf-8'
            data = json.loads(url.text)
            loaded = True
def loadori():
    global data
    retlist = []
    for hitokoto in data:
        if hitokoto['type'] == 'a' or hitokoto['type'] == 'c':
            retlist.append(hitokoto)
    return jsonify(random.choice(retlist))
def search(cont:str):
    global data
    retlist = []
    for hitokoto in data:
        if cont in hitokoto['hitokoto'] \
            or cont in hitokoto['from'] \
            or (hitokoto['from_who'] is not None and cont in hitokoto['from_who']):
            retlist.append(hitokoto)
    if len(retlist) == 0:
        return jsonify({
            "hitokoto": "not found",
            "type": None,
            "from": None,
            "from_who": None
        })
    return jsonify(random.choice(retlist))

app = Flask(__name__)
CORS(app, resources=r'/*')
# app.config['JSON_AS_ASCII'] = False
app.json.ensure_ascii = False
    
@app.route('/',methods=['GET'])
def hitokoto():
    global data
    try:
        load()
        args = request.args
        if 'from' in args:
            speaker = args['from']
            if speaker == 'whale':
                speaker = '🐋'
            if speaker == 'genshin':
                speaker = '原神'
            if speaker == 'original':
                return loadori()
            retlist = []
            for i in range(len(data)):
                hitokoto = data[i]
                if speaker in hitokoto['from'] or ((hitokoto['from_who'] is not None) and speaker in hitokoto['from_who']):
                    retlist.append(hitokoto)
            if len(retlist) > 0:
                num = random.randint(0,len(retlist)-1)
                return jsonify(retlist[num])
        
        if 'search' in args:
            return search(args['search'])
        
        if 'id' in args and 0 <= int(args['id']) < len(data):
            num = int(args['id'])
        else:
            num = random.randint(0,len(data)-1)
        
        return jsonify(data[num])
    except Exception as err:
        return err.__str__()
        

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=9000)
