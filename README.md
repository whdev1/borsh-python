# Python Borsh Library
This is an unofficial Python library for serializing and deserializing data in the [Borsh](https://borsh.io/) binary serialization format.

Borsh stands for *Binary Object Representation Serializer for Hashing.* It was originally implemented in Rust for use with the [Near protocol](https://near.org/) with a focus on "consistency, safety, and speed." It is used for serializing data in a number of applications, including the [Solana](https://solana.com) blockchain.

## Usage
All Borsh byte streams have a *schema* that specifies name and type pairs for each of the values in the stream. The names of the available types are based on Rust and may be found [on this page](https://borsh.io/#pills-specification).

In this library, schemas may be declared as follows:

```Python
import borsh
from borsh import types

# create an example dict that we will serialize
example_dict = {
  'x': 123,
  'y': 30000,
  'z': 'hello'
}

# define the schema for the dict
example_dict_schema = borsh.schema({
  'x': types.u8,
  'y': types.i16,
  'z': types.string
})
```

We can serialize `example_dict` by calling the `serialize` method and providing the schema:

```Python
serialized_bytes = borsh.serialize(example_dict_schema, example_dict)

print(serialized_bytes)
# b'{0u\x05\x00\x00\x00hello'
```

This byte string can be deserialized by calling the `deserialize` method and providing the same schema:

```Python
deserialized_data = borsh.deserialize(example_dict_schema, serialized_bytes)

print(deserialized_data)
# {'x': 123, 'y': 30000, 'z': 'hello'}
```

Borsh data streams are often base64 encoded. This library can handle these streams when used in conjunction with the `base64` library. For example:

```Python
import base64
import borsh
from borsh import types

base64_borsh_data = base64.b64decode('ezB1BQAAAGhlbGxv')

example_dict_schema = borsh.schema({
  'x': types.u8,
  'y': types.i16,
  'z': types.string
})

print(borsh.deserialize(example_dict_schema, base64_borsh_data))
# {'x': 123, 'y': 30000, 'z': 'hello'}
```

## Type Mapping
This library supports the following Borsh types, each of which is mapped to a respective Python type during deserialization.

| Borsh Type      | Python Type      |
| --------------- | ---------------- |
| `dynamic_array` | `List[int]`      |
| `fixed_array`   | `List[int]`      |
| `f32`           | `float`          |
| `f64`           | `float`          |
| `i8`            | `int`            |
| `i16`           | `int`            |
| `i32`           | `int`            |
| `i64`           | `int`            |
| `i128`          | `int`            |
| `option(type)`  | `None` or `type` |
| `string`        | `str`            |
| `u8`            | `int`            |
| `u16`           | `int`            |
| `u32`           | `int`            |
| `u64`           | `int`            |
| `u128`          | `int`            |
| `unit`          | `None`           |