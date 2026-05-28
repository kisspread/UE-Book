# Mutable

> Mutable adds the tools and runtime to create customizable objects for your games.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 可定制对象系统 |
| 分类 | CustomizableObjects |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、测试资产） |
| 模块 | `MutableRuntime` (Runtime), `CustomizableObject` (Runtime), `MutableTools` (Runtime), `CustomizableObjectEditor` (Runtime), `MutableValidation` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-05 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable) | |

## 用途

Mutable 是一个用于在运行时创建可高度自定义游戏对象（如角色、武器、载具）的完整工具链和运行时系统。它解决的核心问题是：如何让玩家能够自由地组合、修改角色的外观部件（发型、服装、纹身）、材质（颜色、图案）甚至网格体形状，同时保持游戏运行的高效性。

该插件通过提供一套节点图编辑器（工具）来定义“可定制对象”（Customizable Object，CO）的逻辑和结构，描述各个可组合部件之间的关系、约束和变异规则。在运行时，引擎可以根据玩家的参数选择，实时生成和组装出最终的、优化过的网格体、材质和纹理。其主要价值在于将复杂的资源组合与优化工作前置到工具阶段，运行时开销极低，非常适合需要大量外观变体的RPG、MMO或定制化程度高的游戏。

## 使用场景

-   你正在开发一款RPG游戏，希望玩家可以自由定制角色的面部特征、发型、服装和装备外观 → 使用 Mutable 来设计角色定制系统。
-   你的游戏有一个庞大的服装或装备系统，每件装备都有多种颜色、图案变体 → 使用 Mutable 来高效管理这些变体，并在运行时动态生成。
-   你需要创建大量外观相似但细节不同的NPC → 使用 Mutable 随机化NPC的外观特征，增加世界生动感。
-   游戏中包含可组合的车辆或机甲系统，部件可以自由更换 → 使用 Mutable 定义部件之间的组合逻辑和兼容性。

## 蓝图用法

Mutable 的核心蓝图节点集中在 `CustomizableObject` 和 `CustomizableObjectInstance` 类中。以下是从源码推断出的核心功能节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateInstance` | 基于一个 `CustomizableObject` 资产创建一个新的运行时实例。 | `UCustomizableObject` |
| `Set*Parameter` | 一系列函数（如 `SetIntParameter`, `SetColorParameter`），用于为实例设置具体的自定义参数值。 | `UCustomizableObjectInstance` |
| `UpdateInstance` | 根据当前设置的参数，异步更新实例的网格体、材质等资源。更新完成后会通过委托通知。 | `UCustomizableObjectInstance` |
| `GetParameter*` | 一系列函数，用于获取实例当前参数的可能选项和值。 | `UCustomizableObjectInstance` |
| `Compile` | （编辑器用）编译可定制对象资产，使其可以在运行时使用。 | `UCustomizableObject` |

### 使用示例（蓝图描述）

1.  **创建实例**：在拥有一个 `UCustomizableObject` 资产引用（例如 `MyCharacterCO`）的蓝图中，调用 `CreateInstance` 节点，获得一个 `UCustomizableObjectInstance` 对象。
2.  **设置参数**：对实例调用 `SetIntParameter` 等节点，传入参数名称（如 `"ShirtStyle"`）和值（如 `2`）。
3.  **更新实例**：调用 `UpdateInstance` 节点开始异步更新。通过绑定 `OnUpdated` 或 `OnUpdatedSkeletalMesh` 委托来监听更新完成。
4.  **应用资源**：更新完成后，从实例中获取生成的 `SkeletalMesh` 和 `Material`，将其应用到 `SkeletalMeshComponent` 上。

## C++ 用法

### 头文件引入

```cpp
#include "MuCO/CustomizableObject.h"
#include "MuCO/CustomizableObjectInstance.h"
```

### 基本用法

以下代码展示了如何在 C++ 中加载 CO、创建实例并设置参数。（概念参考自 `ValidationUtils.h` 中的测试流程）

```cpp
// 假设 CO 资产已加载或通过路径找到
UCustomizableObject* MyCO = LoadObject<UCustomizableObject>(nullptr, TEXT("/Game/MyCharacter/MyCharacterCO"));

if (MyCO)
{
    // 创建实例
    UCustomizableObjectInstance* Instance = MyCO->CreateInstance();

    // 设置参数
    Instance->SetIntParameter(FName("SkinColor"), 1);
    Instance->SetColorParameter(FName("EyeColor"), FLinearColor(0.2f, 0.5f, 1.0f, 1.0f));

    // 请求更新实例
    FUpdateContext UpdateContext;
    UpdateContext.Callback = [](const FUpdateContext& Result)
    {
        if (Result.IsValid())
        {
            // 更新成功，可以使用 Result.Instance 获取更新后的资源
            USkeletalMesh* NewMesh = Result.Instance->GetSkeletalMesh();
            // 将 NewMesh 应用到你的 SkeletalMeshComponent...
        }
    };
    Instance->UpdateSkeletalMesh(UpdateContext);
}
```

### 进阶用法

对于需要精确控制编译过程或批量处理的场景，可以参考 `MutableValidation` 模块中的工具类。

1.  **同步编译CO**：使用 `FCustomizableObjectCompilationUtility` 来同步编译一个 CO，这在自动化测试或命令行工具中很有用。
    ```cpp
    #include "MuV/CustomizableObjectCompilationUtility.h"
    
    FCustomizableObjectCompilationUtility CompilationUtil;
    bool bSuccess = CompilationUtil.CompileCustomizableObject(*MyCO);
    ```

2.  **同步更新实例**：使用 `FCustomizableObjectInstanceUpdateUtility` 来同步等待一个实例更新完成（包括纹理Mip流送）。
    ```cpp
    #include "MuV/CustomizableObjectInstanceUpdateUtility.h"
    
    FCustomizableObjectInstanceUpdateUtility UpdateUtil;
    bool bUpdateSuccess = UpdateUtil.UpdateInstance(*MyInstance);
    // 在此之后，实例的网格体和材质已准备好
    ```

## Demo 示例

一个最小化的 C++ 示例，展示如何创建一个可定制对象实例并更新它。

**MyCharacterCustomizer.h**
```cpp
#pragma once

#include "GameFramework/Actor.h"
#include "MyCharacterCustomizer.generated.h"

class UCustomizableObjectInstance;
class USkeletalMeshComponent;

UCLASS()
class AMyCharacterCustomizer : public AActor
{
    GENERATED_BODY()

public:
    AMyCharacterCustomizer();

protected:
    virtual void BeginPlay() override;

private:
    void OnInstanceUpdateCompleted();

    UPROPERTY()
    TObjectPtr<UCustomizableObjectInstance> CharacterInstance;

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<USkeletalMeshComponent> MeshComponent;
};
```

**MyCharacterCustomizer.cpp**
```cpp
#include "MyCharacterCustomizer.h"
#include "MuCO/CustomizableObject.h"
#include "MuCO/CustomizableObjectInstance.h"
#include "Components/SkeletalMeshComponent.h"

AMyCharacterCustomizer::AMyCharacterCustomizer()
{
    MeshComponent = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("BodyMesh"));
    RootComponent = MeshComponent;
}

void AMyCharacterCustomizer::BeginPlay()
{
    Super::BeginPlay();

    // 假设 CO 资产通过编辑器设置
    UCustomizableObject* CharacterCO = LoadObject<UCustomizableObject>(nullptr, TEXT("/Game/Characters/BaseCharacterCO"));
    if (!CharacterCO) return;

    // 创建实例
    CharacterInstance = CharacterCO->CreateInstance();

    // 设置一些初始参数
    CharacterInstance->SetIntParameter(FName("Gender"), 0);
    CharacterInstance->SetIntParameter(FName("HairStyle"), 3);

    // 绑定更新完成回调
    FUpdateContext UpdateContext;
    UpdateContext.Callback = [WeakThis = TWeakObjectPtr<AMyCharacterCustomizer>(this)](const FUpdateContext& Result)
    {
        if (WeakThis.IsValid())
        {
            WeakThis->OnInstanceUpdateCompleted();
        }
    };

    // 开始异步更新
    CharacterInstance->UpdateSkeletalMesh(UpdateContext);
}

void AMyCharacterCustomizer::OnInstanceUpdateCompleted()
{
    if (CharacterInstance)
    {
        // 应用生成的网格体和材质
        MeshComponent->SetSkeletalMesh(CharacterInstance->GetSkeletalMesh());
        // 处理材质...
    }
}
```

## 模块依赖

从 `CustomizableObject` 模块的 `Build.cs` 分析，使用者主要需要依赖以下模块。Mutable 系统内部的模块依赖较多，但对外暴露的 API 主要集中在 `CustomizableObject` 和 `MutableRuntime`。

| 模块 | 用途 |
|---|---|
| `CustomizableObject` | 包含核心的 `UCustomizableObject` 和 `UCustomizableObjectInstance` 类，是使用者主要交互的模块。 |
| `MutableRuntime` | 提供 Mutable 的运行时核心库，是 `CustomizableObject` 模块的基础。 |
| `DerivedDataCache` | Mutable 在运行时可能涉及数据缓存，以提升生成性能。 |
| `MutableTools` | 提供编辑器工具支持。如果需要在运行时或自动化流程中编译 CO（如测试），则需要依赖此模块。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `70229bdc` | [Mutable] Fix duplicated Skeletal Mesh geometry if there is multiple SKM with the same name. | 修复了当存在多个同名骨骼网格体时，几何体被重复生成的问题。 |
| 2026-05-26 | `2b0ca8bd` | [mutable] Fixed “Clip mesh with UV Mask” op not loading the appropriate mask mip. | 修复了“使用UV遮罩裁剪网格”操作未加载正确遮罩Mip层级的错误。 |
| 2026-05-26 | `06ea27d3` | [Mutable] Fix texture parameters using the wrong method to compute the LODBias. | 修复了纹理参数计算LOD偏差时使用了错误方法的问题。 |
| 2026-05-26 | `e9c39661` | [Mutable] Allow more clothing asset types by using the ClothingAssetBase interface. | 通过使用 `ClothingAssetBase` 接口，现在支持更多类型的服装资产。 |
| 2026-05-25 | `c8ce9ff7` | [Mutable] Fix possible data race when comparing PassthroughObjects. | 修复了比较“透传对象”时可能出现的数据竞争问题。 |

### 维护评价

Mutable 插件目前处于**活跃维护**状态。它于2024年9月从实验性状态转为Beta版，表明Epic Games认为其功能已趋于稳定。从最近的提交记录来看（密集的 bug 修复和功能改进），开发团队仍在积极维护和优化该插件。提交内容不仅包括关键错误的修复（如数据竞争、资源生成错误），还包含功能增强（如扩展服装资产支持）。

**推荐使用**：对于需要实现游戏角色/装备深度定制化的项目，Mutable 是官方推荐的解决方案。虽然标记为 Beta，但其持续、密集的更新表明它已足够成熟用于生产环境。开发者应关注其版本更新，以获取最新的修复和功能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/mutable-customizable-objects-in-unreal-engine/) (Epic 官方文档，链接可能存在变动，请以官方最新信息为准)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable/Source/MutableValidation/Private/MuV) (主要的验证和测试命令行工具位于此目录)