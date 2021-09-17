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
                    types.fixed_array,
                    types.option
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

    # loop over all of the keys in the schema. catch an index error when there
    # is not enough data for the specified schema
    try:
        key = None
        for key in schema:
            results, position = _deserialize_single(
                key,
                schema[key],
                data,
                position,
                results
            )
    except IndexError as ie:
        raise IndexError('out of data while reading value for key \'' + str(key) + '\'')

    # return the deserialize results
    return results

def _deserialize_single(key: object, _type: object, data: bytes, position: int, results: dict) -> (dict, int):
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
        results[key] = struct.unpack('f', buffer)[0]
    # check for a unit type
    elif _type == types.unit:
        # add None for this key
        results[key] = None
    # check for a fixed_array
    elif isinstance(_type, types.fixed_array):
        # get the length of the fixed array
        byte_length = _type.length

        # decode the specified number of bytes into a list of u8's
        u8_results = []
        for n in range(byte_length):
            u8_results.append(data[position])
            position += 1
        
        # add the list to the results
        results[key] = u8_results
    # check for a dynamic array
    elif _type == types.dynamic_array:
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

        # get the specified number of bytes as u8's
        u8_results = []
        for n in range(length):
            u8_results.append(data[position])
            position += 1

        # add the list to the results
        results[key] = u8_results
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
                _type.option_type,
                data,
                position,
                results
            )
    else:
        raise NotImplementedError('deserializing \'' + str(key) + '\' not implemented yet')

    # return the new result dict and position
    return results, position