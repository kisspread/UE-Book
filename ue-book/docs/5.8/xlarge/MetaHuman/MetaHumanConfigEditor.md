# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | 数字人类动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产、配置、工具） |
| 模块 | `MetaHumanAnimator` (Editor), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime), `MeshTrackerInterface` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕（约 N 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

**MetaHuman Animator** 是一个功能庞大、高度专业化的插件，其核心目的是提供从真实人类表演到 Epic 虚拟人类 (MetaHuman) 角色动画的端到端解决方案。它不仅仅是简单的面部动画工具，而是一个完整的“捕获-追踪-求解-驱动”流水线。

具体来说，它解决了以下问题：
1.  **面部数据捕获与导入**：支持从多种设备（如 iPhone 的深度摄像头）捕获面部表演视频和深度数据。
2.  **面部特征追踪**：自动或半自动地从捕获的视频/图像中追踪关键面部特征点和轮廓。
3.  **动画求解**：将追踪到的数据求解为控制 MetaHuman 角色面部骨骼和变形器的动画数据。
4.  **性能优化与管理**：提供批量处理工具、配置管理以及与 Sequencer 的深度集成，以管理复杂动画数据。
5.  **高级功能**：支持基于音频的面部动画生成 (Speech2Face)、身体动作追踪（通过外部模块）、以及高保真深度图生成。

这个插件存在的意义是让游戏开发者、虚拟制片团队和动画师能够高效、逼真地将真人表演赋予 MetaHuman 角色，大幅降低高质量数字人动画的制作门槛和时间成本。

## 使用场景

- **虚拟制片 (Virtual Production)**：在实时渲染的电影或广告中，需要快速将演员的表演同步到数字替身（MetaHuman）上。
- **游戏开发中的过场动画**：为游戏角色制作基于真人表演的、高质量且风格统一的面部动画，尤其是大量对话内容。
- **快速原型或预演 (Previz)**：在完整动画制作前，快速测试和预览对话场景的效果。
- **创建逼真的 NPC 对话**：在开放世界游戏中，为海量 NPC 对话生成自然、多样的面部动画。
- **基于音频的快速动画**：当没有视频源时，仅凭角色台词音频自动生成基础的、节奏匹配的口型和面部表情动画。

## 蓝图用法

> **注意**：此插件的核心功能主要由 C++ 驱动，通过编辑器工具（Widget、Customization、Asset Actions）暴露给用户。纯蓝图可调用的 API 相对较少，主要集中在数据资产的操作和流程控制上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get All MetaHuman Configs` | 获取所有可用的 MetaHuman 配置资产。 | `UMetaHumanConfig` (推测) |
| `Create New Performance` | 创建一个新的 Performance 资产，用于存储面部动画数据。 | `UMetaHumanPerformance` (推测) |

### 使用示例（蓝图描述）

一个典型的蓝图工作流可能是：
1.  使用 `Asset Registry` 节点查找 `MetaHumanConfig` 类型的资产，用于初始化或验证角色。
2.  通过 `Create Object from Blueprint` 或工厂模式创建 `UMetaHumanPerformance` 资产。
3.  调用该 Performance 对象上的导入函数，传入捕获的视频文件路径或深度数据。
4.  将处理后的 Performance 数据应用到场景中对应 MetaHuman 角色的 `Control Rig` 组件上。

*（由于插件以编辑器扩展和底层算法为主，详细蓝图节点需结合具体资产类型和上下文进一步分析）*

## C++ 用法

### 头文件引入

```cpp
// 核心模块
#include "MetaHumanConfig.h"
#include "MetaHumanPerformance.h"
#include "MetaHumanIdentity.h"

// 捕获与工具链
#include "MetaHumanCaptureUtils.h"
#include "MetaHumanFaceAnimationSolver.h"

// 编辑器扩展 (仅限 Editor 模块使用)
#include "MetaHumanConfigEditor.h"
#include "MetaHumanIdentityEditor.h"
```

### 基本用法

以操作 `MetaHumanConfig` 资产为例，展示如何通过 C++ 进行基本查询和编辑。

```cpp
// 来源: MetaHumanConfigEditor/Source/MetaHumanConfigEditor/Private/Customizations/MetaHumanConfigCustomizations.h
// 背景: 这是一个编辑器细节自定义类，展示了如何与 MetaHumanConfig 交互。
// 假设我们已经有了一个 UMetaHumanConfig* ConfigAsset;

// 1. 查询配置类型
EMetaHumanConfigType ConfigType = ConfigAsset->GetConfigType(); // 获取配置类型（如面部、身体等）

// 2. 获取配置中的资产数据（例如，关联的 Control Rig 或网格体）
FAssetData AssetData;
if (ConfigAsset->TryGetAssetData(TEXT("FaceControlRig"), AssetData))
{
    // 成功获取了资产数据，可以加载或使用
    UClass* AssetClass = AssetData.GetClass();
}

// 3. (编辑器中) 应用自定义细节面板
// 在编辑器模块中注册细节自定义
PropertyModule.RegisterCustomClassLayout(
    UMetaHumanConfig::StaticClass()->GetFName(),
    FOnGetDetailCustomizationInstance::CreateStatic(&FMetaHumanConfigCustomization::MakeInstance)
);
```

### 进阶用法

组合多个模块，构建一个简化的面部动画处理流程。

```cpp
// 来源: 结合 MetaHumanFaceAnimationSolver, MetaHumanPerformance, MetaHumanCore 模块推断
// 目标: 从追踪数据生成动画数据

// 假设我们已有 UMetaHumanPerformance* PerformanceAsset 和 追踪结果数据
// 1. 初始化面部动画求解器
UMetaHumanFaceAnimationSolver* AnimationSolver = NewObject<UMetaHumanFaceAnimationSolver>();
AnimationSolver->Initialize(/* 配置参数 */);

// 2. 使用求解器处理数据，生成动画曲线
TArray<FMetaHumanFrameAnimationData> AnimationFrames;
AnimationSolver->Solve(/* 追踪到的轮廓点/深度数据 */, AnimationFrames);

// 3. 将动画数据设置到 Performance 资产中
PerformanceAsset->SetAnimationData(AnimationFrames);

// 4. (在运行时或编辑器预览中) 驱动 MetaHuman 角色
if (AActor* MetaHumanActor = /* 获取场景中的 MetaHuman Actor */)
{
    if (USkeletalMeshComponent* MeshComp = MetaHumanActor->GetComponentByClass<USkeletalMeshComponent>())
    {
        // 应用 Performance 数据，通常通过 Control Rig 或 自定义 AnimInstance
        // 具体的驱动方式依赖于插件内部的集成逻辑
        ApplyPerformanceToMeshComponent(PerformanceAsset, MeshComp);
    }
}
```

## Demo 示例

此插件规模巨大（500+文件），且功能高度专业，不适合提供单一个文件的最小Demo。
一个完整的使用Demo通常需要：
1.  一个 MetaHuman 角色蓝图。
2.  捕获的视频文件（例如，使用 Live Link Face App 录制）。
3.  通过编辑器中的 `MetaHuman Animator` 工具面板（`Window > MetaHuman Animator`）创建和配置 `Performance` 资产。
4.  将处理后的 `Performance` 数据链接到角色蓝图。

建议参考 Epic Games 官方提供的 **MetaHuman Sample Project** 或文档中的 **MetaHuman Animator Quick Start** 指南。

## 模块依赖

由于插件本身包含大量互相依赖的模块，作为使用者，你的模块主要依赖 **运行时核心模块**。

| 模块 | 用途 |
|---|---|
| `MetaHumanCore` | MetaHuman 系统的核心运行时逻辑和数据类型。 |
| `MetaHumanPerformance` | 存储和管理面部动画性能数据（Perfo）的资产。 |
| `MetaHumanConfig` | 存储 MetaHuman 角色配置的资产。 |
| `MetaHumanFaceAnimationSolver` | 面部动画求解算法的核心模块。 |
| `MetaHumanCaptureUtils` | 捕获数据处理的工具函数库。 |
| `ControlRig` | (UE 内置) 用于驱动 MetaHuman 骨骼动画的控制系统，是动画应用的最终环节。 |

*编辑器功能（如工具面板、资产自定义）需要依赖对应的 `Editor` 后缀模块。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时，禁用关卡序列导出功能。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 角色的渲染瑕疵。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 在进行身体追踪时过滤可视化对象，优化性能。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MetaHuman Animator] 新增为已有网格体导出动画序列的功能。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复与 Sequencer 集成时的缓存问题。 |

### 维护评价

**活跃维护**。
-   从 git 历史看，更新非常频繁（最近一次更新距今不足 1 周），且 commit 内容显示团队在持续添加新功能（如为现有网格体导出动画）、优化性能（修复渲染瑕疵、缓存问题）和增强集成（身体追踪支持）。
-   作为 Epic 官方的旗舰级数字人创作工具，MetaHuman Animator 是 MetaHuman 生态的核心，预计会被长期积极维护和迭代。
-   没有观察到废弃或实验性的标记。虽然模块数量众多，但这是因为其功能复杂，而非设计缺陷。
-   **强烈推荐使用**，尤其是对于涉及 MetaHuman 角色的专业动画和虚拟制片项目。对于小型或概念验证项目，可能需要考虑其学习和配置成本。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/metahuman-animator-in-unreal-engine/) (通常位于 Epic 官方文档站，此处为推断路径)
- 测试用例：未在提供的路径中明确列出，可能位于 `Engine/Plugins/MetaHuman/Tests` 或各子模块的 `Tests` 目录下。