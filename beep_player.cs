using System;
using System.Diagnostics;
using System.Runtime.InteropServices;

class BeepPlayer
{
    [DllImport("kernel32.dll")]
    static extern bool Beep(int freq, int dur);

    static void Main(string[] args)
    {
        if (args.Length < 2) return;
        var f = args[0].Split(',');
        var d = args[1].Split(',');
        var sw = Stopwatch.StartNew();
        long elapsedTarget = 0;
        for (int i = 0; i < f.Length; i++)
        {
            int freq = int.Parse(f[i]);
            int dur  = int.Parse(d[i]);
            elapsedTarget += dur;
            if (freq > 0) Beep(freq, dur);
            // Sleep exactly the gap between target and reality
            long remaining = elapsedTarget - sw.ElapsedMilliseconds;
            if (remaining > 0)
                System.Threading.Thread.Sleep((int)remaining);
        }
    }
}
