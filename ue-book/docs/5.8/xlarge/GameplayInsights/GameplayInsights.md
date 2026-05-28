# Animation Insights

> Allows debugging of animation systems via Unreal Insights（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 动画洞察 |
| 分类 | Insights |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GameplayInsights` (Runtime), `GameplayInsightsEditor` (Runtime), `RewindDebugger` (Runtime), `RewindDebuggerRuntime` (Runtime), `RewindDebuggerVLog` (Runtime), `RewindDebuggerVLogRuntime` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-15 |
| 年龄标签 | 🆕（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/GameplayInsights) | |

## 用途

Animation Insights 插件是 Unreal Insights 性能分析系统的一个扩展，专为**动画系统**提供深度调试和性能分析能力。它解决了在复杂动画状态下难以追踪、定位和回放动画系统内部状态的问题。

该插件的核心价值在于：
1.  **数据追踪与记录**：在运行时收集并记录动画系统的详细数据，包括骨骼网格体姿态、动画图状态、混合权重、动画通知、蒙太奇、状态机状态等。
2.  **时间线可视化**：将记录的动画数据以时间线的形式集成到 Unreal Insights 的 Timing Insights 面板中，允许开发者像分析CPU/GPU性能一样，直观地观察动画系统随时间的变化。
3.  **状态回溯与调试**：与 **Rewind Debugger** 紧密集成，允许开发者在事后“倒带”到某个特定时间点，查看当时所有动画对象的状态、属性值和动画图快照，极大简化了复杂动画问题的调试流程。
4.  **编辑器集成**：在编辑器中，可以与动画蓝图编辑器联动，将录制的动画状态以“自定义调试对象”的形式传递给动画蓝图调试器，实现录制数据的可视化调试。

简而言之，它是一个**将动画系统变成“性能图表”和“可调试状态机”** 的工具，用于解决动画相关的性能瓶颈和逻辑错误。

## 使用场景

-   **你需要定位动画系统的性能瓶颈**：例如，某个角色在特定动画状态下帧率下降。通过 Animation Insights，你可以查看动画图的执行时间线、混合节点的权重变化，快速找到最耗时的动画节点或混合逻辑。
-   **你需要调试复杂的动画图逻辑**：当动画状态机状态切换错误或混合行为不符合预期时，使用 Rewind Debugger 回溯到问题发生的时刻，检查动画图中每个节点的输入输出值、连接关系和状态机状态。
-   **你需要分析骨骼网格体姿态的变化**：追踪骨骼网格体的组件空间姿态、曲线值（如 Morph 目标）和动画通知的触发情况，用于调试动画瑕疵或实现精确的动画同步。
-   **你需要在多玩家或复杂场景中调试动画**：插件支持按对象、世界进行数据追踪和筛选，可以在充满各种动画角色的场景中，精确地聚焦于你关心的那个角色或动画实例。

## 蓝图用法

此插件主要是一个**编辑器运行时工具**，其核心功能通过 Unreal Insights UI 提供，而非暴露给游戏蓝图逻辑。它提供的蓝图/C++接口主要用于控制追踪行为。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Enable Object Property Trace` | 启用或禁用对特定 UObject 属性的追踪 | `IGameplayInsightsModule` |
| `Is Object Property Trace Enabled` | 查询某个 UObject 是否启用了属性追踪 | `IGameplayInsightsModule` |
| `Start Trace` | 手动开始一次数据追踪（需配合 Unreal Insights 使用） | `IGameplayInsightsModule` |

**注意**：这些功能需要在编辑器环境下，通过获取 `IGameplayInsightsModule` 模块实例来调用，通常用于开发工具或测试脚本中，而不是在游戏运行时蓝图里。

### 使用示例（蓝图描述）

由于主要功能在编辑器工具面板中，蓝图层面的使用较少。一个典型的用法是，在编辑器工具中，通过 C++ 获取 `IGameplayInsightsModule`，然后调用 `EnableObjectPropertyTrace` 来为特定的动画组件开启属性追踪，以便在 Insights 中观察其详细状态。

## C++ 用法

该插件的 C++ 用法主要围绕**访问和分析 Insights 记录的数据**，通常用于编写自定义的分析器或扩展 Insights 视图。

### 头文件引入

```cpp
#include "IGameplayProvider.h"
#include "IAnimationProvider.h"
```

### 基本用法

从分析会话中获取 Provider 以读取追踪数据。

```cpp
// 获取已录制的分析会话（通常在 Insights 插件或自定义分析器上下文中）
const TraceServices::IAnalysisSession& Session = /* ... */;

// 获取动画数据提供者
const IAnimationProvider* AnimationProvider = ReadAnimationProvider(Session);
if (AnimationProvider)
{
    // 在读取数据前，需要开始读锁
    FAnalysisSessionReadScope ReadScope(Session);

    // 遍历所有记录了骨骼网格体姿态的对象
    AnimationProvider->EnumerateSkeletalMeshPoseTimelines([&](uint64 ObjectId, const IAnimationProvider::SkeletalMeshPoseTimeline& Timeline)
    {
        // 对每个对象，读取其姿态时间线
        AnimationProvider->ReadSkeletalMeshPoseTimeline(ObjectId, [&](const IAnimationProvider::SkeletalMeshPoseTimeline& PoseTimeline, bool bIsTickTimeline)
        {
            // 处理该对象的所有姿态帧
            for (auto It = PoseTimeline.CreateIterator(); It; ++It)
            {
                const FSkeletalMeshPoseMessage& PoseMessage = It.GetValue();
                // ... 处理姿态数据，例如获取变换
                FTransform ComponentToWorld;
                TArray<FTransform> BoneTransforms;
                if (const FSkeletalMeshInfo* MeshInfo = AnimationProvider->FindSkeletalMeshInfo(PoseMessage.MeshId))
                {
                    AnimationProvider->GetSkeletalMeshComponentSpacePose(PoseMessage, *MeshInfo, ComponentToWorld, BoneTransforms);
                    // 现在你可以使用 ComponentToWorld 和 BoneTransforms
                }
            }
        });
    });
}
```
*来源：基于 `IAnimationProvider.h` 和 `AnimationProvider.h` 中的接口设计。*

### 进阶用法

结合 `IGameplayProvider` 获取对象信息，并分析动画图状态。

```cpp
const TraceServices::IAnalysisSession& Session = /* ... */;
const IGameplayProvider* GameplayProvider = /* 从 Session 获取 */;
const IAnimationProvider* AnimationProvider = ReadAnimationProvider(Session);

if (GameplayProvider && AnimationProvider)
{
    FAnalysisSessionReadScope ReadScope(Session);

    // 遍历所有记录的对象
    GameplayProvider->EnumerateObjects([&](const FObjectInfo& ObjectInfo)
    {
        // 检查是否是骨骼网格体组件
        if (GameplayProvider->IsSubClassOf(ObjectInfo.ClassId, USkeletalMeshComponent::StaticClass()->GetClassId()))
        {
            uint64 ObjectId = ObjectInfo.GetId().GetMainId();

            // 读取该对象的动画图时间线
            AnimationProvider->ReadAnimGraphTimeline(ObjectId, [&](const IAnimationProvider::AnimGraphTimeline& AnimGraphTimeline)
            {
                for (auto It = AnimGraphTimeline.CreateIterator(); It; ++It)
                {
                    const FAnimGraphMessage& AnimGraphMessage = It.GetValue();
                    UE_LOG(LogTemp, Log, TEXT("Object %llu: AnimGraph phase %d with %d nodes at time %f"),
                        ObjectId,
                        static_cast<int32>(AnimGraphMessage.Phase),
                        AnimGraphMessage.NodeCount,
                        It.GetStartTime());
                }
            });
        }
    });
}
```
*来源：基于 `IGameplayProvider.h` 和 `IAnimationProvider.h` 的组合使用。*

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何获取 Provider 并遍历动画图数据。此代码可作为编辑器工具或分析模块的一部分。

**AnimationInsightsDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class FAnimationInsightsDemo
{
public:
    static void DemoAnalyzeAnimGraph(const TraceServices::IAnalysisSession& Session);
};
```

**AnimationInsightsDemo.cpp**
```cpp
#include "AnimationInsightsDemo.h"
#include "IAnimationProvider.h"
#include "IGameplayProvider.h"
#include "GameplayTraceModule.h" // 用于 ReadAnimationProvider

void FAnimationInsightsDemo::DemoAnalyzeAnimGraph(const TraceServices::IAnalysisSession& Session)
{
    // 获取动画数据提供者
    const IAnimationProvider* AnimProvider = ReadAnimationProvider(Session);
    const IGameplayProvider* GameProvider = TraceServices::ReadProvider<IGameplayProvider>(Session, TEXT("Gameplay"));

    if (!AnimProvider || !GameProvider)
    {
        UE_LOG(LogTemp, Warning, TEXT("Animation Insights providers not available."));
        return;
    }

    // 创建读作用域
    FAnalysisSessionReadScope ReadScope(Session);

    // 找到第一个骨骼网格体组件对象并分析其动画图
    bool bFound = false;
    GameProvider->EnumerateObjects([&](const FObjectInfo& ObjectInfo)
    {
        if (bFound) return;
        if (GameProvider->IsSubClassOf(ObjectInfo.ClassId, USkeletalMeshComponent::StaticClass()->GetClassId()))
        {
            uint64 ObjectId = ObjectInfo.GetId().GetMainId();

            // 尝试读取动画图时间线
            AnimProvider->ReadAnimGraphTimeline(ObjectId, [&](const IAnimationProvider::AnimGraphTimeline& Timeline)
            {
                if (Timeline.GetEventCount() > 0)
                {
                    UE_LOG(LogTemp, Log, TEXT("Found AnimGraph data for object: %s (ID: %llu)"), ObjectInfo.Name, ObjectId);
                    bFound = true;

                    // 可以在这里深入分析 Timeline 中的每个 FAnimGraphMessage
                }
            });
        }
    });

    if (!bFound)
    {
        UE_LOG(LogTemp, Log, TEXT("No object with AnimGraph data found in this trace session."));
    }
}
```

## 模块依赖

要使用此插件的功能，你的模块通常不需要直接依赖它，因为它是分析工具。但若要**扩展**其功能或访问其 Provider，则需要依赖以下模块。

| 模块 | 用途 |
|---|---|
| `TraceAnalysis` | 核心分析框架，用于解析 Insights 会话 |
| `TraceServices` | 提供 `IAnalysisSession`、`IProvider` 等基础服务 |
| `RewindDebugger` | 提供 `FRewindDebuggerTrack` 等用于构建回放调试器轨道的基类 |
| `InsightsCore` | Insights 工具的核心 UI 和功能 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `a3d17a57` | fix Rewind Debugger eyedropper to cancel when reattaching player control while it's active | 修复回放调试器吸管工具在玩家控制重新附加时未能取消的问题 |
| 2026-05-13 | `ec80c6b8` | [RewindDebugger] Add programmable scrub and view-centring surface on `IRewindDebugger`. | 为 `IRewindDebugger` 接口添加可编程的擦洗和视图居中表面 |
| 2026-04-28 | `7805b240` | Rewind Debugger toolbar UX pass. | 对回放调试器的工具栏进行用户体验优化 |
| 2026-04-15 | `4b250a9d` | [RewindDebugger] | 对回放调试器进行改进 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移到 UE_LOGF |

### 维护评价

**活跃维护**。该插件仍在持续更新和改进中，最近的更新集中在2026年4月和5月，主要针对其核心组件 **Rewind Debugger** 进行功能增强和问题修复。这表明 Epic Games 仍在积极投入开发，将其作为动画调试工作流中的重要工具。

-   **优势**：功能强大且深度集成于 Unreal Insights 和 Rewind Debugger，是 Epic 官方支持的动画性能分析和调试解决方案。
-   **注意事项**：默认未启用 (`EnabledByDefault: false`)，需要开发者手动启用。它是一个开发/调试工具，而非游戏运行时功能。文档和示例较少，需要一定的 Insights 和动画系统知识才能有效使用。
-   **推荐**：强烈推荐给所有需要进行**动画性能优化**或**复杂动画逻辑调试**的团队。它是解决深层次动画问题的利器。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/GameplayInsights)
-   [官方文档](https://docs.unrealengine.com/) (需搜索 `Animation Insights` 或 `Rewind Debugger`)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/GameplayInsights/Tests)

---

# 子模块文档

由于此插件规模较大（`large`），包含多个模块，因此为其每个主要子模块生成独立的文档页。

## 子模块列表

-   [GameplayInsights 核心模块](./GameplayInsights.md) - 数据追踪与分析的核心逻辑
-   [GameplayInsightsEditor 模块](./GameplayInsightsEditor.md) - 编辑器集成与UI扩展
-   [RewindDebugger 模块](./RewindDebugger.md) - 回放调试器框架与基础轨道
-   [RewindDebuggerRuntime 模块](./RewindDebuggerRuntime.md) - 运行时数据追踪支持
-   [RewindDebuggerVLog 模块](./RewindDebuggerVLog.md) - 可视化日志集成
-   [RewindDebuggerVLogRuntime 模块](./RewindDebuggerVLogRuntime.md) - 可视化日志运行时支持