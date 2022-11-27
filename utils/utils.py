def fixed_lenght(text, lenght):
    if len(text) > lenght:
        text = text[: lenght - 3] + "..."
    elif len(text) < lenght:
        text = (text + " " * lenght)[:lenght]
    return text
