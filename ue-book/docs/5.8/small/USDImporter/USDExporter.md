# USD Importer

> Adds support for importing the USD file format into Unreal Engine（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | USD 导入导出器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器自定义 UI） |
| 模块 | `GeometryCacheUSD` (Runtime), `USDClassesEditor` (Runtime), `USDExporter` (Runtime), `USDSchemas` (Runtime), `USDStage` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDStageImporter` (Runtime), `USDTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter) | |

---

# USD Exporter 模块文档

> **注意**：本文档聚焦于 `USDImporter` 插件中的 `USDExporter` 模块。该插件整体包含 9 个模块，187 个源文件，属于大型插件（large）。

## 用途

USDExporter 模块是 Unreal Engine 与 Pixar USD（Universal Scene Description）格式之间的**导出桥梁**。它解决了以下核心问题：

1. **资产导出为 USD**：将 UE 内的 StaticMesh、SkeletalMesh、GeometryCache、Material 等资产导出为 USD 格式文件
2. **关卡导出为 USD**：将整个 UE 关卡（含子关卡）导出为 USD Stage，支持 Actor 层级、植被、地形等
3. **动画序列导出**：将 LevelSequence 和 AnimSequence 导出为 USD 动画
4. **材质烘焙**：将 UE 材质烘焙为 UsdPreviewSurface 标准材质
5. **USD 脚本接口**：通过蓝图和 Python 暴露大量 USD 操作函数，用于自动化管线

该模块不仅仅是文件格式转换器，还提供了完整的 USD Stage 操控 API（Prim 剪切/复制/粘贴、Layer 管理、引用/Payload 操作等），使 UE 成为一个功能完整的 USD 创作工具。

## 使用场景

- 你需要将 UE 关卡资产导出到 DCC 工具（Maya、Houdini 等）→ 使用 USD 关卡导出
- 你需要构建影视级资产管线，统一 USD 格式 → 使用 USD 资产导出 + 材质烘焙
- 你需要自动化导出大量资产到 USD → 使用蓝图/Python 脚本调用 `UUsdConversionBlueprintLibrary`
- 你需要在运行时操作 USD Stage（添加引用、修改 Prim）→ 使用 `UUsdConversionBlueprintContext`
- 你需要导出地形（Landscape）为带 LOD 的 USD 网格 → 使用 Landscape 导出选项
- 你需要导出植被实例（Foliage）为 USD → 使用 Foliage 相关工具函数

## 蓝图用法

### 世界工具 (World Utils)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetNumLevelsToExport` | 获取需要导出的关卡总数（排除忽略列表） | `UUsdConversionBlueprintLibrary` |
| `StreamInRequiredLevels` | 流式加载所有需要导出的子关卡 | `UUsdConversionBlueprintLibrary` |
| `RevertSequencerAnimations` | 导出前撤回 Sequencer 动画效果 | `UUsdConversionBlueprintLibrary` |
| `ReapplySequencerAnimations` | 导出后恢复 Sequencer 动画效果 | `UUsdConversionBlueprintLibrary` |
| `GetLoadedLevelNames` | 获取当前已加载关卡的路径名列表 | `UUsdConversionBlueprintLibrary` |
| `GetVisibleInEditorLevelNames` | 获取编辑器中可见的关卡路径名列表 | `UUsdConversionBlueprintLibrary` |
| `StreamOutLevels` | 导出完成后流式卸载之前加载的子关卡 | `UUsdConversionBlueprintLibrary` |
| `GetActorsToConvert` | 获取需要转换的 Actor 集合 | `UUsdConversionBlueprintLibrary` |
| `GenerateObjectVersionString` | 生成对象版本标识字符串（基于 GUID + 时间戳） | `UUsdConversionBlueprintLibrary` |
| `CanExportToLayer` | 检查是否可以导出到指定 USD Layer | `UUsdConversionBlueprintLibrary` |

### Layer 工具 (Layer Utils)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `MakePathRelativeToLayer` | 将路径转为相对于指定 Layer 的相对路径 | `UUsdConversionBlueprintLibrary` |
| `InsertSubLayer` | 向父 Layer 插入子 Layer 引用 | `UUsdConversionBlueprintLibrary` |
| `AddReference` | 向 Prim 添加 USD Reference 合成弧 | `UUsdConversionBlueprintLibrary` |
| `AddPayload` | 向 Prim 添加 USD Payload 合成弧 | `UUsdConversionBlueprintLibrary` |

### Prim 工具 (Prim Utils)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetPrimPathForObject` | 根据 UE 对象获取对应 USD Prim 路径 | `UUsdConversionBlueprintLibrary` |
| `GetSchemaNameForComponent` | 根据 SceneComponent 获取 USD Schema 名称 | `UUsdConversionBlueprintLibrary` |
| `RemoveAllPrimSpecs` | 移除 Prim 的所有 Spec（包括 Variant 内的） | `UUsdConversionBlueprintLibrary` |
| `CutPrims` | 剪切 Prim 到剪贴板 | `UUsdConversionBlueprintLibrary` |
| `CopyPrims` | 复制 Prim 到剪贴板 | `UUsdConversionBlueprintLibrary` |
| `PastePrims` | 粘贴剪贴板中的 Prim 到目标父 Prim | `UUsdConversionBlueprintLibrary` |
| `CanPastePrims` | 检查剪贴板中是否有可粘贴的 Prim | `UUsdConversionBlueprintLibrary` |
| `ClearPrimClipboard` | 清空 Prim 剪贴板 | `UUsdConversionBlueprintLibrary` |
| `DuplicatePrims` | 按指定模式复制 Prim | `UUsdConversionBlueprintLibrary` |

### 植被导出工具 (Foliage Exporter)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetInstancedFoliageActorForLevel` | 获取关卡的 InstancedFoliageActor | `UUsdConversionBlueprintLibrary` |
| `GetUsedFoliageTypes` | 获取植被 Actor 使用的所有 FoliageType | `UUsdConversionBlueprintLibrary` |
| `GetSource` | 获取 FoliageType 的源资产（如 StaticMesh） | `UUsdConversionBlueprintLibrary` |
| `GetInstanceTransforms` | 获取指定 FoliageType 的所有实例变换 | `UUsdConversionBlueprintLibrary` |

### 元数据工具 (Metadata Utils)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetUsdAssetUserData` | 获取对象上的 UsdAssetUserData | `UUsdConversionBlueprintLibrary` |
| `SetUsdAssetUserData` | 设置对象的 UsdAssetUserData | `UUsdConversionBlueprintLibrary` |
| `SetMetadataField` | 设置元数据键值对 | `UUsdConversionBlueprintLibrary` |
| `ClearMetadataField` | 清除元数据字段 | `UUsdConversionBlueprintLibrary` |
| `HasMetadataField` | 检查是否存在指定元数据字段 | `UUsdConversionBlueprintLibrary` |
| `GetMetadataField` | 获取元数据字段值 | `UUsdConversionBlueprintLibrary` |

### 组件转换 (Component Conversion)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetStageRootLayer` | 设置/打开 USD Stage 根层 | `UUsdConversionBlueprintContext` |
| `GetStageRootLayer` | 获取当前 Stage 根层路径 | `UUsdConversionBlueprintContext` |
| `SetEditTarget` | 设置当前编辑目标层 | `UUsdConversionBlueprintContext` |
| `Cleanup` | 释放 Stage 引用（脚本中必须调用） | `UUsdConversionBlueprintContext` |
| `ConvertLightComponent` | 转换灯光组件到 USD | `UUsdConversionBlueprintContext` |
| `ConvertMeshComponent` | 转换网格组件到 USD | `UUsdConversionBlueprintContext` |
| `ConvertCineCameraComponent` | 转换摄像机组件到 USD | `UUsdConversionBlueprintContext` |
| `ConvertAudioComponent` | 转换音频组件到 USD | `UUsdConversionBlueprintContext` |
| `ConvertInstancedFoliageActor` | 转换植被实例到 USD | `UUsdConversionBlueprintContext` |
| `ConvertLandscapeProxyActorMesh` | 转换地形网格到 USD | `UUsdConversionBlueprintContext` |
| `ConvertLandscapeProxyActorMaterial` | 转换地形材质到 USD | `UUsdConversionBlueprintContext` |
| `ConvertMaterialOverrides` | 转换材质覆盖到 USD | `UUsdConversionBlueprintContext` |
| `AuthorUnrealMaterialBinding` | 编写 UE 材质绑定关系 | `UUsdConversionBlueprintContext` |

### 使用示例（蓝图描述）

**场景：将 UE 关卡导出为 USD 文件**

1. 使用 `StreamInRequiredLevels` 确保所有需要导出的子关卡已加载
2. 创建 `ULevelExporterUSDOptions` 对象，设置 StageOptions（格式、UpAxis 等）
3. 设置 AssetFolder 指定资产输出目录
4. 调用导出任务（通过 ExportTask 或直接调用 `ULevelExporterUSD::ExportBinary`）
5. 导出完成后调用 `StreamOutLevels` 恢复关卡状态

**场景：通过 Python 脚本操作 USD Stage**

1. 创建 `UUsdConversionBlueprintContext` 对象
2. 调用 `SetStageRootLayer` 打开或创建 Stage
3. 调用 `SetEditTarget` 设置写入目标层
4. 使用 `Convert*` 系列函数导出各种组件
5. **必须**调用 `Cleanup` 释放 Stage 引用

## C++ 用法

### 头文件引入

```cpp
#include "USDConversionBlueprintLibrary.h"
#include "USDConversionBlueprintContext.h"
#include "LevelExporterUSDOptions.h"
#include "USDAssetOptions.h"
```

### 基本用法：检查导出并生成版本标识

```cpp
// 检查是否可以导出到指定路径
// 来源: Public/USDConversionBlueprintLibrary.h
bool bCanExport = UUsdConversionBlueprintLibrary::CanExportToLayer(TEXT("C:/Exports/MyLevel.usda"));

// 生成对象版本标识用于增量导出
FString VersionString = UUsdConversionBlueprintLibrary::GenerateObjectVersionString(
    MyLevel, ExportOptions
);
```

### 进阶用法：使用上下文对象进行组件转换

```cpp
// 创建转换上下文
// 来源: Public/USDConversionBlueprintContext.h
UUsdConversionBlueprintContext* Context = NewObject<UUsdConversionBlueprintContext>();

// 打开或创建 USD Stage
FFilePath StagePath;
StagePath.FilePath = TEXT("C:/Exports/MyStage.usda");
Context->SetStageRootLayer(StagePath);

// 设置编辑目标层
FFilePath EditTarget;
EditTarget.FilePath = TEXT("C:/Exports/MyStage.usda");
Context->SetEditTarget(EditTarget);

// 转换灯光组件
Context->ConvertLightComponent(MyLightComponent, TEXT("/Root/Lights/MyLight"));

// 转换网格组件
Context->ConvertMeshComponent(MyMeshComponent, TEXT("/Root/Meshes/MyMesh"));

// 完成后必须清理，释放 Stage 引用
Context->Cleanup();
```

### 进阶用法：Prim 剪切/复制/粘贴操作

```cpp
// 来源: Public/USDConversionBlueprintLibrary.h
FString StageRoot = TEXT("C:/Exports/MyStage.usda");

// 复制 Prims
TArray<FString> PrimPaths = { TEXT("/Root/Mesh1"), TEXT("/Root/Mesh2") };
bool bCopied = UUsdConversionBlueprintLibrary::CopyPrims(StageRoot, PrimPaths);

// 粘贴到新的父 Prim 下
if (bCopied)
{
    TArray<FString> PastedPaths = UUsdConversionBlueprintLibrary::PastePrims(
        StageRoot, TEXT("/Root/Group")
    );
}
```

## Demo 示例

```cpp
// USDExportDemo.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "USDExportDemo.generated.h"

class UUsdConversionBlueprintContext;

UCLASS()
class AUSDExportDemo : public AActor
{
    GENERATED_BODY()

public:
    AUSDExportDemo();

    /** 将关卡中的静态网格导出为 USD */
    UFUNCTION(BlueprintCallable, Category = "USD Demo")
    bool ExportLevelToUSD(const FString& OutputPath);

    /** 使用上下文对象批量导出组件 */
    UFUNCTION(BlueprintCallable, Category = "USD Demo")
    bool ExportComponentsToUSD(const FString& OutputPath, const TArray<USceneComponent*>& Components);

protected:
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    UPROPERTY()
    UUsdConversionBlueprintContext* ConversionContext = nullptr;
};
```

```cpp
// USDExportDemo.cpp
#include "USDExportDemo.h"
#include "USDConversionBlueprintLibrary.h"
#include "USDConversionBlueprintContext.h"
#include "LevelExporterUSDOptions.h"

AUSDExportDemo::AUSDExportDemo()
{
    PrimaryActorTick.bCanEverTick = false;
}

bool AUSDExportDemo::ExportLevelToUSD(const FString& OutputPath)
{
    UWorld* World = GetWorld();
    if (!World) return false;

    // 检查是否可以导出到目标路径
    if (!UUsdConversionBlueprintLibrary::CanExportToLayer(OutputPath))
    {
        UE_LOG(LogTemp, Warning, TEXT("Cannot export to layer: %s"), *OutputPath);
        return false;
    }

    // 确保所有关卡已加载
    TSet<FString> LevelsToIgnore;
    int32 NumLevels = UUsdConversionBlueprintLibrary::GetNumLevelsToExport(World, LevelsToIgnore);
    UUsdConversionBlueprintLibrary::StreamInRequiredLevels(World, LevelsToIgnore);

    // 撤回 Sequencer 动画效果
    UUsdConversionBlueprintLibrary::RevertSequencerAnimations();

    // ... 执行实际导出逻辑 ...

    // 恢复 Sequencer 动画
    UUsdConversionBlueprintLibrary::ReapplySequencerAnimations();

    // 流式卸载之前加载的关卡
    TArray<FString> LoadedNames = UUsdConversionBlueprintLibrary::GetLoadedLevelNames(World);
    TArray<FString> VisibleNames = UUsdConversionBlueprintLibrary::GetVisibleInEditorLevelNames(World);
    UUsdConversionBlueprintLibrary::StreamOutLevels(World, LoadedNames, VisibleNames);

    return true;
}

bool AUSDExportDemo::ExportComponentsToUSD(
    const FString& OutputPath,
    const TArray<USceneComponent*>& Components)
{
    // 创建或复用上下文对象
    if (!ConversionContext)
    {
        ConversionContext = NewObject<UUsdConversionBlueprintContext>();
    }

    // 设置 Stage 根层
    FFilePath StagePath;
    StagePath.FilePath = OutputPath;
    ConversionContext->SetStageRootLayer(StagePath);
    ConversionContext->SetEditTarget(StagePath);

    // 遍历组件进行转换
    for (USceneComponent* Comp : Components)
    {
        if (!Comp) continue;

        FString PrimPath = UUsdConversionBlueprintLibrary::GetPrimPathForObject(Comp);

        if (UMeshComponent* MeshComp = Cast<UMeshComponent>(Comp))
        {
            ConversionContext->ConvertMeshComponent(MeshComp, PrimPath);
        }
        else if (ULightComponentBase* LightComp = Cast<ULightComponentBase>(Comp))
        {
            ConversionContext->ConvertLightComponent(LightComp, PrimPath);
        }
    }

    // 清理上下文，释放 Stage 引用
    ConversionContext->Cleanup();
    return true;
}

void AUSDExportDemo::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (ConversionContext)
    {
        ConversionContext->Cleanup();
        ConversionContext = nullptr;
    }
    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `USDClasses` | USD 通用类定义（AssetUserData、StageOptions 等） |
| `USDUtilities` | USD 底层工具函数（Prims 操作、Stage 缓存、类型转换） |
| `USDStage` | USD Stage 管理、编辑器集成 |
| `MaterialBaking` | 材质烘焙为纹理（用于 UsdPreviewSurface 导出） |
| `Analytics` | 导出分析数据上报 |
| `Foliage` | 植被实例数据访问 |
| `Landscape` | 地形数据访问和导出 |
| `LevelSequence` | LevelSequence 动画导出支持 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 截断为 float 的编译警告 |
| 2026-04-29 | `bc4a1bd2` | USD: Add support for assigning BP-independent control rigs. | 添加独立于蓝图的 Control Rig 赋值支持 |
| 2026-04-28 | `4fb59a1d` | USD: Work around update to 26.03 causing AnimQuery internal references to be invalidated when LOD va... | 修复 AnimQuery 在 LOD 变化时内部引用失效问题 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式化说明符不匹配问题 |
| 2026-04-09 | `fb7af182` | USD: Bake all frames of exposure animation tracks. | 烘焙所有曝光动画轨道的帧 |

### 维护评价

**活跃维护**。该模块持续获得功能性更新和 Bug 修复，最近的提交（2026 年 5 月）表明仍在活跃开发中。

- ✅ 仍在活跃维护，最近 1 个月内有功能增强和 Bug 修复
- ✅ 覆盖了完整的导出管线（网格、材质、动画、关卡、植被、地形）
- ⚠️ 标记为实验性（`IsBetaVersion=true`），API 可能在未来版本中变化
- ⚠️ 默认未启用（`EnabledByDefault=false`），需在插件设置中手动启用
- ✅ 提供了丰富的蓝图/Python 接口，适合自动化管线集成
- ✅ 推荐用于需要 USD 导出能力的影视/虚拟制作项目

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter/Source/USDExporter)
- [USD 官方文档](https://openusd.org/release/index.html)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter/Source/USDTests)