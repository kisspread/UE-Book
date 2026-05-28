# ChaosUserDataPT

> Custom per-particle userdata. Write-only on game thread, read-only on physics thread.

| 属性 | 值 |
|---|---|
| 中文名 | 粒子自定义数据 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ChaosUserDataPT` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-10-04 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosUserDataPT) | |

## 用途

ChaosUserDataPT 解决的是**将游戏逻辑数据关联到 Chaos 物理粒子**的问题。

在物理模拟中，当需要在**逐接触点级别**根据游戏玩法属性影响物理交互时（例如不同材质的物体需要不同的摩擦力、弹力，或者需要为特定粒子附加伤害倍率等），就需要一种机制将游戏线程设置的数据安全地传递给物理线程。

该插件通过 `TUserDataManagerPT` 模板类提供了一套类型安全的方案：

- **游戏线程（GT）**：只能写入/修改/删除粒子的自定义数据（`SetData_GT` / `RemoveData_GT` / `ClearData_GT`）
- **物理线程（PT）**：只能读取数据（`GetData_PT` / `VisitData_PT`）

数据通过 Chaos 的 SimCallback 机制从 GT 单向同步到 PT，避免了多线程竞态问题。该插件本身不提供访问物理线程数据的入口——它将如何从物理线程获取 `TUserDataManagerPT` 实例的选择权交给使用者，以保持灵活性。

## 使用场景

- 你需要为物理粒子附加自定义属性（如材质类型、伤害倍率、团队标识等），并在物理碰撞回调中读取
- 你在实现逐接触点级别的物理效果定制，需要在物理线程访问游戏逻辑数据
- 你需要在 Chaos 求解器的约束/碰撞处理阶段根据自定义数据修改物理行为

## 蓝图用法

该插件不包含任何蓝图可调用节点。`TUserDataManagerPT` 是纯 C++ 模板类，需要在代码中使用。

## C++ 用法

### 头文件引入

```cpp
#include "ChaosUserDataPT.h"
```

### 基本用法

#### 1. 定义你的自定义数据类型

```cpp
// 一个简单的自定义数据结构，关联到每个物理粒子
struct FMyParticleData
{
    float DamageMultiplier = 1.0f;
    int32 TeamId = 0;
    bool bIsFlammable = false;
};
```

#### 2. 创建并注册 TUserDataManagerPT

```cpp
// 在你的物理相关组件中，创建并注册到 Chaos 求解器
#include "ChaosUserDataPT.h"
#include "PhysicsSolver.h"

// 创建配置（可选：是否在 GT 缓存数据用于读回）
Chaos::FUserDataPTConfig Config;
Config.bGetData_GT = true;  // 如果你也需要在 GT 读取数据

// 注册到 Chaos 求解器
Chaos::TUserDataManagerPT<FMyParticleData>* UserDataManager = 
    Solver->CreateAndRegisterSimCallbackObject_External<Chaos::TUserDataManagerPT<FMyParticleData>>(Config);
```

#### 3. 在游戏线程设置/移除数据

```cpp
// === 设置数据（游戏线程）===
void SetParticleUserData(Chaos::TUserDataManagerPT<FMyParticleData>* Manager,
                          const Chaos::FGeometryParticle& Particle)
{
    FMyParticleData Data;
    Data.DamageMultiplier = 2.5f;
    Data.TeamId = 1;
    Data.bIsFlammable = true;

    // 方式一：拷贝设置
    Manager->SetData_GT(Particle, Data);
    
    // 方式二：移动设置（避免拷贝）
    Manager->SetData_GT(Particle, MoveTemp(Data));
}

// === 移除数据（游戏线程）===
void RemoveParticleUserData(Chaos::TUserDataManagerPT<FMyParticleData>* Manager,
                             const Chaos::FGeometryParticle& Particle)
{
    Manager->RemoveData_GT(Particle);
}

// === 清除所有数据（游戏线程）===
void ClearAllParticleData(Chaos::TUserDataManagerPT<FMyParticleData>* Manager)
{
    Manager->ClearData_GT(/* bResize */ true);
}
```

#### 4. 在物理线程读取数据

```cpp
// === 在物理线程的碰撞/约束回调中读取数据 ===
void OnPhysicsContact(Chaos::TUserDataManagerPT<FMyParticleData>* Manager,
                       const Chaos::FGeometryParticleHandle& ParticleHandle)
{
    // 读取单个粒子的数据
    if (const FMyParticleData* Data = Manager->GetData_PT(ParticleHandle))
    {
        // 根据自定义数据修改物理行为
        float EffectiveDamage = BaseDamage * Data->DamageMultiplier;
        bool bShouldIgnite = Data->bIsFlammable;
    }

    // 遍历所有粒子数据
    Manager->VisitData_PT([](Chaos::FUniqueIdx Idx, const FMyParticleData& Data)
    {
        // 对每个粒子的数据执行操作
    });
}
```

#### 5. 通过 FPhysicsObjectHandle 设置数据（便捷重载）

```cpp
// 当你只有 FPhysicsObjectHandle（而不是 FGeometryParticle）时，可以使用便捷重载
void SetDataViaPhysicsObject(Chaos::TUserDataManagerPT<FMyParticleData>* Manager,
                              Chaos::FPhysicsObjectHandle Object)
{
    FMyParticleData Data;
    Data.TeamId = 2;
    
    Manager->SetData_GT(Object, Data);  // 内部会自动查找对应的粒子句柄
    Manager->RemoveData_GT(Object);     // 移除也支持
}
```

### 进阶用法

#### GT 端读回数据

```cpp
// 创建时启用 GT 缓存
Chaos::FUserDataPTConfig Config;
Config.bGetData_GT = true;

auto* Manager = Solver->CreateAndRegisterSimCallbackObject_External<
    Chaos::TUserDataManagerPT<FMyParticleData>>(Config);

// 设置数据后，在 GT 端读回最后设置的值
Manager->SetData_GT(Particle, MyData);

// 在 GT 端获取缓存的数据（适用于增量修改场景）
if (const FMyParticleData* CachedData = Manager->GetData_GT(Particle))
{
    FMyParticleData ModifiedData = *CachedData;
    ModifiedData.DamageMultiplier += 0.5f;  // 增量修改
    Manager->SetData_GT(Particle, ModifiedData);
}
```

#### 配合 Chaos 碰撞回调使用

```cpp
// 在 Chaos 的碰撞事件处理中访问自定义数据
// 典型场景：根据碰撞双方的自定义数据决定反应
void ProcessContactPair(Chaos::TUserDataManagerPT<FMyParticleData>* Manager,
                        const Chaos::FGeometryParticleHandle& ParticleA,
                        const Chaos::FGeometryParticleHandle& ParticleB)
{
    const FMyParticleData* DataA = Manager->GetData_PT(ParticleA);
    const FMyParticleData* DataB = Manager->GetData_PT(ParticleB);

    if (DataA && DataB)
    {
        // 同队伍不产生伤害
        if (DataA->TeamId == DataB->TeamId)
        {
            return;
        }

        // 根据双方数据计算物理响应
        float CombinedMultiplier = DataA->DamageMultiplier * DataB->DamageMultiplier;
        // ...
    }
}
```

## Demo 示例

### MyCustomPhysicsData.h

```cpp
#pragma once

#include "ChaosUserDataPT.h"
#include "Chaos/GeometryParticlesfwd.h"

// 自定义粒子数据结构
struct FParticleGameplayData
{
    float FrictionOverride = -1.0f;  // < 0 表示使用默认值
    float RestitutionOverride = -1.0f;
    int32 TeamId = -1;
    bool bExplosive = false;

    // 必须提供默认构造函数
    FParticleGameplayData() = default;
};

class FMyPhysicsUserDataManager
{
public:
    // 初始化：注册到求解器
    void Initialize(Chaos::FPBDRigidsSolver* Solver);
    
    // 游戏线程接口
    void SetParticleData(const Chaos::FGeometryParticle& Particle, const FParticleGameplayData& Data);
    void RemoveParticleData(const Chaos::FGeometryParticle& Particle);
    void ClearAllData();

private:
    Chaos::TUserDataManagerPT<FParticleGameplayData>* UserDataManager = nullptr;
};
```

### MyCustomPhysicsData.cpp

```cpp
#include "MyCustomPhysicsData.h"
#include "PhysicsSolver.h"

void FMyPhysicsUserDataManager::Initialize(Chaos::FPBDRigidsSolver* Solver)
{
    // 启用 GT 缓存以便增量修改
    Chaos::FUserDataPTConfig Config;
    Config.bGetData_GT = true;

    UserDataManager = Solver->CreateAndRegisterSimCallbackObject_External<
        Chaos::TUserDataManagerPT<FParticleGameplayData>>(Config);
}

void FMyPhysicsUserDataManager::SetParticleData(
    const Chaos::FGeometryParticle& Particle,
    const FParticleGameplayData& Data)
{
    if (UserDataManager)
    {
        UserDataManager->SetData_GT(Particle, Data);
    }
}

void FMyPhysicsUserDataManager::RemoveParticleData(
    const Chaos::FGeometryParticle& Particle)
{
    if (UserDataManager)
    {
        UserDataManager->RemoveData_GT(Particle);
    }
}

void FMyPhysicsUserDataManager::ClearAllData()
{
    if (UserDataManager)
    {
        UserDataManager->ClearData_GT(true);
    }
}
```

## 模块依赖

该插件的公共头文件依赖 Chaos 物理引擎核心类型（`FUniqueIdx`、`FSimCallbackObject`、`FPBDRigidsSolver` 等），这些来自 Chaos 模块。无其他特殊依赖。

| 模块 | 用途 |
|---|---|
| `Chaos` | Chaos 物理引擎核心，提供粒子句柄、求解器、SimCallback 机制 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-09 | `d862fb6a` | TUserDataManagerPT: add GetData_GT for optional game-thread read-back | 新增 GT 端数据读回功能，支持可选的游戏线程缓存读取 |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 全局代码格式化：析构函数改用 = default 语法 |
| 2024-11-10 | `66e9bb39` | Removed all #if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes from the code base | 移除 5.2 版本的 include 顺序兼容宏 |
| 2024-06-11 | `15021cb3` | Buoyancy subsystem only loop over midphases that involve water | 浮力子系统优化（非本插件直接改动） |
| 2024-06-11 | `d9860ed2` | [Backout] - CL34293403 - CIS Compile Error | 回退一个导致编译错误的提交 |

### 维护评价

- **创建时间**：2022-10-04，约 3 年历史
- **实质性更新**：2026-04-09 有重要的功能性更新（新增 `GetData_GT`），说明仍在积极维护
- **代码质量**：有完整的统计计数器声明，API 设计合理，有废弃策略（5.8 中清理旧 API）
- **标记状态**：`IsBetaVersion = true`，仍处于实验阶段
- **推荐度**：✅ **推荐使用**。虽然标记为 Beta，但最近有实质性功能更新，说明 Epic 仍在投入维护。适合需要在 Chaos 物理线程访问自定义数据的高级物理交互场景。注意该插件默认启用但需要通过 C++ 使用，且需要熟悉 Chaos 物理引擎的回调机制。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosUserDataPT)
- 官方文档：无