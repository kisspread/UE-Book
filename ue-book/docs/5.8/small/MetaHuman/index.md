# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画器 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、动画资源） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | unknown |
| 年龄标签 |  |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是一个集成的工具包，旨在将真实的演员面部表演数据转化为超逼真数字人（MetaHuman）的动画。它不仅仅是一个工具集合，而是一套完整的工作流程，涵盖了从捕捉原始表演数据（如视频）、进行面部追踪与拟合、求解面部动画，到最终在引擎中应用这些动画的全过程。其核心目标是降低创建高质量、个性化数字人面部动画的门槛，使其可用于影视、游戏、虚拟直播等领域。

## 使用场景

-   **影视与虚拟制作**：使用 iPhone 或其他深度摄像机捕捉演员面部表演，快速生成与演员高度相似的数字替身动画。
-   **游戏开发**：为游戏角色创建基于真实表演的面部动画，提升过场动画的叙事真实感。
-   **虚拟主播/偶像**：驱动 MetaHuman 角色进行实时的面部表情表演。

## 蓝图用法

此插件主要通过编辑器中的工具栏、资产编辑器和上下文菜单提供蓝图/编辑器工作流。核心功能被封装为独立的子模块。

### 核心工作流节点（推测）

| 工具/功能 | 说明 | 可能所在模块 |
|---|---|---|
| **创建 MetaHuman 身份** | 从照片或扫描数据创建数字人身份模板 | `MetaHumanIdentity`, `MetaHumanIdentityEditor` |
| **导入表演数据** | 导入 iPhone 深度视频、音频或其他捕捉数据 | `MetaHumanCaptureSource`, `MetaHumanFootageIngest` |
| **面部追踪与拟合** | 对导入的视频数据进行面部关键点追踪和网格拟合 | `MetaHumanFaceContourTracker`, `MetaHumanFaceFittingSolver` |
| **动画求解** | 将追踪到的面部数据转换为 MetaHuman 骨骼的动画控制数据 | `MetaHumanFaceAnimationSolver` |
| **应用动画** | 将生成的动画应用到场景中的 MetaHuman 角色 | `MetaHumanPerformance`, `MetaHumanSequencer` |

### 使用示例（编辑器操作描述）

1.  **创建身份**：在 Content Browser 中右键，选择 `Create MetaHuman Identity`。
2.  **捕捉数据**：使用 `MetaHuman Capture` 工具捕获 iPhone 的 TrueDepth 相机视频。
3.  **处理数据**：在 MetaHuman Editor 窗口中，依次执行 `Track Contours` -> `Fit Face` -> `Solve Animation`。
4.  **导出与应用**：将求解出的动画资产（如 `Level Sequence`）拖拽到场景中已放置的 MetaHuman 角色上。

## C++ 用法

对于开发者，此插件提供了一系列 C++ 接口用于深度定制或集成到自动化管线中。

### 头文件引入

根据你的需求，引入对应子模块的头文件，例如：
```cpp
// 引入核心动画求解接口
#include "MetaHumanFaceAnimationSolver/Public/IMetaHumanFaceAnimationSolverModule.h"
// 引入性能数据处理
#include "MetaHumanPerformance/Public/MetaHumanPerformance.h"
```

### 基本用法

由于插件规模庞大，具体的 API 用法需参考各子模块文档。通用模式如下：
```cpp
// 示例：获取 MetaHuman 面部动画求解模块的接口
// 路径：Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanFaceAnimationSolver/...
IMetaHumanFaceAnimationSolverModule* SolverModule = FModuleManager::GetModulePtr<IMetaHumanFaceAnimationSolverModule>(TEXT("MetaHumanFaceAnimationSolver"));
if (SolverModule)
{
    // 使用模块接口进行操作
    // ...
}
```

## Demo 示例

由于此插件包含庞大的编辑器工具和资产流程，提供一个可编译的最小 C++ 示例不切实际且可能无意义。建议：
1.  使用 Epic Games 提供的官方 MetaHuman 示例项目。
2.  参考插件内各个子模块的测试用例（如果存在）。
3.  在编辑器中按照上述“蓝图/编辑器用法”流程进行操作实践。

## 模块依赖

要使用此插件或在你的模块中依赖其功能，除了标准的 Core/Engine 模块外，你可能需要依赖以下独特模块：

| 模块 | 用途 |
|---|---|
| `SkeletalMeshUtilitiesCommon` | 提供骨骼网格体相关的通用工具函数 |
| `ControlRigDeveloper` | 与 Control Rig（控制系统）开发相关的功能 |
| `MetaHumanCaptureDataEditor` | 用于编辑和处理捕捉数据 |
| `MetaHumanSDKEditor` | MetaHuman SDK 的编辑器部分，提供核心身份资产操作 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体追踪时禁用关卡序列导出 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 上的渲染伪影 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持为已有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复序列器缓存问题 |

### 维护评价

-   **活跃维护**：根据最新的 Git 记录，该插件在过去一周内有多次实质性功能更新和 Bug 修复（如身体追踪集成、渲染修复、导出优化），表明 Epic Games 正在**积极维护**此核心数字人工具。
-   **推荐使用**：作为官方出品的核心数字人创作与动画工作流插件，其稳定性和功能完整性有保障，是从事数字人开发项目的必备工具。
-   **注意事项**：由于模块众多且功能专业，学习曲线较陡。建议从官方文档和示例项目入手。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
-   [官方文档]() (暂无)
-   [测试用例]() (可能位于 `Engine/Tests/MetaHuman/` 或各子模块内)