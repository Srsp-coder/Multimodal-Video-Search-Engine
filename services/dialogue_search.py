from rapidfuzz import fuzz


def search_dialogue(all_words, target, threshold=70):

    target_clean = target.lower().strip()
    target_words = target_clean.split()

    best_score = 0
    best_match = None

    target_length = len(target_words)

    for i in range(
        len(all_words) - target_length + 1
    ):

        window = all_words[
            i:i + target_length
        ]

        window_text = " ".join(
            word["word"]
            for word in window
        ).lower()

        score = fuzz.ratio(
            target_clean,
            window_text
        )

        if score > best_score:

            best_score = score

            best_match = {
                "text": window_text,
                "score": score,
                "start": window[0]["start"],
                "end": window[-1]["end"]
            }

    if (
        best_match is None
        or best_match["score"] < threshold
    ):
        return None

    return best_match