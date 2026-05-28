# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画师工具包 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（内容资产、Slate 样式、算法实现等） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 为 Unreal Engine 提供的官方数字人类创建与动画化工具包。它解决的是“如何从现实世界的捕获数据高效、自动化地生成高质量的数字人类资产和动画”这一核心问题。该插件是 MetaHuman 工作流的中心枢纽，整合了从演员面部/身体表演捕获、数据处理、面部绑定、动画驱动到最终序列化输出的完整流水线。

基于源码分析，其核心功能模块包括：
1.  **捕获与摄取**：管理物理捕获设备（如 iPhone、专业摄像头）、录制现场表演并将原始数据（视频、深度信息等）导入引擎。
2.  **面部追踪与求解**：分析捕获的面部标记点或视频流，计算出 MetaHuman 面部骨骼（Control Rig）的驱动数据。
3.  **身份创建与定制**：提供从照片或扫描数据创建新的 MetaHuman 数字身份（Identity）的完整流程。
4.  **动画与序列化**：将求解出的动画数据应用到 MetaHuman 角色上，并支持将其导出为动画序列。
5.  **批量处理与流水线**：支持自动化处理大量捕获数据。

## 使用场景

-   **影视级数字人类**：为电影或高品质过场动画制作逼真的数字演员，需要从真实演员捕获表演并应用到 MetaHuman 角色。
-   **游戏过场动画**：为 3A 级游戏快速生成大量高质量的面部动画，减少手工关键帧工作。
-   **虚拟制作与实时渲染**：在虚拟制片流程中，使用现场捕获数据驱动虚拟角色。
-   **MetaHuman 定制**：从照片或扫描数据创建独一无二的 MetaHuman 角色。
-   **音频驱动动画**：仅通过音频输入自动生成口型和基本面部表情。

## 蓝图用法

MetaHuman Animator 主要是一个面向编辑器的工具包，其核心操作通过编辑器 UI（如 Capture Manager 窗口）和 Content Browser 的资产操作完成。暴露给蓝图的可调用函数相对有限，更多地用于配置和查询。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get()` | 获取 Capture Manager 的单例实例。 | `FCaptureManager` |
| `Show()` | 显示 Capture Manager 编辑器窗口。 | `FCaptureManager` |
| `ShowMonitoringTab` | 为指定的捕获源打开或激活其监控选项卡。 | `FCaptureManager` |

### 使用示例（蓝图描述）

在蓝图中，你通常会通过调用 `FCaptureManager::Get()->Show()` 来打开捕获管理器窗口，以进行素材导入和设备监控。更复杂的流程（如批量处理）通常通过 Python 脚本或直接在编辑器中使用 UI 工具来完成，而不是通过蓝图节点。

## C++ 用法

### 头文件引入

```cpp
#include "CaptureManager.h" // 用于访问捕获管理器
#include "MetaHumanFootageIngestModule.h" // 模块接口
```

### 基本用法

从 `FCaptureManager` 类的用法可以看出，它是一个单例模式。以下是如何在编辑器代码中访问它的示例。

```cpp
// 来源: Public/CaptureManager.h
// 显示 Capture Manager 窗口
if (FCaptureManager* CaptureManager = FCaptureManager::Get())
{
    CaptureManager->Show();
}

// 为特定捕获源打开监控标签
UMetaHumanCaptureSource* MyCaptureSource = ...; // 获取或创建你的捕获源
if (FCaptureManager* CaptureManager = FCaptureManager::Get())
{
    TWeakPtr<SDockTab> MonitoringTab = CaptureManager->ShowMonitoringTab(MyCaptureSource);
    // 可以进一步操作这个标签页
}
```

### 进阶用法

MetaHuman Animator 的复杂用法涉及多个子模块协同工作。例如，一个完整的捕获、求解和导出流程会涉及 `MetaHumanCaptureSource`, `MetaHumanFaceAnimationSolver`, `MetaHumanSequencer` 等模块的 API。然而，这些 API 通常被封装在编辑器 UI 和工具命令（`UToolMenus`, `FUICommandInfo`）之后。要深入使用，需要：

1.  **注册自定义捕获源**：实现 `IMetaHumanCaptureSource` 接口以集成自定义捕获硬件。
2.  **扩展处理流水线**：通过 `MetaHumanPipeline` 模块定义自定义的数据处理步骤。
3.  **自动化批量操作**：使用 `MetaHumanBatchProcessor` 模块的 API 来处理文件夹中的多个表演数据。
4.  **操作求解器**：使用 `MetaHumanFaceFittingSolver` 或 `MetaHumanFaceAnimationSolver` 的 C++ 类来驱动面部绑定。

这些用法通常需要深入理解整个 MetaHuman 数据流和各个模块的依赖关系。

## Demo 示例

MetaHuman Animator 的演示主要通过 Epic Games 提供的示例项目和官方文档中的工作流指南进行。一个最小化的 C++ 示例是初始化模块并显示管理器窗口：

```cpp
// MyEditorModule.h
#pragma once

#include "Modules/ModuleManager.h"

class FMyEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

```cpp
// MyEditorModule.cpp
#include "MyEditorModule.h"
#include "CaptureManager.h" // 依赖 MetaHumanFootageIngest 模块

void FMyEditorModule::StartupModule()
{
    // 确保 CaptureManager 单例已初始化（通常在模块启动时自动完成）
    // 之后可以通过 FCaptureManager::Get() 访问
}

void FMyEditorModule::ShutdownModule()
{
    // 清理工作
}

IMPLEMENT_MODULE(FMyEditorModule, MyEditorModule)
```

**注意**：此示例仅展示如何引入头文件和确认模块可用。实际的完整工作流（捕获、处理、导出）通常通过编辑器 UI 操作或复杂的 Python 脚本来完成，这些脚本会调用该插件暴露给 Python 的 API。

## 模块依赖

从提供的模块列表和依赖关系看，此插件内部模块众多且相互依赖。对于外部使用者而言，主要依赖以下插件提供的公共 API 和资产：

| 模块 | 用途 |
|---|---|
| `MetaHumanSDKEditor` | MetaHuman SDK 的编辑器部分，提供基础类型和工具。 |
| `ControlRigDeveloper` | 用于运行时和编辑器中创建、编辑和操作 Control Rig（MetaHuman 的驱动骨骼）。 |
| `SkeletalMeshUtilitiesCommon` | 提供处理骨骼网格体的通用工具函数。 |
*注：Core, CoreUObject, Engine, Slate 等为通用依赖，已省略。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 修复了在启用身体跟踪时，关卡序列导出可能出错的问题。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复了 MetaHuman 角色身上的渲染瑕疵。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 在身体跟踪模式下过滤掉不必要的可视化对象。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持为已有的 MetaHuman 网格体导出动画序列。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复了 Sequencer 相关的缓存问题。 |

### 维护评价

-   **活跃维护**：从 git 历史看，该插件在 2026 年 5 月仍有频繁的功能更新和错误修复，表明 Epic Games 正在积极维护和改进 MetaHuman Animator。
-   **核心工具链**：作为创建数字人类的核心工具，它很可能伴随着 Unreal Engine 主版本的更新而持续演进。
-   **已知问题与限制**：从源码中可以看到，`MetaHumanFootageIngest` 等部分模块已被标记为 **`UE_DEPRECATED(5.7)`**，并指出功能已迁移到 `CaptureManager` 模块。这意味着用户应注意避免使用过时的 API，并关注新模块的文档。
-   **推荐使用**：**强烈推荐**用于任何需要高质量、基于捕获数据的数字人类动画项目。它是 Epic Games 官方支持的一站式解决方案，但需要遵循其不断更新的最佳实践。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
-   [官方文档](https://docs.unrealengine.com/5.8/en-US/metahuman-unreal-engine/)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source) （注：测试用例通常位于各子模块的 `Tests` 目录下，或集成在引擎自动化测试框架中）