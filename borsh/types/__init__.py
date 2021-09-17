from enum import auto, Enum, unique

# class _dynamic_array
#
# the internal class representing a Borsh dynamic array. not intended to be directly instantiated
# by user code; use 'types.dynamic_array' instead
class _dynamic_array:
    array_type = None

    def __init__(self, _type):
        self.array_type = _type

# class _fixed_array
#
# the internal class representing a Borsh fixed array. not intended to be directly instantiated
# by user code; use 'types.fixed_array' instead
class _fixed_array:
    length = None
    array_type = None

    def __init__(self, _type, length: int):
        if not isinstance(length, int):
            length_class_name = length.__class__.__name__
            raise TypeError('invalid type \'' + str(length_class_name) + '\' for fixed_array length (expected \'int\')')

        self.length = length
        self.array_type = _type

# class _hashmap
#
# the internal class representing a Borsh hashmap. not intended to be directly instantiated
# by user code; use 'types.hashmap' instead
class _hashmap:
    hashmap_key_type = None
    hashmap_value_type = None

    def __init__(self, hashmap_key_type, hashmap_value_type):
        if not hashmap_key_type in vars(types).values() or not hashmap_value_type in vars(types).values() and \
            not hashmap_key_type.__class__ in vars(types).values() or not hashmap_value_type.__class__ in vars(types).values():
            raise ValueError('constructor for \'hashmap\' requires two borsh.types object as arguments')
        
        self.hashmap_key_type = hashmap_key_type
        self.hashmap_value_type = hashmap_value_type

# class _hashset
#
# the internal class representing a Borsh hashset. not intended to be directly instantiated
# by user code; use 'types.hashset' instead
class _hashset:
    hashset_type = None

    def __init__(self, hashset_type):
        if not option_type in vars(types).values() and not option_type.__class__ in vars(types).values():
            raise ValueError('constructor for \'hashset\' requires a borsh.types object as an argument')
        
        self.hashset_type = hashset_type

# class _option
#
# the internal class representing a Borsh optional value. not intended to be directly instantiated
# by user code; use 'types.option' instead
class _option:
    option_type = None

    def __init__(self, option_type):
        if not option_type in vars(types).values() and not option_type.__class__ in vars(types).values():
            raise ValueError('constructor for \'option\' requires a borsh.types object as an argument')
        
        self.option_type = option_type

# class _option
#
# the internal class representing a Borsh struct. not intended to be directly instantiated
# by user code; use 'types.struct' instead
class _struct:
    struct_dict = None

    def __getitem__(self, index):
        return self.struct_dict[index]

    def __init__(self, struct_dict: dict):
        if not isinstance(struct_dict, dict):
            raise TypeError('constructor for \'struct\' requires a schema-like dict object as an argument')

        self.struct_dict = struct_dict

    def __repr__(self):
        return str(self.struct_dict)

    def __str__(self):
        return self.__repr__()

# class types
#
# 'types' is essentially a namespace for all of the different Borsh types. it was originally an enum
# but this made the 'types.dynamic_array(types.u8)' style syntax impossible. there are offsets added
# to certain values to ensure that they are unique for comparison

float_offset = 30
signed_int_offset = 20

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
    dynamic_array = _dynamic_array

    # struct type
    struct = _struct

    # field types
    fields = auto()
    named_fields = auto()
    unnamed_fields = auto()

    # enum type
    enum = auto()

    # hash types
    hashmap = _hashmap
    hashset = _hashset

    # option type
    option = _option

    # string type
    string = auto()

# class type_groups
#
# this class provides a convenient interface for grouping together types that should
# have the same processing logic (for example, unsigned integer types)
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