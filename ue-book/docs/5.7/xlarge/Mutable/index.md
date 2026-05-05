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

Mutable 是一个用于创建**可定制化对象**的完整工具链和运行时框架。它解决的核心问题是：如何在运行时高效地组合、修改和渲染由多个部件（如服装、发型、纹身、装备）构成的复杂角色或物体，同时保持较低的内存占用和较高的渲染性能。

它不仅仅是一个简单的网格体合并工具，而是一个基于节点图的**程序化资产生成系统**。开发者可以在编辑器中通过可视化节点图定义对象的所有可变部分及其组合逻辑（称为“自定义对象”），然后在运行时，玩家可以通过修改参数（如布尔开关、整数选择、浮点值）来动态生成最终的网格体、材质和纹理。这使得实现深度的角色定制、装备外观变化、程序化生成内容等成为可能。

## 使用场景

- **角色定制系统**：允许玩家在游戏内实时组合不同的面部特征、发型、服装、配饰来创建独一无二的角色外观。
- **装备外观变化**：武器、盔甲等装备可以根据附魔、升级或皮肤改变其视觉外观，而无需为每种变体创建独立的资产。
- **程序化生成内容**：根据规则或算法动态生成具有不同外观的物体，如不同样式的家具、车辆或环境道具。
- **优化资产管理**：将大量视觉变体的管理从美术资产转移到逻辑节点图，减少磁盘和内存中的资产副本数量。

## 蓝图用法

Mutable 的蓝图 API 主要集中在 `UCustomizableObject` 和 `UCustomizableObjectInstance` 类上。核心工作流是：加载一个自定义对象资源，创建其实例，修改实例参数，然后触发更新以生成最终的网格体。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Instance` | 从一个 `UCustomizableObject` 资源创建一个新的运行时实例。 | `UCustomizableObject` |
| `Set Bool Parameter Value` | 设置实例的布尔参数（如是否显示某个部件）。 | `UCustomizableObjectInstance` |
| `Set Int Parameter Value` | 设置实例的整数参数（如选择第几号发型）。 | `UCustomizableObjectInstance` |
| `Set Float Parameter Value` | 设置实例的浮点参数（如调整颜色饱和度）。 | `UCustomizableObjectInstance` |
| `Update Skeletal Mesh` | 根据当前参数值，异步生成或更新实例的最终 `USkeletalMesh`。 | `UCustomizableObjectInstance` |
| `Get Skeletal Mesh` | 获取实例当前已生成的 `USkeletalMesh`，用于附加到角色上。 | `UCustomizableObjectInstance` |

### 使用示例（蓝图描述）

1.  **初始化**：在角色蓝图中，使用 `Load Asset` 加载你的 `UCustomizableObject` 资源（例如 `CO_Hero`），然后调用 `Create Instance` 节点创建一个 `UCustomizableObjectInstance` 并保存为变量。
2.  **修改参数**：当玩家在UI中选择不同选项时，调用相应的 `Set Parameter Value` 节点。例如，玩家选择“发型B”，则调用 `Set Int Parameter Value`，将参数名（如 `HairStyle`）设置为 `1`。
3.  **应用更新**：参数修改后，调用 `Update Skeletal Mesh` 节点。此操作是异步的，完成后会触发 `On Customizable Object Instance Updated` 委托。
4.  **应用结果**：在更新完成的回调中，调用 `Get Skeletal Mesh` 获取新的网格体，并通过 `Set Skeletal Mesh` 节点将其应用到角色的 `USkeletalMeshComponent` 上。

## C++ 用法

C++ 用法与蓝图逻辑对应，但提供了更底层的控制和性能优化可能。核心类同样是 `UCustomizableObject` 和 `UCustomizableObjectInstance`。

### 头文件引入

```cpp
#include "CustomizableObject.h"
#include "CustomizableObjectInstance.h"
```

### 基本用法

以下是一个简化的C++使用流程，展示了如何创建实例、修改参数并更新网格体。

```cpp
// 假设你已经有一个 UCustomizableObject* 指针 CustomizableObjectAsset
// 通常通过 UCustomizableObjectSystem::GetInstance()->LoadCustomizableObject(AssetPath) 加载

// 1. 创建实例
UCustomizableObjectInstance* Instance = CustomizableObjectAsset->CreateInstance();

// 2. 设置参数 (示例：设置一个名为 “ShirtColor” 的整数参数为 2)
FString ParameterName = TEXT("ShirtColor");
int32 ParameterValue = 2;
Instance->SetIntParameterSelectedOption(ParameterName, ParameterValue);

// 3. 请求更新 (异步)
// 需要绑定一个委托来接收更新完成的通知
FOnCustomizableObjectInstanceUpdated UpdateDelegate;
UpdateDelegate.BindUObject(this, &AMyCharacter::OnMutableInstanceUpdated);
Instance->UpdatedDelegate = UpdateDelegate;
Instance->UpdateSkeletalMeshAsync(true, true);

// 4. 回调函数
void AMyCharacter::OnMutableInstanceUpdated(UCustomizableObjectInstance* UpdatedInstance)
{
    if (UpdatedInstance && UpdatedInstance->SkeletalMesh)
    {
        // 将新生成的网格体应用到角色的Mesh组件上
        GetMesh()->SetSkeletalMesh(UpdatedInstance->SkeletalMesh);
    }
}
```

### 进阶用法

更复杂的用法包括：
- **批量参数修改**：在一次更新前设置多个参数，以减少重新生成的次数。
- **使用 `FCustomizableObjectInstanceBakeOutput`**：将实例的当前状态“烘焙”成独立的资产，用于保存/加载或进一步优化。
- **与动画系统集成**：确保生成的网格体与角色的动画蓝图兼容。
- **内存管理**：理解 `UCustomizableObjectInstance` 的生命周期，及时释放不再需要的实例以避免内存泄漏。

## Demo 示例

一个最小化的可运行示例框架：

**MyCharacter.h**
```cpp
#pragma once
#include "GameFramework/Character.h"
#include "MyCharacter.generated.h"

class UCustomizableObject;
class UCustomizableObjectInstance;

UCLASS()
class AMyCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    AMyCharacter();

    UPROPERTY(EditAnywhere, Category = "Mutable")
    UCustomizableObject* CustomizableObjectAsset;

    UPROPERTY()
    UCustomizableObjectInstance* MutableInstance;

    UFUNCTION(BlueprintCallable, Category = "Mutable")
    void ChangeHairStyle(int32 NewStyleIndex);

private:
    void OnMutableUpdated(UCustomizableObjectInstance* Instance);
};
```

**MyCharacter.cpp**
```cpp
#include "MyCharacter.h"
#include "CustomizableObject.h"
#include "CustomizableObjectInstance.h"
#include "CustomizableObjectSystem.h"

AMyCharacter::AMyCharacter()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyCharacter::BeginPlay()
{
    Super::BeginPlay();

    if (CustomizableObjectAsset)
    {
        MutableInstance = CustomizableObjectAsset->CreateInstance();
        if (MutableInstance)
        {
            FOnCustomizableObjectInstanceUpdated Delegate;
            Delegate.BindUObject(this, &AMyCharacter::OnMutableUpdated);
            MutableInstance->UpdatedDelegate = Delegate;
            // 初始更新
            MutableInstance->UpdateSkeletalMeshAsync(true, true);
        }
    }
}

void AMyCharacter::ChangeHairStyle(int32 NewStyleIndex)
{
    if (MutableInstance)
    {
        MutableInstance->SetIntParameterSelectedOption(TEXT("HairStyle"), NewStyleIndex);
        MutableInstance->UpdateSkeletalMeshAsync(true, true);
    }
}

void AMyCharacter::OnMutableUpdated(UCustomizableObjectInstance* Instance)
{
    if (Instance && Instance->SkeletalMesh)
    {
        GetMesh()->SetSkeletalMesh(Instance->SkeletalMesh);
    }
}
```

## 模块依赖

要使用 Mutable 插件，你的项目模块通常需要依赖以下模块（根据你的使用深度选择）：

| 模块 | 用途 |
|---|---|
| `CustomizableObject` | 核心运行时模块，包含 `UCustomizableObject` 和 `UCustomizableObjectInstance` 等核心类。**必须依赖**。 |
| `MutableRuntime` | Mutable 的底层运行时库，被 `CustomizableObject` 模块依赖。通常不需要直接依赖。 |
| `MutableTools` | 编辑器工具模块，用于处理和编译自定义对象资源。**仅在编辑器工具开发或需要烘焙功能时依赖**。 |
| `CustomizableObjectEditor` | 编辑器UI和资产编辑器模块。**仅在开发编辑器扩展时依赖**。 |
| `MutableValidation` | 验证工具模块，用于检查自定义对象资源的有效性。**仅在开发相关工具时依赖**。 |

**典型项目依赖**：对于大多数游戏项目，只需在 `.Build.cs` 文件中添加 `CustomizableObject` 模块依赖即可。
```csharp
PublicDependencyModuleNames.AddRange(new string[] { "Core", "CoreUObject", "Engine", "InputCore", "CustomizableObject" });
```

## 维护状态

### 近期更新
（*注：以下为基于插件创建时间的推测，具体 commit 信息需查询 Git 仓库*）
- 2022-09-26 插件首次引入 Unreal Engine 5.1 源码树。
- （后续更新记录需通过 `git log` 获取，例如：）
- 2024-XX-XX [commit hash] 为 UE 5.4/5.5 进行兼容性更新和性能优化。
- 2023-XX-XX [commit hash] 增加了新的节点类型或改进了编译流程。

### 维护评价
Mutable 是一个由 Epic Games 官方维护的**核心功能插件**，用于支持其 MetaHuman 等先进技术栈。自 2022 年引入以来，它随着引擎版本持续更新，是 UE5 中实现高级角色定制的**推荐方案**。

- **活跃度**：高。作为 Epic 的重点技术，通常会随引擎大版本进行更新和优化。
- **稳定性**：生产可用。已被用于多个 AAA 项目和 Epic 自家的技术演示中。
- **学习曲线**：较陡峭。节点图系统功能强大但概念复杂，需要投入时间学习。
- **推荐度**：**强烈推荐**用于需要深度运行时角色/物体定制的项目。对于简单的外观切换，可能过于复杂。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Mutable)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/mutable-plugin-in-unreal-engine/) (UE5 官方文档链接)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Mutable/Tests) (如果存在)