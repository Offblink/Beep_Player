#!/usr/bin/env python3
"""
bp — ABC notation to PC speaker beeps.  Drop an .abc file, get beeps.

Usage:
  bp song.abc             play an ABC file
  bp song.abc -o out.bat  export standalone .bat
  bp song.abc -o out.json export JSON
  bp twinkle              play built-in: twinkle|ode|happy|scale|mario
  bp --list               list built-in songs
  bp song.abc --tempo 180 override tempo (BPM)
"""

import argparse, json, re, subprocess, sys
from dataclasses import dataclass, field
from pathlib import Path

# ── constants ──────────────────────────────────────────────────────────
NOTE_SEMITONES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}

@dataclass
class Note:
    freq: float
    dur_ms: int

@dataclass
class Tune:
    title: str = ""
    tempo: int = 120
    unit_note: str = "1/8"
    key: str = "C"
    notes: list[Note] = field(default_factory=list)

# ── frequency ──────────────────────────────────────────────────────────
def note_to_freq(name: str, acc: int, octave: int) -> float:
    semitone = NOTE_SEMITONES[name.upper()] + acc
    midi = 69 + (octave - 4) * 12 + (semitone - NOTE_SEMITONES["A"])
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))

# ── ABC parser ─────────────────────────────────────────────────────────
NOTE_RE = re.compile(r"(\^+|_+|=)?([A-Ga-g])([']*|[,]*)(\d*/*\d*?)"
                     r"(?=[\s|\]^_=A-Ga-gz\[:\]]|$)")

def parse_dur(s: str) -> float:
    """'2'→2.0  '/2'→0.5  '3/2'→1.5  ''→1.0"""
    s = s.strip()
    if not s: return 1.0
    if "/" in s:
        n, d = s.split("/", 1)
        return (int(n) if n else 1) / (int(d) if d else 2)
    return float(s)

def parse_abc(text: str) -> Tune:
    t = Tune()
    lines = text.split("\n")
    body_start = 0

    for i, line in enumerate(lines):
        line = line.strip()
        if not line: body_start = i + 1; continue
        if ":" in line and line[0].isalpha():
            f, _, v = line.partition(":")
            f, v = f.strip().upper(), v.strip()
            if f == "T": t.title = v
            elif f == "Q":
                m = re.match(r"(?:(\d+/\d+)\s*=\s*)?(\d+)", v)
                if m:
                    if m.group(1): t.unit_note = m.group(1)
                    t.tempo = int(m.group(2))
            elif f == "L": t.unit_note = v
            elif f == "K": t.key = v.split()[0]
            body_start = i + 1
        else:
            body_start = i; break

    # L: field → unit fraction
    if "/" in t.unit_note:
        n, d = t.unit_note.split("/")
        uf = float(n) / float(d)
    else:
        uf = 1.0 / float(t.unit_note) if t.unit_note.isdigit() else 0.125

    base_ms = (60000.0 / t.tempo) * (uf / 0.25)

    # Key signature
    ks = {"C":0,"G":1,"D":2,"A":3,"E":4,"B":5,"F#":6,"C#":7,
          "F":-1,"Bb":-2,"Eb":-3,"Ab":-4,"Db":-5,"Gb":-6,"Cb":-7}
    so = ["F","C","G","D","A","E","B"]; fo = ["B","E","A","D","G","C","F"]
    na = ks.get(t.key.upper(), 0)
    key_acc = {}
    if na > 0:
        for n in so[:na]: key_acc[n] = 1
    elif na < 0:
        for n in fo[:abs(na)]: key_acc[n] = -1

    body = " ".join(lines[body_start:])
    body = re.sub(r'%.*', '', body)
    body = " ".join(body.split())

    pos = 0
    while pos < len(body):
        if body[pos].isspace(): pos += 1; continue

        if body[pos] == "[":
            end = body.index("]", pos) if "]" in body[pos:] else len(body)
            cn = body[pos+1:end]
            best_f, best_d = 0.0, 1.0; cp = 0
            while cp < len(cn):
                m = NOTE_RE.match(cn, cp)
                if not m: cp += 1; continue
                acc_s, note, om, ds = m.group(1) or "", m.group(2), m.group(3) or "", m.group(4) or ""
                acc = key_acc.get(note.upper(), 0)
                if acc_s.startswith("^"): acc = len(acc_s)
                elif acc_s.startswith("_"): acc = -len(acc_s)
                elif acc_s == "=": acc = 0
                octv = 4 if note.isupper() else 5
                octv += om.count("'") - om.count(",")
                fq = note_to_freq(note.upper(), acc, octv)
                dm = parse_dur(ds)
                if fq > best_f: best_f, best_d = fq, dm
                cp = m.end()
            if best_f > 0:
                t.notes.append(Note(freq=best_f, dur_ms=int(best_d * base_ms)))
            pos = end + 1; continue

        if body[pos] == "|":
            pos += 1
            while pos < len(body) and body[pos] in ":[]|": pos += 1
            continue

        m = NOTE_RE.match(body, pos)
        if m:
            acc_s, note, om, ds = m.group(1) or "", m.group(2), m.group(3) or "", m.group(4) or ""
            pos = m.end()

            if note.lower() == "z":
                dm = parse_dur(ds); dur = int(dm * base_ms)
                if dur > 0: t.notes.append(Note(freq=0, dur_ms=dur))
                continue

            acc = key_acc.get(note.upper(), 0)
            if acc_s.startswith("^"): acc = len(acc_s)
            elif acc_s.startswith("_"): acc = -len(acc_s)
            elif acc_s == "=": acc = 0

            octv = 4 if note.isupper() else 5
            octv += om.count("'") - om.count(",")
            fq = note_to_freq(note.upper(), acc, octv)
            dm = parse_dur(ds); dur = int(dm * base_ms)
            if dur > 0: t.notes.append(Note(freq=fq, dur_ms=dur))
            continue
        pos += 1

    return t

# ── output ─────────────────────────────────────────────────────────────
BEEP_EXE = Path(__file__).parent / "beep_player.exe"

def play(notes: list[Note]):
    if not notes: return
    if BEEP_EXE.exists():
        fs = ",".join(str(round(n.freq)) if n.freq > 0 else "0" for n in notes)
        ds = ",".join(str(n.dur_ms) for n in notes)
        subprocess.run([str(BEEP_EXE), fs, ds])
    else:
        # PowerShell fallback — single loop, minimal overhead
        fa = ", ".join(str(round(n.freq)) if n.freq > 0 else "0" for n in notes)
        da = ", ".join(str(n.dur_ms) for n in notes)
        ps = f"$f=@({fa});$d=@({da});for($i=0;$i-lt$f.Count;$i++){{if($f[$i]-eq0){{Start-Sleep -m $d[$i]}}else{{[Console]::Beep($f[$i],$d[$i])}}}}"
        subprocess.run(["powershell", "-NoProfile", "-Command", ps])

def export(notes: list[Note], path: Path):
    suf = path.suffix.lower()
    if suf == ".json":
        path.write_text(json.dumps(
            [{"freq": round(n.freq, 1), "dur": n.dur_ms} for n in notes], indent=2))
    elif suf in (".ps1", ".bat"):
        lines = []
        if suf == ".bat":
            lines = ["@echo off", "echo Playing...", ""]
        for i in range(0, len(notes), 200):
            chunk = []
            for n in notes[i:i+200]:
                if n.freq <= 0:
                    chunk.append(f"Start-Sleep -Milliseconds {n.dur_ms}")
                else:
                    chunk.append(f"[Console]::Beep({round(n.freq)},{n.dur_ms})")
            if suf == ".bat":
                lines.append("powershell -c \"" + "; ".join(chunk) + "\"")
            else:
                lines.extend(chunk)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8" if suf == ".ps1" else None)

# ── built-in songs ─────────────────────────────────────────────────────
SONGS = {
    "twinkle": """X:1\nT:Twinkle Twinkle Little Star\nM:4/4\nL:1/4\nK:C\nC C G G | A A G2 | F F E E | D D C2 |\nG G F F | E E D2 | G G F F | E E D2 |\nC C G G | A A G2 | F F E E | D D C2 |""",
    "ode": """X:1\nT:Ode to Joy\nM:4/4\nL:1/4\nK:C\nE E F G | G F E D | C C D E | E4 D2 |\nE E F G | G F E D | C C D E | D4 C2 |""",
    "happy": """X:1\nT:Happy Birthday\nM:3/4\nL:1/4\nK:C\nG G | A G C2 | B4 G G | G E C2 | B A F F | E C D2 | C4 |""",
    "scale": """X:1\nT:C Major Scale\nM:4/4\nL:1/4\nK:C\nC D E F | G A B c | c B A G | F E D C |""",
    "mario": """X:1\nT:Super Mario Bros\nM:4/4\nL:1/8\nK:C\nE E z E z C E z | G4 z4 |\nc4 z G z4 | E4 z A z B z | ^A A4 |\nG4 E G | A4 F A | G4 E c | B ^A B4 |""",
}

# ── cli ────────────────────────────────────────────────────────────────
def main():
    p = argparse.ArgumentParser(description="bp — ABC notation to PC speaker beeps")
    p.add_argument("input", nargs="?", help="ABC file or built-in song name")
    p.add_argument("-o", "--output", help="Export .bat/.ps1/.json")
    p.add_argument("--tempo", type=int, help="Override tempo (BPM)")
    p.add_argument("--list", action="store_true", help="List built-in songs")
    args = p.parse_args()

    if args.list:
        print("Built-in songs:")
        for k, v in SONGS.items():
            t = re.search(r"T:(.+)", v)
            print(f"  {k:10s} — {t.group(1) if t else '?'}")
        return

    if not args.input:
        p.print_help(); return

    if args.input in SONGS:
        text = SONGS[args.input]
    else:
        fp = Path(args.input)
        if not fp.exists():
            print(f"bp: '{args.input}' not found", file=sys.stderr)
            print("Use --list for built-in songs", file=sys.stderr)
            sys.exit(1)
        text = fp.read_text(encoding="utf-8")

    tune = parse_abc(text)
    if args.tempo: tune.tempo = args.tempo

    print(f"{tune.title}  [{tune.tempo}BPM {tune.key}]  {len(tune.notes)} notes")

    if args.output:
        export(tune.notes, Path(args.output))
        print(f"  -> {args.output}")
    else:
        play(tune.notes)

if __name__ == "__main__":
    main()
