# Groom

> Rendering and simulation of grooms

| 属性 | 值 |
|---|---|
| 中文名 | 毛发系统 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（毛发资产、LOD 模板） |
| 模块 | `HairCardGeneratorFramework` (Runtime), `HairStrandsCore` (Runtime), `HairStrandsDataflow` (Runtime), `HairStrandsDeformer` (Runtime), `HairStrandsEditor` (Runtime), `HairStrandsRuntime` (Runtime), `HairStrandsSolver` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-11-24 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/HairStrands) | |

> **注意**：此插件默认未启用（`EnabledByDefault: false`），需要在 **Edit → Plugins** 中手动启用 **Groom** 插件，并重启编辑器。

## 用途

HairStrands 是 UE5 的**基于发丝的毛发（Groom）渲染与物理模拟系统**。它解决的核心问题是：如何将影视级的毛发资产（通常由 XGen、Houdini、Maya 等 DCC 工具以 Alembic 格式导出）导入引擎，并在实时场景中高效渲染和模拟。

该插件提供了一套完整的毛发处理管线：

- **导入**：从 Alembic（.abc）文件导入发丝数据（Strand），支持百万级发丝的资产
- **渲染**：支持两种渲染模式——逐发丝（Strand-based）渲染和 LOD 卡片（Hair Cards）渲染，前者画质更高但开销大，后者适合远距离 LOD
- **模拟**：内置物理求解器，支持毛发与骨骼动画的绑定（Binding）、碰撞检测、风力等
- **LOD 策略**：自动从发丝数据生成卡片几何体，作为低精度 LOD
- **Dataflow 集成**：通过节点图对毛发数据进行程序化编辑和变换

之所以存在此插件，是因为传统引擎通常只支持贴图模拟的头发（Hair Cards），无法直接渲染真实的发丝数据。Groom 插件填补了从影视资产到实时渲染之间的桥梁。

## 子模块总览

本插件包含 7 个 Runtime 模块，各司其职：

| 模块 | 职责 |
|---|---|
| `HairStrandsCore` | 核心数据结构：Groom 资产（`UGroomAsset`）、绑定资产（`UGroomBindingAsset`）、发丝描述数据 |
| `HairStrandsRuntime` | 运行时渲染：将发丝数据提交给 GPU 渲染管线，管理 LOD 切换 |
| `HairStrandsSolver` | 物理模拟求解器：发丝碰撞、风力、自碰撞等 |
| `HairStrandsDeformer` | 网格变形器：将 Groom 变形逻辑集成到 Mesh Deformer 管线 |
| `HairStrandsEditor` | 编辑器工具：Groom 资产的编辑器预览、属性面板 |
| `HairStrandsDataflow` | Dataflow 节点集成：通过节点图程序化处理毛发数据 |
| `HairCardGeneratorFramework` | LOD 卡片生成：从发丝数据自动生成 Hair Cards 几何体 |

## 使用场景

- 你在制作写实角色，需要影视级毛发效果 → 启用 Groom 插件，导入 Alembic 毛发资产
- 你需要角色毛发跟随骨骼动画自然飘动 → 使用 Groom Binding + 物理模拟
- 你的项目需要在移动端或低端平台使用毛发 → 用 Hair Card Generator 自动生成 LOD 卡片
- 你需要在 Dataflow（PCG 节点图）中程序化编辑毛发造型 → 使用 HairStrandsDataflow 模块
- 你需要自定义毛发的网格变形（如 Morph Target 驱动）→ 使用 HairStrandsDeformer 集成到 Mesh Deformer 管线

## 蓝图用法

### 核心组件与资产

| 类 | 说明 |
|---|---|
| `UGroomAsset` | 毛发资产，从 Alembic 文件导入，存储发丝数据 |
| `UGroomBindingAsset` | 绑定资产，定义 Groom 如何附着到 SkeletalMesh |
| `UGroomComponent` | 场景组件，将 GroomAsset 实例化到场景中并驱动渲染 |

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Groom` | 设置组件使用的毛发资产 | `UGroomComponent` |
| `Set Binding` | 设置 Groom 与骨骼网格的绑定关系 | `UGroomComponent` |
| `Set Physics Asset` | 为毛发模拟指定碰撞体 | `UGroomComponent` |
| `Set Niagara Components` | 将 Niagara 粒子系统与毛发关联（用于驱动效果） | `UGroomComponent` |
| `Set Simulation Settings` | 设置物理模拟参数（硬度、阻尼、碰撞等） | `UGroomComponent` |

### 使用示例

1. **基础毛发渲染**：在角色 SkeletalMeshComponent 上添加一个 `GroomComponent` → 设置其 `Groom` 属性为导入的 `UGroomAsset` → 设置 `Binding` 为对应的 `UGroomBindingAsset` → 发丝会附着在角色头部并跟随动画。

2. **物理模拟配置**：在 GroomComponent 上启用物理模拟 → 设置 `HairSimulationSettings`（包括碰撞半径、阻尼系数、风力方向等）→ 毛发会在运行时产生自然的物理飘动效果。

3. **LOD 切换**：在 `UGroomAsset` 中配置 LOD 策略 → 近距离使用 Strand 渲染（高精度），远距离自动切换到 Hair Cards 渲染（低开销）。

## C++ 用法

### 头文件引入

```cpp
#include "GroomAsset.h"
#include "GroomBindingAsset.h"
#include "GroomComponent.h"
```

### 基本用法：程序化创建 Groom Component

```cpp
// 假设已有 UGroomAsset* GroomAsset 和 USkeletalMeshComponent* SkelMeshComp
// 加载毛发资产
UGroomAsset* GroomAsset = LoadObject<UGroomAsset>(nullptr, TEXT("/Game/Hair/MyGroom.MyGroom"));

// 创建 Groom Component 并附加到角色
UGroomComponent* GroomComp = NewObject<UGroomComponent>(SkelMeshComp->GetOwner());
GroomComp->SetGroomAsset(GroomAsset);
GroomComp->SetMobility(EComponentMobility::Movable);
GroomComp->AttachToComponent(SkelMeshComp, FAttachmentTransformRules::SnapToTargetNotIncludingScale);
GroomComp->RegisterComponent();
```

### 进阶用法：配置模拟参数

```cpp
#include "HairStrandsCore.h"
#include "GroomComponent.h"

UGroomComponent* GroomComp = /* 获取已有的 GroomComponent */;

// 启用物理模拟
FHairSimulationSettings SimSettings;
SimSettings.bEnableSimulation = true;
SimSettings.LinearDamping = 0.1f;
SimSettings.AngularDamping = 0.1f;
SimSettings.CollisionRadius = 1.0f;
SimSettings.bSolveBending = true;

// 通过 Component 的 SimulationSettings 属性设置
GroomComp->SetEnableSimulation(true);
```

### 进阶用法：Dataflow 编程（HairStrandsDataflow）

Dataflow 模块提供了节点图接口，可以在 C++ 中创建自定义处理节点：

```cpp
#include "HairStrandsDataflow.h"

// Dataflow 节点通过 UE 的 Dataflow 框架注册
// 通常通过编辑器中的 Dataflow 资产创建节点图
// C++ 端可自定义节点继承自 FDataflowNode
```

## Demo 示例

以下示例展示如何在 C++ 中加载 Groom 资产并创建组件：

```cpp
// MyCharacter.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "GroomComponent.h"
#include "MyCharacter.generated.h"

UCLASS()
class AMyCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    AMyCharacter();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Hair")
    UGroomComponent* GroomComponent;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Hair")
    UGroomAsset* GroomAsset;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Hair")
    UGroomBindingAsset* GroomBinding;

    UFUNCTION(BlueprintCallable, Category = "Hair")
    void SetupGroom(UGroomAsset* InAsset, UGroomBindingAsset* InBinding);
};
```

```cpp
// MyCharacter.cpp
#include "MyCharacter.h"

AMyCharacter::AMyCharacter()
{
    // 创建 Groom 组件并附加到 Mesh
    GroomComponent = CreateDefaultSubobject<UGroomComponent>(TEXT("Groom"));
    GroomComponent->SetupAttachment(GetMesh());
}

void AMyCharacter::SetupGroom(UGroomAsset* InAsset, UGroomBindingAsset* InBinding)
{
    if (InAsset)
    {
        GroomComponent->SetGroomAsset(InAsset);
    }
    if (InBinding)
    {
        GroomComponent->SetBindingAsset(InBinding);
    }
    // 强制刷新组件
    GroomComponent->RecreateRenderState();
}
```

## 模块依赖

从各模块 Build.cs 的依赖关系推断，以下是此插件独特的依赖模块：

| 模块 | 用途 |
|---|---|
| `Niagara` | 毛发粒子效果系统集成 |
| `GeometryFramework` | 几何体处理框架 |
| `MeshDescription` | 网格描述数据，用于卡片生成 |
| `RenderCore` | 底层渲染管线 |
| `RHI` | 硬件渲染接口 |
| `PhysicsCore` | 物理引擎核心，用于毛发模拟 |
| `OptimusCore` | 计算着色器调度（Deformer Graph） |
| `DataflowCore` | Dataflow 节点图框架 |
| `DataflowEngine` | Dataflow 运行时引擎 |
| `GeometryCache` | 几何缓存（Alembic 数据管理） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `aa770ac7` | Remove crash in mobile renderer when using groom binding. | 修复移动端使用 Groom Binding 时的崩溃问题 |
| 2026-05-26 | `3da4e98e` | Fix crash when selecting the addSolverDeformer dataflow node | 修复选择 addSolverDeformer Dataflow 节点时崩溃 |
| 2026-05-26 | `d2f5bcd4` | Fix crash when recompiling BP while playing groom in dataflow editor + fix bad number of vertices ca | 修复 Dataflow 编辑器中重编译蓝图时崩溃及顶点数错误 |
| 2026-05-22 | `9ce84766` | Remove the CreateGroomDataflowAsset from the context menu | 从右键菜单移除 CreateGroomDataflowAsset 入口 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口通知机制，减少重复代码 |

### 维护评价

**活跃维护中** ✅

- **创建时间**：2020 年 11 月，随 UE5 早期开发引入，已有约 6 年历史
- **更新频率**：近期（2026 年 5 月）仍有多次实质性提交，主要集中在稳定性修复（崩溃修复）和 Dataflow 集成优化
- **维护团队**：Epic Games 官方维护，属于 UE5 核心毛发渲染管线
- **状态评估**：该插件是 MetaHuman 和写实角色工作流的关键组成部分，不太可能被废弃。但由于功能复杂度高，仍存在边缘场景的稳定性问题（近期多次崩溃修复可佐证）
- **建议**：✅ **推荐在写实角色项目中使用**。但请注意该插件默认未启用，需要手动开启。对于移动端项目，需额外关注 Hair Cards LOD 的性能表现。近期修复表明在 Dataflow 编辑器中使用时可能遇到稳定性问题，建议使用最新引擎版本。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/HairStrands)
- [Hair Strands 官方文档](https://docs.unrealengine.com/5.8/en-US/hair-strands-and-groom-features-in-unreal-engine/)
- 测试用例：引擎内置测试（位于 `Engine/Tests/` 目录下）