# RigLogic Plugin v10.3.0

> RigLogic Plugin for Facial Animation v10.3.0

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（DNA资产、蓝图资产、材质模板） |
| 模块 | `RigLogicLib` (Runtime), `RigLogicModule` (Runtime), `RigLogicEditor` (Runtime), `RigLogicDeveloper` (Runtime), `RigLogicLibTest` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-07-20 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/RigLogic) | |

## 用途

RigLogic 是一个高性能的面部动画运行时系统，专为驱动数字人（如 MetaHuman）的面部表情而设计。它解决的核心问题是：如何将一组简化的面部控制参数（GUI Controls）高效地转换为复杂的骨骼变换（Joint Transforms）和混合形状权重（Blend Shape Weights），从而实现逼真的面部动画。

该插件的核心是一个名为 `FRigLogic` 的无状态计算引擎。它读取一个预先制作好的 **DNA 文件**（Digital Nature Asset），该文件包含了角色的面部骨骼结构、混合形状、以及驱动它们的数学模型（包括 PSD、RBF 和神经网络）。在运行时，`FRigLogic` 根据输入的控制值，通过这些模型计算出最终的动画输出。

简单来说，RigLogic 是连接“艺术家控制”与“角色面部表现”之间的桥梁，是 MetaHuman 工作流中驱动面部动画的核心技术。

## 使用场景

-   **MetaHuman 角色动画**：这是 RigLogic 最主要的应用场景。MetaHuman Creator 生成的角色会附带 DNA 文件，RigLogic 插件负责在 UE 中实时驱动其面部动画。
-   **自定义数字人项目**：如果你使用其他工具（如 Maya）创建了基于 DNA 标准的数字人模型，并希望在 UE 中为其添加高质量的面部动画，可以使用此插件。
-   **需要高性能面部动画的项目**：RigLogic 支持 SIMD（SSE/AVX/NEON）加速，适合对性能要求高的实时应用，如游戏、虚拟直播、实时渲染影视等。
-   **复杂的面部动画逻辑**：DNA 文件可以包含复杂的动画逻辑，如基于物理的次级运动、神经网络驱动的微表情等，RigLogic 能够在运行时高效执行这些逻辑。

## 蓝图用法

RigLogic 的蓝图接口主要通过 `UDNAAsset` 和 ControlRig 中的 `RigUnit_RigLogic` 节点暴露。

### 核心资产

| 资产类型 | 说明 |
|---|---|
| `UDNAAsset` (MetaHuman DNA Data) | 存储角色 DNA 数据的资产。可以从 `.dna` 文件导入，是驱动动画的数据源。 |
| `USkeletalMesh` | 骨骼网格体资产，需要附加 `UDNAAsset` 作为 `AssetUserData` 才能被 RigLogic 驱动。 |

### 核心节点 (ControlRig)

在 ControlRig 蓝图中，你可以使用 `RigUnit_RigLogic` 节点来驱动角色。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Rig Unit Rig Logic` | 核心计算单元。读取输入曲线（控制值），通过 DNA 数据计算，输出骨骼变换和混合形状曲线。 | `URigUnit_RigLogic` |

### 使用示例（蓝图描述）

1.  **准备资产**：确保你的 `USkeletalMesh` 已经通过 MetaHuman 流程或手动方式附加了正确的 `UDNAAsset`。
2.  **创建 ControlRig**：为你的角色创建一个 ControlRig 资产。
3.  **添加 RigLogic 节点**：在 ControlRig 的图表中，添加 `Rig Unit Rig Logic` 节点。
4.  **连接输入**：将你的动画蓝图或游戏逻辑中产生的面部控制曲线（例如 `CTRL_c_mouth_smileLeft`）连接到该节点的 `Input Curves` 引脚。
5.  **连接输出**：该节点会输出 `Output Bones`（骨骼变换）和 `Output Curves`（混合形状权重）。将这些输出连接到 ControlRig 的 `Output Pose` 和 `Output Curves` 节点，最终传递给动画蓝图。
6.  **设置 LOD**：节点会根据当前的 LOD 级别自动调整计算复杂度。

## C++ 用法

### 头文件引入

```cpp
#include "DNAReader.h"
#include "DNAUtils.h"
#include "RigLogic.h"
#include "RigInstance.h"
#include "DNAAsset.h"
```

### 基本用法

以下代码展示了如何从文件加载 DNA 数据，并使用 RigLogic 计算一帧动画输出。

```cpp
// 来源: Engine/Plugins/Animation/RigLogic/Source/RigLogicModule/Public/DNAUtils.h
// 来源: Engine/Plugins/Animation/RigLogic/Source/RigLogicModule/Public/RigLogic.h
// 来源: Engine/Plugins/Animation/RigLogic/Source/RigLogicModule/Public/RigInstance.h

// 1. 从文件加载 DNA 数据
FString DNAFilePath = TEXT("/Game/MetaHumans/MyCharacter/face.dna");
TSharedPtr<IDNAReader> DNAReader = ReadDNAFromFile(DNAFilePath, EDNADataLayer::All);
if (!DNAReader.IsValid())
{
    UE_LOG(LogTemp, Error, TEXT("Failed to load DNA file: %s"), *DNAFilePath);
    return;
}

// 2. 创建 RigLogic 计算引擎实例 (无状态，可共享)
FRigLogic RigLogic;
RigLogic.Init(DNAReader.Get());

// 3. 为每个角色实例创建 RigInstance (有状态，存储输出缓冲区)
FRigInstance RigInstance(&RigLogic);

// 4. 设置输入控制值 (例如，设置微笑控制为 0.8)
uint16 SmileControlIndex = 0; // 需要根据 DNA 中的 GUI Control 名称查找索引
RigInstance.SetGUIControl(SmileControlIndex, 0.8f);

// 5. 设置 LOD 级别
RigInstance.SetLOD(0);

// 6. 执行计算
RigLogic.Calculate(&RigInstance);

// 7. 获取输出结果
TArrayView<const float> JointOutputs = RigInstance.GetJointOutputs();
TArrayView<const float> BlendShapeOutputs = RigInstance.GetBlendShapeOutputs();

// JointOutputs 和 BlendShapeOutputs 现在包含了计算后的骨骼变换和混合形状权重数据
// 你需要根据 DNAIndexMapping 将这些数据应用到 USkeletalMeshComponent 上
```

### 进阶用法

在实际的 UE 集成中，通常通过 `UDNAAsset` 和 `FSharedRigRuntimeContext` 来管理数据，并在动画节点中使用。

```cpp
// 来源: Engine/Plugins/Animation/RigLogic/Source/RigLogicModule/Public/DNAAsset.h
// 来源: Engine/Plugins/Animation/RigLogic/Source/RigLogicModule/Public/SharedRigRuntimeContext.h
// 来源: Engine/Plugins/Animation/RigLogic/Source/RigLogicModule/Public/AnimNode_RigLogic.h

// 假设你已经有一个附加了 UDNAAsset 的 USkeletalMeshComponent
USkeletalMeshComponent* SkelMeshComp = ...;
UDNAAsset* DNAAsset = SkelMeshComp->GetSkeletalMeshAsset()->GetAssetUserData<UDNAAsset>();

if (DNAAsset)
{
    // 1. 获取或创建共享的运行时上下文 (包含 RigLogic 引擎和索引映射)
    // 通常在动画实例初始化时完成
    TSharedPtr<FSharedRigRuntimeContext> SharedContext = DNAAsset->GetSharedRigRuntimeContext();
    if (!SharedContext.IsValid())
    {
        SharedContext = MakeShared<FSharedRigRuntimeContext>();
        TSharedPtr<IDNAReader> BehaviorReader = DNAAsset->GetBehaviorReader();
        SharedContext->RigLogic = MakeShared<FRigLogic>();
        SharedContext->RigLogic->Init(BehaviorReader.Get());
        SharedContext->BehaviorReader = BehaviorReader;
        SharedContext->CacheVariableJointIndices();
        SharedContext->CacheInverseNeutralJointRotations();
        DNAAsset->SetSharedRigRuntimeContext(SharedContext);
    }

    // 2. 创建或获取角色实例 (通常在动画节点中管理)
    // FAnimNode_RigLogic 内部会为每个骨骼网格组件维护一个 FRigInstance
    FRigInstance* RigInstance = ...; // 从动画节点获取

    // 3. 在动画更新中设置控制值并计算
    // 控制值通常来自动画蓝图中的曲线
    RigInstance->SetGUIControlValues(ControlValuesArray.GetData());
    RigInstance->SetLOD(CurrentLOD);
    SharedContext->RigLogic->Calculate(RigInstance.Get());

    // 4. 应用结果到骨骼网格
    // FAnimNode_RigLogic 的 Evaluate 函数内部会处理这个映射过程
    // 它使用 FDNAIndexMapping 将 RigLogic 的输出映射到 UE 的骨骼和曲线系统
}
```

## Demo 示例

以下是一个最小化的 C++ 示例，演示如何在 Actor 中使用 RigLogic 驱动一个简单的面部表情。

**MyRigLogicActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DNAReader.h"
#include "RigLogic.h"
#include "RigInstance.h"
#include "MyRigLogicActor.generated.h"

UCLASS()
class AMyRigLogicActor : public AActor
{
    GENERATED_BODY()

public:
    AMyRigLogicActor();

protected:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

private:
    UPROPERTY(VisibleAnywhere)
    USkeletalMeshComponent* SkeletalMeshComponent;

    TSharedPtr<IDNAReader> DNAReader;
    TSharedPtr<FRigLogic> RigLogic;
    TUniquePtr<FRigInstance> RigInstance;

    // 用于演示的控制值
    float SmileValue = 0.0f;
    float BlinkValue = 0.0f;
    bool bSmiling = false;
    bool bBlinking = false;

    void UpdateAnimation();
};
```

**MyRigLogicActor.cpp**
```cpp
#include "MyRigLogicActor.h"
#include "DNAUtils.h"
#include "Components/SkeletalMeshComponent.h"

AMyRigLogicActor::AMyRigLogicActor()
{
    PrimaryActorTick.bCanEverTick = true;

    SkeletalMeshComponent = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("SkeletalMesh"));
    RootComponent = SkeletalMeshComponent;
}

void AMyRigLogicActor::BeginPlay()
{
    Super::BeginPlay();

    // 1. 加载 DNA 文件 (请替换为你的实际路径)
    FString DNAPath = FPaths::ProjectContentDir() / TEXT("MetaHumans/Demo/face.dna");
    DNAReader = ReadDNAFromFile(DNAPath, EDNADataLayer::All);

    if (DNAReader.IsValid())
    {
        // 2. 初始化 RigLogic 引擎
        RigLogic = MakeShared<FRigLogic>();
        RigLogic->Init(DNAReader.Get());

        // 3. 创建角色实例
        RigInstance = MakeUnique<FRigInstance>(RigLogic.Get());

        UE_LOG(LogTemp, Log, TEXT("RigLogic initialized. GUI Controls: %d"), RigInstance->GetGUIControlCount());
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load DNA file from: %s"), *DNAPath);
    }
}

void AMyRigLogicActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    // 简单的表情动画逻辑
    if (bSmiling)
    {
        SmileValue = FMath::FInterpTo(SmileValue, 1.0f, DeltaTime, 5.0f);
        if (SmileValue > 0.99f) bSmiling = false;
    }
    else
    {
        SmileValue = FMath::FInterpTo(SmileValue, 0.0f, DeltaTime, 5.0f);
        if (SmileValue < 0.01f) bSmiling = true;
    }

    if (bBlinking)
    {
        BlinkValue = FMath::FInterpTo(BlinkValue, 1.0f, DeltaTime, 10.0f);
        if (BlinkValue > 0.99f) bBlinking = false;
    }
    else
    {
        BlinkValue = FMath::FInterpTo(BlinkValue, 0.0f, DeltaTime, 10.0f);
        if (BlinkValue < 0.01f) bBlinking = true;
    }

    UpdateAnimation();
}

void AMyRigLogicActor::UpdateAnimation()
{
    if (!RigInstance.IsValid() || !RigLogic.IsValid())
    {
        return;
    }

    // 4. 设置控制值 (索引需要根据你的 DNA 文件确定，这里假设 0 是微笑，1 是眨眼)
    RigInstance->SetGUIControl(0, SmileValue);
    RigInstance->SetGUIControl(1, BlinkValue);
    RigInstance->SetLOD(0);

    // 5. 执行计算
    RigLogic->Calculate(RigInstance.Get());

    // 6. 获取输出并应用到骨骼网格组件
    // 注意：这是一个简化的示例。实际应用中，你需要使用 FDNAIndexMapping
    // 来正确地将 RigLogic 的输出映射到 USkeletalMeshComponent 的骨骼和 MorphTarget。
    TArrayView<const float> JointOutputs = RigInstance->GetJointOutputs();
    TArrayView<const float> BlendShapeOutputs = RigInstance->GetBlendShapeOutputs();

    // 在真实项目中，这里应该调用类似 FAnimNode_RigLogic 中的映射和应用逻辑。
    // 例如，遍历 BlendShapeOutputs，根据映射设置对应的 MorphTarget 权重。
    // SkeletalMeshComponent->SetMorphTarget(FName("mouth_smile"), BlendShapeOutputs[SmileMorphIndex]);

    UE_LOG(LogTemp, VeryVerbose, TEXT("RigLogic Calculated. Smile: %.2f, Blink: %.2f"), SmileValue, BlinkValue);
}
```

## 模块依赖

RigLogic 插件由多个模块组成，各司其职。如果你要在自己的模块中使用 RigLogic 的功能，需要添加以下依赖：

| 模块 | 用途 |
|---|---|
| `RigLogicLib` | RigLogic 的核心计算库，包含 DNA 解析和动画计算算法。这是最底层的依赖。 |
| `RigLogicModule` | RigLogic 的 UE 集成模块。提供了 `UDNAAsset`, `FRigLogic`, `FRigInstance`, `FAnimNode_RigLogic` 等 UE 类型。**这是大多数使用者需要依赖的模块**。 |
| `RigLogicEditor` | 编辑器支持模块，提供 DNA 文件导入、资产编辑器等功能。仅在编辑器环境下需要。 |
| `RigLogicDeveloper` | 开发者工具模块，可能包含调试和开发辅助功能。 |
| `RigLogicLibTest` | RigLogicLib 的单元测试模块。 |

**在你的 `.Build.cs` 文件中添加依赖示例：**
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "RigLogicModule" // 添加这一行以使用 RigLogic 的 UE 集成功能
});
```

## 维护状态

### 近期更新

```
- 014fb9a74725 [UEMHC] Fix outfit resizing for face mesh when body blending
- fba8697eab3a Make `UDNAAsset::GetDNAIndexMapping` work under transactions by using transactionally-safe locks.
- 3216c33a88c3 [UEMHC] reorder geometry and behaviour readers as this is not behaving as expected and breaks UEMHC unit tests #rb andrean.franc, bojan.brankov
```

### 维护评价

-   **活跃维护**：最近的提交（2025年10月）表明该插件仍在积极维护中，主要围绕 MetaHuman 工作流（UEMHC）进行修复和优化。
-   **核心功能稳定**：作为 MetaHuman 的核心驱动技术，RigLogic 的基础计算框架已经非常成熟。
-   **持续集成**：提交信息中频繁出现 `[UEMHC]` 标签，说明它与 Epic 的 MetaHuman 工具链紧密集成，更新会跟随 MetaHuman 工具的迭代。
-   **推荐使用**：对于任何涉及 MetaHuman 或需要专业级面部动画的项目，RigLogic 是官方推荐且必不可少的插件。其性能和质量经过大规模验证。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/RigLogic)
-   [官方文档](https://docs.unrealengine.com/5.7/en-US/riglogic-plugin-in-unreal-engine/) (Epic 官方文档链接，通常包含在 MetaHuman 文档中)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/RigLogic/Source/RigLogicLibTest)