import tensorflow as tf
import transformers
from huggingface_hub import from_pretrained_keras
import tensorflow_hub as hub
import numpy as np

class BertSemanticDataGenerator(tf.keras.utils.Sequence):

    def __init__(
            self,
            sentence_pairs,
            labels,
            batch_size=32,
            shuffle=True,
            include_targets=True,
    ):
        self.sentence_pairs = sentence_pairs
        self.labels = labels
        self.shuffle = shuffle
        self.batch_size = batch_size
        self.include_targets = include_targets
        # Load our BERT Tokenizer to encode the text.
        # We will use base-base-uncased pretrained model.
        self.tokenizer = transformers.BertTokenizer.from_pretrained(
            "bert-base-uncased", do_lower_case=True
        )
        self.indexes = np.arange(len(self.sentence_pairs))
        self.on_epoch_end()

    def __len__(self):
        # Denotes the number of batches per epoch.
        return len(self.sentence_pairs) // self.batch_size

    def __getitem__(self, idx):
        # Retrieves the batch of index.
        indexes = self.indexes[idx * self.batch_size: (idx + 1) * self.batch_size]
        sentence_pairs = self.sentence_pairs[indexes]

        # With BERT tokenizer's batch_encode_plus batch of both the sentences are
        # encoded together and separated by [SEP] token.
        encoded = self.tokenizer.batch_encode_plus(
            sentence_pairs.tolist(),
            add_special_tokens=True,
            max_length=128,
            return_attention_mask=True,
            return_token_type_ids=True,
            padding='max_length',  # Update padding argument
            truncation=True,  # Add truncation argument
            return_tensors="tf",
        )

        # Convert batch of encoded features to numpy array.
        input_ids = np.array(encoded["input_ids"], dtype="int32")
        attention_masks = np.array(encoded["attention_mask"], dtype="int32")
        token_type_ids = np.array(encoded["token_type_ids"], dtype="int32")

        # Set to true if data generator is used for training/validation.
        if self.include_targets:
            labels = np.array(self.labels[indexes], dtype="int32")
            return [input_ids, attention_masks, token_type_ids], labels
        else:
            return [input_ids, attention_masks, token_type_ids]

        

def check_similarity(sentence1, sentence2, model):
    labels = ["Contradiction", "Perfect", "Neutral"]
    sentence_pairs = np.array([[str(sentence1), str(sentence2)]])
    test_data = BertSemanticDataGenerator(
        sentence_pairs, labels=None, batch_size=1, shuffle=False, include_targets=False,
    )
    probs = model.predict(test_data[0])[0]

    labels_probs = {labels[i]: round(float(probs[i]),2) for i, _ in enumerate(labels)}
    return labels_probs

# model = from_pretrained_keras("keras-io/bert-semantic-similarity")

# print(check_similarity("""Machine Learning is the] field of study that gives computers the ability to learn
# without being explicitly programmed.
# OR
# A computer program is said to learn from experience E with respect to some task T
# and some performance measure P, if its performance on T, as measured by P,
# improves with experience E.

# 3 examples are as follows:
# Detecting tumors in brain scans
# This is semantic segmentation, where each pixel in the image is classified (as we
# want to determine the exact location and shape of tumors), typically using CNNs
# as well
#  Creating a chatbot or a personal assistant
# This involves many NLP components, including natural language understanding
# (NLU) and question-answering modules.
# Summarizing long documents automatically
# This is a branch of NLP called text summarization, again using the same tools.""","""A computer program is said to learn from experience.
# with respect to some task I and some performance
# measure P, if its performance on T, as measured by P.
# improves with Experience E.
# 3 examples are:-
# →
# K
# →
# Detecting tumor in scans:
# This is semantic segmentation, where each pixel in
# the image is classified using CNN's.
# Summarizing long documents:
# Its a branch of NLP that summarizes long text.
# Object Detection,
# This is done using Image segmentation using Deep
# Learning.""", model))