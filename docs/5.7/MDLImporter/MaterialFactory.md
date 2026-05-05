# 材质工厂

> 将蒸馏后的 MDL 材质参数映射为 UE5 UMaterial 资产。

## 概述

材质工厂系统负责将 `Mdl::FMaterial` 中间表示转换为 UE5 的 `UMaterial` 资产。核心决策点是**材质类型选择**：根据 MDL 材质的属性特征，自动选择最合适的 UE5 Shading Model 和 Blend Mode。

**类层次：**

```
IMaterialFactory (接口, material/MaterialFactory.h)
  ├── FOpaqueMaterialFactory        → BlendMode=Opaque
  ├── FMaskedMaterialFactory        → BlendMode=Masked
  ├── FTranslucentMaterialFactory   → BlendMode=Translucent
  ├── FClearcoatMaterialFactory     → ShadingModel=ClearCoat
  ├── FEmissiveMaterialFactory      → BlendMode=Opaque (自发光)
  ├── FCarpaintMaterialFactory      → ShadingModel=ClearCoat (车漆)
  └── FBakedMaterialFactory         → 通用烘焙材质

FMDLMaterialSelector        ← 材质类型选择器
FMDLMaterialFactory         ← 顶层材质创建协调器
FMDLMaterialPropertyFactory ← 材质属性/参数创建
```

## 材质类型枚举

**文件:** `MDLMaterialSelector.h`

```cpp
enum class EMaterialType
{
    Opaque = 0,     // 不透明 PBR
    Masked,         // Alpha Test（双面）
    Translucent,    // 半透明（双面 + Surface 照明）
    Clearcoat,      // 清漆（ClearCoat Shading Model）
    Emissive,       // 自发光
    Carpaint,       // 汽车漆面（ClearCoat + Flake 纹理）
    Subsurface,     // 次表面散射
    Count
};
```

### 材质类型 → UE5 设置映射

| MDL 材质类型 | Blend Mode | Shading Model | Two Sided | 特殊设置 |
|---|---|---|---|---|
| Opaque | Opaque | Default Lit | ✗ | — |
| Masked | Masked | Default Lit | ✓ | OpacityMask 连接 |
| Translucent | Translucent | Default Lit | ✓ | TLM_Surface 照明模式 |
| Clearcoat | Opaque | ClearCoat | ✗ | ClearCoat Normal 节点 |
| Emissive | Opaque | Default Lit | ✗ | Emissive Color 连接 |
| Carpaint | Opaque | ClearCoat | ✗ | Flakes 纹理数组 + LUT |
| Subsurface | Opaque | Subsurface | ✗ | Subsurface Color 连接 |

### 类型选择逻辑

`FMDLMaterialSelector::GetMaterialType()` 根据 `Mdl::FMaterial` 的属性判断材质类型：

- 有 Scattering/Absorption → **Subsurface**
- 有 Carpaint 且 bEnabled → **Carpaint**
- 有 Clearcoat 且 Weight 被处理 → **Clearcoat**
- Opacity 被处理且 < 1 → **Translucent**
- Opacity 被处理 → **Masked**
- Emission 被处理且无 BaseColor → **Emissive**
- 其他 → **Opaque**

## FMDLMaterialFactory — 材质创建协调器

**文件:** `MDLMaterialFactory.h`, `MDLMaterialFactory.cpp`

```cpp
class FMDLMaterialFactory
{
    // 创建材质骨架（UMaterial 对象），建立 NameMaterialMap
    bool CreateMaterials(const FString& Filename, UObject* ParentPackage,
                         EObjectFlags Flags, Mdl::FMaterialCollection& Materials);

    // 蒸馏后填充材质属性（设置 ShadingModel、连接表达式节点）
    void PostImport(Mdl::FMaterialCollection& Materials);

    // 重新导入单个材质
    void Reimport(const Mdl::FMaterial& MdlMaterial, UMaterial& Material);
};
```

### PostImport 流程

```
For each MdlMaterial in Materials:
  1. 材质类型选择: MaterialSelector.GetMaterialType(MdlMaterial)
  2. 设置材质属性: BlendMode, ShadingModel, TwoSided
  3. 创建材质参数: MaterialPropertyFactory.CreateProperties()
  4. 创建材质节点: MaterialFactory.Create(MdlMaterial, ParameterMap, Material)
  5. 连接表达式到材质输出节点:
     - BaseColor → MaterialEditorOnly.BaseColor
     - EmissiveColor → MaterialEditorOnly.EmissiveColor
     - Roughness → MaterialEditorOnly.Roughness
     - Metallic → MaterialEditorOnly.Metallic
     - Specular → MaterialEditorOnly.Specular
     - Normal → MaterialEditorOnly.Normal (或 UnderClearcoatNormal)
     - Opacity/OpacityMask → MaterialEditorOnly.Opacity/OpacityMask
     - ClearCoat → MaterialEditorOnly.ClearCoat
     - ClearCoatRoughness → MaterialEditorOnly.ClearCoatRoughness
  6. 布局材质表达式: UMaterialEditingLibrary::LayoutMaterialExpressions()
  7. 标记包为脏: Material.MarkPackageDirty()
```

## IMaterialFactory — 材质工厂接口

**文件:** `material/MaterialFactory.h`

```cpp
namespace Mat
{
    enum class EMaterialParameter
    {
        BaseColor, BaseColorMap,
        SubSurfaceColor, SubSurfaceColorMap,
        EmissionColor, EmissionColorMap, EmissionStrength,
        Roughness, RoughnessMap,
        Metallic, MetallicMap,
        Specular, SpecularMap,
        IOR, AbsorptionColor,
        Opacity, OpacityMap,
        NormalMap, NormalStrength,
        DisplacementMap, DisplacementStrength,
        ClearCoatWeight, ClearCoatWeightMap,
        ClearCoatRoughness, ClearCoatRoughnessMap,
        ClearCoatNormalMap, ClearCoatNormalStrength,
        CarFlakesMap, CarFlakesLut,
        Tiling, TilingU, TilingV
    };

    using FParameterMap = TMap<EMaterialParameter, UMaterialExpression*>;

    class IMaterialFactory
    {
        virtual void Create(const Mdl::FMaterial& MdlMaterial,
                           const FParameterMap& Parameters,
                           UMaterial& Material) const = 0;
    };
}
```

## 具体工厂实现

### TranslucentMaterialFactory

**文件:** `material/TranslucentMaterialFactory.h`, `material/TranslucentMaterialFactory.cpp`

处理半透明材质。MDL 的半透明材质使用 IOR（折射率）+ Opacity + BaseColor 的组合来描述，需要特殊的参数映射：

- IOR → Refraction 输入
- Opacity → Opacity 输入
- BaseColor → 透射颜色

### CarpaintMaterialFactory

**文件:** `material/CarpaintMaterialFactory.h`, `material/CarpaintMaterialFactory.cpp`

处理汽车漆面材质。车漆是 MDL 中的高级材质类型，包含：
- **Flakes 纹理数组**：金属闪光片的 LUT（Look-Up Table）
- **ThetaFi LUT**：角度相关的反射查找表
- **ClearCoat 层**：上层清漆

### BakedMaterialFactory

**文件:** `material/BakedMaterialFactory.h`, `material/BakedMaterialFactory.cpp`

通用烘焙材质工厂。当材质属性无法直接映射为 UE5 材质节点时，将整个属性烘焙为纹理。

### MapConnecter

**文件:** `material/MapConnecter.h`

处理材质贴图的连接逻辑（将烘焙后的纹理连接到材质属性）。
