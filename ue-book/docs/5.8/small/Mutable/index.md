# Mutable

> Mutable adds the tools and runtime to create customizable objects for your games.

| 属性 | 值 |
|---|---|
| 中文名 | 可变对象系统 |
| 分类 | CustomizableObjects |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（测试资源） |
| 模块 | `CustomizableObject` (Runtime), `CustomizableObjectEditor` (Runtime), `MutableRuntime` (Runtime), `MutableTools` (Runtime), `MutableValidation` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-05 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable) | |

## 用途

Mutable 是一个复杂的运行时对象合成与自定义系统。它的核心目标是解决游戏开发中，特别是需要大量角色、装备、外观变化的项目（如 MMO、ARPG）中，**资源冗余和组合爆炸**的问题。通过在一个“基础对象”（`UCustomizableObject`）中定义可变的部件、材质、网格和参数，引擎可以在运行时根据玩家选择或游戏逻辑，动态地“编译”出成千上万种视觉上独一无二的对象实例，而无需为每一种组合都烘焙独立的资产。这极大地节省了内存和存储空间，并实现了高度的动态化。

## 使用场景

- **MMO 或大型 RPG 的角色定制**：玩家可以自由组合发型、五官、服装、盔甲、武器等，系统在运行时实时生成独特的角色外观。
- **装备部件系统**：一件武器由剑柄、剑刃、护手等可变部件组成，每个部件都有多种材质和样式选项。
- **动态材质与外观**：根据游戏内状态（如角色受伤、装备附魔）改变物体的纹理或网格部件。
- **需要大量类似但略有不同物体的场景**：例如城市中的不同家具变体、不同涂装的载具等。

## 蓝图用法

核心功能通过 `CustomizableObject` 和 `CustomizableObjectInstance` 类暴露给蓝图。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Customizable Object Instance` | 根据一个 `UCustomizableObject` 资产创建一个运行时实例 (`UCustomizableObjectInstance`)。 | `UCustomizableObject` |
| `Set Int Parameter` | 为实例设置一个整型参数（如选择哪个眉毛样式）。 | `UCustomizableObjectInstance` |
| `Set Float Parameter` | 为实例设置一个浮点型参数（如调整身高缩放）。 | `UCustomizableObjectInstance` |
| `Set Bool Parameter` | 为实例设置一个布尔型参数（如是否显示头盔）。 | `UCustomizableObjectInstance` |
| `Set Color Parameter` | 为实例设置一个颜色参数（如改变衣服颜色）。 | `UCustomizableObjectInstance` |
| `Set Projector Parameter` | 设置投影器参数，用于复杂的纹理投射（如纹身）。 | `UCustomizableObjectInstance` |
| `Update Customizable Object Instance` | 请求系统重新编译并更新实例的所有可见组件。在修改参数后必须调用。 | `UCustomizableObjectInstance` |
| `Get Skeletal Mesh` / `Get Physics Asset` | 从编译完成的实例中获取最终的骨骼网格体和物理资产，用于生成角色。 | `UCustomizableObjectInstance` |

### 使用示例（蓝图描述）
1.  在一个角色蓝图中，添加一个 `Customizable Object Instance` 组件或变量。
2.  游戏开始时，使用 `Create Customizable Object Instance` 节点，传入预先设计好的 `UCustomizableObject` 资产，创建实例。
3.  根据玩家在 UI 上的选择，调用 `Set Int Parameter`（例如 `ParamName: “HairStyle”, Value: 2`）设置相应的外观参数。
4.  所有参数设置完成后，调用 `Update Customizable Object Instance`。
5.  系统在后台编译，完成后，使用 `Get Skeletal Mesh` 获取新的网格体，并设置给角色的 Skeletal Mesh Component。

## C++ 用法

### 头文件引入
```cpp
#include "CustomizableObject.h"
#include "CustomizableObjectInstance.h"
```

### 基本用法 (创建实例并更新)
```cpp
// 来源：引擎内部使用模式，参考 CustomizableObject 模块测试
// 1. 获取一个已有的 CustomizableObject 资产
UCustomizableObject* MyObject = LoadObject<UCustomizableObject>(nullptr, TEXT("/Game/MyAssets/CO_HumanMale"));

if (MyObject)
{
    // 2. 创建实例
    UCustomizableObjectInstance* MyInstance = MyObject->CreateInstance();

    // 3. 设置参数
    MyInstance->SetIntParameterSelectedOption(FName("Torso"), FName("Armor_Heavy"));
    MyInstance->SetFloatParameterValue(FName("BodyScale"), 1.1f);

    // 4. 注册到系统并请求更新
    // 通常由组件（如 UCustomizableSkeletalComponent）自动处理
    // 手动更新可以使用 MyInstance->UpdateSkeletalMeshAsync();
}
```

### 进阶用法 (版本控制和资源包)
```cpp
// 来源：CustomizableObjectInstance 的版本与序列化功能
// Mutable 支持复杂的版本和差异更新，用于网络同步
FString InstanceData;
MyInstance->SerializeInstance(InstanceData); // 序列化当前实例状态

// 在另一端（如客户端）反序列化以同步外观
UCustomizableObjectInstance* NewInstance = MyObject->CreateInstance();
NewInstance->DeserializeInstance(InstanceData);
NewInstance->UpdateSkeletalMeshAsync();

// 使用“资源包”（Resource Pack）可以预编译和缓存特定的组合，提高加载速度
// 这是一个高级特性，通常在编辑器工具或自动化构建流程中使用。
```

## Demo 示例

**MyCharacter.h**
```cpp
#pragma once
#include "GameFramework/Character.h"
#include "MyCharacter.generated.h"

class UCustomizableObjectInstance;
class UCustomizableSkeletalComponent;

UCLASS()
class AMyCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    AMyCharacter();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Customization")
    UCustomizableSkeletalComponent* CustomizableSkeletalComponent;

    UPROPERTY(BlueprintReadWrite, Category = "Customization")
    UCustomizableObjectInstance* CustomizableInstance;

    UFUNCTION(BlueprintCallable, Category = "Customization")
    void UpdateAppearanceFromParameters();
};
```

**MyCharacter.cpp**
```cpp
#include "MyCharacter.h"
#include "Components/CustomizableSkeletalComponent.h"
#include "CustomizableObjectInstance.h"
#include "CustomizableObject.h"

AMyCharacter::AMyCharacter()
{
    // 创建自定义骨骼组件，用于替代默认的 Mesh Component
    CustomizableSkeletalComponent = CreateDefaultSubobject<UCustomizableSkeletalComponent>(TEXT("CustomizableSkeletal"));
    CustomizableSkeletalComponent->SetupAttachment(GetRootComponent());
}

void AMyCharacter::UpdateAppearanceFromParameters()
{
    if (CustomizableInstance && CustomizableSkeletalComponent)
    {
        // 将实例绑定到组件
        CustomizableSkeletalComponent->SetCustomizableObjectInstance(CustomizableInstance);
        // 触发更新，组件会自动处理网格体的生成和设置
        CustomizableSkeletalComponent->UpdateSkeletalMeshAsync();
    }
}
```

## 模块依赖

从 Build.cs 分析，使用者需要依赖以下核心模块：

| 模块 | 用途 |
|---|---|
| `CustomizableObject` | **必需**。提供核心的 `UCustomizableObject` 和 `UCustomizableObjectInstance` 类及运行时支持。 |
| `MutableRuntime` | **必需**。提供底层的合成引擎和数据格式。 |
| `MutableTools` | 编辑器和烘焙流程中用于编译和优化 `UCustomizableObject` 资产。 |
| `DerivedDataCache` | 用于缓存编译后的合成数据，提高加载性能。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `70229bdc` | [Mutable] Fix duplicated Skeletal Mesh geometry if there is multiple SKM with the same name. | 修复多个同名骨骼网格体导致的几何体重复问题。 |
| 2026-05-26 | `2b0ca8bd` | [mutable] Fixed "Clip mesh with UV Mask" op not loading the appropriate mask mip. | 修复 UV 遮罩裁剪操作加载错误 mip 层级的问题。 |
| 2026-05-26 | `06ea27d3` | [Mutable] Fix texture parameters using the wrong method to compute the LODBias. | 修复纹理参数计算 LODBias 方法错误导致的显示问题。 |
| 2026-05-26 | `e9c39661` | [Mutable] Allow more clothing asset types by using the ClothingAssetBase interface. | 通过使用基础接口，支持更多类型的布料资产。 |
| 2026-05-25 | `c8ce9ff7` | [Mutable] Fix possible data race when comparing PassthroughObjects. | 修复比较 PassthroughObject 时可能出现的数据竞争。 |

### 维护评价
Mutable 插件目前处于**积极维护**状态。它于 2024 年 9 月从实验状态转入 Beta，并持续获得重要的 bug 修复和功能增强（如近期的网格体、纹理、布料和多线程问题修复）。虽然标记为 `⚠️ 实验性 (Beta)`，但其更新频率高且解决的是核心功能问题，表明 Epic 将其视为一个向正式版演进的关键系统。对于需要高级动态对象合成的项目，这是一个强大且值得信赖的选择，但需注意其 Beta 状态可能意味着 API 或数据格式在未来版本中仍有调整的可能。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/mutable-plugin-in-unreal-engine/) （示例链接，Epic 官方文档应存在）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable/Tests)