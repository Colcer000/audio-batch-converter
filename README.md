# Audio Batch Converter
A python script that converts audio files, artwork and metadata into listen-ready formats. It uses ffmpeg for audio formatting and MusicBrainz for metadata completion.

*For the script to work, make sure the audio files have artist and title in the metadata.*

How it works?
- It scans the current folder for audio files and associated images;
- Converts them to desired settings (format, sample rate, bitrate, channels);
- It can convert and save artwork in a 1000x1000 png format;
- Searches MusicBrainz for the most accurate tags (replaces only album, year and genre)
- Uses Mutagen library to modify metadata.
- Optionally, rename the files in "Artist - Title".

How to use:
- Install ffmpeg and copy "ffmpeg.exe" in "_internal" folder (download separately);
- Place all the desired songs in the same folder as the script;
- If you have better pictures to add to the audio, rename them to the name of the audio file and keep them in the same folder with the audio and the script;
- Run the script;
- Apply desired settings and start batch conversion.
