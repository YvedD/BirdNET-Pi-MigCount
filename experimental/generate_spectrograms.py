from experimental.spectrogram_generator import load_config, generate_for_directory, CONFIG_PATH

def main():
    cfg = load_config(CONFIG_PATH)
    results = generate_for_directory(cfg.input_directory, cfg.output_directory, cfg)
    print(f"Generated {len(results)} spectrogram(s)")

if __name__ == "__main__":
    main()
