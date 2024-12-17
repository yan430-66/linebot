import requests
import os
import pygame

base_url = "https://pokeapi.co/api/v2/"
image_folder = "poke_images"
sound_folder = "poke_sounds"

# Create the folders if they don't exist
if not os.path.exists(image_folder):
    os.makedirs(image_folder)

if not os.path.exists(sound_folder):
    os.makedirs(sound_folder)

def get_pokemon_info(name):
    url = f"{base_url}/pokemon/{name}"
    response = requests.get(url)
    if response.status_code == 200:
        pokemon_data = response.json()
        return pokemon_data
    else:
        print("Error")
        return None

def get_pokemon_description(name):
    url = f"{base_url}/pokemon-species/{name}"
    response = requests.get(url)
    if response.status_code == 200:
        species_data = response.json()
        for entry in species_data['flavor_text_entries']:
            if entry['language']['name'] == 'en':
                return entry['flavor_text']
    else:
        print("Error")
        return None

def download_file(url, filename):
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
    else:
        print(f"Error downloading {filename}")

def play_sound(filename):
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

pokemon_name = input("Enter the name of the Pokémon: ").lower()
pokemon_info = get_pokemon_info(pokemon_name)
pokemon_description = get_pokemon_description(pokemon_name)

if pokemon_info:
    print(f"{pokemon_info['name'].capitalize()} ")
    print(f"ID: {pokemon_info['id']}")
    print(f"Height: {pokemon_info['height']}")
    print(f"Weight: {pokemon_info['weight']}")
    if pokemon_description:
        print(f"Description: {pokemon_description}")
    image_url = pokemon_info['sprites']['front_default']
    print(f"Image URL: {image_url}")
    image_path = os.path.join(image_folder, f"{pokemon_name}.jpg")
    download_file(image_url, image_path)

    # Get the Pokémon's cry URL
    cry_url = f"https://pokemoncries.com/cries/{pokemon_info['id']}.mp3"
    sound_path = os.path.join(sound_folder, f"{pokemon_name}.mp3")
    download_file(cry_url, sound_path)
    play_sound(sound_path)   