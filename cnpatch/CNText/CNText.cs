// 80 Days 汉化辅助：让逐词排版的剧情文字支持中文（逐字切分 + 中文间不加词间距 + 简单避头尾）
using System;
using System.Collections.Generic;
using System.Text;
using UnityEngine;
using TMPro;

public static class CNText
{
    const string NoStart = "，。！？、；：”’）》」』…—·%％";   // 不能出现在行首
    const string NoEnd = "“‘（《「『";                         // 不能出现在行尾

    public static bool IsCJK(char c)
    {
        return (c >= 0x2E80 && c <= 0x9FFF) || (c >= 0xF900 && c <= 0xFAFF) || (c >= 0xFF00 && c <= 0xFFEF)
            || (c >= 0x3000 && c <= 0x303F) || c == '\u201C' || c == '\u201D' || c == '\u2018' || c == '\u2019'
            || c == '\u2026' || c == '\u2014' || c == '\u00B7';
    }

    static bool HasCJK(string s)
    {
        for (int i = 0; i < s.Length; i++) if (IsCJK(s[i])) return true;
        return false;
    }

    static string TagName(string tag)
    {
        int i = tag.StartsWith("</") ? 2 : 1, j = i;
        while (j < tag.Length && tag[j] != '=' && tag[j] != '>' && tag[j] != ' ') j++;
        return tag.Substring(i, j - i).ToLowerInvariant();
    }

    static void UpdateTags(List<string> open, string tag)
    {
        string name = TagName(tag);
        if (tag.StartsWith("</"))
        {
            for (int k = open.Count - 1; k >= 0; k--)
                if (TagName(open[k]) == name) { open.RemoveAt(k); break; }
        }
        else if (name != "br" && name != "sprite" && name != "space" && !tag.EndsWith("/>"))
            open.Add(tag);
    }

    // 与 string.Split(char[], StringSplitOptions) 同参数，便于直接替换调用
    public static string[] Split(string s, char[] sep, StringSplitOptions opt)
    {
        string[] parts = s.Split(sep, opt);
        if (!HasCJK(s)) return parts;
        List<string> res = new List<string>();
        foreach (string p in parts)
        {
            if (!HasCJK(p)) { res.Add(p); continue; }
            List<string> open = new List<string>();
            StringBuilder cur = new StringBuilder();
            bool visible = false, onlyNoEnd = true;
            int i = 0;
            while (i < p.Length)
            {
                char c = p[i];
                if (c == '<')
                {
                    int j = p.IndexOf('>', i);
                    if (j > i)
                    {
                        string tag = p.Substring(i, j - i + 1);
                        cur.Append(tag); UpdateTags(open, tag); i = j + 1; continue;
                    }
                }
                string unit; bool cjk = IsCJK(c);
                if (cjk) { unit = c.ToString(); i++; }
                else
                {
                    int j = i;
                    while (j < p.Length && !IsCJK(p[j]) && p[j] != '<') j++;
                    if (j == i) j = i + 1;
                    unit = p.Substring(i, j - i); i = j;
                }
                bool attach = !visible || onlyNoEnd || (cjk && NoStart.IndexOf(c) >= 0)
                              || (!cjk && char.IsPunctuation(unit[0]));
                if (!attach)
                {
                    res.Add(cur.ToString()); cur.Length = 0;
                    foreach (string t in open) cur.Append(t);
                    onlyNoEnd = true;
                }
                cur.Append(unit); visible = true;
                if (!(unit.Length == 1 && NoEnd.IndexOf(unit[0]) >= 0)) onlyNoEnd = false;
            }
            if (cur.Length > 0) res.Add(cur.ToString());
        }
        return res.ToArray();
    }

    static char EdgeChar(string s, bool last)
    {
        // 跳过富文本标签，取第一个/最后一个可见字符
        if (!last)
        {
            for (int i = 0; i < s.Length; i++)
            {
                if (s[i] == '<') { int j = s.IndexOf('>', i); if (j > i) { i = j; continue; } }
                return s[i];
            }
        }
        else
        {
            for (int i = s.Length - 1; i >= 0; i--)
            {
                if (s[i] == '>') { int j = s.LastIndexOf('<', i); if (j >= 0) { i = j; continue; } }
                return s[i];
            }
        }
        return ' ';
    }

    static string Txt(Transform t)
    {
        TMP_Text x = t.GetComponent<TMP_Text>();
        return x == null ? null : x.text;
    }

    // 中文逐字切分后“词”数约为英文的 3 倍，淡入速度同比放大，保持原有阅读节奏
    public static float Speed(float wordsPerSecond)
    {
        return wordsPerSecond * 3f;
    }

    // 词后间距：当前词以中文结尾，或下一个词以中文开头，则不加空隙
    public static float Gap(float spaceWidth, Component word)
    {
        try
        {
            Transform t = word.transform, p = t.parent;
            string cur = Txt(t);
            if (cur == null || p == null) return spaceWidth;
            if (IsCJK(EdgeChar(cur, true))) return 0f;
            int idx = t.GetSiblingIndex();
            if (idx + 1 < p.childCount)
            {
                string nx = Txt(p.GetChild(idx + 1));
                if (nx != null && IsCJK(EdgeChar(nx, false))) return 0f;
            }
        }
        catch (Exception) { }
        return spaceWidth;
    }

    // 物品详情里的 npcTypes（数据 id）显示为中文
    static readonly string[][] Npc = {
        new[]{"sea-dog","老水手"}, new[]{"posh","上流"}, new[]{"prim","拘谨"}, new[]{"foreign","外国"}, new[]{"wistful","多愁善感"},
        new[]{"sour","尖酸"}, new[]{"stalwart","刚毅"}, new[]{"stubborn","固执"}, new[]{"feminine","淑女"}, new[]{"suspicious","多疑"},
        new[]{"humorous","幽默"}, new[]{"excitable","易激动"}, new[]{"earnest","认真"}, new[]{"soldier","军人"}, new[]{"poor","穷苦"},
        new[]{"luxurious","讲究享受"}, new[]{"official","官员"} };
    public static string NpcWords(string s)
    {
        if (string.IsNullOrEmpty(s) || s.IndexOf("类型的人") < 0) return s;
        foreach (var p in Npc) s = System.Text.RegularExpressions.Regex.Replace(s, @"(?<![A-Za-z-])" + System.Text.RegularExpressions.Regex.Escape(p[0]) + @"(?![A-Za-z-])", p[1]);
        return s;
    }

    // journey.SubstituteWord 找不到替换词时会原样返回英文键
    public static string Sub(string s)
    {
        switch (s)
        {
            case "luggage rack": return "行李架";
            case "extra space": return "额外空间";
            case "driver": return "司机";
            case "departure": return "出发";
        }
        return s;
    }

    // 交通类别 / 介质 id -> 中文（数据里这些是 id，只在显示时翻译）
    public static string Cat(string s)
    {
        if (s == null) return s;
        switch (s.ToLowerInvariant())
        {
            case "trains": return "火车";
            case "inventions": return "新发明";
            case "steamships": return "蒸汽船";
            case "airships": return "飞艇";
            case "mechanical animals": return "机械兽";
            case "animals": return "牲畜";
            case "cars": return "汽车";
            case "carriages": return "马车";
            case "boats": return "船";
            case "sea": return "海路";
            case "land": return "陆路";
            case "air": return "空路";
            case "unknown": return "未知方式";
        }
        return s;
    }

    static readonly System.Text.RegularExpressions.Regex SpaceNearCJK = new System.Text.RegularExpressions.Regex(
        @"(?<=[\u2E80-\u9FFF\uFF00-\uFFEF\u3000-\u303F\u201C\u201D\u2026\u2014](?:<[^>]*>)*) +|(?<!\.) +(?=(?:<[^>]*>)*[\u2E80-\u9FFF\uFF00-\uFFEF\u3000-\u303F\u201C\u201D\u2026\u2014])");
    static readonly System.Text.RegularExpressions.Regex AsciiPunctAfterCJK = new System.Text.RegularExpressions.Regex(
        @"(?<=[\u2E80-\u9FFF\u3000-\u303F\uFF00-\uFFEF](?:<[^>]*>)*)([?!,:;])");

    // 拼句后的清理：去掉中文旁边的英文空格、半角标点改全角、去重复句号
    public static string Tidy(string s)
    {
        if (string.IsNullOrEmpty(s) || !HasCJK(s)) return s;
        s = SpaceNearCJK.Replace(s, "");
        s = AsciiPunctAfterCJK.Replace(s, m =>
        {
            switch (m.Value) { case "?": return "？"; case "!": return "！"; case ",": return "，"; case ":": return "："; default: return "；"; }
        });
        s = s.Replace("的的", "的").Replace("。？", "？").Replace("。。", "。").Replace("，。", "。").Replace("：。", "。").Replace("？。", "？").Replace("！。", "！").Replace("，，", "，").Replace("：，", "：").Replace("，：", "：");
        return s;
    }

    // 剧情段落拼接后的重复标点（片段 A 结尾和片段 B 开头都带标点）
    static readonly System.Text.RegularExpressions.Regex PunctA = new System.Text.RegularExpressions.Regex("([。！？])[ ]*[。，]");
    static readonly System.Text.RegularExpressions.Regex PunctB = new System.Text.RegularExpressions.Regex("[，：][ ]*([。，])");
    static readonly System.Text.RegularExpressions.Regex PunctC = new System.Text.RegularExpressions.Regex("[。][ ]*([？！])");
    public static string Punct(string s)
    {
        if (string.IsNullOrEmpty(s) || !HasCJK(s)) return s;
        try
        {
            s = PunctA.Replace(s, "$1");
            s = PunctB.Replace(s, m => m.Value[0] == '：' && m.Groups[1].Value == "，" ? "：" : m.Groups[1].Value);
            s = PunctC.Replace(s, "$1");
        }
        catch { }
        return s;
    }

    // ---- 界面短标签 / 时钟 / 时间（截图反馈：MARKET、SATURDAY、11:22 PM、7am 等仍是英文）----
    static readonly Dictionary<string, string> UIMap = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
    {
        {"MARKET","市场"},{"BANK","银行"},{"HOTEL","旅馆"},{"PLAN","计划"},{"EXPLORE","探索"},{"WAIT","等待"},
        {"CONVERSE","交谈"},{"TALK","交谈"},{"CHAT","闲聊"},{"BEG","乞讨"},{"RETURN","返回"},{"BEGIN","开始"},
        {"FOGG","福格"},{"LUGGAGE","行李"},{"DEPART","出发"},{"LEAVE","离开"},{"REST","休息"},{"SLEEP","睡觉"},
        {"STAY","留宿"},{"CONTINUE","继续"},{"BACK","返回"},{"JOURNEY","旅程"},{"ROUTES","路线"},{"MAP","地图"},
        {"TELEGRAM","电报"},{"SHOP","商店"},{"SELL","出售"},{"BUY","购买"},{"CLOSE","关闭"},{"CANCEL","取消"},
        {"DONE","完成"},{"NEXT","下一步"},{"HELP","帮助"},{"SETTINGS","设置"},{"QUIT","退出"},{"SAVE","保存"},
        {"LOAD","读取"},{"TRAVEL","旅行"},{"BOARD","登船"},{"EMBARK","启程"},{"ASK","打听"},{"WALK","散步"},
        {"SUNDAY","星期日"},{"MONDAY","星期一"},{"TUESDAY","星期二"},{"WEDNESDAY","星期三"},{"THURSDAY","星期四"},{"FRIDAY","星期五"},{"SATURDAY","星期六"},
        {"Noon","中午"},{"12 noon","中午12点"},{"Midnight","午夜"},
    };
    static readonly System.Text.RegularExpressions.Regex DayRx = new System.Text.RegularExpressions.Regex(@"^\s*(<b>)?\s*(?:DAY|Day|天数|第)\s*(</b>)?\s*(<b>)?\s*(\d+)\s*(</b>)?\s*天?\s*$");
    static readonly System.Text.RegularExpressions.Regex ClockRx = new System.Text.RegularExpressions.Regex(@"(?<![0-9:])(\d{1,2})(?::(\d\d))?\s?(AM|PM|am|pm|a\.m\.|p\.m\.)(?![A-Za-z])");
    static string Period(int h24) { return h24 < 5 ? "凌晨" : h24 < 12 ? "上午" : h24 < 13 ? "中午" : h24 < 18 ? "下午" : "晚上"; }
    // 11:22 PM -> 晚上11:22；7am -> 上午7点
    public static string Time(string s)
    {
        if (string.IsNullOrEmpty(s)) return s;
        try
        {
            return ClockRx.Replace(s, m =>
            {
                int h = int.Parse(m.Groups[1].Value); bool pm = m.Groups[3].Value.ToLowerInvariant().StartsWith("p");
                int h24 = (h % 12) + (pm ? 12 : 0);
                string p = Period(h24);
                return m.Groups[2].Success ? p + h + ":" + m.Groups[2].Value : p + h + "点";
            });
        }
        catch { return s; }
    }
    static readonly HashSet<string> Seen = new HashSet<string>();
    public static string UI(string s)
    {
        if (string.IsNullOrEmpty(s)) return s;
        try
        {
            string t = s.Trim(), z;
            if (UIMap.TryGetValue(t, out z)) return z;
            var m = DayRx.Match(s);
            if (m.Success) { if (m.Groups[1].Success) return "<b>第" + m.Groups[4].Value + "天</b>"; if (m.Groups[3].Success) return "第<b>" + m.Groups[4].Value + "</b>天"; return "第" + m.Groups[4].Value + "天"; }
            s = Time(s);
            // 记录仍含英文单词的界面文字，方便以后补译（写到游戏目录 cn_untranslated.txt）
            if (System.Text.RegularExpressions.Regex.IsMatch(s, "[A-Za-z]{3,}") && Seen.Add(s))
                System.IO.File.AppendAllText("cn_untranslated.txt", s.Replace("\n", "\\n") + "\n");
        }
        catch { }
        return s;
    }
}
