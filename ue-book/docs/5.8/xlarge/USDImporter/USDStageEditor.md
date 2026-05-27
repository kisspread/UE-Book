# USD Importer

> Adds support for importing the USD file format into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | USD 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质模板、测试资源） |
| 模块 | `GeometryCacheUSD` (Runtime), `USDClassesEditor` (Runtime), `USDExporter` (Runtime), `USDSchemas` (Runtime), `USDStage` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDStageImporter` (Runtime), `USDTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter) | |

## 用途

本插件为 Unreal Engine 提供完整的 Pixar USD（Universal Scene Description）格式支持，解决以下核心问题：

1. **USD 资产导入**：将 `.usd`、`.usda`、`.usdc` 格式的场景描述文件导入为 UE 资产（网格体、材质、动画等）
2. **Stage 编辑器**：提供交互式的 USD Stage 查看和编辑窗口，支持 Prim 树浏览、Layer 管理、属性查看
3. **实时同步**：通过 USD Stage Actor 在运行时/编辑器中实时渲染 USD 场景
4. **USD 导出**：将 UE 场景数据导出为 USD 格式，支持 DCC 工具间的资产交换
5. **Geometry Cache**：USD 格式的几何体缓存支持
6. **USD Schema 集成**：支持 USD 的 Variants、References、Payloads 等高级特性

与简单的文件格式转换器不同，本插件维护了一个完整的 USD 运行时，支持 USD 的 Composition Arcs（引用、变体、Payloads），使得导入结果忠实于原始 USD 资产的层级结构和变体设计。

**需要手动启用**：此插件默认禁用（`EnabledByDefault: false`），需在 Plugins 面板中手动启用，或在项目的 `.uproject` 文件中添加 `"Enabled": true`。

## 使用场景

- 你的美术团队使用 Maya/Houdini/Blender 通过 USD 管线生产资产 → 用 USDImporter 导入到 UE
- 你需要查看和调试 USD Stage 的层级结构、Prim 属性、变体选择 → 用 USD Stage Editor 窗口
- 你需要将 UE 中的关卡或资产导出为 USD 格式供 DCC 工具使用 → 用 USDExporter
- 你需要在运行时动态加载和切换 USD 变体（Variants） → 用 USDStage Actor 的 Blueprint 接口
- 你需要 USD 格式的缓存动画数据用于几何体缓存播放 → 用 GeometryCacheUSD
- 你需要在 USD 和 UE 之间保持资产的实时双向同步 → 用 USDStage Actor 的 Live Edit 功能

## 蓝图用法

### 核心节点

#### Stage Editor 控制

| 节点 | 说明 | 所在类 |
|---|---|---|
| `OpenStageEditor` | 打开 USD Stage Editor 窗口（已打开则聚焦） | `UUsdStageEditorBlueprintLibrary` |
| `CloseStageEditor` | 关闭 USD Stage Editor 窗口 | `UUsdStageEditorBlueprintLibrary` |
| `IsStageEditorOpened` | 检查 Stage Editor 窗口是否已打开 | `UUsdStageEditorBlueprintLibrary` |

#### Stage Actor 管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetAttachedStageActor` | 获取当前 Stage Editor 关联的 Stage Actor | `UUsdStageEditorBlueprintLibrary` |
| `SetAttachedStageActor` | 设置 Stage Editor 关联的 Stage Actor（传 null 清除） | `UUsdStageEditorBlueprintLibrary` |

#### 选择操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetSelectedLayerIdentifiers` | 获取当前选中的 Layer 标识符列表 | `UUsdStageEditorBlueprintLibrary` |
| `SetSelectedLayerIdentifiers` | 设置 Layer 选中状态 | `UUsdStageEditorBlueprintLibrary` |
| `GetSelectedPrimPaths` | 获取当前选中的 Prim 路径列表 | `UUsdStageEditorBlueprintLibrary` |
| `SetSelectedPrimPaths` | 设置 Prim 选中状态 | `UUsdStageEditorBlueprintLibrary` |
| `GetSelectedPropertyNames` | 获取当前选中的属性名称列表 | `UUsdStageEditorBlueprintLibrary` |
| `SetSelectedPropertyNames` | 设置属性选中状态 | `UUsdStageEditorBlueprintLibrary` |
| `GetSelectedPropertyMetadataNames` | 获取选中的属性元数据名称列表 | `UUsdStageEditorBlueprintLibrary` |
| `SetSelectedPropertyMetadataNames` | 设置属性元数据选中状态 | `UUsdStageEditorBlueprintLibrary` |

#### 文件菜单操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FileNew` | 创建新内存 Layer 并打开新 Stage | `UUsdStageEditorBlueprintLibrary` |
| `FileOpen` | 从磁盘打开 USD Stage（空路径弹出文件对话框） | `UUsdStageEditorBlueprintLibrary` |
| `FileSave` | 保存当前 Stage 到磁盘 | `UUsdStageEditorBlueprintLibrary` |
| `FileReload` | 重新加载所有 Layer | `UUsdStageEditorBlueprintLibrary` |
| `FileReset` | 重置 Stage 状态（静音状态、编辑目标等） | `UUsdStageEditorBlueprintLibrary` |
| `FileClose` | 关闭当前 Stage（清空 RootLayer） | `UUsdStageEditorBlueprintLibrary` |

#### 导出操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FileExportAllLayers` | 将所有 Layer 导出为新文件 | `UUsdStageEditorBlueprintLibrary` |
| `FileExportFlattenedStage` | 导出为单个扁平化 Stage | `UUsdStageEditorBlueprintLibrary` |
| `FileExportFlattenedLayerStack` | 导出为扁平化 Layer Stack | `UUsdStageEditorBlueprintLibrary` |
| `ExportSelectedLayers` | 导出当前选中的 Layer | `UUsdStageEditorBlueprintLibrary` |

#### 导入操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ActionsImport` | 将当前 Stage 导入为持久化 UE 资产和 Actor | `UUsdStageEditorBlueprintLibrary` |

### 使用示例（蓝图描述）

**自动化 USD 导入流程**：

1. 使用 `OpenStageEditor` 节点打开 Stage Editor 窗口
2. 调用 `FileOpen` 节点，传入 USD 文件路径字符串，例如 `"C:/Assets/Scene.usd"`
3. 通过 `GetSelectedPrimPaths` 获取自动选中的 Prim
4. 调用 `SetSelectedPrimPaths` 手动选择需要导入的 Prim
5. 调用 `ActionsImport` 节点，指定输出内容目录（如 `"/Game/USDImports"`）和导入选项
6. 使用 `FileClose` 关闭 Stage

**USD 变体切换**：

1. 通过 `SetAttachedStageActor` 将已放置的 USD Stage Actor 关联到编辑器
2. 使用 `SetSelectedPrimPaths` 选择包含变体集的 Prim
3. 通过属性面板中的变体下拉框切换变体选择
4. 调用 `ActionsImport` 将变体选择结果导入为持久资产

## C++ 用法

### 头文件引入

```cpp
// USD Stage Editor 模块接口
#include "USDStageEditorModule.h"

// USD Stage Editor 蓝图库（C++ 中直接使用静态函数）
#include "USDStageEditorBlueprintLibrary.h"
```

### 基本用法

从模块接口获取编辑器实例并操作（来源：`USDStageEditorModule.h`）：

```cpp
// 获取 USD Stage Editor 模块
IUsdStageEditorModule& StageEditorModule = FModuleManager::Get().LoadModuleChecked<IUsdStageEditorModule>("USDStageEditor");

// 打开 Stage Editor 窗口
if (StageEditorModule.OpenStageEditor())
{
    UE_LOG(LogTemp, Log, TEXT("USD Stage Editor 已打开"));
}

// 检查窗口状态
if (StageEditorModule.IsStageEditorOpened())
{
    // 获取当前选中的 Prim
    TArray<UE::FUsdPrim> SelectedPrims = StageEditorModule.GetSelectedPrims();
    UE_LOG(LogTemp, Log, TEXT("选中了 %d 个 Prim"), SelectedPrims.Num());
}
```

### 进阶用法

通过 C++ 模块接口进行完整文件操作流程（来源：`USDStageEditorModule.h`、`USDStageEditorBlueprintLibrary.h`）：

```cpp
#include "USDStageEditorModule.h"
#include "USDStageEditorBlueprintLibrary.h"

void ImportUSDAsset(const FString& USDFilePath, const FString& ContentFolder)
{
    IUsdStageEditorModule& Module = FModuleManager::Get().LoadModuleChecked<IUsdStageEditorModule>("USDStageEditor");
    
    // 1. 确保编辑器窗口已打开
    Module.OpenStageEditor();
    
    // 2. 打开 USD 文件
    Module.FileOpen(USDFilePath);
    
    // 3. 获取所有选中的 Prim
    TArray<UE::FUsdPrim> Prims = Module.GetSelectedPrims();
    
    // 4. 设置选择的属性
    TArray<FString> PropNames = { TEXT("points"), TEXT("normals") };
    Module.SetSelectedPropertyNames(PropNames);
    
    // 5. 执行导入（传入 UUsdStageImportOptions 配置导入参数）
    Module.ActionsImport(ContentFolder, nullptr);
    
    // 6. 完成后关闭
    Module.FileClose();
}

// 使用蓝图库的静态函数（无需获取模块实例）
void QuickOpenUSD(const FString& Path)
{
    // 这些函数也可以直接在 C++ 中调用
    UUsdStageEditorBlueprintLibrary::OpenStageEditor();
    UUsdStageEditorBlueprintLibrary::FileOpen(Path);
    
    // 获取关联的 Stage Actor
    AUsdStageActor* Actor = UUsdStageEditorBlueprintLibrary::GetAttachedStageActor();
    if (Actor)
    {
        UE_LOG(LogTemp, Log, TEXT("Stage Actor: %s"), *Actor->GetName());
    }
}
```

## Demo 示例

最小示例：打开 USD 文件并查询选择状态。

### MyUSDHelper.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "USDStageEditorModule.h"

class FMyUSDHelper
{
public:
    /** 打开 USD 文件并返回选中的 Prim 数量 */
    static int32 OpenAndCountPrims(const FString& FilePath);
    
    /** 导出选中层到指定目录 */
    static bool ExportSelectedLayersTo(const FString& OutputDir);
};
```

### MyUSDHelper.cpp

```cpp
#include "MyUSDHelper.h"
#include "USDStageEditorBlueprintLibrary.h"

int32 FMyUSDHelper::OpenAndCountPrims(const FString& FilePath)
{
    // 打开编辑器并加载文件
    UUsdStageEditorBlueprintLibrary::OpenStageEditor();
    UUsdStageEditorBlueprintLibrary::FileOpen(FilePath);
    
    // 查询当前选中
    TArray<FString> SelectedPaths = UUsdStageEditorBlueprintLibrary::GetSelectedPrimPaths();
    
    return SelectedPaths.Num();
}

bool FMyUSDHelper::ExportSelectedLayersTo(const FString& OutputDir)
{
    if (!UUsdStageEditorBlueprintLibrary::IsStageEditorOpened())
    {
        return false;
    }
    
    UUsdStageEditorBlueprintLibrary::ExportSelectedLayers(OutputDir);
    return true;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `UnrealUSDWrapper` | USD SDK 的 UE 封装层，提供 FSdfLayer、FUsdPrim、FUsdAttribute 等核心类型 |
| `USDStage` | USD Stage Actor 及其运行时行为 |
| `USDSchemas` | USD Schema 类型定义（如 Collapsed Prim Schema） |
| `USDExporter` | USD 导出功能 |
| `USDClassesEditor` | USD 编辑器通用类 |
| `USDStageImporter` | USD 导入器核心逻辑 |
| `GeometryCacheUSD` | USD 几何体缓存支持 |
| `USDStageEditorViewModels` | Stage Editor 的 MVVM ViewModel 层 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的警告 |
| 2026-04-29 | `bc4a1bd2` | USD: Add support for assigning BP-independent control rigs. | 新增支持分配独立于蓝图的 Control Rig |
| 2026-04-28 | `4fb59a1d` | USD: Work around update to 26.03 causing AnimQuery internal references to be invalidated when LOD va | 修复 USD 26.03 更新导致 AnimQuery 内部引用在 LOD 变化时失效的问题 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正 32/64 位格式说明符与实际参数类型不匹配的问题 |
| 2026-04-09 | `fb7af182` | USD: Bake all frames of exposure animation tracks. | USD：烘焙曝光动画轨道的所有帧 |

### 维护评价

- **创建时间**：2018 年 11 月，已有约 8 年历史
- **近期活跃度**：2026 年 4-5 月有多次实质性功能更新（Control Rig 集成、USD 26.03 兼容性修复、动画烘焙改进），维护非常活跃
- **Beta 状态**：`.uplugin` 标记为 `IsBetaVersion: true`，表明 Epic 仍视其为实验性功能，API 可能发生变化
- **默认禁用**：`EnabledByDefault: false`，需手动启用
- **模块规模**：9 个模块、187 个源文件，属于大型基础设施级插件

**综合评价**：插件处于**活跃维护**状态，频繁更新表明 Epic 持续投入开发。虽然标记为 Beta，但已具备完整的导入/导出/编辑能力，是 UE 中与 DCC 工具进行 USD 资产交换的核心基础设施。推荐在 USD 生产管线中使用，但需注意 Beta 标签意味着 API 可能在版本间发生变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter)
- [官方文档](https://docs.unrealengine.com/en-US/working-with-content/using-universal-scene-description-in-unreal-engine/)（USD in UE 官方文档）