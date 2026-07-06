import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.pipeline.stages.sentence_segmentation import segment_answer, split_sentences


def test_split_sentences_handles_simple_text():
    text = "The company was founded in 2015. It raised $20 million in 2021."
    sentences = split_sentences(text)
    assert sentences == ["The company was founded in 2015.", "It raised $20 million in 2021."]


def test_segment_answer_adds_sentence_list():
    example = {
        "id": "ex-1",
        "answer": "The policy covers health insurance. It also offers paid leave.",
    }
    segmented = segment_answer(example)
    assert segmented["sentences"] == [
        "The policy covers health insurance.",
        "It also offers paid leave.",
    ]
