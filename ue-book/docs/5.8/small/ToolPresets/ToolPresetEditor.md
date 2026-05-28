# Tool Presets

> Adds support for saving and loading tool settings as presets.

| 属性 | 值 |
|---|---|
| 中文名 | 工具预设 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（预设资产） |
| 模块 | `ToolPresetAsset` (Editor), `ToolPresetEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-01-20 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ToolPresets) | |

## 用途

该插件为 Unreal Engine 编辑器中的各类**可配置工具**（尤其是建模工具）提供了**预设管理系统**。它解决了一个常见的工作流痛点：艺术家和设计师经常需要重复配置相同的工具参数（例如雕刻笔刷强度、网格生成参数等）。此插件允许用户将当前工具的设置保存为一个命名的“预设”，并能在任何时候快速加载该预设，将参数应用回工具，从而极大提高了配置的复用性和工作效率。

从源码分析，其核心是创建了一种新的资产类型（`InteractiveToolsPresetCollectionAsset`），用于存储和组织这些预设，并通过编辑器 UI（管理面板）进行管理。

## 使用场景

-   **3D 建模工作流**：你在使用建模模式（Modeling Mode）下的各种工具（如挤出、切割、变形），并为不同的效果（如平滑雕刻、硬边创建）配置了特定的参数。你可以将这些参数保存为预设，在需要时快速切换。
-   **动画/绑定工具**：在使用骨骼编辑、权重绘制等工具时，针对不同角色或部位保存不同的笔刷和参数预设。
-   **任何需要重复配置的编辑器工具**：任何继承自工具框架（`UInteractiveTool`）并暴露可编辑属性的工具，理论上都可以利用此预设系统。

## 蓝图用法

**重要说明**：此插件主要是**编辑器工具和资产管理系统**，其核心功能通过编辑器 UI 和 C++ API 暴露。在公开的源码头文件中，**未发现任何标记为 `BlueprintCallable` 的函数**。因此，不能直接在蓝图图表中调用预设管理功能。预设的创建、选择和应用完全通过提供的编辑器面板完成。

## C++ 用法

### 头文件引入

```cpp
#include "IToolPresetEditorModule.h"
#include "ToolPresetSettings.h"
```

### 基本用法：访问编辑器模块与设置

该插件主要通过模块接口和项目设置来交互。

```cpp
// 来源: Public/IToolPresetEditorModule.h
// 1. 获取编辑器模块并打开预设管理器面板
IToolPresetEditorModule& PresetEditorModule = IToolPresetEditorModule::Get();
PresetEditorModule.ExecuteOpenPresetEditor();

// 来源: Public/ToolPresetSettings.h
// 2. 访问用户设置（存储在编辑器配置中）
UToolPresetUserSettings* UserSettings = UToolPresetUserSettings::Get();
if (UserSettings)
{
    // 检查默认集合是否启用
    bool bDefaultEnabled = UserSettings->bDefaultCollectionEnabled;
    // 获取用户启用的预设集合资产路径
    TSet<FSoftObjectPath>& EnabledCollections = UserSettings->EnabledPresetCollections;
}

// 3. 访问项目设置（在“项目设置 > 插件 > Interactive Tool Presets”中配置）
UToolPresetProjectSettings* ProjectSettings = GetMutableDefault<UToolPresetProjectSettings>();
if (ProjectSettings)
{
    // 获取项目级别加载的预设集合资产路径
    TSet<FSoftObjectPath>& ProjectCollections = ProjectSettings->LoadedPresetCollections;
}
```

## Demo 示例

以下示例演示了如何通过代码打开预设管理器面板，并读取基本设置。

**ToolPresetsDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "ToolPresetsDemo.generated.h"

UCLASS(BlueprintType)
class UToolPresetsDemo : public UObject
{
    GENERATED_BODY()
public:
    /** 在编辑器中打开工具预设管理器面板 */
    UFUNCTION(BlueprintCallable, Category = "ToolPresets Demo", meta = (DevelopmentOnly))
    static void OpenPresetManager();

    /** 打印当前预设项目设置中加载的集合数量 */
    UFUNCTION(BlueprintCallable, Category = "ToolPresets Demo", meta = (DevelopmentOnly))
    static void PrintProjectPresetCollectionCount();
};
```

**ToolPresetsDemo.cpp**
```cpp
#include "ToolPresetsDemo.h"
#include "IToolPresetEditorModule.h"
#include "ToolPresetSettings.h"

void UToolPresetsDemo::OpenPresetManager()
{
    if (IToolPresetEditorModule::IsAvailable())
    {
        IToolPresetEditorModule::Get().ExecuteOpenPresetEditor();
    }
}

void UToolPresetsDemo::PrintProjectPresetCollectionCount()
{
    const UToolPresetProjectSettings* ProjectSettings = GetDefault<UToolPresetProjectSettings>();
    if (ProjectSettings)
    {
        int32 Count = ProjectSettings->LoadedPresetCollections.Num();
        UE_LOG(LogTemp, Warning, TEXT("Number of preset collections loaded in project settings: %d"), Count);
    }
}
```

## 模块依赖

要使用此插件的功能，你的模块通常需要依赖 `ToolPresetEditor` 模块（用于访问管理器面板和设置类）。该模块本身依赖于 `ToolPresetAsset`（资产定义）和 `ModelingToolsEditorMode`（与建模模式集成）。

| 模块 | 用途 |
|---|---|
| `ToolPresetEditor` | 提供预设管理器编辑器面板、设置类和模块接口 |
| `ToolPresetAsset` | 定义预设集合资产 (`InteractiveToolsPresetCollectionAsset`) 的核心数据结构 |
| `ModelingToolsEditorMode` | 提供与建模模式工具集成的功能（是此插件的主要应用场景） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构了 JSON 对象，支持两种字符串类型，优化内存使用。 |
| 2026-04-14 | `c19c7e83` | [ContentBrowser] New Add Menu Misc Menu | 内容浏览器添加菜单新增杂项菜单项，可能影响预设资产创建入口。 |
| 2026-03-02 | `9758fa58` | FORT-984709 - Remove string duplication in FJsonObject to free memory | 移除 JSON 对象中的重复字符串，进一步释放内存。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复前一次提交中错误的查找替换问题。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退了代码提交 CL51314860 的更改。 |

### 维护评价

**综合评价：实验性，维护中但功能稳定。**

-   **创建时间**：创建于 2023 年初，相对年轻。
-   **更新频率**：最近一次更新在 2026 年 4 月，从提交记录看，近期有持续的维护活动，但**主要是底层优化（如内存、字符串处理）和与主引擎代码库同步的调整**，而非功能增强。
-   **活跃度**：仍在维护中，但作为实验性插件，功能迭代速度不快。
-   **已知限制**：1) 标记为实验性 (`IsExperimentalVersion=true`)，表明 Epic 可能认为其 API 或功能尚未完全稳定。2) 初始提交显示其设计与建模工具模式深度绑定，通用性可能有限。
-   **推荐使用**：**推荐**在以下场景使用：你需要为建模工具或类似可配置工具创建和管理预设，并且不介意使用实验性功能。该插件提供了一套完整的 UI 和资产管理方案，能有效提升工作流效率。但请注意其“实验性”标签，未来 API 可能发生变化。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ToolPresets)