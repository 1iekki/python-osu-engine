# Python Osu Engine

This is a clone of Osu! rythm game made using python with pygame library.

##  Demo

A demo of the game.
<video width="640" height="360" controls>
  <source src="assets/demo.mp4" type="video/mp4">
</video>

## 🔧 Requirements and Installation

1. Clone the repository
```
git clone https://github.com/1iekki/python-osu-engine
```
2. Install required package
```
pip install pygame
```

## 🎮 How to run

1. Navigate to python-osu-engine folder
```
cd python-osu-engine
```
2. Run the game.py script
```
python game.py
```

## 🔊 Importing maps

The game does not include any beatmaps. See below how to add your own beatmaps.

### Importing .osz files

You can move a .osz file to the game folder. The game will automatically import them on game start. It has to be restarted if it is already running.

### Importing maps from osu

You can import maps by copying the map folder from your osu directory into ./beatmaps folder.

## 🔨 Settings

### Changing settings
The game does not have a settings panel. You can edit the settings by editing the hashtable inside settings.py script and running the script.

### Default settings 
The game runs on fullscreen at 1920x1080 by default. The default input keys are S and D.
