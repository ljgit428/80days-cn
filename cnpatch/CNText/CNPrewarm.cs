// 80 Days 汉化：中文字形预热 + 防卸载   (v4)
//
// 问题：TMP 的中文动态后备字体在运行期才把字形烤进图集。一旦 Unity 在场景切换时
//       通过 Resources.UnloadUnusedAssets() 回收了「源字体 Font / 图集贴图 / 字体资源」
//       之一，之后每个第一次遇到的新字都会加载失败，并被 TMP 的
//       m_MissingUnicodesFromFontFile 永久拉黑 —— 本局剩下的时间里该字恒为空格。
//
// 对策：1) Pin()  给字体资源 / 源 TTF / 图集贴图 / 材质打 DontUnloadUnusedAsset，掐断回收路径
//       2) Warm() 分帧把 cn_charset.txt 里全部汉字预先烤进图集，运行期不再新增字形
//
// ── 版本history ────────────────────────────────────────────────────────────
// v1  在 GameController.Awake 直接调 TMP_FontAsset.TryAddCharacters → NullReferenceException。
// v2  加 ReadFontAssetDefinition() + 重试，仍每轮只推进一个 chunk。用 Mono.Cecil 反
//     Unity.TextMeshPro.dll 的 IL 定位到崩溃点：
//        IL_01d0  call FontEngine::TryAddGlyphsToTexture(..., out Glyph[] glyphs)
//        IL_01de  ldelem.ref    // glyphs[i]
//        IL_01e1  ldloc.s V_9   // <<< NullReferenceException
//        IL_01e3  callvirt Glyph::get_index()
//     TryAddGlyphsToTexture 返回的数组带 null 空洞，TMP 遍历时不做 null 检查。
//     这是 TMP 1.4 批量 API 自身的缺陷，与字体资源无关。
// v3  改走 TMP_FontAssetUtilities.GetCharacterFromFontAsset()，即 TMP_Text.SetArraySizes
//     渲染每个字符时调用的同一个函数。实测 resolved=3688/3688、missing=0、NRE=0，通过。
// v4  修卡顿。v3 每帧固定烤 256 字，而实测单字光栅化约 5.6ms，等于每帧硬卡 1.4 秒、
//     连续十几次，主菜单肉眼可见一顿一顿。改为按**时间预算**切分：每帧最多干
//     FrameBudgetMs 毫秒就让出去，总时长不变但摊平。另外先烤 Dynamic 字体
//     （真正产生光栅化开销的是它们），之后各 Static 字体只是字典命中，几乎免费。
//     安全阀：游戏根目录放一个 cn_no_prewarm.txt 即可整体关掉预热（Pin 仍然生效）。
//
// 由 Patcher 在 Game.GameController::Awake 开头注入 CNPrewarm.Install();
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Text;
using UnityEngine;
using TMPro;

public static class CNPrewarm
{
    static bool installed;
    public static void Install()
    {
        if (installed) return;
        installed = true;
        try
        {
            var go = new GameObject("CNPrewarm");
            UnityEngine.Object.DontDestroyOnLoad(go);
            go.AddComponent<CNPrewarmRunner>();
        }
        catch (System.Exception e) { Debug.LogWarning("[CN] prewarm install failed: " + e); }
    }
}

public class CNPrewarmRunner : MonoBehaviour
{
    const float FrameBudgetMs = 6f;   // 每帧最多花这么多毫秒在预热上
    const int MaxPasses = 10;
    const string Probe = "摞珍咧遵扯祥盒的一是我你他中国人";

    static string charset = "";
    static bool disabled;
    static readonly HashSet<int> done = new HashSet<int>();
    static readonly Dictionary<int, int> tries = new Dictionary<int, int>();

    static string GameFile(string name)
    {
        return Path.Combine(Application.dataPath, ".." + Path.DirectorySeparatorChar + name);
    }

    void Start()
    {
        try
        {
            if (File.Exists(GameFile("cn_no_prewarm.txt")))
            {
                disabled = true;
                Debug.Log("[CN] prewarm disabled by cn_no_prewarm.txt (Pin 仍生效)");
            }
            string p = GameFile("cn_charset.txt");
            if (File.Exists(p)) charset = File.ReadAllText(p, Encoding.UTF8).Trim();
            Debug.Log("[CN] charset chars = " + charset.Length + "  frameBudget=" + FrameBudgetMs + "ms");
        }
        catch (System.Exception e) { Debug.LogWarning("[CN] charset read failed: " + e.Message); }
        StartCoroutine(Loop());
    }

    IEnumerator Loop()
    {
        yield return new WaitForSeconds(2f);        // 先让首个场景把字体资源初始化好、菜单可交互
        while (true)
        {
            Pin();                                   // 场景切换后新载入的字体资源也要钉住
            if (!disabled && charset.Length > 0) yield return Warm();
            yield return new WaitForSeconds(5f);
        }
    }

    static void Pin()
    {
        var all = Resources.FindObjectsOfTypeAll<TMP_FontAsset>();
        for (int i = 0; i < all.Length; i++)
        {
            var fa = all[i];
            if (fa == null) continue;
            fa.hideFlags |= HideFlags.DontUnloadUnusedAsset;
            if (fa.sourceFontFile != null) fa.sourceFontFile.hideFlags |= HideFlags.DontUnloadUnusedAsset;
            if (fa.atlasTexture != null) fa.atlasTexture.hideFlags |= HideFlags.DontUnloadUnusedAsset;
            var texs = fa.atlasTextures;
            if (texs != null)
                for (int k = 0; k < texs.Length; k++)
                    if (texs[k] != null) texs[k].hideFlags |= HideFlags.DontUnloadUnusedAsset;
            if (fa.material != null) fa.material.hideFlags |= HideFlags.DontUnloadUnusedAsset;
        }
    }

    IEnumerator Warm()
    {
        var all = Resources.FindObjectsOfTypeAll<TMP_FontAsset>();

        // 先 Dynamic 后 Static：真正的光栅化开销都在 Dynamic 上，
        // 烤完之后各 Static 走同一条后备链就只是字典命中了。
        var order = new List<TMP_FontAsset>();
        for (int i = 0; i < all.Length; i++)
            if (all[i] != null && all[i].atlasPopulationMode == AtlasPopulationMode.Dynamic) order.Add(all[i]);
        for (int i = 0; i < all.Length; i++)
            if (all[i] != null && all[i].atlasPopulationMode != AtlasPopulationMode.Dynamic) order.Add(all[i]);

        for (int i = 0; i < order.Count; i++)
        {
            var fa = order[i];
            int id = fa.GetInstanceID();
            if (done.Contains(id)) continue;
            int n; tries.TryGetValue(id, out n);
            if (n >= MaxPasses) continue;
            tries[id] = n + 1;

            var missed = new StringBuilder();
            int hit = 0, frames = 0;
            bool crashed = false;
            float t0 = Time.realtimeSinceStartup;
            float slice = Time.realtimeSinceStartup;
            int tableBefore = fa.characterTable == null ? -1 : fa.characterTable.Count;

            for (int c = 0; c < charset.Length; c++)
            {
                char ch = charset[c];
                try
                {
                    bool alt; TMP_FontAsset src;
                    // 与 TMP_Text.SetArraySizes 渲染每个字符时完全相同的调用
                    var got = TMP_FontAssetUtilities.GetCharacterFromFontAsset(
                        ch, fa, true, FontStyles.Normal, FontWeight.Regular, out alt, out src);
                    if (got == null) missed.Append(ch); else hit++;
                }
                catch (System.Exception e)
                {
                    Debug.LogWarning("[CN] " + fa.name + " char U+" + ((int)ch).ToString("X4") + " failed: " + e.Message);
                    crashed = true;
                    break;
                }
                // 按时间预算让出，避免整帧被光栅化吃掉
                if ((Time.realtimeSinceStartup - slice) * 1000f >= FrameBudgetMs)
                {
                    yield return null;
                    frames++;
                    slice = Time.realtimeSinceStartup;
                }
            }

            int tableAfter = fa.characterTable == null ? -1 : fa.characterTable.Count;
            int ok = 0;
            for (int k = 0; k < Probe.Length; k++) { try { if (fa.HasCharacter(Probe[k], true)) ok++; } catch { } }

            Debug.Log("[CN] prewarm " + fa.name
                      + "  mode=" + fa.atlasPopulationMode
                      + "  atlas=" + fa.atlasWidth + "x" + fa.atlasHeight
                      + "  resolved=" + hit + "/" + charset.Length
                      + "  missing=" + missed.Length
                      + "  charTable " + tableBefore + "->" + tableAfter
                      + "  probe=" + ok + "/" + Probe.Length
                      + "  " + (Time.realtimeSinceStartup - t0).ToString("0.00") + "s/" + frames + "帧"
                      + (crashed ? "  [CRASHED]" : ""));

            string f = "cn_prewarm_missing_" + fa.name.Replace(' ', '_') + ".txt";
            try
            {
                if (missed.Length > 0) File.WriteAllText(f, missed.ToString(), Encoding.UTF8);
                else if (File.Exists(f)) File.Delete(f);
            }
            catch { }

            if (!crashed && missed.Length == 0) done.Add(id);
        }
    }
}
