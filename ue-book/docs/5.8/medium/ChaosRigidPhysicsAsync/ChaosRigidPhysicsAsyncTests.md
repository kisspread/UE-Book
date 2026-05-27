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
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosRigidPhysicsAsync) | |

## 用途

该插件是 Chaos 物理引擎中**刚体物理模拟**的一个**异步实现**。它并非一个面向最终用户的高级功能插件，而是 Chaos 物理系统底层架构的一部分，旨在将刚体物理的计算（如碰撞检测、约束求解、积分）从游戏线程或渲染线程中分离出来，放入独立的物理线程或任务中执行，以提升性能和避免阻塞主线程。

其核心价值在于为 `RigidPhysics` 模块提供了一个异步的后端工厂 (`FRigidFactoryAsync`) 和场景设置 (`FRigidSceneSettingsAsync`)，使得物理场景的创建、配置和模拟可以异步进行。

## 使用场景

- 你正在开发一个对物理性能要求极高的游戏（如大量刚体交互、复杂载具模拟），需要将物理计算负载从游戏线程卸载。
- 你正在扩展或定制 Chaos 物理引擎，需要为其刚体子系统提供一个异步的执行环境。
- 你正在编写底层物理相关的自动化测试或基准测试，需要直接操控异步物理场景。

## 蓝图用法

基于提供的测试源码分析，该插件主要提供底层 C++ API，未发现直接暴露给蓝图的 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)`。其使用场景更偏向于引擎底层开发和测试。

## C++ 用法

### 头文件引入

```cpp
#include "ChaosRigidPhysicsAsync/RigidFactoryAsync.h"
#include "ChaosRigidPhysicsAsync/RigidSceneSettingsAsync.h"
#include "RigidPhysics/RigidScene.h"
```

### 基本用法

以下示例展示了如何使用异步工厂创建一个物理场景并运行一次模拟步进。此模式常见于底层测试和性能分析。
（来源：`Private/RigidTestFixture.h` 及其对应实现）

```cpp
#include "ChaosRigidPhysicsAsync/RigidFactoryAsync.h"
#include "ChaosRigidPhysicsAsync/RigidSceneSettingsAsync.h"
#include "RigidPhysics/RigidScene.h"

// 1. 创建异步工厂和场景设置
Chaos::Rigids::Async::FRigidFactoryAsync Factory;
Chaos::Rigids::Async::FRigidSceneSettingsAsync SceneSettings;

// 2. 使用工厂创建物理场景句柄
UE::Physics::FRigidSceneHandle SceneHandle = Factory.CreateScene(SceneSettings);

// 3. (可选) 向场景中添加刚体、几何体、约束等
// ... 使用 Factory 和 SceneHandle 的相关方法 ...

// 4. 运行物理模拟回调（在物理线程/任务中执行）
// 通常通过测试夹具的 RunPTCallback 方法封装
auto SimulateCallback = [&](const UE::Physics::FRigidContextSimRW& Context)
{
    // 在此处执行物理模拟逻辑，Context 提供了对模拟状态的读写访问
    // 例如：应用力、更新约束、查询碰撞结果等
};
// 模拟 10 毫秒，迭代 1 次
Factory.RunPhysicsTask(SimulateCallback, 0.01f, 1);
```

### 进阶用法

结合测试夹具 (`FRigidTestFixture`) 和场景修改器 (`IRigidSceneModifier`) 进行更复杂的测试。这展示了如何在模拟前后插入自定义逻辑。
（来源：`Private/RigidTestFixture.h`, `Private/TestSceneModifier.h`）

```cpp
#include "ChaosRigidPhysicsAsync/RigidFactoryAsync.h"
#include "RigidPhysics/RigidModifier.h"
#include "RigidPhysics/RigidScene.h"

// 定义一个自定义的场景修改器
class FMySceneModifier : public UE::Physics::IRigidSceneModifier
{
public:
    virtual void PreSimulate(const UE::Physics::FRigidContextGameRW& Context) override
    {
        // 在游戏线程准备模拟数据前执行
        // 例如：根据游戏状态设置刚体初始位置
    }

    virtual void PreTick(const UE::Physics::FRigidContextSimRW& Context) override
    {
        // 在物理线程每个模拟子步前执行
        // 例如：施加动态的力或扭矩
    }
};

// 在测试或运行时设置中使用
Chaos::Rigids::Async::FRigidFactoryAsync Factory;
Chaos::Rigids::Async::FRigidSceneSettingsAsync SceneSettings;
UE::Physics::FRigidSceneHandle SceneHandle = Factory.CreateScene(SceneSettings);

// 注册修改器
FMySceneModifier MyModifier;
SceneHandle.SetModifier(&MyModifier);

// 后续的模拟步骤将自动调用 MyModifier 中的回调
```

## Demo 示例

一个最小化的、可编译的示例，演示如何初始化异步物理场景并运行一次模拟。
（注意：此示例省略了错误处理和资源清理，仅展示核心流程）

**MyAsyncPhysicsDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "ChaosRigidPhysicsAsync/RigidFactoryAsync.h"
#include "ChaosRigidPhysicsAsync/RigidSceneSettingsAsync.h"
#include "RigidPhysics/RigidScene.h"

class FMyAsyncPhysicsDemo
{
public:
    void Initialize();
    void SimulateOneStep(float DeltaTime);

private:
    Chaos::Rigids::Async::FRigidFactoryAsync Factory;
    Chaos::Rigids::Async::FRigidSceneSettingsAsync SceneSettings;
    UE::Physics::FRigidSceneHandle SceneHandle;
};
```

**MyAsyncPhysicsDemo.cpp**
```cpp
#include "MyAsyncPhysicsDemo.h"

void FMyAsyncPhysicsDemo::Initialize()
{
    // 使用默认设置创建场景
    SceneHandle = Factory.CreateScene(SceneSettings);
}

void FMyAsyncPhysicsDemo::SimulateOneStep(float DeltaTime)
{
    // 定义一个在物理线程中执行的回调
    auto SimCallback = [this](const UE::Physics::FRigidContextSimRW& Context)
    {
        // 在这里可以访问和修改物理状态
        // 例如，查询场景中的所有刚体并施加重力
        // Context.GetBodies().ForEach([](auto& Body){ Body.AddForce(FVector(0,0,-980.f)); });
    };

    // 提交模拟任务
    Factory.RunPhysicsTask(SimCallback, DeltaTime, 1);
}
```

## 模块依赖

从 `ChaosRigidPhysicsAsync.Build.cs` 和 `ChaosRigidPhysicsAsyncTests.Build.cs` 分析得出。

| 模块 | 用途 |
|---|---|
| `RigidPhysics` | 核心刚体物理抽象层，提供场景、刚体、几何体等基础类型和接口 |
| `Chaos` | Chaos 物理引擎核心库 |
| `ChaosSolverEngine` | Chaos 求解器引擎 |
| `PhysicsCore` | 物理系统核心模块 |
| `AutomationTest` | (仅测试模块) 用于编写自动化测试 |

## 维护状态

### 近期更新

- 2026-04-14 `35e60df1` Migrate UE_LOG to UE_LOGF.
- 2026-04-13 `55407bce` Chaos API: Updated the scene api by splitting Tick into Start/End Tick. Also added WaitOnTick.
- 2026-04-09 `c63a4c15` Chaos API: Updating shape instance to handle materials.
- 2026-04-08 `6d6dbc44` Chaos API: Adding PhysicsService and removing the dependecy of the async plugin on dataflow.
- 2026-03-31 `5f0e43c9` Chaos API: Updating shape instance to handle convex, triangle mesh, and height field geometry types.

### 维护评价

- **状态**: **实验性 (Experimental)**。插件元数据明确标记为 `IsExperimentalVersion: true`，且默认禁用 (`EnabledByDefault: false`)。
- **年龄**: 极新 (约0年)，处于活跃开发初期。
- **推荐度**: **不推荐用于生产环境**。该插件是 Chaos 物理引擎的底层实验性组件，API 和功能可能随时发生破坏性变更。仅建议用于引擎开发、研究或特定的性能测试场景。
- **已知限制**: 作为实验性功能，其稳定性、功能完整性和文档支持均未达到生产就绪标准。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosRigidPhysicsAsync)
- [官方文档]() (无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosRigidPhysicsAsync/Tests)