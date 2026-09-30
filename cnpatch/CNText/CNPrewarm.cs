// 80 Days 汉化：中文字形预热 + 防卸载   (v3)
//
// 问题：TMP 的中文动态后备字体在运行期才把字形烤进图集。一旦 Unity 在场景切换时
//       通过 Resources.UnloadUnusedAssets() 回收了「源字体 Font / 图集贴图 / 字体资源」
//       之一，之后每个第一次遇到的新字都会加载失败，并被 TMP 的
//       m_MissingUnicodesFromFontFile 永久拉黑 —— 本局剩下的时间里该字恒为空格。
//
// 对策：1) Pin()  给字体资源 / 源 TTF / 图集贴图 / 材质打 DontUnloadUnusedAsset，掐断回收路径
//       2) Warm() 启动后分帧把 cn_charset.txt 里全部汉字预先烤进图集，运行期不再新增字形
//
// ── 版本history ────────────────────────────────────────────────────────────
// v1  在 GameController.Awake 直接调 TMP_FontAsset.TryAddCharacters → NullReferenceException，
//     requested=0。原因：此时字体资源的内部查找表还没建。
// v2  加了 ReadFontAssetDefinition() + 失败重试。结果每轮只能推进一个 chunk，之后照样 NRE。
//     用 Mono.Cecil 反 Unity.TextMeshPro.dll 的 IL 定位到确切崩溃点：
//
//        IL_01d0  call FontEngine::TryAddGlyphsToTexture(..., out Glyph[] glyphs)
//        IL_01db  ldloc.2        // glyphs
//        IL_01de  ldelem.ref     // glyphs[i]
//        IL_01e1  ldloc.s V_9    // <<< NullReferenceException
//        IL_01e3  callvirt Glyph::get_index()
//
//     即 glyphs[i] 为 null：TryAddGlyphsToTexture 返回的数组带空洞，而 TMP 遍历时
//     不做 null 检查。这是 TMP 1.4 批量 API 自身的缺陷，跟我们的字体资源无关。
// v3  彻底不用批量 API。改走 TMP_FontAssetUtilities.GetCharacterFromFontAsset()
//     —— 这正是 TMP_Text.SetArraySizes 渲染每个字符时调用的同一个函数，
//     逐字、带后备链、TMP 自己天天在跑的路径。能在这里烤进去的字，游戏里必然也能显示。
//     附带好处：逐字粒度，一个字失败不会带走整批。
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
    const int PerFrame = 256;       // 每帧处理多少字，避免启动卡顿
    const int MaxPasses = 10;       // 单个字体资源的重试上限
    const string Probe = "摞珍咧遵扯祥盒的一是我你他中国人";

    static string charset = "";
    static readonly HashSet<int> done = new HashSet<int>();
    static readonly Dictionary<int, int> tries = new Dictionary<int, int>();

    void Start()
    {
        try
        {
            string p = Path.Combine(Application.dataPath, ".." + Path.DirectorySeparatorChar + "cn_charset.txt");
            if (File.Exists(p)) charset = File.ReadAllText(p, Encoding.UTF8).Trim();
            Debug.Log("[CN] charset chars = " + charset.Length);
        }
        catch (System.Exception e) { Debug.LogWarning("[CN] charset read failed: " + e.Message); }
        StartCoroutine(Loop());
    }

    IEnumerator Loop()
    {
        yield return new WaitForSeconds(1f);        // 让首个场景先把字体资源初始化好
        while (true)
        {
            Pin();                                   // 场景切换后新载入的字体资源也要钉住
            if (charset.Length > 0) yield return Warm();
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
        for (int i = 0; i < all.Length; i++)
        {
            var fa = all[i];
            if (fa == null) continue;
            int id = fa.GetInstanceID();
            if (done.Contains(id)) continue;
            int n; tries.TryGetValue(id, out n);
            if (n >= MaxPasses) continue;
            tries[id] = n + 1;

            var missed = new StringBuilder();
            int added = 0, hit = 0, budget = 0;
            bool crashed = false;
            float t0 = Time.realtimeSinceStartup;
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
                if (++budget >= PerFrame) { budget = 0; yield return null; }
            }

            int tableAfter = fa.characterTable == null ? -1 : fa.characterTable.Count;
            added = tableAfter - tableBefore;
            int ok = 0;
            for (int k = 0; k < Probe.Length; k++) { try { if (fa.HasCharacter(Probe[k], true)) ok++; } catch { } }

            Debug.Log("[CN] prewarm " + fa.name
                      + "  mode=" + fa.atlasPopulationMode
                      + "  atlas=" + fa.atlasWidth + "x" + fa.atlasHeight
                      + "  resolved=" + hit + "/" + charset.Length
                      + "  missing=" + missed.Length
                      + "  charTable " + tableBefore + "->" + tableAfter
                      + "  probe=" + ok + "/" + Probe.Length
                      + "  " + (Time.realtimeSinceStartup - t0).ToString("0.00") + "s"
                      + (crashed ? "  [CRASHED]" : ""));

            string f = "cn_prewarm_missing_" + fa.name.Replace(' ', '_') + ".txt";
            try
            {
                if (missed.Length > 0) File.WriteAllText(f, missed.ToString(), Encoding.UTF8);
                else if (File.Exists(f)) File.Delete(f);
            }
            catch { }

            if (!crashed && missed.Length == 0) done.Add(id);   // 全中才收工，否则下一轮重来
        }
    }
}
