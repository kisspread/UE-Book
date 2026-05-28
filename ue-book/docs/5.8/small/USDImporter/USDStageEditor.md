# USD Importer

> Adds support for importing the USD file format into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | USD 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（USD 资产、测试资源） |
| 模块 | `GeometryCacheUSD` (Runtime), `USDClassesEditor` (Runtime), `USDExporter` (Runtime), `USDSchemas` (Runtime), `USDStage` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDStageImporter` (Runtime), `USDTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter) | |

## 用途

本插件为 Unreal Engine 提供完整的 USD（Universal Scene Description）工作流支持。USD 是 Pixar 开发的开放标准场景描述格式，广泛应用于影视和视觉特效行业。

插件解决的核心问题：
- **USD 文件导入**：将 `.usd`、`.usda`、`.usdc` 格式的资产导入 UE，包括几何体、材质、动画、变体等
- **Stage 编辑**：提供可视化编辑器界面，在 UE 内直接浏览和编辑 USD Stage 的层级结构
- **实时同步**：通过 USD Stage Actor 将 USD Stage 实时映射到 UE 场景中，支持 LOD、Payload、变体切换
- **双向工作流**：不仅支持导入，还支持从 UE 导出 USD 格式
- **专业动画集成**：支持 Control Rig、Animation BP 等专业动画工具与 USD 的集成

**注意**：该插件默认禁用且标记为实验性（Beta），需要在项目设置中手动启用。

## 使用场景

- 你在影视或视觉特效行业工作，需要将 Maya/Houdini 等 DCC 工具的资产通过 USD 格式导入 UE → 用 USDImporter
- 你需要在 UE 内实时预览和切换 USD 资产的变体（Variants）、参考（References）、Payload → 用 USD Stage Editor
- 你需要在 UE 和 DCC 工具之间建立 USD 格式的资产交换管线 → 用 USDImporter + USDExporter
- 你的团队使用 USD 的分层工作流，需要在 UE 内管理多个层（Layers）的组合 → 用 USD Stage Editor

## 蓝图用法

`UUsdStageEditorBlueprintLibrary` 提供了完整的蓝图 API，用于以编程方式控制 USD Stage Editor 的所有功能。

### 核心节点

#### 窗口控制

| 节点 | 说明 | 所在类 |
|---|---|---|
| `OpenStageEditor` | 打开 USD Stage Editor 窗口（已打开则聚焦），返回是否成功 | `UUsdStageEditorBlueprintLibrary` |
| `CloseStageEditor` | 关闭 USD Stage Editor 窗口，返回是否成功关闭 | `UUsdStageEditorBlueprintLibrary` |
| `IsStageEditorOpened` | 检查 USD Stage Editor 窗口是否已打开 | `UUsdStageEditorBlueprintLibrary` |

#### Stage Actor 管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetAttachedStageActor` | 获取当前附加到编辑器的 USD Stage Actor | `UUsdStageEditorBlueprintLibrary` |
| `SetAttachedStageActor` | 设置附加到编辑器的 USD Stage Actor（传 nullptr 清除） | `UUsdStageEditorBlueprintLibrary` |

#### 选择操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetSelectedLayerIdentifiers` | 获取当前选中层的标识符列表（如 `["C:/root.usda"]`) | `UUsdStageEditorBlueprintLibrary` |
| `SetSelectedLayerIdentifiers` | 设置层选择（传空数组清除选择） | `UUsdStageEditorBlueprintLibrary` |
| `GetSelectedPrimPaths` | 获取当前选中 Prim 的路径列表（如 `["/Root/Mesh"]`) | `UUsdStageEditorBlueprintLibrary` |
| `SetSelectedPrimPaths` | 设置 Prim 选择 | `UUsdStageEditorBlueprintLibrary` |
| `GetSelectedPropertyNames` | 获取当前选中属性的名称列表（如 `["points", "displayColor"]`) | `UUsdStageEditorBlueprintLibrary` |
| `SetSelectedPropertyNames` | 设置属性选择 | `UUsdStageEditorBlueprintLibrary` |
| `GetSelectedPropertyMetadataNames` | 获取当前选中属性元数据的名称列表 | `UUsdStageEditorBlueprintLibrary` |
| `SetSelectedPropertyMetadataNames` | 设置属性元数据选择 | `UUsdStageEditorBlueprintLibrary` |

#### 文件菜单操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FileNew` | 创建新的内存层并打开新 Stage（对应 File → New） | `UUsdStageEditorBlueprintLibrary` |
| `FileOpen` | 从磁盘文件打开 USD Stage（传空字符串弹出文件选择对话框） | `UUsdStageEditorBlueprintLibrary` |
| `FileSave` | 保存当前 Stage（未保存时使用指定路径） | `UUsdStageEditorBlueprintLibrary` |
| `FileExportAllLayers` | 导出所有层到新文件（对应 File → Export → All Layers） | `UUsdStageEditorBlueprintLibrary` |
| `FileExportFlattenedStage` | 导出扁平化 Stage（对应 File → Export → Flattened stage） | `UUsdStageEditorBlueprintLibrary` |
| `FileExportFlattenedLayerStack` | 导出扁平化层栈（对应 File → Export → Flattened layer stack） | `UUsdStageEditorBlueprintLibrary` |
| `FileReload` | 重新加载所有层（对应 File → Reload） | `UUsdStageEditorBlueprintLibrary` |
| `FileReset` | 重置 Stage 状态（对应 File → Reset state） | `UUsdStageEditorBlueprintLibrary` |
| `FileClose` | 关闭当前 Stage（对应 File → Close） | `UUsdStageEditorBlueprintLibrary` |

#### 导入/导出操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ActionsImport` | 将当前 Stage 导入为持久化 UE 资产和关卡 Actor（对应 Actions → Import） | `UUsdStageEditorBlueprintLibrary` |
| `ExportSelectedLayers` | 导出当前选中的层到指定目录 | `UUsdStageEditorBlueprintLibrary` |

### 使用示例（蓝图描述）

**示例 1：打开 USD Stage Editor 并加载文件**

1. 拖入 `OpenStageEditor` 节点
2. 分支：如果返回 True，拖入 `FileOpen` 节点
3. 设置 `FilePath` 参数为 `"C:/Assets/MyScene.usda"`
4. （可选）先拖入 `SetAttachedStageActor` 节点，连接你的 USD Stage Actor

**示例 2：通过蓝图自动化导出选中层**

1. 拖入 `GetSelectedLayerIdentifiers` 获取当前选择
2. 分支：如果选择不为空，拖入 `ExportSelectedLayers`
3. 设置 `OutputDirectory` 为 `"C:/ExportFolder/"`

**示例 3：批量导入 USD 资产**

1. 使用 `SetAttachedStageActor` 连接到目标 Stage Actor
2. 使用 `FileOpen` 加载 USD 文件
3. 调用 `ActionsImport`，传入 Content 路径和 `UUsdStageImportOptions` 对象
4. 导入完成后调用 `FileClose`

## C++ 用法

### 头文件引入

```cpp
// 模块接口
#include "USDStageEditorModule.h"

// 蓝图库（用于静态函数调用）
#include "USDStageEditorBlueprintLibrary.h"
```

### 基本用法：通过模块接口操作 Stage Editor

```cpp
// 来源：Public/USDStageEditorModule.h

// 获取模块接口
IUsdStageEditorModule& StageEditorModule = FModuleManager::GetModuleChecked<IUsdStageEditorModule>("USDStageEditor");

// 打开编辑器窗口
if (StageEditorModule.OpenStageEditor())
{
    // 设置要编辑的 Stage Actor
    AUsdStageActor* MyActor = /* 获取你的 USD Stage Actor */;
    StageEditorModule.SetAttachedStageActor(MyActor);

    // 打开特定 USD 文件
    StageEditorModule.FileOpen(TEXT("C:/Assets/MyScene.usda"));

    // 查询当前选择
    TArray<FString> SelectedPrims = StageEditorModule.GetSelectedPrimPaths();
    for (const FString& PrimPath : SelectedPrims)
    {
        UE_LOG(LogTemp, Log, TEXT("Selected Prim: %s"), *PrimPath);
    }
}
```

### 进阶用法：完整的导入管线

```cpp
// 综合运用多个功能完成导入流程

#include "USDStageEditorModule.h"
#include "USDStageEditorBlueprintLibrary.h"

void ImportUSDAsset(const FString& UsdFilePath, const FString& OutputContentFolder)
{
    IUsdStageEditorModule& Module = FModuleManager::GetModuleChecked<IUsdStageEditorModule>("USDStageEditor");

    // 1. 确保编辑器已打开
    if (!Module.IsStageEditorOpened())
    {
        Module.OpenStageEditor();
    }

    // 2. 打开目标 USD 文件
    Module.FileOpen(UsdFilePath);

    // 3. 设置导入选项
    UUsdStageImportOptions* Options = NewObject<UUsdStageImportOptions>();
    // 配置导入选项...

    // 4. 执行导入
    Module.ActionsImport(OutputContentFolder, Options);

    // 5. 导出扁平化版本用于备份
    Module.FileExportFlattenedStage(OutputContentFolder / TEXT("Flattened.usda"));

    // 6. 完成后关闭
    Module.FileClose();
}
```

## Demo 示例

### 最小示例：通过蓝图库控制 Stage Editor

```cpp
// UsdEditorDemo.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "UsdEditorDemo.generated.h"

UCLASS()
class AUsdEditorDemo : public AActor
{
    GENERATED_BODY()

public:
    // 打开 Stage Editor 并加载指定文件
    UFUNCTION(BlueprintCallable, Category = "USD Demo")
    void OpenAndLoadUSDStage(const FString& FilePath);

    // 导出当前选中的层
    UFUNCTION(BlueprintCallable, Category = "USD Demo")
    void ExportSelectedLayersTo(const FString& OutputDirectory);

    // 获取当前选择信息
    UFUNCTION(BlueprintPure, Category = "USD Demo")
    FString GetCurrentSelectionSummary() const;
};
```

```cpp
// UsdEditorDemo.cpp
#include "UsdEditorDemo.h"
#include "USDStageEditorBlueprintLibrary.h"

void AUsdEditorDemo::OpenAndLoadUSDStage(const FString& FilePath)
{
    // 确保编辑器窗口打开
    if (!UUsdStageEditorBlueprintLibrary::IsStageEditorOpened())
    {
        UUsdStageEditorBlueprintLibrary::OpenStageEditor();
    }

    // 加载 USD 文件
    UUsdStageEditorBlueprintLibrary::FileOpen(FilePath);
}

void AUsdEditorDemo::ExportSelectedLayersTo(const FString& OutputDirectory)
{
    UUsdStageEditorBlueprintLibrary::ExportSelectedLayers(OutputDirectory);
}

FString AUsdEditorDemo::GetCurrentSelectionSummary() const
{
    TArray<FString> Prims = UUsdStageEditorBlueprintLibrary::GetSelectedPrimPaths();
    TArray<FString> Layers = UUsdStageEditorBlueprintLibrary::GetSelectedLayerIdentifiers();

    FString Summary = FString::Printf(TEXT("Selected Prims: %d, Layers: %d"),
        Prims.Num(), Layers.Num());

    for (const FString& Prim : Prims)
    {
        Summary += TEXT("\n  Prim: ") + Prim;
    }

    return Summary;
}
```

## 模块依赖

USDStageEditor 模块依赖以下非标准模块（推断自源码类型引用）：

| 模块 | 用途 |
|---|---|
| `USDStage` | USD Stage Actor 和 Stage 核心逻辑 |
| `USDSchemas` | USD Schema 类型定义（Prim 类型映射） |
| `USDStageEditorViewModels` | 编辑器 UI 的 ViewModel 层（视图模型绑定） |
| `USDClasses` | USD 共享类定义（FUsdPrim、FSdfLayer 等类型） |
| `UnrealUSDWrapper` | USD SDK 的 UE 封装层 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点数的编译警告 |
| 2026-04-29 | `bc4a1bd2` | USD: Add support for assigning BP-independent control rigs. | 新增支持独立于蓝图的 Control Rig 分配 |
| 2026-04-28 | `4fb59a1d` | USD: Work around update to 26.03 causing AnimQuery internal references to be invalidated when LOD va... | 修复 26.03 版本更新导致 LOD 变体切换时 AnimQuery 内部引用失效的问题 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32 位和 64 位格式说明符与参数不匹配的问题 |
| 2026-04-09 | `fb7af182` | USD: Bake all frames of exposure animation tracks. | 修复曝光动画轨道所有帧的烘焙处理 |

### 维护评价

- **活跃维护** ✅：最近一个月内有多次功能性更新，包括新特性（Control Rig 支持）和 Bug 修复
- **实验性状态** ⚠️：`.uplugin` 中 `IsBetaVersion=true` 且 `EnabledByDefault=false`，仍处于 Beta 阶段
- **模块规模**：大型插件（187 个源文件），包含 9 个模块，覆盖导入、导出、编辑器 UI、测试等完整功能
- **持续演进**：从 2018 年创建至今持续更新，最近在动画集成和 LOD 系统方面有显著改进
- **已知限制**：
  - 需要手动在项目设置中启用
  - 依赖外部 USD SDK
  - 部分功能依赖 `USE_USD_SDK` 宏编译条件
- **推荐使用**：适合需要 USD 工作流的专业制作管线，但需注意 Beta 状态意味着 API 可能变动

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter)
- [官方文档]()（.uplugin 未提供文档链接）