from flask import Flask, request, jsonify
import requests, json, random
loaded = False
data = None
def load():
    global loaded, data
    if not loaded:
        with open('/cat.json','r',encoding='utf-8') as fp:
            data = json.load(fp)
        loaded = True
    
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
    
@app.route('/',methods=['GET'])
def hitokoto():
    #return 'test'
    try:
        load()
        num = random.randint(0,len(data)-1)
        hitokoto = data[num]
        return jsonify(hitokoto)
    except Exception:
        return 'fuck'
        
@app.route('/test',methods=['GET'])
def test():
    return 'testtest'
    load()
    num = random.randint(0,len(data)-1)
    hitokoto = data[num]
    return jsonify(hitokoto)

if __name__ == '__main__':
    app.run(debug = True)