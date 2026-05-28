# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 元人动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（管线节点、追踪器、动画工具） |
| 模块 | `MetaHumanPipeline` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 约 2023 年 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 MetaHuman 工具包的官方运行时组件，核心是提供了一个灵活、可扩展的数据处理管道（Pipeline）框架。该模块本身不直接实现面部追踪或动画生成，而是定义了如何将各个独立的处理步骤（如面部追踪、深度生成、光流计算、语音转动画等）组合成一个连贯的数据处理流程。

它的存在是为了解决从原始数据（如视频、深度图像、音频）到最终可用于驱动 MetaHuman 角色的动画数据之间的自动化、可配置处理流程构建问题。开发者和艺术家可以通过连接不同的处理节点（Node）来创建定制化的数据处理流水线。

## 使用场景

- **从 iPhone/双目视频创建面部动画**：构建一个包含 `FFaceTrackerIPhoneNode` 或 `FFaceTrackerStereoNode` 的管道，处理视频输入，输出面部追踪数据。
- **基于音频生成面部动画**：使用 `FSpeechToAnimNode` 节点，将音频文件（USoundWave）作为输入，直接生成驱动 MetaHuman 面部的动画曲线。
- **批量处理面部动画**：结合 `FAsyncNode` 和 `FBatchProcessor` 等机制，高效地处理大量视频或音频文件，生成动画资产。
- **自定义处理流程**：你可以继承 `FNode`，创建自己的处理节点，例如加入独特的滤镜、数据修正或与其他系统（如物理模拟）集成的逻辑。

## 蓝图用法

此模块（`MetaHumanPipeline`）主要提供 C++ 层面的管道构建能力，并未暴露直接在蓝图中使用的节点。实际的蓝图工具（如 `MetaHumanPerformance` 或编辑器工具）会使用此模块作为后端来执行处理。

## C++ 用法

### 头文件引入

要使用管道系统和内置节点，你需要包含相应的头文件。
```cpp
#include "Nodes/FaceTrackerNode.h"
#include "Nodes/SpeechToAnimNode.h"
#include "Nodes/HyprsenseNode.h"
// 其他节点头文件根据需要引入
```

### 基本用法

管道的基本单元是 `FNode`。每个节点通过 `FPipelineData` 对象接收输入数据，进行处理后，将结果通过 `FPipelineData` 传递给下一个节点。以下是一个简化示例，演示如何使用内置节点。

```cpp
// 示例：创建一个 iPhone 面部追踪节点并设置参数
// （来源：基于 FaceTrackerNode.h 的接口推断）
void SetupFaceTrackingPipeline()
{
    // 创建一个 iPhone 面部追踪节点
    TSharedPtr<UE::MetaHuman::Pipeline::FFaceTrackerIPhoneNode> FaceTrackerNode =
        MakeShared<UE::MetaHuman::Pipeline::FFaceTrackerIPhoneNode>(TEXT("MyFaceTracker"));
    
    // 配置节点参数
    FaceTrackerNode->SolverConfigData = TEXT("/Path/To/SolverConfig.json");
    FaceTrackerNode->DNAReader = LoadDNAReader(); // 假设有一个函数加载DNA
    FaceTrackerNode->Calibrations = GetCameraCalibrations(); // 获取相机标定数据
    FaceTrackerNode->Camera = TEXT("Front");
    FaceTrackerNode->NumberOfFrames = 100;
    
    // 在管道的某个阶段使用这个节点
    // ... (在实际的 FGraph 或 FTask 管理中使用)
}
```

### 进阶用法

你可以创建自定义节点，并将其集成到管道中。下面是一个最简单的自定义节点示例，它将接收到的整数加1后输出。

```cpp
// 定义自定义节点（来源：基于 TestNodes.h 的 FIntIncNode 模式）
class FMyCustomIncNode : public UE::MetaHuman::Pipeline::FNode
{
public:
    FMyCustomIncNode(const FString& InName) 
        : FNode("MyCustomInc", InName)
    {
        // 定义输入和输出引脚
        Pins.Add(FPin("Input", EPinDirection::Input, EPinType::Int));
        Pins.Add(FPin("Output", EPinDirection::Output, EPinType::Int));
    }

    virtual bool Process(const TSharedPtr<FPipelineData>& InPipelineData) override
    {
        // 从输入引脚获取数据
        const int32 InputValue = InPipelineData->GetData<int32>(Pins[0]);
        
        // 处理数据
        const int32 OutputValue = InputValue + 1;
        
        // 将结果设置到输出引脚
        InPipelineData->SetData<int32>(Pins[1], OutputValue);
        
        return true; // 返回 true 表示处理成功
    }
};

// 在管道中使用自定义节点
void UseCustomNodeInPipeline()
{
    TSharedPtr<FMyCustomIncNode> MyNode = MakeShared<FMyCustomIncNode>(TEXT("Incrementer"));
    // ... 将 MyNode 添加到管道图中，并与其他节点连接
}
```

## Demo 示例

以下是一个完整的、可编译的最小示例，演示如何创建一个简单的整数处理管道。

**CustomIncNode.h**
```cpp
// CustomIncNode.h
#pragma once

#include "CoreMinimal.h"
#include "Nodes/Node.h"

class FCustomIncNode : public UE::MetaHuman::Pipeline::FNode
{
public:
    FCustomIncNode(const FString& InName);

    virtual bool Process(const TSharedPtr<UE::MetaHuman::Pipeline::FPipelineData>& InPipelineData) override;
};
```

**CustomIncNode.cpp**
```cpp
// CustomIncNode.cpp
#include "CustomIncNode.h"
#include "PipelineData.h"

FCustomIncNode::FCustomIncNode(const FString& InName)
    : FNode("CustomInc", InName)
{
    // 定义输入输出引脚
    Pins.Add(FPin("ValueIn", EPinDirection::Input, EPinType::Int, 0));
    Pins.Add(FPin("ValueOut", EPinDirection::Output, EPinType::Int, 0));
}

bool FCustomIncNode::Process(const TSharedPtr<UE::MetaHuman::Pipeline::FPipelineData>& InPipelineData)
{
    // 获取输入的整数
    const int32 Value = InPipelineData->GetData<int32>(Pins[0]);
    
    // 处理（这里简单+1）
    const int32 NewValue = Value + 1;
    
    // 设置输出
    InPipelineData->SetData<int32>(Pins[1], NewValue);
    
    return true;
}
```

**UsageExample.cpp**
```cpp
// UsageExample.cpp (演示如何构建和运行一个极简管道)
#include "CustomIncNode.h"
#include "PipelineData.h"
#include "Graph.h" // 假设的管道图管理器

void RunSimplePipelineDemo()
{
    // 1. 创建节点
    TSharedPtr<FCustomIncNode> IncNode1 = MakeShared<FCustomIncNode>(TEXT("First"));
    TSharedPtr<FCustomIncNode> IncNode2 = MakeShared<FCustomIncNode>(TEXT("Second"));
    
    // 2. 假设有一个管道图管理器 FGraph
    UE::MetaHuman::Pipeline::FGraph PipelineGraph;
    
    // 3. 将节点添加到图中
    PipelineGraph.AddNode(IncNode1);
    PipelineGraph.AddNode(IncNode2);
    
    // 4. 连接节点（IncNode1 的输出连接到 IncNode2 的输入）
    PipelineGraph.Connect(IncNode1, 0, IncNode2, 0); // Pin Index 0
    
    // 5. 为第一个节点准备初始输入数据
    TSharedPtr<UE::MetaHuman::Pipeline::FPipelineData> InitialData = 
        MakeShared<UE::MetaHuman::Pipeline::FPipelineData>();
    InitialData->SetData<int32>(IncNode1->Pins[0], 10); // 输入初始值 10
    
    // 6. 执行管道（具体执行方式取决于管道图的实现）
    // PipelineGraph.Execute(InitialData);
    
    // 执行后，理论上 IncNode2 的输出引脚值应为 12 (10+1+1)
}
```

## 模块依赖

`MetaHumanPipeline` 模块依赖 `UnrealEd`，这是因为某些节点（如 `FSpeechToAnimNode`）在加载资产（如 `USoundWave`）时需要编辑器功能。对于运行时使用，这些依赖通常由宿主模块处理。

| 模块 | 用途 |
|---|---|
| `NNE` | 用于加载和运行神经网络模型（HyprSense 追踪器） |
| `ControlRig` | 用于最终的动画数据输出（通过其他上层模块） |
| `MediaUtils` | 用于处理视频、音频等媒体数据 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时，禁用关卡序列导出功能。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 角色的渲染伪影问题。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 在进行身体追踪时过滤掉调试可视化对象。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持为已有的 MetaHuman 网格体导出动画序列。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复了 Sequencer 中的缓存问题。 |

### 维护评价

**活跃维护**。
- 插件创建时间较新（约3年），属于 Epic Games 的官方 MetaHuman 工具链核心组件。
- 从最近的 git 记录来看，更新非常频繁（几乎每天），且内容涵盖**新功能添加**、**渲染/动画问题修复**以及**工作流改进**。
- 代码中存在 `UE_DEPRECATED(5.8, ...)` 标记，表明开发团队正在积极进行 API 清理和升级（例如将 NNE 模型从 `IModelInstanceGPU` 迁移到 `IModelInstanceRunSync`）。
- **强烈推荐使用**，但需注意其作为运行时管道框架的定位，上层的用户界面和便捷工具通常由 `MetaHumanPerformance` 等其他插件提供。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档]() (暂无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanPipeline/Private/Test) (推测路径，需根据实际情况确认)