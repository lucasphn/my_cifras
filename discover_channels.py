"""
Script one-time: descobre os channel IDs do YouTube para todos os artistas
em _CATHOLIC_ARTISTS_BR e imprime o dict para colar em app.py como _CHANNEL_MAP.

Uso:
    YOUTUBE_API_KEY=sua_chave python discover_channels.py

Cada artista consome 100 unidades de quota (search.list type=channel).
Com ~120 artistas = 12.000 unidades. Se sua quota diária for 10.000, rode
em dois dias usando --skip para retomar:

    python discover_channels.py --skip 100
"""

import os
import sys
import time
import json
import argparse
import requests

_CATHOLIC_ARTISTS_BR = [
    # Padres e freis
    "Padre Marcelo Rossi", "Padre Fábio de Melo", "Padre Reginaldo Manzotti",
    "Padre Zezinho", "Padre Antônio Maria", "Padre Joãozinho",
    "Padre Alessandro Campos", "Padre Adriano Zandoná", "Frei Gilson",
    "Padre Edson Delfino", "Padre Mario Sartoni", "Padre Rodrigo Natal",
    # Artistas solo
    "Adriana Arydes", "Eliana Ribeiro", "Walmir Alencar", "Thiago Brado",
    "Flavio Vitor Jr", "Ramon e Rafael", "Juninho Cassimiro", "Rosa de Saron",
    "Ziza Fernandes", "Suely Façanha", "Eros Biondini", "Farlla",
    "Gen Rosso", "Dunga", "Dan Machado", "Danilo Lopes", "Cleiton Saraiva",
    "Eduardo Cruz", "Maíra Jaber", "Diego Fernandes", "Fabiano Ferreira",
    "Emerson Pereira", "Geruza Luz", "Lee Cardoso", "Luan Rodrigues",
    "Lucas Ferreira", "Mandume", "Pablo Cifuentes", "Rafael Arcanjo",
    "Rodrigo Torres", "Wagner Santana", "Yuri Costa", "Alex Pillar",
    "André Florêncio", "Bruno Camurati", "Camila Holanda", "Davidson Silva",
    "Elias Cipriano", "Felipe Alcantara", "Gustavo Verissimo",
    "Jonatan Moraes", "Leandro Kaleb", "Levi Andrei", "Nando Mendes",
    "Phelippe Luz", "Tony Allysson", "Wagner Fernandes", "Eugênio Jorge",
    "Cidinha Cunha", "Adriana Gil", "Aline Brasil", "Amanda Carvalho",
    "Bruno Malaquias", "Cassiano Meirelles", "Clauton Rocha", "Dago Soares",
    "Daniel Clemente", "Dauana Sales", "Dudu Amaral", "Fabiano Ramos",
    "Fabricio Aquino", "Fernando Vinhote", "Gabi Calhau", "Fátima Souza",
    "Gracielle", "Ivan Domingos", "Janaína Santana", "Jardel Adorador",
    "Jonas Santana", "Jonny Mendes", "Juliana de Paula", "Marcelo Mariano",
    "Michelle Abrantes", "Naldo José", "Olívia Ferreira", "Pamela Lourenço",
    "Prislayne Mattos", "Raissa e Mateus", "Reginaldo Moraes", "Ricardo Lins",
    "Rose Liz", "Simone Medeiros", "Talita Garcia", "Ticiana de Paula",
    "Vera Lúcia", "Wesley Gabriel",
    # Comunidades, ministérios e bandas
    "Comunidade Católica Shalom", "Canção Nova", "Fraternidade São João Paulo II",
    "Anjos de Resgate", "Colo de Deus", "Vida Reluz", "GBA Stage",
    "Missionário Shalom", "Ministério Adoração e Vida", "Ministério Excelsis",
    "Banda Dom", "Comunidade Católica Kairós", "Gerados pela Imaculada",
    "Ministério Anawim", "Ministério Reacender", "Som de Santidade",
    "Missão Fogo Alto", "Projeto Yeshua", "Servos da Coroa",
    "Ministério Eterno Amor", "Ministério Fonte de Graça",
    "Aliança de Misericórdia", "Anjos das Ruas", "Banda Arkanjos",
    "Banda Capella", "Banda Dominus", "Banda Filhos de Lourdes",
    "Canthares", "Comunidade CAJU", "Divino Oleiro Louvor",
    "Forró Mensageiros da Paz", "ID2", "Ministério Alelluia",
    "Ministério Basílica", "Ministério Chamado de Deus",
    "Ministério Diante da Cruz", "Ministério LDM", "Ministério Sacrare",
    "Ministério Seráfico", "Ministério Tronos", "Missão Católica Yeshua",
    "Terra da Cruz", "Via Sete8", "Voz Eterna", "Single Core",
    "Ministério Vida em Santidade", "Ministério Amor e Adoração", 'Adoração e Vida',
]

CACHE_FILE = "_channel_ids.json"


def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_cache(data):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def discover(api_key, skip=0):
    cache = load_cache()
    artists = [a for a in _CATHOLIC_ARTISTS_BR if a not in cache]
    artists = artists[skip:]

    print(f"Descobrindo {len(artists)} artistas (skip={skip})...", flush=True)

    for i, artist in enumerate(artists, 1):
        try:
            r = requests.get(
                "https://www.googleapis.com/youtube/v3/search",
                params={"part": "snippet", "q": artist, "type": "channel", "maxResults": 1, "key": api_key},
                timeout=10,
            )
            r.raise_for_status()
            items = r.json().get("items", [])
            if items:
                cid = items[0]["id"]["channelId"]
                cache[artist] = cid
                print(f"  [{i}/{len(artists)}] {artist} → {cid}")
            else:
                print(f"  [{i}/{len(artists)}] {artist} → NÃO ENCONTRADO")
            save_cache(cache)
            time.sleep(0.2)
        except Exception as e:
            print(f"  [{i}/{len(artists)}] {artist} → ERRO: {e}")

    return cache


def print_python_dict(cache):
    print("\n" + "=" * 60)
    print("Cole isso em app.py como _CHANNEL_MAP:")
    print("=" * 60)
    print("_CHANNEL_MAP: dict = {")
    for artist, cid in sorted(cache.items()):
        print(f'    {artist!r}: {cid!r},')
    print("}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip", type=int, default=0, help="Pular N artistas (para retomar entre dias)")
    parser.add_argument("--print-only", action="store_true", help="Só imprime o dict do cache atual")
    args = parser.parse_args()

    api_key = os.environ.get("YOUTUBE_API_KEY", "")
    if not api_key and not args.print_only:
        print("Erro: defina YOUTUBE_API_KEY no ambiente.")
        sys.exit(1)

    if args.print_only:
        cache = load_cache()
    else:
        cache = discover(api_key, skip=args.skip)

    print_python_dict(cache)
    print(f"\nTotal descobertos: {len(cache)}/{len(_CATHOLIC_ARTISTS_BR)}")
