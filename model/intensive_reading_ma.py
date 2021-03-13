import torch
import torch.nn as nn
import torch.nn.functional as F
from model import utils
from transformers import ElectraModel


class IntensiveReadingWithMatchAttention(nn.Module):
    def __init__(self, hidden_dim=256, clm_model='google/electra-small-discriminator'):
        super(IntensiveReadingWithCrossAttention, self).__init__()
        self.pre_trained_clm = ElectraModel.from_pretrained(clm_model)
        self.Hq_proj = nn.Linear(hidden_dim, hidden_dim, bias=True)
        self.span_detect_layer = nn.Linear(hidden_dim, 2, bias=True)
        nn.init.xavier_uniform_(self.Hq_proj.weight, gain=1 / math.sqrt(2))
        nn.init.xavier_uniform_(self.span_detect_layer.weight, gain=1 / math.sqrt(2))
        nn.init.constant_(self.Hq_proj.bias, 0.)
        nn.init.constant_(self.span_detect_layer.bias, 0.)


    def forward(self, input_ids, attention_mask, token_type_ids, pad_idx):
        # batch_size * seq_length * hidden_dim
        H = self.pre_trained_clm(input_ids, attention_mask, token_type_ids).last_hidden_state
        question_hidden, passage_hidden, question_pad_mask, passage_pad_mask = utils.generate_question_and_passage_hidden(H, attention_mask, token_type_ids, pad_idx)
        Hq = question_hidden
        Hq = Hq_proj(Hq)
        attn_scores = torch.bmm(H, Hq.transpose(1, 2))  # size: [batch_size * H_seq_length * Hq_seq_length]
        M = F.softmax(attn_scores, dim=-1)
        Hpri = torch.bmm(M, Hq)
        
        # [batch_size * H_seq_length * 2]
        span_output = self.span_detect_layer(Hpri).transpose(0, 1)

        start_logits, end_logits = span_output.split(1, dim=-1)

        # [H_seq_length * batch_size]
        start_logits = start_logits.squeeze(dim=-1)
        end_logits = end_logits.squeeze(dim=-1)
        return start_logits, end_logits


        
        