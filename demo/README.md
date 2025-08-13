# Demo of StepFun-Prover-Preview

We provide a demo to show how to use our multi-turn model by combining Lean4-repl and vllm.


## Setup

### Install requirements
```bash
pip install -r requirements.txt
```

### Install and Modify Lean4-repl

The original implementation of REPL(https://github.com/leanprover-community/repl/tree/master) has OOM issue when trying to run large amounts of commands on a single Lean4-repl instance (see more details in https://github.com/leanprover-community/repl/issues/77#issuecomment-2822440029). So we modify the REPL to enable us to repeatedly using the same Lean4-repl instance efficiently, which is crucial in our unlimited multi-turn scenario.

- Install Lean4 following https://leanprover-community.github.io/install/linux.html

- Install Lean4-repl. Note the version is `v4.20.0-rc5` in our experiments. So get the repo by 
  ```bash
  git clone -b bump_to_v4.20.1 https://github.com/leanprover-community/repl.git
  ```

- Place `leanprover/lean4:v4.20.0-rc5` in `repl
/lean-toolchain`

- Replace `repl/REPL/Main.lean` in `repl` by `Stepfun-Prover-Preview/demo/Main.lean`

- Compile mathlib by adding 
  ```bash
  [[require]]
  name = "mathlib"
  scope = "leanprover-community"
  rev = "v4.20.0-rc5"
  ```
  in `repl/lakefile.toml`, then run `lake update`

### Download the models (optional)

## Test a case

Fill in your `REPL_DIR`, `MODEL_DIR`, and `Formal_problem` in `Stepfun-Prover-Preview/demo/interact_with_lean4repl.py`

```python
...
REPL_DIR = "/your/path/to/repl"
MODEL_DIR = "/your/path/to/model"

formal_problem = """
import Mathlib

theorem your_theorem xxxx
""".strip()
...
```
then run
```bash
cd Stepfun-Prover-Preview/demo
python interact_with_lean4repl.py
```
