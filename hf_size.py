from huggingface_hub import HfApi
api = HfApi()
info = api.dataset_info("Angelakeke/DeepRare", files_metadata=True)

total_size = sum(f.size for f in info.siblings if f.size is not None)
print(f"Total size: {total_size / (1024 * 1024 * 1024):.2f} GB")
for f in info.siblings:
    if f.size:
        print(f" - {f.rfilename}: {f.size / (1024 * 1024):.2f} MB")
