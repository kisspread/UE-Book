# Mutable

> Mutable adds the tools and runtime to create customizable objects for your games.

| 属性 | 值 |
|---|---|
| 中文名 | 可定制对象 |
| 分类 | CustomizableObjects |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `MutableRuntime` (Runtime), `CustomizableObject` (Runtime), `MutableTools` (Runtime), `MutableValidation` (Runtime), `CustomizableObjectEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-05 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable) | |

## 用途
这个插件旨在为 Unreal Engine 5 提供一套完整的系统，用于创建和管理**可定制对象（Customizable Objects）**。它允许开发者在编辑器中通过图表化的方式定义对象的不同变体（例如，角色外观、服装、装备的组成部分），并在运行时根据玩家选择或游戏逻辑，高效地组合这些变体，生成唯一的、最终的游戏资产（如 Skeletal Mesh）。核心解决的问题是**在保证运行时性能和内存效率的前提下，实现大规模、复杂的游戏资产定制化**。

## 使用场景
- **角色创建系统**：允许玩家自由组合发型、五官、肤色、服装、盔甲等部件来创建独一无二的角色外观。
- **装备外观系统**：同一类武器（如剑）可以有不同的护手、剑刃、宝石镶嵌，通过组合产生大量视觉变体。
- **程序化生成资产**：根据规则（如怪物等级、地域）动态生成外观各异的敌人或道具模型。
- **减少美术重复劳动**：美术只需制作基础部件，系统负责组合，极大提升资产制作管线的效率和可维护性。

## 蓝图用法
Mutable 插件主要通过 `UCustomizableObject` 和 `UCustomizableObjectInstance` 类向蓝图暴露功能。

### 核心节点
| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Parameter Value` (各种参数类型) | 设置可定制对象实例的某个参数值，如整数、浮点、布尔、向量、颜色。 | `UCustomizableObjectInstance` |
| `Update Customizable Object Instance` | 根据当前设置的参数值，异步更新实例，生成或更新最终的 Skeletal Mesh。 | `UCustomizableObjectInstance` |
| `Set Skeletal Mesh` | 将更新生成的 Skeletal Mesh 应用到目标 Skeletal Mesh Component 上。 | 应用逻辑（通常由蓝图实现） |
| `Get Parameter Range` / `Get Parameter Possible Values` | 获取某个参数的可能取值范围或枚举值，用于构建UI。 | `UCustomizableObject` |

### 使用示例（蓝图描述）
1.  **初始化**：在角色蓝图中，有一个 `UCustomizableObjectInstance` 变量，并在 `BeginPlay` 时通过 `Create Customizable Object Instance` 节点（或直接实例化）将其与一个 `UCustomizableObject` 资产关联。
2.  **参数设置**：当玩家在UI界面选择发型时，通过蓝图调用 `Set Parameter Value (Integer)`，将发型参数的索引设置为玩家选择的ID。
3.  **触发更新**：设置完一系列参数后，调用 `Update Customizable Object Instance` 节点。这个节点是异步的，会生成一个更新请求。
4.  **应用结果**：监听实例的更新完成回调（如通过 `Update Completed` 事件）。在回调中，获取更新后的 `Skeletal Mesh` 资产，并使用 `Set Skeletal Mesh` 节点将其设置到角色的 Skeletal Mesh Component 上。
5.  **优化**：对于频繁变更的参数（如颜色），可以考虑使用 `Set Parameter Value` 后不立即更新，而是设置一个延迟或批量更新，避免频繁生成网格。

## C++ 用法
在 C++ 中，主要与 `UCustomizableObject` 和 `UCustomizableObjectInstance` 类交互。以下示例基于 `MutableValidation` 模块中的工具类提炼，展示了核心工作流。

### 头文件引入
```cpp
#include "MuCO/CustomizableObject.h"
#include "MuCO/CustomizableObjectInstance.h"
```

### 基本用法
**来源文件**：`Private/MuV/CustomizableObjectCompilationUtility.h`

同步编译一个可定制对象，这在命令行工具或需要确保编译完成后再进行后续操作的场景中非常有用。
```cpp
#include "MuCO/CustomizableObject.h"
#include "CustomizableObjectCompilationUtility.h" // 假设位于你的项目中

// 假设 InCustomizableObject 是一个已加载的 UCustomizableObject 指针
UCustomizableObject* MyCO = ...;
bool bSuccess = false;

// 创建编译工具并执行同步编译
TSharedPtr<FCustomizableObjectCompilationUtility> CompileUtility = MakeShareable(new FCustomizableObjectCompilationUtility());
bSuccess = CompileUtility->CompileCustomizableObject(*MyCO, true, nullptr);

if (bSuccess)
{
    UE_LOG(LogTemp, Log, TEXT("Customizable Object compiled successfully."));
}
```

### 进阶用法
**来源文件**：`Private/MuV/CustomizableObjectInstanceUpdateUtility.h` & `Private/MuV/ValidationUtils.h`

编译对象后，创建实例、设置参数并更新它。
```cpp
#include "MuCO/CustomizableObjectInstance.h"
#include "CustomizableObjectInstanceUpdateUtility.h" // 假设位于你的项目中

// 1. 确保 CO 已编译 (使用上面的 CompileUtility)
// ... 

// 2. 从编译后的 CO 创建实例
UCustomizableObject* CompiledCO = ...;
UCustomizableObjectInstance* MyInstance = CompiledCO->CreateInstance();

// 3. 设置参数（假设知道参数名为 “HairStyle”， 且为整数类型）
FString ParamName = TEXT("HairStyle");
int32 SelectedStyleIndex = 2; // 玩家选择的发型索引
MyInstance->SetIntParameter(ParamName, SelectedStyleIndex);

// 4. 使用工具类同步更新实例
TSharedPtr<FCustomizableObjectInstanceUpdateUtility> UpdateUtility = MakeShareable(new FCustomizableObjectInstanceUpdateUtility());
bool bUpdateSuccess = UpdateUtility->UpdateInstance(*MyInstance);

if (bUpdateSuccess)
{
    // 5. 获取更新后的 Skeletal Mesh
    USkeletalMesh* NewMesh = MyInstance->GetSkeletalMesh();
    if (NewMesh)
    {
        // 将新网格应用到某个 SkeletalMeshComponent
        MySkeletalMeshComponent->SetSkeletalMesh(NewMesh);
    }
}
```

## Demo 示例
一个最小的 C++ 示例，展示如何在运行时编译、创建实例并应用结果。省略了错误处理的简洁版本。
```cpp
// MyCharacter.h
#pragma once
#include "GameFramework/Character.h"
#include "MyCharacter.generated.h"

class UCustomizableObject;
class UCustomizableObjectInstance;
class USkeletalMeshComponent;

UCLASS()
class AMyCharacter : public ACharacter
{
    GENERATED_BODY()
public:
    AMyCharacter();

    // 引用在编辑器中创建的可定制对象资产
    UPROPERTY(EditAnywhere, Category = "Customization")
    TSoftObjectPtr<UCustomizableObject> CustomizableObjectAsset;

    // 要应用定制外观的网格组件
    UPROPERTY(VisibleAnywhere)
    TObjectPtr<USkeletalMeshComponent> CustomizableMeshComponent;

    UFUNCTION(BlueprintCallable)
    void ApplyCustomization(int32 SkinColorIndex);

private:
    UPROPERTY()
    TObjectPtr<UCustomizableObjectInstance> CurrentInstance;
};

// MyCharacter.cpp
#include "MyCharacter.h"
#include "MuCO/CustomizableObject.h"
#include "MuCO/CustomizableObjectInstance.h"
#include "Components/SkeletalMeshComponent.h"

AMyCharacter::AMyCharacter()
{
    CustomizableMeshComponent = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("CustomizableMesh"));
    CustomizableMeshComponent->SetupAttachment(GetMesh()); // 或根据你的架构设置
}

void AMyCharacter::ApplyCustomization(int32 SkinColorIndex)
{
    // 1. 异步加载资产
    CustomizableObjectAsset.LoadSynchronous();
    UCustomizableObject* CO = CustomizableObjectAsset.Get();
    if (!CO) return;

    // 2. 创建实例 (如果还没有)
    if (!CurrentInstance)
    {
        CurrentInstance = CO->CreateInstance();
    }

    // 3. 设置参数
    CurrentInstance->SetIntParameter(TEXT("SkinColor"), SkinColorIndex);

    // 4. 更新实例 (异步)
    CurrentInstance->UpdateSkeletalMeshAsync(true, true);
    // 5. 绑定更新完成委托 (在构造函数或BeginPlay中绑定更佳)
    FSimpleMulticastDelegate::FDelegate UpdateDelegate = FSimpleMulticastDelegate::FDelegate::CreateLambda([this]()
    {
        if (USkeletalMesh* Mesh = CurrentInstance->GetSkeletalMesh())
        {
            CustomizableMeshComponent->SetSkeletalMesh(Mesh);
        }
    });
    CurrentInstance->UpdatedDelegate.Add(UpdateDelegate);
}
```

## 模块依赖
要使用 Mutable 插件的功能，你的模块需要依赖以下模块：
| 模块 | 用途 |
|---|---|
| `CustomizableObject` | 包含核心运行时类 (`UCustomizableObject`, `UCustomizableObjectInstance`)，是使用 Mutable 功能的必备依赖。 |
| `MutableTools` | 提供资产编译和处理工具。如果你需要在编辑器工具或命令行中编译 `.uasset` 形式的可定制对象，需要依赖此模块。 |

## 维护状态

### 近期更新
| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `70229bdc` | [Mutable] Fix duplicated Skeletal Mesh geometry if there is multiple SKM with the same name. | 修复当场景中存在多个同名骨骼网格体时，可定制对象生成的几何体重复的问题。 |
| 2026-05-26 | `2b0ca8bd` | [mutable] Fixed "Clip mesh with UV Mask" op not loading the appropriate mask mip. | 修复了“使用UV遮罩裁剪网格”操作未能加载正确遮罩Mip级别的问题。 |
| 2026-05-26 | `06ea27d3` | [Mutable] Fix texture parameters using the wrong method to compute the LODBias. | 修复了纹理参数使用错误方法计算LOD偏差的问题。 |
| 2026-05-26 | `e9c39661` | [Mutable] Allow more clothing asset types by using the ClothingAssetBase interface. | 通过使用ClothingAssetBase接口，现在支持更多种类的布料资产类型。 |
| 2026-05-25 | `c8ce9ff7` | [Mutable] Fix possible data race when comparing PassthroughObjects. | 修复了比较直通对象（PassthroughObjects）时可能出现的数据竞争问题。 |

### 维护评价
**活跃维护**。尽管插件整体创建于2024年9月，但自2026年5月底以来有非常密集的提交记录，内容集中于**Bug修复和功能改进**（如支持更多布料资产、修复关键的几何体和纹理问题）。这表明该插件正处于积极的开发和完善阶段，团队在积极响应问题和优化功能。作为从实验性状态移出的“Beta”版本，它目前用于生产环境的风险在降低，但仍需关注其Beta标签。**推荐在需要大规模资产定制化的项目中使用，但需留意其Beta版本的稳定性说明和持续更新。**

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/Customizable-Objects-in-Unreal-Engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable/Source/MutableValidation) (Validation模块内含测试命令行工具)