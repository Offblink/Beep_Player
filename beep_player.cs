using System;
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
        for (int i = 0; i < f.Length; i++)
        {
            int freq = int.Parse(f[i]);
            int dur  = int.Parse(d[i]);
            if (freq > 0) Beep(freq, dur);
            else System.Threading.Thread.Sleep(dur);
        }
    }
}
