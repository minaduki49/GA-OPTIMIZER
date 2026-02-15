# GA OPTIMIZER (Pro / Free)

GA OPTIMIZER is an optimization tool that utilizes Genetic Algorithms (GA) to automatically "evolve" Stable Diffusion prompts, helping you pursue the ideal generated image.

## 🚀 Overview

Based on a user-provided prompt, the system generates a "population" (combinations of prompts) and iteratively evaluates them using CLIP model scoring. By repeating this process, the system produces higher-quality images with each passing generation.

### Key Features
1. **Generation**: Generates images using Stable Diffusion (sdxl-turbo).
2. **Evaluation**: Uses CLIP (ViT-B/32) to score the alignment between the image and the prompt, as well as the level of detail.
3. **Evolution**: Selects high-scoring individuals for Crossover and Mutation to create the next generation.

## 🛠 Setup

### 1. Environment
* **OS**: Windows / Linux / macOS
* **Python**: 3.10 recommended (for `.pyc` compatibility and stability)
* **GPU**: NVIDIA GPU (CUDA) recommended

### 2. Installation
Run the following commands in your terminal (adjust based on your specific environment):

```bash
pip install fastapi uvicorn python-multipart Pillow numpy torch diffusers transformers accelerate
pip install git+[https://github.com/openai/CLIP.git](https://github.com/openai/CLIP.git)

💻 How to Use
1. Launch the Application
Run the following command in the project root directory:

Bash
python run_app.py
Once launched, your browser will automatically open to http://127.0.0.1:8000.

2. Run the Evolution Process
Pro Version: Enter and activate your license key (e.g., GA-20261231-USER-XXXX) at startup.

Positive Prompt: Enter core keywords for what you want to generate.

Negative Prompt: Enter elements you want to exclude.

Parameters: Adjust Generations, Population Size (Pop Size), and Mutation Rate, then click "START EVOLUTION".

⚠️ Notes
License Expiry: Pro license keys have an embedded expiration date. The software will not function if the current date exceeds the expiration date.

Model Loading: The first launch requires downloading Stable Diffusion and CLIP models (several GB), which may take some time.
