# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | 动画师工具 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-04-07 |
| 年龄标签 | 👴 老古董（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games MetaHuman 数字人系统的核心动画制作与驱动工具集。它不仅仅是一个单一插件，而是一套完整的管线（Pipeline），旨在解决从原始面部捕捉数据（如视频、音频）到驱动高保真 MetaHuman 面部动画的全流程问题。

其核心价值在于：
1.  **数据处理管线**：将各种来源的捕捉数据（iPhone 原深感摄像头、立体摄影机、音频等）转化为可用于驱动数字人面部的标准化数据。
2.  **面部求解（Solve）**：包含先进的面部追踪（Contour Tracking）、网格拟合（Fitting）和动画求解（Animation Solver）算法，能够从 2D 视频或 3D 网格序列中提取出精确的面部肌肉运动。
3.  **动画转换与驱动**：将求解出的面部动画数据（如 Solve Controls）转换并映射到 MetaHuman 骨骼的 Control Rig 控制器上，实现最终动画效果。
4.  **编辑器集成与批处理**：提供完整的编辑器工具（如 Identity、Performance、Pipeline 等资产类型）以及批量处理功能，支持非破坏性、可迭代的动画制作流程。

简而言之，该插件为开发者和艺术家提供了一套工业级的解决方案，用于创建极其逼真、基于真实演员表演的 MetaHuman 面部动画。

## 使用场景

-   **影视与过场动画制作**：为游戏或影视作品中的高保真角色制作基于演员表演的面部动画，替代传统手K或昂贵的动作捕捉。
-   **虚拟偶像/直播**：实时或准实时地将表演者的面部表情驱动到虚拟形象上。
-   **高质量数字人项目**：任何需要创建逼真数字人并为其赋予生动表情的项目，如虚拟客服、数字孪生等。
-   **动画预览与迭代**：快速将拍摄的参考视频转换为角色动画，用于早期创意验证和动画风格探索。

## 蓝图用法

由于该插件主要提供编辑器资产处理管线和后台求解算法，其核心功能通常通过 **编辑器资产（如 `UPipeline`、`UPerformance`）** 和 **自定义资产编辑器（如 UAssetDefinition_MHPipeline）** 来驱动，而非直接暴露大量 `BlueprintCallable` 函数。

主要的用户交互发生在 Unreal Editor 的自定义资产编辑器和操作按钮中。以下是一些关键的编辑器交互概念（非直接蓝图节点）：

### 核心资产与工作流

| 概念 | 说明 |
|---|---|
| `UMetaHumanIdentity` | 身份资产，用于定义角色的基础面部网格和纹理，是动画驱动的基础。 |
| `UMetaHumanPerformance` | 表演资产，代表一次具体的面部捕捉表演数据（视频/图像序列）。 |
| `UMetaHumanPipeline` (或 `UMHPipeline`) | 管线资产，定义了从“表演”到“动画”的完整处理流程，包括追踪、求解、转换等步骤。 |
| `UMetaHumanCaptureData` | 捕获数据资产，封装原始的视频帧或深度数据。 |

### 使用流程（编辑器描述）

1.  **创建身份（Identity）**：在内容浏览器中右键创建 `MetaHuman Identity` 资产。打开后，导入或指定角色的基础面部 Mesh（通常是 MetaHuman 的模板 Mesh）。
2.  **导入表演（Performance）**：创建 `MetaHuman Performance` 资产。通过其编辑器导入 iPhone 原深感摄像头录制的 `.mlv` 文件或其他格式的图像序列。
3.  **创建与配置管线（Pipeline）**：创建 `MetaHuman Pipeline` 或类似资产（如 `UMHPipeline`）。在其编辑器中，将“身份”和“表演”资产作为输入。
4.  **运行管线**：在管线编辑器中点击处理按钮。插件会在后台依次运行面部追踪、网格拟合、动画求解等模块。
5.  **查看与导出结果**：处理完成后，可以在性能或管线资产中预览求解出的面部动画。最终可以将动画数据导出为关卡序列（Level Sequence）或直接应用到场景中的 MetaHuman 角色上。

## C++ 用法

本节侧重于从提供的测试代码 `MetaHumanControlsConversionTest` 模块推断出的核心数据转换逻辑。这代表了管线中“动画求解”输出到“骨骼控制”输入的关键一步。

### 头文件引入

使用该功能通常需要包含求解器或转换模块的头文件。
```cpp
#include "MetaHumanFaceAnimationSolver.h"
#include "MetaHumanFaceFittingSolver.h"
// 或包含管线相关头文件，如 MetaHumanPipeline.h
```

### 基本用法：理解控制转换

`MetaHumanControlsConversionTest` 模块的测试数据揭示了核心的数据结构：**Solve Controls** 和 **Rig Controls**。

**Solve Controls**：这是面部求解器（Face Animation Solver）输出的中间数据，键名格式为 `CTRL_{区域}_{动作}.{轴}`，例如 `CTRL_L_brow_down.ty`。它表示特定面部肌肉区域在特定轴向上的运动幅度。

**Rig Controls**：这是最终用于驱动 MetaHuman 骨骼控制器的数值，键名格式为 `CTRL_expressions_{动作}{左右}`，例如 `CTRL_expressions_browDownL`。它对应于 Control Rig 中的属性。

**转换逻辑**：插件内部包含一个转换映射或函数，将 Solve Controls 映射到 Rig Controls。例如，输入 `CTRL_L_brow_down.ty` 的值 `0.1966f`，会被转换并赋值给输出 `CTRL_expressions_browDownL`。

```cpp
// 概念性代码，展示数据流（非实际API）
// 假设通过某个求解器或转换器实例获取数据
FSolveControlsData SolveOutput = AnimationSolver->GetSolveControls();
FRigControlsData RigInput;
ConversionUtils::ConvertSolveToRig(SolveOutput, RigInput);
// RigInput 现在包含了可以直接应用到骨骼控制器的值。
```

### 进阶用法：使用测试数据验证转换

测试模块 `MetaHumanControlsConversionTest` 提供了具体的输入（`InputSolveControls`）和预期的输出（`ExpectedRigControls`）。这可用于验证你的转换逻辑是否正确。

```cpp
// 来源：Private/Tests/ControlsTestData.h
#include "Tests/ControlsTestData.h"

void VerifyConversionAccuracy(const TMap<FString, float>& InActualRigControls)
{
    const TMap<FString, float>& Expected = SolveControlsTestData::ExpectedRigControls;
    for (const auto& ExpectedPair : Expected)
    {
        if (const float* ActualValue = InActualRigControls.Find(ExpectedPair.Key))
        {
            // 比较实际值与期望值（需考虑浮点精度）
            bool bMatch = FMath::IsNearlyEqual(*ActualValue, ExpectedPair.Value, 0.001f);
            // 根据 bMatch 记录结果或断言
        }
    }
}
```

## Demo 示例

以下是一个极简的示例，概念性地展示了如何访问 MetaHuman 的动画求解数据结构并读取面部控制值。请注意，这更多是数据消费端的演示，实际启动求解管线通常通过编辑器资产操作。

**MetaHumanAnimationDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MetaHumanAnimationDemo.generated.h"

UCLASS()
class MYPROJECT_API AMetaHumanAnimationDemo : public AActor
{
    GENERATED_BODY()

public:
    AMetaHumanAnimationDemo();

    // 概念性函数：获取当前面部控制值
    UFUNCTION(BlueprintCallable, Category = "MetaHuman Demo")
    float GetBrowDownControl(bool bLeftSide) const;

    // 概念性函数：设置面部控制值（用于手动测试或简单驱动）
    UFUNCTION(BlueprintCallable, Category = "MetaHuman Demo")
    void SetBrowDownControl(bool bLeftSide, float Value);

protected:
    virtual void BeginPlay() override;

private:
    // 存储面部控制值的映射（概念性）
    TMap<FString, float> CurrentSolveControls;
};
```

**MetaHumanAnimationDemo.cpp**
```cpp
#include "MetaHumanAnimationDemo.h"

AMetaHumanAnimationDemo::AMetaHumanAnimationDemo()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMetaHumanAnimationDemo::BeginPlay()
{
    Super::BeginPlay();

    // 初始化一些测试数据（类似 ControlsTestData.h 中的数据）
    CurrentSolveControls.Add(TEXT("CTRL_L_brow_down.ty"), 0.0f);
    CurrentSolveControls.Add(TEXT("CTRL_R_brow_down.ty"), 0.0f);
    // ... 初始化其他控制
}

float AMetaHumanAnimationDemo::GetBrowDownControl(bool bLeftSide) const
{
    FString Key = bLeftSide ? TEXT("CTRL_L_brow_down.ty") : TEXT("CTRL_R_brow_down.ty");
    if (const float* Value = CurrentSolveControls.Find(Key))
    {
        return *Value;
    }
    return 0.0f;
}

void AMetaHumanAnimationDemo::SetBrowDownControl(bool bLeftSide, float Value)
{
    FString Key = bLeftSide ? TEXT("CTRL_L_brow_down.ty") : TEXT("CTRL_R_brow_down.ty");
    if (CurrentSolveControls.Contains(Key))
    {
        CurrentSolveControls[Key] = Value;
        // 在实际应用中，这里可能需要触发将新值应用到MetaHuman角色的逻辑。
        // 这通常涉及将SolveControls转换为RigControls，然后驱动ControlRig。
    }
}
```

## 模块依赖

该插件自身模块众多且相互依赖。如果你的项目模块需要与 MetaHuman Animator 的特定子系统交互（例如，编写自定义求解器或访问管线数据），你需要在你的 `.Build.cs` 中添加相应的依赖。

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | MetaHuman 核心算法库，包含面部求解、追踪等底层技术。多个模块（如 `MetaHumanConfig`, `MetaHumanFaceAnimationSolver`）都依赖它。 |
| `ControlRig` | 用于构建和驱动 MetaHuman 的骨骼控制器（Control Rig）。 |
| `LiveLink` | 实时链接表演数据（可选）。 |
| `SkeletalMeshUtilitiesCommon` | 用于处理骨骼网格体的通用工具。 |
| `MediaUtils`, `ImageWriteQueue` | 用于处理媒体文件（视频、图像）的输入输出。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用全身追踪时，禁用关卡序列导出功能。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 角色上的渲染瑕疵。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 当进行全身追踪时，过滤可视化调试对象。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MHA] 支持为已存在的网格体导出动画序列。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存相关问题。 |

### 维护评价

MetaHuman Animator 是 Epic Games 官方维护的**核心产品插件**，活跃度非常高。从近期提交历史可以看出，团队在持续进行功能增强（如新增为已有网格体导出动画的功能）和稳定性修复（渲染瑕疵、缓存问题）。

- **创建时间**：约 4 年（根据首次提交记录 2022-04-07）。
- **维护频率**：非常活跃，每周甚至每天都有更新。
- **维护状态**：**活跃维护中**，是 MetaHuman 工具链的关键组成部分。
- **已知限制**：由于是复杂的多模块管线，配置和使用门槛较高，通常需要遵循官方文档的详细步骤。对硬件（如 iPhone 原深感摄像头）和软件环境（特定版本的捕捉应用）有一定要求。
- **推荐程度**：**强烈推荐**。对于任何涉及 MetaHuman 高保真面部动画的项目，这是必不可少的官方工具集。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/meta-human-animator-in-unreal-engine/) （注意：由于 .uplugin 的 DocsURL 为空，此链接为 Epic 官网通用的 MetaHuman Animator 文档地址）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanControlsConversionTest/Private/Tests) （当前模块的测试数据所在目录）