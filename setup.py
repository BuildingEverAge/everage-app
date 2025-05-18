import os
import subprocess
import sys
import json

def install_packages():
    print("📦 Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet",
                           "streamlit", "openai", "matplotlib", "pandas", "seaborn", "scikit-learn", "fpdf"])

def create_secrets(api_key):
    streamlit_dir = ".streamlit"
    if not os.path.exists(streamlit_dir):
        os.makedirs(streamlit_dir)
    secrets_path = os.path.join(streamlit_dir, "secrets.toml")
    with open(secrets_path, "w") as f:
        f.write(f"""[openai]
api_key = "{api_key}"
""")
    print(f"✅ API key saved to {secrets_path}")

def create_data_file():
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    data_path = os.path.join(data_dir, "user_data.json")
    if not os.path.exists(data_path):
        with open(data_path, "w") as f:
            json.dump({}, f)
        print(f"📁 Created data storage: {data_path}")
    else:
        print(f"📁 Data file already exists: {data_path}")

def main():
    install_packages()
    create_data_file()
    api_key = input("🔑 Paste your OpenAI API Key (starts with 'sk-'): ").strip()
    if not api_key.startswith("sk-"):
        print("❌ That doesn't look like a valid OpenAI API key. Please try again.")
        return
    create_secrets(api_key)
    run_app = input("🚀 Do you want to run the Streamlit app now? (y/n): ").strip().lower()
    if run_app == "y":
        print("▶️ Running Streamlit app...")
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
    else:
        print("✅ Setup complete! You can run your app anytime using:\n   streamlit run app.py")

if __name__ == "__main__":
    main()
