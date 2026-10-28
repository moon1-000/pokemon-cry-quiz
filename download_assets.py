"""
포켓몬 1~1025번 울음소리(.ogg)와 공식 일러스트(.png)를 PokéAPI에서 한 번에 받는 스크립트.

사용법 (index.html, pokemon.json과 같은 폴더에서):
    python download_assets.py

결과:
    assets/cries/1.ogg ... 1025.ogg      (약 20MB)
    assets/images/1.png ... 1025.png     (약 400MB, 원하면 --no-images)
옵션:
    --legacy     1~649번은 옛날 게임(8비트 느낌) 울음소리도 assets/cries_legacy/ 에 받기
    --no-images  이미지는 받지 않기

다 받은 뒤 index.html의 `const LOCAL = false;` 를 true로 바꾸면 내 서버의 파일을 씁니다.
"""
import json, os, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

CRY = "https://raw.githubusercontent.com/PokeAPI/cries/main/cries/pokemon/{kind}/{id}.ogg"
IMG = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{id}.png"

def fetch(url, path):
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return "skip"
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=30) as r, open(path, "wb") as f:
                f.write(r.read())
            return "ok"
        except Exception as e:
            if getattr(e, "code", None) == 404:
                return "missing"
            time.sleep(1 + attempt)
    return "fail"

def main():
    ids = [p["id"] for p in json.load(open("pokemon.json", encoding="utf-8"))]
    jobs = []
    os.makedirs("assets/cries", exist_ok=True)
    jobs += [(CRY.format(kind="latest", id=i), f"assets/cries/{i}.ogg") for i in ids]
    if "--legacy" in sys.argv:
        os.makedirs("assets/cries_legacy", exist_ok=True)
        jobs += [(CRY.format(kind="legacy", id=i), f"assets/cries_legacy/{i}.ogg") for i in ids if i <= 649]
    if "--no-images" not in sys.argv:
        os.makedirs("assets/images", exist_ok=True)
        jobs += [(IMG.format(id=i), f"assets/images/{i}.png") for i in ids]

    counts = {}
    with ThreadPoolExecutor(max_workers=8) as ex:
        for n, res in enumerate(ex.map(lambda j: fetch(*j), jobs), 1):
            counts[res] = counts.get(res, 0) + 1
            if n % 100 == 0 or n == len(jobs):
                print(f"{n}/{len(jobs)}  {counts}")
    print("완료:", counts)

if __name__ == "__main__":
    main()
