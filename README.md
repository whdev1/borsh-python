# Python Borsh Library
This is an unofficial Python library for serializing and deserializing data in the [Borsh](https://borsh.io/) binary serialization format.

Borsh stands for *Binary Object Representation Serializer for Hashing.* It was originally implemented in Rust for use with the [Near protocol](https://near.org/) with a focus on "consistency, safety, and speed." It is used for serializing data in a number of applications, including the [Solana](https://solana.com) blockchain.

## Installation
This library can be installed using pip:

```
pip install borsh-python
```

## Usage
All Borsh byte streams have a *schema* that specifies name and type pairs for each of the values in the stream. The names of the available types are based on Rust and may be found [on this page](https://borsh.io/#pills-specification).

In this library, schemas may be declared as follows:

```Python
import borsh
from borsh import types

# create an example dict that we will serialize
example_dict = {
  'w': 123,
  'x': 30000,
  'y': 'hello',
  'z': [1, 2, 3, 4]
}

# define the schema for the dict
example_dict_schema = borsh.schema({
  'w': types.u8,
  'x': types.i16,
  'y': types.string,
  'z': types.dynamic_array(types.i8)
})
```

We can serialize `example_dict` by calling the `serialize` method and providing the schema:

```Python
serialized_bytes = borsh.serialize(example_dict_schema, example_dict)

print(serialized_bytes)
# b'{0u\x05\x00\x00\x00hello\x04\x00\x00\x00\x01\x02\x03\x04'
```

This byte string can be deserialized by calling the `deserialize` method and providing the same schema:

```Python
deserialized_data = borsh.deserialize(example_dict_schema, serialized_bytes)

print(deserialized_data)
# {'w': 123, 'x': 30000, 'y': 'hello', 'z': [1, 2, 3, 4]}
```

Borsh data streams are often base64 encoded. This library can handle these streams when used in conjunction with the `base64` library. For example:

```Python
import base64
import borsh
from borsh import types

base64_borsh_data = base64.b64decode('ezB1BQAAAGhlbGxvBAAAAAECAwQ=')

example_dict_schema = borsh.schema({
  'w': types.u8,
  'x': types.i16,
  'y': types.string,
  'z': types.dynamic_array(types.i8)
})

print(borsh.deserialize(example_dict_schema, base64_borsh_data))
# {'w': 123, 'x': 30000, 'y': 'hello', 'z': [1, 2, 3, 4]}
```

## Structs
The Borsh format supports a `struct` type which is similar in function to its counterparts in C-family languages. Consider that we are trying to wrap our `example_dict` into a `struct`. We may declare our data and schema as follows:

```Python
import borsh
from borsh import types

# define the data dict with our data wrapped in a struct called 'example'
example_struct_dict = {
  'example': types.struct({
    'w': 123,
    'x': 30000,
    'y': 'hello',
    'z': [1, 2, 3, 4]
  })
}

# define a schema for our new struct
example_struct_schema = {
  'example': types.struct({
    'w': types.u8,
    'x': types.i16,
    'y': types.string,
    'z': types.dynamic_array(types.i8)
  })
}
```

We may serialize and deserialize our `struct` like this:

```Python
serialized_bytes = borsh.serialize(example_struct_schema, example_struct_dict)

example_struct = borsh.deserialize(example_struct_schema, serialized_bytes)['example']
print(example_struct['y'])
# hello
```

## Type Mapping
This library supports the following Borsh types, each of which is mapped to a respective Python type during deserialization.

| Borsh Type      | Python Type      |
| --------------- | ---------------- |
| `dynamic_array` | `List[type]`     |
| `fixed_array`   | `List[type]`     |
| `f32`           | `float`          |
| `f64`           | `float`          |
| `hashmap`       | `dict{k_t: v_t}` |
| `hashset`       | `Set[type]`      |
| `i8`            | `int`            |
| `i16`           | `int`            |
| `i32`           | `int`            |
| `i64`           | `int`            |
| `i128`          | `int`            |
| `option(type)`  | `None` or `type` |
| `string`        | `str`            |
| `struct`        | `_struct[dict]`  |
| `u8`            | `int`            |
| `u16`           | `int`            |
| `u32`           | `int`            |
| `u64`           | `int`            |
| `u128`          | `int`            |
| `unit`          | `None`           |

## Unimplemented Types
The following Borsh types are not yet implemented in this library:

| Borsh Type      |
| --------------- |
| `enum`          |
| `fields`        |
| `named_fields`  |
| `unnamed_fields`|