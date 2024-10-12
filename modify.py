import json

mydict = []
with open('./sentences-bundle/sentences/c.json','r',encoding='utf8') as fp:
    json_data = json.load(fp)
    print(type(json_data))
    '''
    for words in json_data:
        #print(type(words))
        tmp = dict()
        tmp['hitokoto'] = words['hitokoto']
        tmp['type'] = words['type']
        tmp['from'] = words['from']
        tmp['from_who'] = words['from_who']
        mydict.append(tmp)
    '''
    while True:
        s = input('input words:')
        if s == '-1':
            break
        if s == '-2':
            with open('./out.json','w',encoding='utf8',newline='\n') as f:
                data = json.dumps(mydict,indent=1,ensure_ascii=False)
                f.write(data)
            continue
        if s == '-3':
            continue
        for words in json_data:
            if words['from'].find(s) != -1:
                tmp = dict()
                tmp['hitokoto'] = words['hitokoto']
                tmp['type'] = words['type']
                tmp['from'] = words['from']
                tmp['from_who'] = words['from_who']
                mydict.append(tmp)
                print(tmp)
        
with open('./c.json','w',encoding='utf8',newline='\n') as f:
    data = json.dumps(mydict,indent=1,ensure_ascii=False)
    f.write(data)
    