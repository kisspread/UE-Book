# Variant Manager Content

> Data classes and assets for the Variant Manager plugin（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 变体管理器内容 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `VariantManagerContent` (Runtime), `VariantManagerContentEditor` (Editor) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2018-09-04 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/VariantManagerContent) | |

## 用途

`VariantManagerContent` 插件是 **Variant Manager** (变体管理器) 的核心数据层。它本身不提供编辑器 UI 或工作流，而是为 `VariantManager` 插件提供必要的**数据资产类**和**运行时支持**。

Variant Manager 用于管理基于 Datasmith 工作流的可视化变体。想象一下：你导入了一个包含多种材质、家具或布局的建筑场景，设计师需要快速切换这些设计选项进行展示。`VariantManagerContent` 定义了存储和组织这些“选项”（称为 Variant）的数据结构，例如 `LevelVariantSets`、`VariantSet` 和 `Variant`。它使得设计师可以在编辑器中捕获 Actor 的属性值作为变体，并在运行时（或编辑器预览时）通过蓝图或代码动态切换这些变体，从而高效地创建交互式产品配置器、建筑可视化演示或汽车内饰展示。

## 使用场景

- **建筑可视化 (ArchViz)**：为同一个客厅场景配置不同的家具组合、墙面材质和灯光方案，并在演示中实时切换。
- **产品配置器**：展示一辆汽车的不同颜色、轮毂样式和内饰选项，让客户在网页或应用中自由搭配。
- **工业设计评审**：快速对比一个产品的多种原型设计方案，评估设计变更的影响。
- **数字化展厅**：在虚拟展厅中，让访客通过点击按钮改变展品的外观、布局或信息。

## 蓝图用法

搜索 `UFUNCTION(BlueprintCallable)` 和 `UPROPERTY(BlueprintReadWrite)`。核心类和节点围绕“变体集”和“变体”数据资产展开。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Variant Sets` | 获取当前关卡变体集资产中包含的所有变体集（VariantSet）的数组。 | `ULevelVariantSets` |
| `Get Variants` | 获取指定变体集中包含的所有变体（Variant）的数组。 | `UVariantSet` |
| `Switch On Variant` | 激活一个变体，将其捕获的属性值应用到对应的 Actor 上。 | `UVariant` |
| `Set Display Text` | 为变体设置显示文本，用于在 UI 中展示。 | `UVariant` |
| `Get Actor` | 获取与该变体属性绑定关联的 Actor。 | `UVariantBinding` |
| `Capture Property` | 捕获 Actor 的某个属性当前值，并记录到绑定中。 | `UVariant` |

### 使用示例（蓝图描述）

假设你有一个名为 `BP_LevelVariantSets` 的关卡变体集资产，其中包含一个名为 “VS_Furniture” 的变体集，该变体集下有两个变体：“V_SofaRed” 和 “V_SofaBlue”。

1.  **获取变体集**：在角色蓝图的 `BeginPlay` 事件中，使用 “Get Variant Sets” 节点从 `BP_LevelVariantSets` 中获取所有变体集，并存为数组 `VariantSetsArray`。
2.  **切换变体**：在 UI 按钮的点击事件中，找到 `VariantSetsArray` 中对应 “VS_Furniture” 的元素（UVariantSet 对象）。然后，使用 “Switch On Variant” 节点，传入 “V_SofaBlue” 这个 UVariant 对象。执行后，场景中沙发模型的材质属性会立即变为蓝色。
3.  **创建数据资产**：在编辑器中，右键点击 Content Browser，选择 “Variant Manager” -> “Level Variant Sets” 来创建新的资产。然后通过 Variant Manager 面板（需要启用 VariantManager 插件）来可视化地添加变体集和变体，并捕获 Actor 属性。

## C++ 用法

重点从测试用例中提取，贴近官方用法。

### 头文件引入

```cpp
#include "LevelVariantSets.h"
#include "Variant.h"
#include "VariantSet.h"
```

### 基本用法

```cpp
// 来源：引擎内部测试逻辑
// 创建一个用于测试的 Actor
AVariantManagerTestActor* TestActor = GetWorld()->SpawnActor<AVariantManagerTestActor>();

// 创建一个变体集和一个变体
UVariantSet* VariantSet = NewObject<UVariantSet>();
UVariant* Variant = NewObject<UVariant>();

// 设置变体的基本信息
Variant->SetDisplayText(FText::FromString(TEXT("我的变体")));
VariantSet->SetDisplayText(FText::FromString(TEXT("测试变体集")));

// 将变体添加到变体集中
VariantSet->AddVariant(Variant);

// 为变体捕获 TestActor 的 CapturedFloatProperty 属性
// 这会在 Variant 内部创建一个 UVariantBinding 来记录此属性
Variant->AddBindingsForActorProperties(TestActor, {GET_MEMBER_NAME_CHECKED(AVariantManagerTestActor, CapturedFloatProperty)});

// 可以立即修改属性值，例如将其设为一个新值
TestActor->CapturedFloatProperty = 999.0f;

// 再次捕获属性，此时绑定会记录新的值（999.0f）
Variant->CaptureForActorProperties(TestActor);

// 在之后需要时，可以通过应用变体来恢复这个值
Variant->ApplyForActorProperties(TestActor); // Actor 的 CapturedFloatProperty 将变为 999.0f
```

### 进阶用法

```cpp
// 组合使用多个变体和运行时查询
#include "LevelVariantSetsActor.h"

// 假设场景中已放置了一个 ALevelVariantSetsActor
ALevelVariantSetsActor* LVSetActor = /* ... 获取引用 ... */;

// 获取其关联的 ULevelVariantSets 资产
ULevelVariantSets* LevelVariantSets = LVSetActor->GetLevelVariantSets();

if (LevelVariantSets)
{
    // 获取第一个变体集
    UVariantSet* FirstVariantSet = LevelVariantSets->GetVariantSet(0);
    if (FirstVariantSet)
    {
        // 遍历该变体集下的所有变体
        TArray<UVariant*> Variants;
        FirstVariantSet->GetVariants(Variants);

        for (UVariant* Var : Variants)
        {
            // 检查变体是否应用了特定 Actor 的某个属性
            bool bIsApplied = Var->IsActorPropertyApplied(TestActor, GET_MEMBER_NAME_CHECKED(AVariantManagerTestActor, CapturedVectorProperty));

            // 获取变体对该属性的捕获值（如果存在）
            // 注意：这只是一个示意，实际获取捕获值需要更深入访问内部绑定数据
            // 通常使用 Apply 来恢复值，而不是直接读取捕获的原始数据。
        }

        // 应用整个变体集（相当于依次应用其下所有变体）
        FirstVariantSet->ApplyVariants();
    }
}
```

## Demo 示例

一个完整的、可编译的最小示例，展示如何在代码中创建和操作变体数据。

```cpp
// VariantManagerDemo.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "VariantManagerDemo.generated.h"

class AVariantManagerTestActor;
class ULevelVariantSets;
class UVariantSet;
class UVariant;

UCLASS()
class AMyVariantManagerDemoActor : public AActor
{
    GENERATED_BODY()

public:
    AMyVariantManagerDemoActor();

protected:
    virtual void BeginPlay() override;

public:
    // 在编辑器中指定要控制的测试 Actor
    UPROPERTY(EditAnywhere, Category="Demo")
    TSoftObjectPtr<AVariantManagerTestActor> TargetTestActor;

    // 用于存储创建的变体集资产（仅为演示，实际中应保存到磁盘）
    UPROPERTY(Transient)
    TObjectPtr<ULevelVariantSets> DemoVariantSetAsset;

    UPROPERTY(Transient)
    TObjectPtr<UVariantSet> DemoVariantSet;

    UPROPERTY(Transient)
    TObjectPtr<UVariant> RedVariant;

    UPROPERTY(Transient)
    TObjectPtr<UVariant> BlueVariant;

    // 用于切换的函数
    UFUNCTION(BlueprintCallable, CallInEditor, Category="Demo")
    void SwitchToRed();

    UFUNCTION(BlueprintCallable, CallInEditor, Category="Demo")
    void SwitchToBlue();

private:
    void CreateDemoVariants();
    void ApplyColorVariantToTarget(UVariant* Variant, const FLinearColor& Color);
};
```

```cpp
// VariantManagerDemo.cpp
#include "VariantManagerDemo.h"
#include "LevelVariantSets.h"
#include "VariantSet.h"
#include "Variant.h"
#include "VariantManagerTestActor.h" // 来自 VariantManagerContentEditor 模块

AMyVariantManagerDemoActor::AMyVariantManagerDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyVariantManagerDemoActor::BeginPlay()
{
    Super::BeginPlay();
    CreateDemoVariants();
}

void AMyVariantManagerDemoActor::CreateDemoVariants()
{
    AVariantManagerTestActor* TestActor = TargetTestActor.LoadSynchronous();
    if (!TestActor) return;

    // 1. 创建数据资产
    DemoVariantSetAsset = NewObject<ULevelVariantSets>(GetTransientPackage(), TEXT("DemoLVSet"));
    DemoVariantSet = NewObject<UVariantSet>(DemoVariantSetAsset, TEXT("ColorVariants"));
    RedVariant = NewObject<UVariant>(DemoVariantSet, TEXT("Red"));
    BlueVariant = NewObject<UVariant>(DemoVariantSet, TEXT("Blue"));

    // 2. 设置显示文本
    DemoVariantSet->SetDisplayText(FText::FromString(TEXT("颜色方案")));
    RedVariant->SetDisplayText(FText::FromString(TEXT("红色")));
    BlueVariant->SetDisplayText(FText::FromString(TEXT("蓝色")));

    // 3. 构建层级关系
    DemoVariantSetAsset->AddVariantSet(DemoVariantSet);
    DemoVariantSet->AddVariant(RedVariant);
    DemoVariantSet->AddVariant(BlueVariant);

    // 4. 捕获属性并设置初始值
    // 捕获 CapturedLinearColorProperty 属性
    RedVariant->AddBindingsForActorProperties(TestActor, {GET_MEMBER_NAME_CHECKED(AVariantManagerTestActor, CapturedLinearColorProperty)});
    BlueVariant->AddBindingsForActorProperties(TestActor, {GET_MEMBER_NAME_CHECKED(AVariantManagerTestActor, CapturedLinearColorProperty)});

    // 为变体设置目标值（虽然 Capture 会记录当前值，但我们可以提前修改）
    TestActor->CapturedLinearColorProperty = FLinearColor::Red;
    RedVariant->CaptureForActorProperties(TestActor); // 捕获红色值

    TestActor->CapturedLinearColorProperty = FLinearColor::Blue;
    BlueVariant->CaptureForActorProperties(TestActor); // 捕获蓝色值
}

void AMyVariantManagerDemoActor::SwitchToRed()
{
    if (RedVariant) ApplyColorVariantToTarget(RedVariant, FLinearColor::Red);
}

void AMyVariantManagerDemoActor::SwitchToBlue()
{
    if (BlueVariant) ApplyColorVariantToTarget(BlueVariant, FLinearColor::Blue);
}

void AMyVariantManagerDemoActor::ApplyColorVariantToTarget(UVariant* Variant, const FLinearColor& Color)
{
    AVariantManagerTestActor* TestActor = TargetTestActor.LoadSynchronous();
    if (Variant && TestActor)
    {
        Variant->ApplyForActorProperties(TestActor);
        UE_LOG(LogTemp, Log, TEXT("已应用变体: %s, Actor 颜色现在应为: %s"), *Variant->GetDisplayText().ToString(), *Color.ToString());
    }
}
```

## 模块依赖

从 `Build.cs` 文件中提取。要使用此插件，你的模块可能需要依赖以下内容：

### VariantManagerContent (Runtime) 模块
| 模块 | 用途 |
|---|---|
| `VariantManager` | 核心运行时逻辑，提供 `UObject` 变体系统实现 |

### VariantManagerContentEditor (Editor) 模块
| 模块 | 用途 |
|---|---|
| `EditorStyle` | 提供编辑器 UI 样式 |
| `PropertyEditor` | 提供细节面板自定义等功能 |
| `VariantManager` | 与 Runtime 模块共享逻辑 |

**说明**：对于大多数使用场景（仅在编辑器中配置变体，并在运行时应用），你**不需要直接依赖这些模块**。你的项目只需启用 `VariantManager` 和 `VariantManagerContent` 插件即可。只有当你编写自定义的编辑器扩展或资产类型工厂时，才需要考虑依赖 `VariantManagerContentEditor`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `0a77223b` | Fixed crash in LevelVariantSet.cpp | 修复了 LevelVariantSet.cpp 中的崩溃问题 |
| 2026-04-16 | `0b4d09a4` | [ContentBrowser] New Add Menu Data Menu | 为内容浏览器添加了新的“添加”菜单数据选项 |
| 2026-04-14 | `50042443` | TLazyObjectPtr Deprecation: | 处理了 TLazyObjectPtr 的弃用警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的 UE_LOG 宏迁移到新的 UE_LOGF 宏 |
| 2026-03-20 | `c5bb9adf` | [AutoViz] Minor updates to Variant Manager | 自动可视化相关的变体管理器小更新 |

### 维护评价

- **创建时间**：2018年创建，已有约8年历史，属于较老的插件。
- **更新频率**：近期（2026年3-5月）有数次提交，主要涉及 Bug 修复、代码现代化（宏迁移、弃用处理）和小的功能调整（如菜单项更新）。这表明该插件仍在维护中，但主要是维护性更新而非大量新功能。
- **状态**：**实验性（Beta）**。`.uplugin` 中明确标记 `IsBetaVersion: true`，这意味着其 API 或行为可能在未来的引擎版本中发生变化，不建议在追求极致稳定性的项目中作为核心依赖。
- **推荐度**：**中等**。对于 Datasmith/建筑可视化工作流，它几乎是必需的。但使用者需接受其“实验性”标签，并留意引擎升级时可能出现的兼容性问题。由于近期仍有维护，短期内可以放心使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/VariantManagerContent)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/VariantManagerContent/Source/VariantManagerContentEditor) (主要测试逻辑位于 `Public/VariantManagerTestActor.h` 中定义的测试 Actor)