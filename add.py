import json

mydict = []
with open('add.txt','r',encoding='utf8') as fp:
    while True:
        s = fp.readline()
        if s == '-1':
            break
        if s == '-2':
            mydict.pop()
            continue
        o = fp.readline()
        fp.readline()
        tmp = dict()
        tmp['hitokoto'] = s.replace("\n","")
        tmp['type'] = 'm'
        tmp['from'] = o.replace("\n","")
        tmp['from_who'] = None
        mydict.append(tmp)
    
with open('./add.json','w',encoding='utf8',newline='\n') as f:
    data = json.dumps(mydict,indent=1,ensure_ascii=False)
    f.write(data)