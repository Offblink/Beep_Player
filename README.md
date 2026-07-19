# Beep_Player

**ABC notation → PC speaker beeps.** Drop an `.abc` file, get a melody played through the motherboard speaker.

```
$ bp twinkle
Twinkle Twinkle Little Star  [120BPM C]  42 notes
```

## Install

```bash
# 1. Clone
git clone https://github.com/Offblink/Beep_Player.git
cd Beep_Player

# 2. Add to PATH (so `bp` works from any directory)
export PATH="/path/to/Beep_Player:$PATH"
```

Requires Python 3.10+.

## Usage
```bash
bp twinkle              # Twinkle Twinkle Little Star
bp ode                  # Ode to Joy
bp happy                # Happy Birthday
bp scale                # C Major scale
bp mario                # Super Mario Bros theme

bp my_song.abc           # play your own ABC file
bp my_song.abc --tempo 180   # override tempo (BPM)
bp my_song.abc -o out.bat    # export standalone .bat (double-click to play)
bp my_song.abc -o out.json   # export JSON

bp --list               # list built-in songs
```

## ABC Notation Quick Reference

[ABC notation](https://abcnotation.com/) is a plain-text music notation format — perfect for single-voice melodies.

```
X:1                     # file header (required)
T:Song Title            # title
M:4/4                   # time signature
L:1/4                   # default note length (quarter note)
K:C                     # key signature (C major)

C C G G | A A G2 |      # C D E F G A B — uppercase = middle octave
F F E E | D D C2 |      # lowercase = one octave higher
                        # C2 = half note, C/2 = eighth note
                        # z = rest, | = bar line
                        # ^ = sharp, _ = flat
```

Huge library of ABC tunes at [abcnotation.com](https://abcnotation.com/).

## How It Works

```
.abc file → Python parser → (freq, dur) pairs → PowerShell [Console]::Beep
```

- `bp.py` — ABC parser, ~240 lines, zero dependencies. Generates a temp `.ps1` and runs it.
- `beep_player.cs` — optional native player source (compile with `csc` if you prefer an `.exe`)

## License

MIT
