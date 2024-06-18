import re
from flask import request, jsonify
from app import app
from app.models import KorDrug
import requests
import urllib.parse

def get_rxcui(ingr):
    ingr = urllib.parse.quote(ingr)
    url = f'https://rxnav.nlm.nih.gov/REST/rxcui.json?name={ingr}&search=0'
    response = requests.get(url)
    data = response.json()

    if 'idGroup' in data and 'rxnormId' in data['idGroup']:
        rxnorm_id = data['idGroup']['rxnormId'][0]
        return rxnorm_id
    else:
        return ''

@app.route('/search_kordrug',methods=['GET'])
def search_kordrug():
    query = request.args.get('query','')
    drugs = KorDrug.query.filter(KorDrug.drug_name.contains(query)).all()
    results = []
    for drug in drugs:
        results.append({
            'id': drug.id,
            'drug_name': drug.drug_name,
            'ent_name': drug.ent_name,
            'efcy': drug.efcy,
            'img_url': drug.img_url,
            'atc_code': drug.atc_code,
            'ingr_string': drug.ingr_string,
            })
        
    return jsonify(results)

@app.route('/match_drug',methods=['GET'])
def match_drug():
    outdic = {}
    sortdic = {}
    sortlist = []
    inlist = []
    URL = 'http://rxnav.nlm.nih.gov/REST/brands.json?ingredientids='
    id = request.args.get('drugid','')
    drug = KorDrug.query.filter_by(id=id).first()

    inlist_string = drug.ingr_string.split('/')
    for string in inlist_string:
        x = get_rxcui(string)
        if x=='':
            continue
        else:
            inlist.append(x)

    print(inlist)
    for a in inlist:
        response = requests.get(URL + a)
        data = response.json()
        if 'conceptProperties' in data['brandGroup']:
            doc = data['brandGroup']['conceptProperties']
        else:
            continue
        
        for dic in doc:        
            if dic['rxcui'] in outdic:
                outdic[dic['rxcui']]['count'] += 1
            else:
                temp = {}
                temp['rxcui'] = dic['rxcui']
                temp['name'] = dic['name']
                temp['count'] = 1
                outdic[dic['rxcui']] = temp

    for b in outdic.values():
        if(sortdic.get(b['count'])):
            sortdic[b['count']].append(b)
        else:
            sortdic[b['count']] = [b]
    #이제 dictionary로 저장됨: {1: (count가 1인거 리스트), 2: (count가 2인거 리스트) ... }

    #이걸 리스트 형태로 정렬해줌 (유사도 낮은 것부터 높은 것 순서대로) +그리고 유사도도 계산해서 추가함
    for key, items in sortdic.items():
        for item in items:
            rxcui = item['rxcui']
            response2 = requests.get(f'https://dailymed.nlm.nih.gov/dailymed/services/v2/spls.json?rxcui={rxcui}')
            data2 = response2.json()

            try:
                title = data2['data'][0]['title']
                p = re.compile('\(([^)]+)')
                m = p.findall(title)
                l = len(str(m).split(', '))
                item['similarity'] = key/(l+len(inlist)-key)
                print(l, len(inlist), key)
                print(item)
                sortlist.append(item)
            except:
                continue

    sortlist = sorted(sortlist, key=lambda x: x['similarity'], reverse=True)
    print(sortlist)
    return jsonify(sortlist)