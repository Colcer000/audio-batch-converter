import audioConverter as ac
import artworkConverter as art
import replayGainAnalyzer as rga

import pathlib as pl
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, TYER, TCON, TXXX, ID3NoHeaderError
from mutagen.flac import FLAC, Picture
from mutagen.oggvorbis import OggVorbis
from mutagen.oggopus import OggOpus
from mutagen.mp4 import MP4, MP4Cover
import musicbrainzngs as mb

import base64
import json
import os
import sys
import traceback

def handle_exception(exc_type, exc_value, exc_traceback):
    print("UNCAUGHT EXCEPTION:")
    traceback.print_exception(exc_type, exc_value, exc_traceback)
    input("Press Enter to exit...")

sys.excepthook = handle_exception

def get_ffmpeg_path():
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, "ffmpeg.exe")
    return "ffmpeg"

ARTWORK_EXT = ["png", "jpg", "jpeg"]
MB_CACHE_FILE = "mb_cache.json"
def load_mb_cache():
    if pl.Path(MB_CACHE_FILE).exists():
        return json.loads(pl.Path(MB_CACHE_FILE).read_text(encoding="utf-8"))
    return {}

def save_mb_cache(cache):
    pl.Path(MB_CACHE_FILE).write_text(
        json.dumps(cache, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

_mb_cache = load_mb_cache()
mb.set_useragent(
    "Col Tags Getter",
    "1.0",
    "1perna2312@gmail.com"
)

def main():
    try:
        print("=" * 21 + " Batch Audio Converter " + "=" * 21 + "\n")
        sample_rate = 48000
        channels = 2
        bitrate = "192k"
        output_format = "mp3"
        preserve_metadata = True
        convert_artwork = True
        file_renaming = True
        modify_metadata = True
        bypass_format = True

        while True:
            print("Settings:")
            print("-" * 23 + " AUDIO CONVERSION " + "-" * 24 + "\n")
            print(f"(1) Output Format: {output_format}")
            print(f"(2) Sample Rate: {sample_rate}")
            print(f"(3) Bitrate: {bitrate}")
            print(f"(4) Channels: {channels}")
            print(f"(5) Preserve Metadata: {preserve_metadata}")

            print("\n" + "-" * 26 + " METADATA " + "-" * 26 + "\n")
            
            print(f"(6) Convert Artwork: {convert_artwork}")
            print(f"(7) Auto File Renaming: {file_renaming}")
            print(f"(8) Change Metadata: {modify_metadata}\n")
            print("(9) Start Batch Conversion")
            print("(0) Exit\n")

            option = input("Select an option to change (0-9): ")
            if option == "0":
                exit()
            elif option == "1":
                output_format = getValidInput("Enter output format [mp3, flac, m4a, opus, ogg, wav, aac]: ", ac.AUDIO_FORMATS)
            elif option == "2":
                sample_rate = getValidInput("Enter sample rate [8000, 11025, 16000, 22050, 32000, 44100, 48000," \
                " 88200, 96000, 176000, 192000, 352000, 384000, 384000]: ", ac.SAMPLE_RATES)
            elif option == "3":
                bitrate = getValidInput("Enter bitrate [64k, 96k, 128k, 192k, 256k, 320k]: ", ac.BITRATES)
            elif option == "4":
                channels = getValidInput("Enter number of channels [1 (Mono), 2 (Stereo)]: ", ["1", "2"])
            elif option == "5":
                preserve_metadata = getValidInput("Keep metadata after conversion? (y/n): ", ["y", "n"]) == "y"
            elif option == "6":
                convert_artwork = getValidInput("Convert artwork in a 1000x1000 png? (y/n): ", ["y", "n"]) == "y"
            elif option == "7":
                file_renaming = getValidInput("Automatically rename files? (y/n): ", ["y", "n"]) == "y"
            elif option == "8":
                modify_metadata = getValidInput("Apply metadata changes and get new ones from MusicBrainz? (y/n): ", ["y", "n"]) == "y"
            elif option == "9":
                bypass_format = getValidInput("Do you wish to bypass conversion? Type \"y\" if you want just metadata work. (y/n): ", ["y", "n"]) == "y"
                settings = ac.AudioConverter(sample_rate=sample_rate, channels=channels, bitrate=bitrate,
                                            output_format=output_format, preserve_metadata=preserve_metadata)
                batchConvert(".", settings, convert_artwork=convert_artwork, file_renaming=file_renaming, modify_metadata=modify_metadata, bypass_conversion=bypass_format)
                print("Batch conversion finished.")
                exit()
            else:
                print("Invalid option.")
    except Exception as e:
        print(f"ERROR: {e}")
        traceback.print_exc()
    finally:
        input("Press Enter to exit...")

def getValidInput(prompt, valid_options):
    while True:
        user_input = input(prompt).lower()
        if user_input in valid_options:
            return user_input
        else:
            print(f"Invalid input. Please enter one of the following: {', '.join(valid_options)}")

def exit():
    input("Press any key to exit...")
    quit()

def batchConvert(dir, settings: ac, convert_artwork=False, file_renaming=False, modify_metadata=False, bypass_conversion=True):
    directory = pl.Path(dir).resolve()
    output_dir = pl.Path("Output")
    output_dir.mkdir(exist_ok=True)

    artwork_dir = pl.Path("Artwork")
    artwork_dir.mkdir(exist_ok=True)

    # Look for files to convert
    audio_files = []
    for ext in ac.AUDIO_FORMATS:
        audio_files.extend(pl.Path(directory).glob(f"*.{ext}"))
    if not audio_files:
        print("AUDIO CONVERTER: No compatible audio files found to work with.")
        return []
    
    artwork_files = []
    for file in audio_files:
        skip = False
        for ext in ARTWORK_EXT:
            searchFor = directory / (file.stem + f".{ext}")
            if searchFor.exists():
                artwork_files.append(searchFor)
                skip = True
                break
        if not skip:
            artwork_files.append(None)
    
    # Convert file by file
    for i, audio_file in enumerate(audio_files, start=0):
        #Define paths for audio files
        filename = audio_file.stem + f".{settings.output_format}"
        output_file = pl.Path(output_dir) / filename

        # AUDIO CONVERTER
        if not bypass_conversion:
            if output_file.exists():
                print(f"AUDIO CONVERTER: Skipping {audio_file.name} conversion (a similar file exists).")
            else:
                settings.converter(str(audio_file), str(output_file))
                print(f"AUDIO CONVERTER: {audio_file.name} converted to {settings.output_format}")
        else:
            if output_file.exists():
                print(f"AUDIO CONVERTER: Skipping {audio_file.name} conversion (a similar file exists).")
            else:
                audio_file.copy(output_file)
                print(f"AUDIO CONVERTER: {audio_file.name} copied to {output_file.parent}")

        
        if settings.preserve_metadata:
            # Get the correct tag type for each format
            tag_type, audio = loadMutagen(audio_file)

            # Artwork generator
            image_file = pl.Path(artwork_dir) / (artwork_files[i].name if artwork_files[i] else (audio_file.stem + ".png"))
            tempart_filename = image_file.stem + "_temp" + image_file.suffix.lower()
            tempimage_file = pl.Path(artwork_dir) / tempart_filename

            if artwork_files[i]:
                artwork_files[i].copy(image_file)
            else:
                if not artworkExtractor(tag_type, audio, image_file):
                    print("ARTWORK EXTRACTOR: Failed extracting thumbnail (might be missing)")

            # Transfrom artwork in 1000x1000 PNG if selected
            if convert_artwork:
                if image_file.exists():
                    art.convertArtwork(str(image_file), str(tempimage_file))
                    image_file.unlink()
                    tempimage_file.rename(image_file)
                    print(f"ARTWORK CONVERTER: Artwork {image_file.name} converted.")
                else:
                    print("ARTWORK CONVERTER: Could not find the image to convert.")    

            if modify_metadata:
                modifyMetadata(tag_type, audio, image_file, output_file)

            if file_renaming:
                renameFiles(tag_type, audio, output_file, image_file)

        total_files = len(audio_files)
        print(f"--- Progress: {i+1} / {total_files}: {audio_file.name} ({(i+1)/total_files*100:.1f}%)")
    
    save_mb_cache(_mb_cache)
    return list(pl.Path(output_dir).glob(f"*.{settings.output_format}"))

def artworkExtractor(tag_type, audio, image_path: pl.Path) -> bool:
    try:
        if tag_type == "id3":
            for tag in audio.getall("APIC"):
                if tag.type == 3:
                    image_path.write_bytes(tag.data)
                    return True
            return False
        elif tag_type == "mp4":
            covers = audio.tags.get("covr")
            if not covers:
                return False
            cover = covers[0]
            # Determine Extension
            if cover.imageformat == MP4Cover.FORMAT_PNG:
                image_path = image_path.with_suffix(".png")
            else:
                image_path = image_path.with_suffix(".jpg")

            image_path.write_bytes(bytes(cover))
            return True
        else:
            if not audio.pictures:
                return False
            for pic in audio.pictures:
                if pic.type == 3:
                    image_path.write_bytes(pic.data)
                    return True
            return False
    except Exception as e:
        print(f"ARTWORK EXTRACTOR: Extraction failed for {image_path.name}: {e}")
        return False

def safe_name(text, replacement=""):
        forbidden = r'\/:*?"<>|'
        return "".join(c if c not in forbidden else replacement for c in text).strip()

# METADATA MODIFIER
def modifyMetadata(tag_type, audio, image_path: pl.Path, save_file: pl.Path):

    if tag_type == "wav" or save_file.suffix.lower() == ".wav":
        print(f"METADATA MODIFIER: WAV does not support metadata. Skipping {save_file.name}")
        return
    elif tag_type == "id3":
        artist = audio.get("TPE1", TPE1(encoding=3, text="Unknown Artist")).text[0]
        title  = audio.get("TIT2", TIT2(encoding=3, text="Unknown Title")).text[0]
        album  = audio.get("TALB", TALB(encoding=3, text="Unknown Album")).text[0]
        date = audio.get("TDRC")
        year = str(date.text[0]) if date else ""
        genre = audio.get("TCON", TCON(encoding=3, text="")).text[0]
    elif tag_type == "mp4":
        artist = audio.get("\xa9ART", ["Unknown Artist"])[0]
        title  = audio.get("\xa9nam", ["Unknown Title"])[0] 
        album  = audio.get("\xa9alb", ["Unknown Album"])[0]
        genre  = audio.get("\xa9gen", [""])[0]
        year   = audio.get("\xa9day", [""])[0]
    else:
        artist = audio.get("artist", ["Unknown Artist"])[0]
        title  = audio.get("title", ["Unknown Title"])[0]
        album  = audio.get("album", ["Unknown Album"])[0]
        year   = audio.get("date", [""])[0]
        genre  = audio.get("genre", [""])[0]

    # ReplayGain Calculation
    rg = rga.analyze_replaygain(save_file)
    if rg:
        gain, peak = rg
    else:
        print("REPLAYGAIN: Failed to calculate.")

    # MusicBrainz and artwork replacement
    recording = mbLookupRec(artist, title)
    if recording:
        mb_album, mb_year, mb_genre = extractMetadata(recording)
        album = mb_album or album
        year  = mb_year or year
        genre = mb_genre or genre

        outtag_type, out_audio = loadMutagen(save_file)

        if outtag_type == "id3":
            out_audio.delall("TALB")
            out_audio.delall("TDRC")
            out_audio.delall("TCON")
            out_audio.delall("TXXX:REPLAYGAIN_TRACK_GAIN")
            out_audio.delall("TXXX:REPLAYGAIN_TRACK_PEAK")

            out_audio.add(TALB(encoding=3, text=album))
            if year:
                out_audio.add(TYER(encoding=3, text=year))
            if genre:
                out_audio.add(TCON(encoding=3, text=genre))

            if rg:
                out_audio.add(TXXX(encoding=3, desc="REPLAYGAIN_TRACK_GAIN", text=f"{gain} dB"))
                out_audio.add(TXXX(encoding=3, desc="REPLAYGAIN_TRACK_PEAK", text=str(peak)))

            if image_path.exists():
                with open(image_path, "rb") as img:
                    out_audio.delall("APIC")
                    out_audio.add(APIC(
                        encoding=3,
                        mime="image/png",
                        type=3,
                        desc="Cover",
                        data=img.read()
                    ))

            out_audio.save(v2_version=3)
        elif outtag_type == "mp4":
            out_audio["\xa9alb"] = album
            out_audio["\xa9gen"] = genre
            out_audio["\xa9day"] = year

            if rg:
                audio["----:com.apple.iTunes:replaygain_track_gain"] = [f"{gain} dB".encode()]
                audio["----:com.apple.iTunes:replaygain_track_peak"] = [str(peak).encode()]

            with open(image_path, "rb") as img:
                out_audio["covr"] = [MP4Cover(img.read(), imageformat=MP4Cover.FORMAT_PNG)]

            out_audio.save()
        else:
            out_audio["artist"] = artist
            out_audio["title"]  = title
            out_audio["album"]  = album
            if year:
                out_audio["date"] = year
            if genre:
                out_audio["genre"] = genre

            if rg:
                out_audio["REPLAYGAIN_TRACK_GAIN"] = f"{gain} dB"
                out_audio["REPLAYGAIN_TRACK_PEAK"] = str(peak)

            if image_path.exists():
                if outtag_type == "flac":
                    out_audio.clear_pictures()

                    pic = Picture()
                    pic.type = 3
                    pic.desc = "Cover"
                    pic.data = image_path.read_bytes()
                    pic.mime = "image/png"

                    out_audio.add_picture(pic)
                else:
                    with open(image_path, "rb") as img:
                        data = img.read()

                    pic = Picture()
                    pic.type = 3
                    pic.desc = "Cover"
                    pic.data = data
                    pic.mime = "image/png"

                    # Base64 encoding
                    pic_data = pic.write()
                    enc_data = base64.b64encode(pic_data)
                    vcomm_val = enc_data.decode("ascii")

                    out_audio["metadata_block_picture"] = [vcomm_val]

            out_audio.save()

def renameFiles(tag_type, audio, audio_path: pl.Path, image_path: pl.Path):
    if tag_type == "wav":
        print(f"FILE RENAMING: WAV cannot be renamed due to unsupported metadata. Skipping {audio_path.name}")
        return
    elif tag_type == "id3":
        artist = audio.get("TPE1", TPE1(encoding=3, text="Unknown Artist")).text[0]
        title  = audio.get("TIT2", TIT2(encoding=3, text="Unknown Title")).text[0]
    elif tag_type == "mp4":
        artist = audio.get("\xa9ART")[0]
        title  = audio.get("\xa9nam")[0] 
    else:
        artist = audio.get("artist", ["Unknown Artist"])[0]
        title  = audio.get("title", ["Unknown Title"])[0]

    # Clear names from junk unsupported by os
    artist = safe_name(artist).replace(" - Topic", "")
    title  = safe_name(title)

    new_audio = audio_path.parent / f"{artist} - {title}{audio_path.suffix.lower()}"
    new_art   = image_path.parent / f"{artist} - {title}.png"

    if audio_path.exists() and not new_audio.exists():
        audio_path.rename(new_audio)
        print(f"FILE RENAMING: Audio {audio_path.name} renamed to {new_audio.name}")
    else:
        print(f"FILE RENAMING: Audio named {new_audio.name} already exists! Skipped renaming.")

    if image_path.exists() and not new_art.exists():
        image_path.rename(new_art)
        print(f"FILE RENAMING: Art {image_path.name} renamed to {new_art.name}")
    else:
        print(f"FILE RENAMING: Art named {new_art.name} already exists! Skipped renaming.")

def loadMutagen(filepath: pl.Path):
    ext = filepath.suffix.lower()

    if ext == ".mp3":
        try:
            audio = ID3(filepath)
        except ID3NoHeaderError:
            audio = ID3()
            audio.filename = str(filepath)
        return "id3", audio
    elif ext == ".flac":
        return "flac", FLAC(filepath)
    elif ext == ".opus":
        return "opus", OggOpus(filepath)
    elif ext == ".ogg":
        return "ogg", OggVorbis(filepath)
    elif ext == ".m4a":
        return "mp4", MP4(filepath)
    elif ext == ".aac":
        return "mp4", MP4(filepath)
    elif ext == ".wav":
        return "wav", None  # skip metadata
    else:
        raise ValueError(f"loadMutagen - Unsupported format: {ext}")

def mbLookupRec(artist, title):
    key = f"{artist.lower()}|{title.lower()}"

    if key in _mb_cache:
        print("MusicBrainz: Data found in cache!")
        return _mb_cache[key]
    
    try:
        result = mb.search_recordings(
            recording=title,
            artist=artist,
            limit=5
        )
    except Exception:
        print("MusicBrainz: Failed to search recordings.")
        return None
    
    if not result["recording-list"]:
        print("MusicBrainz: No record results.")
        return None
    
    best = max(result["recording-list"],
        key=lambda r: int(r.get("score", 0)))
    
    _mb_cache[key] = best
    save_mb_cache(_mb_cache)
    print("MusicBrainz: Data searched and saved in cache.")
    return best

def extractMetadata(recording):
    album = None
    year = None
    genre = None

    # Album and year
    if "release-list" in recording:
        releases = recording["release-list"]

        # Prefer official albums
        releases.sort(key=lambda r: (
            r.get("status") != "Official",
            r.get("primary-type") != "Album"
        ))

        release = releases[0]
        album = release.get("title")
        date = release.get("date")
        if date:
            year = date[:4]

    # For Genre
    if "tag-list" in recording:
        tags = sorted(
            recording["tag-list"],
            key=lambda t: int(t.get("count", 0)),
            reverse=True
        )
        if tags:
            genre = tags[0]["name"].title()

    return album, year, genre
   
if __name__ == "__main__":
    main()
