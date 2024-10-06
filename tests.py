import pytest
from fastapi.testclient import TestClient
from main import app, fakePokemonDb

client = TestClient(app)

# TESTS PARA EL MIDDLEWARE

def test_middleware_invalid_pokemon_id():
    response = client.get("/api/pokemon/25!")
    assert response.status_code == 400
    assert response.json() == {"detail": "Identificador del pokemon no valido"}

def test_middleware_invalid_url():
    response = client.get("/api/notpokemon/25")
    assert response.status_code == 404
    assert response.json() == {"detail": "URL no encontrada o no existe el endpoint"}

# TESTS PARA LAS FUNCIONES

# Test para la ruta raíz (home)
def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.text.strip('"') == "API POKEDEX OAK // Autor: Jesús Alejandro Dávila Pinchao // Framework:FastAPI"

# Test para la ruta de listado general de Pokémon
def test_general_pokemons():
    response = client.get("/api/general")
    assert response.status_code == 200
    assert isinstance(response.json(), list)  # La respuesta debe ser una lista

# Test para obtener los detalles de un Pokémon existente (pikachu en la base local)
def test_get_pokemon_from_local_db():
    response = client.get("/api/pokemon/25")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["Nombre"] == "pikachu"
    assert "Habilidades" in json_data
    assert "Tipo" in json_data
    assert "Sprites" in json_data

# Test para obtener un Pokémon inexistente en la base de datos local pero que existe en la API externa
def test_get_pokemon_from_api():
    response = client.get("/api/pokemon/1")  # Bulbasaur, ID 1 en la PokeDex
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["Nombre"] == "bulbasaur"
    assert "Habilidades" in json_data
    assert "Tipo" in json_data
    assert "Sprites" in json_data
    assert json_data["Numero de la PokeDesk"] == 1
    # Verificar que se ha añadido al fakePokemonDb
    assert 1 in fakePokemonDb

# Test para actualizar un Pokémon en la base de datos local
def test_update_pokemon():
    # Primero se añade a la base de datos local
    client.get("/api/pokemon/25")
    update_data = {
        "name": "PikachuUpdated",
        "abilities": ["static"],
        "sprites": {"front_default": "https://example.com/updated_sprite.png"},
        "type": ["electric"]
    }
    response = client.patch("/api/pokemon/25", json=update_data)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["pokemon"]["Nombre"] == "PikachuUpdated"
    assert json_data["pokemon"]["Habilidades"] == ["static"]
    assert json_data["pokemon"]["Sprites"] == {"front_default": "https://example.com/updated_sprite.png"}

# Test para intentar actualizar un Pokémon que no está en la base de datos local
def test_update_non_existing_pokemon():
    update_data = {
        "name": "NonExistingPokemon",
        "abilities": ["non-existing-ability"]
    }
    response = client.patch("/api/pokemon/10000", json=update_data)
    assert response.status_code == 404
    assert response.json() == {"detail": "Pokemon no encontrado o no añadido, prueba hacer una petición GET del pokemon para que este sea añadido a la base de datos local"}

# Probar la búsqueda de un Pokémon por nombre
def test_get_pokemon_by_name():
    
    response = client.get("/api/pokemon/pikachu")
    assert response.status_code == 200
    data = response.json()
    
    assert data["Nombre"] == "pikachu"
    assert "Habilidades" in data
    assert "Numero de la PokeDesk" in data
    assert "Tipo" in data
    assert "Sprites" in data

# Probar una solicitud con un nombre de Pokémon no válido
def test_get_pokemon_by_invalid_name():
    
    response = client.get("/api/pokemon/invalidpokemon")
    assert response.status_code == 404
    assert response.json() == {"detail": "Pokemon no existente"}
"""
# Asegurarse de que el Pokémon esté primero en la base de datos simulada
def test_patch_pokemon_by_name():
    
    fakePokemonDb[25] = {
        "Nombre": "pikachu",
        "Habilidades": ["static", "lightning-rod"],
        "Numero de la PokeDesk": 25,
        "Tipo": ["electric"],
        "Sprites": {"front_default": "https://example.com/sprite.png"}
    }

    # Realizar la solicitud PATCH para actualizar las habilidades de Pikachu
    response = client.patch("/api/pokemon/pikachu", json={
        "abilities": ["static", "surge-surfer"]
    })
    assert response.status_code == 200

    data = response.json()
    
    # Verificar que los datos se hayan actualizado correctamente
    assert data["pokemon"]["Habilidades"] == ["static", "surge-surfer"]
    assert data["pokemon"]["Nombre"] == "pikachu"

# Probar actualización de un Pokémon que no existe
def test_patch_pokemon_invalid_name():
    
    response = client.patch("/api/pokemon/invalidpokemon", json={
        "abilities": ["new-ability"]
    })
    assert response.status_code == 404
    assert response.json() == {"detail": "Pokemon no encontrado o no añadido, prueba hacer una petición GET del pokemon para que este sea añadido a la base de datos local"}
"""