# Avalanche Mask

> Compositing, designer and broadcasting tool.

| 属性 | 值 |
|---|---|
| 中文名 | 遮罩模块 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（C++ 代码、头文件） |
| 模块 | `AvalancheMask` (Runtime), `AvalancheMaskEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheMask) | |

## 用途

Avalanche Mask 是 Unreal Engine Motion Design（原名 Avalanche）套件中的一个核心模块，专门负责 **2D 遮罩（Mask）功能**的生成与应用。它解决的主要问题是：在虚拟制片和广播图形场景中，需要一种高性能、可视觉化且可链式组合的遮罩系统，用于控制3D场景中物体的材质可见性、混合模式和透明度。

其核心逻辑是：通过场景中的 **源（Source）** 演员（如形状、文字、图像）生成一个**遮罩纹理**，然后将此纹理 **读取（Read）** 并应用到 **目标（Target）** 演员的材质上。整个过程基于 UE 的 `GeometryMask` 框架，并在此基础上构建了更友好的修改器（Modifier）工作流，支持父子通道继承、模糊、羽化等高级效果。

**为什么存在：**
1.  **标准化工作流**：为 Motion Design 提供统一的遮罩创建和应用接口，避免每个功能（如文字、形状、克隆器）重复造轮子。
2.  **材质集成**：自动处理目标演员材质的实例化、参数设置和状态保存/恢复，极大简化了开发者的负担。
3.  **性能优化**：通过缓存和子系统（Subsystem）管理材质实例和句柄，减少运行时开销。
4.  **可扩展性**：其句柄（Handle）系统设计，使其能够支持多种不同类型的材质（标准材质、材质设计器材质、参数化材质、媒体板材质等）。

## 使用场景

-   你正在使用 Motion Design 制作虚拟制片的广播图形，需要一个**矩形**和一个**圆形**来共同构成一个遮罩，用于显示后面的视频流 → 为矩形和圆形添加 `UAvaMask2DWriteModifier`（写入），为视频演员添加 `UAvaMask2DReadModifier`（读取），并设置相同的通道（Channel）。
-   你需要创建一个**渐隐的遮罩**效果 → 为源演员的遮罩修改器启用“羽化（Feathering）”功能。
-   你希望遮罩关系能够**随场景树父子关系自动继承** → 使用通道的“继承自父级（Use Parent Channel）”功能。
-   你的目标演员使用了**材质设计器（Material Designer）**创建的特殊材质 → 遮罩模块会通过 `FAvaMaskDesignedMaterialHandle` 自动适配并注入遮罩参数。

## 蓝图用法

遮罩功能主要通过 `UActorModifier` 体系暴露，核心是两个修改器类。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Channel` | 设置此修改器使用的遮罩通道名称 | `UAvaMask2DBaseModifier` |
| `Set Use Parent Channel` | 设置是否使用父级Actor的通道（如果父级没有，则向上查找） | `UAvaMask2DBaseModifier` |
| `Set Is Inverted` | 设置是否反转遮罩效果（可见变不可见） | `UAvaMask2DBaseModifier` |
| `Set Base Opacity` | （仅 Read 修改器）设置目标材质的基础不透明度 | `UAvaMask2DReadModifier` |
| `Set Write Operation` | （仅 Write 修改器）设置写入操作：叠加（Add）或相减（Subtract） | `UAvaMask2DWriteModifier` |
| `Set Blur Strength` | 设置遮罩模糊强度 | `UAvaMask2DBaseModifier` |
| `Set Outer Feather Radius` | 设置遮罩外羽化半径 | `UAvaMask2DBaseModifier` |

### 使用示例（蓝图描述）

1.  **创建简单的遮罩遮挡**：
    *   在场景中放置一个 `StaticMeshActor`（目标）和一个 `AvaShapeDynamicMeshBase`（例如矩形，源）。
    *   为矩形源演员添加 `UAvaMask2DWriteModifier`，将其通道（Channel）设为 `MyMask`。
    *   为目标演员添加 `UAvaMask2DReadModifier`，也将其通道设为 `MyMask`。
    *   运行时，目标演员的材质将在矩形源的形状区域内可见，区域外不可见（或根据基础不透明度淡出）。

2.  **实现父子遮罩继承**：
    *   将多个源演员（如矩形、圆形）作为另一个父级空Actor的子级。
    *   为父级Actor添加一个 `UAvaMask2DWriteModifier`，并设置其通道为 `ParentChannel`。
    *   为其子级源演员添加 `UAvaMask2DWriteModifier`，但不设置具体通道，而是勾选 `Use Parent Channel`。
    *   所有子级源的遮罩将合并写入到父级指定的 `ParentChannel` 中。

## C++ 用法

### 头文件引入

```cpp
#include "Mask2D/AvaMask2DBaseModifier.h"
#include "Mask2D/AvaMask2DReadModifier.h"
#include "Mask2D/AvaMask2DWriteModifier.h"
```

### 基本用法

以下代码展示了如何在C++中为Actor动态添加和配置一个“读取”遮罩修改器。
（来源：`Public/Mask2D/AvaMask2DReadModifier.h` 及 `Public/Mask2D/AvaMask2DBaseModifier.h` 的接口设计）

```cpp
// 假设 InTargetActor 是需要应用遮罩的目标Actor，InMaskChannelName 是一个唯一的通道名
if (AActor* InTargetActor)
{
    // 获取或添加 Actor 修改器组件
    UActorModifierComponent* ModifierComp = InTargetActor->FindComponentByClass<UActorModifierComponent>();
    if (!ModifierComp)
    {
        ModifierComp = NewObject<UActorModifierComponent>(InTargetActor);
        InTargetActor->AddInstanceComponent(ModifierComp);
        ModifierComp->RegisterComponent();
    }
    
    // 创建 Read 修改器
    UAvaMask2DReadModifier* ReadModifier = NewObject<UAvaMask2DReadModifier>(ModifierComp);
    
    // 配置修改器
    ReadModifier->SetChannel(InMaskChannelName); // 设置要读取的通道
    ReadModifier->SetBaseOpacity(0.5f); // 设置基础不透明度
    ReadModifier->SetIsInverted(false); // 不反转
    
    // 将修改器添加到组件
    ModifierComp->AddModifier(ReadModifier);
}
```

### 进阶用法

以下代码展示了如何处理遮罩应用失败时的回滚，以及如何与材质句柄系统交互（更底层控制）。
（来源：`Private/Handling/AvaMaskMaterialInstanceHandle.h`， `Private/Handling/AvaMaskActorMaterialCollectionHandle.h` 的设计模式）

```cpp
#include "Handling/AvaMaskMaterialInstanceSubsystem.h"
#include "Handling/AvaMaskActorMaterialCollectionHandle.h"

// 模拟一个应用遮罩状态并处理失败的过程
bool ApplyMaskToActorWithRollback(AActor* InTargetActor, const FAvaMask2DSubjectParameters& InParams)
{
    // 1. 创建材质集合句柄（自动扫描Actor所有可渲染组件的材质）
    TSharedPtr<FAvaMaskActorMaterialCollectionHandle> CollectionHandle = 
        MakeShared<FAvaMaskActorMaterialCollectionHandle>(InTargetActor);
    
    if (!CollectionHandle->IsValid())
    {
        UE_LOG(LogTemp, Warning, TEXT("Actor %s has no valid materials for masking."), *InTargetActor->GetName());
        return false;
    }
    
    // 2. 保存原始状态（用于回滚）
    FInstancedStruct HandleData = CollectionHandle->MakeDataStruct();
    CollectionHandle->SaveOriginalState(HandleData.GetStructView());
    
    // 3. 验证材质是否包含必需的遮罩参数
    FText FailReason;
    if (!CollectionHandle->ValidateMaterials(FailReason))
    {
        UE_LOG(LogTemp, Error, TEXT("Material validation failed: %s"), *FailReason.ToString());
        return false;
    }
    
    // 4. 应用新的遮罩状态
    if (!CollectionHandle->ApplyModifiedState(InParams, HandleData.GetStructView()))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to apply mask state to actor %s. Rolling back."), *InTargetActor->GetName());
        // 5. 应用失败，回滚到原始状态
        CollectionHandle->ApplyOriginalState(HandleData.GetStructView());
        return false;
    }
    
    return true;
}
```

## Demo 示例

一个最小化的示例，展示如何创建一个 Actor 子类，使其自身带有一个读取特定通道遮罩的修改器。

**MyMaskedActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Mask2D/AvaMask2DReadModifier.h"
#include "MyMaskedActor.generated.h"

UCLASS()
class AMyMaskedActor : public AActor
{
    GENERATED_BODY()

public:
    AMyMaskedActor();

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY()
    TObjectPtr<UAvaMask2DReadModifier> ReadMaskModifier;
    
    UPROPERTY(EditAnywhere, Category="Mask")
    FName MaskChannelName = TEXT("DefaultMask");
};
```

**MyMaskedActor.cpp**
```cpp
#include "MyMaskedActor.h"
#include "Components/ActorModifierComponent.h"

AMyMaskedActor::AMyMaskedActor()
{
    // 创建一个基础的 StaticMesh 组件作为视觉主体
    UStaticMeshComponent* MeshComp = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
    RootComponent = MeshComp;
    
    // 创建修改器组件
    UActorModifierComponent* ModifierComp = CreateDefaultSubobject<UActorModifierComponent>(TEXT("ModifierComp"));
    ModifierComp->SetupAttachment(RootComponent);
}

void AMyMaskedActor::BeginPlay()
{
    Super::BeginPlay();

    // 在运行时动态创建并配置读取遮罩修改器
    ReadMaskModifier = NewObject<UAvaMask2DReadModifier>(this);
    ReadMaskModifier->SetChannel(MaskChannelName);
    ReadMaskModifier->SetBaseOpacity(0.7f);
    ReadMaskModifier->SetIsInverted(false);

    // 查找并添加到修改器组件
    if (UActorModifierComponent* ModifierComp = FindComponentByClass<UActorModifierComponent>())
    {
        ModifierComp->AddModifier(ReadMaskModifier);
    }
}
```

## 模块依赖

AvalancheMask 模块依赖于以下关键的独特模块：

| 模块 | 用途 |
|---|---|
| `GeometryMask` | 提供底层的几何遮罩画布（Canvas）和读写接口，是整个遮罩系统的基石。 |
| `DynamicMaterial` | 用于支持材质设计器（Material Designer）创建的材质，通过 `FAvaMaskDesignedMaterialHandle` 进行交互。 |
| `AvalancheShapes` | 识别和处理运动设计形状组件（`UAvaShapeDynamicMeshBase`），为其提供专用的材质句柄。 |
| `Text3D` | 识别和处理3D文字组件（`UText3DComponent`），为其提供专用的材质集合句柄。 |
| `AvalancheCore` | 提供基础的运动设计 Actor 修改器框架（`UActorModifierArrangeBaseModifier`）。 |
| `ActorModifierCore` | 提供更通用的 Actor 修改器生命周期和元数据管理。 |
| `MaterialUtilities` | 提供材质参数验证等工具函数。 |

*其他依赖如 `Core`, `Engine`, `Slate`, `UMG`, `GeometryScripting`, `MaterialDesign` 等为通用或间接依赖。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将运动设计编辑器标签页独立分组，提升界面组织性。 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 在演播页设置中添加了 MRQ 分析功能。 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 在播出控制工具栏添加了更灵活的页面加载选项。 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 新增项目设置，可强制禁用3D文字和形状的碰撞。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 优化视口客户端关联/取消关联的通知机制。 |

### 维护评价

**维护状态：活跃维护**
-   **创建时间**：该插件于2025年5月从实验性（Experimental）目录迁移至正式的虚拟制作（VirtualProduction）目录，标志着其已达到稳定可用状态。
-   **更新频率**：从提供的近期提交记录看，在2026年5月仍有密集的功能更新和优化，表明 Epic Games 团队正在持续迭代和改进 Motion Design 套件。
-   **功能稳定性**：代码中大量使用了 `UE_DEPRECATED(5.8, ...)` 宏，表明在 5.8 版本中进行了重大的架构重构（如废弃旧的 `ActorData` 和 `MaterialHandle` 系统，转向 `MaterialContainerState` 和 `MaterialBridge`），这通常意味着技术债务得到清理，系统更加健壮。
-   **推荐使用**：**强烈推荐**。作为 Epic 官方维护的虚拟制作核心工具链的一部分，它功能强大、设计现代，并与编辑器深度集成。对于任何需要程序化或动态遮罩效果的 Motion Design 项目，此模块是最佳选择。需要注意的是，它依赖于多个其他高级模块，项目需确保这些依赖可用。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheMask)
-   官方文档：暂无独立文档，参考 Unreal Engine 虚拟制作与 Motion Design 整体文档。
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheFunctionalTest) (参考 `AvalancheFunctionalTest` 模块)