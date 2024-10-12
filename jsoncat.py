import json

mylist = []
while True:
    s = input('输入文件名：')
    if s == '-1':
        break
    with open(s,'r',encoding='utf8') as fp:
        json_data = json.load(fp)
        for word in json_data:
            mylist.append(word)

with open('./cat.json','w',encoding='utf8',newline='\n') as f:
    data = json.dumps(mylist,indent=1,ensure_ascii=False)
    f.write(data)

print(len(mylist))