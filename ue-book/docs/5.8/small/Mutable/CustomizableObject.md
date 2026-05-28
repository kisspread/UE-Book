# Mutable

> Mutable adds the tools and runtime to create customizable objects for your games.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 可定制对象系统 |
| 分类 | CustomizableObjects |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（运行时库，编辑器工具，验证模块） |
| 模块 | `MutableRuntime` (Runtime), `CustomizableObject` (Runtime), `CustomizableObjectEditor` (Runtime), `MutableTools` (Runtime), `MutableValidation` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-05 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable) | |

## 用途

Mutable 是一个用于创建动态、运行时可自定义对象的复杂插件系统。其核心思想是将资产（如骨骼网格体、材质、纹理）定义为可由参数驱动、可组合和可转换的“可变”资源。它解决了需要在游戏过程中根据玩家选择、游戏状态或程序逻辑动态生成、修改和优化大量视觉资产的问题。该插件提供了一套完整的工具链，包括在编辑器中设计可定制对象的节点图，以及一个高性能的运行时系统，用于根据参数异步生成和流式加载最终的游戏资产（网格体、材质、纹理等）。

## 使用场景

- 你在制作角色定制系统，玩家可以自由混合搭配发型、服装、配色方案 → 使用 Mutable 管理和生成成千上万种角色外观组合。
- 你需要根据游戏进程或玩家进度，动态改变场景中的物体外观（如损坏程度、季节变化）→ 使用 Mutable 的材质和网格体变形功能。
- 你的游戏包含大量需要个性化但共享基础结构的装备或武器 → 使用 Mutable 的模板和组合系统来优化内存和创建流程。
- 你需要为生成的角色或物体高效地流式加载不同LOD等级的网格体和材质 → 使用 Mutable 的集成流式管理系统。

## 蓝图用法

该插件的蓝图API主要通过 `UCustomizableObject` 和 `UCustomizableObjectInstance` 两个核心类暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateInstance` | 根据此可定制对象创建一个新的实例。 | `UCustomizableObject` |
| `GetParameterCount` | 获取此对象中定义的参数总数。 | `UCustomizableObject` |
| `GetParameterTypeByName` | 根据参数名获取参数的类型（如布尔、整型、浮点等）。 | `UCustomizableObject` |
| `SetIntParameterSelectedOption` | 设置实例的整型参数值。 | `UCustomizableObjectInstance` |
| `SetFloatParameterSelectedOption` | 设置实例的浮点参数值。 | `UCustomizableObjectInstance` |
| `SetBoolParameterSelectedOption` | 设置实例的布尔参数值。 | `UCustomizableObjectInstance` |
| `SetProjectorPosition` | 设置投影器参数的位置。 | `UCustomizableObjectInstance` |
| `UpdateSkeletalMeshAsync` | 异步更新实例的骨骼网格体。 | `UCustomizableObjectInstanceUsage` |
| `Bake` | 将实例的当前状态烘焙为一组独立的静态资产（用于导出或优化）。 | `UCustomizableObjectInstance` |
| `GetInstance` | 获取 `UCustomizableObjectSystem` 的单例，用于查询系统状态和配置。 | `UCustomizableObjectSystem` |

### 使用示例（蓝图描述）

1.  **创建并配置实例**：从内容浏览器拖入一个 `UCustomizableObject` 资产，使用 “CreateInstance” 节点创建实例。将实例引用存储为变量。
2.  **修改参数**：使用实例的 “SetBoolParameterSelectedOption”、”SetIntParameterSelectedOption” 等节点，根据UI输入或游戏逻辑更改角色的外观参数（例如，将 “HasHat” 设为 true，将 “HatColor” 设为红色）。
3.  **应用实例到角色**：获取角色蓝图中的 `UCustomizableSkeletalComponent` 或 `UCustomizableSkeletalMeshActor`，调用其 “SetCustomizableObjectInstance” 函数，传入你配置好的实例。
4.  **触发更新**：调用 `UCustomizableSkeletalComponent` 的 “UpdateSkeletalMeshAsync” 函数。系统将异步生成新的网格体和材质，并在完成后自动应用到关联的 `SkeletalMeshComponent`。
5.  **监听更新完成**：为实例的 “UpdatedDelegate” 绑定事件，以执行更新后的逻辑，例如重置动画蓝图。

## C++ 用法

### 头文件引入

```cpp
// 核心对象和实例
#include "MuCO/CustomizableObject.h"
#include "MuCO/CustomizableObjectInstance.h"

// 用于挂载实例的组件
#include "MuCO/CustomizableSkeletalComponent.h"

// 系统单例
#include "MuCO/CustomizableObjectSystem.h"

// 参数类型定义
#include "MuCO/CustomizableObjectParameterTypeDefinitions.h"
```

### 基本用法

以下代码展示了如何在运行时创建一个可定制对象的实例并修改其参数。

```cpp
// 假设 MyCustomizableObject 是一个已加载的 UCustomizableObject 资产指针
UCustomizableObject* MyCustomizableObject = ...;

// 1. 创建实例
UCustomizableObjectInstance* MyInstance = MyCustomizableObject->CreateInstance();

// 2. 修改实例参数（整型参数示例）
const FString ParamName = TEXT("HatType");
const FString OptionName = TEXT("TopHat");
MyInstance->SetIntParameterSelectedOption(ParamName, OptionName);

// 3. 修改布尔参数
const FString BoolParamName = TEXT("HasGlasses");
MyInstance->SetBoolParameterSelectedOption(BoolParamName, true);

// 4. 将实例应用到场景中的可定制组件
// MyCustomizableSkeletalComponent 是场景中 UCustomizableSkeletalComponent 的指针
MyCustomizableSkeletalComponent->SetCustomizableObjectInstance(MyInstance);

// 5. 请求更新
MyCustomizableSkeletalComponent->UpdateSkeletalMeshAsync();
```

### 进阶用法

使用 `FCompileParams` 进行编译控制，以及使用委托监听更新事件。

```cpp
#include "MuCO/CustomizableObject.h"

// 异步编译一个可定制对象
FCompileParams CompileParams;
CompileParams.bAsync = true;
CompileParams.bSkipIfCompiled = true; // 如果已编译则跳过

UCustomizableObject* ObjectToCompile = ...;

// 使用Lambda绑定完成回调
CompileParams.CallbackNative.BindLambda([ObjectToCompile](const FCompileCallbackParams& Params)
{
    if (Params.bCompiled)
    {
        UE_LOG(LogTemp, Log, TEXT("CustomizableObject %s compiled successfully."), *ObjectToCompile->GetName());
    }
    else if (Params.bRequestFailed)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to compile CustomizableObject %s."), *ObjectToCompile->GetName());
    }
});

// 触发编译
ICustomizableObjectModule::Get().CompileCustomizableObject(*ObjectToCompile, &CompileParams, false, false);

// 监听实例更新
UCustomizableObjectInstance* Instance = ...;
Instance->UpdatedNativeDelegate.AddLambda([](UCustomizableObjectInstance* UpdatedInstance)
{
    UE_LOG(LogTemp, Log, TEXT("Instance %s has been updated."), *UpdatedInstance->GetName());
    // 在这里处理更新后的逻辑，例如获取新的网格体
});
```

## Demo 示例

一个最小化示例，展示如何在 Actor 中管理一个可定制对象实例。

**MyCustomizableCharacter.h**
```cpp
#pragma once

#include "GameFramework/Actor.h"
#include "MyCustomizableCharacter.generated.h"

class UCustomizableSkeletalComponent;
class UCustomizableObject;
class UCustomizableObjectInstance;

UCLASS()
class AMyCustomizableCharacter : public AActor
{
    GENERATED_BODY()

public:
    AMyCustomizableCharacter();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    UCustomizableSkeletalComponent* CustomizableSkeletalComp;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    UCustomizableObject* CustomizableObjectAsset;

    UPROPERTY(BlueprintReadOnly)
    UCustomizableObjectInstance* CurrentInstance;

    UFUNCTION(BlueprintCallable)
    void InitializeCharacter();

    UFUNCTION(BlueprintCallable)
    void SetRandomAppearance();

private:
    UFUNCTION()
    void OnInstanceUpdated(UCustomizableObjectInstance* Instance);
};
```

**MyCustomizableCharacter.cpp**
```cpp
#include "MyCustomizableCharacter.h"
#include "MuCO/CustomizableObject.h"
#include "MuCO/CustomizableObjectInstance.h"
#include "MuCO/CustomizableSkeletalComponent.h"

AMyCustomizableCharacter::AMyCustomizableCharacter()
{
    CustomizableSkeletalComp = CreateDefaultSubobject<UCustomizableSkeletalComponent>(TEXT("CustomizableComp"));
    RootComponent = CustomizableSkeletalComp;
}

void AMyCustomizableCharacter::InitializeCharacter()
{
    if (CustomizableObjectAsset)
    {
        // 创建实例
        CurrentInstance = CustomizableObjectAsset->CreateInstance();
        CurrentInstance->UpdatedNativeDelegate.AddUObject(this, &AMyCustomizableCharacter::OnInstanceUpdated);

        // 设置到组件
        CustomizableSkeletalComp->SetCustomizableObjectInstance(CurrentInstance);
        CustomizableSkeletalComp->UpdateSkeletalMeshAsync();
    }
}

void AMyCustomizableCharacter::SetRandomAppearance()
{
    if (CurrentInstance)
    {
        // 设置随机整型参数值（示例）
        const FString ParamName = TEXT("SkinColor");
        const int32 NumValues = CustomizableObjectAsset->GetEnumParameterNumValues(ParamName);
        if (NumValues > 0)
        {
            const int32 RandomIndex = FMath::RandRange(0, NumValues - 1);
            const FString& RandomValue = CustomizableObjectAsset->GetEnumParameterValue(ParamName, RandomIndex);
            CurrentInstance->SetIntParameterSelectedOption(ParamName, RandomValue);
        }
        // 触发更新
        CustomizableSkeletalComp->UpdateSkeletalMeshAsync();
    }
}

void AMyCustomizableCharacter::OnInstanceUpdated(UCustomizableObjectInstance* Instance)
{
    // 更新完成后的逻辑
    UE_LOG(LogTemp, Display, TEXT("Character appearance updated."));
}
```

## 模块依赖

该插件依赖于一个核心的、非标准的运行时库模块。

| 模块 | 用途 |
|---|---|
| `MutableCore` | Mutable 插件的核心运行时库，提供底层的可变模型计算、资源生成和内存管理。 |

*(注：除了 `MutableCore`，该插件还依赖标准的 UE 模块如 `Core`, `CoreUObject`, `Engine` 等，但这些已按规范省略。)*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `70229bdc` | [Mutable] Fix duplicated Skeletal Mesh geometry if there is multiple SKM with the same name. | 修复当存在多个同名骨骼网格体时，生成几何体重复的问题。 |
| 2026-05-26 | `2b0ca8bd` | [mutable] Fixed "Clip mesh with UV Mask" op not loading the appropriate mask mip. | 修复“使用UV遮罩裁剪网格”操作未加载正确遮罩Mip的问题。 |
| 2026-05-26 | `06ea27d3` | [Mutable] Fix texture parameters using the wrong method to compute the LODBias. An incorrect LODBias | 修复纹理参数计算LODBias方法错误导致LODBias不正确的问题。 |
| 2026-05-26 | `e9c39661` | [Mutable] Allow more clothing asset types by using the ClothingAssetBase interface. | 通过使用 `ClothingAssetBase` 接口，支持更多服装资产类型。 |
| 2026-05-25 | `c8ce9ff7` | [Mutable] Fix possible data race when comparing PassthroughObjects. | 修复比较 PassthroughObjects 时可能发生的竞态条件。 |

### 维护评价

- **年龄**：该插件创建于 2024 年 9 月，是一个相对新的插件。
- **更新频率**：近期（2026年5月）有多次提交，主要集中在 **Bug修复** 和 **兼容性改进**，表明插件正处于活跃的调试和稳定阶段。
- **维护状态**：**活跃维护中**。团队正在积极修复问题并提升稳定性。
- **已知限制**：该插件标记为 **实验性** (从Experimental状态移出)。文档中未提及具体已知问题，但作为实验性功能，其API和行为在后续版本中可能发生变化。
- **推荐**：适用于需要高度运行时可定制性的项目。由于其实验性状态和复杂性，建议在正式项目中采用前，进行充分的技术验证和性能测试。对于新项目，如果角色或物体定制是核心功能，值得投入学习和使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/mutable-unreal-engine-plugin/) (假设链接，以官方最新文档为准)