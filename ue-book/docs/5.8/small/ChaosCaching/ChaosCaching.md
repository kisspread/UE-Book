# Chaos Caching

> Chaos Cache asset support for recording and playing back physics simulations

| 属性 | 值 |
|---|---|
| 中文名 | 物理缓存 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `ChaosCaching` (Runtime), `ChaosCachingEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-09-01 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosCaching) | |

## 用途

ChaosCaching 插件提供了一套完整的 Chaos 物理模拟录制与回放系统。它解决的核心问题是：**如何将实时物理模拟的结果保存为可复用的资产，并在需要时精确回放**。

该插件通过适配器模式（Adapter Pattern）支持多种物理组件类型（GeometryCollection、StaticMesh、SkeletalMesh），能够录制破碎、碰撞、拖尾等物理事件，并通过 Sequencer 集成实现与动画系统的同步播放。这使得开发者可以：

- 将昂贵的物理模拟预计算为缓存，避免运行时重复计算
- 在 Sequencer 中精确控制物理动画的时间线
- 录制物理事件（破碎、碰撞）并在静态姿态模式下回放
- 通过 USD 导出路径支持离线缓存

## 使用场景

- 你需要制作电影级破碎效果，但不想每次都重新模拟 → 用 ChaosCaching 录制一次后反复回放
- 你在 Sequencer 中需要物理模拟与镜头同步 → 用 MovieSceneChaosCacheTrack 控制物理时间线
- 你需要在特定时间点触发物理效果（如爆炸）→ 使用 Triggered 启动模式
- 你要让物理碎片按预设路径运动，同时保留碰撞响应 → 使用 Static Pose 模式配合事件回放

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start` | 从指定时间开始缓存评估（静态姿态或播放模式） | `AChaosCacheManager` |
| `Stop` | 停止缓存评估 | `AChaosCacheManager` |
| `IsRecording` | 检查缓存管理器是否正在录制 | `AChaosCacheManager` |
| `SetCurrentTime` | 设置当前评估时间（蓝图调用） | `AChaosCacheManager` |
| `TriggerComponent` | 触发指定组件开始播放或录制 | `AChaosCacheManager` |
| `TriggerComponentByCache` | 通过缓存名称触发组件 | `AChaosCacheManager` |
| `TriggerAll` | 触发所有被观察组件的录制或播放 | `AChaosCacheManager` |
| `FindOrAddObservedComponent` | 查找或添加组件到观察列表 | `AChaosCacheManager` |
| `RemoveObservedComponent` | 从观察列表移除组件 | `AChaosCacheManager` |
| `ClearObservedComponents` | 清空所有观察组件 | `AChaosCacheManager` |
| `ResetAllComponentTransforms` | 重置所有组件到录制时的世界空间变换 | `AChaosCacheManager` |
| `ResetSingleTransform` | 重置指定索引组件的变换 | `AChaosCacheManager` |
| `SetCacheCollection` | 更改缓存集合资产 | `AChaosCacheManager` |

### 使用示例（蓝图描述）

**录制物理模拟：**

1. 在场景中放置 `AChaosCacheManager`（或子类 `AChaosCachePlayer`）
2. 在 Details 面板中：
   - 创建或指定 `CacheCollection` 资产
   - 设置 `CacheMode` 为 `Record`
   - 设置 `StartMode` 为 `Timed`（自动开始）或 `Triggered`（手动触发）
   - 在 `ObservedComponents` 数组中添加要录制的物理组件引用
3. 运行游戏，物理模拟将自动录制到缓存资产中

**回放缓存：**

1. 将 `CacheMode` 切换为 `Play`
2. 设置 `StartTime` 控制回放起始时间
3. 调用 `Start()` 节点开始回放
4. 可通过 `TriggerComponent` 控制单个组件的回放

**Sequencer 集成：**

1. 在 Sequencer 中添加 Chaos Cache Track
2. 添加 Section 并指定 `CacheCollection`
3. 通过关键帧动画控制 `StartTime` 属性

## C++ 用法

### 头文件引入

```cpp
#include "Chaos/CacheManagerActor.h"
#include "Chaos/ChaosCache.h"
#include "Chaos/CacheCollection.h"
```

### 基本用法

```cpp
// 创建缓存管理器并配置录制
AChaosCacheManager* CacheManager = GetWorld()->SpawnActor<AChaosCacheManager>();

// 设置缓存集合
UChaosCacheCollection* CacheCollection = NewObject<UChaosCacheCollection>();
CacheManager->CacheCollection = CacheCollection;

// 配置录制模式
CacheManager->CacheMode = ECacheMode::Record;
CacheManager->StartMode = EStartMode::Timed;

// 添加要录制的组件
CacheManager->FindOrAddObservedComponent(MyPhysicsComponent, TEXT("MyCache"));

// 开始录制
CacheManager->Start(0.0f);

// 检查录制状态
bool bRecording = CacheManager->IsRecording();
```

### 进阶用法

```cpp
// 切换到播放模式并从特定时间回放
CacheManager->CacheMode = ECacheMode::Play;
CacheManager->StartTime = 2.5f;
CacheManager->Start(2.5f);

// 手动触发组件
CacheManager->TriggerComponent(MyPhysicsComponent);
CacheManager->TriggerComponentByCache(FName("MyCache"));

// 动态管理观察组件
CacheManager->RemoveObservedComponent(OldComponent);
CacheManager->FindOrAddObservedComponent(NewComponent, TEXT("NewCache"), true);

// 重置组件变换
CacheManager->ResetAllComponentTransforms();
CacheManager->ResetSingleTransform(0);

// 自定义适配器注册（扩展支持的组件类型）
class FMyCustomCacheAdapter : public Chaos::FComponentCacheAdapter
{
public:
    virtual SupportType SupportsComponentClass(UClass* InComponentClass) const override;
    virtual UClass* GetDesiredClass() const override;
    virtual uint8 GetPriority() const override;
    virtual FGuid GetGuid() const override;
    virtual Chaos::FPhysicsSolver* GetComponentSolver(UPrimitiveComponent* InComponent) const override;
    virtual void SetRestState(UPrimitiveComponent* InComponent, UChaosCache* InCache, 
                              const FTransform& InRootTransform, Chaos::FReal InTime) const override;
    virtual void Record_PostSolve(UPrimitiveComponent* InComp, const FTransform& InRootTransform,
                                  FPendingFrameWrite& OutFrame, Chaos::FReal InTime) const override;
    virtual void Playback_PreSolve(UPrimitiveComponent* InComponent, UChaosCache* InCache,
                                   Chaos::FReal InTime, FPlaybackTickRecord& TickRecord,
                                   TArray<TPBDRigidParticleHandle<Chaos::FReal, 3>*>& OutUpdatedRigids) const override;
    virtual bool ValidForPlayback(UPrimitiveComponent* InComponent, UChaosCache* InCache) const override;
};

// 注册自定义适配器（通常在模块启动时）
Chaos::RegisterAdapter(new FMyCustomCacheAdapter());
```

## Demo 示例

### 最小可编译示例

```cpp
// MyCacheTestActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Chaos/CacheManagerActor.h"
#include "MyCacheTestActor.generated.h"

UCLASS()
class AMyCacheTestActor : public AActor
{
    GENERATED_BODY()

public:
    AMyCacheTestActor();

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Cache")
    TObjectPtr<UChaosCacheCollection> CacheCollection;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Cache")
    TObjectPtr<UPrimitiveComponent> PhysicsComponent;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Cache")
    float RecordingDuration = 5.0f;

    UFUNCTION(BlueprintCallable, Category = "Cache")
    void StartRecording();

    UFUNCTION(BlueprintCallable, Category = "Cache")
    void StopRecordingAndPlay();

private:
    UPROPERTY()
    TObjectPtr<AChaosCacheManager> CacheManager;

    float RecordingStartTime;
};

// MyCacheTestActor.cpp
#include "MyCacheTestActor.h"
#include "Components/StaticMeshComponent.h"

AMyCacheTestActor::AMyCacheTestActor()
{
    PrimaryActorTick.bCanEverTick = true;
    PhysicsComponent = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PhysicsMesh"));
    RootComponent = PhysicsComponent;
}

void AMyCacheTestActor::StartRecording()
{
    if (!CacheCollection)
    {
        CacheCollection = NewObject<UChaosCacheCollection>(this);
    }

    // Spawn cache manager if needed
    if (!CacheManager)
    {
        FActorSpawnParameters SpawnParams;
        SpawnParams.Owner = this;
        CacheManager = GetWorld()->SpawnActor<AChaosCacheManager>(AChaosCacheManager::StaticClass(), 
                                                                   GetActorTransform(), SpawnParams);
    }

    // Configure for recording
    CacheManager->CacheCollection = CacheCollection;
    CacheManager->CacheMode = ECacheMode::Record;
    CacheManager->StartMode = EStartMode::Triggered;
    
    // Add component to observe
    if (PhysicsComponent)
    {
        CacheManager->FindOrAddObservedComponent(PhysicsComponent, TEXT("MainPhysics"));
    }

    // Start recording
    CacheManager->TriggerAll();
    RecordingStartTime = GetWorld()->GetTimeSeconds();
    
    UE_LOG(LogTemp, Log, TEXT("Cache recording started"));
}

void AMyCacheTestActor::StopRecordingAndPlay()
{
    if (!CacheManager || !CacheCollection)
    {
        return;
    }

    // Switch to playback mode
    CacheManager->CacheMode = ECacheMode::Play;
    CacheManager->StartTime = 0.0f;
    
    // Reconfigure observed components for playback
    CacheManager->FindOrAddObservedComponent(PhysicsComponent, TEXT("MainPhysics"));
    
    // Start playback
    CacheManager->TriggerAll();
    
    UE_LOG(LogTemp, Log, TEXT("Cache playback started"));
}
```

## 模块依赖

从源码分析，该插件依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `Chaos` | Chaos 物理求解器核心 |
| `ChaosSolverEngine` | 物理求解器引擎接口 |
| `GeometryCollectionEngine` | GeometryCollection 组件支持 |
| `GeometryCollectionSimulationCore` | 几何集合模拟核心 |
| `MovieSceneTracks` | Sequencer 轨道支持 |
| `LevelSequence` | 关卡序列集成 |
| `USDExporter` | USD 缓存导出（可选） |

**插件依赖**：`Takes`（Take Recorder 集成）

**模块依赖声明**（Build.cs 中应包含）：
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Chaos",
    "ChaosSolverEngine",
    "GeometryCollectionEngine"
});

PrivateDependencyModuleNames.AddRange(new string[] {
    "MovieSceneTracks",
    "LevelSequence"
});
```

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下的精度警告 |
| 2026-05-12 | `d4c60147` | Geometry collection cache adapter : fix logic issue when dealing with root proxies | 修复几何集合缓存适配器处理根代理的逻辑问题 |
| 2026-05-12 | `24eff459` | Chaos : Add trailing data to Chaos Event Relay | 为 Chaos 事件中继添加拖尾数据支持 |
| 2026-04-14 | `0d40a411` | [ContentBrowser] New Add Menu Physics Menu | 内容浏览器新增物理菜单分类 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新格式 |

### 维护评价

**活跃维护**：该插件仍在积极维护中，最近一次更新（2026-05-13）距离当前时间不到 1 个月。

**优势**：
- 持续修复 bug 和改进功能（几何集合适配器逻辑修复、事件系统增强）
- 适配器模式设计良好，易于扩展新组件类型
- Sequencer 集成完整，支持动画时间线控制
- 支持多种物理事件类型（破碎、碰撞、拖尾）

**已知限制**：
- 标记为实验性（`IsExperimentalVersion=true`），API 可能变更
- 需要手动启用（`EnabledByDefault=false`）
- 部分功能仍在开发中（如 USD 缓存导出）

**推荐**：✅ 推荐使用。尽管标记为实验性，但代码质量高、维护活跃、功能完整。适合需要物理模拟缓存、Sequencer 物理动画或运行时物理优化的项目。注意 API 可能在未来版本中变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosCaching)
- [官方文档]()（暂无）
- [测试用例]()（待确认）