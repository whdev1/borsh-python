import struct   # unpack
from .types import types, type_groups

class schema:
    _inner_dict = None

    def __getitem__(self, index):
        return self._inner_dict[index]

    # initializes a new borsh schema object
    def __init__(self, schema_def: dict) -> None:
        # ensure the user gave us a dict
        if not isinstance(schema_def, dict):
            # if not, raise an error containing the class names of this instance
            # and the object that the user attempted to pass
            self_class_name = self.__class__.__name__
            schema_class_name = schema_def.__class__.__name__

            raise TypeError(
                'constructor for \'' + str(self_class_name) + '\' requires a dict object as its argument, ' + 
                'received \'' + str(schema_class_name) + '\''
            )

        # loop over everything in the schema definition and ensure they all entries
        # are of the expected format:
        #
        #   {str, borsh.type}
        #
        self._inner_dict = {}
        for key in schema_def:
            # check that the key is a string
            if not isinstance(key, str):
                key_class_name = key.__class__.__name__
                raise TypeError('invalid key type \'' + str(key_class_name) + '\' in schema dict')

            # check that the value is a Borsh type
            if not schema_def[key] in vars(types).values():
                # check for a constructible type
                constructible_types = [
                    types.dynamic_array,
                    types.fixed_array,
                    types.hashmap,
                    types.hashset,
                    types.option,
                    types.struct
                ]
                if not schema_def[key].__class__ in constructible_types:
                    raise TypeError('value \'' + str(schema_def[key]) + '\' is not a valid Borsh type')

            # if the key/value pair is valid, insert it
            self._inner_dict[key] = schema_def[key]
    
    def __iter__(self):
        return self._inner_dict.__iter__()

    def __next__(self):
        return self._inner_dict.__next__()

# deserialize(schema: schema, data: bytes) -> dict
#
# deserializes the specified Borsh data into a new dict
def deserialize(schema: schema, data: bytes) -> dict:
    results = {}

    # initialize a position in the buffer
    position = 0

    # give the user a nice error if they accidentally passed the wrong data type
    if not isinstance(data, bytes):
        raise TypeError('deserialize() expects data to be \'bytes\', not \'' + str(data.__class__.__name__) + '\'')

    # loop over all of the keys in the schema. catch an index error when there
    # is not enough data for the specified schema
    try:
        key = None
        for key in schema:
            results, position = _deserialize_single(
                key,
                schema,
                schema[key],
                data,
                position,
                results
            )
    except IndexError as ie:
        raise IndexError('out of data while reading value for key \'' + str(key) + '\'')

    # return the deserialized results
    return results

# _deserialize_single(key: object, _type: object, data: bytes, position: int, results: dict) -> (dict, int)
#
# internal method for deserializing a single Borsh object. not intended to be called by user code; use
# the deserialize() method instead
def _deserialize_single(key: object, _schema: schema, _type: object, data: bytes, position: int, results: dict) -> (dict, int):
    # determine what data type it is and perform the correct behavior
    # first, check for a uint type
    if _type in type_groups.uint_types:
        # determine the number of bytes to get
        byte_width = _type

        # get the correct number of bytes, shifting left each time
        # to conform with the little endian format of Borsh
        result = 0
        for n in range(byte_width):
            result <<= 8
            result += data[position + (byte_width - (n + 1))]

        # store the result
        results[key] = result
        position += byte_width
    # then, check for a signed int type
    elif _type in type_groups.int_types:
        # determine the number of bytes to get
        byte_width = _type - type_groups.signed_int_offset

        # get the correct number of bytes, shifting left each time
        # to conform with the little endian format of Borsh
        result = 0
        for n in range(byte_width):
            result <<= 8
            result += data[position + (byte_width - (n + 1))]

        # convert the result uint to a signed int. check if the highest bit is set
        bit_width = 8 * byte_width
        if result >> (bit_width - 1):
            # flip the sign bit
            result ^= 1 << (bit_width - 1)

            # subtract the two's complement offset
            result -= 1 << (bit_width - 1)

        # store the result
        results[key] = result
        position += byte_width
    # check for a float type
    elif _type in type_groups.float_types:
        # get the number of bytes for this float type
        byte_width = _type - type_groups.float_offset
        
        # put together a buffer of the specified number of bytes
        buffer = b''
        for n in range(byte_width):
            buffer += data[position : position + 1]
            position += 1

        # unpack the float and add it to the results
        if len(buffer) == 4:
            results[key] = struct.unpack('f', buffer)[0]
        elif len(buffer) == 8:
            results[key] = struct.unpack('d', buffer)[0]
        else:
            raise ValueError('invalid byte width ' + str(len(buffer)) + ' for float type')
    # check for a unit type
    elif _type == types.unit:
        # add None for this key
        results[key] = None
    # check for a fixed_array
    elif isinstance(_type, types.fixed_array):
        # get the length of the fixed array
        obj_length = _type.length

        # decode the specified number of objects into a list
        obj_results = []
        for n in range(obj_length):
            temp_results, position = _deserialize_single(
                key,
                _schema,
                _type.array_type,
                data,
                position,
                results
            )
            obj_results.append(results[key])
        
        # add the list to the results
        results[key] = obj_results
    # check for a dynamic array
    elif isinstance(_type, types.dynamic_array):
        # first, read the u32 size specifier
        byte_width = 4

        # get the correct number of bytes, shifting left each time
        # to conform with the little endian format of Borsh
        obj_length = 0
        for n in range(byte_width):
            obj_length <<= 8
            obj_length += data[position + (byte_width - (n + 1))]

        # increment the buffer pointer
        position += obj_length

        # decode the specified number of objects into a list
        obj_results = []
        for n in range(obj_length):
            temp_results, position = _deserialize_single(
                key,
                _schema,
                _type.array_type,
                data,
                position,
                results
            )
            obj_results.append(results[key])
        
        # add the list to the results
        results[key] = obj_results
    # check for a hashmap
    elif isinstance(_type, types.hashmap):
         # first, read the u32 size specifier
        byte_width = 4

        # get the correct number of bytes, shifting left each time
        # to conform with the little endian format of Borsh
        length = 0
        for n in range(byte_width):
            length <<= 8
            length += data[position + (byte_width - (n + 1))]

        # increment the buffer pointer
        position += byte_width

        # get the hashmap data
        hashmap_data = {}
        for n in range(length):
            ret_data = {}
            ret_data, position = _deserialize_single(
                key,
                _schema,
                _type.hashmap_key_type,
                data,
                position,
                results
            )
            new_key = ret_data[key]

            ret_data = {}
            ret_data, position = _deserialize_single(
                key,
                _schema,
                _type.hashmap_value_type,
                data,
                position,
                results
            )
            new_value = ret_data[key]

            hashmap_data[new_key] = new_value

        # store the hashmap data that we got
        results[key] = hashmap_data
    # check for a hashset
    elif isinstance(_type, types.hashset):
        # first, read the u32 size specifier
        byte_width = 4

        # get the correct number of bytes, shifting left each time
        # to conform with the little endian format of Borsh
        length = 0
        for n in range(byte_width):
            length <<= 8
            length += data[position + (byte_width - (n + 1))]

        # increment the buffer pointer
        position += byte_width

        # get the hashset data
        set_data = []
        for n in range(length):
            ret_data = {}
            ret_data, position = _deserialize_single(
                key,
                _schema,
                _type.hashset_type,
                data,
                position,
                results
            )
            set_data.append(ret_data[key])
        
        # convert the data to a set and add it to the results dict
        results[key] = set(set_data)
    # check for string data
    elif _type == types.string:
        # first, read the u32 size specifier
        byte_width = 4

        # get the correct number of bytes, shifting left each time
        # to conform with the little endian format of Borsh
        length = 0
        for n in range(byte_width):
            length <<= 8
            length += data[position + (byte_width - (n + 1))]

        # increment the buffer pointer
        position += byte_width

        # get the specified number of bytes and append them to a list of chars
        result_chars = []
        for n in range(length):
            result_chars.append(chr(data[position]))
            position += 1

        # convert the list to a string and add it to the results
        results[key] = ''.join(result_chars)
    # check for an option
    elif isinstance(_type, types.option):
        # first, get the u8 '1' or '0' representing whether or not this option is present
        option_present = data[position]
        position += 1

        # check if the option is here
        if option_present:
            results, position = _deserialize_single(
                key,
                _schema,
                _type.option_type,
                data,
                position,
                results
            )
        else:
            results[key] = None
    # check for a schema
    elif isinstance(_type, types.struct):
        # get the corresponding struct definition as a schema
        struct_schema = schema(_schema[key].struct_dict)

        # loop through all of the keys in the struct
        struct_data = {}
        for _key in _type.struct_dict:
            temp_results = {}
            temp_results, position = _deserialize_single(
                _key,
                _schema,
                struct_schema[_key],
                data,
                position,
                temp_results
            )
            
            struct_data[_key] = temp_results[_key]

        # add a new struct to the results
        results[key] = types.struct(struct_data)
    else:
        raise NotImplementedError('deserializing \'' + str(key) + '\' not implemented yet')

    # return the new result dict and position
    return results, position

# serialize(schema: schema, data: dict) -> bytes
#
# serializes the specified dict into a Borsh byte stream
def serialize(schema: schema, data: dict) -> bytes:
    results = b''

    # loop over all of the keys in the schema. catch an index error when there
    # is not enough data for the specified schema
    try:
        key = None
        for key in schema:
            results += _serialize_single(
                key,
                schema[key],
                schema,
                data
            )
    except IndexError as ie:
        raise IndexError('out of data while reading value for key \'' + str(key) + '\'')

    # return the serialized results
    return results

# _serialize_single(key: object, _type: object, data: bytes, position: int, results: dict) -> (dict, int)
#
# internal method for serializing a single Borsh object. not intended to be called by user code; use
# the serialize() method instead
def _serialize_single(key, _type, _schema, data: object) -> bytes:
    # initialize a byte string to hold the results
    results = b''

    # check which type we have received
    # first, check for a uint type
    if _type in type_groups.uint_types:
        # determine the byte width of this uint
        byte_width = _type
        
        # convert the value to a byte string
        results = data[key].to_bytes(byte_width, byteorder='little')
    # then, check for a signed int type
    elif _type in type_groups.int_types:
        # determine the byte width of this int
        byte_width = _type - type_groups.signed_int_offset

        # convert the value to a byte string
        results = data[key].to_bytes(byte_width, byteorder='little')
    # check for a float type
    elif _type in type_groups.float_types:
        # determine the byte width of this float
        byte_width = _type - type_groups.float_offset

        # convert the value to a byte string
        if byte_width == 4:
            results = struct.pack('f', data[key])
        elif byte_width == 8:
            results = struct.pack('d', data[key])
        else:
            raise ValueError('invalid byte width ' + str(byte_width) + ' for float type')
    # check for a unit type
    elif _type == types.unit:
        # don't do anything; return an empty byte string
        pass
    # check for a fixed_array
    elif isinstance(_type, types.fixed_array):
        # get the length of the fixed array
        obj_length = _type.length
        
        # loop over the list that we received and add each value to the byte string
        for n in range(obj_length):
            results += _serialize_single(
                key,
                _type.array_type,
                _schema,
                {key: data[key][n]}
            )
    # check for a dynamic_array or a fixed_array
    elif isinstance(_type, types.dynamic_array):
        # store the length of the array as a u32
        results = len(data[key]).to_bytes(4, byteorder='little')
        
        # loop over the list that we received and add each value to the byte string
        for n in range(len(data[key])):
            results += _serialize_single(
                key,
                _type.array_type,
                _schema,
                {key: data[key][n]}
            )
    # check for a hashmap
    elif isinstance(_type, types.hashmap):
        # store the length of the map as a u32
        results = len(data[key]).to_bytes(4, byteorder='little')

        # loop over all of the pairs in the hashmap
        for _key in data[key].keys():
            # serialize the key
            results += _serialize_single(
                key,
                _type.hashmap_key_type,
                _schema,
                {key: _key}
            )

            # serialize the value
            results += _serialize_single(
                key,
                _type.hashmap_value_type,
                _schema,
                {key: data[key][_key]}
            )
    # check for a hashset
    elif isinstance(_type, types.hashset):
        # store the length of the set as a u32
        results = len(data[key]).to_bytes(4, byteorder='little')

        # sort the set
        data[key] = sorted(data[key])
        
        # loop over the list that we received and add each int to the byte string
        set_list = list(data[key])
        for n in range(len(data[key])):
            results += _serialize_single(
                key,
                _type.hashset_type,
                _schema,
                {key: set_list[n]}
            )
    # check for a string
    elif _type == types.string:
        # store the length of the string as a u32
        results = len(data[key]).to_bytes(4, byteorder='little')

        # store the actual string
        results += bytes(data[key], 'utf-8')
    # check for an option
    elif isinstance(_type, types.option):
        # see if the key is present in the data
        if key in data.keys():
            # make a copy of the schema and replace the option with
            # the option subtype
            _schema_dup = _schema
            _schema_dup._inner_dict[key] = _type.option_type

            results = b'\1' + _serialize_single(
                key,
                _type.option_type,
                _schema_dup,
                data
            )
        else:
            results = b'\0'
    # check for a struct
    elif isinstance(_type, types.struct):
        # get a reference to the struct and its schema
        struct_obj = data[key]
        struct_schema = schema(_schema[key].struct_dict)

        # loop over all of the keys in the struct
        for key in struct_obj.struct_dict.keys():
            results += _serialize_single(
                key,
                struct_schema[key],
                struct_schema,
                {key: struct_obj.struct_dict[key]}
            )
    else:
        raise NotImplementedError('serializing \'' + str(_type) + '\' not implemented yet')

    return results