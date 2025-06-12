# TODO: ONNXRuntime and NumPy Compatibility

To properly wire up onnxruntime with numpy compatibility for your project — especially given its use in embedding functions and model inference — here’s what you need to do practically and cleanly:

---

✅ Step-by-step Fix for onnxruntime + numpy Compatibility

1. Uncomment ONNXRuntime in pyproject.toml

In ./pyproject.toml, change:

#"onnxruntime==1.22.0",

To:

onnxruntime==1.22.0

This ensures your project explicitly pins to onnxruntime 1.22.0.


---

2. Lock Compatible NumPy Version

ONNXRuntime has strict NumPy compatibility. As of ONNXRuntime 1.22.0, the safest NumPy is:

numpy==1.26.4

This matches what you have in your test_crew_emits_end_task_event.yaml, so you're good.

To enforce it, ensure numpy==1.26.4 is pinned either in:

pyproject.toml

or in your requirements.txt (if you're using that alongside)


---

3. Purge and Reinstall (Important)

If you're working in a virtual environment, clear any conflicting cache:

pip uninstall onnxruntime numpy -y
pip cache purge
pip install onnxruntime==1.22.0 numpy==1.26.4

Alternatively, with uv or pip-tools, re-lock the dependencies:

uv pip compile --upgrade
uv pip sync

Or if you use poetry:

poetry lock --no-update
poetry install


---

4. Verify Import and Compatibility

Run a quick check in Python:

import numpy
import onnxruntime
print(numpy.__version__)
print(onnxruntime.__version__)

Make sure there are no DLL load failed or binary incompatibility errors.


---

5. Double-check Runtime Compatibility (e.g. aarch64, etc.)

If you're on a platform like Termux or aarch64, make sure the installed .whl for onnxruntime matches your Python and architecture:

CPython version (e.g., cp310)

Platform (e.g., manylinux_2_27_aarch64 or win_amd64)


Your lockfile URLs indicate full coverage across platforms, so unless you're cross-compiling, you should be fine.


---

🧠 Summary

Package	Version	Reason

onnxruntime	1.22.0	Explicitly pinned, tested in lock
numpy	1.26.4	Compatible with ORT 1.22.0


Make the changes, recompile your lockfile, and reinstall dependencies. If errors persist on import onnxruntime, provide the full traceback and system architecture.
