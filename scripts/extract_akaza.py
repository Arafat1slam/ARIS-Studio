import sys, os
sys.path.insert(0, os.path.abspath('scripts'))
from scenepacks_fetcher import load_cache, extract_scenes_from_stream

cache = load_cache()
akaza_url = cache.get('5641', {}).get('stream_url')

akaza_cuts = [
    (45.0, 2.5),   # Compass deployment
    (95.0, 2.5),   # Glare / sinister grin
    (150.0, 2.5),  # Fast fist rush
    (240.0, 2.5),  # Air type punch impact
    (380.0, 2.5),  # Close-up fight strike
    (520.0, 2.5),  # Blue compass glowing floor
    (680.0, 2.5),  # Fierce clash
    (810.0, 2.5)   # Final annihilation punch
]

print("Extracting 8 Akaza action shots from scenepack...")
clips = extract_scenes_from_stream(akaza_url, akaza_cuts, output_prefix="akaza_action")
print(f"Extracted {len(clips)} Akaza shots!")
