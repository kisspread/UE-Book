# ChaosUserDataPT

> Custom per-particle userdata. Write-only on game thread, read-only on physics thread.

| 属性 | 值 |
|---|---|
| 中文名 | 粒子用户数据 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ChaosUserDataPT` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-05-12 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosUserDataPT) | |

## 用途

在 Chaos 物理引擎中，每个粒子（Particle）通常只携带固定的物理属性（质量、速度、形状等）。但在很多游戏场景下，需要在**接触级别**的物理交互中引用额外的游戏性数据——例如不同材质的自定义摩擦系数、碰撞伤害值、魔法抗性等。

ChaosUserDataPT 提供了一个轻量的模板类 `TUserDataManagerPT`，它利用 Chaos 的 SimCallback 机制，在**游戏线程**上安全地**写入**每个粒子关联的自定义数据，并在**物理线程**上以只读方式访问这些数据。数据按粒子唯一索引（`FUniqueIdx`）进行映射，天然线程安全，无需手动加锁。

该插件本身不提供任何具体的数据类型或访问策略，它只是一个“数据管道”：你来定义 `TUserData` 的结构，它负责在物理线程上维护这些数据，并保证 GT 写入 → PT 读取的同步。

## 使用场景

- **自定义物理材质**：你希望粒子表面的摩擦/弹力根据游戏逻辑动态变化（例如冰面、油渍、粘液），可以给每个粒子绑定一个 `float` 或 `FVector` 作为系数，在接触回调中读取。
- **碰撞触发游戏逻辑**：子弹击中不同敌人时，需要根据弹头携带的伤害值、穿透力进行判定，这些数据可以附着在子弹粒子上。
- **浮力/水流效果**：对特定粒子附加一个“流体密度”标记，在浮力求解器中读取并调整浮力大小。
- **实现自定义约束**：在约束求解过程中需要读取额外的属性（如弹簧的弹性限度、摩擦力）。

## 蓝图用法

> 本插件为纯 C++ 模板类，未公开任何 `UFUNCTION` 或 `UBlueprintCallable` 节点，因此**无法直接在蓝图中使用**。需要通过 C++ 封装后暴露给蓝图。

如果你需要在蓝图中使用该功能，建议编写一个 `UObject` 派生类来管理 `TUserDataManagerPT` 实例，并将 `SetData_GT` / `GetData_PT` 等操作包装为蓝图函数。

## C++ 用法

### 头文件引入

```cpp
#include "ChaosUserDataPT.h"
#include "PhysicsProxy/SingleParticlePhysicsProxy.h"   // 如果需要 FUniqueIdx
```

### 基本用法

以下示例演示如何定义一个简单的用户数据结构（`int32` 作为自定义标签），为粒子设置数据，并在物理线程上读取。

```cpp
// 1. 定义用户数据类型
using FMyUserData = int32;  // 仅用于示例，实际可以是结构体/类

// 2. 获取 Chaos 求解器实例
// 假设你已经有一个 FPhysScene* 或 UWorld*，通过它获取 FDynamicSolver
Chaos::FDynamicSolver* Solver = /* 从场景获得 */;

// 3. 注册 SimCallback 返回管理器指针
TUniquePtr<Chaos::TUserDataManagerPT<FMyUserData>> UserDataManager(
    Solver->CreateAndRegisterSimCallbackObject_External<Chaos::TUserDataManagerPT<FMyUserData>>()
);

// 4. 游戏线程：为某个粒子设置用户数据
FSingleParticlePhysicsProxy* ParticleProxy = /* 从场景创建或获取 */;
const Chaos::FUniqueIdx Idx = ParticleProxy->GetGameThreadAPI().UniqueIdx();
UserDataManager->SetData_GT(Idx, MakeUnique<FMyUserData>(42));  // 写入 42

// 5. 物理线程（例如在 OnPreSimulate_Internal 中）：读取数据
// 注意：此代码运行在物理线程回调内部，通过 SimCallbackInput 访问
const TUserDataManagerPT<FMyUserData>* ManagerPT = /* 获取物理线程管理器实例 */;
const FMyUserData* Data = ManagerPT->GetData_PT(Idx);
if (Data)
{
    // 使用 *Data（值为 42）
}
```

**关键点**：
- `SetData_GT` 拥有所有权（`TUniquePtr<TUserData>`），调用后数据移入输入队列。
- `GetData_PT` 返回原始指针，物理线程持有数据的所有权直至被清除。
- 移除数据使用 `RemoveData_GT(Idx)`，清空所有使用 `ClearData_GT(bResizeOnClear)`。

### 进阶用法

- **批量设置**：在游戏线程循环中为大量粒子设置数据，每个粒子仅一次 SetData_GT 调用。
- **线程安全访问**：物理线程上只读，游戏线程上只写，无需额外同步。
- **配合接触回调**：在 `FPhysicsContact` 或其回调中获取粒子的 `FUniqueIdx`，然后调用 `ManagerPT->GetData_PT` 获取自定义数据，影响物理行为。

## Demo 示例

一个完整的 C++ 示例，展示如何在一个自定义的 `AActor` 中使用该插件创建和管理粒子用户数据。

```cpp
// MyPhysicsActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ChaosUserDataPT.h"
#include "PhysicsProxy/SingleParticlePhysicsProxy.h"
#include "MyPhysicsActor.generated.h"

UCLASS()
class AMyPhysicsActor : public AActor
{
    GENERATED_BODY()

public:
    AMyPhysicsActor();

protected:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

private:
    // 自定义用户数据结构（例如浮点值表示自定义质量比例）
    struct FMyParticleData
    {
        float CustomFactor;
    };

    TUniquePtr<Chaos::TUserDataManagerPT<FMyParticleData>> UserDataMgr;
    TArray<FSingleParticlePhysicsProxy*> ParticleProxies;
};
```

```cpp
// MyPhysicsActor.cpp
#include "MyPhysicsActor.h"
#include "Chaos/ChaosEngineInterface.h"
#include "PhysicsEngine/PhysicsSettings.h"

AMyPhysicsActor::AMyPhysicsActor()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AMyPhysicsActor::BeginPlay()
{
    Super::BeginPlay();

    // 获取物理场景求解器
    UWorld* World = GetWorld();
    if (!World) return;
    FPhysScene* PhysScene = World->GetPhysicsScene();
    if (!PhysScene) return;

    // 通过外部接口获取某个求解器（简化示例，假设第一个）
    Chaos::FPhysicsSolver* Solver = nullptr;
    TArray<Chaos::FPhysicsSolver*> Solvers;
    PhysScene->GetSolvers(Solvers);
    if (Solvers.Num() > 0)
        Solver = Solvers[0];
    if (!Solver) return;

    // 创建管理器
    UserDataMgr = Solver->CreateAndRegisterSimCallbackObject_External<Chaos::TUserDataManagerPT<FMyParticleData>>();

    // 创建几个粒子并保存代理
    for (int32 i = 0; i < 3; ++i)
    {
        // 实际创建粒子需要物理材质、形状等，此处省略
        // 假设已创建 FSingleParticlePhysicsProxy* Proxy;
        // FSingleParticlePhysicsProxy* Proxy = ...;
        // ParticleProxies.Add(Proxy);
    }
}

void AMyPhysicsActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (!UserDataMgr.IsValid()) return;

    // 每帧为每个粒子设置不同的自定义因子
    for (int32 i = 0; i < ParticleProxies.Num(); ++i)
    {
        FSingleParticlePhysicsProxy* Proxy = ParticleProxies[i];
        if (!Proxy) continue;

        const Chaos::FUniqueIdx Idx = Proxy->GetGameThreadAPI().UniqueIdx();
        auto Data = MakeUnique<FMyParticleData>();
        Data->CustomFactor = FMath::FRandRange(0.5f, 2.0f);
        UserDataMgr->SetData_GT(Idx, MoveTemp(Data));
    }
}
```

> 注意：实际创建粒子需通过 `SpawnSingleParticle` 等 API，本示例仅为展示数据绑定模式。

## 模块依赖

该插件依赖 Chaos 物理引擎及其相关模块，无需额外手动配置。

| 模块 | 用途 |
|---|---|
| `Chaos` | 提供求解器、粒子代理、SimCallback 基础 |
| `PhysicsCore` | 提供物理场景接口、FPhysScene、物理代理等 |

其余依赖均为标准引擎模块（Core、CoreUObject、Engine 等），已自动包含。

## 维护状态

### 近期更新

- 2024-11-10 `66e9bb39` 移除所有 `#if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2` 作用域（代码清理）
- 2024-06-11 `15021cb3` 浮力子系统仅循环涉及水的中相（与插件核心无关，属于同目录下的其他改动）
- 2024-06-11 `d9860ed2` 回退编译错误修复
- 2024-06-11 `c2cf199a` 浮力子系统仅循环涉及水的中相（重复）
- 2023-05-12 `0f1b41d0` Chaos：为异步回调添加统计 ID，以便更好识别哪些回调正在运行以及运行时间

### 维护评价

- **创建时间**：2023-05-12，距今约 2.5 年。
- **活跃度**：最近一次实质性功能更新是 2023-05-12（添加统计 ID），后续仅有一些清理和无关的浮力改动。最近 1 年内没有任何针对本插件核心逻辑的更新。
- **状态**：插件标记为 `IsBetaVersion=true`，属于实验性插件。核心 API 自发布后未改动，说明设计稳定但可能缺少维护。
- **推荐使用**：如果你的项目已使用 Chaos 物理引擎且需要在粒子上绑定自定义数据，本插件提供了最简单、线程安全的方式。但请注意其实验性，在正式项目中建议自行封装一层，并准备应对可能的 API 变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosUserDataPT)
- 官方文档：无
- 测试用例：未发现单独测试文件（插件仅 5 个源文件，无 Tests 目录）