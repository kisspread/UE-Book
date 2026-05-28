# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | 数字人动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器工具、材质模板、测试资源等） |
| 模块 | `MetaHumanAnimator` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanPipeline` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕（信息不足，推测为近期版本） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的用于创建、驱动和管理 MetaHuman 数字人的完整工具链插件。它解决的核心问题是：如何从面部视频捕捉或音频等数据源，高效、自动化地生成高质量的、可用于实时驱动的 MetaHuman 数字人资产和动画。

其存在价值在于提供了一个官方、集成、工作流导向的解决方案，涵盖了从原始数据导入、面部追踪、模型拟合、动画解算到最终编辑器集成的全过程，极大降低了创建逼真数字人的技术门槛和复杂度。

## 使用场景

- 你需要从一段面部视频表演（如 iPhone 拍摄）创建数字人角色的动画数据。
- 你有一个 MetaHuman 角色，希望通过面部视频驱动其表情和口型。
- 你需要批量处理多个视频素材，为多个 MetaHuman 角色生成动画。
- 你需要一个可视化的编辑器工具来管理所有捕捉设备、素材源和处理过程。
- 你在开发一个需要高质量数字人角色的游戏或影视项目，并希望使用 Epic 官方的工具链。

## 蓝图用法

由于插件包含众多运行时模块，其蓝图节点分散在各类中。以下是一些核心功能的示例：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Show` | 显示或激活主捕捉管理器编辑器窗口 | `FCaptureManager` |
| `StartCaptureSources` | 为所有已配置的捕捉源启动捕捉 | `SCaptureSourcesWidget` |
| `RefreshCurrentCaptureSource` | 刷新当前选中的捕捉源信息 | `SCaptureSourcesWidget` |
| `GetCurrentCaptureSource` | 获取当前选中的捕捉源对象 | `SCaptureSourcesWidget` |
| `UnqueueTake` | 将一个“Take”从导入队列中移除 | `SFootageIngestWidget` |
| `SaveImportedAssets` | 保存所有通过素材导入流程生成的资产 | `SFootageIngestWidget` |

### 使用示例（蓝图描述）

1.  **显示捕捉管理器**：你可以通过蓝图调用 `FCaptureManager::Get()->Show()` 来打开完整的“Capture Manager”编辑器面板，这是一个集成了所有素材管理、设备监控和导入功能的工作中心。
2.  **编程式添加素材源**：虽然主要交互通过 UI 进行，但理论上可以通过获取 `SCaptureSourcesWidget` 实例，调用其方法来程序化地添加或管理 `UMetaHumanCaptureSource` 资产。
3.  **响应导入事件**：`SFootageIngestWidget` 提供了 `OnTargetFolderAssetPathChanged` 等委托，蓝图系统可以绑定这些委托，在导入路径更改时执行自定义逻辑，例如自动创建特定目录结构。

## C++ 用法

### 头文件引入

```cpp
// 访问核心的动画器工具链
#include "MetaHumanAnimator.h"

// 用于访问“素材导入”模块（注意：该模块在5.7版本已标记为弃用，功能迁移至 CaptureManager 模块）
#include "MetaHumanFootageIngest/Public/CaptureManager.h"
#include "MetaHumanFootageIngest/Public/CaptureSourcesWidget.h"
```

### 基本用法

以下示例展示了如何通过 C++ 代码获取并显示 MetaHuman Animator 的主界面。

```cpp
// 来源: 基于 Public/CaptureManager.h 的实现逻辑
#include "MetaHumanFootageIngest/Public/CaptureManager.h"

// 在某个合适的时机（例如菜单按钮点击），显示捕捉管理器
void UMyEditorUtility::OpenMetaHumanAnimator()
{
    // 获取单例实例
    FCaptureManager* CaptureManager = FCaptureManager::Get();
    if (CaptureManager)
    {
        // 调用 Show() 方法来显示或激活编辑器窗口
        CaptureManager->Show();
    }
}
```

### 进阶用法

以下示例展示了如何访问和管理一个特定的 `MetaHumanCaptureSource`，这通常是与设备或视频文件关联的核心数据资产。

```cpp
// 来源: 基于 Public/CaptureSourcesWidget.h 中 FFootageCaptureSource 结构的用法
#include "MetaHumanCaptureSource/Public/MetaHumanCaptureSource.h"
#include "MetaHumanFootageIngest/Public/CaptureSourcesWidget.h"

// 假设我们已经通过某种方式（例如资产路径）获取到了一个 UMetaHumanCaptureSource
UMetaHumanCaptureSource* MyCaptureSource = LoadObject<UMetaHumanCaptureSource>(nullptr, TEXT("/Game/MetaHumans/MyCharacter_Capture"));

if (MyCaptureSource)
{
    // MetaHumanCaptureSource 包含了对一个具体拍摄数据的描述
    // 你可以通过它获取关联的 Takes（拍摄片段）列表，或查询其当前状态（在线/离线）
    // FFootageCaptureSource 是一个内部运行时结构，代表了 UI 中的可操作项。
    // 实际的“处理”和“导入”流程由 SFootageIngestWidget 协调。
}
```

## Demo 示例

MetaHuman Animator 是一个复杂的、面向编辑器的工具链，而非一个简单的单个运行时组件。因此，没有像简单组件那样的“最小可编译示例”。

**推荐的示例方式**：
1.  启用 `MetaHumanAnimator` 插件。
2.  打开编辑器，通过 `窗口 > 虚拟制片 > Capture Manager` 菜单打开主界面。
3.  按照 Epic 官方文档或 QuickStart 指南，使用 iPhone 或其他兼容设备进行面部捕捉并导入数据。
4.  观察“素材导入”（Footage Ingest）、“身份”（Identity）等子面板的工作流程。

完整的集成示例通常在 Epic 的 **MetaHuman Sample 项目**或 **Virtual Production** 示例项目中提供。

## 模块依赖

插件自身包含大量高度模块化的内部依赖。如果你的项目需要直接与插件的某些特定部分交互（例如，仅使用面部拟合解算器），你需要依赖对应的子模块。

| 模块 | 用途 |
|---|---|
| `MetaHumanCore` | 提供核心数据类型、工具和基础功能。 |
| `MetaHumanIdentity` | 处理 MetaHuman 角色的身份创建、编辑和资产生成。 |
| `MetaHumanCaptureSource` | 定义和管理来自各种设备（如 ARKit）的捕捉数据源。 |
| `MetaHumanFaceFittingSolver` | 执行将面部标记点拟合到 MetaHuman 面部拓扑的核心算法。 |
| `MetaHumanFaceAnimationSolver` | 根据追踪数据解算出最终的面部动画曲线。 |
| `MetaHumanPipeline` | 定义和管理数据处理流水线。 |
| `SkeletalMeshUtilitiesCommon` | 用于骨骼网格体的常见操作（MetaHumanIdentity 依赖）。 |
| `ControlRigDeveloper` | 用于与 Control Rig 框架集成（MetaHumanIdentity 依赖）。 |

**重要提示**：`MetaHumanFootageIngest` 模块（包含本文档分析的多个头文件）已在 **UE 5.7** 中被标记为弃用，其功能已迁移至新的 `CaptureManager` 模块。在新项目中应优先使用新模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 在启用身体追踪时禁用关卡序列导出功能。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 上的渲染瑕疵。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 在身体追踪时过滤可视化对象。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MetaHuman Animator] 支持为现有网格体导出动画序列。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 的缓存问题。 |

### 维护评价

**状态：积极维护中**

**综合评价**：
- **活跃度**：Git 历史显示插件在最近（2026年5月）仍在进行功能性更新和 Bug 修复，而非仅仅是维护性提交，表明其处于**积极开发和维护**状态。
- **内容**：近期提交集中在改进动画导出、修复渲染问题和增强身体追踪集成，说明插件核心功能仍在进化。
- **已知限制**：当前 `MetaHumanFootageIngest` 模块已被弃用，用户应注意代码迁移至 `CaptureManager` 模块。插件对硬件（如 iPhone 用于面部捕捉）和特定工作流有一定要求。
- **推荐使用**：**强烈推荐**。作为 Epic 官方的、仍在积极维护的 MetaHuman 工作流核心插件，它是创建高质量实时数字人的首选和事实标准。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/en-US/metahuman/)（链接指向 MetaHuman 总体文档，Animator 是其一部分）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Tests)（插件内部测试目录）