# Editor Toolset

> Toolsets for interacting with the Unreal Editor and core types (Blueprints, Actors, Properties, etc.) via the AI Toolset Registry.

| 属性 | 值 |
|---|---|
| 中文名 | 编辑器工具集 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `EditorToolset` (Editor) |
| 实验性 | ⚦ 是 |
| 创建时间 | 2026-05-13 |
| 年龄标签 | 🆕（约 -1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/EditorToolset) | |

## 用途

EditorToolset 是一个**面向 AI 代理的实验性编辑器扩展插件**。它通过 AI Toolset Registry，将 Unreal Editor 的丰富功能封装成标准化的“工具集”(Toolset)，使 AI 模型能够以结构化的方式感知和操控编辑器环境。

该插件的核心功能分为两部分：
1.  **编辑器交互 (`UEditorAppToolset`)**：为 AI 提供“眼睛”和“手”，使其能够查看编辑器界面、捕获带有空间标注的视口截图、控制播放会话、查询和修改 Actor 与资产选择、导航内容浏览器等。
2.  **运行时监控 (`ULogsToolset`)**：为 AI 提供“耳朵”，使其能够读取引擎日志、筛选日志条目，并动态调整日志详细程度，便于 AI 在运行时进行调试和状态监控。

本质上，它是构建能够自主编辑关卡、运行测试和分析场景的 AI 助手的**底层基础设施**。

## 使用场景

-   你正在开发一个 **AI 关卡设计助手** → 使用 `CaptureViewport` 获取带网格和标签的场景截图，让 AI 理解空间布局，然后使用 `SelectActors`、`SetCameraTransform` 等节点指导 AI 进行资产放置。
-   你需要一个 **AI 自动化测试代理** → 使用 `StartPIE` 和 `StopPIE` 驱动 Play-In-Editor 会话，用 `IsPIERunning` 检查状态，用 `GetLogEntries` 监控运行时错误。
-   你正在创建 **智能资产检查工具** → 使用 `CaptureAssetImage` 为资产生成缩略图，`GetSelectedAssets` 读取选择，`OpenEditorForAsset` 打开资产编辑器，实现资产的自动审查和标注。
-   你需要 **动态调试和监控** → 使用 `ULogsToolset` 的 `GetLogEntries` 和 `SetVerbosity`，让 AI 能够实时查看特定类别的日志，并按需提高关键日志的详细程度。

## 蓝图用法

该插件的函数主要通过 `meta = (AICallable)` 标记，专为 AI 工具调用设计，但同样可以被蓝图调用。其节点可分为以下几类：

### 核心节点

**编辑器视图与空间感知**
| 节点 | 说明 | 所在类 |
|---|---|---|
| `CaptureViewport` | 捕获当前关卡视口的截图及元数据（相机、网格、Actor标签），为空间感知提供数据。 | `UEditorAppToolset` |
| `CaptureEditorImage` | 捕获整个编辑器应用程序窗口的截图。 | `UEditorAppToolset` |
| `CaptureAssetImage` | 为指定资产（网格体、材质等）生成缩略图。 | `UEditorAppToolset` |
| `GetVisibleActors` | 获取视锥体内的所有 Actor。 | `UEditorAppToolset` |
| `WorldPosToScreenCoords` | 将世界坐标转换为归一化的屏幕坐标。 | `UEditorAppToolset` |
| `ScreenCoordsToWorld` | 从屏幕坐标发射射线，返回命中点的世界坐标。 | `UEditorAppToolset` |

**Actor 与资产选择**
| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetSelectedActors` | 获取当前在关卡编辑器中选中的 Actor 列表。 | `UEditorAppToolset` |
| `SelectActors` | 选中指定的 Actor。 | `UEditorAppToolset` |
| `FocusOnActors` | 将编辑器相机对准指定的 Actor。 | `UEditorAppToolset` |
| `GetSelectedAssets` | 获取内容浏览器中当前选中的资产路径列表。 | `UEditorAppToolset` |
| `SelectAssets` | 在内容浏览器中选中指定路径的资产。 | `UEditorAppToolset` |

**Play-In-Editor 控制**
| 节点 | 说明 | 所在类 |
|---|---|---|
| `StartPIE` | 启动一个 PIE 或 Simulate 会话，支持自定义启动点、播放模式和预热时间。 | `UEditorAppToolset` |
| `StopPIE` | 停止当前运行的播放会话。 | `UEditorAppToolset` |
| `IsPIERunning` | 检查当前是否有 PIE 会话正在运行。 | `UEditorAppToolset` |

**日志监控**
| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetLogEntries` | 读取当前会话的日志，支持按类别和正则表达式筛选。 | `ULogsToolset` |
| `GetLogCategories` | 获取所有已注册的日志类别名称。 | `ULogsToolset` |
| `GetVerbosity` | 查询指定日志类别的当前详细级别。 | `ULogsToolset` |
| `SetVerbosity` | 设置指定日志类别的详细级别。 | `ULogsToolset` |

### 使用示例（蓝图描述）

**示例 1：获取带标注的视口截图**
1.  创建一个 `FViewportAnnotationConfig` 结构体，设置网格间距 (`GridSpacing`)、网格范围 (`GridExtent`) 等参数。
2.  调用 `CaptureViewport` 节点，将上述配置传入 `Annotations` 引脚。
3.  从输出的 `FViewportCapture` 结构体中，获取 `Image`（截图）、`CameraLocation`（相机位置）和 `LabeledActors`（带标签的Actor列表）信息。

**示例 2：自动运行并监控一个 PIE 会话**
1.  调用 `StartPIE` 节点，创建一个 `FPIESessionOptions` 结构体，设置 `bSimulate = false`（标准PIE）和 `WarmupSeconds = 3.0`。
2.  将 `StartPIE` 的返回值（一个异步对象）连接到 `Make Literal Async Value` 节点，再连接到 `Wait for Async Value` 节点，以等待 PIE 启动完成。
3.  使用 `GetLogEntries` 节点，设置 `Category = “LogTemp”`，监视特定类别的日志。
4.  完成后，调用 `StopPIE` 并同样等待其完成。

## C++ 用法

### 头文件引入

```cpp
#include "EditorAppToolset.h"
#include "LogsToolset.h"
```

### 基本用法

从头文件声明可以看出，所有工具函数均为静态函数，可直接通过类名调用。主要分为 `UEditorAppToolset` 和 `ULogsToolset` 两大类。

```cpp
// 来源：Source/EditorToolset/Private/EditorAppToolset.h

// 1. 获取当前选中的 Actor
TArray<AActor*> SelectedActors = UEditorAppToolset::GetSelectedActors();

// 2. 获取编辑器视口相机的 Transform
FTransform CameraTransform = UEditorAppToolset::GetCameraTransform();

// 3. 查询名为 “LogTemp” 的日志类别当前的详细程度
FString CurrentVerbosity = ULogsToolset::GetVerbosity(TEXT("LogTemp"));

// 4. 读取最近 500 条包含 “Error” 关键字的日志
TArray<FString> ErrorLogs = ULogsToolset::GetLogEntries(TEXT(""), TEXT("Error"), 500);
```

### 进阶用法

捕获带标注的视口截图需要配置多个参数。以下代码片段展示了如何设置一个简单的网格覆盖和 Actor 标签。

```cpp
// 来源：基于 Source/EditorToolset/Private/EditorAppToolset.h 和 BitmapAnnotation.h 推断

// 配置注释覆盖
FViewportAnnotationConfig AnnotationConfig;
AnnotationConfig.GridSpacing = 1000.f; // 网格间距 10 米
AnnotationConfig.GridExtent = 5000.f;  // 网格范围 50 米
AnnotationConfig.MaxLabelDistance = 3000.f; // 最大标签距离 30 米
AnnotationConfig.MaxLabels = 8;        // 最多显示 8 个 Actor 标签

// 从当前视口捕获
FViewportCapture Capture = UEditorAppToolset::CaptureViewport(
    TOptional<FTransform>(),          // 使用当前视口相机
    TOptional<FViewportAnnotationConfig>(AnnotationConfig),
    false                             // 隐藏编辑器 UI
);

// 检查捕获结果
if (!Capture.Image.IsEmpty())
{
    // 成功获取带有网格和 Actor 标签的截图
    // Capture.LabeledActors 包含了截图中可见的、带有标签的 Actor 信息
    // 可以将 Capture.Image 传递给 AI 视觉模型进行分析
}
```

## Demo 示例

以下示例展示了如何编写一个简单的工具函数，用于启动 PIE 会话、等待其运行，然后从日志中筛选错误信息。

```cpp
// MyDemoTool.h
#pragma once

#include "CoreMinimal.h"
#include "UObject/ObjectMacros.h"

class FMyDemoTool
{
public:
    static void RunDemo();
};
```

```cpp
// MyDemoTool.cpp
#include "MyDemoTool.h"
#include "EditorAppToolset.h"
#include "LogsToolset.h"

void FMyDemoTool::RunDemo()
{
    // 1. 配置并启动 PIE 会话
    FPIESessionOptions PIEOptions;
    PIEOptions.bSimulate = false; // 标准 PIE
    PIEOptions.WarmupSeconds = 2.0f;

    UE_LOG(LogTemp, Log, TEXT("启动 PIE 会话..."));
    // 注意：StartPIE 是异步的，此处为简化演示，实际项目中应使用异步回调或 Wait 节点
    UToolCallAsyncResultVoid* StartResult = UEditorAppToolset::StartPIE(PIEOptions);

    // 2. 等待 PIE 启动完成（简化处理）
    // 在实际异步逻辑中，应等待 StartResult 完成。

    // 3. 检查 PIE 状态并获取日志
    if (UEditorAppToolset::IsPIERunning())
    {
        UE_LOG(LogTemp, Log, TEXT("PIE 会话已运行。"));
        TArray<FString> AllLogs = ULogsToolset::GetLogEntries();
        TArray<FString> ErrorLogs;
        for (const FString& LogLine : AllLogs)
        {
            if (LogLine.Contains(TEXT("Error")))
            {
                ErrorLogs.Add(LogLine);
            }
        }
        UE_LOG(LogTemp, Log, TEXT("捕获到 %d 条错误日志。"), ErrorLogs.Num());

        // 4. 停止 PIE
        UToolCallAsyncResultVoid* StopResult = UEditorAppToolset::StopPIE();
        // 同样，这里也应等待 StopResult 完成。
    }
}
```

## 模块依赖

该插件的模块依赖未在提供的信息中明确列出，但从其功能和 `.uplugin` 中的 `Plugins` 字段可知，它**强依赖于 ToolsetRegistry 插件**。因此，使用此插件的项目需要确保 ToolsetRegistry 可用。

| 模块 | 用途 |
|---|---|
| `ToolsetRegistry` | AI 工具集注册表，提供工具定义和异步任务调用的基础框架。EditorToolset 将其工具注册到此系统中。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `69dab60d` | Move core toolsets, tests, and skills from ToolsetRegistry into EditorToolset. Also remove a few unn... | 将核心工具集、测试和技能从 ToolsetRegistry 迁移至本插件，并进行一些清理。 |
| 2026-05-13 | `c7baaf9c` | Migrated EditorApp and Logs toolsets from ToolsetRegistry to new EditorToolset plugin. | 从 ToolsetRegistry 迁移编辑器和日志工具集，创建本插件。 |

### 维护评价

-   **状态**：**活跃维护中**。该插件在**创建后一天**就收到了重要的功能迁移提交 (`69dab60d`)，表明其处于积极开发和完善的初期阶段。
-   **特点**：这是一个**实验性** (`IsExperimentalVersion: true`) 插件，且默认未启用 (`Installed: false`)。这意味着它功能尚不稳定，API 可能在未来版本中发生变化，需要手动启用才能使用。
-   **风险**：由于是实验性新插件，生态系统支持有限，可能依赖未广泛使用的 ToolsetRegistry 系统。在正式项目中采用需谨慎。
-   **推荐**：对于正在探索 **AI 辅助编辑器工作流** 或 **高级自动化测试** 的项目，这是一个值得关注的前沿工具。它提供了非常底层的编辑器交互能力。但对于常规游戏开发，目前无需关注。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/EditorToolset)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/EditorToolset/Source/EditorToolset/Private/Tests)