# Groom

> Rendering and simulation of grooms（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 毛发渲染 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质模板、Groom资产） |
| 模块 | `HairStrandsCore` (Runtime), `HairCardGeneratorFramework` (Runtime), `HairStrandsDataflow` (Runtime), `HairStrandsDeformer` (Runtime), `HairStrandsEditor` (Runtime), `HairStrandsRuntime` (Runtime), `HairStrandsSolver` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-11-24 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/HairStrands) | |

## 用途

`HairStrands`（或称为Groom系统）插件是 Unreal Engine 5 中用于处理高保真毛发（头发、皮毛、胡子等）的核心系统。它解决了传统多边形网格无法高效表现数万根独立发丝的问题。该插件的核心功能是提供一套完整的流程，用于导入、处理、渲染和模拟基于发丝（Strand）的毛发资产。

其主要工作包括：
- **数据管理**：管理 `UGroomAsset` 等核心资产，这些资产包含数百万根发丝的拓扑、宽度、颜色等信息。
- **渲染优化**：提供多种渲染路径（Strands, Cards, Meshes）和LOD策略，以在保证视觉质量的同时优化运行时性能。
- **物理模拟**：集成或提供解算器（Solver）来模拟毛发与角色骨骼、碰撞体以及风的交互，实现真实的动态效果。
- **开发扩展**：通过 `IHairCardGenerator` 等接口，允许第三方工具或插件集成，以生成用于性能优化的毛发卡片（Cards）或网格（Meshes）。

该插件的存在使得在实时环境中渲染和模拟电影级别的毛发成为可能。

## 使用场景

- 你正在开发一个注重角色外观的3A级游戏，角色拥有复杂且需要物理交互的发型。
- 你正在制作一个虚拟人或数字人项目，需要实现毛发根根分明的超高写实度。
- 你需要为游戏中的动物角色（如狮子、马匹）创建逼真的毛发，并希望其随动作自然摆动。
- 你有一个需要导入从第三方DCC软件（如Maya, XGen, Houdini）中制作的毛发数据的工作流。
- 你需要通过生成毛发卡片（Hair Cards）或网格来优化大量毛发角色在开放世界中的性能。

## 蓝图用法

基于提供的 `IHairCardGenerator` 接口分析，该插件的核心蓝图交互可能更偏向于C++层面和资产数据。然而，引擎通常通过资产编辑器和组件（如 `UGroomComponent`）暴露蓝图接口。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| 加载 Groom 资产 | 在蓝图中异步或同步加载一个 Groom 资源。 | `UGroomAsset` (资产引用) |
| 设置 Groom 组件属性 | 配置 `UGroomComponent` 的模拟、渲染等属性。 | `UGroomComponent` |

### 使用示例（蓝图描述）

1.  **在角色蓝图中添加 Groom 组件**：
    - 在你的角色蓝图中，从组件面板添加 `GroomComponent`。
    - 在该组件的细节面板中，指定一个 `GroomAsset` 作为其数据源。
2.  **控制物理模拟**：
    - 通过蓝图调用 `UGroomComponent` 上的函数（如 `SetSimulatePhysics`）来开关或控制毛发的物理模拟状态。
3.  **动态绑定到骨骼网格体**：
    - 在角色蓝图中，确保 `GroomComponent` 附加到正确的骨骼网格体组件上，并配置好绑定（Binding），以使毛发能够跟随角色的骨骼动画。

## C++ 用法

核心使用模式围绕 Groom 资产的创建、加载和组件的管理展开。

### 头文件引入

```cpp
// 访问核心资产和组件
#include "GroomAsset.h"
#include "GroomComponent.h"

// 使用卡片生成器接口（对于工具开发者）
#include "IHairCardGenerator.h"
```

### 基本用法

**创建和配置一个简单的 Groom 组件**（来源：引擎典型用法模式）：

```cpp
// 在Actor的头文件中
#include "GroomComponent.h"

UCLASS()
class AMyCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    AMyCharacter();

protected:
    // Groom组件
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<UGroomComponent> GroomComponent;

    // 加载的Groom资产
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Groom")
    TObjectPtr<UGroomAsset> GroomAsset;
};

// 在Actor的构造函数中
AMyCharacter::AMyCharacter()
{
    // 创建Groom组件
    GroomComponent = CreateDefaultSubobject<UGroomComponent>(TEXT("HairGroom"));
    GroomComponent->SetupAttachment(GetMesh()); // 附加到骨骼网格体

    // 通过默认路径加载资产（或在编辑器中设置）
    if (GroomAsset)
    {
        GroomComponent->SetGroomAsset(GroomAsset);
    }
}
```

### 进阶用法

**实现一个自定义的毛发卡片生成器**（来源：基于 `IHairCardGenerator` 接口）：

```cpp
// MyHairCardGenerator.h
#pragma once
#include "IHairCardGenerator.h"

class FMyHairCardGenerator : public IHairCardGenerator
{
public:
    FMyHairCardGenerator();
    virtual ~FMyHairCardGenerator();

    // IHairCardGenerator 接口实现
    virtual bool GenerateHairCardsForLOD(UGroomAsset* Groom, FHairGroupsCardsSourceDescription& CardsDesc) override;
    virtual bool IsCompatibleSettings(UHairCardGenerationSettings* OldSettings) override;
};
```

```cpp
// MyHairCardGenerator.cpp
#include "MyHairCardGenerator.h"
#include "GroomAsset.h"

FMyHairCardGenerator::FMyHairCardGenerator()
{
    // 注册到模块化特性系统
    HairCardGenerator_Utils::RegisterModularHairCardGenerator(this);
}

FMyHairCardGenerator::~FMyHairCardGenerator()
{
    // 反注册
    HairCardGenerator_Utils::UnregisterModularHairCardGenerator(this);
}

bool FMyHairCardGenerator::GenerateHairCardsForLOD(UGroomAsset* Groom, FHairGroupsCardsSourceDescription& CardsDesc)
{
    if (!Groom) return false;

    // 自定义的卡片生成逻辑，例如使用你的外部工具或算法
    // ...
    // 生成结果应填充到 CardsDesc 中
    UE_LOG(LogTemp, Log, TEXT("Custom card generation for LOD %d initiated."), CardsDesc.LODIndex);
    return true;
}

bool FMyHairCardGenerator::IsCompatibleSettings(UHairCardGenerationSettings* OldSettings)
{
    // 检查旧设置是否与你的生成器兼容
    return true;
}
```

## Demo 示例

以下是一个在场景中生成并显示 Groom 的最小示例。

**MyGroomActor.h**
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "MyGroomActor.generated.h"

class UGroomComponent;
class UGroomAsset;

UCLASS()
class AMyGroomActor : public AActor
{
    GENERATED_BODY()
    
public:	
    AMyGroomActor();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<USceneComponent> Root;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Groom")
    TObjectPtr<UGroomComponent> GroomComp;

    UPROPERTY(EditAnywhere, Category="Groom")
    TObjectPtr<UGroomAsset> GroomAssetToLoad;
};
```

**MyGroomActor.cpp**
```cpp
#include "MyGroomActor.h"
#include "GroomComponent.h"
#include "GroomAsset.h"

AMyGroomActor::AMyGroomActor()
{
    Root = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
    RootComponent = Root;

    GroomComp = CreateDefaultSubobject<UGroomComponent>(TEXT("Groom"));
    GroomComp->SetupAttachment(Root);
}

void AMyGroomActor::BeginPlay()
{
    Super::BeginPlay();

    // 在运行时检查资产是否有效
    if (GroomAssetToLoad)
    {
        GroomComp->SetGroomAsset(GroomAssetToLoad);
        UE_LOG(LogTemp, Log, TEXT("Groom asset assigned successfully."));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("No Groom asset specified!"));
    }
}
```

## 模块依赖

从插件结构和模块名称推断，使用者的模块需要依赖以下模块以访问其核心功能：

| 模块 | 用途 |
|---|---|
| `HairStrandsCore` | 访问 Groom 资产类型（`UGroomAsset`）和核心数据结构。 |
| `HairStrandsRuntime` | 访问运行时渲染和模拟组件（如 `UGroomComponent`）。 |
| `HairCardGeneratorFramework` | （可选）用于实现或使用自定义的毛发卡片生成器。 |

**注意**：具体依赖关系需以各模块的 `Build.cs` 文件为准。以上是基于功能划分的合理推断。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `aa770ac7` | Remove crash in mobile renderer when using groom binding. | 修复了在移动端渲染器使用Groom绑定时的崩溃问题。 |
| 2026-05-26 | `3da4e98e` | Fix crash when selecting the addSolverDeformer dataflow node | 修复了在数据流编辑器中选择 addSolverDeformer 节点时的崩溃。 |
| 2026-05-26 | `d2f5bcd4` | Fix crash when recompiling BP while playing groom in dataflow editor + fix bad number of vertices ca | 修复了在数据流编辑器中播放Groom时重编译蓝图导致的崩溃，并修复了顶点数错误的问题。 |
| 2026-05-22 | `9ce84766` | Remove the CreateGroomDataflowAsset from the context menu | 从上下文菜单中移除了 “CreateGroomDataflowAsset” 选项。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口优化：通过通知客户端关联或解除关联来减少冗余代码。 |

### 维护评价

`HairStrands`（Groom）插件是 Unreal Engine 处理高品质毛发的核心且复杂的系统。根据近期的提交历史，该插件仍在 **积极维护** 中。

- **活跃维护**：最近的提交记录（2026年5月）集中于修复移动端渲染器崩溃、数据流编辑器中的交互崩溃以及优化编辑器代码，表明 Epic 团队持续关注该插件的稳定性和用户体验。
- **核心功能**：作为 UE5 面向次世代和影视级应用的重要功能，其维护优先级很高。
- **使用建议**：对于任何需要高质量毛发渲染和模拟的项目，该插件是**推荐使用**的。尽管初始学习曲线可能较陡，且需要手动启用 (`EnabledByDefault: false`)，但其提供的完整功能和官方支持使其成为可靠的选择。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/HairStrands)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/groom-quick-start-guide-in-unreal-engine/)（通用指南）
- 测试用例：通常位于 `Engine/Plugins/Runtime/HairStrands/Tests` 或引擎测试目录下，具体路径需在源码中搜索。