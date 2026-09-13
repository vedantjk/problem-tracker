# Console I/O streams

For string-backed streams and their conversion trade-offs, see [strings](strings.md). For why `std::int8_t` and `std::uint8_t` often use the character overloads of `<<` and `>>`, see [types and conversions](types_conversions.md).

## The stream model and class hierarchy

A stream is a sequential source or destination for characters. An input stream produces characters for the program; an output stream consumes characters from it. The same formatted interface works whether the underlying device is a terminal, string, file, or network because formatting is separated from the stream buffer that communicates with that device.

I/O is part of the standard library, not the core language. `<iostream>` provides the console stream classes and the four pre-connected narrow-character objects. Their class names are aliases of templates: `std::istream` is `std::basic_istream<char>`, `std::ostream` is `std::basic_ostream<char>`, `std::iostream` is `std::basic_iostream<char>`, and `std::ios` is `std::basic_ios<char>`.

```text
                         std::ios_base
                              |
                        std::basic_ios
                         /           \
          virtual std::basic_istream  virtual std::basic_ostream
                         \           /
                         std::basic_iostream

          std::basic_streambuf          (separate buffer hierarchy)
```

`basic_iostream` uses multiple inheritance so it can provide both input and output. The virtual inheritance of `basic_ios` ensures the bidirectional stream has one shared formatting and error-state base. A stream object owns or refers to a `basic_streambuf`; formatted operations translate values to or from characters, while the buffer moves those characters to or from the external device.

| Object | Static type | Connected stream | Important default behavior |
|---|---|---|---|
| `std::cin` | `std::istream` | standard input | Usually the terminal; tied to `std::cout`, so an input operation flushes pending prompts first. |
| `std::cout` | `std::ostream` | standard output | Normally buffered. |
| `std::cerr` | `std::ostream` | standard error | Has `unitbuf` set, so output operations flush automatically. |
| `std::clog` | `std::ostream` | standard error | Buffered and useful for non-urgent diagnostic logging. |

“Standard error” is a distinct channel even when it appears on the same terminal as standard output. Shells can redirect the two independently. `std::cerr` is commonly called unbuffered, but the more precise C++ description is that its `unitbuf` flag requests a flush after each output operation.

## Formatted extraction with `>>`

`operator>>` parses text according to the destination type. It skips leading whitespace by default, consumes the longest prefix that forms a value, stores the converted result, and leaves later characters for the next extraction. Chaining works because each extraction returns the stream:

```cpp
int quantity{};
double price{};

if (std::cin >> quantity >> price) {
    // Both conversions succeeded.
}
```

Extraction is type-directed, not size-directed. Reading into `char` or `unsigned char` extracts one character, whereas reading into `int` parses a sequence of digits. Consequently, on implementations where `std::uint8_t` aliases `unsigned char`, `std::cin >> value` reads one character and stores that character's code. Read into a wider integer and range-check when the intended input is a small numeric value.

The stream's `skipws` flag controls leading-whitespace skipping. `std::noskipws` disables it for later formatted extractions, and `std::skipws` restores it. For a single character including whitespace, the unformatted `get` operation usually states the intent more directly.

Old code often uses `std::setw(N)` before extracting into a raw character buffer so at most `N-1` characters plus the null terminator are stored. Before C++20, forgetting that bound could overflow the buffer. Since C++20, extraction into a character array uses an array-reference overload that knows its extent and limits the read to `N-1`; extraction through a decayed `char*` is no longer supported by that overload. Prefer `std::string` for ordinary token input:

```cpp
std::string word;
std::cin >> word;               // One whitespace-delimited token, grows safely.
```

Any characters not consumed by one extraction remain available to the next one. This is why reading a number with `>>` and then immediately calling `std::getline` often produces an empty line: the numeric extraction leaves the terminating newline behind.

## Unformatted input and lines

Unformatted input works with characters without numeric or textual conversion.

| Operation | Effect |
|---|---|
| `in.get(ch)` | Extracts one character, including whitespace. |
| `in.get(buffer, n, delim)` | Reads at most `n-1` characters and stops before `delim`, leaving it in the stream. |
| `in.getline(buffer, n, delim)` | Reads into a character array and extracts/discards `delim`; filling the array before finding it sets `failbit`. |
| `std::getline(in, string, delim)` | Reads safely into a `std::string` and extracts/discards `delim`; the default delimiter is newline. |
| `in.gcount()` | Reports characters extracted by the most recent applicable unformatted member operation. A discarded delimiter from the member `getline` is included. |
| `in.ignore(count, delim)` | Discards up to `count` characters, stopping after `delim` if it appears first. |
| `in.peek()` | Inspects the next character without extracting it. |
| `in.unget()` | Attempts to put the most recently extracted character back. |
| `in.putback(ch)` | Attempts to put a specified character back. |

Use `std::getline` with `std::string` for human-entered lines. After a preceding formatted extraction, consume the pending whitespace first when that is the intended policy:

```cpp
#include <iostream>
#include <string>

int age{};
std::string name;

std::cin >> age;
std::getline(std::cin >> std::ws, name);
```

`std::ws` consumes all leading whitespace, not just one newline, so it also removes deliberate leading spaces from the line. If leading spaces matter, discard only through the pending newline:

```cpp
#include <limits>

std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
std::getline(std::cin, name);
```

`get(buffer, n)` and the member `getline(buffer, n)` differ at the delimiter: `get` leaves it pending, while `getline` removes it. That single difference explains why two consecutive calls to `get(buffer, n)` can make the second call extract nothing when the first stopped at a newline.

## Output, flags, and manipulators

`operator<<` formats a value as characters and inserts them into an output stream. It returns the stream, so output can be chained. A manipulator inserted into the chain changes the stream's formatting state:

```cpp
#include <iomanip>
#include <iostream>

std::cout << std::hex << 27 << ' ' << 28 << '\n'  // 1b 1c
          << std::dec << 29 << '\n';              // 29
```

Most formatting state is sticky: it remains on the stream until changed again. `std::hex`, `std::fixed`, `std::setprecision`, `std::setfill`, and alignment are examples. Field width is the important exception: `std::setw(n)` and `width(n)` affect only the next formatted field and then reset to zero.

Flags can be manipulated directly with `setf` and `unsetf`, but manipulators are usually clearer. Flags in a format group are mutually exclusive. Calling `setf(std::ios::hex)` alone merely adds the bit and can leave `dec` set; either use the masked overload `setf(std::ios::hex, std::ios::basefield)` or simply insert `std::hex`.

| Purpose | Enable or choose | Restore or alternative |
|---|---|---|
| Boolean names | `std::boolalpha` | `std::noboolalpha` |
| Sign on positive numbers | `std::showpos` | `std::noshowpos` |
| Uppercase digits/exponent | `std::uppercase` | `std::nouppercase` |
| Integer base | `std::dec`, `std::hex`, `std::oct` | choose another base |
| Floating notation | `std::fixed`, `std::scientific`, `std::defaultfloat` | choose another notation |
| Always show decimal point/trailing zeros | `std::showpoint` | `std::noshowpoint` |
| Alignment | `std::left`, `std::right`, `std::internal` | choose another alignment |
| Fill character | `std::setfill(ch)` | set another character |
| Next field's minimum width | `std::setw(n)` | resets automatically after the field |
| Precision | `std::setprecision(n)` | set another precision |

The integer base changes representation, not the stored value: decimal `27` is octal `33` and hexadecimal `1b`. `uppercase` changes hexadecimal letters and exponent markers, not ordinary text.

## Floating-point precision

The meaning of precision depends on the active floating notation:

- With `std::defaultfloat`, `setprecision(n)` is approximately the number of significant digits.
- With `std::fixed`, it is the number of digits after the decimal point.
- With `std::scientific`, it is also the number of digits after the decimal point.
- If fewer digits are requested than needed, output is rounded.
- `std::showpoint` forces a decimal point and enough trailing zeros to express the requested precision.

```cpp
std::cout << std::setprecision(4) << 123.456 << '\n';               // 123.5
std::cout << std::fixed << std::setprecision(4) << 123.456 << '\n'; // 123.4560
```

Formatting controls presentation only; they do not change the value stored in the floating-point object.

## Width, fill, and alignment

A field width is a minimum, never a truncation limit. If the formatted value is wider than the requested field, the entire value is printed. Otherwise, the fill character occupies the spare positions:

```cpp
std::cout << std::setfill('*');
std::cout << std::setw(10) << std::right    << -12345 << '\n'; // ****-12345
std::cout << std::setw(10) << std::left     << -12345 << '\n'; // -12345****
std::cout << std::setw(10) << std::internal << -12345 << '\n'; // -****12345
```

`right` pads before the whole representation, `left` pads after it, and `internal` keeps a sign or base prefix at the left while padding between that prefix and the digits.

## Flushing is separate from inserting a newline

`'\n'` inserts a newline. `std::flush` flushes buffered output without inserting a character. `std::endl` does both, which is rarely needed for routine line output and can make output-heavy code much slower. Streams also flush at appropriate lifecycle or synchronization points, and `std::cin`'s tie to `std::cout` normally makes prompts visible before a blocking input operation.

Use `std::cerr` for diagnostics that should be emitted promptly and routed through standard error; use `std::clog` when buffered diagnostic output is acceptable.

## Errors and pitfalls

Formatting belongs to the stream, not to a single statement. A function that inserts `std::hex`, `std::fixed`, a fill character, or an alignment changes later output through that same stream unless it restores the old state. Width alone resets after one field.

Mixing `>>` with `std::getline` without accounting for the pending delimiter commonly reads an empty line. Choose whether to consume all leading whitespace with `std::ws` or discard through exactly one newline with `ignore`.

Character extraction is selected by type. `char`, `signed char`, and `unsigned char` are handled as characters, so an eight-bit integer typedef may not parse or print numerically. Cast on output or parse through a wider integer on input.

`peek`, `unget`, and `putback` can fail; they are requests to the underlying buffer, not an unlimited history mechanism. As with every stream operation, test the stream state before relying on the result.

## Interview Q&A

### Why can the same insertion and extraction syntax work for terminals, strings, and files?

The stream class owns formatting and error state, while a stream buffer handles the actual character source or destination. Code talks to the common `istream` or `ostream` interface and the attached buffer talks to the terminal, string, file, or device.

### What is the difference between formatted and unformatted input?

Formatted extraction with `>>` interprets characters according to the destination type and normally skips leading whitespace. Unformatted functions such as `get`, `getline`, `peek`, and `ignore` work directly with characters and delimiters. I use formatted extraction for tokens and numeric values, and `std::getline` into a string for complete human-entered lines.

### Why does getline sometimes return an empty string after operator>>?

The formatted extraction consumes the value but leaves the delimiter, usually a newline. `getline` sees that newline immediately, extracts and discards it, and therefore returns an empty line. I deliberately choose either `std::ws` to remove all leading whitespace or `ignore(max, '\n')` to discard only through the pending line ending.

### Which output settings persist?

Most of them: base, floating notation, precision, boolean style, sign display, case, fill, and alignment. Width is the exception; `setw` applies to the next field only. A reusable output function should avoid surprising its caller by leaking changed formatting state.

### How does setprecision change floating-point output?

With defaultfloat it controls significant digits. With fixed or scientific it controls digits after the decimal point. The conversion is rounded for display and does not modify the stored floating-point value.

### What is the difference between newline, flush, and endl?

`'\n'` inserts a newline, `std::flush` pushes buffered output to the destination, and `std::endl` performs both. I use newline normally and flush only when the destination must see the output immediately.

### Why might reading a number into uint8_t consume only one digit?

On common implementations `uint8_t` is an alias for `unsigned char`, so overload resolution selects character extraction. It reads one character because of the type, not because the object occupies one byte. I read into a wider unsigned integer, validate the range, and then cast.

## Practice history

### Reading

- Read 12/09 from the I/O Streams: Console group in the Beginner C++ tree.
- [LearnCpp 28.1: Input and output (I/O) streams](https://www.learncpp.com/cpp-tutorial/input-and-output-io-streams/)
- [LearnCpp 28.2: Input with istream](https://www.learncpp.com/cpp-tutorial/input-with-istream/)
- [LearnCpp 28.3: Output with ostream and ios](https://www.learncpp.com/cpp-tutorial/output-with-ostream-and-ios/)

<!-- gc-questions:start -->

## Related getcracked questions

Pulled from the Beginner C++ progress tree. ✓ answered correctly, ✗ attempted and missed, ○ not attempted yet. Regenerate with `python3 cpp/tools/gc_links.py` after re-scraping.

### I/O Streams: Console
- ○ [Double flushing?](https://getcracked.io/question/751) — Cooked
- ○ [std::cout vs std::cerr](https://getcracked.io/question/1283) — Easy
- ○ [Streams of strings.](https://getcracked.io/question/968) — Easy
- ○ [Streams](https://getcracked.io/question/1348) — Medium
- ○ [1s in chat if you're cooked](https://getcracked.io/question/1222) — Hard

<!-- gc-questions:end -->
