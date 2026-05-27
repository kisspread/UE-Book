# Chaos Cloth

> Adds Chaos Cloth modules.

| 属性 | 值 |
|---|---|
| 中文名 | 混沌布料 |
| 分类 | Physics |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ChaosCloth` (Runtime), `ChaosClothEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2024-03-22 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosCloth) | |

## 用途

ChaosCloth 是 UE5 基于 Chaos 物理引擎的布料模拟系统，用于在运行时和编辑器中模拟角色衣物、旗帜、窗帘等柔性物体的物理行为。它是 UE5 中 PhysX 布料的替代方案，使用 Chaos 求解器提供更精确的布料物理效果。

该插件解决的核心问题：
- **布料物理模拟**：基于粒子的 XPBD（Extended Position-Based Dynamics）和力约束（Force-based）双求解器架构，模拟布料的拉伸、弯曲、面积保持等物理约束
- **碰撞检测**：支持布料与角色骨骼碰撞体（Capsule/Sphere/SkinnedTriangleMesh）的交互，以及布料自碰撞
- **环境交互**：空气动力学模型（阻力/升力）、压力、浮力（与 Buoyancy/Water 插件联动）、重力
- **动画驱动**：通过 AnimDrive 约束将布料引导回动画姿态，支持权重贴图逐点控制

该插件从 **Experimental** 阶段毕业（2024-03-22），并合并了独立的 ChaosClothEditor 模块，标志着 Chaos 布料已成为 UE5 的正式布料物理方案。

## 使用场景

- 你有一个带布料模拟的角色（披风、裙子、衣摆）→ 在 SkeletalMesh 的 Clothing 面板中配置 Chaos Cloth 资产
- 你需要运行时动态调整布料参数（风力、刚度、重力）→ 通过 `UChaosClothingInteractor` 蓝图接口控制
- 你需要布料与水面交互（浮力）→ 启用 Buoyancy/Water 依赖，配置浮力参数
- 你需要高精度的布料与复杂碰撞体交互（蒙皮三角网格碰撞）→ 使用 `FClothComplexColliders` 与 `SkinnedTriangleMesh`
- 你需要缓存布料动画用于回放 → 通过 ChaosCaching 系统与 `FSkeletalMeshCacheAdapter` 集成

## 蓝图用法

ChaosCloth 的蓝图接口主要通过 `UChaosClothingInteractor` 暴露，可在运行时动态控制布料模拟参数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetMaterialLinear` | 设置线性材质参数（边刚度、弯曲刚度、面积刚度） | `UChaosClothingInteractor` |
| `SetMaterial` | 设置材质参数（Low/High 加权值，配合权重贴图） | `UChaosClothingInteractor` |
| `SetMaterialBuckling` | 设置屈曲参数（屈曲比率和屈曲刚度） | `UChaosClothingInteractor` |
| `SetLongRangeAttachmentLinear` | 设置线性远距离附着（系绳刚度/缩放） | `UChaosClothingInteractor` |
| `SetLongRangeAttachment` | 设置远距离附着（Low/High 加权值） | `UChaosClothingInteractor` |
| `SetCollision` | 设置碰撞参数（碰撞厚度、摩擦系数、CCD、自碰撞厚度） | `UChaosClothingInteractor` |
| `SetBackstop` | 启用/禁用背挡约束 | `UChaosClothingInteractor` |
| `SetDamping` | 设置阻尼系数（全局阻尼和局部阻尼） | `UChaosClothingInteractor` |
| `SetWind` | 设置风力参数（阻力/升力/气密度/风速/外阻力/外升力） | `UChaosClothingInteractor` |
| `SetPressure` | 设置压力参数 | `UChaosClothingInteractor` |
| `SetGravity` | 设置重力（缩放/覆盖/覆盖向量） | `UChaosClothingInteractor` |
| `SetAnimDriveLinear` | 设置线性动画驱动刚度 | `UChaosClothingInteractor` |
| `SetAnimDrive` | 设置动画驱动（刚度/阻尼 Low/High） | `UChaosClothingInteractor` |
| `SetVelocityScale` | 设置速度缩放（线性/角速度/虚构角缩放） | `UChaosClothingInteractor` |
| `SetVelocityClamps` | 设置速度钳制（线性/加速度/角速度/角加速度上限） | `UChaosClothingInteractor` |
| `ResetAndTeleport` | 重置布料模拟或传送重置 | `UChaosClothingInteractor` |

**求解器级别节点**（`UChaosClothingSimulationInteractor`）：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetNumIterations` | 设置求解器迭代次数 | `UChaosClothingSimulationInteractor` |
| `SetMaxNumIterations` | 设置最大迭代次数 | `UChaosClothingSimulationInteractor` |
| `SetNumSubsteps` | 设置子步数 | `UChaosClothingSimulationInteractor` |
| `EnableGravityOverride` | 启用全局重力覆盖 | `UChaosClothingSimulationInteractor` |
| `DisableGravityOverride` | 禁用全局重力覆盖 | `UChaosClothingSimulationInteractor` |

### 使用示例（蓝图描述）

1. **获取布料交互器**：从 `SkeletalMeshComponent` 获取 `ClothingSimulationInteractor`，将其转换为 `UChaosClothingSimulationInteractor`，再通过 `CreateClothingInteractor()` 获取特定布料的 `UChaosClothingInteractor`
2. **设置风力**：调用 `SetWind` 节点，设置 `Drag = (0.07, 0.5)`、`Lift = (0.07, 0.5)`、`AirDensity = 1.225e-6`、`WindVelocity = (100, 0, 0)`，让布料在 X 方向受风吹
3. **运行时调节刚度**：调用 `SetMaterialLinear`，将 `EdgeStiffness` 和 `BendingStiffness` 从 1.0 降低到 0.3，模拟更软的布料材质
4. **传送重置**：在角色瞬移时调用 `ResetAndTeleport(bReset=false, bTeleport=true)` 防止布料拉伸

## C++ 用法

### 头文件引入

```cpp
#include "ChaosCloth/ChaosClothingSimulation.h"
#include "ChaosCloth/ChaosClothConfig.h"
#include "ChaosCloth/ChaosClothingSimulationInteractor.h"
```

### 基本用法

通过布料配置类 `UChaosClothConfig` 设置物理参数（来源：`Public/ChaosCloth/ChaosClothConfig.h`）：

```cpp
// 获取布料配置对象（通常在 Clothing Asset 中自动创建）
UChaosClothConfig* ClothConfig = /* 从 ClothingAsset 获取 */;

// 设置质量模式为密度
ClothConfig->MassMode = EClothMassMode::Density;
ClothConfig->Density = 0.35f;  // 棉布: 0.2, 丝绸: 0.1, 牛仔: 0.4

// 设置材质属性
ClothConfig->EdgeStiffnessWeighted = { 1.f, 1.f };    // 边刚度 (Low, High)
ClothConfig->BendingStiffnessWeighted = { 0.5f, 0.5f }; // 弯曲刚度
ClothConfig->AreaStiffnessWeighted = { 1.f, 1.f };     // 面积刚度

// 设置碰撞
ClothConfig->CollisionThickness = 1.0f;
ClothConfig->FrictionCoefficient = 0.8f;
ClothConfig->bUseCCD = false;
ClothConfig->bUseSelfCollisions = false;

// 设置环境参数
ClothConfig->DampingCoefficient = 0.01f;
ClothConfig->GravityScale = 1.f;
ClothConfig->Drag = { 0.035f, 1.f };
ClothConfig->Lift = { 0.035f, 1.f };
```

### 进阶用法

使用 `UChaosClothingInteractor` 在运行时动态控制布料（来源：`Public/ChaosCloth/ChaosClothingSimulationInteractor.h`）：

```cpp
// 从 SkeletalMeshComponent 获取布料模拟交互器
USkeletalMeshComponent* SKComp = /* 获取组件 */;
UClothingSimulationInteractor* BaseInteractor = SKComp->GetClothingInteractor();
UChaosClothingSimulationInteractor* SimInteractor = Cast<UChaosClothingSimulationInteractor>(BaseInteractor);

if (SimInteractor)
{
    // 设置求解器参数
    SimInteractor->SetNumIterations(3);
    SimInteractor->SetMaxNumIterations(10);
    SimInteractor->SetNumSubsteps(1);
    
    // 获取特定布料的交互器
    UClothingInteractor* ClothInteractor = SimInteractor->CreateClothingInteractor();
    UChaosClothInteractor* ChaosInteractor = Cast<UChaosClothInteractor>(ClothInteractor);
    
    if (ChaosInteractor)
    {
        // 动态设置材质参数
        ChaosInteractor->SetMaterial(
            FVector2D(0.8f, 0.8f),   // EdgeStiffness (Low, High)
            FVector2D(0.5f, 0.5f),   // BendingStiffness
            FVector2D(1.f, 1.f)      // AreaStiffness
        );
        
        // 设置风力效果
        ChaosInteractor->SetWind(
            FVector2D(0.07f, 0.5f),  // Drag
            FVector2D(0.07f, 0.5f),  // Lift
            1.225e-6f,               // AirDensity
            FVector(200.f, 0.f, 0.f), // WindVelocity
            FVector2D(0.07f, 0.5f),  // OuterDrag
            FVector2D(0.07f, 0.5f)   // OuterLift
        );
        
        // 设置速度缩放
        ChaosInteractor->SetVelocityScale(
            FVector(0.75f, 0.75f, 0.75f),  // LinearVelocityScale
            0.75f,                           // AngularVelocityScale
            1.f                              // FictitiousAngularScale
        );
    }
    
    // 设置重力覆盖
    SimInteractor->EnableGravityOverride(FVector(0.f, 0.f, -490.f)); // 半重力
}
```

### 约束系统用法

直接使用底层约束系统（来源：`Public/ChaosCloth/ChaosClothConstraints.h`）：

```cpp
Chaos::FClothConstraints Constraints;

// 初始化为力约束求解器模式
Constraints.Initialize(
    Evolution,           // Softs::FEvolution*
    PerSolverField,      // FPerSolverFieldSystem*
    InterpolatedPositions,
    InterpolatedNormals,
    AnimationVelocities,
    Normals,
    LastSubframeCollisionTransformsCCD,
    CollisionParticleCollided,
    CollisionContacts,
    CollisionNormals,
    CollisionPhis,
    ParticleRangeId
);

// 添加约束规则（从属性集合读取配置）
Constraints.AddRules(
    ConfigProperties,    // Softs::FCollectionPropertyConstFacade&
    TriangleMesh,        // FTriangleMesh&
    PatternData,         // FClothingPatternData*
    WeightMaps,          // TMap<FString, TConstArrayView<FRealSingle>>&
    VertexSets,          // 顶点选择集
    FaceSets,            // 面选择集
    FaceIntMaps,         // 面整数映射
    Tethers,             // 系绳连接数据
    MeshScale,           // 网格缩放
    bEnabled,            // 是否启用
    ComplexColliders,    // 复杂碰撞体
    ManagedArrayCollection,  // 管理数组集合
    AccessoryMeshes      // 附件网格
);
```

## 模块依赖

从插件依赖（`.uplugin` 的 Plugins 字段）和源码结构推断：

| 模块 | 用途 |
|---|---|
| `ChaosCaching` | 布料模拟数据缓存（录制/回放），通过 `FSkeletalMeshCacheAdapter` 集成 |
| `Buoyancy` | 浮力场支持，布料可与浮力场交互（`FBuoyancyField`） |
| `Water` | 水体交互，配合浮力系统实现布料水面交互 |

特殊依赖：无特殊依赖（仅标准 Core/Engine/Slate 等 + Chaos 物理引擎内部模块）

> **注意**：该插件深度依赖 Chaos 物理引擎内部模块（`FEvolution`/`FPBDEvolution`、`FPerSolverFieldSystem`、各种 Softs 约束类等），这些是引擎内部 API，不在 Public 模块依赖中列出。普通使用者无需直接调用这些底层接口。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为 float 的编译警告 |
| 2026-04-23 | `85f3a947` | [Chaos Cloth] Clamp SolverLOD in ChaosClothingSimulationSolver to prevent out of bound crash when so | 钳制 SolverLOD 防止求解器越界崩溃 |
| 2026-04-21 | `9322be91` | Minor cloth debug draw improvements: | 布料调试绘制的小幅改进 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 新日志宏 |
| 2026-03-31 | `0d36bcd0` | Chaos Cloth : | 混沌布料更新 |

### 维护评价

**活跃维护** ✅

- **创建时间**：2024-03-22（约 2 年前，从 Experimental 毕业）
- **更新频率**：最近 2 个月内有 5 次提交，更新频繁
- **更新内容**：包含 bug 修复（越界崩溃、编译警告）、API 改进（日志宏迁移）、调试工具改进
- **维护状态**：由 Epic Games 官方团队维护，属于核心物理系统的一部分
- **成熟度**：已从 Experimental 毕业，作为 UE5 默认布料方案（`EnabledByDefault: true`）
- **已知限制**：部分 API 标记为 Deprecated（如旧版 Wind 模型、MultiRes 约束），建议使用新版 API

**推荐使用**：该插件是 UE5 布料模拟的官方推荐方案，活跃维护中，可放心用于生产环境。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosCloth)
- [官方文档]()（无）