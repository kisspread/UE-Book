# Variant Manager

> Manages scene actor variants

| 属性 | 值 |
|---|---|
| 中文名 | 变体管理器 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `VariantManager` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 🏛️ 文物（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/VariantManager) | |

## 用途

Variant Manager 是一个用于管理场景中 Actor 多状态变体的系统。它解决的核心问题是：在建筑可视化、产品配置器等场景中，你需要让场景中的物体能够在多种预设配置之间快速切换（例如椅子颜色、桌子样式、灯光配置等）。

该插件提供了一个层次化的数据结构：
- **Level Variant Sets**（顶层容器资产）→ 包含多个 **Variant Set**（变体集，如"椅子颜色"）→ 每个 Variant Set 包含多个 **Variant**（变体，如"红色"、"蓝色"）
- 每个 Variant 可以绑定多个 **Actor**，每个绑定可以捕获特定的 **Property**（属性，如变换、可见性、材质、自定义属性）
- 切换 Variant 时，系统会将记录的属性值应用到绑定的 Actor 上

该插件与 Datasmith 工作流紧密关联，是 Epic Games 企业级工具链的一部分，主要用于 Datasmith 导入的建筑/工业可视化项目的交互式配置。

> ⚠️ **注意**：该插件默认未启用（`EnabledByDefault: false`），且仍处于 Beta 状态（`IsBetaVersion: true`）。

## 使用场景

- 你在做一个建筑可视化项目（Arch-Viz），需要快速切换室内设计方案 → 用 Variant Manager 定义不同设计方案的变体集
- 你在做一个产品配置器，让用户选择产品的颜色、材质等选项 → 用 Variant Manager 管理每个配置选项
- 你从 Datasmith 导入了 CAD 模型，需要在不同组件配置之间切换 → 用 Variant Manager 组织和切换这些配置
- 你需要在运行时通过蓝图或 Python 脚本切换场景配置 → 用 Variant Manager Blueprint Library 提供的 API

## 蓝图用法

Variant Manager 通过 `UVariantManagerBlueprintLibrary` 暴露了大量蓝图可调用函数。该库被标记为 `ScriptName="VariantManagerLibrary"`，同时支持蓝图节点和 Python 脚本调用。

> 首次使用前需要手动启用插件：编辑 → 插件 → 搜索 "Variant Manager" → 启用 → 重启编辑器。

### 资产与 Actor 创建

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateLevelVariantSetsAsset` | 在指定路径创建 LevelVariantSets 资产 | `UVariantManagerBlueprintLibrary` |
| `CreateLevelVariantSetsActor` | 在当前场景创建 LevelVariantSetsActor 并关联资产 | `UVariantManagerBlueprintLibrary` |

### 变体层级管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddVariantSet` | 向 LevelVariantSets 添加变体集 | `UVariantManagerBlueprintLibrary` |
| `AddVariant` | 向 VariantSet 添加变体 | `UVariantManagerBlueprintLibrary` |
| `RemoveVariantSet` | 从 LevelVariantSets 移除变体集 | `UVariantManagerBlueprintLibrary` |
| `RemoveVariant` | 从 VariantSet 移除变体 | `UVariantManagerBlueprintLibrary` |
| `RemoveVariantSetByName` | 按名称查找并移除变体集 | `UVariantManagerBlueprintLibrary` |
| `RemoveVariantByName` | 按名称查找并移除变体 | `UVariantManagerBlueprintLibrary` |

### Actor 绑定与属性捕获

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddActorBinding` | 将 Actor 绑定到 Variant | `UVariantManagerBlueprintLibrary` |
| `CaptureProperty` | 为绑定的 Actor 捕获指定路径的属性 | `UVariantManagerBlueprintLibrary` |
| `GetCapturableProperties` | 获取 Actor 或类可捕获的所有属性路径 | `UVariantManagerBlueprintLibrary` |
| `GetCapturedProperties` | 获取 Variant 中某个 Actor 已捕获的属性列表 | `UVariantManagerBlueprintLibrary` |
| `RemoveActorBinding` | 从 Variant 移除 Actor 绑定 | `UVariantManagerBlueprintLibrary` |
| `RemoveCapturedProperty` | 移除捕获的属性 | `UVariantManagerBlueprintLibrary` |

### 属性录制与应用

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Record` | 从 Actor 当前状态录制属性值 | `UVariantManagerBlueprintLibrary` |
| `Apply` | 将录制的属性值应用到 Actor | `UVariantManagerBlueprintLibrary` |
| `GetPropertyTypeString` | 获取属性值的 C++ 类型字符串 | `UVariantManagerBlueprintLibrary` |

### 类型化属性访问器（PropertyAccessors）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetValueBool` / `GetValueBool` | 读写布尔属性 | `UVariantManagerBlueprintLibrary` |
| `SetValueInt` / `GetValueInt` | 读写整数属性 | `UVariantManagerBlueprintLibrary` |
| `SetValueFloat` / `GetValueFloat` | 读写浮点属性 | `UVariantManagerBlueprintLibrary` |
| `SetValueString` / `GetValueString` | 读写字符串属性 | `UVariantManagerBlueprintLibrary` |
| `SetValueVector` / `GetValueVector` | 读写向量属性 | `UVariantManagerBlueprintLibrary` |
| `SetValueRotator` / `GetValueRotator` | 读写旋转属性 | `UVariantManagerBlueprintLibrary` |
| `SetValueColor` / `GetValueColor` | 读写颜色属性 | `UVariantManagerBlueprintLibrary` |
| `SetValueLinearColor` / `GetValueLinearColor` | 读写线性颜色属性 | `UVariantManagerBlueprintLibrary` |
| `SetValueQuat` / `GetValueQuat` | 读写四元数属性 | `UVariantManagerBlueprintLibrary` |
| `SetValueObject` / `GetValueObject` | 读写 UObject 属性 | `UVariantManagerBlueprintLibrary` |
| `SetValueVector4` / `GetValueVector4` | 读写四维向量属性 | `UVariantManagerBlueprintLibrary` |
| `SetValueVector2D` / `GetValueVector2D` | 读写二维向量属性 | `UVariantManagerBlueprintLibrary` |
| `SetValueIntPoint` / `GetValueIntPoint` | 读写 IntPoint 属性 | `UVariantManagerBlueprintLibrary` |

### 函数调用器（FunctionCallers）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateFunctionCaller` | 创建函数调用器（指定签名类型） | `UVariantManagerBlueprintLibrary` |
| `AddFunctionCaller` | 添加函数调用器 | `UVariantManagerBlueprintLibrary` |
| `GetFunctionCallerNames` | 获取 Actor 的函数调用器名称列表 | `UVariantManagerBlueprintLibrary` |
| `GetFunctionCallerArguments` | 获取函数调用器的参数 | `UVariantManagerBlueprintLibrary` |
| `UpdateFunctionCallerArguments` | 更新函数调用器参数 | `UVariantManagerBlueprintLibrary` |
| `RemoveFunctionCaller` | 移除函数调用器 | `UVariantManagerBlueprintLibrary` |
| `GetOrCreateDirectorBlueprint` | 获取或创建 Director 蓝图 | `UVariantManagerBlueprintLibrary` |

### 变体依赖管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddDependency` | 添加变体依赖 | `UVariantManagerBlueprintLibrary` |
| `SetDependency` | 设置指定索引的依赖 | `UVariantManagerBlueprintLibrary` |
| `DeleteDependency` | 删除指定索引的依赖 | `UVariantManagerBlueprintLibrary` |
| `GetDependencies` | 获取所有依赖列表 | `UVariantManagerBlueprintLibrary` |

### 使用示例（蓝图描述）

**创建完整的变体配置流程**：

1. 调用 `CreateLevelVariantSetsAsset` 创建资产（AssetName="MyConfig"，AssetPath="/Game"）
2. 调用 `CreateLevelVariantSetsActor` 在场景中放置对应的 Actor
3. 创建 VariantSet：先用 `UVariantSet` 的 NewObject 创建，再调用 `AddVariantSet` 添加
4. 创建 Variant：先用 `UVariant` 的 NewObject 创建，再调用 `AddVariant` 添加
5. 调用 `AddActorBinding` 将目标 Actor 绑定到 Variant
6. 调用 `CaptureProperty` 捕获特定属性（PropertyPath 如 "RelativeLocation" 或 "StaticMeshComponent.Material[0]"）
7. 使用类型化访问器（如 `SetValueVector`）设置变体的属性值
8. 在运行时通过 `Apply` 切换变体状态

**运行时切换变体**：

获取 LevelVariantSetsActor → 获取其 LevelVariantSets → 查找 VariantSet → 查找 Variant → 调用 `Apply`（UVariant 本身也有 `SwitchOn` 方法）

## C++ 用法

### 头文件引入

```cpp
#include "VariantManagerModule.h"
#include "VariantManager.h"
#include "VariantManagerBlueprintLibrary.h"
```

### 基本用法

通过模块接口创建和使用 Variant Manager：

```cpp
// 通过模块接口创建 VariantManager 实例
// 来源: Source/VariantManager/Public/VariantManagerModule.h
IVariantManagerModule& VariantManagerModule = IVariantManagerModule::Get();

// 创建 LevelVariantSets 资产
UVariantManagerBlueprintLibrary::CreateLevelVariantSetsAsset(
    TEXT("MyLevelVariantSets"), TEXT("/Game"));

// 检查模块是否可用
if (IVariantManagerModule::IsAvailable())
{
    // 模块已加载，可以安全使用
}
```

### 进阶用法

使用 `FVariantManager` 进行属性捕获和管理：

```cpp
// 获取 FVariantManager 实例
// 来源: Source/VariantManager/Public/VariantManagerBlueprintLibrary.h
FVariantManager& Manager = UVariantManagerBlueprintLibrary::GetVariantManager();

// 初始化（绑定到 LevelVariantSets 资产）
Manager.InitVariantManager(MyLevelVariantSets);

// 获取 Actor 可捕获的属性
TArray<TSharedPtr<FCapturableProperty>> CapturableProps;
TArray<AActor*> Actors = { MyActor };
Manager.GetCapturableProperties(Actors, CapturableProps);

// 创建对象绑定并捕获属性
TArray<AActor*> SelectedActors = { Actor1, Actor2 };
TArray<UVariant*> Variants = { MyVariant };
TArray<UVariantObjectBinding*> Bindings = Manager.CreateObjectBindingsAndCaptures(
    SelectedActors, Variants);

// 录制属性值（将 Actor 当前状态保存到 Variant）
TArray<UPropertyValue*> PropValues;
for (UPropertyValue* Prop : MyBinding->GetPropertyValues())
{
    Manager.RecordProperty(Prop);
}

// 应用属性值（将 Variant 的值应用到 Actor）
for (UPropertyValue* Prop : MyBinding->GetPropertyValues())
{
    Manager.ApplyProperty(Prop);
}

// 调用 Director 函数
Manager.CallDirectorFunction(MyFunctionName, TargetObjectBinding);
```

使用 Blueprint Library 进行类型化属性操作：

```cpp
// 来源: Source/VariantManager/Public/VariantManagerBlueprintLibrary.h

// 获取 Actor 可捕获的属性列表
TArray<FString> PropertyPaths = UVariantManagerBlueprintLibrary::GetCapturableProperties(MyActor);

// 为 Variant 中的 Actor 捕获属性
UPropertyValue* PropVal = UVariantManagerBlueprintLibrary::CaptureProperty(
    MyVariant, MyActor, TEXT("RelativeLocation"));

// 设置属性值
UVariantManagerBlueprintLibrary::SetValueVector(PropVal, FVector(100, 200, 300));

// 获取属性值
FVector Location = UVariantManagerBlueprintLibrary::GetValueVector(PropVal);

// 录制和应用
UVariantManagerBlueprintLibrary::Record(PropVal);
UVariantManagerBlueprintLibrary::Apply(PropVal);

// 管理函数调用器
UVariantManagerBlueprintLibrary::CreateFunctionCaller(
    MyVariant, MyActor, TEXT("MyFunction"),
    EVariantFunctionCallerSignature::OneParameter);

// 管理依赖
FVariantDependency Dep;
// ... 配置依赖
UVariantManagerBlueprintLibrary::AddDependency(MyVariant, Dep);
```

## Demo 示例

以下是一个完整的最小示例，在运行时通过 C++ 代码创建变体配置并切换：

```cpp
// MyVariantManagerActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyVariantManagerActor.generated.h"

class ULevelVariantSets;
class UVariantSet;
class UVariant;

UCLASS()
class AMyVariantManagerActor : public AActor
{
    GENERATED_BODY()

public:
    AMyVariantManagerActor();

    virtual void BeginPlay() override;

    /** 切换到指定索引的变体 */
    UFUNCTION(BlueprintCallable)
    void SwitchToVariant(int32 VariantSetIndex, int32 VariantIndex);

    /** 用当前 Actor 状态录制所有变体的属性值 */
    UFUNCTION(BlueprintCallable)
    void RecordCurrentState();

protected:
    /** 配置目标 Actor（在编辑器中设置） */
    UPROPERTY(EditAnywhere, Category = "Variant Config")
    TArray<AActor*> TargetActors;

private:
    UPROPERTY()
    TObjectPtr<ULevelVariantSets> LevelVariantSets;

    UPROPERTY()
    TObjectPtr<UVariantSet> VariantSet;

    UPROPERTY()
    TObjectPtr<UVariant> VariantA;

    UPROPERTY()
    TObjectPtr<UVariant> VariantB;

    void SetupVariantConfiguration();
};
```

```cpp
// MyVariantManagerActor.cpp
#include "MyVariantManagerActor.h"
#include "VariantManagerModule.h"
#include "VariantManagerBlueprintLibrary.h"
#include "LevelVariantSets.h"
#include "LevelVariantSetsActor.h"
#include "Variant.h"
#include "VariantSet.h"
#include "PropertyValue.h"

AMyVariantManagerActor::AMyVariantManagerActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyVariantManagerActor::BeginPlay()
{
    Super::BeginPlay();

    if (!IVariantManagerModule::IsAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("VariantManager module not available"));
        return;
    }

    SetupVariantConfiguration();
}

void AMyVariantManagerActor::SetupVariantConfiguration()
{
    // 创建 LevelVariantSets 资产
    LevelVariantSets = UVariantManagerBlueprintLibrary::CreateLevelVariantSetsAsset(
        TEXT("MyVariantSets"), TEXT("/Game/VariantConfig"));

    if (!LevelVariantSets)
    {
        return;
    }

    // 创建 VariantSet
    VariantSet = UVariantManagerBlueprintLibrary::GetVariantManager()
        .CreateVariantSet(LevelVariantSets);

    if (!VariantSet)
    {
        return;
    }

    VariantSet->SetName(TEXT("ChairColor"));

    // 创建两个 Variant
    VariantA = UVariantManagerBlueprintLibrary::GetVariantManager()
        .CreateVariant(VariantSet);
    VariantA->SetName(TEXT("Red"));

    VariantB = UVariantManagerBlueprintLibrary::GetVariantManager()
        .CreateVariant(VariantSet);
    VariantB->SetName(TEXT("Blue"));

    // 为每个 Variant 绑定目标 Actor 并捕获属性
    for (AActor* Actor : TargetActors)
    {
        if (!Actor) continue;

        UVariantManagerBlueprintLibrary::AddActorBinding(VariantA, Actor);
        UVariantManagerBlueprintLibrary::AddActorBinding(VariantB, Actor);

        // 捕获可见性属性
        UVariantManagerBlueprintLibrary::CaptureProperty(
            VariantA, Actor, TEXT("StaticMeshComponent.bVisible"));
        UVariantManagerBlueprintLibrary::CaptureProperty(
            VariantB, Actor, TEXT("StaticMeshComponent.bVisible"));

        // 捕获材质属性
        UVariantManagerBlueprintLibrary::CaptureProperty(
            VariantA, Actor, TEXT("StaticMeshComponent.OverrideMaterials"));
        UVariantManagerBlueprintLibrary::CaptureProperty(
            VariantB, Actor, TEXT("StaticMeshComponent.OverrideMaterials"));
    }

    // 录制 VariantA 的当前状态
    RecordCurrentState();
}

void AMyVariantManagerActor::SwitchToVariant(int32 VariantSetIndex, int32 VariantIndex)
{
    if (!VariantSet) return;

    TArray<UVariant*> Variants = VariantSet->GetVariants();
    if (Variants.IsValidIndex(VariantIndex))
    {
        UVariantManagerBlueprintLibrary::GetVariantManager()
            .SwitchOnVariant(Variants[VariantIndex]);
    }
}

void AMyVariantManagerActor::RecordCurrentState()
{
    if (!VariantA) return;

    TArray<AActor*> BoundActors;
    for (auto& Binding : VariantA->GetObjectBindings())
    {
        if (Binding && Binding->GetObject().IsValid())
        {
            for (UPropertyValue* Prop : Binding->GetPropertyValues())
            {
                UVariantManagerBlueprintLibrary::Record(Prop);
            }
        }
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

该插件的 `VariantManager` 模块的 Build.cs 使用标准的 Unreal 模块依赖。其核心功能依赖于引擎内置的 Datasmith 相关类型（`ULevelVariantSets`、`UVariant`、`UVariantSet`、`UPropertyValue` 等），这些类型在引擎核心中定义。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新的 UE_LOGF 格式 |
| 2026-03-20 | `c5bb9adf` | [AutoViz] Minor updates to Variant Manager | 面向 AutoViz 的 Variant Manager 小幅更新 |
| 2025-10-30 | `0990a715` | Ran UnrealCodeFixup on Fortnite to change all ~Type() {} to instead be ~Type() = default | 自动代码修复：析构函数改用 = default |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 自动代码修复：引擎范围析构函数规范化 |

### 维护评价

- **创建时间**：2019 年 10 月，至今约 7 年
- **维护状态**：**活跃维护中** — 截至 2026 年 5 月仍有功能性更新（AutoViz 相关更新表明仍在积极适配新的使用场景）
- **Beta 状态**：`.uplugin` 中 `IsBetaVersion: true`，表明 Epic 仍将其视为实验性功能
- **默认未启用**：`EnabledByDefault: false`，用户需手动启用
- **已知限制**：Beta 阶段，API 可能在未来版本发生变化
- **推荐使用**：✅ 推荐用于建筑可视化和产品配置场景。该插件是 Datasmith 工作流的重要组成部分，虽然标记为 Beta 但已有多年稳定使用历史，且仍在持续维护更新。

> 注意：尽管该插件仍在活跃维护，但其 Beta 标记意味着 Epic 可能在未来版本中对其进行重大更改或重构。在生产环境中使用时需关注版本更新说明。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/VariantManager)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)