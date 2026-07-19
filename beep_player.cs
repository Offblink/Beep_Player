using System;
using System.Diagnostics;
using System.Runtime.InteropServices;

class BeepPlayer
{
    [DllImport("kernel32.dll")]
    static extern bool Beep(int freq, int dur);

    const int MAX_CHUNK = 500;
    const int MIN_CHUNK = 50;
    const int FREQ_SWITCH_GAP = 15;

    static void DoBeep(int freq, int durMs)
    {
        int remaining = durMs;
        while (remaining >= MIN_CHUNK)
        {
            int chunk = Math.Min(remaining, MAX_CHUNK);
            Beep(freq, chunk);
            remaining -= chunk;
        }
    }

    static void Main(string[] args)
    {
        if (args.Length < 2) return;
        var f = args[0].Split(',');
        var d = args[1].Split(',');
        var sw = Stopwatch.StartNew();
        long target = 0;
        int prevFreq = 0;
        for (int i = 0; i < f.Length; i++)
        {
            int freq = int.Parse(f[i]);
            int dur  = int.Parse(d[i]);
            if (freq > 0)
            {
                if (prevFreq > 0 && freq != prevFreq)
                {
                    target += FREQ_SWITCH_GAP;
                    System.Threading.Thread.Sleep(FREQ_SWITCH_GAP);
                }
                target += dur;
                DoBeep(freq, dur);
                prevFreq = freq;
            }
            else
            {
                target += dur;
                System.Threading.Thread.Sleep(dur);
                prevFreq = 0;
            }
            while (sw.ElapsedMilliseconds < target)
                System.Threading.Thread.Sleep(10);
        }
        while (sw.ElapsedMilliseconds < target)
            System.Threading.Thread.Sleep(10);
    }
}
