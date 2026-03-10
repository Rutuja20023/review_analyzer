def calculate_product_score(review_text, product_name=None, rating=None):

    if not review_text:
        return 0, "No Review"

    words = review_text.split()
    if len(words) < 3:
        return 0, "Average"

    text_lower = review_text.lower()

    positive_words = ["good","excellent","best","premium","sturdy","durable",
                      "strong","solid","worth","affordable","recommend",
                      "perfect","superb","awesome","amazing","quality",
                      "fast","great"]

    negative_words = ["bad","poor","worst","defective","broken","damaged",
                      "issue","problem","disappointed","waste",
                      "terrible","horrible"]

    negations = ["not","never","no"]
    intensifiers = ["very","extremely","really","highly","super","absolutely"]

    total_score = 0

    for i, word in enumerate(words):
        word_lower = word.lower().strip('.,!?')
        word_original = word.strip('.,!?')

        is_positive = word_lower in positive_words
        is_negative = word_lower in negative_words

        if is_positive or is_negative:
            base_score = 2 if is_positive else -2

            if i > 0 and words[i-1].lower() in negations:
                base_score = -base_score

            if i > 0 and words[i-1].lower() in intensifiers:
                base_score *= 2

            if word_original.isupper() and len(word_original) > 2:
                base_score += 2 if base_score > 0 else -2

            total_score += base_score

    if rating:
        try:
            rating_val = float(rating)
            if rating_val >= 4:
                total_score += 2
            elif rating_val <= 2:
                total_score -= 2
        except:
            pass

    if total_score >= 10:
        category = "Highly Recommended"
    elif total_score >= 5:
        category = "Recommended"
    elif total_score >= 0:
        category = "Average"
    elif total_score >= -5:
        category = "Below Average"
    else:
        category = "Not Recommended"

    return total_score, category