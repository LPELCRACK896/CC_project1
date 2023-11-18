from collections import namedtuple


Reference = namedtuple('Reference', ['alias', 'class_owner', 'type_of_reference'])
TemporaryContext = namedtuple('TemporaryContext',
                              ["is_primitive", "data_type", "register", "expiring_line", "is_instance", "is_address"])
