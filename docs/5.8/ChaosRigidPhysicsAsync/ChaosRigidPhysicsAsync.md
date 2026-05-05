# Chaos Rigid Physics Async

> Provides the Chaos Rigid Body Physics Engine (Async Implementation)

| 属性 | 值 |
|---|---|
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ChaosRigidPhysicsAsync` (Runtime), `ChaosRigidPhysicsAsyncTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-31 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosRigidPhysicsAsync) | |

## 用途

本插件为 Chaos 物理引擎提供了**异步刚体物理**的实现层。它基于 UE 的 `RigidPhysics` 抽象接口（`IRigidBody`、`IRigidScene` 等），将 Chaos 的 `FPBDRigidsSolver` 封装为可在独立物理线程上运行的异步场景。

核心解决的问题是：**将刚体物理模拟从游戏线程解耦到独立的物理线程上执行**，从而避免物理计算阻塞游戏逻辑。插件采用 GT（Game Thread）/ PT（Physics Thread）双线程架构——每个核心概念（场景、刚体、关节、形状）都有对应的 GT 和 PT 版本，GT 版本负责接收用户输入和读取结果，PT 版本在物理线程上执行实际模拟。

这是 Chaos 物理系统向模块化、可插拔架构演进的一部分，通过 `RigidPhysics` 抽象层使得物理后端可以替换。

## 使用场景

- 你需要将物理模拟放到独立线程上运行，避免阻塞游戏线程 → 使用本插件的异步场景
- 你在构建自定义物理管线，需要直接操作 Chaos 求解器但通过异步接口 → 使用 `FRigidSceneAsyncGT` / `FRigidSceneAsyncPT`
- 你需要在异步物理线程上创建和管理刚体、关节约束、几何集合 → 使用本插件提供的完整异步 API
- 你在开发需要高帧率且物理密集的游戏（如大量刚体交互），需要将物理计算卸载到后台线程

## 蓝图用法

本插件**不提供蓝图接口**。所有类均标记为 `UE_INTERNAL`，属于引擎内部 C++ API，不暴露给蓝图系统。

## C++ 用法

### 头文件引入

```cpp
#include "ChaosRigidPhysicsAsync/RigidSceneAsync.h"
#include "ChaosRigidPhysicsAsync/RigidFactoryAsync.h"
#include "ChaosRigidPhysicsAsync/RigidSceneSettingsAsync.h"
#include "ChaosRigidPhysicsAsync/RigidBodyAsync.h"
#include "ChaosRigidPhysicsAsync/JointConstraint6DOFAsync.h"
```

### 基本用法

创建异步物理场景并添加刚体：

```cpp
#include "ChaosRigidPhysicsAsync/RigidFactoryAsync.h"
#include "ChaosRigidPhysicsAsync/RigidSceneSettingsAsync.h"
#include "ChaosRigidPhysicsAsync/RigidSceneAsync.h"
#include "ChaosRigidPhysicsAsync/RigidBodyAsync.h"

using namespace Chaos::Rigids::Async;

// 1. 创建工厂
FRigidFactoryAsync Factory;

// 2. 配置异步场景设置
FRigidSceneSettingsAsync SceneSettings;
SceneSettings.AsyncDt = 1.0f / 60.0f;  // 固定物理步长 60Hz
SceneSettings.ThreadingMode = EChaosThreadingMode::DedicatedThread;  // 使用专用物理线程

// 3. 创建异步场景
UE::Physics::FRigidSceneHandle SceneHandle = Factory.CreateScene(
    TEXT("MyAsyncScene"), &SceneSettings);

// 4. 通过 GT 场景创建刚体
FRigidSceneAsyncGT* SceneGT = /* 从 handle 获取 */;
FRigidBodyAsyncGT* Body = SceneGT->CreateBody(
    TEXT("MyBody"),
    UE::Physics::ERigidMovementType::Dynamic);

// 5. 设置刚体属性
Body->SetMass(10.0);
Body->SetInertia(FVector3d(1.0, 1.0, 1.0));
Body->SetGravityScale(1.0f);
Body->InitTransform(FTransform(FVector(0, 0, 100)));

// 6. 创建碰撞形状
UE::Physics::FRigidShapeInstanceSetup ShapeSetup;
// ... 配置形状参数 ...
FRigidShapeInstanceAsync* Shape = Body->CreateShape(ShapeSetup);

// 7. 驱动物理模拟
SceneGT->StartTick(DeltaTime);  // 开始一个物理 tick
// ... 游戏线程继续其他工作 ...
SceneGT->WaitOnTick();           // 等待物理 tick 完成
SceneGT->EndTick();              // 结束 tick，读取结果

// 8. 读取结果
FTransform BodyTransform = Body->GetTransform();
FBounds3d BodyBounds = Body->GetBounds();

// 9. 清理
SceneGT->DestroyBody(Body);
Factory.DestroyScene(SceneHandle);
```

### 进阶用法

创建 6DOF 关节约束：

```cpp
#include "ChaosRigidPhysicsAsync/JointConstraint6DOFAsync.h"

// 创建两个刚体
FRigidBodyAsyncGT* BodyA = SceneGT->CreateBody(TEXT("BodyA"), UE::Physics::ERigidMovementType::Dynamic);
FRigidBodyAsyncGT* BodyB = SceneGT->CreateBody(TEXT("BodyB"), UE::Physics::ERigidMovementType::Dynamic);

// 创建 6DOF 关节约束
FJointConstraint6DOFAsyncGT* Joint = SceneGT->CreateJointConstraint6DOF();

// 设置约束的两个刚体
Joint->SetBodies(BodyA, BodyB);

// 设置关节变换（局部空间）
Joint->SetJointTransforms(
    FTransform3d(FVector3d(0, 0, 50)),   // BodyA 上的连接点
    FTransform3d(FVector3d(0, 0, -50))); // BodyB 上的连接点

// 配置线性运动类型
Joint->SetLinearMotionTypesX(UE::Physics::EJointMotionType::Locked);
Joint->SetLinearMotionTypesY(UE::Physics::EJointMotionType::Locked);
Joint->SetLinearMotionTypesZ(UE::Physics::EJointMotionType::Limited);

// 设置线性限制
Joint->SetLinearLimit(10.0);

// 配置角度限制
Joint->SetAngularMotionTypesX(UE::Physics::EJointMotionType::Limited);
Joint->SetAngularMotionTypesY(UE::Physics::EJointMotionType::Free);
Joint->SetAngularMotionTypesZ(UE::Physics::EJointMotionType::Free);
Joint->SetAngularLimits(FVector3d(45.0, 180.0, 180.0)); // 度

// 启用软限制
Joint->SetSoftLinearLimitsEnabled(true);
Joint->SetSoftLinearStiffness(1000.0);
Joint->SetSoftLinearDamping(100.0);

// 启用碰撞
Joint->SetCollisionEnabled(true);

// 激活约束
Joint->Activate();
```

管理形状实例容器：

```cpp
#include "ChaosRigidPhysicsAsync/ShapeInstanceContainerAsync.h"

// 形状实例通过容器管理，支持对象池复用
// GT 端使用 FShapeInstanceContainerAsyncGT
// PT 端使用 FShapeInstanceContainerAsyncPT

// 形状视图用于跟踪附加到某个刚体的所有形状
FShapeInstanceView ShapeView;
int32 ShapeIndex = ShapeContainer.Add(*ShapeInstance, ShapeView);

// 通过视图和索引获取形状
FRigidShapeInstanceAsync* Shape = ShapeContainer.Get(ShapeView, ShapeIndex);

// 配置形状属性
Shape->SetQueryEnabled(true);       // 启用查询（射线检测等）
Shape->SetSimEnabled(true);         // 启用模拟碰撞
Shape->SetCollisionTraceType(ECollisionTraceFlag::CTF_UseSimpleAndComplex);

// 设置碰撞过滤
Chaos::Filter::FShapeFilterData FilterData;
// ... 配置过滤数据 ...
Shape->SetShapeFilter(FilterData);

// 设置材质
TArray<UE::Physics::FMaterialHandle> Materials;
// ... 填充材质句柄 ...
Shape->SetMaterials(MoveTemp(Materials));
```

## Demo 示例

一个完整的最小示例，展示如何创建异步物理场景、添加刚体并驱动模拟：

```cpp
// AsyncPhysicsDemo.h
#pragma once

#include "CoreMinimal.h"
#include "ChaosRigidPhysicsAsync/RigidFactoryAsync.h"
#include "ChaosRigidPhysicsAsync/RigidSceneAsync.h"
#include "ChaosRigidPhysicsAsync/RigidSceneSettingsAsync.h"
#include "ChaosRigidPhysicsAsync/RigidBodyAsync.h"

class FAsyncPhysicsDemo
{
public:
    void Initialize();
    void Tick(float DeltaTime);
    void Shutdown();

private:
    Chaos::Rigids::Async::FRigidFactoryAsync Factory;
    Chaos::Rigids::Async::FRigidSceneAsyncGT* SceneGT = nullptr;
    Chaos::Rigids::Async::FRigidBodyAsyncGT* TestBody = nullptr;
    UE::Physics::FRigidSceneHandle SceneHandle;
};
```

```cpp
// AsyncPhysicsDemo.cpp
#include "AsyncPhysicsDemo.h"

using namespace Chaos::Rigids::Async;

void FAsyncPhysicsDemo::Initialize()
{
    // 配置异步场景
    FRigidSceneSettingsAsync Settings;
    Settings.AsyncDt = 1.0f / 60.0f;
    Settings.ThreadingMode = EChaosThreadingMode::DedicatedThread;

    // 创建场景
    SceneHandle = Factory.CreateScene(TEXT("DemoScene"), &Settings);
    SceneGT = static_cast<FRigidSceneAsyncGT*>(
        /* 从 SceneHandle 获取场景指针 */);

    // 创建一个动态刚体
    TestBody = SceneGT->CreateBody(
        TEXT("FallingBox"),
        UE::Physics::ERigidMovementType::Dynamic);

    // 设置物理属性
    TestBody->SetMass(5.0);
    TestBody->SetGravityScale(1.0f);
    TestBody->InitTransform(FTransform(FVector(0, 0, 500)));

    // 激活刚体
    TestBody->Activate();
}

void FAsyncPhysicsDemo::Tick(float DeltaTime)
{
    if (!SceneGT) return;

    // 启动物理 tick（异步执行）
    SceneGT->StartTick(DeltaTime);

    // 此处可以执行其他游戏逻辑，物理在后台线程计算
    // ...

    // 等待物理完成
    SceneGT->WaitOnTick();
    SceneGT->EndTick();

    // 读取刚体变换
    if (TestBody && TestBody->IsActive())
    {
        FTransform CurrentTransform = TestBody->GetTransform();
        UE_LOG(LogTemp, Log, TEXT("Body position: %s"),
            *CurrentTransform.GetLocation().ToString());
    }
}

void FAsyncPhysicsDemo::Shutdown()
{
    if (SceneGT && TestBody)
    {
        SceneGT->DestroyBody(TestBody);
        TestBody = nullptr;
    }

    Factory.DestroyScene(SceneHandle);
    SceneGT = nullptr;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RigidPhysics` | 提供 `IRigidBody`、`IRigidScene`、`IRigidFactory` 等抽象接口 |
| `Chaos` | Chaos 物理引擎核心，提供 `FPBDRigidsSolver`、`FJointConstraint`、`FPerShapeData` 等 |
| `PhysicsCore` | 物理核心类型定义 |
| `ChaosSolvers` | Chaos 求解器模块 |

## 维护状态

### 近期更新

- 2026-04-14 `35e60df1` Migrate UE_LOG to UE_LOGF.
- 2026-04-13 `55407bce` Chaos API: Updated the scene api by splitting Tick into Start/End Tick. Also added WaitOnTick.
- 2026-04-09 `c63a4c15` Chaos API: Updating shape instance to handle materials.
- 2026-04-08 `6d6dbc44` Chaos API: Adding PhysicsService and removing the dependecy of the async plugin on dataflow.
- 2026-03-31 `5f0e43c9` Chaos API: Updating shape instance to handle convex, triangle mesh, and height field geometry types.

### 维护评价

- **实验性状态**：`.uplugin` 中 `IsExperimentalVersion=true`，`EnabledByDefault=false`，明确标记为实验性功能
- **API 稳定性**：所有公开类和方法均标记为 `UE_INTERNAL`，API 随时可能变更
- **功能完整度**：核心的场景、刚体、关节、形状管理已实现，但 GeometryCollection 支持不完整，许多高级物理属性（CCD、速度限制、惯性调节等）被注释掉
- **架构成熟度**：GT/PT 分离架构设计清晰，遵循 Chaos 引擎的标准模式
- **风险提示**：⚠️ 这是实验性插件，不建议在生产环境中使用。API 可能在任何版本中发生破坏性变更。适合用于研究和原型开发。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosRigidPhysicsAsync)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosRigidPhysicsAsync/Tests)