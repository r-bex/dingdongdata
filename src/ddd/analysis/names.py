from model.performance import Performance

BRACKET_CHARS = [("[", "]"), ("(",")"), ("{", "}"), ("<", ">")]

# TODO: ensure this is happening for other ringers
# example is date after name e.g. Firstname Surname (1999)
# TODO: write test
def _remove_brackets(name: str) -> str:
    """TODO: docstring"""
    for (open_bracket, close_bracket) in BRACKET_CHARS:
        if open_bracket in name and close_bracket in name:
            open_index = name.index(open_bracket)
            close_index = name.index(close_bracket)
            name = name[:open_index] + name[close_index:]
    
    return name

# TODO: write test
def _sanitise_name(name: str) -> str:
    """Because Chris Cooper can't be trusted"""
    # Remove any words in brackets
    name_without_brackets = _remove_brackets(name)

    # Remove anything that isn't a letter, space, - or '
    permitted_chars = [" ", "-", "'"]
    valid_chars = []
    for name_char in name_without_brackets:
        if name_char.isalpha() or name_char in permitted_chars:
            valid_chars.append(name_char)
    reconstituted_name = "".join(valid_chars)

    # Strip any surviving outer whitespace
    return reconstituted_name.strip()

# TODO: write test
def _get_all_unique_names(performances: list[Performance]) -> set[str]:
    """
    Return the set of all ringer names from the performances provided
    :param performances: a list of Performance objects
    :return: a set of sanitised ringer names as strings
    """
    all_ringers = []
    for performance in performances:
        for ringer in performance.get_ringers():
            all_ringers.append(_sanitise_name(ringer))
    return set(all_ringers)

# TODO: write test
# TODO: can be replaced when using clever matching
def find_similar_names(performances: list[Performance], name: str) -> list[str]:
    """TODO: docstring"""
    # Minus given name
    unique_names = _get_all_unique_names(performances)
    if name in unique_names:
        unique_names.remove(name)
    candidate_names = [candidate for candidate in unique_names if _could_be_the_same_person(candidate, name)]
    return candidate_names
    
# TODO: can be replaced when using clever matching
# TODO: write test
def _generate_name_words(name: str) -> list[str]: # TODO: name this function better
    """TODO: docstring"""
    words = []
    for word in name.split(" "):
        if "-" in word:
            words += word.split("-")
        else:
            words.append(word)
    return set(words)

# TODO: can be replaced when using clever matching
# TODO: write test
def _could_be_the_same_person(name_a: str, name_b: str) -> bool:
    """TODO: docstring"""
    words_a = _generate_name_words(name_a)
    words_b = _generate_name_words(name_b)
    # Do the names have at least two words in common?
    intersection = words_a.intersection(words_b)
    return len(intersection) >= 2

