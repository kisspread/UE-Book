# Mutable

> Mutable adds the tools and runtime to create customizable objects for your games.

| 属性 | 值 |
|---|---|
| 中文名 | 可变对象工具 |
| 分类 | CustomizableObjects |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（运行时库、编辑器工具、验证模块） |
| 模块 | `MutableRuntime` (Runtime), `CustomizableObject` (Runtime), `CustomizableObjectEditor` (Runtime), `MutableTools` (Runtime), `MutableValidation` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-09-05 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable) | |

## 用途

Mutable 是一个用于创建可自定义、可变形游戏资产的工具集。它提供了一个运行时引擎和一套编辑器工具，允许开发者创建可在运行时根据参数（如玩家选择、等级、装备等）动态组合和修改的复杂对象。这解决了需要大量变体角色、装备或物体，而又不想手动创建每一个可能组合时的性能和工作流程问题。它本质上是一个基于节点的可视化编程系统，用于定义资产的变形逻辑和组合方式。

## 使用场景

*   你需要为 RPG 游戏创建数百种可能的武器/盔甲外观，且不想手动建模每一种。
*   你需要一个支持发型、肤色、服装、配饰等高度自定义的角色创建系统。
*   你需要创建外观随游戏进度（如损坏、升级）而变化的物体。
*   你需要在运行时动态生成大量外观各异但基础结构相同的 NPC。

## 蓝图用法

Mutable 主要通过自定义资产（CustomizableObject）和运行时函数进行操作，其大部分逻辑在编辑器中以节点图方式构建。运行时通过 `UCustomizableObject` 和 `UCustomizableObjectInstance` 类进行交互。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `UpdateSkeletalMeshAsync` | 异步更新骨骼网格体实例 | `UCustomizableObjectInstance` |
| `SetVectorParameter` | 设置可变对象实例的向量参数 | `UCustomizableObjectInstance` |
| `SetScalarParameter` | 设置可变对象实例的标量参数 | `UCustomizableObjectInstance` |
| `SetBoolParameter` | 设置可变对象实例的布尔参数 | `UCustomizableObjectInstance` |
| `SetTextureParameter` | 设置可变对象实例的纹理参数 | `UCustomizableObjectInstance` |

### 使用示例（蓝图描述）

1.  在 Content Browser 中右键 -> Miscellaneous -> Customizable Object，创建一个自定义对象资产。
2.  双击打开该资产，进入节点编辑器界面，构建你的资产变形逻辑。
3.  在蓝图中，使用 `Create Customizable Object Instance` 节点创建一个运行时实例。
4.  使用 `Set*Parameter` 节点（如 `SetBoolParameter`）修改实例参数。
5.  调用 `UpdateSkeletalMeshAsync` 来根据当前参数生成或更新网格体。
6.  将生成的网格体应用到 `Skeletal Mesh Component` 上。

## C++ 用法

### 头文件引入

```cpp
#include "CustomizableObject.h"
#include "CustomizableObjectInstance.h"
```

### 基本用法

创建并更新一个可自定义对象实例。
（来源：UE5 官方示例和文档惯例）

```cpp
// 获取或加载一个 UCustomizableObject
UCustomizableObject* MyObject = LoadObject<UCustomizableObject>(nullptr, TEXT("/Game/Path/To/MyCustomizableObject"));
if (!MyObject) return;

// 创建一个实例
UCustomizableObjectInstance* MyInstance = MyObject->CreateInstance();

// 设置一个布尔参数，例如“戴帽子”
MyInstance->SetBoolParameter(FName("WearHat"), true);

// 设置一个整数参数，例如“服装变体”
MyInstance->SetIntParameter(FName("OutfitVariant"), 2);

// 异步更新网格体
MyInstance->UpdateSkeletalMeshAsync(true, true);
```

### 进阶用法

监听网格体更新完成的委托，并将结果应用到角色组件。
（来源：自定义对象系统常见模式）

```cpp
// 在某个 Actor 的 BeginPlay 中
void AMyCharacter::BeginPlay()
{
    Super::BeginPlay();

    if (MyCustomizableInstance)
    {
        // 绑定更新完成的委托
        FOnCustomizableObjectUpdatedDelegate Delegate;
        Delegate.BindUObject(this, &AMyCharacter::OnCustomizableObjectUpdated);
        MyCustomizableInstance->UpdatedDelegate.Add(Delegate);

        // 触发首次更新
        MyCustomizableInstance->UpdateSkeletalMeshAsync(true, true);
    }
}

// 委托回调
void AMyCharacter::OnCustomizableObjectUpdated()
{
    if (MyCustomizableInstance)
    {
        USkeletalMesh* NewMesh = MyCustomizableInstance->GetSkeletalMesh();
        if (NewMesh && GetMesh())
        {
            GetMesh()->SetSkeletalMesh(NewMesh);
        }
    }
}
```

## Demo 示例

一个最小的自定义对象使用示例。
（此示例假设已在编辑器中创建了 `MyCustomizableObject` 资产，并包含一个名为 `HasHat` 的布尔参数。）

**MyCharacter.h**
```cpp
#pragma once

#include "CoreMinimal.h"
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

protected:
    virtual void BeginPlay() override;

    UPROPERTY()
    UCustomizableObject* CustomizableObject;

    UPROPERTY()
    UCustomizableObjectInstance* CustomizableInstance;

    UFUNCTION()
    void OnObjectUpdated();

public:
    UFUNCTION(BlueprintCallable, Category = "Customization")
    void ToggleHat();
};
```

**MyCharacter.cpp**
```cpp
#include "MyCharacter.h"
#include "CustomizableObject.h"
#include "CustomizableObjectInstance.h"

AMyCharacter::AMyCharacter()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyCharacter::BeginPlay()
{
    Super::BeginPlay();

    // 加载自定义对象资产
    CustomizableObject = LoadObject<UCustomizableObject>(nullptr, TEXT("/Game/MyCustomizableObject"));
    if (CustomizableObject)
    {
        // 创建实例
        CustomizableInstance = CustomizableObject->CreateInstance();

        // 绑定更新委托
        FOnCustomizableObjectUpdatedDelegate Delegate;
        Delegate.BindUObject(this, &AMyCharacter::OnObjectUpdated);
        CustomizableInstance->UpdatedDelegate.Add(Delegate);

        // 首次更新
        CustomizableInstance->UpdateSkeletalMeshAsync(true, true);
    }
}

void AMyCharacter::OnObjectUpdated()
{
    if (CustomizableInstance && GetMesh())
    {
        USkeletalMesh* NewMesh = CustomizableInstance->GetSkeletalMesh();
        if (NewMesh)
        {
            GetMesh()->SetSkeletalMesh(NewMesh);
        }
    }
}

void AMyCharacter::ToggleHat()
{
    if (CustomizableInstance)
    {
        // 读取当前值并取反
        bool bCurrentHasHat = CustomizableInstance->GetBoolParameter(FName("HasHat"));
        CustomizableInstance->SetBoolParameter(FName("HasHat"), !bCurrentHasHat);
        CustomizableInstance->UpdateSkeletalMeshAsync(true, true);
    }
}
```

## 模块依赖

从提供的 `Build.cs` 文件中提取。使用 `Mutable` 插件的主要功能（创建和运行自定义对象）通常需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `CustomizableObject` | 核心运行时模块，提供 `UCustomizableObject` 和 `UCustomizableObjectInstance` 类。 |
| `MutableRuntime` | Mutable 底层运行时引擎，处理资产变形和组合。 |
| `MutableTools` | 编辑器工具模块，提供节点编辑器和编译功能。 |

**注意**：你的项目模块需要在 `Build.cs` 文件中添加对 `CustomizableObject` 模块的依赖，才能使用其 API。
```csharp
PublicDependencyModuleNames.AddRange(new string[] { "Core", "CoreUObject", "Engine", "InputCore", "CustomizableObject" });
```

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `70229bdc` | [Mutable] Fix duplicated Skeletal Mesh geometry if there is multiple SKM with the same name. | 修复当存在多个同名骨骼网格体时导致几何体重复的问题。 |
| 2026-05-26 | `2b0ca8bd` | [mutable] Fixed "Clip mesh with UV Mask" op not loading the appropriate mask mip. | 修复“使用 UV 遮罩裁剪网格”操作未加载合适遮罩 mip 级别的问题。 |
| 2026-05-26 | `06ea27d3` | [Mutable] Fix texture parameters using the wrong method to compute the LODBias. | 修复纹理参数使用错误方法计算 LODBias 的问题。 |
| 2026-05-26 | `e9c39661` | [Mutable] Allow more clothing asset types by using the ClothingAssetBase interface. | 通过使用 ClothingAssetBase 接口允许更多服装资产类型。 |
| 2026-05-25 | `c8ce9ff7` | [Mutable] Fix possible data race when comparing PassthroughObjects. | 修复比较 PassthroughObjects 时可能出现的数据竞争问题。 |

### 维护评价

该插件创建于 2024 年 9 月，相对年轻。从最近的提交历史看，**维护非常活跃**。最近的更新（截至文档生成时）全部是针对各种运行时和编译问题的 Bug 修复，这表明插件正在被积极地测试和完善。虽然它最初是从实验性状态移出的，但目前的更新频率和修复内容表明它已进入稳定期，是一个推荐用于需要高度资产自定义的项目的解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable)
- [官方文档](https://docs.unrealengine.com/en-US/InteractiveExperiences/CustomizableObjects/index.html)（如果有，但通常 Epic 会提供）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable/Tests)（根据惯例，测试可能位于此路径）