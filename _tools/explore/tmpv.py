b=open(r'F:\Games\80 Days\80 Days_Data\Managed\Unity.TextMeshPro.dll','rb').read()
for w in ['m_AtlasPopulationMode','m_IsMultiAtlasTexturesEnabled','m_AtlasTextures','m_FallbackFontAssetTable','m_SourceFontFile','fallbackFontAssets','TryAddCharacters','m_ClearDynamicDataOnBuild','m_AtlasWidth','m_AtlasPadding','m_FaceInfo','m_GlyphTable','m_CharacterTable','m_Version','TMP_Settings','m_warningsDisabled','missingGlyphCharacter','m_missingGlyphCharacter']:
    print(w, b.count(w.encode()), b.count(w.encode('utf-16-le')))
