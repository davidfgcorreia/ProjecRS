import os
import re



def parse_and_write(input_file="../storage/output_file_promt_ai/output_indexes.txt", output_dir="../storage/parsed_output_tables"):
    os.makedirs(output_dir, exist_ok=True)
    with open(input_file, "r", encoding="utf-8") as infile:
        for line in infile:
            line = line.strip()
            if not line or ";" not in line:
                continue
            # Check for main restrictors in square brackets after base name
            match = re.match(r"^([^\\[\];]+)\s*(\[[^\]]*\])?\s*;\s*(.*)$", line)
            if not match:
                continue
            base = match.group(1).strip()
            restrictors = match.group(2)
            rest = match.group(3).strip()
            # Split on semicolons not inside curly braces
            def split_outside_curly(s):
                segments = []
                current = []
                depth = 0
                for c in s:
                    if c == '{':
                        depth += 1
                    elif c == '}':
                        if depth > 0:
                            depth -= 1
                    if c == ';' and depth == 0:
                        segments.append(''.join(current).strip())
                        current = []
                    else:
                        current.append(c)
                if current:
                    segments.append(''.join(current).strip())
                return [seg for seg in segments if seg]
            segments = split_outside_curly(rest)
            output_path = os.path.join(output_dir, f"{base}.txt")
            parsed_lines = []
            if restrictors:
                restrictors = restrictors.strip()
                parsed_lines.append(f"main_restrictors : {restrictors}")
            # Roman numeral regex: I, II, III, IV, V, VI, VII, VIII, IX, X, with optional a/b/c suffix
            roman_regex = re.compile(r"^(I{1,3}|IV|V|VI{0,3}|VII{0,1}|VIII|IX|X)([abc])?$", re.IGNORECASE)
            new_segments = []
            for seg in segments:
                if seg.lower().startswith("rct phase"):
                    key, sep, value = seg.partition(":")
                    value = value.strip()
                    if value and not roman_regex.match(value):
                        # Remove value if not roman numeral or small variation
                        new_segments.append(f"{key.strip()}: ")
                    else:
                        new_segments.append(seg)
                else:
                    new_segments.append(seg)
            parsed_lines.extend(new_segments)
            with open(output_path, "w", encoding="utf-8") as outfile:
                outfile.write("\n".join(parsed_lines) + "\n")

if __name__ == "__main__":
    parse_and_write()
