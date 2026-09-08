# Strings

For where a string literal and a `std::string` live in memory, and how the small-string optimization lays out the object, see [memory layout](memory_layout.md). For `std::string_view` as a parameter type, see [pointers and references](pointers_references.md).

## The three string things

A string literal such as `"hello"` is an array of `const char` with a trailing null character, stored in read-only static storage; its type is `const char[6]` and it decays to `const char*` when used as a pointer. A `const char*` is just a pointer to characters that someone promises end with a null; it does not own them and does not know their length without walking to the null. A `std::string` owns its characters, knows its size, grows on demand, and is what most C++ code should use. A `std::string_view`, from C++17, is a non-owning pointer-plus-length that can refer to any of the three without copying and need not be null-terminated.

Conversions run one way. A literal or a `const char*` converts implicitly to `std::string`, which copies the characters. A `std::string` does not convert implicitly to `const char*`; use `c_str()` for a null-terminated pointer or `data()` for the character buffer, which since C++11 is also null-terminated. Both `std::string` and `const char*` convert implicitly to `std::string_view`, and a `string_view` converts to `std::string` only explicitly, because that conversion allocates.

## Constructors

`std::string` has more constructors than any other everyday type, and several share a shape while meaning different things. The first argument's type decides the meaning of the number that follows it.

| Call | Result | Meaning |
|---|---|---|
| `std::string s;` | `""` | Default: empty. |
| `std::string s("hello");` | `"hello"` | From a `const char*`, copying up to the null. |
| `std::string s("hello world", 5);` | `"hello"` | From a `const char*` and a **count**: the first five characters. |
| `std::string s(other);` | copy of `other` | Copy construction. |
| `std::string s(std::move(other));` | takes `other`'s buffer | Move construction; `other` is left valid but unspecified, in practice empty. |
| `std::string s(other, 6);` | `other` from index 6 to the end | From a `std::string` and a **position**. |
| `std::string s(other, 6, 3);` | three characters from index 6 | From a `std::string`, a position, and a count. |
| `std::string s(5, 'a');` | `"aaaaa"` | A **count** and a character. |
| `std::string s('a', 5);` | 97 copies of the character with code 5 | The same overload with the arguments swapped; compiles because `char` converts to a count. |
| `std::string s(first, last);` | the characters in the iterator range | From any pair of input iterators. |
| `std::string s{'a', 'b'};` | `"ab"` | From an initializer list of characters. |
| `std::string s{65, 'a'};` | `"Aa"` | Braces prefer the initializer-list constructor, so 65 becomes `'A'`. |
| `std::string s(sv);` | copy of the view's characters | From a `std::string_view`; explicit, never implicit. |
| `std::string s(sv, 2, 3);` | three characters from index 2 of the view | View, position, count. |
| `std::string s(nullptr);` | compile error since C++23, undefined behavior before | Deleted overload; passing a null `const char*` was always a bug. |

The two traps to say out loud: `(const char*, n)` means the first `n` characters while `(std::string, n)` means from position `n`; and `(5, 'a')` versus `('a', 5)` both compile with opposite meanings. When building a string from part of another, `substr` or an iterator pair says what it means and sidesteps the overload set.

## Size, capacity, and access

`size()` and `length()` are the same function; both return the number of `char`s, not characters in any encoding sense. `empty()` is the readable test for zero length. `capacity()` is how many characters fit before the next reallocation; `reserve(n)` grows it ahead of time, and `shrink_to_fit()` asks, without a guarantee, to release the excess. `resize(n)` changes the size, truncating or padding with null characters, or with a supplied character. `clear()` empties the string but normally keeps the capacity.

`s[i]` does no bounds check and, since C++11, `s[s.size()]` is a valid read of the terminating null. `s.at(i)` checks and throws `std::out_of_range`. `front()` and `back()` require a non-empty string. `data()` and `c_str()` both return a null-terminated `const char*`; `data()` additionally has a non-const overload since C++17, so a string can be handed to a C API that writes into it after `resize`. The pointer from any of these is invalidated by any operation that may reallocate.

Iterators come from `begin()`, `end()`, and the reverse pair, so the standard algorithms and range-for apply directly.

## Building and editing

`+=` and `append` add to the end and accept a string, a view, a `const char*`, a character, or a count and character. `push_back(c)` appends one character; `pop_back()` removes the last. `insert(pos, ...)` and `erase(pos, count)` edit in the middle, with `erase(pos)` alone removing everything from `pos` to the end. `replace(pos, count, ...)` does both. `operator+` on two strings creates a new string; in a loop, prefer `+=` on one string with a `reserve` up front, because each `+` builds a temporary.

`substr(pos, count)` returns a new string, copying; `count` defaults to the rest, and a `pos` past the end throws `std::out_of_range`. The C++20 additions `starts_with`, `ends_with`, and C++23's `contains` accept a string, a view, a `const char*`, or a character and replace the usual `find` idioms.

## Searching and comparing

`find(x, pos)` returns the index of the first match at or after `pos`, or `std::string::npos`, which is `size_type(-1)`, the largest value the type holds. Every search function returns `npos` on failure, and the idiomatic test is `if (pos != std::string::npos)`. `rfind` searches backward. `find_first_of`, `find_last_of`, `find_first_not_of`, and `find_last_not_of` search for any character from a set, which is how trimming whitespace is usually written.

Comparison operators do lexicographic comparison by `char` value, so uppercase sorts before lowercase in ASCII. `compare` returns negative, zero, or positive and has overloads for comparing substrings without constructing them. C++20 gives strings `<=>` returning `std::strong_ordering`. Comparing a `std::string` with a literal is a content comparison, because the overload takes the string side; comparing two `const char*` with `==` compares addresses.

## Converting to and from numbers

`std::stoi`, `std::stol`, `std::stod`, and relatives parse from a `std::string`, skip leading whitespace, stop at the first invalid character, and throw `std::invalid_argument` when nothing parses or `std::out_of_range` on overflow. An optional second argument receives the index where parsing stopped. `std::to_string` converts numbers to a string using the C locale's `printf` formatting, so `to_string(0.1)` is `"0.100000"`.

`std::from_chars`, from `<charconv>` in C++17, is the fast, locale-independent, non-throwing alternative: it takes a character range and a reference to the result, returns a struct with a pointer to where it stopped and an error code, and does not skip whitespace or accept a leading plus sign. `std::to_chars` is its inverse into a caller-provided buffer. In a parser on a hot path, `from_chars` on a `string_view` is the right tool; `stoi` is for convenience code.

`std::stringstream` parses or formats with the stream operators, so `iss >> a >> b` splits on whitespace and `oss << x << ' ' << y` builds a string via `oss.str()`. It is flexible and slow: each stream carries locale and formatting state, and constructing one costs an allocation. Use it for one-off formatting, `getline` with a delimiter for simple splitting, and `from_chars` where speed matters.

## Errors and pitfalls

A `const char*` obtained from `c_str()` or `data()` dangles as soon as the string reallocates or is destroyed; storing it past the next mutating call is a use-after-free.

A `std::string_view` into a temporary string dangles at the end of the full expression: `std::string_view v = getName();` refers to a destroyed object on the next line.

`std::string s = nullptr;` is a compile error since C++23 and undefined behavior before it. `std::string s = 'a';` does not compile, but `s = 'a';` does, because assignment has a `char` overload and construction does not.

`s.size()` is unsigned, so `s.size() - 1` on an empty string wraps to `npos`, and `for (auto i = s.size() - 1; i >= 0; --i)` never ends.

## Interview Q&A

### What is the difference between a string literal, a const char*, and a std::string?

A literal is a null-terminated array of const char in read-only static storage. A const char* is a pointer to characters that are promised to end in a null; it owns nothing and knows no length. A std::string owns its buffer and knows its size. Literals and const char* convert implicitly to std::string by copying; the reverse needs c_str.

### Why is std::string s("hello world", 5) different from std::string s(str, 5)?

The overloads are chosen by the first argument's type. With a const char*, the number is a count of characters to copy. With a std::string, the number is a starting position. Same shape, opposite meaning, so for substrings I use substr or an iterator range.

### When would you use from_chars over stoi?

On a hot path or in a parser. from_chars is locale-independent, does not allocate, does not throw, and reports where it stopped and why through a return struct, so it works on a string_view without constructing a string. stoi needs a std::string, consults the locale, and throws on failure.

### What does npos mean?

It is the largest value of the string's size type, size_type(-1), and it is what every find function returns when there is no match. It also means "to the end" when passed as a count to substr or erase.

## Practice history

### Reading

- Filed 07/09 from the std::string constructor question; strings group of the Beginner C++ tree is only partially read.

<!-- gc-questions:start -->

## Related getcracked questions

Pulled from the Beginner C++ progress tree. ✓ answered correctly, ✗ attempted and missed, ○ not attempted yet. Regenerate with `python3 cpp/tools/gc_links.py` after re-scraping.

### char, const char*, and string
- ✓ [0.0_7](https://getcracked.io/question/975) — Easy
- ✓ [Char + Char](https://getcracked.io/question/674) — Easy
- ✓ [String placement](https://getcracked.io/question/1216) — Easy
- ✓ [String them together.](https://getcracked.io/question/996) — Easy
- ✓ [What's a character?](https://getcracked.io/question/847) — Easy
- ✗ [Where did it go?](https://getcracked.io/question/757) — Easy
- ✗ [You don't understand strings.](https://getcracked.io/question/699) — Easy
- ✗ [Another string question?](https://getcracked.io/question/1423) — Medium
- ✗ [Change it for me.](https://getcracked.io/question/870) — Medium
- ✗ [GG](https://getcracked.io/question/687) — Medium
- ✗ [More chars more problems.](https://getcracked.io/question/858) — Medium
- ✓ [Pointers to Pointers to Pointers](https://getcracked.io/question/767) — Medium
- ✗ [Signed Char == Unsigned Char?](https://getcracked.io/question/381) — Medium
- ✗ [What even is a string?](https://getcracked.io/question/881) — Medium
- ✗ [What's zero?](https://getcracked.io/question/818) — Medium
- ○ [Implement std::string](https://getcracked.io/problem/90/implement-std-string) — problem

### stringstream, string_view, and from_chars
- ✓ [Returned View](https://getcracked.io/question/2051) — Medium

### Small String Optimization
- ✓ [SOO, about that object.](https://getcracked.io/question/1206) — Easy
- ○ [Implement std::string](https://getcracked.io/problem/90/implement-std-string) — problem

<!-- gc-questions:end -->
