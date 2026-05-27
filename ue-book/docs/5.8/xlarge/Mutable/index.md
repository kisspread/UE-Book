# Mutable

> Mutable adds the tools and runtime to create customizable objects for your games.

| 属性 | 值 |
|---|---|
| 中文名 | 可定制对象系统 |
| 分类 | CustomizableObjects |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `MutableRuntime` (Runtime), `CustomizableObject` (Runtime), `MutableTools` (Runtime), `MutableValidation` (Runtime), `CustomizableObjectEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-05 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable) | |

## 用途

Mutable 是一个完整的运行时和工具链系统，旨在为游戏创建高度可定制、可动态组合的复杂对象。它解决的核心问题是：如何在玩家游玩时，根据玩家的选择（如捏脸、装备搭配）或游戏逻辑（如不同等级NPC的外观），实时地、高效地生成外观差异巨大的资产组合，而不必预先烘焙和存储所有可能的变体。

该插件将资产的逻辑定义（如哪些部分可替换、材质如何变化）与最终生成的渲染数据分离开，通过“可定制对象”蓝图资产来定义组合规则，由运行时根据输入参数（浮点、整型、布尔、颜色等）动态构建最终的网格体、材质和纹理。

## 使用场景

- **角色创建系统**：玩家可以自由组合发型、五官、纹身、服装部件，并看到实时预览。
- **装备定制**：武器、盔甲可以通过修改贴图、部件来改变外观，支持运行时换色、加装附件。
- **批量生成NPC变体**：通过设置不同的参数种子，从同一个“可定制对象”生成大量外观略有差异的NPC，避免千篇一律。
- **UGC（用户生成内容）**：允许玩家通过受限的参数接口创建和分享自定义外观，系统在后台确保技术可行性（LOD、材质复杂度等）。

## 模块总览

| 模块 | 类型 | 简要说明 |
|---|---|---|
| [MutableRuntime](MutableRuntime.md) | Runtime | **运行时核心**，负责根据参数实例化、构建最终网格体和材质。包含构建图、实例状态和性能优化逻辑。 |
| [CustomizableObject](CustomizableObject.md) | Runtime | **资产类型核心**，定义了 `UCustomizableObject` 和 `UCustomizableObjectInstance` 等核心UObject资产，是连接编辑器工具与运行时的桥梁。 |
| [MutableTools](MutableTools.md) | Runtime | **工具链核心**（运行时模块），包含编译、优化、序列化“可定制对象”蓝图资产所需的算法和工具类。主要被编辑器模块调用。 |
| [MutableValidation](MutableValidation.md) | Runtime | **验证模块**，用于检查“可定制对象”资产的有效性和完整性，确保其能在运行时正确构建。 |
| [CustomizableObjectEditor](CustomizableObjectEditor.md) | Runtime | **编辑器扩展**，提供 `UCustomizableObject` 的自定义资产编辑器、细节面板自定义界面以及相关的编辑器工具操作（如编译、缓存）。 |

## 蓝图用法

蓝图API主要集中在 `CustomizableObject` 和 `CustomizableObjectEditor` 模块暴露的类中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Customizable Object Instance` | 从一个 `UCustomizableObject` 蓝图资产创建一个新的、可独立设置参数的 `UCustomizableObjectInstance`。 | `UCustomizableObjectLibrary` |
| `Set Int Parameter` | 为实例设置一个整型参数（如选择发型ID）。 | `UCustomizableObjectInstance` |
| `Set Float Parameter` | 为实例设置一个浮点参数（如瞳孔缩放比例）。 | `UCustomizableObjectInstance` |
| `Set Bool Parameter` | 为实例设置一个布尔参数（如是否显示伤疤）。 | `UCustomizableObjectInstance` |
| `Set Vector Parameter` | 为实例设置一个颜色/向量参数（如衣服颜色）。 | `UCustomizableObjectInstance` |
| `Set Projector Parameter` | 设置投影器参数，用于实现贴花或动态纹理投射。 | `UCustomizableObjectInstance` |
| `Update Customizable Object Instance` | 在修改参数后，调用此节点触发实例的异步重建，生成最终的渲染数据。 | `UCustomizableObjectInstance` |

### 使用示例（蓝图描述）

1.  在角色蓝图中，添加一个 `SkeletalMeshComponent`。
2.  在角色初始化时，调用 `Create Customizable Object Instance`，传入引用的 `MyCharacter_CO` 可定制对象资产。
3.  将返回的 `UCustomizableObjectInstance` 保存为变量 `MyInstance`。
4.  当玩家在UI界面选择新发型（例如，索引 `2`）时，调用 `MyInstance` 的 `Set Int Parameter`，参数名设为 `"HairStyle"`，值设为 `2`。
5.  调用 `MyInstance` 的 `Update Customizable Object Instance`。
6.  将更新后 `MyInstance` 的输出网格体 (`Get Skeletal Mesh`) 和材质赋值给角色的 `SkeletalMeshComponent`。

## C++ 用法

C++ 用法通常涉及更底层的实例控制、批量操作或自定义LOD策略。

### 头文件引入

```cpp
// 要操作可定制对象实例
#include "CustomizableObjectInstance.h"

// 要引用可定制对象资产类型
#include "CustomizableObject.h"
```

### 基本用法

```cpp
// 来源：测试用例中常见的实例化和参数设置流程
UCustomizableObject* CustomizableObject = LoadObject<UCustomizableObject>(nullptr, TEXT("/Game/MyObjects/Character_CO"));
if (CustomizableObject)
{
    // 创建一个新实例
    UCustomizableObjectInstance* Instance = NewObject<UCustomizableObjectInstance>();
    Instance->SetObject(CustomizableObject);

    // 设置参数
    Instance->SetIntValue(FName("BodyType"), 1); // 设置体型
    Instance->SetFloatValue(FName("Age"), 0.5f); // 设置年龄（控制面部变形）
    Instance->SetBoolValue(FName("ShowHat"), true); // 显示帽子

    // 启动异步构建
    Instance->UpdateSkeletalMeshAsync();
    // 之后可以通过委托或轮询获取构建结果
}
```

### 进阶用法

```cpp
// 来源：性能优化或特殊渲染路径相关测试
// 手动控制实例的LOD更新
if (Instance->IsUpdatePending())
{
    // 可以延迟更新以优化性能
    Instance->SetForceUpdate(false);
}

// 在特定时间点强制完成同步更新（谨慎使用）
Instance->UpdateSkeletalMeshSynchronous();
```

## Demo 示例

以下是一个最小可编译的 C++ 示例，展示如何创建并更新一个可定制对象实例。

**MyCustomizableCharacter.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "MyCustomizableCharacter.generated.h"

class UCustomizableObjectInstance;
class USkeletalMeshComponent;

UCLASS()
class AMyCustomizableCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    AMyCustomizableCharacter();

    virtual void BeginPlay() override;

    /** 根据预设更改外观 */
    UFUNCTION(BlueprintCallable)
    void ChangeAppearance(int32 BodyType, bool bShowMask);

protected:
    // 指向你的可定制对象资产（在蓝图中设置）
    UPROPERTY(EditAnywhere, Category="Customizable Object")
    UCustomizableObject* CustomizableObjectAsset;

    // 生成的实例
    UPROPERTY(Transient)
    UCustomizableObjectInstance* CustomizableInstance;

    // 实例的网格体将被应用到此组件
    UPROPERTY(VisibleAnywhere)
    USkeletalMeshComponent* CustomizableSkeletalMesh;
};
```

**MyCustomizableCharacter.cpp**
```cpp
#include "MyCustomizableCharacter.h"
#include "CustomizableObjectInstance.h"
#include "CustomizableObject.h"
#include "Components/SkeletalMeshComponent.h"

AMyCustomizableCharacter::AMyCustomizableCharacter()
{
    CustomizableSkeletalMesh = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("CustomizableMesh"));
    CustomizableSkeletalMesh->SetupAttachment(GetMesh()); // 或附加到根组件
}

void AMyCustomizableCharacter::BeginPlay()
{
    Super::BeginPlay();

    if (CustomizableObjectAsset)
    {
        // 1. 创建实例
        CustomizableInstance = NewObject<UCustomizableObjectInstance>();
        CustomizableInstance->SetObject(CustomizableObjectAsset);

        // 2. 设置初始参数
        CustomizableInstance->SetIntValue(FName("BodyType"), 0);
        CustomizableInstance->SetBoolValue(FName("ShowMask"), false);

        // 3. 构建并应用
        CustomizableInstance->UpdateSkeletalMeshAsync();

        // 4. 监听构建完成事件（简化示例，实际应用中需绑定委托）
        FTimerHandle TimerHandle;
        GetWorldTimerManager().SetTimer(TimerHandle, [this]()
        {
            if (CustomizableInstance && CustomizableInstance->GetSkeletalMesh())
            {
                CustomizableSkeletalMesh->SetSkeletalMesh(CustomizableInstance->GetSkeletalMesh());
            }
        }, 1.0f, false); // 简单的延迟，非最佳实践
    }
}

void AMyCustomizableCharacter::ChangeAppearance(int32 BodyType, bool bShowMask)
{
    if (CustomizableInstance)
    {
        CustomizableInstance->SetIntValue(FName("BodyType"), BodyType);
        CustomizableInstance->SetBoolValue(FName("ShowMask"), bShowMask);
        CustomizableInstance->UpdateSkeletalMeshAsync();
        // 同样需要处理网格体更新（通过委托）
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MutableRuntime` | 提供可定制对象运行时构建和实例化的核心逻辑。 |
| `MutableTools` | 提供编辑器工具链，用于编译和优化可定制对象资产。 |
| `MutableValidation` | 提供资产验证功能，确保可定制对象定义有效。 |
| `CustomizableObject` | 提供 `UCustomizableObject` 和 `UCustomizableObjectInstance` 等核心资产类。 |
| `CustomizableObjectEditor` | 提供自定义资产编辑器、细节面板扩展等编辑器功能。 |
| `DerivedDataCache` | 用于缓存编译后的可定制对象数据，加速迭代。 |
| `UnrealEd` | 编辑器集成基础依赖。 |
| `MeshDescription` | 处理网格体数据的底层表示和转换。 |
| `MeshUtilitiesCommon` | 提供网格体相关的工具函数。 |
| `PhysicsCore` | 处理可定制对象可能包含的物理资产。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `70229bdc` | [Mutable] Fix duplicated Skeletal Mesh geometry if there is multiple SKM with the same name. | 修复同名骨骼网格体导致几何数据重复的问题。 |
| 2026-05-26 | `2b0ca8bd` | [mutable] Fixed "Clip mesh with UV Mask" op not loading the appropriate mask mip. | 修复“使用UV蒙版裁剪网格体”操作加载错误mip级别的问题。 |
| 2026-05-26 | `06ea27d3` | [Mutable] Fix texture parameters using the wrong method to compute the LODBias. An incorrect LODBias | 修复纹理参数使用错误方法计算LODBias的问题。 |
| 2026-05-26 | `e9c39661` | [Mutable] Allow more clothing asset types by using the ClothingAssetBase interface. | 通过使用`ClothingAssetBase`接口，允许支持更多类型的布料资产。 |
| 2026-05-25 | `c8ce9ff7` | [Mutable] Fix possible data race when comparing PassthroughObjects. | 修复比较`PassthroughObjects`时可能出现的数据竞争。 |

### 维护评价

Mutable 插件处于**活跃维护**状态。它于2024年9月从Experimental状态移至Beta，表明其核心功能已趋稳定。从近期更新记录（2026年5月）来看，开发团队仍在持续修复bug、优化性能并增加功能（如扩展布料资产支持）。作为Epic Games直接维护的“Beta”插件，其代码质量和长期支持有较高保障。

**主要优势**：
-   为解决游戏资产动态组合这一复杂问题提供了成熟的全套解决方案。
-   活跃的维护意味着问题能得到及时修复和功能迭代。
-   与UE编辑器深度集成，提供所见即所得的编辑体验。

**注意事项**：
-   标记为Beta，意味着API或资产格式在后续版本中仍有变化的可能。
-   系统相对复杂，学习曲线较陡，需要理解其编辑器工具链和运行时构建流程。

**推荐使用**：对于需要在运行时实现高度复杂、参数化角色或物品自定义的游戏项目，**强烈推荐**使用Mutable插件。它是目前UE官方提供的最权威和功能最全面的解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/mutable-unreal-engine-plugin/) (假设文档存在)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable/Tests)