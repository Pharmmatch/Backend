from apscheduler.schedulers.background import BackgroundScheduler
import requests
from app.models import KorDrug
from app import app, db

# DB 업데이트 하고 싶을 때 app.py에 추가 (2시간 정도 걸림)
# all_drugs = fetch_kor_drugs()
# insert_data(all_drugs)

def fetch_kor_drugs():
    with app.app_context():  # Set up the application context
        url = 'http://apis.data.go.kr/1471000/DrbEasyDrugInfoService/getDrbEasyDrugList'
        serviceKey = '6SwYRQgE0MocZBUtMlYIdNGTBXFqBD+Ft4Sin0+ELHfDVUv/BMaQUmnxI1R3EASHzyYSeDeHyGIVE3muz2XeSg=='
        all_drugs = []

        for i in range(1, 50):
            params = {'serviceKey': serviceKey, 'pageNo': i, 'numOfRows': 100, 'type': 'json'}
            response = requests.get(url, params=params)
            data = response.json()

            if 'body' in data and 'items' in data['body'] and data['body']['items']:
                k = 0
                items = data['body']['items']
                for item in items:
                    k += 1
                    params2 = {'serviceKey': serviceKey, 'item_seq': item['itemSeq'], 'type': 'json'}
                    response2 = requests.get('http://apis.data.go.kr/1471000/DrugPrdtPrmsnInfoService05/getDrugPrdtPrmsnDtlInq04', params=params2)
                    response2.raise_for_status()
                    
                    try:
                        data2 = response2.json()
                        if 'items' in data2['body']:
                            item['atc_code'] = data2['body']['items'][0]['ATC_CODE']
                            item['ingr_string'] = data2['body']['items'][0]['MAIN_INGR_ENG']
                        all_drugs.append(item)
                        print(f'appended: {i}-{k}')
                    except requests.exceptions.RequestException as e:
                        print("error:", e)
            else:
                break
        print('all_drugs fetched')
        return all_drugs

def insert_data(all_drugs):
    with app.app_context():
        db.session.query(KorDrug).delete()
        print('db loading...')
        for item in all_drugs:
            drug = KorDrug(
                drug_name=item['itemName'][:255],
                ent_name=item['entpName'],
                efcy=item['efcyQesitm'],
                img_url=item['itemImage'],
                atc_code=item.get('atc_code',None),
                ingr_string=item.get('ingr_string', None),   
            )
            db.session.add(drug)
            print('added')
        print('complete!')

        db.session.commit()

# scheduler = BackgroundScheduler()
# scheduler.add_job(fetch_kor_drugs, 'interval', weeks=50)
# scheduler.start()