from nltk.translate.bleu_score import corpus_bleu
from fastai1.fastai.callback import Callback


class BleuMetric(Callback):
    def on_epoch_begin(self, **kwargs):
        self.references = list()
        self.candidates = list()

    def on_batch_end(self, last_output, last_target, **kwargs):
        # pdb.set_trace()
        num_sentences = last_output[0].size(1)
        cands = last_output[0].data.max(2)[1].transpose(1, 0).chunk(num_sentences, 0)
        refs = last_target.transpose(1, 0).chunk(num_sentences, 0)

        self.candidates.extend([[tok for tok in c[0].cpu().numpy() if tok != 1] for c in cands])
        self.references.extend([[[tok for tok in r[0].cpu().numpy() if tok != 1]] for r in refs])

    def on_epoch_end(self, last_metrics, **kwargs):
        # pdb.set_trace()
        assert len(self.references) == len(self.candidates)
        return add_metrics(last_metrics, corpus_bleu(self.references, self.candidates))