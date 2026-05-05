# Deformer Graph

> Editor for creating GPU mesh deformation graphs（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容类型未知） |
| 模块 | `OptimusSettings` (Runtime), `OptimusCore` (Runtime), `OptimusDeveloper` (UncookedOnly), `OptimusEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-08-30 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/DeformerGraph) | |

## 用途

DeformerGraph（内部代号 Optimus）是一个基于节点的可视化编辑器，用于创建和调试在 GPU 上运行的网格变形逻辑。它解决的核心问题是：将复杂的、计算密集型的网格变形（如肌肉模拟、布料、程序化变形）从 CPU 卸载到 GPU，从而大幅提升性能并实现更复杂的效果。该插件提供了一个完整的数据流图编辑环境，允许美术和技术美术人员通过连接节点来定义变形数据（如骨骼变换、顶点位置）如何被读取、处理并最终写回网格，而无需编写底层的计算着色器代码。

## 使用场景

- **角色高级变形**：你需要为角色实现复杂的肌肉膨胀、脂肪抖动或基于物理的次级动画，但 CPU 变形管线性能不足或效果受限。
- **GPU 加速的程序化动画**：你希望在 GPU 上实时计算大量顶点的位移，例如风吹草地、水面波浪或群体动画。
- **快速原型化 GPU 计算逻辑**：你想快速验证一个基于 GPU 的网格变形算法，而不想从头编写和调试计算着色器。
- **集成自定义 GPU 变形**：你希望将自定义的 GPU 变形逻辑无缝集成到 UE 的动画蓝图和渲染管线中。

## 蓝图用法

蓝图 API 主要集中在 `OptimusCore` 模块中，用于在运行时与变形图资产交互。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Deformer Graph` | 创建一个新的变形图资产实例。 | `UOptimusDeformerGraphFactory` |
| `Add Data Interface` | 向变形图添加一个数据接口（如骨骼网格、变换数组）。 | `UOptimusDeformerGraph` |
| `Set Skeletal Mesh Component` | 将变形图资产应用到指定的骨骼网格组件上。 | `UOptimusComponentSource` |
| `Set Execution Phase` | 设置变形图的执行阶段（如预变形、后变形）。 | `UOptimusDeformerGraph` |
| `Compile` | 编译变形图，生成 GPU 着色器代码。 | `UOptimusDeformerGraph` |
| `Execute` | 在指定的组件上执行一次变形图计算。 | `UOptimusComponentSource` |

### 使用示例（蓝图描述）

1.  **创建与配置**：使用 `Create Deformer Graph` 节点创建资产。通过 `Add Data Interface` 节点添加 `Optimus Skinned Mesh Data Interface` 来获取网格数据。
2.  **连接组件**：在角色蓝图中，获取其 `Skeletal Mesh Component`，然后使用 `Set Skeletal Mesh Component` 节点将配置好的变形图资产应用到该组件上。
3.  **触发执行**：通常，变形图会在动画蓝图的 `Post Evaluation` 阶段自动执行。你也可以通过 `Execute` 节点在特定事件（如按键）时手动触发一次计算。

## C++ 用法

### 头文件引入

```cpp
#include "OptimusDeformerGraph.h"
#include "OptimusComponentSource.h"
```

### 基本用法

以下代码演示了如何在 C++ 中创建一个简单的变形图并将其应用到组件上。
（来源：基于 `OptimusCore` 模块的公开 API 和测试模式推断）

```cpp
// 假设在某个 Actor 或 Component 的初始化函数中
UOptimusDeformerGraph* DeformerGraph = NewObject<UOptimusDeformerGraph>();

// 添加一个数据接口来读取骨骼网格数据
UOptimusSkinnedMeshDataInterface* SkinnedMeshDI = NewObject<UOptimusSkinnedMeshDataInterface>();
DeformerGraph->AddDataInterface(SkinnedMeshDI);

// 编译变形图
DeformerGraph->Compile();

// 获取目标骨骼网格组件
USkeletalMeshComponent* TargetSkelMeshComp = GetSkeletalMeshComponent();

// 创建组件源并应用变形图
UOptimusComponentSource* ComponentSource = NewObject<UOptimusComponentSource>();
ComponentSource->SetSkeletalMeshComponent(TargetSkelMeshComp);
ComponentSource->SetDeformerGraph(DeformerGraph);
ComponentSource->SetExecutionPhase(EOptimusExecutionPhase::PostEvaluation);
```

### 进阶用法

更复杂的用法涉及创建自定义数据接口和计算内核节点，这通常在编辑器中完成。C++ 端主要负责资产的加载、实例化和运行时参数的动态设置。

## Demo 示例

一个最小的可运行示例，展示如何通过 C++ 代码加载并应用一个已有的变形图资产。

```cpp
// MyActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyActor.generated.h"

class USkeletalMeshComponent;
class UOptimusDeformerGraph;
class UOptimusComponentSource;

UCLASS()
class AMyActor : public AActor
{
    GENERATED_BODY()

public:
    AMyActor();

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY(VisibleAnywhere)
    USkeletalMeshComponent* SkeletalMeshComp;

    UPROPERTY(EditAnywhere, Category = "Deformer")
    UOptimusDeformerGraph* DeformerGraphAsset;

    UPROPERTY()
    UOptimusComponentSource* DeformerComponentSource;
};
```

```cpp
// MyActor.cpp
#include "MyActor.h"
#include "Components/SkeletalMeshComponent.h"
#include "OptimusDeformerGraph.h"
#include "OptimusComponentSource.h"

AMyActor::AMyActor()
{
    PrimaryActorTick.bCanEverTick = false;

    SkeletalMeshComp = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("SkeletalMesh"));
    RootComponent = SkeletalMeshComp;
}

void AMyActor::BeginPlay()
{
    Super::BeginPlay();

    if (DeformerGraphAsset && SkeletalMeshComp)
    {
        // 创建组件源并绑定资产与组件
        DeformerComponentSource = NewObject<UOptimusComponentSource>(this);
        DeformerComponentSource->SetSkeletalMeshComponent(SkeletalMeshComp);
        DeformerComponentSource->SetDeformerGraph(DeformerGraphAsset);
        // 变形图将在动画求值后自动执行
        DeformerComponentSource->SetExecutionPhase(EOptimusExecutionPhase::PostEvaluation);
    }
}
```

## 模块依赖

要使用此插件，你的项目或模块需要依赖以下模块（基于 `.uplugin` 的 `Plugins` 字段）：

| 模块 | 用途 |
|---|---|
| `ComputeFramework` | 提供 GPU 计算框架的底层支持，是 DeformerGraph 执行计算的基础。 |
| `ControlRig` | 提供与动画控制系统的集成，用于读取和写入骨骼变换等动画数据。 |

**注意**：`OptimusCore`, `OptimusEditor` 等模块的内部依赖（如 `RenderCore`, `RHI`）属于引擎核心或渲染模块，无需额外声明。

## 维护状态

### 近期更新

（由于未提供具体的 Git 日志，以下为基于插件状态的推测性描述）
- 该插件自 2022 年创建以来，作为实验性功能持续迭代。
- 版本号为 0.9，表明其仍处于 Beta 测试阶段，API 和功能可能发生变化。
- 作为 Epic 官方维护的动画核心功能之一，预计会随引擎版本更新而持续维护。

### 维护评价

- **创建时间**：约 3 年前（2022年），相对较新。
- **状态**：**实验性 (Beta)**。`IsBetaVersion=true` 且 `EnabledByDefault=false`，表明它尚未被视为稳定生产功能。
- **活跃度**：作为 Epic 重点开发的 GPU 动画特性，预计在引擎主版本中会持续更新。
- **推荐使用**：**谨慎推荐**。适用于愿意承担实验性 API 变更风险，并追求前沿 GPU 变形性能的项目。不建议用于需要长期稳定维护的商业项目核心功能，除非你有团队能够跟进其变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/DeformerGraph)
- [官方文档]() (暂无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Tests/Runtime/DeformerGraph) (如果存在)