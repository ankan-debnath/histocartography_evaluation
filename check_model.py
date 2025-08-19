import torch

model_path = '/usr/local/lib/python3.8/dist-packages/histocartography/preprocessing/../../checkpoints/pannuke.pt'

try:
    data = torch.load(model_path)
    print("✅ Valid PyTorch model file.")
    print(f"Loaded object type: {type(data)}")
except Exception as e:
    print("❌ Not a valid PyTorch model file.")
    print("Error:", e)
