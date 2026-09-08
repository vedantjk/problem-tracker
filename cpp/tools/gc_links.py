#!/usr/bin/env python3
"""Regenerate the "Related getcracked questions" section in every cpp/*.md file.

Input: cpp/tools/gc_tree_items.json, scraped from the Beginner C++ progress tree
(one entry per tree node: id, title, items[] with href/title/cells/svgs).
Status is read from the lucide icon class on each row: check = correct,
x = attempted and missed, minus = not attempted.

Each tree node maps to one or more concept files below. Nodes with no mapping are
listed in README.md under "Questions without a concept file yet".

Run from the repo root:  python3 cpp/tools/gc_links.py
"""
import json, re, pathlib, collections

ROOT = pathlib.Path(__file__).resolve().parents[2]
CPP = ROOT / "cpp"
DATA = CPP / "tools" / "gc_tree_items.json"
BASE = "https://getcracked.io"
START, END = "<!-- gc-questions:start -->", "<!-- gc-questions:end -->"

NODE_TO_FILES = {
    "What, Why, and When?": ["build_linkage"],
    "Steps to C++ Development": ["build_linkage"],
    "Installing your IDE": ["build_linkage"],
    "Comments, Whitespace, Formatting, Printing": ["build_linkage"],
    "Variables, Objects, Initialization": ["initialization_deduction"],
    "Keywords and Identifiers": ["build_linkage"],
    "Undefined Behavior": ["ub_catalog"],
    "Literals, Operators and Expressions": ["expressions", "types_conversions"],
    "The other behaviors.": ["ub_catalog", "expressions"],
    "Declarations, Definitions, and Multiple Code Files": ["build_linkage"],
    "The Preprocessor and Header Guards": ["build_linkage"],
    "Functions, Parameters, Arguments and Return Values": ["functions_scope_lambdas"],
    "Scope": ["functions_scope_lambdas"],
    "Namespaces": ["build_linkage"],
    "Anonymous Functions": ["functions_scope_lambdas"],
    "The Debugging Process": ["build_linkage"],
    "Debugging with the IDE": ["build_linkage"],
    "void": ["types_conversions", "functions_scope_lambdas"],
    "Object Sizes": ["memory_layout"],
    "Signed versus Unsigned Integers": ["types_conversions"],
    "Fixed Width Integers": ["types_conversions"],
    "Floating Point Types": ["floating_point"],
    "Bools": ["types_conversions"],
    "Enumerations": ["types_conversions"],
    "static_cast": ["types_conversions"],
    "auto": ["initialization_deduction"],
    "Tuple": ["functions_scope_lambdas"],
    "Bitflags and std::bitset": ["bits_punning"],
    "Bitwise Operators and Bit Masks": ["bits_punning", "types_conversions"],
    "reinterpret_cast and std::memcpy": ["bits_punning"],
    "std::bit_cast": ["bits_punning"],
    "Precedence": ["expressions"],
    "Arithmetic Operators": ["expressions", "types_conversions"],
    "Pre and Post Decrement": ["expressions"],
    ", and ?": ["expressions"],
    "Relational Operators": ["expressions", "types_conversions"],
    "Operator Overloading": ["expressions"],
    "if": ["control_flow"],
    "Switch and Fallthrough": ["control_flow"],
    "Loops I: while, do-while, for": ["control_flow"],
    "Loops II: break and continue": ["control_flow"],
    "Ending Early": ["control_flow"],
    "range-based for-loop": ["control_flow"],
    "Recursion": ["functions_scope_lambdas", "control_flow"],
    "Stack": ["memory_layout"],
    "Heap": ["memory_layout"],
    "Storage Durations": ["functions_scope_lambdas", "initialization_deduction"],
    "std::exception and Stack Unwinding": ["error_handling"],
    "std::optional and nullopt": ["error_handling"],
    "std::expected<T, E>": ["error_handling"],
    "Const": ["initialization_deduction", "pointers_references"],
    "Pointers": ["pointers_references"],
    "References": ["pointers_references"],
    "Move Semantics": ["smart_pointers_move", "value_categories"],
    "lvalue, rvalue, xvalue, prvalue, glvalue": ["value_categories"],
    "std::unique_ptr": ["smart_pointers_move"],
    "std::shared_ptr": ["smart_pointers_move"],
    "std::weak_ptr": ["smart_pointers_move"],
    "Constant and Constexpr Variables": ["initialization_deduction"],
    "char, const char*, and string": ["memory_layout", "initialization_deduction"],
    "stringstream, string_view, and from_chars": ["pointers_references"],
    "Small String Optimization": ["memory_layout"],
    "Special Member Functions": ["smart_pointers_move"],
    "Friends and Enemies": ["expressions"],
    "Universal References & Perfect Forwarding": ["value_categories"],
}


# Item-level additions: an href prefix that also belongs in another file
# (the tree files the allocator problems under the Pointers node).
ITEM_EXTRA_FILES = {
    "/problem/18/": ["allocators"],
    "/problem/158/": ["allocators"],
}


def status(svgs: str) -> str:
    if "lucide-check" in svgs:
        return "✓"
    if "lucide-x" in svgs:
        return "✗"
    return "○"


def kind(href: str) -> str:
    if "/question/" in href:
        return "question"
    if "/problem" in href:
        return "problem"
    return "resource"


def main() -> None:
    nodes = json.loads(DATA.read_text())
    per_file: dict[str, list[tuple[str, list[dict]]]] = collections.defaultdict(list)
    unmapped: list[tuple[str, list[dict]]] = []
    totals = collections.Counter()

    for n in nodes:
        items = [
            {"kind": kind(i["href"]), "href": i["href"], "title": i["title"],
             "diff": (i["cells"][1] if len(i["cells"]) > 1 else ""), "status": status(i["svgs"])}
            for i in n["items"] if kind(i["href"]) != "resource"
        ]
        if not items:
            continue
        for it in items:
            totals[(it["kind"], it["status"])] += 1
        files = NODE_TO_FILES.get(n["title"])
        if files:
            for f in files:
                per_file[f].append((n["title"], items))
        else:
            unmapped.append((n["title"], items))
        for it in items:
            for prefix, extra in ITEM_EXTRA_FILES.items():
                if it["href"].startswith(prefix):
                    for f in extra:
                        per_file[f].append((n["title"], [it]))

    def render(groups: list[tuple[str, list[dict]]]) -> str:
        out = [START, "", "## Related getcracked questions", "",
               "Pulled from the Beginner C++ progress tree. ✓ answered correctly, ✗ attempted and missed, ○ not attempted yet. "
               "Regenerate with `python3 cpp/tools/gc_links.py` after re-scraping.", ""]
        for node, items in groups:
            out.append(f"### {node}")
            for it in items:
                tag = "problem" if it["kind"] == "problem" else it["diff"]
                out.append(f"- {it['status']} [{it['title']}]({BASE}{it['href']}) — {tag}")
            out.append("")
        out.append(END)
        return "\n".join(out)

    for f, groups in per_file.items():
        path = CPP / f"{f}.md"
        text = path.read_text()
        block = render(groups)
        if START in text and END in text:
            text = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: block, text, flags=re.S)
        else:
            text = text.rstrip("\n") + "\n\n" + block + "\n"
        path.write_text(text)
        done = sum(1 for _, items in groups for it in items if it["status"] != "○")
        total = sum(len(items) for _, items in groups)
        print(f"{f:28} {done:3}/{total:3} attempted")

    # README: unmapped nodes
    readme = CPP / "README.md"
    text = readme.read_text()
    out = [START, "", "## Questions without a concept file yet", "",
           "Tree nodes not yet mapped to a concept file (mostly Intermediate material). "
           "When a file is created for one of these, add the mapping in `cpp/tools/gc_links.py`.", ""]
    for node, items in unmapped:
        attempted = [it for it in items if it["status"] != "○"]
        out.append(f"- **{node}** — {len(attempted)}/{len(items)} attempted"
                   + (": " + ", ".join(f"{it['status']} [{it['title']}]({BASE}{it['href']})" for it in attempted) if attempted else ""))
    out += ["", END]
    block = "\n".join(out)
    if START in text and END in text:
        text = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: block, text, flags=re.S)
    else:
        text = text.rstrip("\n") + "\n\n" + block + "\n"
    readme.write_text(text)

    q_att = totals[("question", "✓")] + totals[("question", "✗")]
    p_att = totals[("problem", "✓")] + totals[("problem", "✗")]
    print(f"questions attempted {q_att} (✓ {totals[('question','✓')]}, ✗ {totals[('question','✗')]}); "
          f"problems attempted {p_att}; unmapped nodes {len(unmapped)}")


if __name__ == "__main__":
    main()
