# Flow Production Tracking

> Flow Production Tracking (formerly known as Shotgun and/or ShotGrid) integration for the Unreal Editor.

| 属性 | 值 |
|---|---|
| 中文名 | 流水线制作跟踪 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `Shotgrid` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-01-18 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Shotgrid) | |

## 用途

该插件旨在将 Unreal Editor 与 Flow Production Tracking（原 Shotgun/ShotGrid）深度集成，解决影视、动画及游戏制作管线中资产管理与任务跟踪的集成问题。它通过 Python 脚本层提供了一个桥梁，使得 Unreal 编辑器能够读取并执行来自 Flow Production Tracking 系统的上下文命令和操作，从而将编辑器的工作流与外部项目管理系统打通。其核心价值在于让制作团队能够直接在 Unreal 编辑器内进行资产跟踪、任务管理和团队协作。

## 使用场景

- 你是一个大型影视或游戏制作团队的技术美术或管线 TD → 你需要将 Unreal 中的资产与 Flow Production Tracking 中的任务、版本和依赖关系关联起来。
- 你的项目使用 Flow Production Tracking 进行项目管理，需要在 Unreal 编辑器内直接查看资产状态、更新任务或触发发布流程。
- 你需要自定义 Unreal 编辑器菜单，将 Flow Production Tracking 的操作（如“提交评审”、“创建新版本”）作为编辑器命令暴露给美术人员。

## 蓝图用法

### 核心节点

插件的核心逻辑封装在 `UShotgridEngine` 类中，它通过蓝图可实现的事件与 Python 脚本交互。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetInstance` | 获取 Python Shotgrid 引擎的单例实例。 | `UShotgridEngine` |
| `OnEngineInitialized` | 当 Python Shotgrid 引擎完成初始化后调用的回调。 | `UShotgridEngine` |
| `GetShotgridMenuItems` | 获取 Python 引擎提供的可用 Shotgrid 菜单项列表（蓝图可实现事件）。 | `UShotgridEngine` |
| `ExecuteCommand` | 通过名称在 Python 引擎中执行一个 Shotgrid 命令（蓝图可实现事件）。 | `UShotgridEngine` |
| `Shutdown` | 关闭 Python Shotgrid 引擎（蓝图可实现事件）。 | `UShotgridEngine` |
| `GetReferencedAssets` | 获取给定 Actor 所引用的资产列表。 | `UShotgridEngine` |
| `GetShotgridWorkDir` | 获取 Shotgrid 工作区的根目录路径。 | `UShotgridEngine` |
| `GetSelectedActors` | 获取当前选中的 Actor 列表（用于确定上下文）。 | `UShotgridEngine` |

### 使用示例（蓝图描述）

1.  **初始化引擎**：在编辑器的合适时机（如编辑器启动后），调用 `UShotgridEngine::GetInstance` 获取引擎实例，然后连接 `OnEngineInitialized` 事件来确认引擎就绪。
2.  **获取菜单项**：实现 `GetShotgridMenuItems` 事件，从 Python 脚本返回一组 `FShotgridMenuItem` 结构体，每个代表一个菜单命令。
3.  **执行命令**：为每个菜单项创建 UI（例如，一个按钮），当用户点击时，调用 `ExecuteCommand` 并传入对应的 `CommandName`。
4.  **设置上下文**：在调用命令前，可以设置 `SelectedAssets` 属性，或使用 `SetSelection` 方法，将当前编辑器中选中的资产或 Actor 信息传递给引擎，以便命令能基于正确的上下文执行。

## C++ 用法

### 头文件引入

```cpp
#include "IShotgridModule.h"
```

### 基本用法

通过模块接口访问 `UShotgridEngine` 的实例。`UShotgridEngine` 本身是 `UObject`，其核心功能通过蓝图可实现事件委托给 Python。

```cpp
// 检查模块是否可用
if (IShotgridModule::IsAvailable())
{
    // 获取模块引用 (虽然模块提供了 Get()，但通常直接使用 UShotgridEngine 的静态方法)
    // IShotgridModule& Module = IShotgridModule::Get();

    // 获取 Shotgrid 引擎单例
    UShotgridEngine* ShotgridEngine = UShotgridEngine::GetInstance();
    if (ShotgridEngine)
    {
        // 获取工作目录
        FString WorkDir = UShotgridEngine::GetShotgridWorkDir();
        UE_LOG(LogTemp, Log, TEXT("Shotgrid Work Dir: %s"), *WorkDir);

        // 获取当前选中的资产 (需要在有编辑器上下文的情况下)
        const TArray<FAssetData>& Assets = ShotgridEngine->SelectedAssets;
        // ... 处理资产信息
    }
}
```

*（来源: `IShotgridModule.h` 和 `ShotgridEngine.h`）*

### 进阶用法

扩展 `UShotgridEngine` 以添加自定义的 C++ 行为。由于它是 `UCLASS(Blueprintable)`，你可以创建子类。

```cpp
// MyShotgridEngine.h
#include "ShotgridEngine.h" // 确保包含原始头文件
#include "MyShotgridEngine.generated.h"

UCLASS()
class UMyShotgridEngine : public UShotgridEngine
{
    GENERATED_BODY()
public:
    // 重写或添加自定义方法
    UFUNCTION(BlueprintCallable, Category = "Custom Shotgrid")
    void MyCustomWorkflow();
};

// MyShotgridEngine.cpp
#include "MyShotgridEngine.h"

void UMyShotgridEngine::MyCustomWorkflow()
{
    // 实现自定义逻辑，可能调用父类功能或与 Python 交互
    TArray<FShotgridMenuItem> MenuItems = GetShotgridMenuItems();
    // ... 逻辑处理
    UE_LOG(LogTemp, Log, TEXT("Custom Shotgrid workflow executed with %d menu items."), MenuItems.Num());
}
```
*注意：这种扩展方式依赖于插件的具体实现细节和初始化流程。*

## Demo 示例

一个最小的、用于展示如何访问 `UShotgridEngine` 并监听其初始化的基本示例。

```cpp
// MyEditorModule.h
#pragma once
#include "Modules/ModuleManager.h"

class FMyEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    void OnShotgridEngineInitialized();
};
```

```cpp
// MyEditorModule.cpp
#include "MyEditorModule.h"
#include "ShotgridEngine.h" // 包含插件的头文件

#define LOCTEXT_NAMESPACE "FMyEditorModule"

void FMyEditorModule::StartupModule()
{
    // 尝试获取引擎实例
    UShotgridEngine* Engine = UShotgridEngine::GetInstance();
    if (Engine)
    {
        // 在蓝图或更复杂的 C++ 中，你可能会绑定到 OnEngineInitialized 事件。
        // 这里我们简单地在启动时检查并调用。
        Engine->OnEngineInitialized();
        UE_LOG(LogTemp, Log, TEXT("Shotgrid Engine initialized and available."));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Failed to get Shotgrid Engine instance."));
    }
}

void FMyEditorModule::ShutdownModule()
{
    // 通常在模块关闭时，需要调用引擎的 Shutdown。
    UShotgridEngine* Engine = UShotgridEngine::GetInstance();
    if (Engine)
    {
        // 注意：Shutdown 是 BlueprintImplementableEvent，在 C++ 中直接调用可能有限制，通常由蓝图或 Python 驱动。
        // Engine->Shutdown();
    }
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyEditorModule, MyEditorModule)
```

## 模块依赖

该插件本身依赖特定的模块，使用该插件时，你的模块也可能需要间接依赖这些。

| 模块 | 用途 |
|---|---|
| `PythonScriptPlugin` | **核心依赖**。插件通过此模块在编辑器内嵌入 Python 解释器，执行与 Flow Production Tracking 交互的脚本。 |
| `EditorScriptingUtilities` | 提供编辑器脚本工具函数，可能用于增强插件的编辑器内操作能力。 |
| `Shotgrid` (本插件) | 如果你要从 C++ 代码直接访问插件提供的接口（如 `IShotgridModule`, `UShotgridEngine`），你的模块需要添加对 `Shotgrid` 模块的依赖。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移至 UE_LOGF，统一日志宏用法。 |
| 2024-08-27 | `32811c8a` | Rename shotgrid to Flow Production Tracking. Fix startup issue with Flow trying to run before python | 完成从 ShotGrid 到 Flow Production Tracking 的重命名，并修复 Python 引擎启动时序问题。 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | (提交信息不完整) 可能是常规维护或子模块更新。 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新内置插件的供应商链接为安全协议（HTTPS）。 |
| 2022-09-18 | `de37b387` | FName -> FSoftObjectPath refactoring. | 进行 FName 到 FSoftObjectPath 的重构，影响资产引用方式。 |

### 维护评价

该插件处于**实验性阶段 (IsBetaVersion=true)** 且**默认禁用**，表明其 API 和行为可能会发生改变。从创建时间（约 4 年）看属于较新的插件。

**活跃程度**：最近一次实质性功能性更新在 2024 年 8 月（重命名与 Bug 修复），距离现在约 2 年。2026 年的更新属于引擎层面的日志宏迁移，不涉及插件功能本身。因此，该插件的**功能更新不活跃**，但仍在跟随引擎主版本进行基础维护。

**推荐使用建议**：
1.  **谨慎使用**：由于其“实验性”状态，不建议在关键生产管线中作为核心依赖。
2.  **关注替代方案**：此插件的官方名称已变更为“Flow Production Tracking”，Epic 可能提供了更新的官方集成方案或文档，使用前应确认是否有更成熟的选择。
3.  **依赖 Python**：该插件的实现强依赖于 Python，使用时需要确保目标平台和构建配置支持 `PythonScriptPlugin`。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Shotgrid)
- 官方文档 (无，`.uplugin` 的 `DocsURL` 为空)