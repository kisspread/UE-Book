# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、配置、求解器） |
| 模块 | `MetaHumanAnimator` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanPerformance` (Runtime) 等 (共29个) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕（年龄未知） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的用于创建和驱动 MetaHuman 角色的完整工具链。它不仅是一个插件，更是一个庞大的**生产管线 (Pipeline)** 集成方案。其核心目的是将 MetaHuman 的完整工作流——从**捕获真实演员表演数据**（通过 iPhone 或专业摄像机）、**重建数字身份 (Identity)**、**驱动面部/身体动画**，到**最终在 Unreal Engine 中实时渲染**——无缝地整合到引擎中。

它解决了独立艺术家或工作室在将真实世界表演转换为高保真数字人类时面临的复杂流程、多软件切换和性能优化问题，提供了一个统一的 UE 内解决方案。

## 使用场景

-   **数字人内容创作**：你使用 iPhone (通过 MetaHuman Capture 应用) 或专业面部捕捉设备拍摄了演员的表演，需要将其转换为可用于 MetaHuman 角色的高质量面部动画。
-   **音频驱动动画**：你有一段音频文件，希望快速生成对应的 MetaHuman 面部动画（Speech2Face）。
-   **表演驱动**：你希望直接将演员的实时表演数据流驱动到 MetaHuman 角色上，用于虚拟制片或实时演示。
-   **批量处理**：你拥有多个 MetaHuman 角色，需要批量应用或调整动画、配置求解器参数。

## 蓝图用法

### 配置相关

| 节点 | 说明 | 所在类 |
|---|---|---|
| `bOverrideDeviceConfig` | 是否覆盖默认设备配置。勾选后可指定 `DeviceConfig` | `UMetaHumanFaceFittingSolver` |
| `DeviceConfig` | 指定用于面部拟合的设备特定配置资源 | `UMetaHumanFaceFittingSolver` |
| `PredictiveSolver` | 用于为表演准备 (Prepare Identity) 阶段训练的预测求解器配置 | `UMetaHumanFaceFittingSolver` |

### 流程控制

| 节点 | 说明 | 所在类 |
|---|---|---|
| `LoadFaceFittingSolvers` | 加载面部拟合所需的求解器模型 | `UMetaHumanFaceFittingSolver` |
| `LoadPredictiveSolver` | 加载用于身份准备阶段的预测求解器 | `UMetaHumanFaceFittingSolver` |
| `CanProcess` | 检查当前配置和数据是否满足开始处理的条件 | `UMetaHumanFaceFittingSolver` |
| `GetConfigDisplayName` | 根据捕获数据获取当前有效配置的显示名称 | `UMetaHumanFaceFittingSolver` |

### 数据获取（内部使用，可用于调试或高级操作）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetFittingTemplateData` | 获取用于拟合的模板网格体数据（JSON字符串） | `UMetaHumanFaceFittingSolver` |
| `GetFittingConfigData` | 获取拟合求解器的配置数据（JSON字符串） | `UMetaHumanFaceFittingSolver` |
| `GetFittingConfigTeethData` | 获取牙齿部分的拟合配置数据 | `UMetaHumanFaceFittingSolver` |
| `GetFittingIdentityModelData` | 获取身份模型数据（JSON字符串） | `UMetaHumanFaceFittingSolver` |
| `GetFittingControlsData` | 获取面部控制器数据（JSON字符串） | `UMetaHumanFaceFittingSolver` |
| `GetPredictiveTrainingData` | 获取用于训练预测求解器的完整训练数据（二进制数组） | `UMetaHumanFaceFittingSolver` |

### 使用示例（蓝图描述）

1.  **在编辑器中配置**：创建一个 `MetaHumanFaceFittingSolver` 资产，在其细节面板中，根据需要勾选“Override Device Config”并选择对应的设备配置，或指定 `PredictiveSolver`。
2.  **蓝图中初始化**：在需要执行面部拟合的蓝图中，获取对该 `FaceFittingSolver` 资产的引用。
3.  **检查与加载**：调用 `CanProcess` 节点检查是否可执行。若返回 `true`，则调用 `LoadFaceFittingSolvers` 节点加载求解器模型。
4.  **绑定事件**：使用 `OnInternalsChanged` 事件委托来监听求解器内部数据的变化，并做出响应（例如更新UI或日志）。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanFaceFittingSolver.h"
```

### 基本用法

```cpp
// 来源：MetaHumanFaceFittingSolver/Public/MetaHumanFaceFittingSolver.h
// 创建一个 Face Fitting Solver 实例
UMetaHumanFaceFittingSolver* FaceFittingSolver = NewObject<UMetaHumanFaceFittingSolver>();

// 检查是否满足处理条件
if (FaceFittingSolver->CanProcess())
{
    // 加载面部拟合所需的求解器
    FaceFittingSolver->LoadFaceFittingSolvers();

    // 绑定数据变化回调
    FaceFittingSolver->OnInternalsChanged().AddLambda([]()
    {
        UE_LOG(LogTemp, Log, TEXT("Face Fitting Solver internals have changed!"));
    });
}
```

### 进阶用法

```cpp
// 假设已有有效的 CaptureData 对象 (UCaptureData* MyCaptureData)
UMetaHumanFaceFittingSolver* Solver = ... // 获取或创建求解器实例

FString ConfigName;
if (Solver->GetConfigDisplayName(MyCaptureData, ConfigName))
{
    UE_LOG(LogTemp, Log, TEXT("Using fitting config: %s"), *ConfigName);
}

// 获取不同阶段的拟合数据（通常用于引擎内部管线调用）
FString TemplateDataJson = Solver->GetFittingTemplateData(MyCaptureData);
FString ConfigDataJson = Solver->GetFittingConfigData(MyCaptureData);
// ... 这些数据会传递给底层的拟合算法
```

## Demo 示例

**MetaHumanFaceFittingSolver_BasicUsage.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MetaHumanFaceFittingSolver_BasicUsage.generated.h"

UCLASS()
class AMyMetaHumanActor : public AActor
{
    GENERATED_BODY()

public:
    AMyMetaHumanActor();

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY(Transient)
    TObjectPtr<class UMetaHumanFaceFittingSolver> MyFaceFittingSolver;

    void OnSolverDataChanged();
};
```

**MetaHumanFaceFittingSolver_BasicUsage.cpp**
```cpp
#include "MetaHumanFaceFittingSolver_BasicUsage.h"
#include "MetaHumanFaceFittingSolver.h" // 关键头文件

AMyMetaHumanActor::AMyMetaHumanActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyMetaHumanActor::BeginPlay()
{
    Super::BeginPlay();

    // 1. 创建或加载求解器实例（通常从磁盘加载资产更常见）
    MyFaceFittingSolver = NewObject<UMetaHumanFaceFittingSolver>(this);

    // 2. 配置（可选，编辑器中操作更方便）
    // MyFaceFittingSolver->DeviceConfig = LoadObject<UMetaHumanConfig>(nullptr, TEXT("/Path/To/Your/Config"));

    // 3. 检查就绪状态
    if (MyFaceFittingSolver && MyFaceFittingSolver->CanProcess())
    {
        UE_LOG(LogTemp, Log, TEXT("Face Fitting Solver is ready. Loading models..."));
        // 4. 加载求解器模型
        MyFaceFittingSolver->LoadFaceFittingSolvers();
        MyFaceFittingSolver->LoadPredictiveSolver();

        // 5. 监听变化
        MyFaceFittingSolver->OnInternalsChanged().AddUObject(this, &AMyMetaHumanActor::OnSolverDataChanged);
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Face Fitting Solver is not ready. Check configuration and capture data."));
    }
}

void AMyMetaHumanActor::OnSolverDataChanged()
{
    UE_LOG(LogTemp, Log, TEXT("Internal solver data updated. Ready for next processing step."));
}
```

## 模块依赖

该插件集成了大量内部模块，使用者通常不需要直接依赖大部分模块。以下列出的是可能与用户开发相关或提供重要功能的独特依赖：

| 模块 | 用途 |
|---|---|
| `MetaHumanSDKEditor` | 提供与 MetaHuman SDK 相关的编辑器集成和资产类型 |
| `SkeletalMeshUtilitiesCommon` | 提供用于骨骼网格体操作的通用工具函数 |
| `ControlRigDeveloper` | 用于创建和编辑控制 MetaHuman 面部动画的 Control Rig |
| `MeshDescription` | 提供用于表示和操作网格体数据（如面部模板）的低级数据结构 |
| `NeuralNetworkInference` | (可能) 用于运行机器学习模型推理，如驱动求解器或 Speech2Face |
| `MediaCompositing` | 用于处理视频媒体数据，可能用于原始捕获视频的预览或合成 |
| `Niagara` | 用于高级粒子和效果，可能在捕获数据可视化或调试中使用 |
| `MeshTrackerInterface` | 提供与外部网格体跟踪系统（如深度摄像头）的接口 |
| `SequencerCore` | 为 MetaHuman 动画与 Sequencer 的深度集成提供基础 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体跟踪时，禁用关卡序列导出功能，避免冲突 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 角色上的渲染伪影问题 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体跟踪时过滤掉不必要的可视化对象，提升清晰度 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持将动画序列导出到已存在的网格体上 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复与 Sequencer 集成时的缓存问题 |

### 维护评价

MetaHuman Animator 是一个**处于活跃维护状态**的官方核心插件。从近期提交记录来看，更新非常频繁（2026年5月有多次提交），内容聚焦于**功能完善**（如身体跟踪支持）、**问题修复**（渲染、缓存、导出）以及**工作流优化**。作为 Epic Games 的战略产品工具，它拥有长期稳定的维护承诺。**强烈推荐**所有使用 MetaHuman 进行内容创作的项目使用此插件，它是目前引擎内最完整、最权威的解决方案。

**注意**：由于其巨大的规模和复杂的依赖关系，建议在集成时关注官方版本说明和兼容性信息。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/metahuman-animator-in-unreal-engine/) (预计链接，文档通常会发布在官方文档站)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/MetaHuman)