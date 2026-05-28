# Mutable

> Mutable adds the tools and runtime to create customizable objects for your games.

| 属性 | 值 |
|---|---|
| 中文名 | 可变物体 |
| 分类 | CustomizableObjects |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（源码和蓝图资产） |
| 模块 | `CustomizableObject` (Runtime), `CustomizableObjectEditor` (Runtime), `MutableRuntime` (Runtime), `MutableTools` (Runtime), `MutableValidation` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-05 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable) | |

## 用途

Mutable 插件是一个强大的运行时可自定义对象系统。它允许设计师和开发者在 Unreal Editor 中通过可视化的节点图编辑器（`CustomizableObject`）定义一个对象的所有可变部分（如网格、材质、纹理、骨骼、物理资源等），并将其编译成一个高效的“模型”。在游戏运行时，系统可以根据玩家的选择或游戏逻辑（如装备、发型、肤色等参数），动态地“实例化”并生成最终的 Skeletal Mesh、材质和纹理，实现高性能的实时换装与自定义，避免了传统预烘焙所有组合带来的巨大内存和磁盘开销。

**核心解决的问题**：在大型游戏（尤其是 MMO、RPG、装扮类游戏）中，如何高效、灵活地实现海量的角色/物品外观自定义组合，同时控制内存和性能开销。

## 使用场景

- **RPG/MMO 角色创建系统**：允许玩家在角色创建界面选择发型、脸型、肤色、装备等，并实时预览最终效果。
- **游戏内装备/外观系统**：实现装备的实时换装，包括网格替换、材质叠加（如血迹、污渍）、UV 投影（纹身、贴花）。
- **虚拟试衣间/形象定制应用**：为用户提供高度自由的虚拟形象定制。
- **程序化生成内容**：通过组合不同的基础资产，在运行时生成大量外观各异的 NPC 或物品。

## 蓝图用法

Mutable 提供了丰富的蓝图接口，主要围绕 `UCustomizableObject`（可自定义对象模板）和 `UCustomizableObjectInstance`（可自定义对象实例）展开。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Instance` | 基于一个 `UCustomizableObject` 资产创建一个新的运行时实例。 | `UCustomizableObject` |
| `Set Int Parameter Selected Option` | 设置一个整数（枚举）参数的当前选中值。 | `UCustomizableObjectInstance` |
| `Set Bool Parameter Selected Option` | 设置一个布尔参数的当前值。 | `UCustomizableObjectInstance` |
| `Set Float Parameter Selected Option` | 设置一个浮点参数的当前值。 | `UCustomizableObjectInstance` |
| `Set Vector Parameter Selected Option` | 设置一个向量/颜色参数的当前值。 | `UCustomizableObjectInstance` |
| `Set Projector Parameter Selected Option` | 设置一个投影器参数（用于 UV 投影）的当前值。 | `UCustomizableObjectInstance` |
| `Update Skeletal Mesh Async` | 异步触发实例的更新，根据当前参数值生成新的 Skeletal Mesh 和相关资源。 | `UCustomizableObjectInstance` |
| `Multilayer Projector Add Layer` | 向多层投影器参数添加一个新的图层。 | `UCustomizableObjectInstance` |
| `Multilayer Projector Update Layer` | 更新多层投影器参数中指定图层的数据（位置、旋转、缩放、图像、透明度）。 | `UCustomizableObjectInstance` |
| `Set Keep Ownership Of Generated Resources` | 设置实例是否保留对生成资源（如 Skeletal Mesh）的所有权，影响资源的重用和回收策略。 | `UCustomizableObjectInstance` |
| `Bake` | 将实例当前状态的资源烘焙为持久化资产。 | `UCustomizableObjectInstance` |

### 使用示例（蓝图描述）

1.  **创建并更新一个实例**：
    *   从一个 `UCustomizableObject` 资产节点拖出引脚，调用 `Create Instance` 节点，得到一个 `UCustomizableObjectInstance` 对象。
    *   调用 `Set Int Parameter Selected Option`，指定参数名称（如 `“HairStyle”`）和要选中的值（如 `“Mohawk”`）。
    *   调用 `Update Skeletal Mesh Async`。系统将在后台根据新参数值生成网格。
    *   监听实例的 `UpdatedDelegate`。当更新成功后，实例的各个组件（通过 `GetComponentNames` 获取）对应的 Skeletal Mesh 就会被更新。

2.  **使用多层投影器添加纹身**：
    *   获取一个具有多层投影器参数（如 `“BodyDecals”`）的实例。
    *   调用 `Multilayer Projector Add Layer` 添加一个图层。
    *   构造一个 `FMultilayerProjectorLayer` 结构体，设置其 `Position`、`Direction`、`Scale`、`Image`（纹身纹理资产引用）和 `Opacity`。
    *   调用 `Multilayer Projector Update Layer` 将该图层数据写入实例。
    *   调用 `Update Skeletal Mesh Async` 使投影生效。

## C++ 用法

### 头文件引入

```cpp
#include "MuCO/CustomizableObject.h"
#include "MuCO/CustomizableObjectInstance.h"
#include "MuCO/CustomizableObjectSystem.h"
```

### 基本用法

以下代码演示了如何创建一个可自定义对象实例并设置其参数。

```cpp
// 假设我们有一个名为 MyCustomizableObject 的 UCustomizableObject* 资产（通常通过 UPROPERTY 持有或加载）

// 1. 确保 Mutable 系统已初始化 (通常在游戏启动时由插件自动完成)
UCustomizableObjectSystem* MutableSystem = UCustomizableObjectSystem::GetInstance();
if (MutableSystem && MutableSystem->IsActive())
{
    // 2. 创建一个实例
    UCustomizableObjectInstance* NewInstance = MyCustomizableObject->CreateInstance();
    
    // 3. 设置一些参数
    NewInstance->SetIntParameterSelectedOption(TEXT("SkinColor"), TEXT("Pale"));
    NewInstance->SetBoolParameterSelectedOption(TEXT("HasGlasses"), true);
    
    // 4. 设置更新回调（可选，用于异步通知）
    FInstanceUpdateNativeDelegate OnUpdateFinished;
    OnUpdateFinished.BindLambda([NewInstance](const FUpdateContext& Context)
    {
        if (Context.UpdateResult == EUpdateResult::Success)
        {
            // 更新成功，此时可以获取生成的 SkeletalMesh
            UE_LOG(LogTemp, Log, TEXT("Customizable Object Instance updated successfully."));
        }
    });
    NewInstance->UpdatedNativeDelegate.Add(OnUpdateFinished);
    
    // 5. 触发异步更新
    NewInstance->UpdateSkeletalMeshAsync();
}
```

**来源文件**: `Public/MuCO/CustomizableObject.h`, `Public/MuCO/CustomizableObjectInstance.h`

### 进阶用法

使用 `ICustomizableObjectModule` 进行扩展注册，以及使用 `FCustomizableObjectInstanceDescriptor` 进行实例状态的序列化与反序列化。

```cpp
// 引入扩展接口
#include "MuCO/ICustomizableObjectModule.h"
#include "MuCO/CustomizableObjectInstanceDescriptor.h"

// 注册一个自定义的扩展
class UMyCustomExtension : public UCustomizableObjectExtension
{
    // ... 实现 GetPinTypes, OnSkeletalMeshCreated 等虚函数
};

// 在模块启动时注册
void FMyGameModule::StartupModule()
{
    if (ICustomizableObjectModule::IsAvailable())
    {
        ICustomizableObjectModule& MutableModule = ICustomizableObjectModule::Get();
        UMyCustomExtension* MyExtension = NewObject<UMyCustomExtension>();
        MutableModule.RegisterExtension(MyExtension);
    }
}

// 序列化实例描述符（用于存档、网络同步等）
void SaveInstanceState(UCustomizableObjectInstance* Instance, FArchive& Ar)
{
    FCustomizableObjectInstanceDescriptor Descriptor;
    // 从实例拷贝当前参数状态到描述符
    // Descriptor.CopyFrom(Instance); // 需要具体实现，此处为示意
    Descriptor.SaveDescriptor(Ar, false);
}

// 反序列化实例描述符
void LoadInstanceState(UCustomizableObjectInstance* Instance, FArchive& Ar)
{
    FCustomizableObjectInstanceDescriptor Descriptor;
    Descriptor.LoadDescriptor(Ar);
    // 将描述符中的参数状态应用到实例
    // Descriptor.ApplyTo(Instance); // 需要具体实现，此处为示意
    Instance->UpdateSkeletalMeshAsync();
}
```

**来源文件**: `Public/MuCO/ICustomizableObjectModule.h`, `Public/MuCO/CustomizableObjectInstanceDescriptor.h`, `Public/MuCO/CustomizableObjectExtension.h`

## Demo 示例

一个最小化的 C++ 示例，展示如何创建一个实例并更新它。

**MyCustomizableActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
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

    UPROPERTY(EditAnywhere, Category = "Customization")
    UCustomizableObject* CustomizableObjectAsset;

    UPROPERTY()
    UCustomizableObjectInstance* CurrentInstance;

    void ApplyNewHairStyle(const FString& NewHairStyle);

private:
    UFUNCTION()
    void OnInstanceUpdated(UCustomizableObjectInstance* Instance);
};
```

**MyCustomizableActor.cpp**
```cpp
#include "MyCustomizableActor.h"
#include "MuCO/CustomizableObject.h"

AMyCustomizableActor::AMyCustomizableActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyCustomizableActor::BeginPlay()
{
    Super::BeginPlay();

    if (CustomizableObjectAsset && !CurrentInstance)
    {
        // 创建实例
        CurrentInstance = CustomizableObjectAsset->CreateInstance();
        
        // 绑定更新完成委托
        CurrentInstance->UpdatedNativeDelegate.AddDynamic(this, &AMyCustomizableActor::OnInstanceUpdated);
        
        // 设置默认参数并更新
        CurrentInstance->SetIntParameterSelectedOption(TEXT("HairStyle"), TEXT("Default"));
        CurrentInstance->UpdateSkeletalMeshAsync();
    }
}

void AMyCustomizableActor::ApplyNewHairStyle(const FString& NewHairStyle)
{
    if (CurrentInstance)
    {
        CurrentInstance->SetIntParameterSelectedOption(TEXT("HairStyle"), NewHairStyle);
        CurrentInstance->UpdateSkeletalMeshAsync();
    }
}

void AMyCustomizableActor::OnInstanceUpdated(UCustomizableObjectInstance* Instance)
{
    if (Instance == CurrentInstance)
    {
        // 更新成功，此处可以获取并设置新的 SkeletalMesh 到组件上
        // 例如：SkeletalMeshComponent->SetSkeletalMesh(Instance->GetComponentSkeletalMesh(TEXT("Body")));
        UE_LOG(LogTemp, Log, TEXT("Character customization updated."));
    }
}
```

## 模块依赖

要使用 Mutable 插件的功能，你的项目模块通常需要依赖以下核心模块：

| 模块 | 用途 |
|---|---|
| `CustomizableObject` | **必需**。包含可自定义对象（`UCustomizableObject`）、实例（`UCustomizableObjectInstance`）和系统（`UCustomizableObjectSystem`）的核心运行时类和蓝图接口。 |
| `MutableRuntime` | **必需**。Mutable 核心运行时库，负责底层的网格、纹理生成和内存管理。 |
| `MutableTools` | **必需**。用于编译可自定义对象图和生成模型数据。在编辑器中和烘焙时使用。 |
| `CustomizableObjectEditor` | **仅编辑器**。提供节点图编辑器、编译 UI 和调试工具。 |
| `MutableValidation` | **可选**。提供额外的数据验证功能，用于在编辑器中检查可自定义对象的设置。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `70229bdc` | [Mutable] Fix duplicated Skeletal Mesh geometry if there is multiple SKM with the same name. | 修复了当存在多个同名骨骼网格体时，网格体几何数据被重复的问题。 |
| 2026-05-26 | `2b0ca8bd` | [mutable] Fixed "Clip mesh with UV Mask" op not loading the appropriate mask mip. | 修复了“使用 UV 蒙版裁剪网格”操作未加载正确蒙版 Mip 的问题。 |
| 2026-05-26 | `06ea27d3` | [Mutable] Fix texture parameters using the wrong method to compute the LODBias. An incorrect LODBias | 修复了纹理参数使用错误方法计算 LOD 偏移的问题。 |
| 2026-05-26 | `e9c39661` | [Mutable] Allow more clothing asset types by using the ClothingAssetBase interface. | 通过使用 ClothingAssetBase 接口，允许支持更多类型的布料资产。 |
| 2026-05-25 | `c8ce9ff7` | [Mutable] Fix possible data race when comparing PassthroughObjects. | 修复了在比较 PassthroughObjects 时可能出现的数据竞争问题。 |

### 维护评价

- **活跃维护**：插件自 2024 年 9 月从实验状态移至测试版以来，近期（2026年5月）仍有多次实质性 Bug 修复和功能改进更新，表明项目处于**积极维护**中。
- **稳定性**：从近期提交信息看，修复集中在具体的渲染、数据和并发问题上，说明插件在持续进行稳定性和正确性优化。
- **状态**：当前版本为 `1.8.0`，标记为 Beta 版（`⚠️ 是`）。这意味着 API 和功能可能在后续版本中发生改变，但核心架构已相对稳定。
- **推荐使用**：对于需要在 Unreal Engine 5.8 中实现复杂、高性能运行时自定义对象的项目，**强烈推荐使用**此插件。它解决了传统自定义系统面临的组合爆炸和性能瓶颈问题，是 Epic Games 官方维护的成熟解决方案。使用者应注意其 Beta 状态，并关注版本更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable)
- 官方文档（在 `.uplugin` 中未提供）
- 测试用例（在提供的文件列表中未明确标识，通常位于插件或引擎测试目录下）