import requests as req
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel


app = FastAPI()

fakePokemonDb = {
    25: {
        "Nombre": "Pikachu",
        "Habilidades": ["static", "lightning-rod"],
        "Numero de la PokeDesk": 25,
        "Tipo": ["electric"],
        "Sprites": {"front_default": "https://example.com/sprite.png"}
    }
}

# Definir el modelo que se espera para las actualizaciones
class PokemonUpdate(BaseModel):
    name: str | None = None
    abilities: list[str] | None = None
    sprites: dict | None = None
    type: list[str] | None = None


@app.middleware("http")
async def processPokemons(request: Request, call_next):
    try:
        urlPath = request.url.path
        if urlPath != '/' and urlPath != '/favicon.ico': 
            if "pokemon" in urlPath:
                id = urlPath.split('/')[-1]

                if (id.isdigit() == False) and (id.isalpha() == False):
                    raise HTTPException(status_code=400, detail="Identificador del pokemon no valido")
            else:
                raise HTTPException(status_code=404, detail="URL no encontrada o no existe el endpoint")
        else:
            print(urlPath)
    except HTTPException as http_exc:
        # Crear una respuesta con el código de estado y el mensaje de error
        return JSONResponse(
            status_code=http_exc.status_code,
            content={"detail": http_exc.detail}
        )

    response = await call_next(request)
    return response

@app.get("/")
def home():
    return "API POKEDEX OAK // Autor: Jesús Alejandro Dávila Pinchao // Framework:FastAPI"

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
    if pokeDesk not in fakePokemonDb:
        fakePokemonDb[pokeDesk] = filterPokemon
    print(filterPokemon)

    return filterPokemon

@app.patch("/api/pokemon/{pokeId}")
async def update_pokemon(pokeId: int, pokemon: PokemonUpdate):

    try:
        id = pokeId
        if id.isdigit() == False:
            pokemons = req.get(url="https://pokeapi.co/api/v2/pokemon/", params=None).json()["results"]
            for i in range(0, len(pokemons)):
                pokemon = pokemons[i]
                if pokemon["name"] == id:
                    id = req.get(url=pokemon["url"], params=None).json()["id"]

        if id not in fakePokemonDb:
            raise HTTPException(status_code=404, detail="Pokemon no encontrado o no añadido, prueba hacer una petición GET del pokemon para que este sea añadido a la base de datos local")

        # Obtener el Pokémon actual
        storedPokemon = fakePokemonDb[id]
        lastPokemon = storedPokemon
        # Actualizar solo los campos proporcionados
        
        if pokemon.name is not None:
            storedPokemon["Nombre"] = pokemon.name
        if pokemon.abilities is not None:
            storedPokemon["Habilidades"] = pokemon.abilities
        if pokemon.sprites is not None:
            storedPokemon["Sprites"] = pokemon.sprites
        if pokemon.type is not None:
            storedPokemon["Tipo"] = pokemon.type

        fakePokemonDb[id] = storedPokemon
        return {"message": "Pokemon updated", "last pokemon":lastPokemon, "pokemon": storedPokemon}
    except HTTPException as http_exc:
        return JSONResponse(
            status_code=http_exc.status_code,
            content={"detail": http_exc.detail}
        )

if __name__ == '__main__':
   uvicorn.run(app, host="localhost", port=8000)