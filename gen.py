import json

mydict = []

def load(filename:str):
    global mydict
    s = filename
    if s == '-1':
        return
    with open(s,'r',encoding='utf8') as fp:
        json_data = json.load(fp)
        for word in json_data:
            mydict.append(word)

if __name__ == '__main__':
    load('a.json')
    load('c.json')
    with open('add.txt','r',encoding='utf8') as fp:
        while True:
            s = fp.readline().replace("\n","")
            while s == '':
                s = fp.readline().replace("\n","")
            if s == '-1':
                break
            o = fp.readline().replace("\n","")
            t = fp.readline().replace("\n","")
            if t == '-1':
                break
            if t != '':
                fp.readline().replace("\n","")
            tmp = dict()
            tmp['hitokoto'] = s
            tmp['type'] = 'm'
            tmp['from'] = o
            if t != '':
                tmp['from_who'] = t
            else:    
                tmp['from_who'] = None
            mydict.append(tmp)
        
    with open('./cat.json','w',encoding='utf8',newline='\n') as f:
        data = json.dumps(mydict,indent=1,ensure_ascii=False)
        f.write(data)