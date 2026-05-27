# Mutable

> Mutable adds the tools and runtime to create customizable objects for your games.

| 属性 | 值 |
|---|---|
| 中文名 | 可变对象系统 |
| 分类 | CustomizableObjects |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器工具、运行时库、验证工具） |
| 模块 | `MutableRuntime` (Runtime), `CustomizableObject` (Runtime), `MutableTools` (Runtime), `CustomizableObjectEditor` (Runtime), `MutableValidation` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-05 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable) | [官方文档](https://github.com/anticto/Mutable-Documentation/wiki) |

## 用途

Mutable 是一个高级角色与物品定制系统，旨在为游戏提供高性能、深度可定制化的内容。它解决的核心问题是：当蓝图或材质实例无法满足复杂的、运行时动态生成整个网格体和纹理的需求时，提供一套完整的解决方案。

其存在意义在于：
1.  **高性能运行时生成**：与传统的蓝图替换网格或材质参数不同，Mutable 在运行时通过虚拟机执行预编译的指令图，直接生成新的 SkeletalMesh 和纹理资产，性能开销更低，特别适合主机和移动端。
2.  **深度内容整合**：允许将多个基础网格、纹理、材质、形态目标（Morph Targets）、物理资产等资源，通过一个可视化的节点图进行复杂的逻辑组合、遮罩、混合和投影，最终生成一个全新的、完整的资产。
3.  **流式加载与LOD管理**：支持网格和纹理的流式加载，可以根据实例的状态（如远近距离、重要程度）动态加载不同精度的LOD，优化内存和性能。

## 使用场景

- **角色创建器**：在开放世界RPG或大型多人游戏中，允许玩家通过滑块、选项和涂装工具，深度定制角色的面部、身体、装备外观，所有变化都需在游戏运行时无缝生成。
- **载具定制系统**：在竞速游戏中，玩家可以自定义车辆的每个部件（车体、轮胎、涂装）、添加贴花，并实时看到合成后的完整车辆模型。
- **武器皮肤系统**：允许为同一把武器应用多种材质、图案和颜色组合，系统根据玩家的选择在运行时生成最终的武器模型和材质实例。
- **需要基于数据表生成大量变体**：当一个游戏资产（如NPC、道具）存在数十上百种视觉变体，且变体由组合逻辑而非独立资产定义时，使用Mutable可以极大减少美术资产数量和内存占用。

## 蓝图用法

Mutable 主要通过其编辑器工具和运行时 C++ API 工作，部分核心功能通过蓝图暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Compile` | 异步编译 `UCustomizableObject`，生成运行时所需的模型数据。 | `UCustomizableObject` |
| `Create` | 基于一个编译好的 `UCustomizableObject` 创建一个 `UCustomizableObjectInstance`。 | `UCustomizableObjectInstance` |
| `Set Int Parameter Value` | 设置实例的整型参数（如选项ID）。 | `UCustomizableObjectInstance` |
| `Set Float Parameter Value` | 设置实例的浮点型参数（如颜色混合因子）。 | `UCustomizableObjectInstance` |
| `Set Bool Parameter Value` | 设置实例的布尔型参数。 | `UCustomizableObjectInstance` |
| `Set Color Parameter Value` | 设置实例的颜色参数。 | `UCustomizableObjectInstance` |
| `Set Texture Parameter Value` | 设置实例的纹理参数。 | `UCustomizableObjectInstance` |
| `Set Skeletal Mesh Parameter Value` | 设置实例的骨骼网格体参数。 | `UCustomizableObjectInstance` |
| `Update Instance` | 根据当前参数值异步更新实例，生成或更新其 Skeletal Mesh 组件。 | `UCustomizableObjectInstance` |
| `Synchronous Update` | 同步更新实例（注意：可能阻塞主线程，仅用于特定情况）。 | `UCustomizableObjectInstance` |
| `Get Skeletal Mesh Components` | 获取实例生成后的所有 Skeletal Mesh 组件。 | `UCustomizableObjectInstance` |

### 使用示例（蓝图描述）

1.  **编译对象**：在编辑器中设计好 `UCustomizableObject` 资产后，调用其 `Compile` 节点。此操作通常在编辑器中完成，或通过 `UCustomizableObjectEditorFunctionLibrary::CompileCustomizableObjectSynchronously` 在蓝图中触发。
2.  **创建实例**：使用 `UCustomizableObjectInstance` 的 `Create` 节点，传入编译好的 `UCustomizableObject` 作为源对象。
3.  **设置参数**：根据玩家输入，使用 `SetXxx Parameter Value` 系列节点修改实例的各个参数（如 `SetIntParameterValue(“HairStyle”, 3)`）。
4.  **更新并应用**：调用 `Update Instance` 节点。系统将异步生成新的网格体和纹理。完成后，会触发 `Updated` 委托。在委托回调中，你可以获取生成的 `USkeletalMeshComponent` 并将其附加到你的角色 Actor 上。

## C++ 用法

Mutable 的核心流程在 C++ 中更加清晰和高效。

### 头文件引入

```cpp
#include "MuCO/CustomizableObject.h"
#include "MuCO/CustomizableObjectInstance.h"
```

### 基本用法

以下代码展示了一个最基本的“编译-创建-更新”循环。此代码来源于编辑器工具和运行时测试的常见模式。
```cpp
// 假设你已经持有一个编译好的 UCustomizableObject* 指针 MyObject
UCustomizableObjectInstance* MyInstance = NewObject<UCustomizableObjectInstance>();
MyInstance->SetObject(MyObject);

// 设置参数
MyInstance->SetIntParameter(FName("BodyType"), 2);
MyInstance->SetFloatParameter(FName("BellySize"), 0.7f);
MyInstance->SetColorParameter(FName("SkinColor"), FLinearColor(0.8f, 0.6f, 0.4f));

// 绑定更新完成回调
FOnUpdatedDelegate OnUpdateCompleted;
OnUpdateCompleted.BindLambda([this, MyInstance]()
{
    if (USkeletalMeshComponent* GeneratedComp = MyInstance->GetFirstSkeletalMeshComponent())
    {
        // 将生成的网格组件附加到你的角色
        MyCharacter->SetMeshComponent(GeneratedComp);
    }
});
MyInstance->Updated.AddDynamic(this, &OnUpdateCompleted); // 注意：BlueprintDynamicDelegate

// 触发异步更新
MyInstance->UpdateSkeletalMesh();
```

### 进阶用法

更复杂的用法涉及**状态管理**和**部分更新**。此模式常见于需要快速切换角色外观状态（如穿戴不同装备套装）的场景。
```cpp
// 定义并设置状态
FName StateName = FName("HeavyArmor");
MyInstance->SetState(StateName);

// 在该状态下，可以强制一些参数的值，无论玩家如何设置
TMap<FName, FString> ForcedParams;
ForcedParams.Add(FName("HelmetVisible"), TEXT("1"));
ForcedParams.Add(FName("ArmorMaterial"), TEXT("M_Iron"));
MyInstance->SetForcedParameterValues(StateName, ForcedParams);

// 设置玩家控制的参数（仅影响未被强制覆盖的参数）
MyInstance->SetFloatParameter(FName("Dirtiness"), 0.1f);

// 触发更新
MyInstance->UpdateSkeletalMesh();
```

## Demo 示例

一个最小的可运行示例，展示如何在 C++ 中使用 Mutable。

### MyCustomizableActor.h
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "MuCO/CustomizableObjectInstance.h"
#include "MyCustomizableActor.generated.h"

UCLASS()
class AMyCustomizableActor : public AActor
{
    GENERATED_BODY()

public:
    AMyCustomizableActor();

    virtual void BeginPlay() override;

    // Mutable 对象和实例
    UPROPERTY(EditAnywhere, Category = "Mutable")
    TObjectPtr<UCustomizableObject> SourceObject;

    UPROPERTY()
    TObjectPtr<UCustomizableObjectInstance> Instance;

    // 更新完成回调
    UFUNCTION()
    void OnInstanceUpdated(UCustomizableObjectInstance* UpdatedInstance);
};
```

### MyCustomizableActor.cpp
```cpp
#include "MyCustomizableActor.h"
#include "MuCO/CustomizableObject.h"
#include "Components/SkeletalMeshComponent.h"

AMyCustomizableActor::AMyCustomizableActor()
{
    PrimaryActorTick.bCanEverTick = false;
    // 创建一个默认的骨骼网格组件
    auto* MeshComp = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("RootMesh"));
    RootComponent = MeshComp;
}

void AMyCustomizableActor::BeginPlay()
{
    Super::BeginPlay();

    if (!SourceObject)
    {
        UE_LOG(LogTemp, Error, TEXT("Source Customizable Object not set!"));
        return;
    }

    // 1. 创建实例
    Instance = NewObject<UCustomizableObjectInstance>();
    Instance->SetObject(SourceObject);

    // 2. 设置一些初始参数
    Instance->SetIntParameter(FName("HairStyle"), 0);
    Instance->SetFloatParameter(FName("BodyFat"), 0.5f);

    // 3. 绑定更新完成委托
    FOnUpdatedDelegate OnUpdateDelegate;
    OnUpdateDelegate.BindUObject(this, &AMyCustomizableActor::OnInstanceUpdated);
    Instance->Updated.AddDynamic(this, &OnUpdateDelegate);

    // 4. 首次更新
    Instance->UpdateSkeletalMesh();
}

void AMyCustomizableActor::OnInstanceUpdated(UCustomizableObjectInstance* UpdatedInstance)
{
    // 检查更新是否成功
    if (UpdatedInstance->IsGenerated())
    {
        // 获取第一个生成的网格组件
        if (USkeletalMeshComponent* GenMesh = UpdatedInstance->GetFirstSkeletalMeshComponent())
        {
            // 将它应用到我们的根网格组件
            if (auto* RootMesh = Cast<USkeletalMeshComponent>(RootComponent))
            {
                RootMesh->SetSkeletalMesh(GenMesh->GetSkeletalMeshAsset());
                // 通常还需要复制材质、物理资产等
            }
        }
    }
}
```

## 模块依赖

要在你的项目中使用 Mutable 的运行时功能，你的模块只需要依赖以下标准模块，无需引入 Mutable 插件内部的特定模块（除非你需要深度集成编辑器工具）。

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | 通过 `UCustomizableObjectInstance` 的公开 API 即可完成所有运行时操作。 |

**注意**：`CustomizableObjectEditor` 和 `MutableTools` 模块是**仅编辑器**的，它们依赖 `UnrealEd` 等，仅在编辑器插件或 Cook 流程中需要。你的游戏运行时模块不应依赖它们。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `70229bdc` | [Mutable] Fix duplicated Skeletal Mesh geometry if there is multiple SKM with the same name. | 修复了当存在多个同名骨骼网格体时，生成的几何数据会重复的问题。 |
| 2026-05-26 | `2b0ca8bd` | [mutable] Fixed "Clip mesh with UV Mask" op not loading the appropriate mask mip. | 修复了“使用UV遮罩裁剪网格”操作未加载合适遮罩Mip级别的问题。 |
| 2026-05-26 | `06ea27d3` | [Mutable] Fix texture parameters using the wrong method to compute the LODBias. An incorrect LODBias | 修复了纹理参数使用错误方法计算LODBias的问题。 |
| 2026-05-26 | `e9c39661` | [Mutable] Allow more clothing asset types by using the ClothingAssetBase interface. | 通过使用ClothingAssetBase接口，支持了更多类型的布料资产。 |
| 2026-05-25 | `c8ce9ff7` | [Mutable] Fix possible data race when comparing PassthroughObjects. | 修复了比较“穿透对象”时可能出现的线程数据竞争问题。 |

### 维护评价

- **活跃维护**：插件自2024年9月从实验性状态转为测试版后，一直在积极更新。从最近的提交历史看（截至2026年5月），几乎每周都有代码提交，主要集中在**Bug修复**（如上述5个提交所示）和**功能改进**。
- **稳定性与成熟度**：虽然标记为测试版（Beta），但频繁且具体的修复表明其核心功能已相对稳定，团队正在积极处理发现的边缘情况和性能问题。
- **推荐使用**：**推荐用于有明确深度定制需求的项目**。它功能强大，性能优化，但学习曲线较陡峭，需要理解其节点图编译和运行时更新的机制。适合中大型团队在确定需要此类系统后，投入时间进行集成。对于轻量级的外观变化，使用材质实例或蓝图替换可能更简单。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable)
- [官方文档](https://github.com/anticto/Mutable-Documentation/wiki)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable/Tests) (路径: `Engine/Plugins/Mutable/Tests`)