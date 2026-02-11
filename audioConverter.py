import ffmpeg

AUDIO_FORMATS = ["mp3", "flac", "m4a", "opus", "ogg", "wav", "aac"]
SAMPLE_RATES = [8000, 11025, 16000, 22050, 32000, 44100, 48000, 88200, 96000, 176000, 192000, 352000, 384000, 384000]
BITRATES = ["64k", "96k", "128k", "192k", "256k", "320k"]

class AudioConverter:
    def __init__(self, sample_rate=48000, channels=2, bitrate="192k",
                 output_format="mp3", acodec=None, preserve_metadata=True):
        self.sample_rate = sample_rate
        self.channels = channels
        self.bitrate = bitrate
        self.output_format = output_format
        self.acodec = acodec
        self.preserve_metadata = preserve_metadata

        # Validate parameters
        if self.acodec is None:
            codec_map = {
                "mp3": "libmp3lame",
                "flac": "flac",
                "wav": "pcm_s16le",
                "aac": "aac",
                "opus": "libopus",
                "ogg": "libvorbis",
                "m4a": "aac",
            }
            self.acodec = codec_map.get(self.output_format, "pcm_s16le")
        if self.output_format not in AUDIO_FORMATS:
            self.output_format = "wav"  # Default to WAV
            print(f"Unsupported output format specified. Defaulting to WAV.")
        if self.sample_rate <= 0 or self.sample_rate not in SAMPLE_RATES:
            self.sample_rate = 48000  # Default sample rate
            print(f"Invalid sample rate specified. Defaulting to 48000 Hz.")
        if self.channels not in [1, 2]:
            self.channels = 2  # Default to stereo
            print(f"Invalid channel count specified. Defaulting to stereo (2 channels).")
        if self.bitrate not in BITRATES:
            self.bitrate = "192k"  # Default bitrate
            print(f"Invalid bitrate specified. Defaulting to 192 kbps.")

    def converter(self, input_path, output_path):
        try:
            m4aShit = {
                "m4a": "mp4"
            }.get(self.output_format, self.output_format)
            output_kwargs = {
                "ar": self.sample_rate,
                "ac": self.channels,
                "format": m4aShit,
                "acodec": self.acodec,
                "audio_bitrate": self.bitrate,
                "loglevel": "error",
            }
            if self.output_format in ("aac", "m4a"):
                output_kwargs.pop("b:a", None)
                output_kwargs["q:a"] = 2  # 0 (Best) : 5 (Worst)

            if not self.preserve_metadata:
                output_kwargs["map_metadata"] = "-1"
            stream = (
                ffmpeg
                .input(input_path)
                .output(output_path, vn=None, **{"map":"0:a:0"}, **output_kwargs) 
            )
            print(ffmpeg.compile(stream))
            stream.run(overwrite_output=True, capture_stderr=True)

        except ffmpeg.Error as e:
            print(f"FFmpeg error converting {input_path}: {e.stderr.decode()}")
            return False
        except Exception as e:
            print(f"Error converting {input_path}: {e}")
            return False
        return True