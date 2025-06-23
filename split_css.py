import os
import re

# File paths
input_file = "static/index.css"
output_dir = "static/css"

# Create output directory
os.makedirs(output_dir, exist_ok=True)

# Define file sections and their identifiers
sections = {
    "index.css": [":root", "body", ".main-container"],
    "typography.css": [".header-title", ".header-subtitle", ".stats-number", ".stats-label"],
    "buttons.css": [".btn", ".btn-primary", ".btn-outline"],
    "cards.css": [".agent-card", ".stats-card", ".summary-result", ".history-card", ".history-item"],
    "form.css": [".form-control", ".progress-bar", ".progress-fill", ".text-counter"],
    "animations.css": ["@keyframes", ".fade-in", ".pulse", ".loading-dots"],
    "responsive.css": ["@media (max-width"],
    "accessibility.css": ["@media (prefers-reduced-motion)", ".visually-hidden"],
    "markdown.css": [".markdown-output"]
}

# Read the full index.css content
with open(input_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Buffers for each output file
buffers = {filename: [] for filename in sections}

# Add everything else to base.css by default
buffers.setdefault("base.css", [])

# Line-by-line filter
for line in lines:
    matched = False
    for filename, triggers in sections.items():
        if any(trigger in line for trigger in triggers):
            buffers[filename].append(line)
            matched = True
            break
    if not matched:
        buffers["index.css"].append(line)  # Dump unmatched into original

# Write each CSS module
for filename, content in buffers.items():
    if content:
        path = os.path.join(output_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(content)
        print(f"✅ Written: {path}")

print("\n🎉 CSS split completed into static/css/")
