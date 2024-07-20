def extract_bracket_content(input_string):
    first_open = input_string.find('{')
    last_close = input_string.rfind('}')

    if first_open == -1 or last_close == -1 or first_open > last_close:
        return "Brackets not found or improperly ordered"

    # Extract content between the first '{' and the last '}'
    content = input_string[first_open:last_close + 1].lower()

    # Count the number of opening and closing brackets
    open_bracket_count = content.count('{')
    close_bracket_count = content.count('}')

    # If the counts are not equal, balance the brackets by adding necessary closing brackets
    if open_bracket_count != close_bracket_count:
        content += '}' * (open_bracket_count - close_bracket_count)

    return content