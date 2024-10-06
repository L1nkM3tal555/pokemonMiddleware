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
    """
    Middleware que intercepta las peticiones y verifica si contienen la palabra 'pokemon' en la URL.
    Si el identificador del Pokémon es inválido o si la ruta no existe, lanza una excepción.

    Parámetros:
    - request (Request): La solicitud HTTP que llega al servidor.
    - call_next (Callable): Función que invoca la siguiente capa del middleware.

    Retorno:
    - JSONResponse: Respuesta en caso de error con el detalle del error.
    - Response: Respuesta normal del servidor si no hay errores.
    """
    try:
        urlPath = request.url.path
        if urlPath != '/' and urlPath != '/favicon.ico' and urlPath != '/api/general': 
            if urlPath.split('/')[2] == 'pokemon':
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
def home()->str:
    """
    Página de inicio simple que muestra información básica sobre la API.

    Retorno:
    - str: Mensaje de bienvenida con la información del autor y el framework utilizado.
    """
    return "API POKEDEX OAK // Autor: Jesús Alejandro Dávila Pinchao // Framework:FastAPI"

@app.get("/api/general")
def generalPokemons()->list:
    """
    Obtiene una lista general de Pokémon desde la API pública `pokeapi.co`.

    Retorno:
    - list: Lista de Pokémon, cada uno con su nombre y URL de acceso.
    """
    
    pokemonsR = req.get(url="https://pokeapi.co/api/v2/pokemon", params=None).json()

    pokemons = pokemonsR["results"]

    while pokemonsR["next"] != None:
        pokemonsR = req.get(url=pokemonsR["next"], params=None).json()
        pokemons.extend(pokemonsR["results"])

    return pokemons

@app.get("/api/pokemon/{id}")
def getPokemon(id:str)->dict:
    """
    Obtiene los detalles de un Pokémon por su ID o nombre desde la API pública `pokeapi.co` o la base de datos local.

    Parámetros:
    - id (str): El ID de la PokeDex o el nombre del Pokémon que se desea obtener.

    Retorno:
    - dict: Diccionario con la información del Pokémon (Nombre, habilidades, Numero de la PokeDex, Tipo y Sprites).
    """
    pokemonStats = None

    nombre = ''
    pokeDesk = 0

    try:
        if id.isdigit() == False:
            pokemonsR = req.get(url="https://pokeapi.co/api/v2/pokemon/", params=None).json()
            found = False
            while pokemonsR["next"] != None and found == False:
                pokemonsPage = pokemonsR["results"]
                i = 0
                while i<len(pokemonsPage) and found == False:
                    pokemon = pokemonsPage[i]
                    if pokemon["name"] == id:
                        pokemonStats = req.get(url=pokemon["url"], params=None).json()
                        nombre = id
                        pokeDesk = pokemonStats["id"]
                        found = True
                    i+=1

                pokemonsR = req.get(url=pokemonsR["next"], params=None).json()

            if found == False:
                raise HTTPException(status_code=404, detail="Pokemon no existente")

        else:
            urlId = "https://pokeapi.co/api/v2/pokemon/"+id
            pokemonStats = req.get(url=urlId, params=None).json()

            if pokemonStats["id"] == int(id):
                nombre = pokemonStats["name"]
                pokeDesk = int(id)

    except HTTPException as http_exc:
        # Crear una respuesta con el código de estado y el mensaje de error
        return JSONResponse(
            status_code=http_exc.status_code,
            content={"detail": http_exc.detail}
        )

    skills = []
    types = []
    ab = pokemonStats["abilities"]
    sp = pokemonStats["sprites"]
    tp = pokemonStats["types"]
    for j in range(0, len(ab)):
        skills.append(ab[j]["ability"]["name"])

    for k in range(0, len(tp)):
        types.append(tp[k]["type"]["name"])

    filterPokemon = {"Nombre": nombre, "Habilidades": skills, "Numero de la PokeDesk": pokeDesk,"Tipo":types, "Sprites": sp}
    if pokeDesk not in fakePokemonDb:
        fakePokemonDb[pokeDesk] = filterPokemon

    return filterPokemon

@app.patch("/api/pokemon/{pokeId}")
async def update_pokemon(pokeId: str, pokemon: PokemonUpdate):
    """
    Actualiza los detalles de un Pokémon en la base de datos local, si ya está registrado.
    Solo se actualizan los campos proporcionados en la solicitud.

    Parámetros:
    - pokeId (str): El ID la PokeDex o el nombre del Pokémon a actualizar.
    - pokemon (PokemonUpdate): El cuerpo de la solicitud que contiene los campos a actualizar.

    Retorno:
    - dict: Mensaje de éxito con el Pokémon actualizado y su estado anterior.
    - JSONResponse: Respuesta en caso de error si el Pokémon no está en la base de datos local.
    """
    try:
        id = pokeId
        if id.isdigit() == False:
            pokemonsR = req.get(url="https://pokeapi.co/api/v2/pokemon/", params=None).json()
            found = False
            while pokemonsR["next"] != None and found == False:
                pokemonsPage = pokemonsR["results"]
                i = 0
                while i<len(pokemonsPage) and found == False:
                    pokemon = pokemonsPage[i]
                    
                    if pokemon["name"] == id:
                        id = req.get(url=pokemon["url"], params=None).json()["id"]
                        found = True
                    
                    i+=1
            
            if found == False:
                raise HTTPException(status_code=404, detail="Pokemon no existente")

            pokemonsR = req.get(url=pokemonsR["next"], params=None).json()

        if int(id) not in fakePokemonDb:
            raise HTTPException(status_code=404, detail="Pokemon no encontrado o no añadido, prueba hacer una petición GET del pokemon para que este sea añadido a la base de datos local")

        # Obtener el Pokémon actual
        storedPokemon = fakePokemonDb[int(id)]
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
        return JSONResponse(status_code=200, content={"message": "Pokemon updated", "last pokemon":lastPokemon, "pokemon": storedPokemon})
    except HTTPException as http_exc:
        return JSONResponse(
            status_code=http_exc.status_code,
            content={"detail": http_exc.detail}
        )
# Inicio del servidor
if __name__ == '__main__':
   uvicorn.run(app, host="localhost", port=8000)