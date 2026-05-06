# USD Importer

> Adds support for importing the USD file format into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | USD 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器UI、测试资源） |
| 模块 | `GeometryCacheUSD` (Runtime), `USDClassesEditor` (Runtime), `USDExporter` (Runtime), `USDSchemas` (Runtime), `USDStage` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDStageImporter` (Runtime), `USDTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-10-01 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Importers/USDImporter) | |

## 用途

USD Importer 插件为 Unreal Engine 提供了对 Pixar USD（通用场景描述）文件格式的完整支持。它不仅是一个导入器，更是一个完整的 USD 工作流集成工具，包含：

- **USD 舞台编辑器**：在 UE 编辑器中直接打开、浏览、编辑 USD 文件（含层级、图层、变体、引用等）。
- **实时同步**：USD 舞台与 UE 视口双向同步，支持选择同步、属性修改同步。
- **导出与烘焙**：可将 UE 关卡内容导出为 USD，或将 USD 舞台扁平化导出为单个 USD 文件。
- **蓝图交互**：通过蓝图 API 控制舞台打开/关闭、选择、导入等操作，便于自动化工作流。

该插件解决了在 UE 中直接处理 USD 资产的需求，适用于 VFX、动画、建筑可视化等需要跨软件交换场景数据的流程。

## 使用场景

- **VFX/动画管线**：从 Houdini、Maya、Blender 导出 USD 文件，在 UE 中预览、调整材质、烘焙后渲染。
- **大型场景协作**：使用 USD 的图层和引用机制管理多用户协作的场景，在 UE 中通过舞台编辑器查看、修改、提交图层。
- **自动化导入流程**：通过蓝图的 `SetSelectedPrimPaths()`、`FileOpen()` 等接口编写剧本，批量处理 USD 文件。
- **开发与调试 USD 资产**：利用舞台编辑器查看 prim 属性、变体、引用，快速定位资产问题。
- **导出 UE 场景为 USD**：将关卡中的静态网格体、骨架网格体、动画等导出为 USD，供其他软件使用。

## 蓝图用法

基于 `USDStageEditorBlueprintLibrary` 类（已标记 `BlueprintCallable` 并暴露到蓝图）。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open Stage Editor` | 打开 USD 舞台编辑器窗口（若已打开则聚焦） | `UUsdStageEditorBlueprintLibrary` |
| `Close Stage Editor` | 关闭 USD 舞台编辑器窗口 | `UUsdStageEditorBlueprintLibrary` |
| `Get Attached Stage Actor` | 获取当前舞台编辑器绑定的舞台 Actor | `UUsdStageEditorBlueprintLibrary` |
| `Set Attached Stage Actor` | 设置舞台编辑器绑定的舞台 Actor | `UUsdStageEditorBlueprintLibrary` |
| `Get Selected Layer Identifiers` | 获取当前选中的图层标识符数组 | `UUsdStageEditorBlueprintLibrary` |
| `Set Selected Layer Identifiers` | 设置当前选中的图层 | `UUsdStageEditorBlueprintLibrary` |
| `Get Selected Prim Paths` | 获取当前选中的 prim 路径数组 | `UUsdStageEditorBlueprintLibrary` |
| `Set Selected Prim Paths` | 设置当前选中的 prim | `UUsdStageEditorBlueprintLibrary` |
| `Get Selected Property Names` | 获取当前选中的属性名称数组 | `UUsdStageEditorBlueprintLibrary` |
| `Set Selected Property Names` | 设置当前选中的属性 | `UUsdStageEditorBlueprintLibrary` |

### 使用示例（蓝图描述）

1. **打开舞台并导入所有选中 prim**：  
   - 调用 `Open Stage Editor`。  
   - 调用 `File Open`（需要 C++ 或通过 `IUsdStageEditorModule` 调用，蓝图暂未暴露该函数，但可通过自定义 C++ 封装）。  
   - 等待用户选择 prim 后，调用 `Get Selected Prim Paths` 获取选中路径数组。  
   - 循环调用 `Actions Import`（蓝图暂未暴露，需通过 C++ 模块）或使用其他导入节点。

2. **同步选择**：  
   - 在视口选择一个 Actor 后，通过 `Set Selected Prim Paths` 同步更新舞台编辑器的 prim 选择。  
   - 反之，当舞台编辑器 prim 选择变化时，通过 `OnPrimSelectionChanged` 事件（需 C++ 绑定）更新视口。  
   - 《USD Stage Editor 设置》中的 `bSelectionSynced` 控制是否自动同步。

## C++ 用法

### 头文件引入

```cpp
#include "USDStageEditorModule.h"
#include "USDStageEditorBlueprintLibrary.h"
```

### 基本用法

从 `USDStageEditorBlueprintLibrary.h` 提取，静态函数可直接调用。

```cpp
// 获取当前绑定的舞台 Actor
AUsdStageActor* Actor = UUsdStageEditorBlueprintLibrary::GetAttachedStageActor();

// 设置新的舞台 Actor
UUsdStageEditorBlueprintLibrary::SetAttachedStageActor(NewActor);

// 获取选中的 prim 路径
TArray<FString> SelectedPrims = UUsdStageEditorBlueprintLibrary::GetSelectedPrimPaths();

// 设置 prim 选择
TArray<FString> NewSelection = { TEXT("/Root") };
UUsdStageEditorBlueprintLibrary::SetSelectedPrimPaths(NewSelection);
```

来源文件：`Engine/Plugins/Importers/USDImporter/Source/USDStageEditor/Public/USDStageEditorBlueprintLibrary.h`

### 进阶用法

通过 `IUsdStageEditorModule` 接口进行更完整的控制（如文件操作、导出等）。

```cpp
// 获取模块实例
IUsdStageEditorModule& Module = FModuleManager::LoadModuleChecked<IUsdStageEditorModule>("USDStageEditor");

// 打开舞台（弹出文件选择对话框）
Module.FileOpen();

// 打开指定路径的舞台
Module.FileOpen(TEXT("C:/MyScene.usda"));

// 保存舞台（若文件未保存则弹出对话框）
Module.FileSave();

// 导出所有图层到目录
Module.FileExportAllLayers(TEXT("C:/ExportDir"));

// 导出扁平化舞台
Module.FileExportFlattenedStage(TEXT("C:/Exported.usda"));

// 导出选中的图层
Module.ExportSelectedLayers(TEXT("C:/ExportDir"));
```

来源文件：`Engine/Plugins/Importers/USDImporter/Source/USDStageEditor/Public/USDStageEditorModule.h`

## Demo 示例

一个最小 C++ 示例，展示如何在编辑器中自动打开 USD 文件并导出扁平化结果。

**MyUSDDemo.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FMyUSDDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    void OnEditorReady();
};
```

**MyUSDDemo.cpp**

```cpp
#include "MyUSDDemo.h"
#include "USDStageEditorModule.h"
#include "UsdWrappers/UsdStage.h"

IMPLEMENT_MODULE(FMyUSDDemoModule, MyUSDDemo)

void FMyUSDDemoModule::StartupModule()
{
    // 延迟到编辑器完全启动后执行
    if (GEditor)
    {
        FTSTicker::GetCoreTicker().AddTicker(
            FTickerDelegate::CreateLambda([this](float DeltaTime) -> bool
            {
                OnEditorReady();
                return false;
            }),
            0.5f
        );
    }
}

void FMyUSDDemoModule::OnEditorReady()
{
    IUsdStageEditorModule& StageEditorModule = FModuleManager::LoadModuleChecked<IUsdStageEditorModule>("USDStageEditor");

    // 打开 USD 文件
    const FString FilePath = TEXT("C:/Demo/MyStage.usda");
    StageEditorModule.FileOpen(FilePath);

    // 等待舞台加载（简单演示，实际应监听 Stage 事件）
    FPlatformProcess::Sleep(0.5f);

    // 导出扁平化舞台
    StageEditorModule.FileExportFlattenedStage(TEXT("C:/Demo/Flattened.usda"));

    // 关闭舞台
    StageEditorModule.FileClose();
}

void FMyUSDDemoModule::ShutdownModule()
{
}
```

> 注意：此示例假设 USD Stage Actor 存在且舞台已加载。生产代码需要处理异步加载和错误检测。

## 模块依赖

从 `USDStageEditor.Build.cs` 以及其他模块的依赖（基于常见 USD 插件依赖推断）整理。

仅列出非标准依赖：

| 模块 | 用途 |
|---|---|
| `UnrealUSDWrapper` | USD C++ API 封装层，提供 UE 与 USD SDK 的绑定 |
| `PythonScriptPlugin` | 可选，支持 Python 脚本控制 USD 操作 |
| `Sequencer` | 与 USD 时间轴集成（如动画导出） |
| `AssetRegistry` | 管理 USD 导入后的资产 |
| `MaterialEditor` | 编辑 USD 材质时使用 |

其他常见依赖（如 Core、Engine、Slate 等）省略。

## 维护状态

### 近期更新

- 2025-10-22 `a1039b21` USD: Disabled UE allocator in USD for Windows.（禁用 Windows 下 USD 的 UE 分配器）
- 2025-10-17 `be609b71` [Backout] - CL47041219（回退某次变更）
- 2025-10-17 `7ab79237` USD: Disabled UE allocator in USD for Windows.（同上，重复提交）
- 2025-10-03 `d887bd60` USD: Use the default collision profile for generated static meshes.（使用默认碰撞配置）
- 2025-10-01 `b4449c58` Anim In Engine: Fix broken linked anim sequences.（修复动画序列链接）

### 维护评价

- **创建时间**：2025-10-01，距今约 0 年，非常新的插件。
- **近期更新**：最近一个月内有 5 次 commit，包含功能更新和修复，维护活跃。
- **状态**：标记为 Beta 版本，但已在核心管线中使用；推荐用于 UE 5.7+ 开发。
- **已知限制**：IsBetaVersion = true，可能存在未发现的 Bug；Windows 下 USD 分配器禁用可能有性能影响。
- **推荐使用**：是，适合需要直接处理 USD 文件的工作流。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Importers/USDImporter)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Importers/USDImporter/Source/USDTests)