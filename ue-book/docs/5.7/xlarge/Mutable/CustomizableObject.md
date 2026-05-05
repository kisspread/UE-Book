# Mutable

> Mutable adds the tools and runtime to create customizable objects for your games.

| 属性 | 值 |
|---|---|
| 分类 | CustomizableObjects |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `MutableRuntime` (Runtime), `CustomizableObject` (Runtime), `MutableTools` (Runtime), `CustomizableObjectEditor` (Runtime), `MutableValidation` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-09-26 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Mutable) | |

## 用途

Mutable 是 UE5 的**可定制对象系统**，用于在运行时根据参数动态生成和组合骨骼网格体、材质和纹理。它解决的核心问题是：**如何在不为每种外观组合烘焙独立资产的前提下，高效地运行时生成大量视觉变体**。

典型应用场景：角色换装系统——玩家可以选择不同的发型、服装、肤色、纹身等，每种组合都会在运行时通过 Mutable 的编译模型（Model）和参数系统实时生成最终的 Skeletal Mesh 和材质，无需预先烘焙所有排列组合。

系统架构分为三层：
1. **编译期**（MutableTools）：将编辑器中的可定制对象图（Customizable Object Graph）编译为高效的运行时模型（Model）
2. **运行时**（MutableRuntime）：执行模型，根据参数生成网格体和纹理数据
3. **UE 集成层**（CustomizableObject）：将 Mutable 核心与 UE 的 SkeletalMesh、Material、LOD、Streaming 等系统对接

## 使用场景

- 你在做角色换装/捏脸系统，需要运行时组合大量外观变体 → 用 Mutable
- 你需要根据玩家选择动态生成不同材质/纹理组合的网格体 → 用 Mutable
- 你需要在编辑器中可视化编辑可定制对象的参数和状态 → 用 Mutable 的编辑器工具
- 你需要将可定制对象烘焙为静态资产用于打包 → 用 Mutable 的烘焙管线
- 你需要管理可定制对象实例的 LOD 和流式加载 → 用 Mutable 的 LOD 管理系统

## 蓝图用法

### 核心节点

#### 实例管理（UCustomizableObjectInstance）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetIntParameterSelectedOption` | 设置整数参数的选中选项（按名称） | `UCustomizableObjectInstance` |
| `GetIntParameterSelectedOption` | 获取整数参数的当前选中选项 | `UCustomizableObjectInstance` |
| `SetFloatParameterSelectedOption` | 设置浮点参数值 | `UCustomizableObjectInstance` |
| `GetFloatParameterSelectedOption` | 获取浮点参数值 | `UCustomizableObjectInstance` |
| `SetBoolParameterSelectedOption` | 设置布尔参数值 | `UCustomizableObjectInstance` |
| `GetBoolParameterSelectedOption` | 获取布尔参数值 | `UCustomizableObjectInstance` |
| `SetVectorParameterSelectedOption` | 设置向量/颜色参数值 | `UCustomizableObjectInstance` |
| `SetTextureParameterSelectedOption` | 设置纹理参数值 | `UCustomizableObjectInstance` |
| `UpdateSkeletalMeshAsync` | 异步更新骨骼网格体 | `UCustomizableObjectInstance` |
| `Bake` | 将当前实例烘焙为静态资产 | `UCustomizableObjectInstance` |

#### 组件（UCustomizableSkeletalComponent）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetCustomizableObjectInstance` | 设置关联的可定制对象实例 | `UCustomizableSkeletalComponent` |
| `GetCustomizableObjectInstance` | 获取关联的可定制对象实例 | `UCustomizableSkeletalComponent` |
| `SetComponentName` | 设置组件名称（替代已弃用的 ComponentIndex） | `UCustomizableSkeletalComponent` |
| `GetComponentName` | 获取组件名称 | `UCustomizableSkeletalComponent` |
| `UpdateSkeletalMeshAsync` | 异步更新该组件的骨骼网格体 | `UCustomizableSkeletalComponent` |
| `UpdateSkeletalMeshAsyncResult` | 异步更新并带回调 | `UCustomizableSkeletalComponent` |
| `SetSkipSetReferenceSkeletalMesh` | 设置是否跳过自动替换参考网格体 | `UCustomizableSkeletalComponent` |
| `SetSkipSetSkeletalMeshOnAttach` | 设置是否跳过附加时自动替换网格体 | `UCustomizableSkeletalComponent` |

#### 轻量级用法（UCustomizableObjectInstanceUsage）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetCustomizableObjectInstance` | 设置关联实例 | `UCustomizableObjectInstanceUsage` |
| `AttachTo` | 附加到 SkeletalMeshComponent | `UCustomizableObjectUsage` |
| `GetAttachParent` | 获取附加的父组件 | `UCustomizableObjectInstanceUsage` |
| `UpdateSkeletalMeshAsync` | 异步更新网格体 | `UCustomizableObjectInstanceUsage` |
| `UpdateSkeletalMeshAsyncResult` | 异步更新并带回调 | `UCustomizableObjectInstanceUsage` |
| `SetComponentName` | 设置组件名称 | `UCustomizableObjectInstanceUsage` |

#### Actor（ACustomizableSkeletalMeshActor）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetCustomizableObjectInstance` | 获取该 Actor 的可定制对象实例 | `ACustomizableSkeletalMeshActor` |
| `GetSkeletalMeshComponent` | 按名称获取骨骼网格体组件 | `ACustomizableSkeletalMeshActor` |

#### 动画标签（UCustomizableObjectInstanceUserData）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetAnimationGameplayTags` | 获取实例的动画 GameplayTag | `UCustomizableObjectInstanceUserData` |
| `SetAnimationGameplayTags` | 设置实例的动画 GameplayTag | `UCustomizableObjectInstanceUserData` |

### 使用示例（蓝图描述）

**基本换装流程：**

1. 创建一个 `UCustomizableObjectInstance`（引用一个编译好的 `UCustomizableObject` 资产）
2. 在场景中放置 `ACustomizableSkeletalMeshActor` 或添加 `UCustomizableSkeletalComponent` 到任意 Actor
3. 将 Instance 设置到 Component 上：`SetCustomizableObjectInstance`
4. 修改参数：调用 `SetIntParameterSelectedOption("HairStyle", "Mohawk")` 等
5. 触发更新：调用 `UpdateSkeletalMeshAsync`，网格体会在后台异步生成

**轻量级用法（非蓝图组件）：**

1. 创建 `UCustomizableObjectInstanceUsage`（UObject，比 Component 更轻量）
2. 调用 `AttachTo` 将其附加到已有的 `USkeletalMeshComponent`
3. 设置 Instance 和参数后调用 `UpdateSkeletalMeshAsync`

**多层投影器（Multilayer Projector）：**

用于在网格体表面投影纹理层（如纹身、贴花），通过 `FMultilayerProjectorLayer` 结构控制每层的位置、方向、缩放、透明度和选择的图像。

## C++ 用法

### 头文件引入

```cpp
#include "MuCO/CustomizableObject.h"
#include "MuCO/CustomizableObjectInstance.h"
#include "MuCO/CustomizableObjectSystem.h"
#include "MuCO/CustomizableSkeletalComponent.h"
#include "MuCO/CustomizableObjectInstanceUsage.h"
```

### 基本用法

```cpp
// 创建实例并设置参数
// 来源: CustomizableObjectInstance.h

UCustomizableObject* MyObject = LoadObject<UCustomizableObject>(nullptr, TEXT("/Game/MyCustomizableObject"));
UCustomizableObjectInstance* Instance = MyObject->CreateInstance();

// 设置整数参数
Instance->SetIntParameterSelectedOption(FString("HairStyle"), FString("Mohawk"));

// 设置浮点参数
Instance->SetFloatParameterSelectedOption(FString("BodyFat"), 0.5f);

// 设置布尔参数
Instance->SetBoolParameterSelectedOption(FString("HasHat"), true);

// 设置颜色参数
Instance->SetVectorParameterSelectedOption(FString("SkinColor"), FLinearColor(0.8f, 0.6f, 0.4f));

// 异步更新网格体
Instance->UpdateSkeletalMeshAsync();
```

### 进阶用法

```cpp
// 使用 CustomizableObjectInstanceUsage 进行轻量级管理
// 来源: CustomizableObjectInstanceUsage.h

UCustomizableObjectInstanceUsage* Usage = NewObject<UCustomizableObjectInstanceUsage>();
Usage->SetCustomizableObjectInstance(MyInstance);
Usage->SetComponentName(FName("Body"));
Usage->AttachTo(MySkeletalMeshComponent);

// 异步更新并带回调
Usage->UpdateSkeletalMeshAsyncResult(
    FInstanceUpdateDelegate::CreateLambda([](EUpdateResult Result)
    {
        if (Result == EUpdateResult::Success)
        {
            UE_LOG(LogTemp, Log, TEXT("Mesh updated successfully"));
        }
    }),
    /*bIgnoreCloseDist=*/ false,
    /*bForceHighPriority=*/ true
);
```

```cpp
// LOD 管理
// 来源: CustomizableInstanceLODManagement.h

UCustomizableInstanceLODManagement* LODManager = NewObject<UCustomizableInstanceLODManagement>();
LODManager->SetCustomizableObjectsUpdateDistance(5000.0f);
LODManager->SetNumberOfPriorityUpdateInstances(3);
LODManager->AddViewCenter(MyPlayerActor);

// 注册到系统
UCustomizableObjectSystem::GetInstance()->SetInstanceLODManagement(LODManager);
```

```cpp
// 使用 Descriptor 进行序列化（网络同步等场景）
// 来源: CustomizableObjectInstanceDescriptor.h

FCustomizableObjectInstanceDescriptor Descriptor(*MyObject);
Descriptor.SetIntParameterSelectedOption(FString("HairStyle"), FString("Mohawk"));

// 序列化
FMemoryWriter Writer(Bytes);
Descriptor.SaveDescriptor(Writer, /*bUseCompactDescriptor=*/ true);

// 反序列化
FMemoryReader Reader(Bytes);
FCustomizableObjectInstanceDescriptor LoadedDescriptor;
LoadedDescriptor.LoadDescriptor(Reader);
```

```cpp
// 扩展系统 - 注册自定义扩展
// 来源: CustomizableObjectExtension.h, ICustomizableObjectModule.h

class UMyCustomExtension : public UCustomizableObjectExtension
{
    GENERATED_BODY()
public:
    virtual TArray<FCustomizableObjectPinType> GetPinTypes() const override
    {
        return { { FName("MyPinType"), FText::FromString("My Type"), FLinearColor::Red } };
    }

    virtual TArray<FObjectNodeInputPin> GetAdditionalObjectNodePins() const override
    {
        FObjectNodeInputPin Pin;
        Pin.PinType = FName("MyPinType");
        Pin.PinName = FName("MyCustomPin");
        Pin.DisplayName = FText::FromString("Custom Data");
        return { Pin };
    }

    virtual void OnSkeletalMeshCreated(
        const USkeletalMesh& Mesh,
        const UCustomizableObjectInstance& Instance,
        const UCustomizableObjectInstanceUsage& Usage,
        const TArray<FInputPinDataContainer>& InputPinData) override
    {
        // 处理自定义输入数据
    }
};

// 注册扩展
ICustomizableObjectModule::Get().RegisterExtension(MyExtension);
```

```cpp
// 动画标签管理
// 来源: CustomizableObjectInstanceAssetUserData.h

UCustomizableObjectInstanceUserData* UserData = NewObject<UCustomizableObjectInstanceUserData>();
FGameplayTagContainer Tags;
Tags.AddTag(FGameplayTag::RequestGameplayTag(FName("Character.Warrior")));
UserData->SetAnimationGameplayTags(Tags);

// 动画槽位
FCustomizableObjectAnimationSlot Slot;
Slot.Name = FName("UpperBody");
Slot.AnimInstance = TSoftClassPtr<UAnimInstance>(FSoftObjectPath("/Game/ABP_UpperBody"));
UserData->AnimationSlots.Add(Slot);
```

## Demo 示例

```cpp
// MyCharacter.h
#pragma once

#include "GameFramework/Character.h"
#include "MuCO/CustomizableObjectInstance.h"
#include "MuCO/CustomizableSkeletalComponent.h"
#include "MyCharacter.generated.h"

UCLASS()
class AMyCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    AMyCharacter();

    UFUNCTION(BlueprintCallable)
    void ChangeHairStyle(const FString& StyleName);

    UFUNCTION(BlueprintCallable)
    void ChangeSkinColor(FLinearColor Color);

    UFUNCTION(BlueprintCallable)
    void ApplyOutfit();

private:
    UPROPERTY(VisibleAnywhere)
    TObjectPtr<UCustomizableSkeletalComponent> CustomizableComponent;

    UPROPERTY(EditDefaultsOnly)
    TObjectPtr<UCustomizableObject> CustomizableObjectAsset;

    UPROPERTY()
    TObjectPtr<UCustomizableObjectInstance> Instance;

    void OnMeshUpdated();
};
```

```cpp
// MyCharacter.cpp
#include "MyCharacter.h"
#include "MuCO/CustomizableObjectSystem.h"

AMyCharacter::AMyCharacter()
{
    CustomizableComponent = CreateDefaultSubobject<UCustomizableSkeletalComponent>(
        TEXT("CustomizableComponent"));
    CustomizableComponent->SetupAttachment(GetRootComponent());
}

void AMyCharacter::BeginPlay()
{
    Super::BeginPlay();

    if (CustomizableObjectAsset)
    {
        Instance = CustomizableObjectAsset->CreateInstance();
        CustomizableComponent->SetCustomizableObjectInstance(Instance);
        CustomizableComponent->SetComponentName(FName("Body"));

        // 异步生成初始网格体
        CustomizableComponent->UpdateSkeletalMeshAsyncResult(
            FInstanceUpdateDelegate::CreateUObject(this, &AMyCharacter::OnMeshUpdated));
    }
}

void AMyCharacter::ChangeHairStyle(const FString& StyleName)
{
    if (Instance)
    {
        Instance->SetIntParameterSelectedOption(FString("HairStyle"), StyleName);
        CustomizableComponent->UpdateSkeletalMeshAsync();
    }
}

void AMyCharacter::ChangeSkinColor(FLinearColor Color)
{
    if (Instance)
    {
        Instance->SetVectorParameterSelectedOption(FString("SkinColor"), Color);
        CustomizableComponent->UpdateSkeletalMeshAsync();
    }
}

void AMyCharacter::ApplyOutfit()
{
    if (Instance)
    {
        Instance->SetIntParameterSelectedOption(FString("Helmet"), FString("IronHelm"));
        Instance->SetIntParameterSelectedOption(FString("ChestArmor"), FString("PlateChest"));
        Instance->SetIntParameterSelectedOption(FString("Gloves"), FString("LeatherGloves"));
        Instance->SetBoolParameterSelectedOption(FString("HasCape"), true);
        CustomizableComponent->UpdateSkeletalMeshAsync();
    }
}

void AMyCharacter::OnMeshUpdated()
{
    UE_LOG(LogTemp, Log, TEXT("Customizable mesh updated for %s"), *GetName());
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MutableTools` | 编译器依赖，用于将可定制对象图编译为运行时模型 |
| `DerivedDataCache` | DDC 集成，缓存编译产物 |
| `MessageLog` | 编译错误/警告的消息日志输出 |

## 子模块文档

由于本插件规模为 xlarge（1449 个源文件），按子模块拆分如下：

| 子模块 | 类型 | 说明 |
|---|---|---|
| [MutableRuntime](MutableRuntime.md) | Runtime | Mutable 核心运行时引擎，负责模型执行和数据生成 |
| [CustomizableObject](CustomizableObject.md) | Runtime | UE 集成层，提供 CO/COI 系统、组件、LOD 管理、流式加载等 |
| [MutableTools](MutableTools.md) | Runtime | 编译器工具，将编辑器中的可定制对象图编译为运行时模型 |
| [CustomizableObjectEditor](CustomizableObjectEditor.md) | Runtime | 编辑器扩展，提供可定制对象的可视化编辑界面 |
| [MutableValidation](MutableValidation.md) | Runtime | 验证模块，用于验证可定制对象数据的正确性 |

## 维护状态

### 近期更新

```
- d8a2eec3ec77 [mutable] Fixed multiple SKM crashes due to an issue with the name scheme used by mutable + the process of making resource names unique (UE). - Simplified the "MakeNameUnique" approach as it was failing in some cases. - All mutable generated resources will have unique names. - Updated baking pipeline code so it takes into consideration that now the textures will have a unique suffix.
- 33443a223bf8 [Mutable] Remove cooked references to private objects in AlwaysLoadedExtensionData.
- d1ce6cb87377 [Mutable] Add option to regenerate cooked data distribution.
```

### 维护评价

Mutable 是 Epic Games 官方维护的**活跃项目**，创建于 2022 年 9 月，版本号已达 1.8.0。近期更新集中在：
- **稳定性修复**：修复了 Skeletal Mesh 崩溃问题（资源命名冲突）
- **打包优化**：清理 cooked 引用、添加 cooked 数据重新生成选项
- **持续迭代**：从代码中的大量自定义版本号（FCustomizableObjectCustomVersion）可以看出经历了数十次重大迭代

**推荐使用**：作为 Epic 官方支持的可定制对象解决方案，Mutable 是 UE5 中角色换装/外观定制的首选方案。系统成熟度高，API 完善，支持蓝图和 C++，具备完整的 LOD 管理、流式加载和烘焙管线。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Mutable)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/mutable-plugin-in-unreal-engine/)