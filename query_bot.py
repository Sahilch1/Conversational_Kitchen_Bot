# query_bot.py
"""
Retrieval and selection logic for the Kitchen Assistant.
Selects the best-matching recipe using both embedding similarity and
ingredient overlap heuristics to favor exact-ingredient matches.
"""

import re
from typing import Dict, List, Union
from vectorstore import build_recipe_index

_index = None


def _get_index():
    """Load and cache the FAISS index (lazy)."""
    global _index
    if _index is None:
        _index = build_recipe_index("recipes.csv")
    return _index


def _parse_document(text: str, metadata: dict = None) -> Dict[str, str]:
    """
    Extract 'title' (or 'name'), 'ingredients' and 'instructions' from a document's page_content.
    Falls back to metadata if fields are missing.
    """
    title = ""
    ingredients = ""
    instructions = ""

    if text:
        for line in text.splitlines():
            if ":" not in line:
                continue
            key, val = line.split(":", 1)
            key = key.strip().lower()
            val = val.strip()
            if key in ("name", "title"):
                title = val
            elif key.startswith("ingredient"):
                ingredients = val
            elif key.startswith("instruction") or key.startswith("step"):
                instructions = val

    if not title and metadata:
        title = metadata.get("name") or metadata.get("title") or title
    if not ingredients and metadata:
        # some loaders may put row values inside metadata
        ingredients = metadata.get("ingredients", ingredients)
    if not instructions and metadata:
        instructions = metadata.get("instructions", instructions)

    return {"title": title or "", "ingredients": ingredients or "", "instructions": instructions or ""}


def _split_steps(instructions: str) -> List[str]:
    """
    Convert instruction text into a list of steps.
    Accepts numbered text like '1. Do this. 2. Do that.' or newline-separated text.
    """
    if not instructions:
        return []

    # Try splitting by numbered patterns (1., 2., ...)
    parts = re.split(r'\s*\d+\.\s*', instructions)
    steps = [p.strip() for p in parts if p.strip()]
    if steps:
        return steps

    # If no numbered pattern, split by newline
    if "\n" in instructions:
        return [line.strip() for line in instructions.splitlines() if line.strip()]

    # Fallback: split on sentence boundaries (period + space)
    return [s.strip() for s in re.split(r'\.\s+', instructions) if s.strip()]


def _token_set(text: str) -> set:
    """Return a set of lowercase alpha-numeric tokens from text."""
    tokens = re.split(r'[^a-zA-Z0-9]+', text.lower() if text else "")
    return {t for t in tokens if t}


def fetch_recipe(user_input: str) -> Union[Dict[str, object], str]:
    """
    Given a user query (ingredients or free text), return a dict:
      {
        "title": "Chicken Curry",
        "ingredients": "chicken, onion, tomato, ...",
        "steps": ["Step 1", "Step 2", ...]
      }
    On error, returns a string with an error message.
    """
    query = (user_input or "").strip()
    if not query:
        return "Please enter ingredients or a recipe question."

    index = _get_index()

    # Try retrieving top candidates with scores where supported.
    try:
        candidates = index.similarity_search_with_score(query, k=5)
    except Exception:
        # Fallback if the method is not available
        try:
            docs = index.similarity_search(query, k=5)
            candidates = [(d, None) for d in docs]
        except Exception as e:
            return f"Search failed: {e}"

    user_tokens = _token_set(query)

    # Choose the best candidate by ingredient overlap (strong preference),
    # tie-breaker: any available similarity score or the first candidate.
    best = None
    best_overlap = -1

    for doc, score in candidates:
        parsed = _parse_document(doc.page_content, getattr(doc, "metadata", None) or {})
        ing_tokens = _token_set(parsed["ingredients"])
        title_tokens = _token_set(parsed["title"])

        # Overlap metric: ingredient overlap + 2*(title overlap)
        overlap = len(user_tokens & ing_tokens) + 2 * len(user_tokens & title_tokens)

        if overlap > best_overlap:
            best_overlap = overlap
            best = {"title": parsed["title"], "ingredients": parsed["ingredients"], "instructions": parsed["instructions"], "score": score}

    # If there was no token overlap at all, fallback to the top retrieved item
    if best is None and candidates:
        doc0 = candidates[0][0]
        p = _parse_document(doc0.page_content, getattr(doc0, "metadata", None) or {})
        best = {"title": p["title"], "ingredients": p["ingredients"], "instructions": p["instructions"], "score": candidates[0][1]}

    # Prepare final output
    steps = _split_steps(best["instructions"]) if best else []
    return {"title": best["title"] if best else "", "ingredients": best["ingredients"] if best else "", "steps": steps}
