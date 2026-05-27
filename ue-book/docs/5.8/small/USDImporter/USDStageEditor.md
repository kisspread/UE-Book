# USD Importer

> Adds support for importing the USD file format into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | USD 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `GeometryCacheUSD` (Runtime), `USDClassesEditor` (Runtime), `USDExporter` (Runtime), `USDSchemas` (Runtime), `USDStage` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDStageImporter` (Runtime), `USDTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter) | |

## 用途

USD Importer 是 Epic Games 为 Unreal Engine 提供的 **Pixar USD（Universal Scene Description）** 全流程支持插件。它不仅仅是简单的文件导入工具，而是一个完整的 USD 工作流集成方案，涵盖：

- **USD 文件导入**：将 `.usd`、`.usda`、`.usdc` 格式文件导入为 UE 资产（网格体、材质、动画等）
- **USD Stage 编辑器**：提供可视化的 USD Stage 浏览与编辑界面，类似 DCC 软件中的 USD 功能
- **USD 导出**：将 UE 场景或资产导出为 USD 格式，实现双向数据交换
- **USD Schema 支持**：通过 `USDSchemas` 模块支持自定义 USD Schema 的解析
- **GeometryCache USD**：支持将 USD 的几何缓存（如 Alembic 式动画网格）导入为 UE 的 GeometryCache

该插件通过 `AUsdStageActor` 将 USD Stage 桥接到 UE 的关卡系统，支持 Variant Set 切换、Payload 加载控制、层级管理等高级 USD 功能。

**注意**：该插件默认未启用（`EnabledByDefault: false`），需要在编辑器的 Plugins 面板中手动开启。

## 使用场景

- 你从 Maya/Houdini/Blender 等 DCC 工具导出了 USD 文件，需要导入到 UE 中 → 用 USD Importer
- 你需要在 UE 中浏览和编辑复杂的 USD 层级结构（Sublayer、Reference、Payload）→ 用 USD Stage Editor
- 你需要将 UE 场景导出为 USD 格式，与上游资产管线对接 → 用 USD Exporter
- 你需要在运行时或编辑器中切换 USD Variant Set（如不同的角色外观变体）→ 用 USD Stage Actor 的 Variant 面板
- 你需要将 USD 的几何缓存（骨骼动画网格序列）导入为 GeometryCache → 用 GeometryCacheUSD

## 蓝图用法

> 以下 API 来自 `UUsdStageEditorBlueprintLibrary`，属于 `USDStageEditor` 模块。通过蓝图脚本可完全控制 USD Stage Editor 的 UI 和操作。

### 核心节点

#### 编辑器窗口控制

| 节点 | 说明 | 所在类 |
|---|---|---|
| `OpenStageEditor` | 打开 USD Stage Editor 窗口，若已打开则聚焦 | `UUsdStageEditorBlueprintLibrary` |
| `CloseStageEditor` | 关闭 USD Stage Editor 窗口 | `UUsdStageEditorBlueprintLibrary` |
| `IsStageEditorOpened` | 检查 Stage Editor 窗口是否已打开 | `UUsdStageEditorBlueprintLibrary` |

#### Stage Actor 绑定

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetAttachedStageActor` | 获取当前绑定到编辑器的 AUsdStageActor | `UUsdStageEditorBlueprintLibrary` |
| `SetAttachedStageActor` | 设置绑定的 Stage Actor（传 None 可解除绑定） | `UUsdStageEditorBlueprintLibrary` |

#### 选择查询与设置

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetSelectedLayerIdentifiers` | 获取当前选中的 Layer 标识符列表 | `UUsdStageEditorBlueprintLibrary` |
| `SetSelectedLayerIdentifiers` | 设置 Layer 选择 | `UUsdStageEditorBlueprintLibrary` |
| `GetSelectedPrimPaths` | 获取当前选中的 Prim 路径列表 | `UUsdStageEditorBlueprintLibrary` |
| `SetSelectedPrimPaths` | 设置 Prim 选择 | `UUsdStageEditorBlueprintLibrary` |
| `GetSelectedPropertyNames` | 获取当前选中的属性名称列表 | `UUsdStageEditorBlueprintLibrary` |
| `SetSelectedPropertyNames` | 设置属性选择 | `UUsdStageEditorBlueprintLibrary` |
| `GetSelectedPropertyMetadataNames` | 获取当前选中的属性元数据名称列表 | `UUsdStageEditorBlueprintLibrary` |
| `SetSelectedPropertyMetadataNames` | 设置属性元数据选择 | `UUsdStageEditorBlueprintLibrary` |

#### 菜单操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FileNew` | 创建新的内存 Layer 并打开 Stage | `UUsdStageEditorBlueprintLibrary` |
| `FileOpen` | 从磁盘打开 USD 文件（空字符串则弹出文件选择对话框） | `UUsdStageEditorBlueprintLibrary` |
| `FileSave` | 保存当前 Stage 到磁盘 | `UUsdStageEditorBlueprintLibrary` |
| `FileExportAllLayers` | 导出所有 Layer 到新位置 | `UUsdStageEditorBlueprintLibrary` |
| `FileExportFlattenedStage` | 导出为单一扁平化 Stage | `UUsdStageEditorBlueprintLibrary` |
| `FileExportFlattenedLayerStack` | 导出为单一扁平化 Layer Stack | `UUsdStageEditorBlueprintLibrary` |
| `FileReload` | 重新加载所有 Layer | `UUsdStageEditorBlueprintLibrary` |
| `FileReset` | 重置 Stage 状态（静音层、编辑目标等） | `UUsdStageEditorBlueprintLibrary` |
| `FileClose` | 关闭当前 Stage | `UUsdStageEditorBlueprintLibrary` |
| `ActionsImport` | 将当前 Stage 导入为持久化 UE 资产 | `UUsdStageEditorBlueprintLibrary` |
| `ExportSelectedLayers` | 导出选中的 Layer | `UUsdStageEditorBlueprintLibrary` |

### 使用示例（蓝图描述）

**示例 1：通过蓝图自动化 USD 导入流程**

1. 使用 `OpenStageEditor` 节点确保编辑器窗口打开
2. 调用 `FileOpen`，传入 USD 文件路径（如 `"C:/Assets/scene.usda"`）
3. 调用 `SetAttachedStageActor` 绑定场景中的 AUsdStageActor
4. 调用 `ActionsImport`，传入目标 Content 文件夹（如 `"/Game/USDImports"`）和导入选项对象

**示例 2：脚本化选择操作**

1. 调用 `SetSelectedPrimPaths` 传入数组 `["/Root/Mesh1", "/Root/Mesh2"]` 选中特定 Prim
2. 调用 `GetSelectedPropertyNames` 获取选中 Prim 的属性列表用于后续处理

## C++ 用法

### 头文件引入

```cpp
#include "USDStageEditorBlueprintLibrary.h"
#include "USDStageEditorModule.h"
```

### 基本用法

通过模块接口直接调用 USD Stage Editor 功能（来源：`USDStageEditorModule.h`）：

```cpp
// 获取 USD Stage Editor 模块接口
IUsdStageEditorModule& StageEditorModule = FModuleManager::LoadModuleChecked<IUsdStageEditorModule>("USDStageEditor");

// 打开编辑器窗口
if (StageEditorModule.OpenStageEditor())
{
    // 绑定一个 Stage Actor
    AUsdStageActor* MyStageActor = /* 获取或 Spawn */;
    StageEditorModule.SetAttachedStageActor(MyStageActor);
    
    // 从磁盘打开 USD 文件
    StageEditorModule.FileOpen(TEXT("C:/Assets/MyScene.usda"));
    
    // 导入为 UE 资产
    UUsdStageImportOptions* Options = NewObject<UUsdStageImportOptions>();
    StageEditorModule.ActionsImport(TEXT("/Game/Imports"), Options);
}
```

### 进阶用法

查询和设置编辑器中的选择状态：

```cpp
IUsdStageEditorModule& StageEditorModule = FModuleManager::LoadModuleChecked<IUsdStageEditorModule>("USDStageEditor");

// 获取当前选中的 Prim
TArray<UE::FUsdPrim> SelectedPrims = StageEditorModule.GetSelectedPrims();

// 获取当前选中的 Layer
TArray<UE::FSdfLayer> SelectedLayers = StageEditorModule.GetSelectedLayers();

// 设置 Prim 选择（基于路径）
TArray<FString> PrimPaths = { TEXT("/Root/Prim1"), TEXT("/Root/Prim2") };
StageEditorModule.SetSelectedPropertyNames(PrimPaths);

// 文件操作序列：新建 → 编辑 → 保存
StageEditorModule.FileNew();
// ... 进行编辑操作 ...
StageEditorModule.FileSave(TEXT("C:/Output/NewStage.usda"));

// 导出扁平化 Stage
StageEditorModule.FileExportFlattenedStage(TEXT("C:/Export/flattened.usda"));
```

## Demo 示例

以下是一个最小示例，演示如何通过 C++ 代码启动 USD Stage Editor 并打开文件：

### UsdStageEditorDemo.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "UsdStageEditorDemo.generated.h"

class AUsdStageActor;

UCLASS()
class AUsdStageEditorDemo : public AActor
{
    GENERATED_BODY()

public:
    AUsdStageEditorDemo();

    UFUNCTION(BlueprintCallable, CallInEditor, Category = "USD Demo")
    void OpenAndImportUsdFile(const FString& UsdFilePath, const FString& OutputFolder);

    UPROPERTY(EditAnywhere, Category = "USD Demo")
    FString DefaultUsdFilePath;

    UPROPERTY(EditAnywhere, Category = "USD Demo")
    FString DefaultOutputFolder = TEXT("/Game/USDImports");
};
```

### UsdStageEditorDemo.cpp

```cpp
#include "UsdStageEditorDemo.h"
#include "USDStageEditorModule.h"

AUsdStageEditorDemo::AUsdStageEditorDemo()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AUsdStageEditorDemo::OpenAndImportUsdFile(const FString& UsdFilePath, const FString& OutputFolder)
{
    IUsdStageEditorModule* StageEditorModule = FModuleManager::GetModulePtr<IUsdStageEditorModule>("USDStageEditor");
    if (!StageEditorModule)
    {
        UE_LOG(LogTemp, Error, TEXT("USDStageEditor module is not loaded. Please enable the USDImporter plugin."));
        return;
    }

    // 确保编辑器窗口打开
    if (!StageEditorModule->IsStageEditorOpened())
    {
        StageEditorModule->OpenStageEditor();
    }

    // 打开 USD 文件
    const FString& PathToOpen = UsdFilePath.IsEmpty() ? DefaultUsdFilePath : UsdFilePath;
    StageEditorModule->FileOpen(PathToOpen);

    // 执行导入
    const FString& Folder = OutputFolder.IsEmpty() ? DefaultOutputFolder : OutputFolder;
    StageEditorModule->ActionsImport(Folder, nullptr);
}
```

## 模块依赖

USDImporter 包含 9 个模块，以下是各模块的用途概览：

| 模块 | 用途 |
|---|---|
| `USDSchemas` | USD Schema 定义与解析，提供 USD 类型到 UE 类型的映射基础 |
| `USDStage` | USD Stage 管理核心，包含 `AUsdStageActor` 及 Stage 运行时逻辑 |
| `USDStageImporter` | USD 文件的实际导入逻辑（资产转换、材质创建等） |
| `USDStageEditor` | USD Stage 编辑器 UI，提供可视化浏览和编辑功能 |
| `USDStageEditorViewModels` | 编辑器 UI 的 ViewModel 层（MVVM 架构） |
| `USDClassesEditor` | 编辑器相关 USD 类定义 |
| `USDExporter` | 将 UE 场景/资产导出为 USD 格式 |
| `GeometryCacheUSD` | USD 几何缓存导入支持（动画网格序列） |
| `USDTests` | USD 功能的自动化测试 |

使用 USDStageEditor 模块的特殊依赖：

| 模块 | 用途 |
|---|---|
| `USDStage` | 提供 `AUsdStageActor`、Stage 管理和 USD Core 封装 |
| `USDStageEditorViewModels` | 编辑器面板的 ViewModel 数据绑定 |
| `LevelEditor` | 关卡编辑器集成（Viewport 选择同步等） |
| `SceneOutliner` | Actor 选择器面板（Stage Actor Picker 使用） |
| `ToolMenus` | 菜单注册与扩展系统 |
| `USDExporter` | 导出功能支持 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-04-29 | `bc4a1bd2` | USD: Add support for assigning BP-independent control rigs. | 新增支持独立于蓝图的 Control Rig 赋值 |
| 2026-04-28 | `4fb59a1d` | USD: Work around update to 26.03 causing AnimQuery internal references to be invalidated when LOD va... | 修复 USD 26.03 更新导致 LOD 变化时 AnimQuery 内部引用失效的问题 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式化说明符不匹配问题 |
| 2026-04-09 | `fb7af182` | USD: Bake all frames of exposure animation tracks. | 支持烘焙曝光动画轨道的所有帧 |

### 维护评价

**🟢 活跃维护中**

- **创建时间**：2018 年 11 月，已持续维护约 7 年
- **更新频率**：近一个月内有 5 次更新，更新非常频繁
- **更新内容**：涵盖功能新增（Control Rig 集成、动画轨道烘焙）、USD SDK 版本兼容修复、编译警告修复等，说明该插件仍在持续迭代和适配新版 USD SDK
- **状态标志**：`IsBetaVersion=true`、`EnabledByDefault=false`，表明 Epic 仍将此标记为实验性功能
- **注意事项**：虽然标记为 Beta，但该插件已被大量项目实际使用（尤其在虚拟制片和影视管线中），且 Epic 持续投入开发资源

**推荐使用**：✅ 推荐。对于需要 USD 管线集成的项目，这是官方且唯一的选择。尽管标记为 Beta，其功能完整度和维护质量均很高。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter)
- [官方文档](https://docs.unrealengine.com/en-US/working-with-content/usd-in-unreal/)（USD In Unreal 官方文档）