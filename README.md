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