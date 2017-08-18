import pip                      # used to install packages
import os                       # used to store sound files
import random                   # used to shuffle songs

#Install necessary packages (if not yet installed)
needed_packages = ['requests', 'spotipy', 'pygame']
installed_packages = [package.key for package in pip.get_installed_distributions()]
for package in needed_packages:
    if package not in installed_packages:
        okay = input("Do you want to install " + package + " (y/n)?: ").lower()
        if okay == 'y':
            pip.main(['install', package])
        else:
            print("This program cannot run")
            exit()

import requests                 # used to download song samples
import spotipy                  # used to access spotify playlist data
import spotipy.util as util     # used to authorize spotify user
import pygame                   # used to play music

#Important constants
MAIN_DATA_DIRECTORY = "Data"

#Functions
def authorize(): # authorize spotify user; give program permission to read user data
    scope = "user-library-read"
    clientId = "a586a97d35ee41bd8836e476de53b6ff"
    clientSecret = "1df216648cbb4c04808304aba2f60c2d"
    redirectURI = "https://www.google.com"

    #Authorize user (get permission to access user playlist data)
    authToken = util.prompt_for_user_token(username, scope,
                                           client_id=clientId,
                                           client_secret=clientSecret,
                                           redirect_uri = redirectURI)
    spotify = spotipy.Spotify(auth=authToken)
    
    return spotify


def choosePlaylist(playlistItems): # give user option to select playlist (from playlists he/she follows)
    #Print all user playlists
    print('Choose a playist:')
    for i, playlist in enumerate(playlistItems):
        print('\t' + str(i + 1)  + ". " + playlist['name'])

    #Recieve user input (choose a playlist)
    choice = int(input('Enter your choice: '))
    playlistUri = playlistItems[choice - 1]['uri']

    #Extract playlist id and playlist user id
    playlistId = playlistUri.split(":")[4]
    playlistUserId = playlistUri.split(":")[2]
    
    return playlistId, playlistUserId

def getSongs(playlistId, playlistUserId): # obtains list of song data for a given playlist
    #Obtain playlist
    playlist = spotify.user_playlist(playlistUserId, playlistId)

    #Extract song titles and preview URLs from playlist
    songs = []
    for song in playlist['tracks']['items']:
        songData = {'name': song['track']['name'],
                    'preview_url': song['track']['preview_url']}
        
        #Some songs do not have previews (will cause error later on)
        if songData['preview_url'] != None:
            songs.append(songData)

    return songs

def downloadSong(url, i): # download song sample from the internet
    #Obtain song data
    data = requests.get(url)

    #Create folder to store song data in
    if not os.path.exists(MAIN_DATA_DIRECTORY):
        os.mkdir(MAIN_DATA_DIRECTORY)

    #Create file to store song data in
    fileName = os.path.join(MAIN_DATA_DIRECTORY, 'mysterySong' + str(i) + '.mp3')
    f = open(fileName, 'wb')

    #Write mp3 data to file
    for chunk in data.iter_content(1000):
        f.write(chunk)
    f.close()

    return fileName

def playGame(songs):
    #Recieve user input (how many rounds)
    turns = int(input("How many rounds would you like to play?: "))

    #Initialize pygame music player
    pygame.mixer.init()

    score = 0
    
    print()
    print()

    #On each turn
    for turn in range(0, turns):
        #Print current turn
        print("Turn #" + str(turn + 1))

        #Obtain song
        song = songs[turn]

        #Download song preview
        fileName = downloadSong(song['preview_url'], turn)

        #Load song preview into pygame music player
        pygame.mixer.music.load(fileName)
        
        #Play song preview
        pygame.mixer.music.play()

        #Wait until user guesses song correctly or song ends
        guess = ""
        while pygame.mixer.music.get_busy():
            guess = input("\tWhat song is this?: ")
            if guess.lower() == song['name'].lower():
                print("\tCorrect!")
                score += 1
                break
            elif guess.lower() == 'idk':
                break
            else:
                print("\tIncorrect!")
                print()

        #Stop playing song preview
        pygame.mixer.music.stop()

        #Reveal answer
        print()
        print("\tSong: " + song['name'])
        print()
        print()
        print()

    #Print final score
    print("Score: " + str(score) + "/" + str(turns))

#Main Program
username = input("What is your Spotify username?: ") # obtain spotify username
  
spotify = authorize() # authorize user account
playlists = spotify.current_user_playlists() # get list of user's playlists

playlistId, playlistUserId = choosePlaylist(playlists['items']) # have user to pick a playlist

songs = getSongs(playlistId, playlistUserId) # obtain list of songs from chosen playlist
random.shuffle(songs) # shuffle songs on playlist

playGame(songs) # play game
