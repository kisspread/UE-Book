# Groom

> Rendering and simulation of grooms

| 属性 | 值 |
|---|---|
| 中文名 | 毛发系统 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产，材质，示例） |
| 模块 | `HairCardGeneratorFramework` (Runtime), `HairStrandsCore` (Runtime), `HairStrandsDataflow` (Runtime), `HairStrandsDeformer` (Runtime), `HairStrandsEditor` (Runtime), `HairStrandsRuntime` (Runtime), `HairStrandsSolver` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-11-24 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/HairStrands) | |

## 用途

HairStrands（Groom）插件为 Unreal Engine 5 提供了一套完整的、基于发束（Strands）的毛发资产创建、渲染与模拟系统。它取代并扩展了旧的毛发解决方案，专注于实现影视级别的高精度、高动态毛发效果，同时优化了实时渲染性能。该插件解决了在 UE 中处理复杂、大规模毛发数据（如角色头发、胡须、动物毛皮）的核心工作流问题，涵盖了从资产导入、数据优化（HairCards）、渲染到物理模拟的全链路。

## 使用场景

- **高端角色制作**：为电影、CG 动画或 AAA 级游戏角色创建逼真的头发、胡须和眉毛。
- **实时毛发渲染**：在游戏或实时应用中实现基于发束的物理正确渲染（PBR）和次表面散射效果。
- **毛发动力学模拟**：为毛发添加基于物理的动态效果，如风吹、角色运动时的飘动。
- **艺术家工作流集成**：支持从 DCC 工具（如 Maya， Blender， XGen）导出的 Groom 资产格式。
- **性能优化**：使用 HairCards 技术将高密度发束转换为优化后的多边形，用于中远景或性能受限的平台。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `LoadGroom` | 从路径异步加载一个 Groom 资产。 | `UHairStrandsBPLibrary` |
| `GetGroomAssets` | 获取当前已加载的所有 Groom 资产引用。 | `UHairStrandsBPLibrary` |
| `SetHairStrandsSimulation` | 为 Groom 组件启用或禁用物理模拟。 | `UHairStrandsComponent` |
| `SetGroomAsset` | 动态更改 Groom 组件的资产。 | `UHairStrandsComponent` |
| `SetGroomBindingAsset` | 设置用于绑定 Groom 到骨骼网格体的绑定资产。 | `UHairStrandsComponent` |

### 使用示例（蓝图描述）

1.  **加载与显示**：在角色蓝图中，使用 `LoadGroom` 异步加载资产，加载成功后通过 `SetGroomAsset` 赋值给 `UHairStrandsComponent`。确保组件已添加到角色的对应骨骼插槽（如 `head`）。
2.  **动态控制**：通过事件图表，在 `BeginPlay` 或特定交互时，调用 `SetHairStrandsSimulation` 节点，在“风吹”或“静止”状态间切换。
3.  **资产替换**：实现角色换发型功能，通过 `SetGroomAsset` 切换不同的 Groom 资产。

## C++ 用法

### 头文件引入

```cpp
#include “HairStrandsCore.h“
#include “GroomAsset.h“
#include “HairStrandsComponent.h“
```

### 基本用法

加载和检查 Groom 资产。
```cpp
// 加载 Groom 资产 (UObject::LoadObject 或异步加载系统)
UGroomAsset* GroomAsset = LoadObject<UGroomAsset>(nullptr, TEXT(“/Game/Characters/Hero/Hero_Hair“));

if (GroomAsset)
{
    // 检查资产有效性，例如是否包含发束数据
    if (GroomAsset->GetHairGroups().Num() > 0)
    {
        UE_LOG(LogHairStrands, Log, TEXT(“Successfully loaded Groom asset: %s“), *GroomAsset->GetName());
    }
}
```
*示例基于 `HairStrandsCore` 模块常见用法。*

### 进阶用法

在 C++ 中程序化控制毛发模拟状态。
```cpp
// 假设在 Actor 或 Component 类中
#include “HairStrandsComponent.h“

UHairStrandsComponent* HairComp = FindComponentByClass<UHairStrandsComponent>();
if (HairComp && HairComp->GetGroomAsset())
{
    // 启用模拟
    HairComp->SetHairSimulation(true);

    // 设置模拟参数（如风速，具体参数需查看 FHairSimulationSettings 结构）
    HairComp->SetHairSimulationWindSpeed(FVector(100.f, 0.f, 0.f));
}
```
*示例基于 `HairStrandsRuntime` 模块与组件交互逻辑。*

## Demo 示例

以下是一个最小示例，在 Actor 中创建一个 Groom 组件并为其加载资产。
```cpp
// MyHairActor.h
#pragma once
#include “GameFramework/Actor.h“
#include “MyHairActor.generated.h“
class UHairStrandsComponent;
class UGroomAsset;

UCLASS()
class AMyHairActor : public AActor
{
    GENERATED_BODY()
public:
    AMyHairActor();
    virtual void BeginPlay() override;

private:
    UPROPERTY(VisibleAnywhere)
    UHairStrandsComponent* HairComponent;

    UPROPERTY(EditAnywhere, Category=“Groom“)
    TSoftObjectPtr<UGroomAsset> GroomAssetToLoad;
};

// MyHairActor.cpp
#include “MyHairActor.h“
#include “HairStrandsComponent.h“
#include “GroomAsset.h“
#include “Engine/StreamableManager.h“

AMyHairActor::AMyHairActor()
{
    HairComponent = CreateDefaultSubobject<UHairStrandsComponent>(TEXT(“HairComponent“));
    RootComponent = HairComponent;
}

void AMyHairActor::BeginPlay()
{
    Super::BeginPlay();

    if (!GroomAssetToLoad.IsNull())
    {
        // 异步加载资产
        FStreamableManager& StreamableManager = UAssetManager::GetStreamableManager();
        StreamableManager.RequestAsyncLoad(GroomAssetToLoad.ToSoftObjectPath(),
            FStreamableDelegate::CreateUObject(this, &AMyHairActor::OnGroomLoaded));
    }
}

void AMyHairActor::OnGroomLoaded()
{
    UGroomAsset* LoadedAsset = GroomAssetToLoad.Get();
    if (LoadedAsset)
    {
        HairComponent->SetGroomAsset(LoadedAsset);
    }
}
```

## 模块依赖

使用此插件进行开发时，你的模块需要依赖以下**独特**的模块：

| 模块 | 用途 |
|---|---|
| `HairStrandsCore` | 提供核心数据类型（`UGroomAsset` 等）、常量和基础接口。 |
| `HairStrandsRuntime` | 包含运行时组件（`UHairStrandsComponent`）和渲染逻辑。 |
| `HairStrandsDeformer` | 提供用于控制毛发变形（如骨骼驱动）的系统。 |
| `GeometryCache` | （可选）如果使用基于几何缓存（Alembic）的毛发数据流，需要依赖此模块。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `aa770ac7` | Remove crash in mobile renderer when using groom binding. | 修复移动端渲染器中使用毛发绑定时的崩溃问题。 |
| 2026-05-26 | `3da4e98e` | Fix crash when selecting the addSolverDeformer dataflow node | 修复在数据流编辑器中选择添加求解器变形器节点时的崩溃。 |
| 2026-05-26 | `d2f5bcd4` | Fix crash when recompiling BP while playing groom in dataflow editor + fix bad number of vertices ca | 修复在数据流编辑器播放毛发时重编译蓝图导致的崩溃，并修正顶点数计算错误。 |
| 2026-05-22 | `9ce84766` | Remove the CreateGroomDataflowAsset from the context menu | 从右键菜单中移除“创建毛发数据流资产”选项。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 优化视口代码，通过通知客户端关联/解除关联来减少重复代码。 |

### 维护评价

HairStrands（Groom）插件处于**积极维护**状态。尽管其创建已有约6年时间，但最近的提交（截至2026年5月）显示开发团队仍在**持续修复关键崩溃、优化工作流和改善稳定性**。这些更新主要集中在 Dataflow 编辑器和移动端渲染等特定场景，表明该插件作为 UE5 的核心毛发解决方案，仍在不断进行完善和问题修复。目前没有发现被废弃的迹象，适合在需要高质量毛发的项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/HairStrands)
- [官方文档]()（.uplugin 未提供）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/Runtime/HairStrands/)