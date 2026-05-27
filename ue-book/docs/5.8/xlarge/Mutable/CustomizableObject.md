# Mutable

> Mutable adds the tools and runtime to create customizable objects for your games.

| 属性 | 值 |
|---|---|
| 中文名 | 可变对象 |
| 分类 | CustomizableObjects |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `MutableRuntime` (Runtime), `CustomizableObject` (Runtime), `CustomizableObjectEditor` (Runtime), `MutableTools` (Runtime), `MutableValidation` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-05 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable) | |

## 用途

Mutable 是一个用于创建游戏内可高度定制化对象（如角色、装备、载具）的运行时系统。它解决的核心问题是：如何通过参数化的方式，在运行时动态组合、修改和生成游戏资源（网格、材质、纹理），从而避免为每个变体预先制作和存储大量美术资产，极大减少内存占用和资产制作时间。

它的工作原理是：在编辑器中通过节点图（类似于蓝图）定义一个“可定制对象”（Customizable Object）的生成规则，编译后生成优化的运行时模型。在游戏运行时，通过设置参数（如颜色、开关部件、选择纹理）来动态生成最终的 `USkeletalMesh` 和材质。该插件提供了完整的工具链（编辑器节点、编译器）和运行时引擎。

## 使用场景

- **角色外观定制系统**：玩家可以改变角色的发型、服装、皮肤颜色、面部特征等。
- **装备/武器变体**：无需为每种武器附魔效果或外观创建单独的网格和材质，可通过参数控制其视觉效果。
- **载具外观定制**：动态改变载具的涂装、部件（轮毂、尾翼）等。
- **材质效果参数化**：在运行时调整材质的参数，如颜色、粗糙度，实现统一材质的效果切换。
- **减少烘焙变体**：代替传统的为每个 LOD 和材质组合烘焙静态网格的方式，使用动态生成。

## 蓝图用法

### 核心节点

Mutable 主要通过 `UCustomizableObject` 和 `UCustomizableObjectInstance` 两个类暴露蓝图功能。

#### 可定制对象 (`UCustomizableObject`)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateInstance` | 为此可定制对象创建一个新的实例，参数使用默认值。 | `UCustomizableObject` |
| `GetParameterCount` | 获取此对象可实例化参数的数量。 | `UCustomizableObject` |
| `GetParameterTypeByName` | 根据参数名获取参数类型。 | `UCustomizableObject` |
| `GetParameterName` | 根据索引获取参数名称。 | `UCustomizableObject` |
| `GetEnumParameterNumValues` | 获取整数（枚举）参数的可选值数量。 | `UCustomizableObject` |
| `GetEnumParameterValue` | 获取整数（枚举）参数指定索引的值名称。 | `UCustomizableObject` |
| `GetFloatParameterDefaultValue` | 获取浮点参数的默认值。 | `UCustomizableObject` |
| `GetBoolParameterDefaultValue` | 获取布尔参数的默认值。 | `UCustomizableObject` |
| `IsCompiled` | 检查此对象是否已编译（打包后总是为真，编辑器中可能为假）。 | `UCustomizableObject` |
| `IsLoading` | 检查对象是否仍在加载中。 | `UCustomizableObject` |

#### 可定制对象实例 (`UCustomizableObjectInstance`)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetIntParameterSelectedOption` | 设置整数（枚举）参数的值。 | `UCustomizableObjectInstance` |
| `SetFloatParameterSelectedOption` | 设置浮点参数的值。 | `UCustomizableObjectInstance` |
| `SetBoolParameterSelectedOption` | 设置布尔参数的值。 | `UCustomizableObjectInstance` |
| `SetVectorParameterSelectedOption` | 设置向量参数的值。 | `UCustomizableObjectInstance` |
| `SetProjectorParameterSelectedOption` | 设置投影器参数的值（用于贴花等）。 | `UCustomizableObjectInstance` |
| `SetCurrentState` | 设置实例的当前状态（状态可控制参数可见性和更新行为）。 | `UCustomizableObjectInstance` |
| `UpdateSkeletalMeshAsync` | 触发实例的异步更新，根据当前参数生成/更新其骨骼网格。 | `UCustomizableObjectInstance` |
| `IsUpdating` | 检查此实例是否正在更新中。 | `UCustomizableObjectInstance` |
| `GetGeneratedSkeletalMesh` | 获取更新后生成的骨骼网格。 | `UCustomizableObjectInstance` |
| `GetComponentNames` | 获取为此实例生成的组件名称列表。 | `UCustomizableObjectInstance` |

#### 可定制骨骼网格组件 (`UCustomizableSkeletalComponent`)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetCustomizableObjectInstance` | 设置要使用的 `UCustomizableObjectInstance`。 | `UCustomizableSkeletalComponent` |
| `UpdateSkeletalMeshAsync` | 便捷方法，异步更新关联实例的网格并应用到此组件。 | `UCustomizableSkeletalComponent` |

### 使用示例（蓝图描述）

1.  **创建并配置实例**：首先，从 `UCustomizableObject` 资产（在编辑器中通过节点图创建）调用 `CreateInstance` 节点生成一个 `UCustomizableObjectInstance`。
2.  **设置参数**：使用 `Set...ParameterSelectedOption` 系列节点（如 `SetIntParameterSelectedOption`），为实例的各个参数（如“发型”、“眼睛颜色”）设置想要的值。
3.  **更新网格**：将实例连接到一个 `UCustomizableSkeletalComponent`（或直接操作实例），然后调用 `UpdateSkeletalMeshAsync` 节点。系统会根据参数异步生成网格。
4.  **监听更新完成**：绑定 `UpdatedDelegate`（蓝图可绑定事件），在网格生成完成后获取生成的 `USkeletalMesh` 并应用到渲染组件。
5.  **运行时交互**：在玩家进行UI操作（如滑动颜色滑块）时，实时修改对应参数的值，并再次调用 `UpdateSkeletalMeshAsync` 来刷新外观。

## C++ 用法

### 头文件引入

```cpp
#include "MuCO/CustomizableObject.h"
#include "MuCO/CustomizableObjectInstance.h"
#include "MuCO/CustomizableSkeletalComponent.h"
#include "MuCO/ICustomizableObjectModule.h"
```

### 基本用法

以下示例展示了如何在 C++ 中创建并更新一个可定制对象实例。

```cpp
// 假设 CO_Object 是一个已加载的 UCustomizableObject 资产指针
if (UCustomizableObject* CO_Object = LoadObject<UCustomizableObject>(nullptr, TEXT("/Game/Characters/Hero_CO")))
{
    // 1. 创建实例
    UCustomizableObjectInstance* Instance = CO_Object->CreateInstance();
    if (Instance)
    {
        // 2. 设置参数值
        // 设置一个名为 “Hair_Style” 的整数（枚举）参数为 “Mohawk”
        Instance->SetIntParameterSelectedOption(TEXT("Hair_Style"), TEXT("Mohawk"));
        // 设置一个名为 “Eye_Color” 的颜色参数
        FLinearColor BlueColor(0.0f, 0.2f, 1.0f);
        Instance->SetVectorParameterSelectedOption(TEXT("Eye_Color"), FVector4f(BlueColor.R, BlueColor.G, BlueColor.B, BlueColor.A));
        // 设置一个名为 “Is_Hat_Visible” 的布尔参数为 true
        Instance->SetBoolParameterSelectedOption(TEXT("Is_Hat_Visible"), true);

        // 3. 绑定更新完成回调（可选）
        Instance->UpdatedNativeDelegate.AddUObject(this, &AMyCharacter::OnInstanceUpdated);

        // 4. 触发异步更新
        Instance->UpdateSkeletalMeshAsync();
    }
}
```

### 进阶用法：使用可定制骨骼网格组件

更常见的用法是通过 `UCustomizableSkeletalComponent` 管理实例和网格的关联。

```cpp
// 在角色类 (AMyCharacter.h) 中
UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Customization")
UCustomizableSkeletalComponent* CustomizableComponent;

// 在 AMyCharacter::BeginPlay() 或构造函数中
CustomizableComponent = CreateDefaultSubobject<UCustomizableSkeletalComponent>(TEXT("CustomizableSkelComp"));
CustomizableComponent->SetupAttachment(GetMesh()); // 附加到主网格组件

// 加载并设置实例
if (UCustomizableObject* CO = LoadObject<UCustomizableObject>(...))
{
    UCustomizableObjectInstance* MyInstance = CO->CreateInstance();
    CustomizableComponent->SetCustomizableObjectInstance(MyInstance);
}

// 在某个时刻（如玩家换装），修改参数并更新
void AMyCharacter::ChangeHairStyle(FString NewStyleName)
{
    if (UCustomizableObjectInstance* Instance = CustomizableComponent->GetCustomizableObjectInstance())
    {
        Instance->SetIntParameterSelectedOption(TEXT("Hair_Style"), NewStyleName);
        // 使用组件的方法触发更新，它会自动处理网格应用
        CustomizableComponent->UpdateSkeletalMeshAsync();
    }
}

// 回调函数
void AMyCharacter::OnInstanceUpdated(UCustomizableObjectInstance* UpdatedInstance)
{
    // 网格已生成，可以在此做一些后续处理，例如重新绑定动画
    UE_LOG(LogTemp, Log, TEXT("Customizable object instance update complete."));
}
```

## Demo 示例

以下是一个最小化的可运行示例，展示如何在 Actor 中设置和更新 Mutable 实例。

```cpp
// MyMutableActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MuCO/CustomizableObjectInstance.h" // 用于回调委托
#include "MyMutableActor.generated.h"

class UCustomizableObject;
class UCustomizableObjectInstance;
class UCustomizableSkeletalComponent;

UCLASS()
class AMyMutableActor : public AActor
{
    GENERATED_BODY()

public:
    AMyMutableActor();

protected:
    virtual void BeginPlay() override;

    // 蓝图可调用的函数，用于演示修改参数
    UFUNCTION(BlueprintCallable, Category = "Demo")
    void ChangeToCharacterA();

    UFUNCTION(BlueprintCallable, Category = "Demo")
    void ChangeToCharacterB();

private:
    // 更新完成的回调
    UFUNCTION()
    void OnCustomizationUpdated(UCustomizableObjectInstance* Instance);

    UPROPERTY(VisibleAnywhere)
    USceneComponent* Root;

    // 关键组件：可定制骨骼网格组件
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Meta = (AllowPrivateAccess = "true"))
    UCustomizableSkeletalComponent* CustomizableSkelComp;

    // 引用的可定制对象资产（假设在蓝图中设置）
    UPROPERTY(EditAnywhere, Category = "Setup")
    TSoftObjectPtr<UCustomizableObject> CustomizableObjectAsset;

    // 我们创建和控制的实例
    UPROPERTY()
    TObjectPtr<UCustomizableObjectInstance> MyInstance;
};
```

```cpp
// MyMutableActor.cpp
#include "MyMutableActor.h"
#include "MuCO/CustomizableObject.h"
#include "MuCO/CustomizableSkeletalComponent.h"
#include "Components/SkeletalMeshComponent.h"

AMyMutableActor::AMyMutableActor()
{
    PrimaryActorTick.bCanEverTick = false;

    Root = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
    RootComponent = Root;

    // 创建可定制骨骼网格组件
    CustomizableSkelComp = CreateDefaultSubobject<UCustomizableSkeletalComponent>(TEXT("CustomizableSkel"));
    CustomizableSkelComp->SetupAttachment(Root);
}

void AMyMutableActor::BeginPlay()
{
    Super::BeginPlay();

    // 加载可定制对象
    if (UCustomizableObject* CO = CustomizableObjectAsset.LoadSynchronous())
    {
        // 创建实例
        MyInstance = CO->CreateInstance();
        if (MyInstance)
        {
            // 将实例交给组件管理
            CustomizableSkelComp->SetCustomizableObjectInstance(MyInstance);

            // 绑定更新完成事件
            MyInstance->UpdatedNativeDelegate.AddUObject(this, &AMyMutableActor::OnCustomizationUpdated);

            // 设置初始参数并开始第一次更新
            MyInstance->SetIntParameterSelectedOption(TEXT("Character"), TEXT("Default"));
            MyInstance->SetBoolParameterSelectedOption(TEXT("ShowHelmet"), true);
            CustomizableSkelComp->UpdateSkeletalMeshAsync();

            UE_LOG(LogTemp, Log, TEXT("Mutable instance created and initial update triggered."));
        }
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load Customizable Object asset!"));
    }
}

void AMyMutableActor::ChangeToCharacterA()
{
    if (MyInstance)
    {
        MyInstance->SetIntParameterSelectedOption(TEXT("Character"), TEXT("A"));
        MyInstance->SetBoolParameterSelectedOption(TEXT("ShowHelmet"), false);
        CustomizableSkelComp->UpdateSkeletalMeshAsync();
    }
}

void AMyMutableActor::ChangeToCharacterB()
{
    if (MyInstance)
    {
        MyInstance->SetIntParameterSelectedOption(TEXT("Character"), TEXT("B"));
        MyInstance->SetBoolParameterSelectedOption(TEXT("ShowHelmet"), true);
        CustomizableSkelComp->UpdateSkeletalMeshAsync();
    }
}

void AMyMutableActor::OnCustomizationUpdated(UCustomizableObjectInstance* Instance)
{
    if (Instance == MyInstance)
    {
        UE_LOG(LogTemp, Log, TEXT("Customization updated for actor %s"), *GetName());
        // 更新完成后的逻辑，例如播放一个换装完成的动画或特效
    }
}
```

## 模块依赖

要使用 Mutable 运行时功能，你的项目模块需要依赖 `CustomizableObject` 模块。如果需要编辑器编译功能，则需要额外依赖 `CustomizableObjectEditor` 模块。

| 模块 | 用途 |
|---|---|
| `CustomizableObject` | 提供 `UCustomizableObject`, `UCustomizableObjectInstance`, `UCustomizableSkeletalComponent` 等核心运行时类。 |
| `CustomizableObjectEditor` | 提供节点图编辑器、编译器等编辑器工具。 |
| `MutableTools` | 底层可定制对象模型的编译和处理工具库。 |
| `MutableRuntime` | 底层可定制对象运行时引擎核心。 |
| `DerivedDataCache` | 用于在编辑器中缓存编译后的可定制对象数据，加速迭代。 |

**注意**：`CustomizableObject` 模块的 `Build.cs` 显示它依赖了 `UnrealEd`, `EditorStyle` 等编辑器模块。这意味着如果在非编辑器环境（如纯游戏客户端）中使用 `CustomizableObject` 模块，可能需要确保条件编译（`WITH_EDITOR`）正确处理，或者将依赖关系调整到更合适的模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `70229bdc` | [Mutable] Fix duplicated Skeletal Mesh geometry if there is multiple SKM with the same name. | 修复存在同名骨骼网格时几何体重复的 bug。 |
| 2026-05-26 | `2b0ca8bd` | [mutable] Fixed "Clip mesh with UV Mask" op not loading the appropriate mask mip. | 修复“使用UV蒙版裁剪网格”操作未加载正确蒙版 mip 级别的问题。 |
| 2026-05-26 | `06ea27d3` | [Mutable] Fix texture parameters using the wrong method to compute the LODBias. | 修复纹理参数计算 LODBias 时使用错误方法的问题。 |
| 2026-05-26 | `e9c39661` | [Mutable] Allow more clothing asset types by using the ClothingAssetBase interface. | 通过使用 ClothingAssetBase 接口支持更多类型的布料资产。 |
| 2026-05-25 | `c8ce9ff7` | [Mutable] Fix possible data race when comparing PassthroughObjects. | 修复比较 PassthroughObjects 时可能的数据竞争问题。 |

### 维护评价

Mutable 插件目前处于 **Beta** 状态，从历史记录看仍在积极维护中。

- **创建时间**：2024年9月，非常新的插件（约2年）。
- **活跃度**：最近一次更新在2026年5月，过去一周内有多次提交，表明维护非常活跃。提交内容主要是 bug 修复和稳定性改进。
- **功能阶段**：虽然标记为 Beta，但功能已相当完整，从实验性状态迁移出来表明已具备生产可用性，但仍可能有一些未发现的边界情况问题。
- **推荐度**：**强烈推荐用于新项目**。对于需要角色或物品高度定制化的游戏项目，Mutable 是 Epic 官方提供的强大解决方案，能够显著优化内存和资产制作流程。建议在项目早期集成，并充分测试其性能和工作流是否符合项目需求。对于现有项目，评估集成成本后也可考虑引入。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/Customizable-Objects-in-Unreal-Engine/) （Epic 官方文档链接，通常包含在 .uplugin 或插件描述中，此处为合理推断）
- 测试用例：在提供的源码信息中未包含测试文件路径。通常可能位于 `Engine/Plugins/Mutable/Tests/` 或 `Engine/Tests/Mutable/` 目录下，或集成在 `CustomizableObjectEditor` 模块中。