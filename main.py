import requests as req
import uvicorn
from fastapi import FastAPI, Request, HTTPException


app = FastAPI()

@app.middleware("http")
async def processPokemons(request: Request, call_next):

    urlPath = request.url.path

    if "pokemon" in urlPath:
        id = urlPath.split('/')[-1]

        if (id.isdigit() == False) and (id.isalpha() == False):
            raise HTTPException(status_code=400, detail="Identificador del pokemon no valido")
    elif urlPath == "/favicon.ico":
        print(urlPath)
    else:
        raise HTTPException(status_code=404, detail="URL no encontrada o no existe el endpoint")

    response = await call_next(request)
    return response

@app.get("/api/general")
def generalPokemons():
    pokemons = req.get(url="https://pokeapi.co/api/v2/pokemon", params=None)
    print(pokemons.json())
    p = pokemons.json()["results"]
    #printedPokemons = ''

    return p

@app.get("/api/pokemon/{id}")
def getPokemon(id:str):
    
    pokemonStats = None

    nombre = ''
    pokeDesk = 0

    if id.isdigit() == False:
        pokemons = req.get(url="https://pokeapi.co/api/v2/pokemon/", params=None).json()["results"]
        for i in range(0, len(pokemons)):
            pokemon = pokemons[i]
            if pokemon["name"] == id:
                pokemonStats = req.get(url=pokemon["url"], params=None).json()
                nombre = id
                pokeDesk = pokemonStats["id"]
    else:
        urlId = "https://pokeapi.co/api/v2/pokemon/"+id
        pokemonStats = req.get(url=urlId, params=None).json()

        if pokemonStats["id"] == int(id):
            nombre = pokemonStats["name"]
            pokeDesk = int(id)

    skills = []
    types = []
    ab = pokemonStats["abilities"]
    sp = pokemonStats["sprites"]
    tp = pokemonStats["types"]
    for j in range(0, len(ab)):
        skills.append(ab[j]["ability"]["name"])

    for k in range(0, len(ab)):
        types.append(tp[k]["type"]["name"])

    
    filterPokemon = {"Nombre": nombre, "Habilidades": skills, "Numero de la PokeDesk": pokeDesk,"Tipo":types, "Sprites": sp}
    print(filterPokemon)

    return filterPokemon

if __name__ == '__main__':
   uvicorn.run(app, host="localhost", port=8000)