from flask import Flask, request, jsonify
import requests, json, random
loaded = False
data = None
def load():
    global loaded, data
    if not loaded:
        url = requests.get("https://hitokoto-navy.vercel.app/cat.json")
        url.encoding = 'utf-8'
        data = json.loads(url.text)
        '''
        with open('/cat.json','r',encoding='utf-8') as fp:
            data = json.load(fp)
        '''
        loaded = True
    
app = Flask(__name__)
# app.config['JSON_AS_ASCII'] = False
app.json.ensure_ascii = False
    
@app.route('/',methods=['GET'])
def hitokoto():
    global data
    try:
        load()
        args = request.args
        if 'id' in args and 0 <= args['id'] < len(data):
            num = args['id']
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