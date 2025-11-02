import tidalapi
import math
from tidalapi import Quality
from operator import itemgetter
from difflib import SequenceMatcher


def fitting_ratio(track0, track1, name_weight=0.3, duration_weight=0.2, album_weight=0.1, artists_weight=0.4,
                  length_not_matching_weight=0.25):
    score = 0

    fn_ratio = SequenceMatcher(None, track0.name, track1.name).ratio()
    score += name_weight * fn_ratio
    if len(track0.name) != len(track1.name):
        score -= name_weight * length_not_matching_weight * fn_ratio

    fn_ratio = SequenceMatcher(None, track0.album.name, track1.album.name).ratio()
    score += album_weight * fn_ratio
    if len(track0.album.name) != len(track1.album.name):
        score -= album_weight * length_not_matching_weight * fn_ratio

    score += (track0.duration - abs(track0.duration - track1.duration)) / track0.duration * duration_weight

    artists_count0 = len(track0.artists)
    artists_count1 = 0
    for artist0 in track0.artists:
        for artist1 in track1.artists:
            if artist0.name == artist1.name:
                artists_count1 += 1
    score += artists_weight * artists_count1 / artists_count0

    return score


def find_most_fitting(fn_list, track0, score_req=0.65):
    output = []
    for track1 in fn_list:

        score = fitting_ratio(track0, track1)
        if score >= score_req:
            output.append([track1, score])

    output = sorted(output, key=itemgetter(1), reverse=True)
    return output


def artists_as_string(fn_track):
    text_output = ""
    for artist in fn_track.artists:
        if text_output == "":
            text_output += artist.name
        else:
            text_output += ", "
            text_output += artist.name
    return text_output


def add_songs_to_playlist(fn_playlist, fn_list, fn_append):
    fn_list.append(fn_append)
    output = fn_list
    if len(fn_list) >= 100:
        fn_playlist.add(fn_list)
        output = []
    return output


def display_track_info(fn_track):
    dur_minutes = math.floor(fn_track.duration / 60)
    dur_secs = str(fn_track.duration - dur_minutes * 60)
    dur_minutes = str(dur_minutes)
    return fn_track.name + " by " + artists_as_string(
        fn_track) + " (Album: " + fn_track.album.name + ") [" + dur_minutes + ":" + dur_secs + "], quality: " + str(
        fn_track.audio_quality)


print(
    "\nA new link is about to be generated, paste it in your web browser and link it with your TIDAL account to continue.\n")

session = tidalapi.Session()
session.login_oauth_simple()
user = tidalapi.user.LoggedInUser(session, session.user.id)

print("")
print("Fetching playlists...")
playlists = tidalapi.user.LoggedInUser.playlists(session.user)
if len(playlists) == 0:
    input("You don't have any playlists! Create one before using the script!")
    exit()
elif len(playlists) == 50:
    input("You do not have any free playlist slots! Please delete one to allow the script to work properly!")
    exit()
print("\n-+-====================-+-")
playlistCount = 1
for playlist in playlists:
    print(playlistCount, ": ", playlist.name, " - ", playlist.description, " (", playlist.num_tracks, " tracks)",
          sep="")
    playlistCount += 1
print("-+-====================-+-\n")


confirmed = 0
selectedPlaylistID = 0
while confirmed == 0:

    selectedPlaylistID = -1
    playlistExists = 0

    while playlistExists == 0:

        selectedPlaylistID = input(
            "Insert the ID (number next to the playlist name) of the playlist you'd like to modify: ")
        selectedPlaylistID = int(selectedPlaylistID)

        if selectedPlaylistID > 0 & selectedPlaylistID <= playlistCount:
            playlistExists = 1

    selectedPlaylist = playlists[selectedPlaylistID - 1]
    print("Selected playlist: ", selectedPlaylist.name, "!\n", sep="")

    confirmation = input("Confirm selection? [Y/N]: ")
    if confirmation.lower() == "y":
        confirmed = 1

selectedPlaylist = playlists[selectedPlaylistID - 1]

selectedOption = 0
while selectedOption == 0:
    print("\nPlease make a selection out of the available options:\n")
    print("-+-====================-+-")
    print(
        "1: Find best possible audio quality for the tracks in it, create a copy and manually select tracks if found. [A LOT SLOWER BUT IS MORE ACCURATE]")
    print(
        "2: Find best possible audio quality for the tracks in it, create a copy and automatically insert tracks! [A LOT FASTER BUT MAY BE LESS ACCURATE]")
    print("-+-====================-+-\n")
    selection = int(input("Selection: "))

    if selection > 0 & selection <= 1:
        selectedOption = selection

if selectedOption == 1 or selectedOption == 2:
    print("Creating a copy of the playlist!")
    user.create_playlist((selectedPlaylist.name + " (BAP)"), selectedPlaylist.description)
    playlists = user.playlists()
    createdPlaylist = None
    for playlist in playlists:
        if playlist.name == selectedPlaylist.name + " (BAP)":
            createdPlaylist = tidalapi.playlist.UserPlaylist(session=session, playlist_id=playlist.id)
            break

    print("\nSearching for best possible audio for all of the tracks\n")

    tracks = selectedPlaylist.tracks()
    trackNo = 0
    addSongs = []
    for track in tracks:
        trackNo += 1
        print("Progress: ", trackNo, "/", selectedPlaylist.num_tracks, " ",
              round(trackNo / selectedPlaylist.num_tracks * 100, 2), "%", sep="")
        if track.audio_quality == Quality.hi_res_lossless:
            addSongs = add_songs_to_playlist(createdPlaylist, addSongs, str(track.id))
        else:
            query = track.name
            query += " " + artists_as_string(track)
            search = session.search(query, [tidalapi.media.Track, None], 50)

            listToChooseFrom = []

            searchingForQuality = Quality.hi_res_lossless
            while True:
                if track.audio_quality == searchingForQuality:
                    break

                for searchedTrack in search["tracks"]:
                    if searchedTrack.audio_quality == searchingForQuality:
                        listToChooseFrom.append(searchedTrack)
                if len(listToChooseFrom) > 0:
                    break

                if searchingForQuality == Quality.hi_res_lossless:
                    searchingForQuality = Quality.high_lossless
                elif searchingForQuality == Quality.high_lossless:
                    searchingForQuality = Quality.low_320k
                elif searchingForQuality == Quality.low_320k:
                    searchingForQuality = Quality.low_96k
                else:
                    break

            listToChooseFrom = find_most_fitting(listToChooseFrom, track)

            if len(listToChooseFrom) == 0 or len(listToChooseFrom) == 1:
                addSongs = add_songs_to_playlist(createdPlaylist, addSongs, str(track.id))
                continue
            elif selectedOption == 2:
                addSongs = add_songs_to_playlist(createdPlaylist, addSongs, str(listToChooseFrom[0][0].id))
            elif selectedOption == 1 and len(listToChooseFrom) > 1:
                added = 0
                while added == 0:
                    print("\n-+-====================-+-")
                    print("Multiple tracks were found! Please select the one you deem fitting!")
                    print("Best possible quality found for this track: ", str(listToChooseFrom[0][0].audio_quality),
                          sep="")
                    print("-+-====================-+-")
                    print("Original track: ", display_track_info(track), sep="")
                    print("Selecting 0 will insert the original instead of the found ones!")
                    print("-+-====================-+-")

                    i = 1
                    for chooseFromTrack in listToChooseFrom:
                        print(i, ": ", display_track_info(chooseFromTrack[0]), ", confidence: ",
                              round(chooseFromTrack[1] * 100, 2), "%", sep="")
                        i += 1
                    print("-+-====================-+-\n")

                    selectedTrackID = int(
                        input("Select the ID (number next to the track name) of the track you wish to insert to the playlist: "))
                    if 1 <= selectedTrackID <= len(listToChooseFrom):
                        added = 1
                        addSongs = add_songs_to_playlist(createdPlaylist, addSongs,
                                                         str(listToChooseFrom[selectedTrackID - 1][0].id))
                    elif selectedTrackID == 0:
                        added = 1
                        addSongs = add_songs_to_playlist(createdPlaylist, addSongs, str(track.id))

    createdPlaylist.add(addSongs)

    print("\nFinished creating the playlist!\n")
    print("Running a compare test...")

    if len(createdPlaylist.tracks()) != len(selectedPlaylist.tracks()):
        print(
            "\nFound missing tracks! It seems like there was an issue with adding them!\nPlease try adding them manually!\nListing those missing tracks...")
        tracks0 = selectedPlaylist.tracks()
        tracks1 = createdPlaylist.tracks()

        offset = 0
        index = 0
        print("\n-+-====================-+-")
        while index + offset < len(tracks0) and index < len(tracks1):
            ratio = fitting_ratio(tracks1[index], tracks0[index + offset])
            if ratio <= 0.25:
                print(str(index + offset + 1) + ": " + display_track_info(tracks0[index + offset]) + " (id: " + str(
                    tracks0[index + offset].id) + ")")
                offset += 1
            else:
                index += 1
        print("-+-====================-+-")

    print("\nCompare test finished!\nJob finished, you'll find the playlist under this name: ", createdPlaylist.name,
          "!", sep="")
    if selectedOption == 2:
        print(
            "\nPlease make sure to check if every found track is the correct one.\nDo not delete the old playlist until you confirm everything yourself!")

input("\nThanks for using the script!\nIt's now safe to close the window!")