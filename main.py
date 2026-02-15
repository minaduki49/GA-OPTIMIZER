from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
import threading, io, base64, os, uuid
import ga_engine 
from ga_engine import evolve

app = FastAPI()

# ---------- PATHS & UTILS ----------
BASE_DIR = os.path.abspath(os.getcwd())
OUTPUT_ROOT = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUT_ROOT, exist_ok=True)
app.mount("/outputs", StaticFiles(directory=OUTPUT_ROOT), name="outputs")

sessions = {}

def img_to_base64(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

def run_ga(session_id: str, prompt: str, negative_prompt: str, mutation_rate: float):
    sess = sessions[session_id]
    out_dir = os.path.join(OUTPUT_ROOT, f"{session_id}_{uuid.uuid4().hex[:6]}")
    os.makedirs(out_dir, exist_ok=True)
    sess["output_dir"] = out_dir

    def callback(img, score, gene, generation):
        try:
            uid = uuid.uuid4().hex[:8]
            filename = f"gen{generation:04}_{uid}_score{int(score)}.png"
            img.save(os.path.join(out_dir, filename))
            sess["current_img"] = img_to_base64(img)
            if score > sess.get("best_score", float("-inf")):
                sess["best_score"] = score
                sess["best_img"] = sess["current_img"]
            return True
        except: return False

    try:
        # ga_engine.py の evolve を呼び出す
        evolve(prompt, negative_prompt, mutation_rate, callback)
    except Exception as e:
        print(f"Error in evolve: {e}")
    finally: 
        sess["running"] = False

# ---------- UI ----------
HTML_UI = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>GA OPTIMIZER FREE</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>
  body { background-color: #0a0a0a; color: #ffffff; font-family: sans-serif; }
  .input-field { background-color: #000000; border: 2px solid #333333; color: #ffffff; font-weight: bold; border-radius: 8px; padding: 12px; width: 100%; }
  .input-field:focus { border-color: #3b82f6; outline: none; }
  .input-field:disabled { opacity: 0.6; cursor: not-allowed; border-color: #222; background-color: #111; }
  .label-text { color: #ffffff; font-weight: 800; font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px; display: block; }
  .evolving { background: linear-gradient(90deg, #1d4ed8, #60a5fa, #1d4ed8); background-size: 200% 100%; animation: move 2s linear infinite; }
  @keyframes move { 0%{background-position:0% 0%} 100%{background-position:-200% 0%} }
</style>
</head>
<body class="p-8">

<div id="app" class="max-w-5xl mx-auto space-y-8">
  <div class="flex justify-between items-center border-b-4 border-zinc-800 pb-4">
    <h2 class="text-5xl font-black italic tracking-tighter">GA OPTIMIZER <span class="text-green-500">FREE</span></h2>
    <div id="status" class="bg-zinc-800 px-4 py-2 rounded-full font-bold text-xs tracking-widest">READY</div>
  </div>

  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
    <div>
      <label class="label-text">Positive Prompt</label>
      <textarea id="prompt" class="input-field h-32">high quality, cinematic lighting, masterpiece</textarea>
    </div>
    <div>
      <label class="label-text text-red-500">Negative Prompt</label>
      <textarea id="neg_prompt" class="input-field h-32">bad anatomy, deformed, disfigured, mutated, extra limbs, ugly, blurred, low quality, worst quality</textarea>
    </div>
  </div>

  <div class="grid grid-cols-3 gap-6">
    <div class="bg-zinc-900 p-6 rounded-2xl border-2 border-zinc-800 text-center">
      <label class="label-text text-zinc-500">Generations (Fixed)</label>
      <div class="text-2xl font-bold py-2">10</div>
    </div>
    <div class="bg-zinc-900 p-6 rounded-2xl border-2 border-zinc-800 text-center">
      <label class="label-text text-zinc-500">Pop Size (Fixed)</label>
      <div class="text-2xl font-bold py-2">5</div>
    </div>
    <div class="bg-zinc-900 p-6 rounded-2xl border-2 border-zinc-800 text-center">
      <label class="label-text">Mutate Rate</label>
      <input id="mutation_rate" type="number" step="0.1" value="0.3" class="input-field text-2xl text-center">
    </div>
  </div>

  <button id="btn" onclick="start()" class="w-full bg-blue-600 text-white font-black py-6 rounded-2xl text-3xl shadow-2xl hover:bg-blue-500 active:scale-95 transition-all">START EVOLUTION</button>

  <div class="grid grid-cols-2 gap-12 pt-8">
    <div class="space-y-4">
      <p class="text-center font-black text-zinc-500 text-sm tracking-widest uppercase">Current Genome</p>
      <img id="current" class="w-full aspect-square bg-black rounded-3xl border-4 border-zinc-800">
    </div>
    <div class="space-y-4">
      <p class="text-center font-black text-blue-500 text-sm tracking-widest uppercase">Best Individual</p>
      <img id="best" class="w-full aspect-square bg-black rounded-3xl border-8 border-blue-600">
    </div>
  </div>
</div>

<script>
let sid = "free-" + Math.random().toString(36).slice(2);

async function start() {
  const btn = document.getElementById("btn");
  const fields = ["prompt", "neg_prompt", "mutation_rate"];
  
  fields.forEach(id => document.getElementById(id).disabled = true);
  btn.disabled = true;
  btn.classList.add("evolving");
  btn.innerText = "EVOLVING...";
  document.getElementById("status").innerText = "RUNNING";

  const res = await fetch("/start", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
      session_id: sid,
      prompt: document.getElementById("prompt").value,
      negative_prompt: document.getElementById("neg_prompt").value, 
      mutation_rate: parseFloat(document.getElementById("mutation_rate").value)
    })
  });

  if(!res.ok) {
    alert("SERVER ERROR");
    stopUI();
  }
}

function stopUI() {
    const btn = document.getElementById("btn");
    btn.disabled = false;
    btn.classList.remove("evolving");
    btn.innerText = "START EVOLUTION";
    document.getElementById("status").innerText = "FINISHED";
    ["prompt", "neg_prompt", "mutation_rate"].forEach(id => document.getElementById(id).disabled = false);
}

async function update() {
  const r = await fetch("/preview?session_id=" + sid);
  if(r.status !== 200) return;
  const d = await r.json();
  if(d.current) document.getElementById("current").src = d.current;
  if(d.best) document.getElementById("best").src = d.best;
  if(d.stopped && document.getElementById("btn").disabled) {
    stopUI();
  }
}
setInterval(update, 1500);
</script>
</body>
</html>
"""

@app.get("/")
async def index(): return HTMLResponse(HTML_UI)

@app.post("/start")
async def start_api(data: dict):
    sid = data["session_id"]
    sessions[sid] = {"running": True, "current_img": None, "best_img": None, "best_score": float("-inf")}
    
    threading.Thread(
        target=run_ga, 
        args=(sid, data["prompt"], data.get("negative_prompt", ""), data.get("mutation_rate", 0.3)), 
        daemon=True
    ).start()
    return {"status": "ok"}

@app.get("/preview")
async def preview(session_id: str):
    s = sessions.get(session_id, {})
    return JSONResponse({"current": s.get("current_img"), "best": s.get("best_img"), "stopped": not s.get("running", True)})