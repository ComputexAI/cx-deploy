from transformers import AutoConfig, AutoModelForCausalLM

TOKEN = "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"

config = AutoConfig.from_pretrained(
    "bigcode/starcoder", trust_remote_code=True, use_auth_token=TOKEN
)
