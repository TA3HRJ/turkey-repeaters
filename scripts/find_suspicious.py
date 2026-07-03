# -*- coding: utf-8 -*-
import json, math, sys

sys.stdout.reconfigure(encoding='utf-8')

with open('docs/data/repeaters.json','r',encoding='utf-8') as f:
    d=json.load(f)
reps=d['repeaters']

CITY_CENTER = {
    'Adana':(37.00,35.32),'Adıyaman':(37.76,38.28),'Afyonkarahisar':(38.75,30.54),
    'Ağrı':(39.72,43.05),'Aksaray':(38.37,34.03),'Amasya':(40.65,35.83),
    'Ankara':(39.93,32.85),'Antalya':(36.90,30.69),'Ardahan':(41.11,42.70),
    'Artvin':(41.18,41.82),'Aydın':(37.84,27.84),'Balıkesir':(39.65,27.88),
    'Bartın':(41.63,32.34),'Batman':(37.89,41.13),'Bayburt':(40.26,40.23),
    'Bilecik':(40.14,29.98),'Bingöl':(38.89,40.49),'Bitlis':(38.40,42.11),
    'Bolu':(40.74,31.61),'Burdur':(37.72,30.29),'Bursa':(40.19,29.06),
    'Çanakkale':(40.15,26.41),'Çankırı':(40.60,33.61),'Çorum':(40.55,34.96),
    'Denizli':(37.77,29.09),'Diyarbakır':(37.92,40.23),'Düzce':(40.84,31.16),
    'Edirne':(41.68,26.56),'Elazığ':(38.68,39.22),'Erzincan':(39.75,39.50),
    'Erzurum':(39.91,41.27),'Eskişehir':(39.78,30.52),'Gaziantep':(37.07,37.38),
    'Giresun':(40.91,38.39),'Gümüşhane':(40.46,39.48),'Hakkari':(37.58,43.74),
    'Hatay':(36.20,36.16),'Iğdır':(39.92,44.04),'Isparta':(37.76,30.55),
    'İstanbul':(41.01,28.96),'İzmir':(38.42,27.14),'Kahramanmaraş':(37.59,36.94),
    'Karabük':(41.20,32.63),'Karaman':(37.18,33.22),'Kars':(40.60,43.10),
    'Kastamonu':(41.38,33.78),'Kayseri':(38.73,35.49),'Kilis':(36.72,37.12),
    'Kırıkkale':(39.85,33.51),'Kırklareli':(41.74,27.22),'Kırşehir':(39.14,34.17),
    'Kocaeli':(40.77,29.94),'Konya':(37.87,32.49),'Kütahya':(39.42,29.98),
    'Malatya':(38.35,38.31),'Manisa':(38.62,27.43),'Mardin':(37.31,40.74),
    'Mersin':(36.80,34.63),'Muğla':(37.22,28.36),'Muş':(38.74,41.49),
    'Nevşehir':(38.62,34.72),'Niğde':(37.97,34.68),'Ordu':(40.98,37.88),
    'Osmaniye':(37.07,36.25),'Rize':(41.02,40.52),'Sakarya':(40.69,30.43),
    'Samsun':(41.29,36.33),'Şanlıurfa':(37.16,38.79),'Siirt':(37.93,41.95),
    'Sinop':(42.03,35.15),'Sivas':(39.75,37.01),'Şırnak':(37.52,42.46),
    'Tekirdağ':(40.98,27.51),'Tokat':(40.31,36.55),'Trabzon':(41.00,39.73),
    'Tunceli':(39.11,39.55),'Uşak':(38.68,29.41),'Van':(38.49,43.38),
    'Yalova':(40.65,29.27),'Yozgat':(39.82,34.81),'Zonguldak':(41.45,31.80),
    'Muğla':(37.22,28.36),'Muş':(38.74,41.49),
}

def norm(s):
    return (s or '').strip().lower()\
        .replace('ş','s').replace('ç','c').replace('ğ','g')\
        .replace('ı','i').replace('ü','u').replace('ö','o')\
        .replace('İ','i').replace('Ş','s').replace('Ç','c')\
        .replace('Ğ','g').replace('Ü','u').replace('Ö','o')

CITY_NORM = {norm(k): v for k, v in CITY_CENTER.items()}

def dist(la1,lo1,la2,lo2):
    R=6371
    dla=math.radians(la2-la1); dlo=math.radians(lo2-lo1)
    a=math.sin(dla/2)**2+math.cos(math.radians(la1))*math.cos(math.radians(la2))*math.sin(dlo/2)**2
    return R*2*math.asin(math.sqrt(a))

# --- 1. Koordinat şehirden çok uzak ---
print("="*80)
print("1. KOORDINAT SEHIR MERKEZINDEN 100 KM+ UZAK (coord_approx=false)")
print("="*80)
far=[]
for r in reps:
    if r.get('coord_approx'): continue
    city=norm(r.get('city',''))
    if city not in CITY_NORM: continue
    clat,clon=CITY_NORM[city]
    rlat,rlon=r.get('lat',0),r.get('lon',0)
    if not rlat: continue
    d=dist(clat,clon,rlat,rlon)
    if d>100:
        far.append((d,r['id'],r.get('city',''),r.get('location',''),rlat,rlon))
far.sort(reverse=True)
for d,rid,city,loc,lat,lon in far:
    print(f"  {rid:8s}  {city:20s}  {loc:28s}  {lat:.4f},{lon:.4f}  [{d:.0f}km]")

# --- 2. Çakışan koordinatlar (farklı şehirler ama aynı nokta) ---
print()
print("="*80)
print("2. FARKLI SEHIRLERDE AYNI KOORDINAT (coord_approx=false)")
print("="*80)
from collections import defaultdict
coord_map=defaultdict(list)
for r in reps:
    if r.get('coord_approx'): continue
    if r.get('lat') and r.get('lon'):
        key=(round(r['lat'],3), round(r['lon'],3))
        coord_map[key].append(r)
for key,rs in coord_map.items():
    cities=set(r.get('city','') for r in rs)
    if len(cities)>1:
        print(f"  Koordinat {key[0]},{key[1]}:")
        for r in rs:
            print(f"    {r['id']:8s}  {r.get('city',''):20s}  {r.get('location','')}")

# --- 3. Off-air kayıtlar ---
print()
print("="*80)
print("3. STATUS=FALSE (OFF-AIR) KAYITLAR")
print("="*80)
offair=[r for r in reps if not r.get('status',True)]
print(f"  Toplam: {len(offair)}")
for r in offair:
    print(f"  {r['id']:8s}  {r.get('city',''):20s}  {r.get('frequency',0):.4f} {r.get('band',''):4s}  {r.get('callsign','') or '-':10s}  {r.get('location','')}")

# --- 4. Yaklaşık koordinatlı kayıtlar ---
print()
print("="*80)
print("4. COORD_APPROX=TRUE (sehir merkezi tahmini kullanilan)")
print("="*80)
approx=[r for r in reps if r.get('coord_approx')]
print(f"  Toplam: {len(approx)}")
for r in approx:
    print(f"  {r['id']:8s}  {r.get('city',''):20s}  {r.get('frequency',0):.4f} {r.get('band',''):4s}  {r.get('location','')}")
