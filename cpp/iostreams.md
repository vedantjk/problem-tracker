# I/O streams and filesystem

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

## File stream hierarchy and RAII

`<fstream>` supplies streams whose buffers are connected to files. They extend the same interfaces used for console and string I/O:

```text
std::istream  <-  std::ifstream     file input
std::ostream  <-  std::ofstream     file output
std::iostream <-  std::fstream      file input and output
```

A file stream can be opened by its constructor or later with `open`. Since C++17, the constructors and `open` also accept `std::filesystem::path`. Always test the stream after opening: a path can be absent, inaccessible, a directory rather than a regular file, or rejected for many other environment-specific reasons.

```cpp
#include <fstream>
#include <iostream>
#include <string>

std::ofstream out{"sample.txt"};
if (!out) {
    std::cerr << "could not open sample.txt for writing\n";
    return 1;
}

out << "first line\nsecond line\n";
```

The file is relative to the process's current working directory, which need not be the source or executable directory. A file stream owns its file buffer and closes it in its destructor, so normal scope exit, returns, and exception unwinding provide RAII cleanup. Explicit `close()` is useful when the file must be closed before the end of the scope, the same stream will be reopened, or the program must detect a final flush/close failure.

Read tokens with `>>`, lines with `std::getline`, or raw blocks with `read`. Drive the loop with the read operation itself; EOF becomes known only after an operation tries to read past the available input:

```cpp
std::ifstream in{"sample.txt"};
if (!in) {
    std::cerr << "could not open sample.txt for reading\n";
    return 1;
}

std::string line;
while (std::getline(in, line)) {
    std::cout << line << '\n';
}

if (!in.eof()) {
    std::cerr << "sample.txt could not be read completely\n";
    return 1;
}
```

`while (!in.eof())` is wrong because the flag describes the previous operation, not whether the next read will succeed; it commonly processes stale data once after the last successful read.

## File open modes

The second constructor or `open` argument is a bitmask of `std::ios::openmode` flags, combined with `|`.

| Mode | Meaning |
|---|---|
| `std::ios::in` | Permit input. Added by default for `ifstream`. |
| `std::ios::out` | Permit output. Added by default for `ofstream`. |
| `std::ios::app` | Seek to the end before every write, so every write appends. |
| `std::ios::ate` | Seek to the end once immediately after opening; later seeks may write elsewhere. |
| `std::ios::trunc` | Truncate an existing file to zero length when opening. |
| `std::ios::binary` | Suppress implementation-specific text translations and open as a binary stream. |

`ofstream` with its default `out` mode normally creates a missing file and truncates an existing one. Add `app` to preserve existing contents and append. `fstream` defaults to `in | out`; that combination normally requires the file to exist and does not truncate it. `in | out | trunc` creates or replaces a file for bidirectional access.

`app` and `ate` are not synonyms. `ate` establishes only the initial position, so a later seek can overwrite earlier bytes. `app` forces each write to the end even after seeking.

```cpp
std::ofstream log{"events.log", std::ios::app};
if (log) {
    log << "connected\n";
}
```

## Text, binary, buffering, and durability

Text mode may translate line endings or treat some byte values specially, depending on the platform. Binary mode suppresses those translations; it does not make `<<` and `>>` serialize numbers as their in-memory representation. Formatted operators still convert values to and from text.

Use `write` and `read` for exact byte counts:

```cpp
std::array<std::byte, 4096> buffer{};
in.read(reinterpret_cast<char*>(buffer.data()),
        static_cast<std::streamsize>(buffer.size()));
auto bytesRead = in.gcount();
```

Writing an object's raw memory is not a portable serialization format. Padding bytes, byte order, type sizes, floating-point representation, pointers, and version changes can all make the bytes unusable elsewhere. Define an explicit format and encode each field deliberately.

File output is buffered. `flush()`, `std::flush`, and `close()` ask the stream buffer to hand pending data to the operating system, and normal destruction closes the file. `std::endl` inserts a newline and flushes, so using it on every line can be expensive. A successful stream flush or close does not necessarily mean the storage device has made the data durable against power loss; that requires platform-specific synchronization guarantees.

`std::exit` does not destroy automatic file-stream objects, and abnormal termination may lose buffered output. Prefer returning through normal scopes. When reporting a successful file write matters, explicitly flush or close and then check the stream, because a destructor cannot report the failure to its caller.

## `std::filesystem` paths

C++17's `<filesystem>` library separates filesystem names and operations from file contents. Its central vocabulary types live in `std::filesystem`; a local alias keeps examples readable:

```cpp
#include <filesystem>

namespace fs = std::filesystem;

fs::path config = fs::path{"etc"} / "app" / "config.toml";
```

A `path` is a structured, platform-aware sequence of path elements. Constructing or manipulating it is usually lexical and does not require the named file to exist. `/` and `/=` append a path component with an appropriate separator; `+=` concatenates raw path text without inserting a separator.

Useful observers include:

| Observer | Result |
|---|---|
| `root_name()`, `root_directory()`, `root_path()` | Root components, whose syntax is platform-dependent. |
| `relative_path()` | Everything after the root path. |
| `parent_path()` | All elements before the filename. |
| `filename()` | Final path component. |
| `stem()` | Filename without its final extension. |
| `extension()` | Final extension, including its leading dot when present. |
| `string()`, `native()` | A converted string or the native path representation. |

Paths are iterable by lexical component. Operations such as `lexically_normal`, `lexically_relative`, and `lexically_proximate` manipulate spelling without consulting the filesystem. By contrast, `canonical` resolves an existing path through the filesystem and requires all components to exist; `weakly_canonical` can handle a non-existing suffix.

Do not build portable paths by concatenating `"/"` or `"\\"` yourself. Use `path` composition, and convert to a string only at an API boundary that actually requires one.

## Filesystem queries and mutations

The library provides queries such as `exists`, `is_regular_file`, `is_directory`, `is_symlink`, `file_size`, `last_write_time`, `status`, `symlink_status`, and `space`. Mutating operations include `create_directory`, `create_directories`, `copy`, `copy_file`, `rename`, `permissions`, `remove`, and `remove_all`.

Most filesystem operations have two error-reporting forms:

- An overload without `std::error_code&` throws `std::filesystem::filesystem_error` on an operating-system error.
- An overload with `std::error_code&` reports the error through that argument instead of throwing.

```cpp
std::error_code ec;
auto size = fs::file_size("capture.bin", ec);
if (ec) {
    std::cerr << "file_size failed: " << ec.message() << '\n';
}
```

The error-code form is useful in cleanup paths, directory scanners, and other code where an inaccessible entry is an expected event. The throwing form is often clearer when failure should abort the whole operation. Do not detect failure by comparing a result with a magic value if an error-code overload is available; inspect `ec`.

Checking and then acting is subject to a race: another process can replace, remove, or change a path between `exists(p)` and `open(p)`. Use preliminary queries for presentation or policy, not as proof that a later operation will succeed. Attempt the real operation and handle its result.

## Directory traversal

`directory_iterator` visits the entries immediately inside one directory. `recursive_directory_iterator` descends into subdirectories. Both work in range-for loops and skip the synthetic `.` and `..` entries. Traversal order is unspecified, so sort collected paths when deterministic output matters.

```cpp
std::error_code ec;
fs::directory_iterator it{"data", fs::directory_options::skip_permission_denied, ec};
fs::directory_iterator end;

for (; !ec && it != end; it.increment(ec)) {
    const fs::directory_entry& entry = *it;
    std::cout << entry.path().filename() << '\n';
}

if (ec) {
    std::cerr << "directory traversal failed: " << ec.message() << '\n';
}
```

Each iterator yields a `directory_entry`, which contains a `path` and may cache file metadata. Queries can still fail because files disappear, permissions change, or symlinks become invalid during traversal. `status` follows a symlink; `symlink_status` describes the link itself. Recursive traversal does not follow directory symlinks by default; enabling that option can introduce cycles, so code must defend against revisiting directories.

## File-I/O and filesystem pitfalls

Relative paths are interpreted from the process's current working directory. Log or report the resolved path when “file not found” would otherwise be mysterious.

Opening a stream and writing successfully are separate events. Check after opening and after the final write/close when output correctness matters. Never use `while (!eof())` to drive reads.

`binary` controls text translation only. It neither removes formatted conversion nor defines a portable object format.

Filesystem calls are snapshots of mutable external state. Results can become stale immediately, iteration order is not portable, and permissions or symlinks can make any step fail. Choose throwing or error-code overloads deliberately and handle the operation that actually matters.

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

### How do ifstream, ofstream, and fstream relate to the ordinary stream classes?

`ifstream` derives from `istream`, `ofstream` from `ostream`, and `fstream` from `iostream`. They use the same extraction, insertion, formatting, and state interfaces; their distinguishing feature is a stream buffer connected to a file. The file stream owns that buffer and closes it through RAII.

### What is the difference between app and ate?

Both initially position output at the end. `ate` does that once, after which seeking elsewhere and overwriting is allowed. `app` forces every write to the end, even after a seek, so it is the mode that guarantees appending.

### Does opening a file with ios::binary serialize objects in binary form?

No. It disables platform text translations such as newline conversion. Formatted `<<` and `>>` still produce and parse text, and dumping an object's bytes is not a portable format because of padding, byte order, sizes, representations, pointers, and versioning.

### When should filesystem operations throw, and when should they use error_code?

I use throwing overloads when an error should abort the whole operation and unwind to one handler. I use `error_code` overloads when failures are expected per entry, such as a directory scanner encountering inaccessible files, or when the code is already in a cleanup path where another exception would be harmful.

### Why is exists(path) not proof that open(path) will succeed?

The filesystem is shared mutable state. The path can be removed, replaced, or have its permissions changed between the check and the open. A preliminary query can inform a message or policy, but the program must attempt the real operation and handle that result.

### What must code assume about directory iteration?

The order is unspecified, entries can disappear or change during traversal, and metadata queries can fail. I collect and sort paths when deterministic order matters, choose an error policy explicitly, and treat symlinks carefully—especially if recursive traversal is configured to follow them.

## Practice history

### Reading

- Read 12/09 from the I/O Streams: Console group in the Beginner C++ tree.
- [LearnCpp 28.1: Input and output (I/O) streams](https://www.learncpp.com/cpp-tutorial/input-and-output-io-streams/)
- [LearnCpp 28.2: Input with istream](https://www.learncpp.com/cpp-tutorial/input-with-istream/)
- [LearnCpp 28.3: Output with ostream and ios](https://www.learncpp.com/cpp-tutorial/output-with-ostream-and-ios/)
- [LearnCpp 28.6: Basic file I/O](https://www.learncpp.com/cpp-tutorial/basic-file-io/)
- [C++ Stories: C++17 filesystem in the standard library](https://www.cppstories.com/2017/08/cpp17-details-filesystem/)

### Questions (getcracked)

- 12/09/2026 per platform record (rescraped 13/09): Double flushing? ok, std::cout vs std::cerr ok, Streams ok, Streams of strings. ok. MISSED: 1s in chat if you're cooked (`uint8_t y; std::cin >> y;` with input `11` extracts one character, `'1'` = 49, so `10 * 49` prints 490; extraction is type-directed and `uint8_t` is `unsigned char`).

<!-- gc-questions:start -->

## Related getcracked questions

Pulled from the Beginner C++ progress tree. ✓ answered correctly, ✗ attempted and missed, ○ not attempted yet. Regenerate with `python3 cpp/tools/gc_links.py` after re-scraping.

### I/O Streams: Console
- ✓ [Double flushing?](https://getcracked.io/question/751) — Cooked
- ✓ [std::cout vs std::cerr](https://getcracked.io/question/1283) — Easy
- ✓ [Streams](https://getcracked.io/question/1348) — Medium
- ✓ [Streams of strings.](https://getcracked.io/question/968) — Medium
- ✗ [1s in chat if you're cooked](https://getcracked.io/question/1222) — Hard

<!-- gc-questions:end -->
