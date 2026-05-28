# USD Importer

> Adds support for importing the USD file format into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | USD 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器面板、蓝图函数库、测试模块） |
| 模块 | `GeometryCacheUSD` (Runtime), `USDClassesEditor` (Runtime), `USDExporter` (Runtime), `USDSchemas` (Runtime), `USDStage` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDStageImporter` (Runtime), `USDTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter) | |

## 用途

USD Importer 插件为 Unreal Engine 提供完整的 USD（Universal Scene Description）工作流支持。它不仅是一个简单的文件导入器，更是一个完整的 USD 舞台编辑和管理工具集。该插件解决的核心问题是：在 Unreal Engine 中打开、查看、编辑、导出 USD 舞台文件（.usda, .usdc, .usdz 等），并实现与 DCC 工具（如 Maya、Houdini）的 USD 资产无缝交互。

主要功能包括：
1. **USD 舞台编辑器**：提供专用的编辑器窗口，以树形结构查看和编辑 USD 舞台的层级（Layer）、图元（Prim）和属性（Property）
2. **舞台演员管理**：通过 `AUsdStageActor` 在场景中实例化 USD 舞台，实现运行时加载和交互
3. **完整的导入/导出管线**：支持从 USD 赞助创建 Unreal 资产，或将 Unreal 场景导出为 USD 格式
4. **高级编辑功能**：支持变体（Variants）选择、引用（References）和载荷（Payloads）管理、图元编辑等
5. **蓝图可脚本化**：提供完整的蓝图函数库，实现 USD 操作的脚本化自动化

## 使用场景

- **游戏资产管线**：使用 USD 作为统一资产交换格式，在 Unreal、Maya、Houdini 之间同步场景数据
- **虚拟制片**：在虚拟制片工作流中加载和编辑 USD 舞台，支持实时场景更新
- **建筑可视化**：导入从 Revit、SketchUp 等工具导出的 USD 建筑模型
- **技术美术工具开发**：通过蓝图脚本自动化批量 USD 操作，如批量导入、属性修改、舞台烘焙等
- **自定义内容创建**：在 Unreal 内直接创建和编辑 USD 舞台，无需切换到外部工具

## 蓝图用法

USD Stage Editor 模块提供 `UUsdStageEditorBlueprintLibrary` 类，包含丰富的蓝图节点用于与 USD 舞台编辑器交互。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `OpenStageEditor` | 打开或聚焦 USD Stage Editor 窗口 | `UUsdStageEditorBlueprintLibrary` |
| `CloseStageEditor` | 关闭 USD Stage Editor 窗口 | `UUsdStageEditorBlueprintLibrary` |
| `IsStageEditorOpened` | 检查编辑器窗口是否打开 | `UUsdStageEditorBlueprintLibrary` |
| `GetAttachedStageActor` | 获取当前附加的舞台演员 | `UUsdStageEditorBlueprintLibrary` |
| `SetAttachedStageActor` | 设置当前附加的舞台演员 | `UUsdStageEditorBlueprintLibrary` |
| `GetSelectedLayerIdentifiers` | 获取选中的图层标识符列表 | `UUsdStageEditorBlueprintLibrary` |
| `SetSelectedLayerIdentifiers` | 设置选中的图层标识符列表 | `UUsdStageEditorBlueprintLibrary` |
| `GetSelectedPrimPaths` | 获取选中的图元路径列表 | `UUsdStageEditorBlueprintLibrary` |
| `SetSelectedPrimPaths` | 设置选中的图元路径列表 | `UUsdStageEditorBlueprintLibrary` |
| `FileOpen` | 从磁盘打开 USD 舞台 | `UUsdStageEditorBlueprintLibrary` |
| `FileSave` | 保存当前 USD 舞台 | `UUsdStageEditorBlueprintLibrary` |
| `ActionsImport` | 将当前舞台导入为持久化 UE 资产 | `UUsdStageEditorBlueprintLibrary` |

### 使用示例（蓝图描述）

1. **自动化 USD 导入流程**：
   - 使用 `OpenStageEditor` 打开编辑器
   - 调用 `FileOpen` 加载指定的 USD 文件路径
   - 调用 `SetSelectedLayerIdentifiers` 选择要导入的层
   - 调用 `ActionsImport` 执行导入操作
   - 使用 `GetAttachedStageActor` 获取生成的舞台演员引用

2. **批量处理 USD 属性**：
   - 调用 `GetSelectedPrimPaths` 获取所有选中的图元
   - 循环遍历图元路径，对每个图元调用蓝图操作
   - 调用 `SetSelectedPropertyNames` 选择要修改的属性
   - 通过舞台演员接口修改属性值

3. **舞台状态管理**：
   - 使用 `FileExportAllLayers` 导出所有图层到指定目录
   - 调用 `FileExportFlattenedStage` 生成扁平化的舞台文件
   - 使用 `FileReload` 重新加载舞台以刷新更改

## C++ 用法

### 头文件引入

```cpp
#include "USDStageEditorModule.h"
```

### 基本用法

从公共 API 接口 `IUsdStageEditorModule` 进行交互。

```cpp
// 获取 USD Stage Editor 模块实例
if (IUsdStageEditorModule* StageEditorModule = FModuleManager::GetModulePtr<IUsdStageEditorModule>("USDStageEditor"))
{
    // 打开编辑器窗口
    StageEditorModule->OpenStageEditor();
    
    // 检查编辑器状态
    bool bIsOpened = StageEditorModule->IsStageEditorOpened();
    
    // 获取当前选中的图元
    TArray<UE::FUsdPrim> SelectedPrims = StageEditorModule->GetSelectedPrims();
    
    // 设置附加的舞台演员
    if (AUsdStageActor* StageActor = FindStageActor())
    {
        StageEditorModule->SetAttachedStageActor(StageActor);
    }
}
```

### 进阶用法

组合使用编辑器操作和舞台管理：

```cpp
// 使用模块接口执行完整的工作流
if (IUsdStageEditorModule* StageEditorModule = FModuleManager::GetModulePtr<IUsdStageEditorModule>("USDStageEditor"))
{
    // 1. 打开 USD 文件
    StageEditorModule->FileOpen(TEXT("C:/Projects/Scene.usda"));
    
    // 2. 等待编辑器就绪（在实际使用中可能需要延迟或回调）
    
    // 3. 获取选中的图层
    TArray<UE::FSdfLayer> SelectedLayers = StageEditorModule->GetSelectedLayers();
    
    // 4. 设置编辑目标层
    if (SelectedLayers.Num() > 0)
    {
        // 通过舞台演员接口设置编辑目标
        if (AUsdStageActor* StageActor = StageEditorModule->GetAttachedStageActor())
        {
            StageActor->SetEditTarget(SelectedLayers[0]);
        }
    }
    
    // 5. 导出扁平化舞台
    StageEditorModule->FileExportFlattenedStage(TEXT("C:/Exports/Flattened.usda"));
    
    // 6. 关闭编辑器
    StageEditorModule->CloseStageEditor();
}
```

## Demo 示例

### 最小可行示例（编辑器工具按钮）

```cpp
// USDStageEditorTool.h
#pragma once

#include "CoreMinimal.h"
#include "Toolkits/AssetEditorManager.h"
#include "USDStageEditorModule.h"

class UUSDStageEditorTool : public UObject
{
    GENERATED_BODY()
    
public:
    UFUNCTION(BlueprintCallable, Category = "USD Tools")
    static void OpenUSDFileAndImport(const FString& UsdFilePath, const FString& ImportPath)
    {
        if (IUsdStageEditorModule* StageEditorModule = 
            FModuleManager::GetModulePtr<IUsdStageEditorModule>("USDStageEditor"))
        {
            // 打开编辑器
            StageEditorModule->OpenStageEditor();
            
            // 加载 USD 文件
            StageEditorModule->FileOpen(UsdFilePath);
            
            // 等待一段时间让编辑器加载（简化示例）
            FPlatformProcess::Sleep(0.5f);
            
            // 执行导入
            StageEditorModule->ActionsImport(ImportPath, nullptr);
            
            UE_LOG(LogTemp, Log, TEXT("USD file imported to: %s"), *ImportPath);
        }
    }
    
    UFUNCTION(BlueprintCallable, Category = "USD Tools")
    static void ExportSelectedPrimToNewFile(const FString& OutputPath)
    {
        if (IUsdStageEditorModule* StageEditorModule = 
            FModuleManager::GetModulePtr<IUsdStageEditorModule>("USDStageEditor"))
        {
            // 获取当前选中的图元
            TArray<FString> SelectedPrims = StageEditorModule->GetSelectedPrimPaths();
            
            if (SelectedPrims.Num() > 0)
            {
                // 只导出选中的图元（通过修改编辑器状态）
                // 注意：实际实现需要更复杂的逻辑
                StageEditorModule->FileExportFlattenedStage(OutputPath);
                
                UE_LOG(LogTemp, Log, TEXT("Exported %d prims to: %s"), 
                       SelectedPrims.Num(), *OutputPath);
            }
            else
            {
                UE_LOG(LogTemp, Warning, TEXT("No prims selected for export"));
            }
        }
    }
};
```

## 模块依赖

从模块分析来看，USDStageEditor 模块依赖以下核心组件：

| 模块 | 用途 |
|---|---|
| `USDStage` | USD 舞台核心逻辑和数据结构 |
| `USDSchemas` | USD Schema 类型系统支持 |
| `USDClassesEditor` | USD 相关的编辑器类定义 |
| `USDStageEditorViewModels` | 编辑器 UI 的数据模型层 |
| `Slate` / `SlateCore` | UI 框架基础 |
| `PropertyEditor` | 属性编辑器集成 |

**特殊依赖说明**：
- `USDStage` 模块提供核心的 USD 舞台管理功能，是编辑器操作的基础
- `USDSchemas` 处理 USD 的 Schema 类型系统，用于识别和操作不同类型的 USD 图元
- 编辑器特定的模块（`USDClassesEditor`, `USDStageEditorViewModels`）处理 UI 层的逻辑
- Slate 框架是 Unreal 编辑器 UI 的基础，提供树形视图、面板等组件

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量到单精度的截断警告 |
| 2026-04-29 | `bc4a1bd2` | USD: Add support for assigning BP-independent control rigs. | 支持分配独立于蓝图的 Control Rigs |
| 2026-04-28 | `4fb59a1d` | USD: Work around update to 26.03 causing AnimQuery internal references to be invalidated when LOD varies. | 解决 26.03 版本更新导致 LOD 变化时 AnimQuery 内部引用失效的问题 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32 位格式说明符在 64 位参数时的适配问题 |
| 2026-04-09 | `fb7af182` | USD: Bake all frames of exposure animation tracks. | 烘焙所有曝光动画轨道的帧 |

### 维护评价

**积极维护**：USD Importer 插件虽然创建于 2018 年（约 7 年前），但仍保持活跃开发。最近 6 个月内有多次实质性功能更新和 bug 修复，特别是对动画系统、Control Rig 集成和浮点精度问题的改进。

**实验性状态**：插件标记为实验性（`IsBetaVersion: true`），且默认未启用（`EnabledByDefault: false`），这意味着它可能包含不完整的 API 或存在已知限制。在生产环境中使用前需要进行充分测试。

**推荐使用**：尽管处于实验性状态，但考虑到 Epic Games 持续维护和更新，该插件是 UE5 中处理 USD 文件的官方解决方案。对于需要 USD 工作流的项目，特别是在游戏开发、虚拟制片和影视制作领域，推荐使用此插件。建议密切关注更新日志，及时获取新功能和稳定性改进。

**注意事项**：
1. 需要手动启用插件（在 Plugins 窗口中勾选）
2. 可能需要 USD SDK 依赖（`USE_USD_SDK` 宏定义）
3. 部分功能可能随引擎版本变化而调整

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter)
- [官方文档](https://docs.unrealengine.com)（UE5 USD 文档，链接待确认）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter/Source/USDTests)