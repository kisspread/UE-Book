# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | 元人类动画师 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（MetaHuman 核心技术库、动画与面部追踪工具、资产配置等） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是一个完整的官方工具套件，用于将真实的面部动作捕捉数据（视频、深度图、追踪点等）驱动 MetaHuman 角色模型。它解决的核心问题是将原始的、可能带有噪声的捕获数据，通过一系列解算器（如面部动画解算器、面部拟合解算器）转换为可用于驱动高质量数字人面部骨骼动画的资产。该插件是 MetaHuman 角色创建和动画工作流中数据驱动动画的核心部分。

## 使用场景

- 你使用 iPhone 或其他专业设备拍摄了演员的面部表演视频，并希望将其转换为 MetaHuman 角色的动画序列。
- 你需要调整面部动画解算的精细度，例如控制眼睛注视的平滑度或牙齿动画的驱动方式（基于追踪点或估算）。
- 你在开发一个需要实时或后期驱动高质量数字人面部的项目，例如影视预览、虚拟制片或游戏过场动画。
- 你需要批量处理多段捕获数据，将其转换为动画序列。

## 蓝图用法

`MetaHumanFaceAnimationSolver` 模块主要为 C++ 后端提供核心配置和数据生成逻辑，其蓝图暴露接口相对有限。更多用于驱动 MetaHuman 角色的蓝图节点（如播放捕获数据、应用动画）位于上层模块（如 `MetaHumanPerformance`，`MetaHumanSequencer`）中。`UMetaHumanFaceAnimationSolver` 本身是一个配置对象。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Solver Template Data` | 获取面部解算器的模板数据（JSON字符串） | `UMetaHumanFaceAnimationSolver` |
| `Get Solver Config Data` | 获取当前解算器的配置数据（JSON字符串） | `UMetaHumanFaceAnimationSolver` |
| `Can Process` | 检查解算器是否已准备好处理数据 | `UMetaHumanFaceAnimationSolver` |

### 使用示例（蓝图描述）

1.  在内容浏览器中右键创建或在蓝图中 spawn 一个 `MetaHumanFaceAnimationSolver` 资产。
2.  在其“细节”面板中，调整“参数”下的覆盖设置，如“深度图影响”、“眼睛解算平滑度”和“牙齿模式”。
3.  在需要生成解算配置的流程中（通常在更深的动画处理管线中），获取该 `UMetaHumanFaceAnimationSolver` 对象的引用，并调用 `Get Solver Config Data` 等节点，将返回的 JSON 字符串传递给底层的解算处理流程。

## C++ 用法

该模块的核心类 `UMetaHumanFaceAnimationSolver` 用于管理和生成面部动画解算所需的各种配置数据。

### 头文件引入

```cpp
#include "MetaHumanFaceAnimationSolver.h"
```

### 基本用法

创建一个解算器实例，并检查其配置是否有效。

```cpp
// 假设已经有了 UMetaHumanFaceAnimationSolver 的实例
UMetaHumanFaceAnimationSolver* Solver = NewObject<UMetaHumanFaceAnimationSolver>();

// 检查解算器是否就绪
if (Solver->CanProcess())
{
    // 获取当前配置的解算器定义数据
    FString SolverDefinitionsData = Solver->GetSolverDefinitionsData();
    // 此字符串可用于后续的解算流程
}
```

### 进阶用法

根据捕获数据动态获取合适的配置，并覆盖特定参数。

```cpp
// 获取与特定捕获数据关联的有效配置
UCaptureData* MyCaptureData = ...; // 从某处获取
FString SolverConfigData = Solver->GetSolverConfigData(MyCaptureData);

// 使用静态函数将配置设置为易于编辑的模式
FString EasyToEditConfig = UMetaHumanFaceAnimationSolver::SetEasyToEditControlConstraints(SolverConfigData);

// 覆盖特定参数
Solver->bOverrideDepthMapInfluence = true;
Solver->DepthMapInfluence = EDepthMapInfluenceValue::Low;
Solver->bOverrideEyeSolveSmoothness = true;
Solver->EyeSolveSmoothness = 0.5f;
```

## Demo 示例

一个演示如何配置并使用 `UMetaHumanFaceAnimationSolver` 生成配置数据的最小示例。

```cpp
// FaceAnimationSolverDemo.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MetaHumanFaceAnimationSolver.h"
#include "FaceAnimationSolverDemo.generated.h"

UCLASS()
class AFaceAnimationSolverDemo : public AActor
{
    GENERATED_BODY()

public:
    AFaceAnimationSolverDemo();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MetaHuman")
    TObjectPtr<UMetaHumanFaceAnimationSolver> Solver;

    UFUNCTION(BlueprintCallable, Category = "MetaHuman")
    FString GenerateSolverConfig();
};

// FaceAnimationSolverDemo.cpp
#include "FaceAnimationSolverDemo.h"

AFaceAnimationSolverDemo::AFaceAnimationSolverDemo()
{
    PrimaryActorTick.bCanEverTick = false;
    Solver = CreateDefaultSubobject<UMetaHumanFaceAnimationSolver>(TEXT("FaceAnimationSolver"));
}

FString AFaceAnimationSolverDemo::GenerateSolverConfig()
{
    if (Solver && Solver->CanProcess())
    {
        // 覆盖一些参数以满足特定需求
        Solver->bOverrideEyeSolveSmoothness = true;
        Solver->EyeSolveSmoothness = 0.8f;
        Solver->bOverrideTeethMode = true;
        Solver->TeethMode = ETeethMode::Estimated;

        // 生成并返回配置数据
        return Solver->GetSolverConfigData();
    }
    return TEXT("");
}
```

## 模块依赖

该插件包含众多模块，其共同的独特依赖是 MetaHuman 自身的技术栈。对于 `MetaHumanFaceAnimationSolver` 模块，其特定依赖如下：

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | 提供 MetaHuman 核心技术的 C++ 库接口，是解算器的基础 |
| `MetaHumanConfig` | 管理和加载 MetaHuman 的配置文件和预设 |
| `MetaHumanCaptureData` / `MetaHumanCaptureUtils` | 处理来自各种设备（如 iPhone）的捕获数据结构和工具 |

**注意**：该插件多个模块依赖 `UnrealEd`，表明其包含大量编辑器功能（如资产编辑器、自定义控件）。最终用户在打包的游戏构建中只会包含 `Runtime` 类型的模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时，禁用关卡序列导出功能 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 身上的渲染伪影问题 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 在身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持为现有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题 |

### 维护评价

MetaHuman Animator 插件是 Epic Games 官方维护的核心 MetaHuman 工作流组件，**处于活跃维护状态**。从最近的提交记录（2026年5月）可以看出，团队仍在持续进行功能增强（如为现有网格导出动画）、bug 修复（渲染、缓存问题）和逻辑优化（身体追踪相关）。虽然插件的初始创建时间未知，但作为 MetaHuman 套件的一部分，它在 UE5 发布后一直得到紧密维护。由于其在数字人工作流中的核心地位，**强烈推荐**用于任何涉及 MetaHuman 面部动画制作的项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档]() （待 Epic Games 提供官方文档链接）
- [测试用例]() （测试用例位于引擎测试框架中，未包含在插件目录内）