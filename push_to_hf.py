import os
from huggingface_hub import HfApi

api = HfApi()

try:
    print("Uploading folder to Vijay-1807/email-triage-env...")
    api.upload_folder(
        folder_path=".",
        repo_id="Vijay-1807/email-triage-env",
        repo_type="space",
        ignore_patterns=[".git", "__pycache__", ".venv", "venv", "uv.lock", "outputs", "push_to_hf.py"],
        commit_message="Fix Phase 2 evaluator scores out of range issue"
    )
    print("✅ Successfully pushed to Hugging Face Space!")
except Exception as e:
    print(f"❌ Error uploading to HF: {e}")
    print("Please make sure you are logged in using `huggingface-cli login` or an HF_TOKEN env variable is set.")
