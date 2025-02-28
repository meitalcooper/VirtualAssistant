import whisper

# List of all available models
models = ['tiny', 'base', 'small', 'medium', 'large', 'turbo']

# Download each model
for model_name in models:
    print(f"Downloading {model_name} model...")
    whisper.load_model(model_name)
    print(f"Downloaded {model_name} model successfully")