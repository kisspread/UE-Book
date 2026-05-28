# Mutable

> Mutable adds the tools and runtime to create customizable objects for your games.

| 属性 | 值 |
|---|---|
| 中文名 | 可定制对象 |
| 分类 | CustomizableObjects |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（核心模块、编辑器工具、运行时库） |
| 模块 | `CustomizableObject` (Runtime), `CustomizableObjectEditor` (Runtime), `MutableRuntime` (Runtime), `MutableTools` (Runtime), `MutableValidation` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-05 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable) | |

## 用途

Mutable 插件解决的是游戏运行时**角色、装备、外观高度可定制化**的核心问题。它提供了一套从“**声明式设计（蓝图/编辑器图）**”到“**运行时高效生成与渲染**”的完整方案。开发者可以在编辑器中，像组合乐高一样，通过一张节点图（Customizable Object）定义好所有可变部分（如皮肤、服装、纹身、发型、配饰）及其组合逻辑。运行时，玩家选择的参数（如 “脸型 A”、“发型 C”、“盔甲 漆黑”）会驱动引擎动态合成为一个单一、优化的 `SkeletalMesh` 和 `Material`，极大减少了因预设组合爆炸带来的美术工作量和内存占用。

## 使用场景

- **RPG/角色自定义**：玩家捏脸、换装、选择装备材质，实时看到变化。
- **战斗通行证/皮肤系统**：为武器、载具、宠物设计大量外观变体，无需创建数百个独立资产。
- **NPC外观生成**：在开放世界中，用一套基础模型动态生成大量外观各异的 NPC。
- **装备升级/附魔视觉**：装备升级后改变外观（如增加发光纹理、改变模型部件）。

## 蓝图用法

核心工作流通过 `CustomizableObject` 蓝图资产和 `CustomizableObjectInstance` 来驱动。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Customizable Object Instance` | 基于一个 CustomizableObject 模板创建运行时实例。 | `UCustomizableObject` |
| `Set Parameter Value (Int/Float/Bool/Color/Texture)` | 为实例设置具体的可选参数值（如选择发型索引、调整颜色）。 | `UCustomizableObjectInstance` |
| `Update Skeletal Mesh Async` | 异步生成或更新该实例所代表的 SkeletalMesh。这是触发外观生成的关键节点。 | `UCustomizableObjectInstance` |
| `Get Skeletal Mesh Component` | 获取生成的 SkeletalMeshComponent，用于挂载到角色上。 | `UCustomizableObjectInstance` |

### 使用示例（蓝图描述）
1.  **准备资产**：美术或技术美术在 `CustomizableObject Editor` 中绘制节点图，定义一个角色的所有可变部分，编译生成 `CustomizableObject` 资产。
2.  **蓝图中创建实例**：在角色蓝图中，使用 `Create Customizable Object Instance` 节点，传入上一步的 `CustomizableObject` 资产，得到一个空白的实例。
3.  **设置玩家选择**：当玩家在UI中选择“发型3”、“肤色2”时，调用实例的 `Set Parameter Value (Int)` 节点，分别设置对应参数。
4.  **应用外观**：调用 `Update Skeletal Mesh Async`，并绑定其完成回调。在回调中，通过 `Get Skeletal Mesh Component` 获取生成好的模型组件，`Set Skeletal Mesh` 应用到角色角色身上。

## C++ 用法

### 头文件引入
```cpp
#include "CustomizableObject.h"
#include "CustomizableObjectInstance.h"
```

### 基本用法
创建实例并异步生成网格体。
```cpp
// 假设 MyCustomizableObject 是已加载的 UCustomizableObject 资产指针
UCustomizableObjectInstance* COInstance = MyCustomizableObject->CreateInstance();
COInstance->SetIntParameterSelectedOption(FName("SkinType"), 1); // 设置皮肤类型参数
COInstance->SetFloatParameterValue(FName("GlowIntensity"), 0.8f); // 设置发光强度

// 异步更新网格体
FInstanceUpdateDelegate UpdateDelegate;
UpdateDelegate.BindUObject(this, &AMyCharacter::OnMutableMeshUpdated);
COInstance->UpdateSkeletalMeshAsync(UpdateDelegate, true); // true 表示更新所有LOD
```

### 进阶用法
管理多个实例和回调，处理生成过程中的状态。
```cpp
void AMyCharacter::OnMutableMeshUpdated(UCustomizableObjectInstance* Instance)
{
    // 检查生成是否成功
    if (Instance->IsUpdateError())
    {
        UE_LOG(LogTemp, Error, TEXT("Mutable Mesh Update Failed!"));
        return;
    }

    // 获取生成的 SkeletalMesh 并应用
    USkeletalMesh* GeneratedMesh = Instance->GetSkeletalMesh();
    if (GeneratedMesh)
    {
        MeshComponent->SetSkeletalMesh(GeneratedMesh);
        // 更新材质等其他组件...
    }
}
```

## Demo 示例

一个最小可运行示例的思路（需配合编辑器资产）：

**MyMutableCharacter.h**
```cpp
#pragma once
#include "GameFramework/Character.h"
#include "MyMutableCharacter.generated.h"

class UCustomizableObject;
class UCustomizableObjectInstance;

UCLASS()
class AMyMutableCharacter : public ACharacter
{
    GENERATED_BODY()
public:
    AMyMutableCharacter();

    UPROPERTY(EditAnywhere, Category = "Mutable")
    UCustomizableObject* BaseCustomizableObject;

    UPROPERTY()
    UCustomizableObjectInstance* CurrentInstance;

    UFUNCTION(BlueprintCallable)
    void ApplyCustomization(int32 SkinIndex, float SizeMultiplier);

    void OnMeshUpdateFinished(UCustomizableObjectInstance* Instance);
};
```

**MyMutableCharacter.cpp**
```cpp
#include "MyMutableCharacter.h"
#include "CustomizableObject.h"
#include "CustomizableObjectInstance.h"
#include "Components/SkeletalMeshComponent.h"

AMyMutableCharacter::AMyMutableCharacter()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyMutableCharacter::ApplyCustomization(int32 SkinIndex, float SizeMultiplier)
{
    if (!BaseCustomizableObject) return;

    if (!CurrentInstance)
    {
        CurrentInstance = BaseCustomizableObject->CreateInstance();
    }

    CurrentInstance->SetIntParameterSelectedOption(FName("BodySkin"), SkinIndex);
    CurrentInstance->SetFloatParameterValue(FName("Scale"), SizeMultiplier);

    FInstanceUpdateDelegate Delegate;
    Delegate.BindUObject(this, &AMyMutableCharacter::OnMeshUpdateFinished);
    CurrentInstance->UpdateSkeletalMeshAsync(Delegate, true);
}

void AMyMutableCharacter::OnMeshUpdateFinished(UCustomizableObjectInstance* Instance)
{
    if (Instance && !Instance->IsUpdateError())
    {
        if (USkeletalMesh* NewMesh = Instance->GetSkeletalMesh())
        {
            GetMesh()->SetSkeletalMesh(NewMesh);
            UE_LOG(LogTemp, Log, TEXT("Mutable character mesh updated successfully."));
        }
    }
}
```

## 模块依赖

此插件主要在引擎内部工作，对于游戏模块而言，依赖其运行时模块即可。

| 模块 | 用途 |
|---|---|
| `MutableRuntime` | 运行时核心库，负责实例化和网格体/材质生成。 |
| `MutableTools` | 提供编辑器中的图编辑、编译、优化等工具链。 |
| `CustomizableObject` | 封装 `UCustomizableObject` 和 `UCustomizableObjectInstance` 等蓝图/C++友好的高层API。 |

*注意：在游戏项目的 Build.cs 中，通常只需直接依赖 `CustomizableObject` 模块，它会自动传递依赖上述其他模块。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `70229bdc` | [Mutable] Fix duplicated Skeletal Mesh geometry if there is multiple SKM with the same name. | 修复同名多个 Skeletal Mesh 时几何体重复的 Bug。 |
| 2026-05-26 | `2b0ca8bd` | [mutable] Fixed "Clip mesh with UV Mask" op not loading the appropriate mask mip. | 修复“使用 UV 裁剪网格体”操作未加载正确遮罩 Mip 的 Bug。 |
| 2026-05-26 | `06ea27d3` | [Mutable] Fix texture parameters using the wrong method to compute the LODBias. An incorrect LODBias | 修复纹理参数计算 LODBias 方法错误导致 LOD 异常的问题。 |
| 2026-05-26 | `e9c39661` | [Mutable] Allow more clothing asset types by using the ClothingAssetBase interface. | 通过使用 ClothingAssetBase 接口，支持更多服装资产类型。 |
| 2026-05-25 | `c8ce9ff7` | [Mutable] Fix possible data race when comparing PassthroughObjects. | 修复比较 PassthroughObjects 时可能出现的线程数据竞争。 |

### 维护评价
**非常活跃**。该插件于 2024 年 9 月从 Experimental 状态正式迁移为 Beta，并持续获得 Epic 官方团队的密集维护。从近期提交记录可见，修复集中在运行时生成准确性、多线程安全和兼容性方面，表明项目已进入稳定优化阶段。考虑到其为大型项目提供核心外观定制功能，且维护积极，**强烈推荐**用于需要深度角色定制的新项目。需注意其仍处于 Beta 状态。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/customizable-objects-in-unreal-engine/) （Epic 官方提供的 Mutable 文档入口）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable/Tests)