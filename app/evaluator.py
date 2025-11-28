from readability import Readability

def evaluate_plan(plan_text):
    # minimal heuristic scoring
    try:
        rd = Readability(plan_text)
        flesch = rd.flesch().score
    except Exception:
        flesch = None
    score = 0
    if flesch and flesch > 50:
        score += 50
    if len(plan_text) > 200:
        score += 30
    return {"flesch": flesch, "score": score}
