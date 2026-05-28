# MetaHuman Footage Ingest

> The official MetaHuman Unreal Engine toolkit（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 素材导入模块 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `MetaHumanFootageIngest` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-12-08 |
| 年龄标签 | 🏛️ 文物（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanFootageIngest) | |

## 用途

**MetaHumanFootageIngest** 是 MetaHuman Animator 工具链中的**视频素材导入与管理模块**。它解决的核心问题是：如何将从 iPhone 或其他设备拍摄的面部表演视频（Footage）高效地导入到 Unreal Engine 中，并转换为可用于驱动 MetaHuman 角色的动画数据。

该模块提供了一个完整的**捕获管理器（Capture Manager）** 编辑器界面，用户可以在此界面中：
1.  **连接和管理捕获设备**（如 iPhone 的 Live Link Face 应用）。
2.  **监控和录制**实时的面部表演数据。
3.  **浏览和管理**本地存储的视频素材（Takes）。
4.  **将视频素材排队、导入并转换**为 Unreal Engine 内部的动画资产。

**重要提示**：根据源码中的 `UE_DEPRECATED` 宏，**该模块从 UE 5.7 版本开始已被标记为废弃（Deprecated）**，其功能已迁移至新的 `CaptureManager` 模块。本文档旨在记录其在旧版本中的功能和用法。

## 使用场景

-   **影视与游戏开发**：当你需要将演员的真实面部表演通过 iPhone（使用 Live Link Face App）捕捉下来，并用于驱动数字角色（MetaHuman）的动画时。
-   **动画制作工作流**：你有大量的、来自不同机位或不同表演的视频素材，需要一个集中的工具来管理、预览和批量导入这些素材。
-   **内容创作**：你想快速基于一段视频生成一个简短的 MetaHuman 面部动画序列，用于社交媒体内容或原型制作。

## 蓝图用法

该模块主要提供**编辑器UI工具**（捕获管理器窗口），而非运行时蓝图节点。其核心类如 `UCaptureManagerEditorContext`、`SCaptureManagerWidget` 等均为编辑器类或 Slate Widget。

主要的运行时交互类是 `UMetaHumanCaptureSource`，它代表一个捕获源。

### 核心类

| 类/结构 | 说明 |
|---|---|
| `UMetaHumanCaptureSource` | 表示一个捕获源（如一个设备或一组文件），是数据导入的起点。 |
| `UCaptureManagerEditorContext` | 编辑器上下文，用于在捕获管理器 UI 中引用当前活动的小部件。 |
| `FFootageTakeItem` | 表示一个“Take”（一段录制的素材），包含名称、状态、预览图等信息。 |
| `FFootageCaptureSource` | 捕获源的运行时数据结构，包含名称、状态、Take列表等。 |
| `FCaptureManager` | 捕获管理器的单例类，负责管理标签页的注册和显示。 |

## C++ 用法

由于该模块已废弃且主要用于编辑器工具，其提供的公开 C++ API 相对有限，且主要服务于内部 UI 和模块间通信。

### 头文件引入

```cpp
#include "MetaHumanFootageIngestModule.h"
#include "CaptureManager.h"
#include "CaptureSourcesWidget.h" // 注意：这些头文件在UE 5.7+中可能已不可用
```

### 基本用法：启动捕获管理器

通过模块接口或全局单例启动捕获管理器窗口。
*(来源: `Public/CaptureManager.h`)*

```cpp
// 获取并显示捕获管理器
if (FCaptureManager* CaptureManager = FCaptureManager::Get())
{
    CaptureManager->Show();
}

// 或者，显示特定捕获源的监控标签页
UMetaHumanCaptureSource* MyCaptureSource = ...; // 获取或创建你的捕获源
TWeakPtr<SDockTab> MonitoringTab = FCaptureManager::Get()->ShowMonitoringTab(MyCaptureSource);
```

### 进阶用法：监听导入事件（模块内部用法）

该模块内部通过委托（Delegates）通知 UI 更新。外部模块通常通过 `UMetaHumanCaptureSource` 本身的事件来监听导入完成。
*(来源: `Public/CaptureSourcesWidget.h`)*

```cpp
// 以下委托在 SCaptureSourcesWidget 中定义，用于通知外部组件（如 FootageIngestWidget）
// 外部模块通常不直接使用这些，而是监听 UMetaHumanCaptureSource 自身的事件
DECLARE_DELEGATE_TwoParams(FOnCaptureSourceFinishedImportingTakes, const TArray<FMetaHumanTake>& InTakes, TSharedPtr<FFootageCaptureSource> InCaptureSource);
```

## Demo 示例

以下是一个最小化的 C++ 示例，演示如何在运行时访问捕获管理器（在编辑器工具中）。
*注意：由于模块已废弃，此示例仅适用于 UE 5.6 及更早版本，或作为理解旧代码的参考。*

**MyFootageTool.h**
```cpp
// 版权所有 Epic Games, Inc. 保留所有权利。
#pragma once

#include "CoreMinimal.h"

class FMyFootageTool
{
public:
    /** 初始化并显示捕获管理器 */
    static void OpenCaptureManager();
};
```

**MyFootageTool.cpp**
```cpp
// 版权所有 Epic Games, Inc. 保留所有权利。
#include "MyFootageTool.h"

// 注意：在UE 5.7+中，包含这些头文件会引发废弃警告或错误
#include "MetaHumanFootageIngestModule.h" // 或直接包含 "CaptureManager.h"
#include "CaptureManager.h"

void FMyFootageTool::OpenCaptureManager()
{
    // 通过全局单例访问捕获管理器
    if (FCaptureManager* CaptureManager = FCaptureManager::Get())
    {
        CaptureManager->Show();
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("CaptureManager 未初始化。请确保 MetaHumanFootageIngest 模块已加载。"));
    }
}
```

## 模块依赖

要使用此模块的功能（或基于其源码进行学习），你的模块需要依赖以下 MetaHuman 特有的模块。

| 模块 | 用途 |
|---|---|
| `MetaHumanCaptureSource` | 提供核心的 `UMetaHumanCaptureSource` 类，是所有捕获数据的来源抽象。 |
| `MetaHumanCaptureUtils` | 提供捕获和转换过程中所需的通用工具函数和数据结构。 |
| `MetaHumanCoreTechLib` | MetaHuman 核心技术库，提供基础的数学、数据处理等功能。 |
| `MetaHumanCaptureDataEditor` | 编辑器模块，用于处理捕获数据相关的资产编辑器功能。 |
| `MetaHumanImageViewerEditor` | 提供图像查看器编辑器功能。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 修复了在启用身体追踪时序列导出功能冲突的问题。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复了 MetaHuman 角色上的渲染瑕疵。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 在身体追踪时过滤可视化的辅助对象。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 实现了对现有网格体直接导出动画序列的功能。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复了 Sequencer 中的缓存问题。 |

### 维护评价

**该模块已被正式废弃（Deprecated）。**

-   **年龄与状态**：创建于 2022 年 12 月，在 UE 5.7（约 2023 年发布）中被标记为废弃，功能被 `CaptureManager` 模块取代。
-   **近期更新**：最近的提交记录（2026年）都是对现有功能的错误修复和优化，**没有新功能开发**。这符合废弃模块的典型维护模式。
-   **推荐使用**：**不推荐在新项目中使用此模块**。请查阅 Epic Games 的官方文档，寻找已迁移到 `CaptureManager` 模块的最新功能和 API。对于维护旧项目或学习 MetaHuman 工具链历史代码的开发者，此模块仍具有参考价值。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanFootageIngest)
-   [官方文档]() (无)
-   [测试用例]() (未在提供的信息中找到)