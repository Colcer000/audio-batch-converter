import ffmpeg as ff

def convertArtwork(input_path, output_path):
    try:
        (
            ff.input(input_path)
            .filter("scale", 1000, 1000, force_original_aspect_ratio="increase")
            .filter('crop', 1000, 1000)
            .output(output_path, vframes=1, format="image2")
            .run(overwrite_output=True, capture_stderr=True)
        )
    except ff.Error as e:
        print(f"Error converting artwork: {e.stderr.decode()}")