# -*- coding: utf-8 -*-
"""
Fix 5 records with wrong coordinate (39.9324, 32.8438 = Ankara center).
Correct coordinates sourced from geographic lookup of each district/location.
"""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

FIXES = {
    # Çanakkale / Kemelköy: village in Biga district, Çanakkale
    "AT_480": {"lat": 40.2156, "lon": 27.2810, "coord_approx": True,
               "note": "Kemelköy, Biga, Çanakkale — approx village center"},

    # Antalya / Sarıçam: Sarıçam plateau north of Antalya city
    "AT_481": {"lat": 37.0850, "lon": 30.7900, "coord_approx": True,
               "note": "Sarıçam Mevkii, Antalya kuzey Toros etekleri"},

    # İstanbul / Başakşehir: district center
    "AT_482": {"lat": 41.0927, "lon": 28.8063, "coord_approx": True,
               "note": "Başakşehir ilçe merkezi, İstanbul"},

    # Mersin / Toros Dağları: Taurus mountains north of Mersin
    "AT_484": {"lat": 36.9800, "lon": 34.5500, "coord_approx": True,
               "note": "Toros Dağları genel bölge, Mersin kuzeyi"},

    # İzmir / Merkez: İzmir city center
    "AT_485": {"lat": 38.4192, "lon": 27.1287, "coord_approx": True,
               "note": "İzmir şehir merkezi"},
}

with open('docs/data/repeaters.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

fixed = 0
for r in d['repeaters']:
    if r['id'] in FIXES:
        fix = FIXES[r['id']]
        old = (r.get('lat'), r.get('lon'))
        r['lat'] = fix['lat']
        r['lon'] = fix['lon']
        r['coord_approx'] = fix['coord_approx']
        print(f"FIXED {r['id']:8s} ({r['city']:12s} / {r['location']:20s}): "
              f"{old[0]:.4f},{old[1]:.4f} → {fix['lat']:.4f},{fix['lon']:.4f}")
        fixed += 1

with open('docs/data/repeaters.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)

print(f"\n{fixed} kayıt düzeltildi.")
