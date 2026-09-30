Console.OutputEncoding = System.Text.Encoding.UTF8;
string[] tests = {
  "“我们要在80天之内环游地球一周。”他提出这个惊人的计划时，神情十分平静。",
  "斐利亚·福格先生<i>提早</i>从改良俱乐部回家了——坐的是新式蒸汽车。",
  "<color=#8ab>点击伦敦</color> 开始",
  "This is a test sentence for the splitter.",
  "我带着1000镑（约合25000法郎）去了<i>Henrietta</i>号！",
};
foreach (var t in tests)
  Console.WriteLine(string.Join(" | ", CNText.Split(t, " ".ToCharArray(), StringSplitOptions.RemoveEmptyEntries)));
