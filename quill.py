#! /usr/bin/env python3

def format_string(raw_string, replacements):
    fmt_string = raw_string
    for (replacement, value) in replacements.items():
        fmt_string = fmt_string.replace('{' + replacement + '}', str(value))
    return fmt_string