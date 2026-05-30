# Groom

> Rendering and simulation of grooms

| 属性 | 值 |
|---|---|
| 中文名 | 毛发系统 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质模板、Niagara 数据接口、Dataflow 节点） |
| 模块 | `HairStrandsCore` (Runtime), `HairStrandsRuntime` (Runtime), `HairStrandsDeformer` (Runtime), `HairStrandsSolver` (Runtime), `HairStrandsDataflow` (Runtime), `HairStrandsEditor` (Runtime), `HairCardGeneratorFramework` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-11-24 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/HairStrands) | |

## 用途

Groom 插件是 UE5 中完整的毛发（Hair/Groom）渲染与模拟框架。它解决的核心问题是：**如何将从外部 DCC 工具（如 Maya、Houdini、Blender 等）导入的高精度毛发数据（Groom）在实时引擎中高效地渲染和物理模拟**。

该插件包含以下关键能力：

- **毛发资产（GroomAsset）管理**：存储发丝几何数据（Strands）、发片卡（Cards）、网格体（Meshes）三种几何表示，并支持在运行时按 LOD 自动切换
- **GPU 插值与变形**：通过 Guide → Strand 的权重插值，将少量引导发丝（Guides）的运动传递到数万根渲染发丝（Strands）
- **物理模拟**：基于 Niagara 的 XPBD（扩展位置基动力学）求解器，支持弯曲约束、拉伸约束、碰撞约束、空气阻力等
- **骨骼网格体绑定（GroomBinding）**：通过 RBF（径向基函数）插值将毛发绑定到骨骼网格体表面，使其随角色皮肤变形
- **GroomCache 动画缓存**：支持导出/导入逐帧毛发动画数据，在 Sequencer 中播放
- **Dataflow 集成**：支持通过 Dataflow 图形化节点编辑毛发数据流
- **光线追踪支持**：可选的光线追踪几何体用于阴影和反射

该插件默认未启用（`EnabledByDefault: false`），需要在项目设置中手动开启。

## 使用场景

- 你在做一个写实风格的角色扮演游戏，角色有高精度毛发 → 用 Groom 插件
- 你需要从 Maya/Houdini 导入 Alembic 格式的毛发数据并实时渲染 → 用 Groom 插件
- 你需要毛发随角色骨骼动画自然飘动和碰撞 → 用 Groom 的物理模拟系统
- 你需要在远处用发片卡（Cards）优化毛发渲染性能，近处用发丝 → 用 Groom 的 LOD 系统
- 你需要在 Sequencer 中播放毛发动画 → 用 GroomCache + Sequencer 集成
- 你需要 Niagara 粒子系统与毛发交互（如风吹效果） → 用 Niagara 数据接口

## 模块概览

| 模块 | 类型 | 职责 |
|---|---|---|
| **HairStrandsCore** | Runtime | 核心数据结构、资产类型、资源管理、渲染管线集成 |
| **HairStrandsRuntime** | Runtime | 运行时渲染逻辑、场景代理、插值计算 |
| **HairStrandsDeformer** | Runtime | 网格变形器集成，用于基于变形器的毛发变形 |
| **HairStrandsSolver** | Runtime | Niagara 物理求解器集成（XPBD） |
| **HairStrandsDataflow** | Runtime | Dataflow 节点系统集成 |
| **HairStrandsEditor** | Runtime | 编辑器功能（注意：模块类型为 Runtime） |
| **HairCardGeneratorFramework** | Runtime | 发片卡（Cards）生成框架 |

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateNewGroomBindingAsset` | 创建毛发绑定资产（自动命名） | `UGroomBlueprintLibrary` |
| `CreateNewGroomBindingAssetWithPath` | 创建毛发绑定资产（指定路径） | `UGroomBlueprintLibrary` |
| `CreateNewGeometryCacheGroomBindingAsset` | 创建绑定到 GeometryCache 的绑定资产 | `UGroomBlueprintLibrary` |
| `IsHairStrandsSupportedInWorld` | 检查当前世界是否支持毛发渲染 | `UGroomBlueprintLibrary` |
| `SetGroomAsset` | 设置毛发资产 | `UGroomComponent` |
| `SetBindingAsset` | 设置绑定资产 | `UGroomComponent` |
| `SetPhysicsAsset` | 设置用于碰撞的物理资产 | `UGroomComponent` |
| `SetEnableSimulation` | 启用/禁用物理模拟 | `UGroomComponent` |
| `ResetSimulation` | 重置物理模拟状态 | `UGroomComponent` |
| `AddCollisionComponent` | 添加碰撞骨骼网格体组件 | `UGroomComponent` |
| `ResetCollisionComponents` | 重置碰撞组件列表 | `UGroomComponent` |
| `GetNiagaraComponent` | 获取指定组的 Niagara 组件 | `UGroomComponent` |
| `SetGroomCache` | 设置 GroomCache 动画资产 | `UGroomComponent` |
| `SetHairLengthScale` | 设置毛发长度缩放 | `UGroomComponent` |
| `SetHairLengthScaleEnable` | 启用/禁用长度缩放 | `UGroomComponent` |
| `SetMeshDeformer` | 设置网格变形器 | `UGroomComponent` |
| `Build` | 异步构建绑定资产 | `UGroomBindingAsset` |

### 使用示例

**创建毛发绑定并应用到角色：**

1. 在场景中放置角色 SkeletalMesh
2. 添加 `UGroomComponent` 到角色
3. 设置 `GroomAsset` 属性指向导入的毛发资产
4. 调用 `CreateNewGroomBindingAsset`（传入 GroomAsset 和 SkeletalMesh）生成绑定资产
5. 将返回的 `UGroomBindingAsset` 设置到组件的 `BindingAsset` 属性
6. 设置 `PhysicsAsset` 属性用于毛发碰撞

**控制毛发模拟：**

1. 获取 `UGroomComponent` 引用
2. 调用 `SetEnableSimulation(true)` 开启模拟
3. 调用 `AddCollisionComponent` 添加需要与毛发碰撞的骨骼网格体
4. 通过 `SimulationSettings` 属性调整重力、空气阻力、碰撞半径等参数

**播放 GroomCache 动画：**

1. 在 Sequencer 中添加 `UGroomComponent` 的轨道
2. 设置 `GroomCache` 属性指向动画缓存资产
3. Sequencer 会自动驱动动画播放

## C++ 用法

### 头文件引入

```cpp
#include "GroomAsset.h"
#include "GroomBindingAsset.h"
#include "GroomComponent.h"
#include "GroomBlueprintLibrary.h"
#include "HairStrandsCore.h"
```

### 基本用法

**创建 GroomBinding 资产（编辑器脚本）：**

```cpp
#include "GroomBlueprintLibrary.h"
#include "GroomAsset.h"
#include "GroomBindingAsset.h"

// 创建一个绑定到骨骼网格体的毛发绑定资产
UGroomAsset* GroomAsset = LoadObject<UGroomAsset>(nullptr, TEXT("/Game/Hair/MyGroom"));
USkeletalMesh* SkelMesh = LoadObject<USkeletalMesh>(nullptr, TEXT("/Game/Characters/Body"));

UGroomBindingAsset* Binding = UGroomBlueprintLibrary::CreateNewGroomBindingAsset(
    GroomAsset,
    SkelMesh,
    100,    // NumInterpolationPoints
    nullptr, // SourceSkeletalMeshForTransfer
    0       // MatchingSection
);
```

**通过 C++ 控制 GroomComponent：**

```cpp
// 在角色类中
UPROPERTY(VisibleAnywhere)
UGroomComponent* GroomComp;

// BeginPlay 中初始化
void AMyCharacter::BeginPlay()
{
    Super::BeginPlay();
    
    if (GroomComp)
    {
        // 设置毛发资产
        GroomComp->SetGroomAsset(MyGroomAsset);
        // 设置绑定资产
        GroomComp->SetBindingAsset(MyBindingAsset);
        // 启用模拟
        GroomComp->SetEnableSimulation(true);
        // 设置物理资产用于碰撞
        GroomComp->SetPhysicsAsset(MyPhysicsAsset);
    }
}
```

### 进阶用法

**通过 Niagara 系统与毛发交互：**

Niagara 数据接口 `UNiagaraDataInterfaceHairStrands` 允许在 Niagara 粒子系统中采样和操控毛发数据。它提供了：

- `GetNumStrands` - 获取发丝数量
- `GetPointPosition` - 获取发丝节点位置
- `ComputeNodePosition` - 计算节点世界空间位置
- `AdvectNodePosition` - 施加外力并平移节点
- `SolveBendRodMaterial` / `SolveStretchRodMaterial` - 求解材质约束
- `SolveHardCollisionConstraint` / `SolveSoftCollisionConstraint` - 碰撞约束求解

这些函数在 Niagara GPU 模拟中使用，用于实现风吹、碰撞等高级毛发交互效果。

**通过 Niagara Velocity Grid 实现流体交互：**

`UNiagaraDataInterfaceVelocityGrid` 和 `UNiagaraDataInterfacePressureGrid` 提供了基于网格的速度场和压力场数据接口，可用于实现毛发与流体（如水、风场）的交互。

**异步构建 GroomBinding：**

```cpp
UGroomBindingAsset* BindingAsset = ...;

// 异步构建，完成后回调
FOnGroomBindingAssetBuildCompleteNative CompletionDelegate;
CompletionDelegate.BindLambda([](UGroomBindingAsset* Asset, EGroomBindingAssetBuildResult Result)
{
    if (Result == EGroomBindingAssetBuildResult::Succeeded)
    {
        // 构建成功，可以使用绑定资产
    }
});

BindingAsset->Build(CompletionDelegate);
```

## Demo 示例

### 最小 Groom 角色示例

```cpp
// MyGroomCharacter.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "MyGroomCharacter.generated.h"

class UGroomComponent;
class UGroomAsset;
class UGroomBindingAsset;
class UPhysicsAsset;

UCLASS()
class AMyGroomCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    AMyGroomCharacter();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    UGroomComponent* GroomComponent;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Groom")
    TObjectPtr<UGroomAsset> GroomAsset;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Groom")
    TObjectPtr<UGroomBindingAsset> BindingAsset;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Groom")
    TObjectPtr<UPhysicsAsset> PhysicsAsset;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Groom")
    bool bEnableSimulation = true;

public:
    UFUNCTION(BlueprintCallable, Category = "Groom")
    void ToggleSimulation();
};
```

```cpp
// MyGroomCharacter.cpp
#include "MyGroomCharacter.h"
#include "GroomComponent.h"
#include "GroomAsset.h"
#include "GroomBindingAsset.h"

AMyGroomCharacter::AMyGroomCharacter()
{
    GroomComponent = CreateDefaultSubobject<UGroomComponent>(TEXT("Groom"));
    GroomComponent->SetupAttachment(GetMesh());
}

void AMyGroomCharacter::BeginPlay()
{
    Super::BeginPlay();

    if (GroomComponent)
    {
        if (GroomAsset)
        {
            GroomComponent->SetGroomAsset(GroomAsset);
        }
        if (BindingAsset)
        {
            GroomComponent->SetBindingAsset(BindingAsset);
        }
        if (PhysicsAsset)
        {
            GroomComponent->SetPhysicsAsset(PhysicsAsset);
        }
        GroomComponent->SetEnableSimulation(bEnableSimulation);
    }
}

void AMyGroomCharacter::ToggleSimulation()
{
    if (GroomComponent)
    {
        bEnableSimulation = !bEnableSimulation;
        GroomComponent->SetEnableSimulation(bEnableSimulation);
        if (!bEnableSimulation)
        {
            GroomComponent->ResetSimulation();
        }
    }
}
```

## 模块依赖

以下为该插件独特且不常见的依赖（需在你的 Build.cs 中引用）：

| 模块 | 用途 |
|---|---|
| `Niagara` | 物理模拟求解器、数据接口 |
| `MeshDeformer` | 网格变形器框架集成 |
| `GeometryCache` | GeometryCache 格式的毛发绑定支持 |
| `Dataflow` | Dataflow 节点系统集成 |
| `DataflowCore` | Dataflow 核心类型 |
| `DataflowEngine` | Dataflow 引擎执行 |
| `HairCardGeneratorFramework` | 发片卡生成 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `aa770ac7` | Remove crash in mobile renderer when using groom binding. | 修复移动端使用毛发绑定时的崩溃 |
| 2026-05-26 | `3da4e98e` | Fix crash when selecting the addSolverDeformer dataflow node | 修复选择 dataflow 求解器节点时的崩溃 |
| 2026-05-26 | `d2f5bcd4` | Fix crash when recompiling BP while playing groom in dataflow editor + fix bad number of vertices ca | 修复 dataflow 编辑器中重编译 BP 时的崩溃及顶点数错误 |
| 2026-05-22 | `9ce84766` | Remove the CreateGroomDataflowAsset from the context menu | 从右键菜单中移除创建 Dataflow 资产选项 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口客户端关联/解除通知重构 |

### 维护评价

- **创建时间**：2020 年 11 月，随 UE5 早期开发阶段引入
- **最近更新频率**：2026 年 5 月仍有活跃更新，最近的 commit 主要是 bug 修复
- **维护状态**：**活跃维护中** — 该插件是 UE5 官方毛发渲染的核心组件，由 Epic Games 持续维护
- **已知注意事项**：
  - 默认未启用（`EnabledByDefault: false`），需手动开启
  - 移动端支持有限，部分功能在移动渲染器上仍有问题（如最近修复的崩溃）
  - Dataflow 集成部分仍在持续完善中
  - 部分 API 标记为 `UE_DEPRECATED`，建议使用新版访问器函数
- **推荐程度**：✅ **强烈推荐** — 这是 UE5 官方毛发解决方案，功能完整，社区广泛使用。对于需要高质量毛发渲染的项目（写实角色、数字人等），这是唯一推荐的方案

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/HairStrands)