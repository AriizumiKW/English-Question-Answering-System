import torch
from model import baseline, utils


class IntensiveReadingWithCrossAttention(baseline.BaselineModel):
    def __init__(self, hidden_dim=256, clm_model='google/electra-small-discriminator'):
        super(IntensiveReadingWithCrossAttention, self).__init__(hidden_dim, clm_model)

    def forward(self, input_ids, attention_mask, token_type_ids, tokenizer):
        pass

