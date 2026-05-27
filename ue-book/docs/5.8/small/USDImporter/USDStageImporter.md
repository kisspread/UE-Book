# USD Importer

> Adds support for importing the USD file format into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | USD 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（USD 相关资产、配置） |
| 模块 | `USDSchemas` (Runtime), `USDClassesEditor` (Runtime), `USDExporter` (Runtime), `USDStage` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDStageImporter` (Runtime), `USDTests` (Runtime), `GeometryCacheUSD` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter) | |

---

## 用途

USDImporter 是 Unreal Engine 的 **Universal Scene Description (USD)** 文件格式导入/导出解决方案。该插件不仅实现了基础的 USD 文件读取，还提供了完整的 USD 场景管线，包括：

- **场景结构保持**：将 USD 的 Prim 层次结构映射为 UE 的 Actor/Component 层次结构
- **资产生成**：从 USD 数据自动生成 StaticMesh、SkeletalMesh、材质、纹理、动画序列、LevelSequence、Groom 资产、Sparse Volume Texture、音频等
- **LOD 支持**：自动识别 USD 中的 LOD Variant Set 并合并为单个 StaticMesh 的多个 LOD 层级
- **网格合并/折叠**：基于 Prim Kind 智能合并同类型的子资产，减少场景冗余
- **双向同步**：通过 USDStage 系统实现实时双向编辑（编辑器中修改回写 USD）
- **材质映射**：支持自定义 Render Context 和 Material Purpose，兼容不同渲染管线的材质方案
- **冲突处理**：提供精细的 Actor 和资产冲突策略（追加/替换/更新变换/忽略）

**为什么存在**：USD 是 Pixar 开发的开放场景描述格式，在电影和动画行业广泛使用。随着 USD 在游戏行业的普及，UE 需要原生支持 USD 文件的导入，以便开发者可以无缝地将影视资产管线中的资产引入游戏项目。

---

## 使用场景

- 你从 **影视/动画制作管线** 中获得了 USD 格式的场景资产（角色、环境、灯光）→ 用 USDImporter 直接导入到 UE 关卡
- 你需要将 **Maya/Houdini/Blender 导出的 USD 文件** 导入 UE 作为静态网格或骨架资产 → 使用 Content Browser 的导入功能或 File → Import Into Level
- 你正在做一个需要 **实时 USD 双向同步** 的虚拟制片项目 → 用 USDStage 系统实现 UE 编辑器与 USD 数据的双向更新
- 你需要导入包含 **多 LOD 变体** 的 USD 场景 → 开启 `Interpret LOD Variant Sets` 自动解析
- 你需要将 USD 中的 **骨骼动画** 转换为 UE 的 UAnimSequence → 开启 `Skeletal Animations` 导入选项
- 你正在使用 **Nanite** 优化大型网格 → 设置 `NaniteTriangleThreshold` 自动为高面数网格启用 Nanite
- 你从 USD 工作流获取 **Groom（毛发）** 资产 → 开启 `Groom Assets` 导入选项
- 你需要导入 **OpenVDB 体积数据** → 开启 `Sparse Volume Textures` 导入选项

---

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `bImportActors` | 是否导入 Actor | `UUsdStageImportOptions` |
| `bImportGeometry` | 是否导入几何体 | `UUsdStageImportOptions` |
| `bImportSkeletalAnimations` | 是否导入骨骼动画（AnimSequence） | `UUsdStageImportOptions` |
| `bImportLevelSequences` | 是否导入 LevelSequence 动画 | `UUsdStageImportOptions` |
| `bImportMaterials` | 是否导入材质和纹理 | `UUsdStageImportOptions` |
| `bImportGroomAssets` | 是否导入 Groom 资产（毛发） | `UUsdStageImportOptions` |
| `bImportSparseVolumeTextures` | 是否导入 OpenVDB 稀疏体积纹理 | `UUsdStageImportOptions` |
| `bImportSounds` | 是否导入音频资产 | `UUsdStageImportOptions` |
| `PrimsToImport` | 指定要导入的 Prim 路径列表（默认导入整个 Stage） | `UUsdStageImportOptions` |
| `bShareAssetsForIdenticalPrims` | 相同 Prim 之间共享生成的资产 | `UUsdStageImportOptions` |
| `bInterpretLODs` | 是否将 LOD Variant Set 解析为 StaticMesh 的多个 LOD | `UUsdStageImportOptions` |
| `NaniteTriangleThreshold` | 超过此三角面数的网格自动启用 Nanite | `UUsdStageImportOptions` |
| `RenderContextToImport` | 指定解析 USD 材质时使用的着色器上下文 | `UUsdStageImportOptions` |
| `MaterialPurpose` | 指定解析材质绑定时使用的材质用途 | `UUsdStageImportOptions` |
| `ExistingActorPolicy` | 已有 Actor 冲突处理策略 | `UUsdStageImportOptions` |
| `ExistingAssetPolicy` | 已有资产冲突处理策略 | `UUsdStageImportOptions` |
| `SubdivisionLevel` | USD 细分网格的细分等级（0=不细分，最大 6） | `UUsdStageImportOptions` |

### 导入选项枚举

| 枚举 | 值 | 说明 |
|---|---|---|
| `EReplaceActorPolicy` | `Append` | 在已有 Actor 旁边生成新的 |
| | `Replace` | 替换已有的 Actor 和组件 |
| | `UpdateTransform` | 仅更新已有 Actor 的变换 |
| | `Ignore` | 忽略新资产，保留旧的 |
| `EReplaceAssetPolicy` | `Append` | 创建带数字后缀的新资产 |
| | `Replace` | 用新资产替换旧资产 |
| | `Ignore` | 忽略新资产，保留旧的 |

### 使用示例（蓝图描述）

**程序化导入 USD 文件：**
1. 创建 `UUsdStageImportOptions` 对象实例
2. 设置各 `bImport*` 开关控制要导入的数据类型
3. 设置 `PrimsToImport` 数组选择要导入的 Prim 子集
4. 调用 `UUsdStageImporter::ImportFromFile` 或通过 `UUsdStageAssetImportFactory` 触发导入

**自定义冲突策略：**
1. 设置 `ExistingActorPolicy` 为 `EReplaceActorPolicy::Replace` 以在重新导入时覆盖旧 Actor
2. 设置 `ExistingAssetPolicy` 为 `EReplaceAssetPolicy::Append` 以保留旧资产并创建新版本

**LOD 自动解析：**
1. 设置 `bImportGeometry = true`
2. 设置 `bInterpretLODs = true`
3. USD 文件中的 "LOD" variant set（含 LOD0、LOD1 等变体）将自动合并为单个 StaticMesh 的多个 LOD

---

## C++ 用法

### 头文件引入

```cpp
#include "USDStageImportOptions.h"
#include "USDStageImportContext.h"
#include "USDStageImporter.h"
#include "USDStageImporterModule.h"
```

### 基本用法

**通过模块接口获取 Importer 实例并导入 USD 文件：**

```cpp
// 来源: Public/USDStageImporterModule.h
if (IUsdStageImporterModule::IsAvailable())
{
    IUsdStageImporterModule& ImporterModule = IUsdStageImporterModule::Get();
    UUsdStageImporter* Importer = ImporterModule.GetImporter();
    
    // 配置导入上下文
    FUsdStageImportContext ImportContext;
    ImportContext.FilePath = TEXT("/path/to/scene.usd");
    ImportContext.bIsAutomated = false;
    ImportContext.bReadFromStageCache = true;
    
    // 执行导入
    Importer->ImportFromFile(ImportContext);
    
    // 导入完成后，可从上下文获取结果
    UObject* ImportedAsset = ImportContext.ImportedAsset;
    TArray<TObjectPtr<UObject>>& AllImported = ImportContext.ImportedAssets;
}
```

### 进阶用法

**自定义导入选项并程序化导入：**

```cpp
#include "USDStageImportOptions.h"
#include "USDStageImportContext.h"
#include "USDStageImporter.h"

// 创建并配置导入选项
UUsdStageImportOptions* Options = NewObject<UUsdStageImportOptions>();

// 控制要导入的数据类型
Options->bImportActors = true;
Options->bImportGeometry = true;
Options->bImportMaterials = true;
Options->bImportSkeletalAnimations = true;
Options->bImportLevelSequences = false;
Options->bImportGroomAssets = false;
Options->bImportSounds = false;

// 仅导入使用的材质以加速导入
Options->bImportOnlyUsedMaterials = true;

// 设置 Nanite 阈值：超过 10000 面的网格启用 Nanite
Options->NaniteTriangleThreshold = 10000;

// 启用 LOD 自动解析
Options->bInterpretLODs = true;

// 设置冲突策略
Options->ExistingActorPolicy = EReplaceActorPolicy::Replace;
Options->ExistingAssetPolicy = EReplaceAssetPolicy::Append;

// 共享相同 Prim 生成的资产
Options->bShareAssetsForIdenticalPrims = true;

// 指定要导入的 Prim 子集
Options->PrimsToImport = { TEXT("/Root/Character"), TEXT("/Root/Environment") };

// 设置渲染上下文（如 UnrealPBR 或自定义）
Options->RenderContextToImport = FName("UnrealPBR");

// 配置导入上下文
FUsdStageImportContext ImportContext;
ImportContext.ImportOptions = Options;
ImportContext.FilePath = TEXT("/content/assets/scene.usd");
ImportContext.bIsAutomated = true;  // 不弹出选项对话框

// 初始化上下文
ImportContext.Init(
    TEXT("MyImportedScene"),
    ImportContext.FilePath,
    TEXT("/Game/ImportedAssets"),
    RF_Public | RF_Standalone,
    /* bInIsAutomated */ true
);

// 执行导入
IUsdStageImporterModule& Module = IUsdStageImporterModule::Get();
UUsdStageImporter* Importer = Module.GetImporter();
Importer->ImportFromFile(ImportContext);

// 获取所有导入的资产
for (TObjectPtr<UObject>& Asset : ImportContext.ImportedAssets)
{
    UE_LOG(LogTemp, Log, TEXT("Imported asset: %s"), *Asset->GetName());
}
```

**仅抑制 Actor 导入（用于仅生成资产的场景）：**

```cpp
// 来源: Public/USDStageImportOptions.h 中的 FScopedSuppressActorImport
{
    UsdUtils::FScopedSuppressActorImport ScopedSuppress(ImportOptions);
    // 在此作用域内，ImportOptions->bImportActors 被临时设为 false
    // 离开作用域后自动恢复原值
    Importer->ImportFromFile(ImportContext);
}
```

**重新导入单个资产：**

```cpp
// 来源: Public/USDStageImporter.h
FUsdStageImportContext ImportContext;
// ... 初始化 ImportContext ...

UObject* OriginalAsset = /* 之前导入的资产 */;
FString OriginalPrimPath = TEXT("/Root/MyMesh");
UObject* OutReimportedAsset = nullptr;

bool bSuccess = Importer->ReimportSingleAsset(
    ImportContext,
    OriginalAsset,
    OriginalPrimPath,
    OutReimportedAsset
);
```

---

## Demo 示例

以下示例展示如何通过 C++ 程序化导入 USD 文件并配置所有关键选项：

**USDImporterDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class FUSDImporterDemo
{
public:
    /** 程序化导入 USD 文件 */
    static bool ImportUSDFile(
        const FString& InUSDFilePath,
        const FString& InOutputPackagePath,
        bool bAutomated = true
    );
    
    /** 仅重新导入指定的资产 */
    static bool ReimportAsset(
        const FString& InUSDFilePath,
        UObject* InOriginalAsset,
        const FString& InPrimPath
    );
};
```

**USDImporterDemo.cpp**
```cpp
#include "USDImporterDemo.h"
#include "USDStageImporterModule.h"
#include "USDStageImporter.h"
#include "USDStageImportContext.h"
#include "USDStageImportOptions.h"

bool FUSDImporterDemo::ImportUSDFile(
    const FString& InUSDFilePath,
    const FString& InOutputPackagePath,
    bool bAutomated)
{
    if (!IUsdStageImporterModule::IsAvailable())
    {
        UE_LOG(LogTemp, Error, TEXT("USDStageImporter module is not available"));
        return false;
    }

    IUsdStageImporterModule& ImporterModule = IUsdStageImporterModule::Get();
    UUsdStageImporter* Importer = ImporterModule.GetImporter();
    if (!Importer)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to get USD Importer instance"));
        return false;
    }

    // 配置导入选项
    UUsdStageImportOptions* Options = NewObject<UUsdStageImportOptions>();
    Options->bImportActors = true;
    Options->bImportGeometry = true;
    Options->bImportMaterials = true;
    Options->bImportSkeletalAnimations = true;
    Options->bImportLevelSequences = true;
    Options->bImportOnlyUsedMaterials = true;
    Options->NaniteTriangleThreshold = 5000;
    Options->bInterpretLODs = true;
    Options->bShareAssetsForIdenticalPrims = true;
    Options->bUsePrimKindsForCollapsing = true;
    Options->bPrimPathFolderStructure = true;
    Options->ExistingActorPolicy = EReplaceActorPolicy::Replace;
    Options->ExistingAssetPolicy = EReplaceAssetPolicy::Append;
    Options->SubdivisionLevel = 0;

    // 初始化导入上下文
    FUsdStageImportContext ImportContext;
    ImportContext.ImportOptions = Options;
    ImportContext.bIsAutomated = bAutomated;
    ImportContext.bReadFromStageCache = true;

    if (!ImportContext.Init(
        FPaths::GetBaseFilename(InUSDFilePath),
        InUSDFilePath,
        InOutputPackagePath,
        RF_Public | RF_Standalone,
        bAutomated))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to initialize import context for: %s"), *InUSDFilePath);
        return false;
    }

    // 执行导入
    Importer->ImportFromFile(ImportContext);

    UE_LOG(LogTemp, Log, TEXT("Successfully imported %d assets from USD"),
        ImportContext.ImportedAssets.Num());

    return ImportContext.ImportedAssets.Num() > 0;
}

bool FUSDImporterDemo::ReimportAsset(
    const FString& InUSDFilePath,
    UObject* InOriginalAsset,
    const FString& InPrimPath)
{
    if (!IUsdStageImporterModule::IsAvailable())
    {
        return false;
    }

    IUsdStageImporterModule& ImporterModule = IUsdStageImporterModule::Get();
    UUsdStageImporter* Importer = ImporterModule.GetImporter();
    if (!Importer)
    {
        return false;
    }

    FUsdStageImportContext ImportContext;
    ImportContext.bIsAutomated = true;
    ImportContext.bReadFromStageCache = true;

    if (!ImportContext.Init(
        FPaths::GetBaseFilename(InUSDFilePath),
        InUSDFilePath,
        InOriginalAsset->GetPackage()->GetPath(),
        RF_Public | RF_Standalone,
        /* bInIsAutomated */ true,
        /* bIsReimport */ true))
    {
        return false;
    }

    UObject* ReimportedAsset = nullptr;
    return Importer->ReimportSingleAsset(
        ImportContext,
        InOriginalAsset,
        InPrimPath,
        ReimportedAsset
    );
}
```

---

## 模块依赖

该插件包含 9 个模块，以下是各模块的主要用途及关键依赖关系：

| 模块 | 用途 |
|---|---|
| `UnrealUSDWrapper` | UE 对 USD 库（OpenUSD）的 C++ 封装层 |
| `USDClasses` | USD 相关的共享类定义（资产缓存、配置等） |
| `USDConverter` | USD 数据类型与 UE 数据类型之间的转换器 |

> **注意**：所有标准 UE 模块（Core, CoreUObject, Engine, Slate, UMG 等）均已省略。该插件还深度依赖 `GeometryCache`、`HairStrandsCore`（Groom 支持）、`MeshConversion`、`StaticMeshDescription`、`LevelSequence` 等模块用于各类型资产的生成。具体依赖请查看各子模块的 Build.cs 文件。

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为 float 的编译警告 |
| 2026-04-29 | `bc4a1bd2` | USD: Add support for assigning BP-independent control rigs. | 新增支持分配独立于蓝图的 Control Rig |
| 2026-04-28 | `4fb59a1d` | USD: Work around update to 26.03 causing AnimQuery internal references to be invalidated when LOD va... | 修复 USD 26.03 更新导致 LOD 变体切换时 AnimQuery 内部引用失效的问题 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式化说明符与实际参数不匹配的问题 |
| 2026-04-09 | `fb7af182` | USD: Bake all frames of exposure animation tracks. | 支持烘焙曝光动画轨道的所有帧 |

### 维护评价

**活跃维护** ✅

- **创建时间**：2018 年 11 月，已运行约 7 年
- **更新频率**：近期（2026 年 4-5 月）有多次实质性更新，包括新功能（Control Rig 支持）、USD 版本兼容修复（26.03）、编译兼容性修复等
- **维护状态**：非常活跃，持续跟踪上游 USD 库更新并修复兼容性问题
- **已知限制**：标记为 Beta (`IsBetaVersion=true`) 且默认未启用 (`EnabledByDefault=false`)，需要在 Plugins 面板中手动启用
- **推荐度**：强烈推荐。作为 Epic 官方维护的 USD 导入管线，功能全面且持续更新。对于需要 USD 工作流的影视/虚拟制片项目是必备插件。尽管标记为 Beta，但已经历 7 年以上的迭代，成熟度很高。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter)
- [官方文档](https://docs.unrealengine.com/)（.uplugin 中未提供专用文档 URL，请参考 UE 官方文档中的 USD 章节）