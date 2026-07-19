using System;
using System.Runtime.InteropServices;

class BeepPlayer
{
    [DllImport("kernel32.dll")]
    static extern bool Beep(int freq, int dur);

    const int MAX_CHUNK = 500;

    static void Main(string[] args)
    {
        if (args.Length < 2) return;
        var f = args[0].Split(',');
        var d = args[1].Split(',');
        for (int i = 0; i < f.Length; i++)
        {
            int freq = int.Parse(f[i]);
            int dur  = int.Parse(d[i]);
            if (freq > 0)
            {
                int remaining = dur;
                while (remaining > 0)
                {
                    int chunk = Math.Min(remaining, MAX_CHUNK);
                    Beep(freq, chunk);
                    remaining -= chunk;
                }
                System.Threading.Thread.Sleep(dur + 5);
            }
            else
            {
                System.Threading.Thread.Sleep(dur);
            }
        }
    }
}
