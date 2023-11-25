from schema import And, Regex, Schema


configSchema = Schema(
    {
        "asignment_name": And(str, Regex(r"^(\w+|(-){0-1})+$")),
        "semester": And(str, Regex(r"^(F|S|SUM)\d{2}$")),
    })

