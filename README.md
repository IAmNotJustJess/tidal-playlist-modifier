# tidal-playlist-modifier
 A somewhat simple Python script that finds you best possible audio quality for your TIDAL playlists.

## Requirements:
- A [TIDAL](https://tidal.com) account, with an active subscription
- [Python 3.10 or newer](https://www.python.org/downloads/) (Older versions were untested)
- [python-tidal](https://github.com/tamland/python-tidal)

## Installation guide:
### 1. Install Python on your machine:
Download a Python 3.10 installer from the [Official Python website](https://www.python.org/) and install the software on your machine.

### 2. Install python-tidal:
Open your system's Command Line (in administrator mode) or Terminal and install the module from [PyPI](https://pypi.org/project/tidalapi/) using `pip`.
```
$ pip install tidalapi
```

## Usage:
Run the `playlist-modifier.py` file

Upon opening the file you'll see a generated OAuth link, for example: 
```
A new link is about to be generated, paste it in your web browser and link it with your TIDAL account to continue.

Visit link.tidal.com/ABCDE to log in, the code will expire in 300 seconds
```

Paste the link in your Web Browser of choice. Upon entering it you log in into your TIDAL account and press the `Yes, continue` button.
After pressing it you can go back to your opened script.

You should see a list of your playlists, their descriptions and their amount of tracks, for example:
```
Fetching playlists...

-+-====================-+-
1: Workout mix - A playlist with multiple songs for my workout sessions. (53 tracks)
2: Random playlist - Read the title silly... (30 tracks)
3: Example playlist - This is an example! (780 tracks)
-+-====================-+-

Insert the ID (number next to the playlist name) of the playlist you'd like to modify:
```
Upon identifying the playlist you'd like to modify, insert its number and press enter. For this example I'm going to choose the playlist number 3.

Now confirm your selection (or not if you mistyped, in that case type `N`) by typing `Y` and pressing `enter`.
```
Selected playlist: Example playlist

Confirm selection? [Y/N]: y
```

You should now see a small menu of options:
```
Please make a selection out of the available options:

-+-====================-+-
1: Find best possible audio quality for the tracks in it, create a copy and manually select tracks if found. [A LOT SLOWER BUT IS MORE ACCURATE]
2: Find best possible audio quality for the tracks in it, create a copy and automatically insert tracks! [A LOT FASTER BUT MAY BE LESS ACCURATE]
-+-====================-+-

Selection:
```
Both options will search for the best quality of the tracks inside your playlist. *(Note: Audio quality is prioritised as followed: Master > Lossless > High > Low)*

By selecting option no. `1` you'll be prompted to confirm a track in a case where the script find multiple tracks it finds fitting, for example it may show you something similar to this:

```
-+-====================-+-
Multiple tracks were found! Please select the one you deem fitting!
Best possible quality found for this track: master
-+-====================-+-
Original track: Example track by Example artist (Album: Example track) [3:34], quality: lossless
Selecting 0 will insert the original instead of the found ones!
-+-====================-+-
1: Example track by Example artist (Album: Example track) [3:35], quality: master, confidence: 99.91%
2: Example track by Example artist (Album: Example album) [3:36], quality: master, confidence: 91.39%
3: Example track by Example artist (Album: Example album [Remixes]) [3:35], quality: master, confidence: 89.9%
4: Example track by Example artist (Album: Example album [Remixes]) [6:58], quality: master, confidence: 72.51%
-+-====================-+-

Select the ID (number next to the track name) of the track you wish to insert to the playlist:
```

You'll be prompted to select a track from the following list (in this case from `1` to `4`), selecting `0` will insert the original track into this playlist. You'll have to repeat this for every track that'll come with multiple results.

By selecting option no. `2` everything will be selected automatically, according to how [confident](docs/CONFIDENCE.md) the script is to its findings. All you have to do is wait for the script to finish.

After finishing with the search procedure the script will do a simple check if the playlists numbers of tracks are the same, if they're not it will try to find the missing tracks and list them for you, so you can add them manually on the app or the website yourself. *(Note: I found this weird issue with some of the tracks, they're never added to the playlist using this script for an unexplained reason)*.

After the script has finished working you should see a new playlist. In this example the name of it would be `Example playlist (BAP)`. The name of the playlist will **always** end with `(BAP)`. It'll be safe to close the script now.

*Enjoy the music!*
