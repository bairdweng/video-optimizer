from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "mosaicml/mpt-7b-chat"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
