# MetaHuman Creator

> MetaHuman Character Asset Creator and Editor.

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman默认管线 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资产） |
| 模块 | `MetaHumanDefaultPipeline` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-03-17 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanCharacter) | |

## 用途

`MetaHumanDefaultPipeline` 是 MetaHuman Character 插件的核心构建模块。它不是用于创建或编辑角色资产的工具界面，而是定义了**默认的资产装配流程**。该模块的核心职责是将构成一个 MetaHuman 角色的各种独立资产（如面部/身体骨骼网格、头发、眉毛、服装等）按照一套标准化的流程组装（Assemble）成一个完整的、可在游戏引擎中运行的角色。它解决了如何标准化、自动化地组合复杂数字人资产的问题，为开发者提供了一个开箱即用的基础装配管线。

## 使用场景

-   **创建和自定义 MetaHuman 角色**：当你使用 MetaHuman Creator 编辑器或相关工具时，最终的“生成”或“装配”过程会调用此模块中定义的管线，将你的选择（发型、服装、肤色等）转化为实际的 SkeletalMesh、Material 和 Groom 资产。
-   **批量生成或自动化生成**：如果你需要在游戏或应用中根据配置动态组装 MetaHuman，可以调用此管线的 AssembleCollection 功能。
-   **扩展装配流程**：该模块设计为可扩展。如果你的项目需要为 MetaHuman 添加新的资产类型（例如，特殊的配饰），可以通过实现 `IMetaHumanCharacterPipelineExtender` 接口来扩展或覆盖默认的装配行为。

## 蓝图用法

该模块中的管线类（如 `UMetaHumanDefaultPipeline`）主要在编辑器数据构建流程中被调用，直接暴露给蓝图的节点较少。主要蓝图可调用节点是用于将装配结果应用到运行时组件上的静态函数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ApplyGroomAssemblyOutputToGroomComponent` | 将毛发装配输出应用到 `UGroomComponent` 上，设置绑定和材质覆盖。 | `UMetaHumanGroomPipeline` |
| `ApplyOutfitAssemblyOutputToClothComponent` | 将服装装配输出应用到 `UChaosClothComponent` 上。 | `UMetaHumanOutfitPipeline` |
| `ApplyOutfitAssemblyOutputToMeshComponent` | 将服装装配输出应用到 `USkeletalMeshComponent` 上。 | `UMetaHumanOutfitPipeline` |
| `ApplySkeletalMeshAssemblyOutputToSkeletalMeshComponent` | 将通用骨骼网格装配输出应用到 `USkeletalMeshComponent` 上。 | `UMetaHumanSkeletalMeshPipeline` |

### 使用示例（蓝图描述）

假设你有一个变量 `GroomAssemblyOutput` (类型为 `FMetaHumanGroomPipelineAssemblyOutput`)，它来自某个装配流程。在蓝图中，你可以这样使用它：
1.  获取场景中你的角色 actor，找到其上的 `UGroomComponent`。
2.  从组件上下文菜单拖拽出线，搜索并添加 `Apply Groom Assembly Output To Groom Component` 节点。
3.  将 `Groom Assembly Output` 变量连接到节点的 `Groom Assembly Output` 输入引脚。
4.  将 `Groom Component` 连接到节点的 `Groom Component` 输入引脚。
5.  运行时执行此节点，即可将装配好的毛发资产和材质参数应用到该组件。

## C++ 用法

该模块主要涉及管线定义和资产处理，运行时直接使用其公共 C++ API 的场景相对较少，更多是作为编辑器工具链的后端。以下示例展示了如何理解和参与其扩展机制。

### 头文件引入

```cpp
// 核心管线基类
#include "MetaHumanDefaultPipelineBase.h"
// 管线扩展接口
#include "MetaHumanDefaultPipelineBase.h" // IMetaHumanCharacterPipelineExtender 也在此文件中
```

### 基本用法：子类化默认管线

默认管线是抽象类，需要通过蓝图或 C++ 子类化来指定实际内容。

```cpp
// MyCustomPipeline.h
#pragma once
#include "MetaHumanDefaultPipeline.h"
#include "MyCustomPipeline.generated.h"

UCLASS(Blueprintable, EditInlineNew)
class UMyCustomMetaHumanPipeline : public UMetaHumanDefaultPipeline
{
    GENERATED_BODY()
public:
    // 在蓝图编辑器中配置此资产（例如，设置 FaceSkelMesh, BodySkelMesh 等）
    UPROPERTY(EditAnywhere, Category = "Character")
    TSoftObjectPtr<USkeletalMesh> MySpecialFaceMesh;
    // ... 其他资产引用
};

// .cpp 中可能需要实现 GetActorClass 等虚函数
// 参考源码: MetaHumanDefaultPipeline.h, MetaHumanDefaultPipelineLegacy.h
```

### 进阶用法：实现管线扩展器

通过实现 `IMetaHumanCharacterPipelineExtender` 接口，你可以在默认管线构建后注入自定义逻辑。

```cpp
// MyPipelineExtender.h
#pragma once
#include "MetaHumanDefaultPipelineBase.h"
#include "MyPipelineExtender.generated.h"

UCLASS()
class UMyCharacterPipelineExtender : public UObject, public IMetaHumanCharacterPipelineExtender
{
    GENERATED_BODY()
public:
    // 为特定的动画系统和质量级别覆盖蓝图类（可选）
    virtual TSubclassOf<AActor> GetOverwriteBlueprint(EMetaHumanQualityLevel QualityLevel, FName AnimationSystemName) const override
    {
        // 返回一个自定义的蓝图 Actor 类，如果适用
        return nullptr;
    }

    // 在基础管线蓝图修改后，进行额外的修改
    virtual void ModifyBlueprint(TNotNull<UBlueprint*> InBlueprint) override
    {
        // 例如，在生成的 Actor 蓝图中添加一个自定义组件
        UBlueprintEditorLibrary::AddComponent(InBlueprint, UMyCustomComponent::StaticClass(), TEXT("MyCustomComp"));
    }
};

// 在你的模块启动时注册
void FMyModule::StartupModule()
{
    IModularFeatures::Get().RegisterModularFeature(IMetaHumanCharacterPipelineExtender::FeatureName, GetMutableDefault<UMyCharacterPipelineExtender>());
}

void FMyModule::ShutdownModule()
{
    IModularFeatures::Get().UnregisterModularFeature(IMetaHumanCharacterPipelineExtender::FeatureName, GetMutableDefault<UMyCharacterPipelineExtender>());
}
```

## Demo 示例

一个最小的自定义管线子类定义。

**MySimplePipeline.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "MetaHumanDefaultPipeline.h"
#include "MySimplePipeline.generated.h"

/**
 * 一个简单的自定义 MetaHuman 管线，引用一个特定的面部网格资产。
 */
UCLASS(Blueprintable, EditInlineNew, meta=(MetaHumanCreatorOnly))
class UMySimpleMetaHumanPipeline : public UMetaHumanDefaultPipeline
{
    GENERATED_BODY()

public:
    UMySimpleMetaHumanPipeline();

    // 此管线使用的面部网格资产
    UPROPERTY(EditAnywhere, Category = "Character")
    TSoftObjectPtr<USkeletalMesh> CustomFaceMesh;

    // 可以覆盖 GetActorClass 以使用特定的 Actor 类
    virtual TSubclassOf<AActor> GetActorClass() const override;
};
```

**MySimplePipeline.cpp**
```cpp
#include "MySimplePipeline.h"

UMySimpleMetaHumanPipeline::UMySimpleMetaHumanPipeline()
{
    // 构造函数中可以进行默认设置
}

TSubclassOf<AActor> UMySimpleMetaHumanPipeline::GetActorClass() const
{
    // 返回你的自定义 Actor 类，或使用基类默认值
    // 例如: return AMyCustomMetaHumanActor::StaticClass();
    return Super::GetActorClass();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ChaosOutfitAsset` | 处理服装资产和物理模拟。 |
| `HairStrandsCore` | 处理毛发发丝系统的核心数据。 |
| `GroomBinding` | 处理毛发与骨骼网格的绑定数据。 |
| `GeometryRemoval` | 处理运行时几何体移除（例如，在衣物下隐藏身体部分）。 |
| `AnimationBlueprintLibrary` | 处理动画蓝图相关功能（用于骨骼网格管线）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `95d906ba` | [UEMHC] Checking for Asset Registry filter validity before using it | 使用资产注册表过滤器前检查其有效性 |
| 2026-05-26 | `7f10fbf1` | [MetaHuman] Titan v9.0.8 | MetaHuman 核心库更新至 v9.0.8 |
| 2026-05-26 | `efb27122` | [UEMHC] Duplicate face/body DNA when duplicating archetype skel meshes | 复制原型骨骼网格时同步复制面部/身体DNA |
| 2026-05-26 | `909bc538` | [MHC] Use safer weak pointers for captured objects in MHC preview delegates | 在MHC预览委托中使用更安全的弱指针捕获对象 |
| 2026-05-26 | `cfa3dac6` | [MetaHuman] Titan v9.0.7 | MetaHuman 核心库更新至 v9.0.7 |

### 维护评价

该插件模块**处于活跃维护中**。创建于2025年3月，作为 MetaHuman Character 的核心构建部分，最近的提交记录（2026年5月）显示仍有频繁的功能更新、bug修复和核心库版本迭代。尽管标记为 Beta 版（`IsBetaVersion=true`）且默认未启用（`EnabledByDefault=false`），表明其 API 和功能仍在稳定化过程中，但鉴于 Epic Games 对 MetaHuman 技术的持续投入，可以预期其会长期维护。**推荐在需要深度自定义 MetaHuman 构建流程的项目中使用，但需注意 Beta 状态可能带来的接口变化。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanCharacter)
- [官方文档]() (暂无)
- [测试用例]() (可能位于 Engine/Tests/MetaHuman/ 目录下)