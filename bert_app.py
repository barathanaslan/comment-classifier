import sys
import torch
import numpy as np
from transformers import BertTokenizer
import re
import pickle
import io

# !pip install torch
# !pip install tensorflow
# !pip install keras

class CPU_Unpickler(pickle.Unpickler):
    """
    Custom Unpickler to load PyTorch models onto the CPU.
    """
    def find_class(self, module, name):
        if module == 'torch.storage' and name == '_load_from_bytes':
            return lambda b: torch.load(io.BytesIO(b), map_location='cpu')
        else:
            return super().find_class(module, name)

try:
    # Load the BERT model from a pickle file
    my_model = CPU_Unpickler(open("bert_text_classification_model.pickle", 'rb')).load()
    tokenizer = BertTokenizer.from_pretrained(
        'dbmdz/bert-base-turkish-128k-uncased',
        do_lower_case=True
    )
    # Use GPU if available, otherwise use CPU
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    token_id = []
    attention_masks = []
except Exception as e:
    print(f"Error while unpickling bert model: {e}")
    sys.exit(1)

# Reload the model and tokenizer to ensure they are available
my_model = CPU_Unpickler(open("bert_text_classification_model.pickle", 'rb')).load()

tokenizer = BertTokenizer.from_pretrained(
    'dbmdz/bert-base-turkish-128k-uncased',
    do_lower_case=True
)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
token_id = []
attention_masks = []

def preprocessing(input_text, tokenizer):
    '''
    Preprocess the input text using the provided tokenizer.

    Args:
        input_text (str): The text to preprocess.
        tokenizer (BertTokenizer): The tokenizer to use for preprocessing.

    Returns:
        transformers.tokenization_utils_base.BatchEncoding: The tokenized input with input IDs, token type IDs, and attention mask.
    '''
    return tokenizer.encode_plus(
        input_text,
        add_special_tokens=True,
        max_length=50,
        pad_to_max_length=True,
        return_attention_mask=True,
        return_tensors='pt'
    )

def predict(comment):
    """
    Predict the label of the given comment using the BERT model.

    Args:
        comment (str): The comment to classify.

    Returns:
        dict: A dictionary with the original comment and the predicted label.
    """
    # Clean the comment by removing special characters and digits, and converting to lowercase
    comment = re.sub(r'[^\w\s]', '', comment)
    comment = re.sub(r'\d', '', comment)
    comment = comment.lower()
    
    # We need Token IDs and Attention Mask for inference on the new sentence
    predictions = []
    test_ids = []
    test_attention_mask = []
    
    # Apply the tokenizer
    encoding = preprocessing(comment, tokenizer)
    
    # Extract IDs and Attention Mask
    test_ids.append(encoding['input_ids'])
    test_attention_mask.append(encoding['attention_mask'])
    test_ids = torch.cat(test_ids, dim=0)
    test_attention_mask = torch.cat(test_attention_mask, dim=0)
    
    # Forward pass, calculate logit predictions
    with torch.no_grad():
        output = my_model(test_ids.to(device), token_type_ids=None, attention_mask=test_attention_mask.to(device))
    prediction = np.argmax(output.logits.cpu().numpy()).flatten().item()

    return {"comment": comment, "label": prediction}
