# ChaosCaching

> Chaos Cache asset support for recording and playing back physics simulations

| 属性 | 值 |
|---|---|
| 中文名 | 物理缓存录制回放 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、序列化资产） |
| 模块 | `ChaosCaching` (Runtime), `ChaosCachingEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-09-01 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosCaching) | |

## 用途

ChaosCaching 是 Chaos 物理系统的**缓存录制与回放框架**。它解决的核心问题是：**如何将实时物理模拟的结果录制下来，并在之后精确地回放**。

典型场景包括：
- **影片级物理效果预览**：物理美工反复调整破坏效果，录制满意的模拟结果后直接回放，避免每次都重新计算
- **Sequencer 时间线集成**：将物理缓存作为动画轨道放入 Sequencer，与镜头、音效等其他轨道精确同步
- **确定性回放**：在打包运行时以确定方式重放物理模拟，保证每次表现一致

该插件采用**适配器模式（Adapter Pattern）**，通过 `FComponentCacheAdapter` 接口为不同组件类型（几何体集合/破坏体、静态网格、骨骼网格等）提供统一的录制/回放抽象，具有良好的可扩展性。

## 使用场景

- 你在做一个建筑破坏效果，需要录制 Chaos 物理模拟并反复回放 → 使用 `AChaosCacheManager` 在 Record 模式下运行一次，然后切换到 Play 模式回放
- 你需要在 Sequencer 中精确控制物理缓存的播放时间 → 将 `AChaosCacheManager` 拖入 Sequencer，使用 `UMovieSceneChaosCacheTrack` 轨道控制
- 你在做电影预渲染，需要物理效果完全确定性回放 → 配合 Sequencer 的 Chaos Cache Track，将物理模拟嵌入镜头序列
- 你需要在蓝图中动态触发不同缓存片段的播放 → 使用 `TriggerComponentByCache` 按缓存名称触发

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start` | 从指定时间开始缓存评估（静态姿态/播放模式） | `AChaosCacheManager` |
| `Stop` | 停止缓存评估 | `AChaosCacheManager` |
| `SetCurrentTime` | 设置当前缓存评估时间 | `AChaosCacheManager` |
| `IsRecording` | 查询当前是否正在录制 | `AChaosCacheManager` |
| `TriggerComponent` | 触发指定组件开始播放/录制 | `AChaosCacheManager` |
| `TriggerComponentByCache` | 通过缓存名称触发播放/录制 | `AChaosCacheManager` |
| `TriggerAll` | 触发所有被观察组件的播放/录制 | `AChaosCacheManager` |
| `FindOrAddObservedComponent` | 查找或添加被观察的组件 | `AChaosCacheManager` |
| `RemoveObservedComponent` | 移除被观察的组件 | `AChaosCacheManager` |
| `ClearObservedComponents` | 清除所有被观察组件 | `AChaosCacheManager` |
| `SetCacheCollection` | 更换缓存集合资产 | `AChaosCacheManager` |
| `ResetAllComponentTransforms` | 重置所有组件到录制时的世界空间变换 | `AChaosCacheManager` |
| `ResetSingleTransform` | 重置指定索引组件到录制时的变换 | `AChaosCacheManager` |
| `EnablePlaybackByCache` | 按缓存名启用/禁用播放 | `AChaosCacheManager` |
| `EnablePlayback` | 按索引启用/禁用播放 | `AChaosCacheManager` |

### 使用示例（蓝图描述）

**场景：录制并回放一个破坏物理模拟**

1. 在场景中放置一个 `AChaosCacheManager` Actor
2. 在 Details 面板中，将 `CacheMode` 设为 `Record`
3. 在 `ObservedComponents` 数组中添加要录制的 `GeometryCollectionComponent`，通过 `SoftComponentRef` 指向目标组件
4. 运行游戏，物理模拟数据被录制到关联的 `UChaosCacheCollection` 资产中
5. 录制完成后停止，将 `CacheMode` 切换为 `Play`
6. 再次运行，缓存管理器将精确回放之前录制的物理模拟

**场景：蓝图中动态触发缓存播放**

1. 获取 `AChaosCacheManager` 的引用
2. 调用 `SetCacheCollection` 设置缓存集合（如果需要切换）
3. 调用 `TriggerComponentByCache`，传入缓存名称 `FName`
4. 被观察的组件将从触发时刻开始播放缓存

## C++ 用法

### 头文件引入

```cpp
#include "Chaos/CacheManagerActor.h"
#include "Chaos/ChaosCache.h"
#include "Chaos/CacheCollection.h"
#include "Chaos/Adapters/CacheAdapter.h"
```

### 基本用法

**以编程方式操控缓存管理器**

```cpp
// 假设已经有一个 AChaosCacheManager* CacheManager 在场景中

// 录制模式：设置并开始录制
CacheManager->SetCacheMode(ECacheMode::Record);
CacheManager->Start();

// ... 运行一段时间后停止录制
CacheManager->Stop();

// 切换到播放模式并回放
CacheManager->SetCacheMode(ECacheMode::Play);
CacheManager->Start(0.0f);  // 从第 0 秒开始播放

// 动态添加要观察的组件
CacheManager->FindOrAddObservedComponent(MyPrimitiveComponent, TEXT("MyCache"));

// 触发特定缓存的播放
CacheManager->TriggerComponentByCache(TEXT("MyCache"));
```

来源：`Public/Chaos/CacheManagerActor.h`

### 进阶用法

**实现自定义缓存适配器**

```cpp
#include "Chaos/Adapters/CacheAdapter.h"

// 自定义适配器，用于支持自定义组件类型
class FMyCustomCacheAdapter : public Chaos::FComponentCacheAdapter
{
public:
    virtual SupportType SupportsComponentClass(UClass* InComponentClass) const override
    {
        if (InComponentClass->IsChildOf(UMyCustomPhysicsComponent::StaticClass()))
        {
            return SupportType::Direct;
        }
        return SupportType::None;
    }

    virtual UClass* GetDesiredClass() const override
    {
        return UMyCustomPhysicsComponent::StaticClass();
    }

    virtual uint8 GetPriority() const override
    {
        return Chaos::FComponentCacheAdapter::UserAdapterPriorityBegin;
    }

    virtual FGuid GetGuid() const override
    {
        // 返回唯一且稳定的 GUID，标识此适配器
        static const FGuid MyGuid(TEXT("..."));
        return MyGuid;
    }

    virtual Chaos::FPhysicsSolver* GetComponentSolver(UPrimitiveComponent* InComponent) const override
    {
        // 返回组件关联的物理求解器
        return nullptr; // 根据实际情况实现
    }

    virtual void SetRestState(UPrimitiveComponent* InComponent, UChaosCache* InCache,
                              const FTransform& InRootTransform, Chaos::FReal InTime) const override
    {
        // 从缓存中读取 InTime 时刻的状态并应用到组件
    }

    virtual void Record_PostSolve(UPrimitiveComponent* InComp, const FTransform& InRootTransform,
                                  FPendingFrameWrite& OutFrame, Chaos::FReal InTime) const override
    {
        // 在物理求解之后，将组件当前状态写入 OutFrame
    }

    virtual void Playback_PreSolve(UPrimitiveComponent* InComponent, UChaosCache* InCache,
                                   Chaos::FReal InTime, FPlaybackTickRecord& TickRecord,
                                   TArray<TPBDRigidParticleHandle<Chaos::FReal, 3>*>& OutUpdatedRigids) const override
    {
        // 在物理求解之前，从缓存中读取 InTime 时刻的状态并推送给物理引擎
    }

    virtual bool ValidForPlayback(UPrimitiveComponent* InComponent, UChaosCache* InCache) const override
    {
        return true;
    }
};

// 自动注册适配器（使用 RAII）
static Chaos::TAutoRegisterCacheAdapter<FMyCustomCacheAdapter> MyAdapterRegistration;
```

来源：`Public/Chaos/Adapters/CacheAdapter.h`

## Demo 示例

**自定义缓存适配器的最小可编译示例：**

```cpp
// MyCacheAdapter.h
#pragma once

#include "Chaos/Adapters/CacheAdapter.h"
#include "Chaos/ChaosCache.h"
#include "Chaos/CacheManagerActor.h"
#include "Components/PrimitiveComponent.h"

class FMyComponentCacheAdapter : public Chaos::FComponentCacheAdapter
{
public:
    virtual SupportType SupportsComponentClass(UClass* InComponentClass) const override
    {
        return SupportType::None; // 根据实际组件类型修改
    }

    virtual UClass* GetDesiredClass() const override
    {
        return UPrimitiveComponent::StaticClass();
    }

    virtual uint8 GetPriority() const override
    {
        return Chaos::FComponentCacheAdapter::UserAdapterPriorityBegin;
    }

    virtual FGuid GetGuid() const override
    {
        return FGuid(TEXT("A1B2C3D4-E5F6-7890-ABCD-EF1234567890"));
    }

    virtual Chaos::FPhysicsSolver* GetComponentSolver(UPrimitiveComponent* InComponent) const override
    {
        return nullptr;
    }

    virtual void SetRestState(UPrimitiveComponent* InComponent, UChaosCache* InCache,
                              const FTransform& InRootTransform, Chaos::FReal InTime) const override
    {
    }

    virtual void Record_PostSolve(UPrimitiveComponent* InComp, const FTransform& InRootTransform,
                                  FPendingFrameWrite& OutFrame, Chaos::FReal InTime) const override
    {
    }

    virtual void Playback_PreSolve(UPrimitiveComponent* InComponent, UChaosCache* InCache,
                                   Chaos::FReal InTime, FPlaybackTickRecord& TickRecord,
                                   TArray<TPBDRigidParticleHandle<Chaos::FReal, 3>*>& OutUpdatedRigids) const override
    {
    }

    virtual bool ValidForPlayback(UPrimitiveComponent* InComponent, UChaosCache* InCache) const override
    {
        return false;
    }
};
```

```cpp
// MyCacheAdapter.cpp
#include "MyCacheAdapter.h"
#include "Chaos/Adapters/CacheAdapter.h"

// 使用模板自动注册，模块加载时自动注册，卸载时自动注销
static Chaos::TAutoRegisterCacheAdapter<FMyComponentCacheAdapter> GMyAdapterRegistration;
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Chaos` | Chaos 物理引擎核心模块 |
| `ChaosSolverEngine` | Chaos 物理求解器引擎 |
| `PhysicsCore` | 物理系统核心接口 |
| `GeometryCollectionEngine` | 几何体集合（破坏体）引擎，用于 GeometryCollection 适配器 |
| `MovieScene` | Sequencer 电影场景核心模块 |
| `MovieSceneTracks` | Sequencer 轨道类型（Float Track 等） |
| `LevelSequence` | 关卡序列支持 |
| `Takes` | Take Recorder 录制支持（.uplugin 中声明的插件依赖） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 截断为 float 的编译警告 |
| 2026-05-12 | `d4c60147` | Geometry collection cache adapter : fix logic issue when dealing with root proxies | 修复几何体集合缓存适配器处理根代理时的逻辑错误 |
| 2026-05-12 | `24eff459` | Chaos : Add trailing data to Chaos Event Relay | 将拖尾数据添加到 Chaos 事件中继 |
| 2026-04-14 | `0d40a411` | [ContentBrowser] New Add Menu Physics Menu | 内容浏览器新增物理菜单（上下文相关改动） |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 日志宏 |

### 维护评价

ChaosCaching 自 2020 年创建以来持续维护，近期（2026 年 5 月）仍有实质性更新，包括 bug 修复和功能增强（如拖尾事件支持）。虽然标记为 **实验性（Experimental）** 且默认不启用，但从最近的 git 历史看，该插件仍在**活跃维护**中，bug 修复较为及时。

**需要注意：**
- 该插件标记为实验性，API 可能在未来版本中发生变化
- `EnabledByDefault=false`，需要在项目设置中手动启用
- 部分早期 API 已标记为废弃（如 `FChaosCacheObjectSpawner`、`ComponentRef`），应使用新的替代方案

**推荐程度**：如果你的项目需要录制和回放 Chaos 物理模拟，这是唯一的选择。虽然标记为实验性，但作为 Epic 官方维护的插件，在中等风险的项目中可以使用。生产环境建议充分测试并关注版本更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosCaching)
- [官方文档]()（暂无）
- [Chaos 物理系统文档](https://docs.unrealengine.com/en-US/InteractiveExperiences/Physics/)