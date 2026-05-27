# ChaosCaching

> Chaos Cache asset support for recording and playing back physics simulations

| 属性 | 值 |
|---|---|
| 中文名 | 混沌缓存 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `ChaosCaching` (Runtime), `ChaosCachingEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-09-01 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosCaching) | |

## 用途

ChaosCaching 插件解决的核心问题是：**如何将 Chaos 物理模拟的结果录制下来，并在需要时精确回放**。

物理模拟具有不确定性——同一个场景每次运行结果都可能不同。当你需要：

- **可重复的物理效果**：影视制作中，特效师需要一个爆炸场景在每次播放时完全一致
- **离线烘焙物理动画**：将实时物理模拟的结果转为确定性动画序列
- **Sequencer 集成**：在过场动画中精确控制物理对象的时间线
- **事件回放**：不仅回放物体运动，还要回放断裂（Breaking）、碰撞（Collision）、拖尾（Trailing）等物理事件

插件通过一个 **适配器系统（Adapter Pattern）** 实现对不同类型物理组件的支持，包括几何体集合（GeometryCollection）、静态网格（StaticMesh）和骨骼网格（SkeletalMesh）。每个适配器知道如何从特定组件类型提取物理状态并写入缓存，以及如何将缓存数据回写到物理求解器中。

插件默认不启用（`EnabledByDefault=false`），且标记为实验性（`IsExperimentalVersion=true`），说明 Epic 认为该功能尚未完全稳定。

## 使用场景

- 你在做一个建筑拆除模拟，需要**精确回放建筑倒塌过程** → 用 ChaosCaching 录制 GeometryCollection 的破坏过程
- 你在 Sequencer 中制作过场动画，场景中有**物理交互**（如物体滚动、碰撞） → 用 ChaosCacheTrack 在时间线上精确控制物理回放
- 你需要**反复调试**一个物理场景的效果，但每次模拟结果都不同 → 先录制一次，之后反复回放同一份缓存
- 你在做影视特效，需要将物理模拟**导出为确定性数据** → 使用 ChaosCaching 的录制功能，配合 USD 缓存目录导出

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetCacheMode` | 设置缓存模式（静态姿势/播放/录制） | `AChaosCacheManager` |
| `SetStartTime` | Sequencer 专用，设置缓存起始时间 | `AChaosCacheManager` |
| `SetCurrentTime` | 从蓝图设置当前回放时间 | `AChaosCacheManager` |
| `Start` | 启动缓存评估（可指定起始时间） | `AChaosCacheManager` |
| `Stop` | 停止缓存评估 | `AChaosCacheManager` |
| `IsRecording` | 查询是否正在录制 | `AChaosCacheManager` |
| `TriggerComponent` | 触发指定组件开始播放/录制 | `AChaosCacheManager` |
| `TriggerComponentByCache` | 通过缓存名触发组件 | `AChaosCacheManager` |
| `TriggerAll` | 触发所有观察组件开始播放/录制 | `AChaosCacheManager` |
| `FindOrAddObservedComponent` | 添加或更新观察组件 | `AChaosCacheManager` |
| `RemoveObservedComponent` | 移除观察组件 | `AChaosCacheManager` |
| `ClearObservedComponents` | 清除所有观察组件 | `AChaosCacheManager` |
| `ResetAllComponentTransforms` | 重置所有组件到录制时的原始变换 | `AChaosCacheManager` |
| `ResetSingleTransform` | 重置指定索引组件的变换 | `AChaosCacheManager` |
| `EnablePlaybackByCache` | 通过缓存名启用/禁用播放 | `AChaosCacheManager` |
| `EnablePlayback` | 通过索引启用/禁用播放 | `AChaosCacheManager` |
| `SetCacheCollection` | 更换缓存集合资产 | `AChaosCacheManager` |

### 使用示例（蓝图描述）

**录制物理模拟并回放**：

1. 在场景中放置 `AChaosCacheManager` Actor
2. 在 Details 面板中，设置 `CacheMode` 为 `Record`，选择一个 `UChaosCacheCollection` 资产
3. 在 `ObservedComponents` 数组中，通过 `UseComponentPicker` 选择要录制的物理组件
4. 运行游戏，物理模拟过程会被录制到缓存集合中
5. 停止游戏，将 `CacheMode` 切换为 `Play`
6. 再次运行，同样的物理效果会精确回放

**蓝图中动态触发**：

1. 获取场景中的 `AChaosCacheManager` 引用
2. 调用 `TriggerComponent` 或 `TriggerComponentByCache` 开始回放
3. 通过 `SetCurrentTime` 跳转到特定时间点
4. 调用 `Stop` 停止回放

**AChaosCachePlayer**：`AChaosCachePlayer` 是 `AChaosCacheManager` 的子类，行为完全相同，仅提供一个语义上更清晰的"播放器"类型，用于蓝图中表示"只播放"的场景。

## C++ 用法

### 头文件引入

```cpp
#include "Chaos/CacheManagerActor.h"
#include "Chaos/ChaosCache.h"
#include "Chaos/CacheCollection.h"
#include "Chaos/CacheEvents.h"
#include "Chaos/Adapters/CacheAdapter.h"
```

### 基本用法

以下示例展示了如何通过 C++ 访问和操作 Chaos 缓存系统：

```cpp
// 获取场景中的 CacheManager 并控制回放
// 来源: Public/Chaos/CacheManagerActor.h

AChaosCacheManager* CacheManager = /* 从场景或蓝图获取 */;

// 启动缓存评估，从 0 秒开始
CacheManager->Start(0.0f);

// 查询是否正在录制
if (CacheManager->IsRecording())
{
    UE_LOG(LogTemp, Log, TEXT("正在录制物理模拟"));
}

// 设置当前回放时间（用于 Sequencer 外部的时间控制）
CacheManager->SetCurrentTime(5.0f);

// 停止缓存
CacheManager->Stop();

// 动态添加观察组件
UPrimitiveComponent* MyComponent = /* 获取组件 */;
CacheManager->FindOrAddObservedComponent(MyComponent, FName("MyCache"), true);

// 触发特定组件的回放
CacheManager->TriggerComponent(MyComponent);

// 重置所有组件到原始录制位置
CacheManager->ResetAllComponentTransforms();
```

### 进阶用法

```cpp
// 自定义缓存适配器 — 支持自定义物理组件类型
// 来源: Public/Chaos/Adapters/CacheAdapter.h

#include "Chaos/Adapters/CacheAdapter.h"

class FMyCustomComponentCacheAdapter : public Chaos::FComponentCacheAdapter
{
public:
    // 声明支持的组件类型
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

    // 用户自定义适配器应使用高于 UserAdapterPriorityBegin 的优先级
    virtual uint8 GetPriority() const override
    {
        return Chaos::FComponentCacheAdapter::UserAdapterPriorityBegin + 1;
    }

    // 返回唯一 GUID，缓存会嵌入此 ID 用于回放匹配
    virtual FGuid GetGuid() const override
    {
        // 每个适配器类型需要唯一的、稳定的 GUID
        static FGuid MyGuid(TEXT("A1B2C3D4-E5F6-7890-ABCD-EF1234567890"));
        return MyGuid;
    }

    virtual Chaos::FPhysicsSolver* GetComponentSolver(UPrimitiveComponent* InComponent) const override
    {
        // 返回该组件关联的物理求解器
        return nullptr; // 实际实现需要从组件获取求解器
    }

    virtual void SetRestState(UPrimitiveComponent* InComponent, UChaosCache* InCache,
                              const FTransform& InRootTransform, Chaos::FReal InTime) const override
    {
        // 从缓存中设置组件的静止状态
    }

    virtual void Record_PostSolve(UPrimitiveComponent* InComp, const FTransform& InRootTransform,
                                  FPendingFrameWrite& OutFrame, Chaos::FReal InTime) const override
    {
        // 在物理求解后录制数据到缓存帧
    }

    virtual void Playback_PreSolve(UPrimitiveComponent* InComponent, UChaosCache* InCache,
                                   Chaos::FReal InTime, FPlaybackTickRecord& TickRecord,
                                   TArray<TPBDRigidParticleHandle<Chaos::FReal, 3>*>& OutUpdatedRigids) const override
    {
        // 在物理求解前将缓存数据应用到组件
    }

    virtual bool ValidForPlayback(UPrimitiveComponent* InComponent, UChaosCache* InCache) const override
    {
        return InComponent->IsA<UMyCustomPhysicsComponent>();
    }
};

// 使用 TAutoRegisterCacheAdapter 实现自动注册
// 来源: Public/Chaos/Adapters/CacheAdapter.h 中的 TAutoRegisterCacheAdapter 模板
static Chaos::TAutoRegisterCacheAdapter<FMyCustomComponentCacheAdapter> AutoRegisterAdapter;
```

```cpp
// 缓存事件系统 — 用于处理断裂、碰撞等物理事件
// 来源: Public/Chaos/CacheEvents.h

#include "Chaos/CacheEvents.h"

// 创建事件轨道并写入事件
FCacheEventTrack EventTrack(FName("BreakingEvents"), FBreakingEvent::StaticStruct());

FBreakingEvent BreakEvent;
BreakEvent.Index = 0;
BreakEvent.Location = FVector(100, 200, 300);
BreakEvent.Velocity = FVector(500, 0, 0);
EventTrack.PushEvent<FBreakingEvent>(1.5f, BreakEvent);

// 查询时间范围内的事件
TArray<FBreakingEvent*> Events = EventTrack.GetEvents<FBreakingEvent>(1.0f, 2.0f);
for (const FBreakingEvent* Event : Events)
{
    UE_LOG(LogTemp, Log, TEXT("断裂发生在 %s"), *Event->Location.ToString());
}
```

```cpp
// 评估缓存数据
// 来源: Public/Chaos/ChaosCache.h

#include "Chaos/ChaosCache.h"

UChaosCache* Cache = /* 从 UChaosCacheCollection 获取 */;

// 初始化回放会话
FCacheUserToken PlaybackToken = Cache->BeginPlayback();

// 创建评估上下文
FPlaybackTickRecord TickRecord;
FCacheEvaluationContext Context(TickRecord);
Context.bEvaluateTransform = true;
Context.bEvaluateCurves = true;
Context.bEvaluateEvents = true;

// 评估缓存
FCacheEvaluationResult Result = Cache->Evaluate(Context, nullptr);

// 访问评估结果
for (int32 i = 0; i < Result.Transform.Num(); ++i)
{
    FTransform& ParticleTransform = Result.Transform[i];
    // 应用变换到物理粒子...
}

// 结束回放
Cache->EndPlayback(PlaybackToken);
```

## Demo 示例

一个最小示例，展示如何创建缓存管理器并录制/回放 GeometryCollection 组件：

```cpp
// ChaosCacheDemoActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ChaosCacheDemoActor.generated.h"

class AChaosCacheManager;
class UGeometryCollectionComponent;
class UChaosCacheCollection;

UCLASS()
class AChaosCacheDemoActor : public AActor
{
    GENERATED_BODY()

public:
    AChaosCacheDemoActor();

    UPROPERTY(EditAnywhere, Category = "Demo")
    TSubclassOf<AChaosCacheManager> CacheManagerClass;

    UPROPERTY(EditAnywhere, Category = "Demo")
    TObjectPtr<UChaosCacheCollection> CacheCollection;

    UPROPERTY(VisibleAnywhere, Category = "Demo")
    TObjectPtr<UGeometryCollectionComponent> GeometryComponent;

    UPROPERTY(VisibleAnywhere, Category = "Demo")
    TObjectPtr<AChaosCacheManager> CacheManager;

    UFUNCTION(BlueprintCallable, CallInEditor, Category = "Demo")
    void StartRecording();

    UFUNCTION(BlueprintCallable, CallInEditor, Category = "Demo")
    void StopRecording();

    UFUNCTION(BlueprintCallable, CallInEditor, Category = "Demo")
    void StartPlayback();

    UFUNCTION(BlueprintCallable, CallInEditor, Category = "Demo")
    void StopPlayback();
};
```

```cpp
// ChaosCacheDemoActor.cpp
#include "ChaosCacheDemoActor.h"
#include "Chaos/CacheManagerActor.h"
#include "Chaos/CacheCollection.h"
#include "GeometryCollection/GeometryCollectionComponent.h"

AChaosCacheDemoActor::AChaosCacheDemoActor()
{
    GeometryComponent = CreateDefaultSubobject<UGeometryCollectionComponent>(TEXT("GeometryComponent"));
    RootComponent = GeometryComponent;

    CacheManagerClass = AChaosCacheManager::StaticClass();
}

void AChaosCacheDemoActor::StartRecording()
{
    if (!CacheManager && CacheManagerClass)
    {
        FActorSpawnParameters SpawnParams;
        SpawnParams.Owner = this;
        CacheManager = GetWorld()->SpawnActor<AChaosCacheManager>(CacheManagerClass, SpawnParams);
    }

    if (CacheManager)
    {
        CacheManager->SetCacheCollection(CacheCollection);
        CacheManager->SetCacheMode(ECacheMode::Record);

        // 将 GeometryCollection 组件添加为观察目标
        CacheManager->FindOrAddObservedComponent(
            GeometryComponent, FName("DemoGC"), true);

        CacheManager->Start(0.0f);
    }
}

void AChaosCacheDemoActor::StopRecording()
{
    if (CacheManager)
    {
        CacheManager->Stop();
    }
}

void AChaosCacheDemoActor::StartPlayback()
{
    if (CacheManager)
    {
        CacheManager->SetCacheMode(ECacheMode::Play);
        CacheManager->Start(0.0f);
    }
}

void AChaosCacheDemoActor::StopPlayback()
{
    if (CacheManager)
    {
        CacheManager->Stop();
        CacheManager->ResetAllComponentTransforms();
    }
}
```

## 模块依赖

基于源码中的依赖关系分析：

| 模块 | 用途 |
|---|---|
| `Chaos` | Chaos 物理求解器核心（粒子、刚体、求解器事件） |
| `ChaosSolverEngine` | 物理求解器引擎接口 |
| `GeometryCollectionEngine` | GeometryCollection 组件支持（破坏模拟） |
| `MovieSceneTracks` | Sequencer 轨道集成 |
| `MovieScene` | Sequencer 核心框架 |

插件依赖：**Takes**（用于 Take Recorder 录制支持）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 到 float 截断的编译警告 |
| 2026-05-12 | `d4c60147` | Geometry collection cache adapter : fix logic issue when dealing with root proxies | 修复几何集合缓存适配器处理根代理时的逻辑错误 |
| 2026-05-12 | `24eff459` | Chaos : Add trailing data to Chaos Event Relay | 向 Chaos 事件中继添加拖尾数据支持 |
| 2026-04-14 | `0d40a411` | [ContentBrowser] New Add Menu Physics Menu | 内容浏览器新增物理菜单分类 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移到 UE_LOGF 日志宏 |

### 维护评价

- **创建时间**：2020 年 9 月，约 6 年历史
- **实验性状态**：仍标记为 `IsExperimentalVersion=true`，且 `EnabledByDefault=false`，6 年未毕业为正式功能
- **最近更新**：2026 年 5 月仍有活跃更新，包括 bug 修复和功能增强（trailing data 支持），说明团队仍在使用和维护
- **代码质量**：存在大量 `UE_DEPRECATED` 标记（5.1、5.3、5.4、5.5、5.6），说明 API 经历了多次重构，旧接口仍在兼容
- **功能完整性**：核心录制/回放功能可用，适配器系统设计良好，支持 Sequencer 集成

**评价**：虽然标记为实验性，但该插件在过去 6 年持续收到更新，功能较为完善。适用于需要精确物理回放的影视/过场动画项目。不建议用于对稳定性要求极高的生产环境，且注意 API 可能在未来版本继续变动。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosCaching)
- [适配器源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosCaching/Source/ChaosCaching/Public/Chaos/Adapters)
- [Sequencer 集成源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosCaching/Source/ChaosCaching/Public/Chaos/Sequencer)