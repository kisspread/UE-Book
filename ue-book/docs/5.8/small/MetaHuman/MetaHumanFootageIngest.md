# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman动画师工具包 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、动画资产、配置文件） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2014-03-14 |
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方为 Unreal Engine 开发的 MetaHuman 工作流核心工具包。它并非一个单一功能的插件，而是一个庞大的工具集，旨在提供从真实世界捕获面部表演，到将其应用于 MetaHuman 数字人角色，再到在引擎中进行精细动画编辑和优化的完整解决方案。**当前文档重点描述的 `MetaHumanFootageIngest` 模块**是该工具链的起始环节，负责管理捕获设备、连接手机或专业摄像头进行面部捕捉，并将捕捉到的视频素材（Footage）导入到 Unreal Engine 项目中，供后续的面部追踪、动画求解等流程使用。

**重要提示**：根据源码中的 `UE_DEPRECATED(5.7)` 标记，`MetaHumanFootageIngest` 模块的功能自 5.7 版本起已迁移至 `CaptureManager` 模块。本文档描述的功能可能在未来版本中不再适用。

## 使用场景

- **专业影视与游戏制作**：使用 iPhone LiDAR 或其他深度传感器捕获演员的面部表演，通过此插件导入引擎，快速生成高质量的数字人动画。
- **实时数字人驱动**：结合 Live Link，在虚拟制片或直播场景中，实时将真实面部表情映射到 MetaHuman 角色上。
- **批量内容生产**：在需要处理大量面部捕捉数据的项目中，利用批处理工具高效管理素材导入和处理流程。
- **自定义面部动画工作流**：开发者可以基于此插件提供的核心模块（如 FaceFittingSolver, FaceAnimationSolver）构建自己的面部动画管线。

## 蓝图用法

`MetaHumanFootageIngest` 模块主要提供编辑器界面（Editor UI）功能，其核心类（如 `SCaptureManagerWidget`, `FCaptureManager`）均为 Slate UI 组件或 C++ 单例，并未暴露大量直接可用的蓝图节点。其功能通过编辑器内的 `Capture Manager` 面板和相关资产（如 `UMetaHumanCaptureSource`）访问。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FCaptureManager::Get()` | 获取捕获管理器的单例实例（C++ 中使用）。 | `FCaptureManager` |
| `FCaptureManager::Show()` | 显示“捕获管理器”编辑器窗口。 | `FCaptureManager` |
| `FCaptureManager::ShowMonitoringTab()` | 显示指定捕获源的监控标签页。 | `FCaptureManager` |

### 使用示例（蓝图描述）

在蓝图中直接调用此模块的底层功能较为有限。典型的工作流程是在 C++ 代码或编辑器扩展插件中，通过 `FCaptureManager::Get()->Show()` 来以编程方式打开捕获管理器界面，供用户操作。

## C++ 用法

### 头文件引入

要使用捕获管理器的核心功能，需要包含其模块头文件。
```cpp
#include "CaptureManager.h"
```
（注意：此头文件位于 `MetaHumanFootageIngest` 模块中，该模块已被标记为废弃。）

### 基本用法

以下示例展示了如何在编辑器插件或工具代码中初始化并显示捕获管理器。

```cpp
// 来源：Source/MetaHumanFootageIngest/Private/MetaHumanFootageIngestModule.cpp 与 Public/CaptureManager.h
// 在模块启动时初始化捕获管理器单例
void FMyEditorToolsModule::StartupModule()
{
    // 获取捕获管理器实例并初始化
    FCaptureManager::Initialize();
    // 通常不会立即显示，而是等待用户触发
}

// 当需要显示捕获管理器时调用
void FMyEditorToolsModule::OpenCaptureManager()
{
    if (FCaptureManager* CaptureManager = FCaptureManager::Get())
    {
        CaptureManager->Show();
    }
}
```

### 进阶用法

结合 `UMetaHumanCaptureSource` 资产，可以编程方式启动和管理特定的捕获源。

```cpp
// 假设已有一个有效的 UMetaHumanCaptureSource* CaptureSource 资产指针
// 来源：源码推断自 Public/CaptureSourcesWidget.h 中的委托
void FMyTool::StartCaptureOnSource(UMetaHumanCaptureSource* CaptureSource)
{
    if (CaptureSource)
    {
        // 调用捕获源的接口开始捕获 (具体接口需查看 UMetaHumanCaptureSource 定义)
        // CaptureSource->StartCapture();

        // 可以通过捕获管理器显示其监控界面
        if (FCaptureManager* CaptureManager = FCaptureManager::Get())
        {
            CaptureManager->ShowMonitoringTab(CaptureSource);
        }
    }
}
```

## Demo 示例

一个最小的、仅用于显示捕获管理器窗口的编辑器工具模块。

**MyCaptureTool.h**
```cpp
#pragma once

#include "Modules/ModuleManager.h"

class FMyCaptureToolModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

    void OpenCaptureManagerWindow();
};
```

**MyCaptureTool.cpp**
```cpp
#include "MyCaptureTool.h"
#include "CaptureManager.h" // 来自 MetaHumanFootageIngest 模块

#define LOCTEXT_NAMESPACE "FMyCaptureToolModule"

void FMyCaptureToolModule::StartupModule()
{
    // 初始化捕获管理器
    FCaptureManager::Initialize();
}

void FMyCaptureToolModule::ShutdownModule()
{
    FCaptureManager::Terminate();
}

void FMyCaptureToolModule::OpenCaptureManagerWindow()
{
    if (FCaptureManager* CM = FCaptureManager::Get())
    {
        CM->Show();
    }
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyCaptureToolModule, MyCaptureTool)
```

## 模块依赖

`MetaHumanFootageIngest` 模块本身的 `Build.cs` 文件未在提供信息中完整列出，但根据其公共头文件引用的类型，可以推断其依赖。

| 模块 | 用途 |
|---|---|
| `MetaHumanCaptureSource` | 核心捕获源资产 (`UMetaHumanCaptureSource`) 的定义。 |
| `MetaHumanCaptureProtocolStack` | 捕获设备通信协议栈。 |
| `MetaHumanCaptureUtils` | 捕获相关的通用工具函数。 |
| `MetaHumanImageViewerEditor` | 用于预览捕获图像的编辑器组件。 |
| `Slate`, `SlateCore`, `UMG` | 构成捕获管理器复杂的用户界面。 |
| `ToolMenus` | 用于构建编辑器工具栏和菜单。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时，禁用关卡序列导出功能，以避免冲突。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复了 MetaHuman 上的渲染瑕疵（伪影）。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 当进行身体追踪时，过滤掉相关的可视化对象，使界面更清晰。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 为已有的网格体导出动画序列，完善了动画导出工作流。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复了 Sequencer（序列器）的缓存问题，提升了编辑器稳定性。 |

### 维护评价

- **活跃维护**：从 Git 历史看，MetaHuman Animator 插件集在近期（2026年5月）仍有频繁的功能更新和 Bug 修复，表明 Epic Games 正在积极维护。
- **模块状态**：**存在关键警告**。当前文档重点描述的 `MetaHumanFootageIngest` 模块已被**明确标记为废弃（Deprecated since 5.7）**。其功能已迁移至新的 `CaptureManager` 模块。这意味着在新版引擎中使用本文档描述的类和接口可能会导致编译警告或功能失效。
- **推荐建议**：对于新项目或引擎版本 >= 5.7 的情况，**强烈不推荐**使用 `MetaHumanFootageIngest` 模块。应转向使用官方提供的最新 `CaptureManager` 模块或相关工具。对于维护旧版（5.6及以下）项目的开发者，此模块仍是有效的捕获入口。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/metahuman-in-unreal-engine/) （MetaHuman 总体文档，非特指此模块）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanFootageIngest) （`MetaHumanFootageIngest` 模块源码目录）