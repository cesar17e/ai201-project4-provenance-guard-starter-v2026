"""
Signal two: the style signal.

Signal one reads the text for meaning. This one measures it *as text* — the
shape of it, without understanding a word.

Three measurements describe the shape of the writing and are combined into
one score. Their normalization and weights are documented in README.md.

    sentence_length_spread   do sentences vary in length, or march in step?
    type_token_ratio         how much of the vocabulary repeats?
    punctuation_density      how much punctuation, and how varied?

Why these might differ between human and AI writing: generated prose tends
toward even, mid-length sentences and a narrower band of vocabulary, because
that's what "most likely next word" produces on average. Human writing is
lumpier — a three-word sentence next to a forty-word one.

⚠️ **The blind spot, which you have to name in Milestone 1.**

This signal cannot read. It has no idea what the text says. Anything that
changes the shape without changing the substance moves it — adding typos,
breaking up sentences, pasting in a quotation. That is a very cheap thing for
someone to do on purpose, and unit 8's attack set will do it to you.

Build each function on its own and call it from a terminal before you wire
anything together:

    python stylometry.py "some text to look at"
"""

import re
import statistics


def sentences(text: str) -> list[str]:
    """Split into sentences. Rough and good enough — given to you."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p.strip()]


def words(text: str) -> list[str]:
    """Split into lowercase words, punctuation stripped. Given to you."""
    return re.findall(r"[a-z0-9']+", text.lower())


# ── The three measures ──────────────────────────────────────────────────────

def sentence_length_spread(text: str) -> float:
    """
    This function measures how much sentences vary in length, and returns a float, we did this by calculating the standard deviation of the sentence lengths and dividing it by the mean length. A higher value indicates more variation in sentence lengths, which is often a characteristic of human writing, while a lower value suggests more uniformity, which can be indicative of AI-generated text.
    """
    sentence_list = sentences(text)

    lengths = [len(words(s)) for s in sentence_list]
    lengths = [n for n in lengths if n > 0]

    if len(lengths) < 2:
        return 0.0

    mean_length = statistics.mean(lengths)

    if mean_length == 0:
        return 0.0

    return statistics.stdev(lengths) / mean_length


def type_token_ratio(text: str) -> float:
    """
    This function measures the diversity of vocabulary in the text. It calculates the ratio of unique words (types) to the total number of words (tokens), returning a float. A higher type-token ratio indicates a richer and more varied vocabulary, which is often associated with human writing, while a lower ratio suggests more repetition and uniformity, which can be characteristic of AI-generated text.
    """
    tokens = words(text)

    if not tokens:
        return 0.0

    unique_words = set(tokens)

    return len(unique_words) / len(tokens)



def punctuation_density(text: str) -> float:
    """
    This function measures the density of punctuation in the text. It counts the number of punctuation characters and divides it by the total number of characters in the text, returning a float. A higher punctuation density may indicate more complex sentence structures and stylistic choices, which can be characteristic of human writing, while a lower density may suggest simpler, more uniform text, which can be indicative of AI-generated content.
    """
    if not text:
        return 0.0

    punctuation = ".,!?;:-—"

    count = sum(1 for char in text if char in punctuation)

    return count / len(text)


# ── Combining them ───────────────────────────────────────────────────────────

def style_signal(text: str) -> float:
    """
    This function combines the three measures (sentence length spread, type-token ratio, and punctuation density) into a single score that indicates the likelihood of the text being AI-generated. It normalizes each measure to a 0–1 scale and then combines them using weighted averages. A higher score suggests a greater likelihood of AI generation, while a lower score indicates more human-like writing.
    The weights for each measure can be adjusted based on empirical observations or specific requirements, but in this implementation, we use the following weights: 0.40 for sentence length spread, 0.35 for type-token ratio, and 0.25 for punctuation density. The final score is clamped between 0.0 and 1.0 to ensure it remains within a valid range
    
    """
    if not words(text):
        return 0.5

    spread = sentence_length_spread(text)
    ttr = type_token_ratio(text)
    punct = punctuation_density(text)

    # Normalize each measurement to 0–1.
    spread_score = 1.0 - min(spread, 1.0)
    vocabulary_score = 1.0 - ttr
    punctuation_score = 1.0 - min(punct / 0.10, 1.0)

    # Combine the three measurements.
    score = (
        0.40 * spread_score
        + 0.35 * vocabulary_score
        + 0.25 * punctuation_score
    )

    return max(0.0, min(score, 1.0))



if __name__ == "__main__":
    import sys

    text = " ".join(sys.argv[1:]) or (
        "The system works well. It handles most cases correctly and provides "
        "good results. Users generally find it easy to use and understand."
    )

    print(f"{len(sentences(text))} sentences, {len(words(text))} words\n")
    print(f"sentence_length_spread   {sentence_length_spread(text)}")
    print(f"type_token_ratio         {type_token_ratio(text)}")
    print(f"punctuation_density      {punctuation_density(text)}")
    print(f"style_signal             {style_signal(text)}   (higher = more likely AI)")
