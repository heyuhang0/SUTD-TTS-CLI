using System;
using System.IO;
using System.Security.Cryptography;

namespace captcha_gen
{
    class Program
    {
        static void Main(string[] args)
        {
            Random r = new Random();

            string outputPath = "dataset";
            Directory.CreateDirectory(outputPath);

            for (int i = 0; i < 1000; i++)
            {
                string captcha = GenerateRandomCode(r);
                RandomImage captchaImage = new RandomImage(captcha.ToString(), 300, 75);
                string savedPath = Path.Combine(outputPath, string.Format("{0}_md5.jpg", captcha));
                captchaImage.Image.Save(savedPath);
                captchaImage.Dispose();

                string md5 = CaculateMD5(savedPath);
                File.Move(savedPath, savedPath.Replace("_md5", string.Format("_{0}", md5)));

                if (i % 100 == 0)
                {
                    Console.WriteLine(string.Format("Progress: {0}", i));
                }
            }
        }

        private static string CaculateMD5(string filename)
        {
            using (var md5 = MD5.Create())
            {
                using (var stream = File.OpenRead(filename))
                {
                    var hash = md5.ComputeHash(stream);
                    return BitConverter.ToString(hash).Replace("-", "").ToLowerInvariant();
                }
            }
        }

        private static string GenerateRandomCode(Random r)
        {
            string s = "";
            for (int j = 0; j < 5; j++)
            {
                int i = r.Next(3);
                int ch;
                switch (i)
                {
                    case 1:
                        ch = r.Next(0, 9);
                        s = s + ch.ToString();
                        break;
                    case 2:
                        ch = r.Next(65, 90);
                        s = s + Convert.ToChar(ch).ToString();
                        break;
                    case 3:
                        ch = r.Next(97, 122);
                        s = s + Convert.ToChar(ch).ToString();
                        break;
                    default:
                        ch = r.Next(97, 122);
                        s = s + Convert.ToChar(ch).ToString();
                        break;
                }
                r.NextDouble();
                r.Next(100, 1999);
            }
            return s;
        }
    }
}
