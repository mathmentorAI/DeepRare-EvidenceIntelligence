import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
from transformers import AutoModel, AutoTokenizer, AutoModelForSequenceClassification

print("Downloading BioLORD-2023-C...")
AutoTokenizer.from_pretrained('FremyCompany/BioLORD-2023-C')
AutoModel.from_pretrained('FremyCompany/BioLORD-2023-C')

print("Downloading MedCPT-Cross-Encoder...")
AutoTokenizer.from_pretrained('ncbi/MedCPT-Cross-Encoder')
AutoModelForSequenceClassification.from_pretrained('ncbi/MedCPT-Cross-Encoder')

print("Models successfully downloaded and cached.")
