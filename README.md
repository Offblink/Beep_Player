# bp

**ABC notation → PC speaker beeps.** 给 `.abc` 乐谱文件一个终端命令，它给你蜂鸣。

```
$ bp twinkle
Twinkle Twinkle Little Star  [120BPM C]  42 notes
```

## Install

```bash
# 1. Clone
git clone https://github.com/Offblink/Beep_Player.git
cd Beep_Player

# 2. Build the native player (needs .NET Framework, ships with Windows)
build.cmd

# 3. Alias (add to ~/.bashrc or ~/.zshrc)
alias bp='python /path/to/bp/bp.py'
```

Requires Python 3.10+ (no pip deps) and `csc.exe` (included in any Windows with .NET Framework 4.x).

## Usage

```bash
bp twinkle              # 小星星
bp ode                  # 欢乐颂
bp happy                # 生日快乐
bp scale                # C 大调音阶
bp mario                # 超级玛丽主题

bp my_song.abc          # 播放你自己的 ABC 文件
bp my_song.abc --tempo 180  # 调速 (BPM)
bp my_song.abc -o out.bat   # 导出独立 .bat（可双击播放）
bp my_song.abc -o out.json  # 导出 JSON 数据

bp --list               # 列出内置曲目
```

## ABC Notation Quick Reference

ABC 是一种纯文本记谱法，用来记录单旋律非常方便。

```
X:1                     # 文件头（必须有）
T:Twinkle Twinkle       # 曲名
M:4/4                   # 拍号
L:1/4                   # 默认音符长度（四分音符）
K:C                     # 调号（C 大调）

C C G G | A A G2 |      # C D E F G A B = Do Re Mi Fa Sol La Ti
F F E E | D D C2 |      # 大写=中音区，小写=高八度
                        # C2=二分音符，C/2=八分音符
                        # z=休止符，|=小节线
                        # ^=升号，_=降号
```

网上海量 ABC 曲库：[abcnotation.com](https://abcnotation.com/)，folk / traditional 为主。

## How It Works

```
.abc file → Python parser → (freq, dur) pairs → beep_player.exe → kernel32::Beep
```

- `bp.py` — ABC 解析器，约 240 行，零依赖
- `beep_player.exe` — 编译好的 C# 原生播放器，直接调用 `kernel32::Beep`，零脚本开销
- `build.cmd` — 从 `beep_player.cs` 源码编译

如果 `beep_player.exe` 不存在，自动回退到 PowerShell 播放。

## Why

因为 PC 蜂鸣器很好玩。就这么简单。

## License

MIT
