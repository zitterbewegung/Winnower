/* Web Worker for the interactive reproduction demo.
 *
 * Hosts Pyodide (WebAssembly CPython), loads the real relative_symmetry_repair
 * package from winnower_src.zip, and runs bootstrap.run_repro on request,
 * streaming progress back to the page. Runs off the main thread so the UI
 * stays responsive during scans.
 */

"use strict";

const PYODIDE_VERSION = "0.26.4";
const PYODIDE_INDEX_URL = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/`;

let initPromise = null;
let lz4Loaded = false;

function post(type, payload) {
  self.postMessage({ type, payload });
}

async function init() {
  post("status", "Downloading the Python runtime (~15 MB, cached after the first visit)…");
  importScripts(PYODIDE_INDEX_URL + "pyodide.js");
  self.pyodide = await loadPyodide({ indexURL: PYODIDE_INDEX_URL });

  post("status", "Loading numpy, scipy, pandas…");
  await pyodide.loadPackage(["numpy", "scipy", "pandas"]);
  try {
    await pyodide.loadPackage("lz4");
    lz4Loaded = true;
  } catch (err) {
    lz4Loaded = false; // bootstrap falls back to its zlib shim
  }

  post("status", "Fetching the Winnower source…");
  const resp = await fetch("winnower_src.zip");
  if (!resp.ok) {
    throw new Error(`Could not fetch winnower_src.zip (HTTP ${resp.status})`);
  }
  pyodide.unpackArchive(await resp.arrayBuffer(), "zip");

  post("status", "Importing the pipeline…");
  pyodide.runPython(`
import sys
if '.' not in sys.path:
    sys.path.insert(0, '.')
import bootstrap
import base64, json

def _run_encoded(family, rule, seed, horizon, progress):
    res = bootstrap.run_repro(family, rule, int(seed), int(horizon), progress=progress)
    for img in res['images'].values():
        img['data'] = base64.b64encode(img['data']).decode()
    return json.dumps(res)
`);
  post("env", {
    pyodide: PYODIDE_VERSION,
    python: pyodide.runPython("import sys; sys.version.split()[0]"),
    numpy: pyodide.runPython("import numpy; numpy.__version__"),
    scipy: pyodide.runPython("import scipy; scipy.__version__"),
    pandas: pyodide.runPython("import pandas; pandas.__version__"),
    lz4: lz4Loaded,
  });
}

self.onmessage = async (event) => {
  const msg = event.data;
  try {
    if (msg.type === "init") {
      if (!initPromise) initPromise = init();
      await initPromise;
      post("ready");
      return;
    }
    if (msg.type === "run") {
      if (!initPromise) initPromise = init();
      await initPromise;
      const progress = (frac, text) => post("progress", { frac, text });
      pyodide.globals.set("js_progress", progress);
      pyodide.globals.set("p_family", msg.family);
      pyodide.globals.set("p_rule", msg.rule);
      pyodide.globals.set("p_seed", msg.seed);
      pyodide.globals.set("p_horizon", msg.horizon);
      const resultJson = pyodide.runPython(
        "_run_encoded(p_family, p_rule, p_seed, p_horizon, js_progress)"
      );
      post("result", JSON.parse(resultJson));
      return;
    }
  } catch (err) {
    post("error", String((err && err.message) || err));
  }
};
