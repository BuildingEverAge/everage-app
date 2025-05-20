import os

# Create .streamlit directory if it doesn't exist
os.makedirs(".streamlit", exist_ok=True)

# Write the config.toml content
config_content = """
[theme]
primaryColor = "#16a085"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"
"""

with open(".streamlit/config.toml", "w") as f:
    f.write(config_content.strip())

print("✅ .streamlit/config.toml has been created successfully.")
