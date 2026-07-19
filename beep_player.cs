using System;
using System.Diagnostics;
using System.Runtime.InteropServices;

class BeepPlayer
{
    [DllImport("kernel32.dll")]
    static extern bool Beep(int freq, int dur);

    const int MAX_BEEP_MS = 500;

    static void Main(string[] args)
    {
        if (args.Length < 2) return;
        var f = args[0].Split(',');
        var d = args[1].Split(',');
        var sw = Stopwatch.StartNew();
        long target = 0;
        for (int i = 0; i < f.Length; i++)
        {
            int freq = int.Parse(f[i]);
            int dur  = int.Parse(d[i]);
            target += dur;
            if (freq > 0)
            {
                int remaining = dur;
                while (remaining > 0)
                {
                    int chunk = Math.Min(remaining, MAX_BEEP_MS);
                    Beep(freq, chunk);
                    remaining -= chunk;
                }
            }
            else System.Threading.Thread.Sleep(dur);
            while (sw.ElapsedMilliseconds < target)
                System.Threading.Thread.Sleep(1);
        }
        while (sw.ElapsedMilliseconds < target)
            System.Threading.Thread.Sleep(1);
    }
}
