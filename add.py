import json

mydict = []
with open('add.txt','r',encoding='utf8') as fp:
    while True:
        s = fp.readline().replace("\n","")
        while s == '':
            s = fp.readline().replace("\n","")
        if s == '-1':
            break
        if s == '-2':
            mydict.pop()
            continue
        o = fp.readline().replace("\n","")
        t = fp.readline().replace("\n","")
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
        #print(tmp)
    
with open('./add.json','w',encoding='utf8',newline='\n') as f:
    data = json.dumps(mydict,indent=1,ensure_ascii=False)
    f.write(data)