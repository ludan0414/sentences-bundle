from flask import Flask, request, jsonify
import requests, json, random
from flask_cors import CORS
loaded = False
data = dict()
def load():
    global loaded, data
    if not loaded:
        url = requests.get("https://hitokoto.ludan.fun/cat.json")
        url.encoding = 'utf-8'
        data = json.loads(url.text)
        loaded = True
    
app = Flask(__name__)
CORS(app, resources=r'/*')
# app.config['JSON_AS_ASCII'] = False
app.json.ensure_ascii = False
    
@app.route('/',methods=['GET','POST'])
def hitokoto():
    global data,loaded
    try:
        load()
        args = request.args
        if 'from' in args:
            speaker = args['from']
            if speaker == 'whale':
                speaker = '🐋'
            if speaker == 'genshin':
                speaker = '原神'
            retlist = []
            for i in range(len(data)):
                hitokoto = data[i]
                if speaker in hitokoto['from'] or ((hitokoto['from_who'] is not None) and speaker in hitokoto['from_who']):
                    retlist.append(hitokoto)
            if len(retlist) > 0:
                num = random.randint(0,len(retlist)-1)
                return jsonify(retlist[num])
        
        if 'id' in args and 0 <= int(args['id']) < len(data):
            num = int(args['id'])
        else:
            num = random.randint(0,len(data)-1)
        
        hitokoto = data[num]
        return jsonify(hitokoto)
    except Exception as err:
        return err.__str__()
        
@app.route('/test',methods=['GET'])
def test():
    return 'testtest'
    load()
    num = random.randint(0,len(data)-1)
    hitokoto = data[num]
    return jsonify(hitokoto)

if __name__ == '__main__':
    app.run()