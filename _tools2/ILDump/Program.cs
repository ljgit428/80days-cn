
using System; using System.IO; using System.Linq; using System.Text;
using Mono.Cecil;
class P {
  static void Main() {
    var asm = AssemblyDefinition.ReadAssembly(@"F:\Games\80 Days\80 Days_Data\Managed\Unity.TextMeshPro.dll");
    var sb = new StringBuilder();
    foreach (var tn in new[]{"TMPro.TMP_FontAssetUtilities","TMPro.TMP_Character","TMPro.TMP_FontAsset","TMPro.TMP_Settings"}) {
      var t = asm.MainModule.GetType(tn);
      if (t == null) { sb.AppendLine(tn + " : NOT FOUND"); continue; }
      sb.AppendLine("=== " + tn + "  public=" + t.IsPublic + " ===");
      foreach (var m in t.Methods.Where(x => x.IsPublic && (
            x.Name.Contains("GetCharacterFromFontAsset") || x.Name=="HasCharacter" || x.Name=="ReadFontAssetDefinition"
         || x.Name=="TryAddCharacter" || x.Name=="ClearFontAssetData" || x.Name=="get_atlasTextures"
         || x.Name=="get_characterTable" || x.Name=="get_fallbackFontAssetTable" || x.Name=="get_defaultFontAsset"
         || x.Name=="get_fallbackFontAssets" || x.Name=="get_missingGlyphCharacter")))
        sb.AppendLine("   " + (m.IsStatic ? "static " : "") + m.ReturnType.Name + " " + m.Name + "("
           + string.Join(", ", m.Parameters.Select(p => (p.IsOut?"out ":"") + p.ParameterType.Name + " " + p.Name)) + ")");
      foreach (var p in t.Properties.Where(x => x.GetMethod != null && x.GetMethod.IsPublic
            && (x.Name=="glyph" || x.Name=="unicode" || x.Name=="textAsset")))
        sb.AppendLine("   prop " + p.PropertyType.Name + " " + p.Name);
      sb.AppendLine();
    }
    File.WriteAllText(@"D:\git\project\80 days CN\_tools2\api.txt", sb.ToString(), new UTF8Encoding(false));
    Console.WriteLine("ok");
  }
}
