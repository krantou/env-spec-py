import re


class EnvSpecSyntaxError(Exception):
    """
    Excpetion used for syntax errors.
    """

    pass


valid_types_list = [
    "color",
    "date",
    "datetime-local",
    "email",
    "month",
    "number",
    "password",
    "tel",
    "text",
    "time",
    "url",
    "week",
]


def create_list(input_str):
    """
    Creates a list from input_str_list.Returns the new list.
    If input_str=[1,2,], returns empty list(syntax error).
    """
    input_str = input_str.replace("[", "")
    input_str = input_str.replace("]", "")
    new_list = input_str.split(",")

    if "" in new_list:
        return []

    for pos in range(0, len(new_list)):
        new_list[pos] = str(new_list[pos]).strip()

    return new_list


def render_label(env_spec_entry):
    """
    Creates the html output for label.Takes as argument the current dictionary.
    """
    label_str = f'<label for="env_spec_{env_spec_entry["name"].lower()}">{env_spec_entry["name"]}</label>\n'

    return label_str


def render_input(env_spec_entry):
    """
    Creates the html output for env_spec_entry input, which is the current dictionary.
    """
    default_value = env_spec_entry["default_value"]
    default_value_state = f'value="{default_value}"' if default_value else ""

    env_spec_entry_input = (
        f'<input id="env_spec_{env_spec_entry["name"].lower()}" '
        f'name="{env_spec_entry["name"].lower()}" type="{env_spec_entry["type"]}" '
        f'{default_value_state}" />\n'
    )
    return env_spec_entry_input


def render_choice(choice, selected=False):
    """
    Creates the html output for key "choice".
    """
    selected_state = "selected" if selected else ""

    return f'\t<option value="{choice}"{selected_state}>{choice}</option>\n'


def render_to_html(env_spec_list):
    """
    Creates the html output from the env_spec list, by checking whether the
    value is None or not.(comments, choices, default_value)
    Returns the html output of the whole list.
    """
    if not env_spec_list:
        return []
    html_output = ""

    for env_spec_entry in env_spec_list:
        if env_spec_entry["choices"] is None:
            ret_str = render_label(env_spec_entry)
            ret_str += render_input(env_spec_entry)
        else:
            ret_str = render_label(env_spec_entry)
            ret_str += f'<select id="env_spec_{env_spec_entry["name"].lower()}" name="{env_spec_entry["name"].lower()}">\n'

            for choice in env_spec_entry["choices"]:
                ret_str += render_choice(
                    choice, choice == env_spec_entry["default_value"]
                )
            ret_str += "</select>\n"

        if env_spec_entry["comment"] is not None:
            ret_str += f"<small>{env_spec_entry['comment']}</small>\n"

        html_output += ret_str
    return html_output


def parse(env_spec_text):
    """
    Parse function creates a list of dictionaries by splitting env_spec_text by
    \n. Every line will be a dictionary.The keys of dictionary are:
    name, type, choices, default_value, comment.
    Returns the env_spec listm or empty list [], for exception.
    """
    env_spec_list = []

    alphanumeric_that_does_not_start_with_digit = r"^[A-Z_][0-9A-Z_]*$"
    name_regex = r"^(.+)\:(.+)$"
    choices_regex = r"^(.+)\]"
    default_values_regex = r"^(.+)\=(.+)$"
    line_comment_regex = r"^#"
    comment_regex = r"^(.+)\#(.+)$"

    lines = env_spec_text.split("\n")

    for line in lines:
        env_spec_entry = {}

        line_comment_match = re.match(line_comment_regex, line)

        if line_comment_match:
            continue

        env_spec_entry["comment"] = None
        comment_match = re.match(comment_regex, line)

        if comment_match:
            line = comment_match.groups()[0]
            comment = comment_match.groups()[1]
            env_spec_entry["comment"] = comment

        name_match = re.match(name_regex, line)

        if name_match:
            name = name_match.groups()[0]
            line = name_match.groups()[1]

            is_variable_name_valid = re.match(
                alphanumeric_that_does_not_start_with_digit, name
            )

            if not is_variable_name_valid:
                raise EnvSpecSyntaxError("SYNTAX ERROR: Invalid variable name.")

            env_spec_entry["name"] = name
            env_spec_entry["choices"] = None
            env_spec_entry["default_value"] = None

            choices_match = re.match(choices_regex, line)
            default_value_match = re.match(default_values_regex, line)

            if choices_match:
                choices_str = choices_match.groups()[0]

                choices = create_list(choices_str)

                if not choices:
                    raise EnvSpecSyntaxError("SYNTAX ERROR: Invalid choices list.")

                env_spec_entry["choices"] = choices

            if default_value_match:
                default_value = default_value_match.groups()[1]
                default_value = default_value.strip()

                if choices_match:
                    if default_value not in choices or default_value == "":
                        raise EnvSpecSyntaxError("SYNTAX ERROR: Invalid default value.")

                env_spec_entry["default_value"] = default_value

            if not choices_match:
                if default_value_match:
                    env_spec_type = default_value_match.groups()[0]
                else:
                    env_spec_type = line

                env_spec_type = env_spec_type.strip()

                if env_spec_type not in valid_types_list:
                    raise EnvSpecSyntaxError("SYNTAX ERROR: Invalid type.")

                env_spec_entry["type"] = env_spec_type
            else:
                env_spec_entry["type"] = "text"
        else:
            name = line.strip()
            is_variable_name_valid = re.match(
                alphanumeric_that_does_not_start_with_digit, name
            )

            if not is_variable_name_valid:
                raise EnvSpecSyntaxError("SYNTAX ERROR: Invalid variable name.")

            env_spec_entry["name"] = name
            env_spec_entry["type"] = "text"
            env_spec_entry["choices"] = None
            env_spec_entry["default_value"] = None

        env_spec_list.append(env_spec_entry)

    return env_spec_list


def render_env_spec(spec_str):
    """
    Render_emv_spec function takes the given spec_str
    and returns the html output.
    """
    env_spec_list = parse(spec_str)
    html_output = render_to_html(env_spec_list)
    return html_output


def main():
    html_output = render_env_spec(spec_str)
    return html_output


if __name__ == "__main__":
    spec_str = "# This line will be ignored\nADMIN_EMAIL: email  # This email will be notified for occurring errors"
    print(main())
