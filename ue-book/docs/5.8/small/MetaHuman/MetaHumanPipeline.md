# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman动画器 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（代码、资产、配置） |
| 模块 | `MetaHumanPipeline` (Runtime), 等共27个模块 |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 未知 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的 MetaHuman 动画工具套件。它并非一个单一的工具，而是一个**可扩展的管线系统**，专为将各种输入数据（如 iPhone 原深感摄像头视频、语音音频、立体相机视频）转换为高质量的 MetaHuman 面部动画而设计。

该插件的核心价值在于提供了一个**模块化、可组合的框架**。它将复杂的面部动画处理流程分解为多个独立的“节点”（Node），例如面部追踪节点（`FFaceTrackerNode`）、语音转动画节点（`FSpeechToAnimNode`）、深度生成节点（`FDepthGenerateNode`）等。开发者可以像搭积木一样，将这些节点通过管线（`FPipeline`）连接起来，构建定制化的动画处理流水线。

它解决了从原始媒体文件到最终可用于驱动 MetaHuman 角色骨骼的动画数据（Controls）之间的完整处理链条问题，是 MetaHuman 生态中处理“动”的核心组件。

## 使用场景

- **电影级面部动捕动画**：你使用专业的立体摄像机或 iPhone 拍摄了演员的面部表演，需要将其转换为精确的 MetaHuman 动画。
- **语音驱动面部动画**：你只有一段音频文件，希望自动生成对应的口型和面部表情动画。
- **iPhone 原深感摄像头面部动画**：你使用 iPhone 的 TrueDepth 摄像头拍摄了视频，需要提取其中的面部运动数据。
- **自定义动画处理流程**：作为技术美术或引擎程序员，你需要对标准的面部追踪或动画解算流程进行修改或扩展，以满足特定项目的需求。

## 蓝图用法

该插件的**核心功能是通过 C++ 实现的**，主要提供了一系列用于构建动画处理管线的节点类。在蓝图层面，它主要通过编辑器工具（如 MetaHuman Animator 编辑器窗口）来使用，而非直接暴露用于蓝图图表的简单函数节点。

用户与该插件的主要交互是通过 UE 编辑器中 MetaHuman Animator 面板完成的，该面板封装了复杂的管线操作。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanPipeline/Public/Nodes/FaceTrackerNode.h"
#include "MetaHumanPipeline/Public/Nodes/SpeechToAnimNode.h"
#include "MetaHumanPipeline/Public/Nodes/AsyncNode.h"
```

### 基本用法：自定义管线节点

该插件的使用主要是**继承或使用现有的管线节点**。下面是一个基于测试用例 (`TestNodes.h`) 的简单自定义节点示例，它接收一个整数并将其递增。

**来源文件：** `Source/MetaHumanPipeline/Private/Nodes/TestNodes.h`

```cpp
// MyIncrementNode.h
#pragma once
#include "MetaHumanPipeline/Public/Nodes/Node.h" // 假设 FNode 定义在此

namespace UE::MetaHuman::Pipeline
{
    class FMyIncrementNode : public FNode
    {
    public:
        FMyIncrementNode(const FString& InName) : FNode("MyIncrement", InName)
        {
            // 定义输入输出引脚类型
            Pins.Add(FPin("InputInt", EPinDirection::Input, EPinType::Int));
            Pins.Add(FPin("OutputInt", EPinDirection::Output, EPinType::Int));
        }

        // 处理每一帧数据的核心函数
        virtual bool Process(const TSharedPtr<FPipelineData>& InPipelineData) override
        {
            // 从管线数据中获取输入值
            int32 InputValue = InPipelineData->GetData<int32>(Pins[0]);
            
            // 执行处理逻辑
            int32 OutputValue = InputValue + 1;
            
            // 将结果设置回管线数据
            InPipelineData->SetData<int32>(Pins[1], OutputValue);
            
            return true; // 处理成功
        }
    };
}
```

### 进阶用法：使用异步节点

对于计算密集型任务（如神经网络推理），可以使用 `FAsyncNode` 模板来将节点包装为可异步执行，避免阻塞主线程。

**来源文件：** `Source/MetaHumanPipeline/Public/Nodes/AsyncNode.h`

```cpp
// 使用现成的 HyprsenseNode 作为被包装的节点类型
// 创建一个包含 2 个内部节点实例的异步包装节点
TArray<TSharedPtr<UE::MetaHuman::Pipeline::FHyprsenseNode>> InternalNodes;
InternalNodes.Add(MakeShared<UE::MetaHuman::Pipeline::FHyprsenseNode>("Tracker1"));
InternalNodes.Add(MakeShared<UE::MetaHuman::Pipeline::FHyprsenseNode>("Tracker2"));

auto AsyncTrackerNode = MakeShared<UE::MetaHuman::Pipeline::FAsyncNode<UE::MetaHuman::Pipeline::FHyprsenseNode>>(
    2, // 异步节点数量
    "MyAsyncFaceTracker"
);

// 在管线中使用 AsyncTrackerNode，它会并行处理到来的数据帧
```

## Demo 示例

以下是一个最小、可编译的自定义节点示例，它将两个浮点数相加。

**MyFloatSumNode.h**
```cpp
#pragma once
#include "MetaHumanPipeline/Public/Nodes/Node.h"

namespace UE::MetaHuman::Pipeline
{
    class FMyFloatSumNode : public FNode
    {
    public:
        FMyFloatSumNode(const FString& InName);

        virtual bool Process(const TSharedPtr<FPipelineData>& InPipelineData) override;
    };
}
```

**MyFloatSumNode.cpp**
```cpp
#include "MyFloatSumNode.h"
#include "MetaHumanPipeline/Public/Nodes/PipelineData.h" // FPipelineData 定义

FMyFloatSumNode::FMyFloatSumNode(const FString& InName)
    : FNode("MyFloatSum", InName)
{
    Pins.Add(FPin("FloatA", EPinDirection::Input, EPinType::Float, 0));
    Pins.Add(FPin("FloatB", EPinDirection::Input, EPinType::Float, 1));
    Pins.Add(FPin("Sum", EPinDirection::Output, EPinType::Float));
}

bool FMyFloatSumNode::Process(const TSharedPtr<FPipelineData>& InPipelineData)
{
    if (!InPipelineData)
    {
        return false;
    }

    const float A = InPipelineData->GetData<float>(Pins[0]);
    const float B = InPipelineData->GetData<float>(Pins[1]);
    const float Result = A + B;

    InPipelineData->SetData<float>(Pins[2], Result);
    return true;
}
```

## 模块依赖

该插件的 `MetaHumanPipeline` 模块依赖于 `UnrealEd`，因为许多节点（如用于管理配置、与资产系统交互）需要编辑器功能。

要使用该插件的管线框架，你的模块可能需要依赖 `MetaHumanPipeline`。由于该插件主要提供处理框架和具体实现节点，其自身对 UE 核心模块（如 Core, Engine, NNE 等）有广泛依赖，但这些对于使用者来说通常是透明的。

| 模块 | 用途 |
|---|---|
| `MetaHumanPipeline` | 核心的动画处理管线框架和各种节点实现 |
| `NNE` (Neural Network Engine) | 为面部追踪等节点提供神经网络推理能力 |
| `ControlRigDeveloper` | 与 MetaHuman 的 Control Rig 骨骼控制联动 |

**注意**：以上依赖关系仅为 `MetaHumanPipeline` 模块的典型依赖。整个 MetaHuman Animator 插件包含 27 个模块，各自有特定的依赖关系。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 修复了在启用身体追踪时关卡序列导出功能可能失效的问题 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复了 MetaHuman 模型上可能存在的渲染伪影 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 优化了身体追踪时的可视化对象过滤，提升性能和清晰度 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 为已有网格体添加了动画序列导出功能 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复了 Sequencer（定序器）相关的缓存问题 |

### 维护评价

**维护状态：活跃维护中**。
-   **创建时间**：未知，但作为 MetaHuman 生态的核心组件，其发布与 UE5 MetaHuman 工具的推出时间接近。
-   **近期活动**：从 Git 历史看，在 **2026 年 5 月** 有非常高频的更新（几乎每天），且提交内容集中在功能增强（如新增导出功能）、bug 修复和性能优化上。
-   **建议**：该插件由 Epic Games 官方维护，是其旗舰 MetaHuman 工具链的一部分，**强烈推荐使用**。它持续获得更新以支持新的平台、硬件和工作流。用户应关注官方文档和引擎更新日志以获取最新特性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/animating-metahumans-in-unreal-engine/)（MetaHuman 动画总览页面，包含 Animator 的使用指引）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanPipeline/Private/Nodes/TestNodes.h)（管线节点的基础测试用例）