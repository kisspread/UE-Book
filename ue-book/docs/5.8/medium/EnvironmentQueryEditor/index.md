# Environment Query Editor

> Allows editing of Environment Query assets, which are used by the AI to collect data about the environment/world

| 属性 | 值 |
|---|---|
| 中文名 | 环境查询编辑器 |
| 分类 | AI |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `EnvironmentQueryEditor` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2020-08-11 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/EnvironmentQueryEditor) | |

## 用途

Environment Query Editor 是 **环境查询系统 (EQS)** 的可视化编辑器工具。EQS 是 Unreal Engine 的 AI 核心系统之一，用于动态评估游戏世界中的环境信息，帮助 AI 角色做出决策（例如寻找掩体、选择攻击位置、评估威胁等级）。

此插件的作用是为 `UEnvQuery` 资产提供一个基于节点的图形化编辑界面，取代了纯代码或纯数据配置的方式，让 AI 设计师和程序员能够直观地创建、编辑和调试复杂的环境查询逻辑。它通过图表展示查询的生成器 (Generator)、测试 (Test) 和选项 (Option) 之间的连接关系，并提供性能分析器 (Profiler) 来监控查询的运行时性能。

**没有此插件，你将无法使用 UE 编辑器图形化地编辑 EQS 资产。**

## 使用场景

-   **AI 寻路与决策**：当你的 AI 角色需要动态评估周围环境来做出移动或战斗决策时，例如为 RTS 游戏中的单位寻找最佳防御位置，或为 FPS 游戏中的敌人寻找掩体。
-   **任务驱动型 AI**：当 AI 行为树 (Behavior Tree) 中的 EQS 查询节点需要复杂的、可视化的参数配置时。
-   **性能优化**：当需要分析特定 EQS 查询的运行性能和开销时，使用内置的性能分析器。

## 蓝图用法

此插件主要是一个**编辑器工具**，运行时功能由 `EnvironmentQuery` 模块提供。它本身不提供大量在运行时蓝图中可直接使用的节点。其核心价值在于创建和编辑 `UEnvQuery` 资产。

### 核心节点

在编辑器中，此插件扩展了资产创建和编辑功能，但没有提供新的、可在运行时蓝图中直接调用的 `BlueprintCallable` 函数。

### 使用示例（蓝图描述）

1.  **创建资产**：在内容浏览器 (Content Browser) 中，右键点击，选择 “Artificial Intelligence” -> “Environment Query”，即可创建一个新的 EQS 资产。
2.  **编辑资产**：双击新创建的 EQS 资产，将打开 Environment Query Editor 窗口。
3.  **构建查询**：在编辑器中，从右键菜单或拖拽操作中添加 “Generator”（如 “Points: Grid”）、“Test”（如 “Trace”、“Distance”）和 “Option” 节点，并用连线将它们连接起来，形成查询逻辑图。
4.  **调试与分析**：使用编辑器工具栏上的 “Profiler” 面板来查看查询在不同游戏场景下的性能数据（如最差时间、平均负载）。

## C++ 用法

### 头文件引入

```cpp
#include "EnvironmentQueryEditorModule.h"
```

### 基本用法

此模块主要用于注册编辑器和自定义细节面板 (Detail Customization)，通常不直接在游戏逻辑的 C++ 代码中调用。其核心接口如下：
（来源: `Source/EnvironmentQueryEditor/Public/EnvironmentQueryEditorModule.h`）

```cpp
// 获取模块单例
FEnvironmentQueryEditorModule& EnvironmentQueryEditorModule = FModuleManager::GetModuleChecked<FEnvironmentQueryEditorModule>(TEXT("EnvironmentQueryEditor"));

// 创建并打开一个 EQS 编辑器实例
UEnvQuery* MyQueryAsset = /* ... 获取或加载一个 UEnvQuery 资产 ... */;
TSharedRef<IEnvironmentQueryEditor> Editor = EnvironmentQueryEditorModule.CreateEnvironmentQueryEditor(
    EToolkitMode::Standalone,
    nullptr,
    MyQueryAsset
);

// 获取编辑器图表节点的类型缓存（通常由插件内部使用）
TSharedPtr<FGraphNodeClassHelper> ClassCache = EnvironmentQueryEditorModule.GetClassCache();
```

### 进阶用法

可以通过模块提供的扩展点，为 EQS 编辑器添加自定义菜单或工具栏按钮：
（来源: `Source/EnvironmentQueryEditor/Public/EnvironmentQueryEditorModule.h`）

```cpp
// 获取菜单扩展管理器
TSharedPtr<FExtensibilityManager> MenuManager = EnvironmentQueryEditorModule.GetMenuExtensibilityManager();
if (MenuManager.IsValid())
{
    // 使用 MenuManager->AddExtender(...) 来添加自定义的菜单项
}

// 获取工具栏扩展管理器
TSharedPtr<FExtensibilityManager> ToolbarManager = EnvironmentQueryEditorModule.GetToolBarExtensibilityManager();
if (ToolbarManager.IsValid())
{
    // 使用 ToolbarManager->AddExtender(...) 来添加自定义的工具栏按钮
}
```

## Demo 示例

此插件为编辑器专用 (UncookedOnly)，其功能主要通过 UE 编辑器的图形界面体现，不适用于创建包含 .h + .cpp 的独立运行时示例。核心用法是作为用户在编辑器中使用的一项工具。

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-13 | `f10a2daf` | [ContentBrowser] New Add Menu AI Menu | 为内容浏览器的“添加”菜单新增了AI分类，可能影响EQS资产的创建入口。 |
| 2025-12-17 | `8a277ed0` | Removing `SNodePanel`'s unused attributes | 清理了图表节点面板的未使用属性，代码优化。 |
| 2025-07-10 | `9803c443` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files... | 为源码添加了内联生成的宏，是引擎的通用代码优化。 |
| 2025-04-07 | `1eb82647` | Fix various LOCTEXT issues. | 修复了多个本地化文本（LOCTEXT）相关的错误。 |
| 2025-03-31 | `515ec7cd` | [Truncation Warnings] Update SNodePanel, SGraphPanel and dependent classes to use FVector2f... | 更新图表面板以使用FVector2f，解决截断警告。 |

### 维护评价

该插件创建于 2020 年 8 月（UE5 早期开发阶段），已稳定运行约 5 年。最近的更新（截至 2026 年）主要集中在与 UE 核心引擎协同的底层优化（如 FVector2f 迁移、本地化修复）和内容浏览器集成改进，而非 EQS 编辑器本身的功能性新增。

它作为 UE 内置 AI 系统（EQS）的官方编辑器，是成熟且稳定的组件，**目前处于稳定维护状态**。虽然没有频繁的新功能添加，但持续的维护确保了其与最新引擎版本的兼容性。推荐所有使用 EQS 的项目依赖此插件。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/EnvironmentQueryEditor)
-   [官方文档](https://docs.unrealengine.com/5.8/en-US/environment-query-system-in-unreal-engine/) (通用 EQS 文档，编辑器用法包含其中)