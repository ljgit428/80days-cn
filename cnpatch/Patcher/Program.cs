// 给 Assembly-CSharp.dll 打中文排版补丁（始终以 ORIGINAL_BACKUP 里的原版为源，可重复执行）
using Mono.Cecil;
using Mono.Cecil.Cil;
using Mono.Cecil.Rocks;

var managed = @"F:\Games\80 Days\80 Days_Data\Managed";
var src = @"D:\git\project\80 days CN\ORIGINAL_BACKUP\80 Days_Data\Managed\Assembly-CSharp.dll";
var helperPath = Path.Combine(managed, "CNText.dll");
var outPath = @"D:\git\project\80 days CN\patched\Assembly-CSharp.dll";

var projRoot = @"D:\git\project\80 days CN";
var resolver = new DefaultAssemblyResolver();
resolver.AddSearchDirectory(managed);
var rp = new ReaderParameters { AssemblyResolver = resolver, ReadingMode = ReadingMode.Immediate };
var asm = AssemblyDefinition.ReadAssembly(src, rp);
var helper = AssemblyDefinition.ReadAssembly(helperPath, rp);
var ht = helper.MainModule.GetType("CNText");
var mod = asm.MainModule;

// dump 模式：列出所有字符串常量（类型::方法 \t 字面量 JSON）
if (args.Length > 0 && args[0] == "dump")
{
    using var w = new StreamWriter(args[1], false, new System.Text.UTF8Encoding(false));
    foreach (var t in mod.GetTypes())
        foreach (var m in t.Methods.Where(m => m.HasBody))
            foreach (var i in m.Body.Instructions.Where(i => i.OpCode == OpCodes.Ldstr))
                w.WriteLine(t.FullName + "::" + m.Name + "\t" + System.Text.Json.JsonSerializer.Serialize((string)i.Operand, new System.Text.Json.JsonSerializerOptions { Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping }));
    Console.WriteLine("dumped");
    return 0;
}
var split = mod.ImportReference(ht.Methods.First(m => m.Name == "Split"));
var gap = mod.ImportReference(ht.Methods.First(m => m.Name == "Gap"));

// 1) StorySentenceElement.AddTextElements: string.Split -> CNText.Split
var sse = mod.GetType("GameViews.Story.StorySentenceElement");
var add = sse.Methods.First(m => m.Name == "AddTextElements");
int n1 = 0;
foreach (var ins in add.Body.Instructions)
    if ((ins.OpCode == OpCodes.Callvirt || ins.OpCode == OpCodes.Call) && ins.Operand is MethodReference mr
        && mr.Name == "Split" && mr.DeclaringType.FullName == "System.String" && mr.Parameters.Count == 2)
    { ins.OpCode = OpCodes.Call; ins.Operand = split; n1++; }

// 2) SentenceLayoutController.PerformLayout: spaceWidth -> CNText.Gap(spaceWidth, 当前词)
var slc = mod.GetType("SentenceLayoutController");
var pl = slc.Methods.First(m => m.Name == "PerformLayout");
pl.Body.SimplifyMacros();
var il = pl.Body.GetILProcessor();
var wordVar = pl.Body.Variables.First(v => v.VariableType.Name == "AnimatableRect");
var targets = pl.Body.Instructions.Where(i => i.OpCode == OpCodes.Ldfld && ((FieldReference)i.Operand).Name == "spaceWidth").ToList();
foreach (var t in targets)
{
    var a = il.Create(OpCodes.Ldloc, wordVar);
    var b = il.Create(OpCodes.Call, gap);
    il.InsertAfter(t, a); il.InsertAfter(a, b);
}
pl.Body.OptimizeMacros();

// 3) StorySentenceElement 内所有读取 fadeInHorizontalSpeed 的地方 -> CNText.Speed(x)
var speed = mod.ImportReference(ht.Methods.First(m => m.Name == "Speed"));
int n3 = 0;
foreach (var m in sse.Methods.Where(m => m.HasBody))
{
    var loads = m.Body.Instructions.Where(i => i.OpCode == OpCodes.Ldfld && ((FieldReference)i.Operand).Name == "fadeInHorizontalSpeed").ToList();
    if (loads.Count == 0) continue;
    m.Body.SimplifyMacros();
    var ilp = m.Body.GetILProcessor();
    foreach (var t in loads) { ilp.InsertAfter(t, ilp.Create(OpCodes.Call, speed)); n3++; }
    m.Body.OptimizeMacros();
}
Console.WriteLine($"fadeInHorizontalSpeed 注入 {n3} 处");
Console.WriteLine($"Split 替换 {n1} 处, spaceWidth 注入 {targets.Count} 处 (词变量 V_{wordVar.Index})");
if (n1 != 1 || targets.Count != 2) { Console.WriteLine("注入点数量不符，放弃写入"); return 1; }
// 4) 代码里写死的英文：按 translation/code_strings.json 替换 ldstr
//    格式 {"类型::方法": {"英文": "中文"}, "*": {"英文": "中文"}}（"*" 为全局）
// 本地明文（不入库）优先；否则用公开的哈希键版本（键为 "#"+sha1(英文)前16位）
var csPath = Path.Combine(projRoot, "translation", "code_strings.json");
if (!File.Exists(csPath)) csPath = Path.Combine(projRoot, "translation", "hashed", "code_strings.json");
static string HK(string s) { using var sha = System.Security.Cryptography.SHA1.Create(); return "#" + Convert.ToHexString(sha.ComputeHash(System.Text.Encoding.UTF8.GetBytes(s))).ToLowerInvariant().Substring(0, 16); }
int n4 = 0;
if (File.Exists(csPath))
{
    var cs = System.Text.Json.JsonSerializer.Deserialize<Dictionary<string, Dictionary<string, string>>>(File.ReadAllText(csPath));
    cs.TryGetValue("*", out var glob);
    foreach (var t in mod.GetTypes())
        foreach (var m in t.Methods.Where(m => m.HasBody))
        {
            cs.TryGetValue(t.FullName + "::" + m.Name, out var loc);
            cs.TryGetValue(t.FullName + "::*", out var typ);
            foreach (var i in m.Body.Instructions.Where(i => i.OpCode == OpCodes.Ldstr))
            {
                var o = (string)i.Operand; string z = null;
                var h = HK(o);
                bool Get(Dictionary<string, string> d) => d != null && (d.TryGetValue(o, out z) || d.TryGetValue(h, out z));
                if (Get(loc) || Get(typ) || Get(glob)) { i.Operand = z == "@=" ? o : z; n4++; }
            }
        }
}
Console.WriteLine($"代码字符串替换 {n4} 处");

// 5) TextGen.Numbers.WordFromValue(int) -> value.ToString()（数字一律用阿拉伯数字）
var wfv = mod.GetType("TextGen/Numbers").Methods.First(m => m.Name == "WordFromValue");
{
    var body = wfv.Body; body.Instructions.Clear(); body.ExceptionHandlers.Clear(); body.Variables.Clear();
    var p = body.GetILProcessor();
    p.Append(p.Create(OpCodes.Ldarga_S, wfv.Parameters[0]));
    p.Append(p.Create(OpCodes.Call, mod.ImportReference(mod.TypeSystem.Int32.Resolve().Methods.First(m => m.Name == "ToString" && m.Parameters.Count == 0))));
    p.Append(p.Create(OpCodes.Ret));
}

// 6) TextGen.DetailTextForItem 的返回值过一遍 CNText.NpcWords（npcTypes 是数据 id，只在显示时翻译）
var npcw = mod.ImportReference(ht.Methods.First(m => m.Name == "NpcWords"));
var dti = mod.GetType("TextGen").Methods.First(m => m.Name == "DetailTextForItem");
{
    dti.Body.SimplifyMacros();
    var p = dti.Body.GetILProcessor();
    foreach (var r in dti.Body.Instructions.Where(i => i.OpCode == OpCodes.Ret).ToList())
    { r.OpCode = OpCodes.Call; r.Operand = npcw; p.InsertAfter(r, p.Create(OpCodes.Ret)); }
    dti.Body.OptimizeMacros();
}

// 7) TextGen/Luggage 里 SubstituteWord 的结果过 CNText.Sub（缺省英文键 -> 中文）
var sub = mod.ImportReference(ht.Methods.First(m => m.Name == "Sub"));
int n7 = 0;
foreach (var m in mod.GetType("TextGen/Luggage").Methods.Where(m => m.HasBody))
{
    m.Body.SimplifyMacros();
    var p = m.Body.GetILProcessor();
    foreach (var c in m.Body.Instructions.Where(i => (i.OpCode == OpCodes.Callvirt || i.OpCode == OpCodes.Call) && i.Operand is MethodReference r && r.Name == "SubstituteWord").ToList())
    { p.InsertAfter(c, p.Create(OpCodes.Call, sub)); n7++; }
    m.Body.OptimizeMacros();
}
Console.WriteLine($"SubstituteWord 包装 {n7} 处");

// 8) Clue.ContentFor*InContext 方法体 -> CNClue.Text(this, kind, context)（中文线索生成器）
var clueType = mod.GetType("GameData.Clues.Clue");
var cnclue = mod.ImportReference(helper.MainModule.GetType("CNClue").Methods.First(m => m.Name == "Text"));
var kinds = new[] { "ContentForCityLackingAmenityClueInContext", "ContentForCitySellItemForMoneyInContext", "ContentForCitySellingPreciousItemClueInContext",
    "ContentForJourneyInContext", "ContentForJourneyConnectsWithJourneyInContext", "ContentForCityReachableViaCityInContext" };
for (int k = 0; k < kinds.Length; k++)
{
    var m = clueType.Methods.First(x => x.Name == kinds[k]);
    var body = m.Body; body.Instructions.Clear(); body.ExceptionHandlers.Clear(); body.Variables.Clear();
    var p = body.GetILProcessor();
    p.Append(p.Create(OpCodes.Ldarg_0));
    p.Append(p.Create(OpCodes.Ldc_I4, k));
    p.Append(p.Create(OpCodes.Ldarg_1));
    p.Append(p.Create(OpCodes.Call, cnclue));
    p.Append(p.Create(OpCodes.Ret));
}
Console.WriteLine($"线索生成器替换 {kinds.Length} 个方法");

// 9) 拼句结果过 CNText.Tidy（去中文旁空格、半角标点转全角）
var tidy = mod.ImportReference(ht.Methods.First(m => m.Name == "Tidy"));
var tidyTargets = new List<MethodDefinition>();
var conv = mod.GetType("Conversation");
tidyTargets.AddRange(conv.Methods.Where(m => m.Name == "get_playerDialog" || m.Name == "get_characterDialog" || m.Name == "get_subHeading"));
tidyTargets.Add(clueType.Methods.First(m => m.Name == "StatementInContext"));
tidyTargets.Add(mod.GetType("InsertClueFromGenericLocal").Methods.First(m => m.Name == "get_generatedText"));
foreach (var t in new[] { "TextGen", "TextGen/Calendar", "TextGen/Luggage", "TextGen/Money", "TextGen/Lists" })
    tidyTargets.AddRange(mod.GetType(t).Methods.Where(m => m.HasBody && m.IsPublic && m.ReturnType.FullName == "System.String"));
foreach (var t in new[] { "Game.Player.Player", "GameViews.InfoCard.DepartureInfoCard" })
    tidyTargets.AddRange(mod.GetType(t).Methods.Where(m => m.HasBody && m.ReturnType.FullName == "System.String" && (m.Name == "get_descriptionOfSituation" || m.Name == "DescriptionOfDaysUntilNextSailingOf")));
int n9 = 0;
foreach (var m in tidyTargets.Distinct())
{
    m.Body.SimplifyMacros();
    var p = m.Body.GetILProcessor();
    foreach (var r in m.Body.Instructions.Where(i => i.OpCode == OpCodes.Ret).ToList())
    { r.OpCode = OpCodes.Call; r.Operand = tidy; p.InsertAfter(r, p.Create(OpCodes.Ret)); n9++; }
    m.Body.OptimizeMacros();
}
Console.WriteLine($"Tidy 包装 {n9} 处");

// 10) 交通类别 id 显示成中文：Conversation 里的 transportCategory、OverviewView 里 ToUpper 之前
var cat = mod.ImportReference(ht.Methods.First(m => m.Name == "Cat"));
int n10 = 0;
foreach (var m in conv.Methods.Where(m => m.HasBody))
{
    m.Body.SimplifyMacros();
    var p = m.Body.GetILProcessor();
    foreach (var c in m.Body.Instructions.Where(i => i.OpCode == OpCodes.Callvirt && i.Operand is MethodReference r && r.Name == "get_transportCategory").ToList())
    { p.InsertAfter(c, p.Create(OpCodes.Call, cat)); n10++; }
    m.Body.OptimizeMacros();
}
{
    var m = mod.GetType("GameViews.Overview.OverviewView").Methods.First(x => x.Name == "GenerateCarouselTitles");
    m.Body.SimplifyMacros();
    var p = m.Body.GetILProcessor();
    foreach (var c in m.Body.Instructions.Where(i => i.OpCode == OpCodes.Callvirt && i.Operand is MethodReference r && r.Name == "ToUpper" && r.Parameters.Count == 0).ToList())
    { p.InsertBefore(c, p.Create(OpCodes.Call, cat)); n10++; }
    m.Body.OptimizeMacros();
}
Console.WriteLine($"类别名包装 {n10} 处");

// 11) 剧情段落排版后去掉拼接产生的重复标点（CNText.Punct）
{
    var punct = mod.ImportReference(ht.Methods.First(m => m.Name == "Punct"));
    var m = mod.GetType("TextMarkup/PunctuationAndSpacing").Methods.First(x => x.Name == "CorrectSpacingAndPunctuation");
    m.Body.SimplifyMacros();
    var p = m.Body.GetILProcessor();
    int n11 = 0;
    foreach (var r in m.Body.Instructions.Where(i => i.OpCode == OpCodes.Ret).ToList())
    { r.OpCode = OpCodes.Call; r.Operand = punct; p.InsertAfter(r, p.Create(OpCodes.Ret)); n11++; }
    m.Body.OptimizeMacros();
    Console.WriteLine($"标点整理包装 {n11} 处");
}

// 12) 界面短标签 / 时钟 / 12 小时制时间（CNText.UI、CNText.Time）
{
    var ui = mod.ImportReference(ht.Methods.First(m => m.Name == "UI"));
    var tm = mod.ImportReference(ht.Methods.First(m => m.Name == "Time"));
    int n12 = 0;
    void WrapRet(MethodDefinition m, MethodReference f)
    {
        m.Body.SimplifyMacros();
        var p = m.Body.GetILProcessor();
        foreach (var r in m.Body.Instructions.Where(i => i.OpCode == OpCodes.Ret).ToList())
        { r.OpCode = OpCodes.Call; r.Operand = f; p.InsertAfter(r, p.Create(OpCodes.Ret)); n12++; }
        m.Body.OptimizeMacros();
    }
    var clk = mod.GetType("GameViews.ClockUpdater");
    foreach (var name in new[] { "get_currentDayString", "get_currentWeekdayString", "get_currentTimeString" })
        WrapRet(clk.Methods.First(m => m.Name == name), ui);
    WrapRet(mod.GetType("GameViews.Departure.DepartureView").Methods.First(m => m.Name == "get_departureTimeString"), tm);
    foreach (var t in new[] { "TextGen", "TextGen/Calendar" })
        foreach (var m in mod.GetType(t).Methods.Where(m => m.HasBody && m.IsPublic && m.ReturnType.FullName == "System.String"))
            WrapRet(m, tm);
    var icon = mod.GetType("GameViews.Cloud.Icon");
    {   // subtitle 赋值前过 UI（(Opens 7am) -> 上午7点 等）
        var m = icon.Methods.First(x => x.Name == "set_subtitle");
        m.Body.SimplifyMacros();
        var p = m.Body.GetILProcessor(); var first = m.Body.Instructions[0];
        p.InsertBefore(first, p.Create(OpCodes.Ldarg, m.Parameters[0]));
        p.InsertBefore(first, p.Create(OpCodes.Call, ui));
        p.InsertBefore(first, p.Create(OpCodes.Starg, m.Parameters[0]));
        m.Body.OptimizeMacros(); n12++;
    }
    foreach (var m in icon.Methods.Where(m => m.HasBody))
    {   // 按钮名 MARKET / BANK / HOTEL / PLAN ...
        m.Body.SimplifyMacros();
        var p = m.Body.GetILProcessor();
        foreach (var c in m.Body.Instructions.Where(i => i.OpCode == OpCodes.Ldfld && ((FieldReference)i.Operand).Name == "iconDisplayName").ToList())
        { p.InsertAfter(c, p.Create(OpCodes.Call, ui)); n12++; }
        m.Body.OptimizeMacros();
    }
    Console.WriteLine($"界面/时间包装 {n12} 处");
}

asm.Write(outPath);
File.Copy(outPath, Path.Combine(managed, "Assembly-CSharp.dll"), true);
Console.WriteLine("installed " + new FileInfo(Path.Combine(managed, "Assembly-CSharp.dll")).Length);
return 0;
