from vllm import LLM, SamplingParams
from transformers import AutoTokenizer
import json
import time
from IPython import embed
from tqdm import tqdm

from pylean import LeanServer


REPL_DIR = "/data/projects/repl"
MODEL_DIR = "/mnt/jfs-wrs-step2-save/opensource_model/Stepfun-Prover-Preview-32B"

formal_problem = """
import Mathlib

theorem test_theorem (x y z : ℝ) (hx : 0 < x) (hy : 0 < y) (hz : 0 < z) :
    (x^2 - z^2) / (y + z) + (y^2 - x^2) / (z + x) + (z^2 - y^2) / (x + y) ≥ 0 := by
""".strip()

lean_server = LeanServer(REPL_DIR, import_timeout=120)
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)

system_prompt = "You will be given an unsolved Lean 4 problem. Think carefully and work towards a solution. At any point, you may use the Lean 4 REPL to check your progress by enclosing your partial solution between <sketch> and </sketch>. The REPL feedback will be provided between <REPL> and </REPL>. Continue this process as needed until you arrive at a complete and correct solution."

user_prompt = f"```lean4\n{formal_problem}\n```"

dialog = [
  {"role": "system", "content": system_prompt},
  {"role": "user", "content": user_prompt}
] 

prompt = tokenizer.apply_chat_template(dialog, tokenize=False, add_generation_prompt=True)

model = LLM(
  MODEL_DIR, 
  tensor_parallel_size=8 # 8 for 32B, 4 for 7B
)

sampling_params = SamplingParams(
    temperature=0.999,
    top_p=0.95,
    top_k=-1,
    max_tokens=16384,
    stop_token_ids=[151643, 151666], # <｜end▁of▁sentence｜>, </sketch>
    include_stop_str_in_output=True,
)

max_seq_len = 20480

turn_num = 0

while True:

  response = model.generate(prompt, sampling_params)
  response_text = response[0].outputs[0].text
  prompt += response_text

  # if the response is not stopped normally
  if response[0].outputs[0].finish_reason != "stop":
    print("The response is not stopped normally, break")
    break

  # if the all tokens exceed the max_seq_len
  elif len(response[0].prompt_token_ids) + len(response[0].outputs[0].token_ids) >= max_seq_len:
    print("Exceed the max_seq_len, break")
    break

  # if the response is stopped by </sketch>, send repl
  elif response[0].outputs[0].stop_reason == 151666:
    if "<sketch>" not in response_text:
      print("Format error, break")
      break

    sketch_start = response_text.find('<sketch>') + len('<sketch>')
    sketch_end = response_text.find('</sketch>')

    # remove the `import Mathlib` because Mathlib is already imported
    sketch = response_text[sketch_start:sketch_end].replace("import Mathlib", "").strip()

    start_time = time.time()
    repl_output = lean_server.run_sketch(sketch, timeout=60, auto_check_and_reinitialize=True, memory_limit=15 * 1024) # 60s timeout, 15GB memory limit
    end_time = time.time()
    elapsed_time = end_time - start_time

    if repl_output is None:
      repl_text = f"repl cannot return status in {elapsed_time} seconds!"
    else:
      repl_text = json.dumps(repl_output, ensure_ascii=False)

    prompt += f"\n<REPL>\n{repl_text}\n</REPL>"
    turn_num += 1

  elif response[0].outputs[0].stop_reason is None : # Finish think and summary, break
    print("Finish think and summary, break")
    break

print(prompt)

lean_server._close()


      




  








