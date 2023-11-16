

primitives = [
    "Int",
    "String",
    "Bool"
]

defaults_values = {
    "Int": 0,
    "String": "\"\"",
    "Bool": 0
}

type_of_data_on_mips = {
    "Int": ".word",
    "String": ".asciiz",
    "Bool": ".byte"
}