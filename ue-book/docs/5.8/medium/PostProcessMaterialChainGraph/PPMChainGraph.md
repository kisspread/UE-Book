# Post Process Material Chain Graph

> Post Process Material Chain Graph allows users to stack post process materials and render those into render targets separate from Scene Color.
This can operate on textures other than scene color without writing those into scene color.

| 属性 | 值 |
|---|---|
| 中文名 | 后处理材质链图 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（UMG 界面资产） |
| 模块 | `PPMChainGraph` (Runtime), `PPMChainGraphEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-27 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PostProcessMaterialChainGraph) | |

## 用途

该插件提供了一套**后处理材质链**系统，用于在标准后处理管线之外执行一系列材质。核心解决的问题是：

1.  **避免直接修改 Scene Color**：允许在中间步骤将结果写入临时渲染目标，而不是直接覆盖场景颜色。
2.  **支持多 Pass 纹理操作**：可以在一个链式流程中，将前一个 Pass 的输出（临时渲染目标）作为后续 Pass 的输入，实现复杂的多步骤图像处理。
3.  **灵活的执行时机控制**：允许将整个材质链安排在后处理管线的不同阶段执行（如运动模糊后、色调映射后等）。

这使得开发者可以实现非破坏性的、可组合的后处理效果链，例如在不修改原始场景颜色的情况下，先应用一个风格化滤镜，再将结果用于景深计算。

## 使用场景

*   你需要实现一个**复杂的、由多个独立后处理材质组合而成的自定义滤镜**，且不希望中间步骤污染最终场景颜色。
*   你需要对**非场景颜色的纹理**（如来自渲染目标的自定义数据）应用一系列后处理操作。
*   你需要在**后处理管线的特定阶段**（例如，在 FXAA 之后）插入一个自定义的材质处理流程。

## 蓝图用法

该插件通过**组件**和**资产**配合使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `UPPMChainGraph` (资产) | 定义后处理材质链的数据资产，包含执行位置、外部纹理和 Pass 列表。 | `UPPMChainGraph` |
| `Post Process Material Chain Graph Executor Component` | 场景组件，负责管理并执行一个或多个 `UPPMChainGraph`。 | `UPPMChainGraphExecutorComponent` |
| `Post Process Material Chain Graph Actor` | 一个方便放置的 Actor，内置了 `ExecutorComponent`。 | `APPMChainGraphActor` |

### 使用示例（蓝图描述）

1.  **创建数据资产**：
    *   在内容浏览器右键 -> `Miscellaneous` -> `Data Asset` -> 选择 `Post Process Material Chain Graph`。
    *   在资产编辑器中，设置 `Point of Execution`（如 “After Tonemap”）。
    *   在 `External Textures` 中可添加非场景颜色的纹理输入。
    *   在 `Passes` 数组中添加元素，每个元素代表一个后处理 Pass。为每个 Pass 指定要执行的 `PostProcessMaterial`，并配置 `Inputs`（将哪个输入映射到材质的哪个 Scene Texture 通道）和 `Output`（写入临时目标或场景颜色）。最后一个 Pass 通常输出到场景颜色。

2.  **放置执行器**：
    *   将 `APPMChainGraphActor` 拖入场景，或在任何 Actor 上添加 `UPPMChainGraphExecutorComponent`。
    *   在组件的 `Post Process Material Chain Graphs` 属性中，添加上一步创建的 `UPPMChainGraph` 资产。
    *   可选配置 `Camera View Settings` 以控制此效果仅在特定摄像机视图中生效。

## C++ 用法

### 头文件引入

```cpp
#include "PPMChainGraph.h"
#include "PPMChainGraphComponent.h"
```

### 基本用法

创建一个简单的后处理材质链图。

```cpp
// 1. 创建一个 Graph 对象（通常在某个管理器或组件中持有）
UPPMChainGraph* MyGraph = NewObject<UPPMChainGraph>();
MyGraph->PointOfExecution = EPPMChainGraphExecutionLocation::AfterToneMap;

// 2. 定义一个 Pass
FPPMChainGraphPostProcessPass& FirstPass = MyGraph->Passes.AddDefaulted_GetRef();
FirstPass.bEnabled = true;
FirstPass.PostProcessMaterial = MyEffectMaterial; // 你的后处理材质
FirstPass.Output = EPPMChainGraphOutput::PPMOutput_RenderTarget;
FirstPass.TemporaryRenderTargetId = TEXT("IntermediateBuffer");

// 将材质的 `PostProcessInput0` 输入连接到前一个结果（此处为场景颜色）
FPPMChainGraphInput& InputMapping = FirstPass.Inputs.Add(EPPMChainGraphPPMInputId::PPMInputMaping_0);
InputMapping.InputId = TEXT("SceneColor");

// 3. 将 Graph 赋予执行器组件
// （通常在组件的初始化或蓝图的 BeginPlay 中）
// PPMChainGraphExecutorComponent->PPMChainGraphs.Add(MyGraph);
```

（概念性代码，展示配置流程）

### 进阶用法

实现一个多 Pass 链，Pass 之间传递数据。

```cpp
// 定义第二个 Pass，其输入来自第一个 Pass 的输出
FPPMChainGraphPostProcessPass& SecondPass = MyGraph->Passes.AddDefaulted_GetRef();
SecondPass.PostProcessMaterial = AnotherMaterial;
SecondPass.Output = EPPMChainGraphOutput::PPMOutput_SceneColor; // 最终写回场景颜色

// 将此 Pass 的输入映射到第一个 Pass 输出的临时渲染目标
FPPMChainGraphInput& PassInput = SecondPass.Inputs.Add(EPPMChainGraphPPMInputId::PPMInputMaping_1);
PassInput.InputId = TEXT("IntermediateBuffer"); // 与第一个 Pass 的 TemporaryRenderTargetId 对应

// 添加一个外部纹理作为额外输入
MyGraph->ExternalTextures.Add(TEXT("NoiseTexture"), MyNoiseTextureAsset);
// 并在某个 Pass 的 Inputs 中通过 InputId 引用它
```

（概念性代码，展示链式数据流）

## Demo 示例

```cpp
// MyPPMChainActor.h
#pragma once
#include "CoreMinimal.h"
#include "PPMChainGraphActor.h"
#include "MyPPMChainActor.generated.h"

UCLASS()
class AMyPPMChainActor : public APPMChainGraphActor
{
    GENERATED_BODY()
public:
    virtual void BeginPlay() override;
};

// MyPPMChainActor.cpp
#include "MyPPMChainActor.h"
#include "PPMChainGraph.h"

void AMyPPMChainActor::BeginPlay()
{
    Super::BeginPlay();

    if (PPMChainGraphExecutorComponent)
    {
        // 创建一个简单的 Graph 用于演示
        UPPMChainGraph* DemoGraph = NewObject<UPPMChainGraph>(this);
        DemoGraph->PointOfExecution = EPPMChainGraphExecutionLocation::AfterToneMap;

        FPPMChainGraphPostProcessPass& Pass = DemoGraph->Passes.AddDefaulted_GetRef();
        Pass.PostProcessMaterial = LoadObject<UMaterial>(nullptr, TEXT("/Game/Materials/M_InvertColor.M_InvertColor"));
        Pass.Output = EPPMChainGraphOutput::PPMOutput_SceneColor;

        PPMChainGraphExecutorComponent->PPMChainGraphs.Add(DemoGraph);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 运行时模块 `PPMChainGraph` 依赖于编辑器模块，可能用于序列化或资产编辑支持。 |
| `PPMChainGraph` | `PPMChainGraphEditor` 模块的核心运行时依赖。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `5c7314c3` | Fix Color Correct Regions render rect being truncated when dynamic resolution scales below 1.0. | 修复了动态分辨率低于1.0时，颜色校正区域的渲染矩形被截断的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志系统宏从 UE_LOG 迁移到 UE_LOGF。 |
| 2026-01-07 | `57ff2f55` | Deprecate legacy GPU profiler related macros. | 废弃了旧的 GPU 性能分析器相关宏。 |
| 2025-02-18 | `8c3ee882` | PPMChainGraph: Export public classes & structs, per third-party request. | 根据第三方请求，导出了公共类和结构体。 |
| 2025-02-13 | `ec3fb596` | Replaced `IsValid(this)` under the rest of Engine/. | 在引擎其他部分替换了 `IsValid(this)` 的用法。 |

### 维护评价

该插件于 2024 年初创建，处于**实验性阶段**。从 git 历史看，最近一次实质性功能更新（导出 API）发生在 2025 年 2 月。后续的提交均为引擎级别的维护性改动（如日志迁移、宏废弃），而非针对此插件的功能增强或 Bug 修复。这意味着插件核心功能已稳定，但**没有活跃的功能开发**。作为实验性特性，它的 API 和行为未来可能发生变化。

**建议**：仅在原型开发或明确需要该特性的场景中使用，并留意其未来可能被移除或重大修改的风险。在生产环境中使用前需进行充分评估。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PostProcessMaterialChainGraph)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/PostProcessMaterialChainGraph)