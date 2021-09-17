from enum import auto, Enum, unique

float_offset = 30
signed_int_offset = 20

class _fixed_array:
    length = None

    def __init__(self, length: int):
        if not isinstance(length, int):
            length_class_name = length.__class__.__name__
            raise TypeError('invalid type \'' + str(length_class_name) + '\' for fixed_array length (expected \'int\')')

        self.length = length

class _option:
    option_type = None

    def __init__(self, option_type):
        if not option_type in vars(types).values():
            raise ValueError('constructor for \'option\' requires a borsh.types object as an argument')
        
        self.option_type = option_type

class types:
    # unsigned integer types
    u8 = 1
    u16 = 2
    u32 = 4
    u64 = 8
    u128 = 16

    # signed integer types
    i8 = 1 + signed_int_offset
    i16 = 2 + signed_int_offset
    i32 = 4 + signed_int_offset
    i64 = 8 + signed_int_offset
    i128 = 16 + signed_int_offset

    # float types
    f32 = 4 + float_offset
    f64 = 8 + float_offset

    # unit type
    unit = auto()

    # array types
    fixed_array = _fixed_array
    dynamic_array = auto()

    # struct type
    struct = auto()

    # field types
    fields = auto()
    named_fields = auto()
    unnamed_fields = auto()

    # enum type
    enum = auto()

    # hash types
    hashmap = auto()
    hashset = auto()

    # option type
    option = _option

    # string type
    string = auto()

class type_groups:
    float_offset = float_offset
    signed_int_offset = signed_int_offset
    
    float_types = [
        types.f32,
        types.f64
    ]

    int_types = [
        types.i8,
        types.i16,
        types.i32,
        types.i64,
        types.i128
    ]

    uint_types = [
        types.u8,
        types.u16,
        types.u32,
        types.u64,
        types.u128
    ]