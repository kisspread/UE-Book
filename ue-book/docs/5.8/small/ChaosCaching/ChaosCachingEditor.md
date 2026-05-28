# ChaosCaching

> Chaos Cache asset support for recording and playing back physics simulations

| 属性 | 值 |
|---|---|
| 中文名 | 混沌缓存 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产类型定义） |
| 模块 | `ChaosCaching` (Runtime), `ChaosCachingEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-09-01 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosCaching) | |

## 用途

ChaosCaching 插件的核心功能是**录制并回放 Unreal Engine 的 Chaos 物理模拟结果**。它解决了物理模拟具有不确定性和高计算成本的问题。通过缓存（记录）物理对象（如刚体、几何体）在一段时间内的位置、旋转、状态等数据，允许用户在后续像播放动画一样精确地重放整个物理过程，确保结果完全一致且性能开销远低于实时模拟。

该插件存在是为需要高度可控、可重复物理效果的场景（如过场动画、游戏内电影）提供支持，并与 Sequencer 和 Take Recorder 深度集成，是电影级物理内容制作的关键工具。

## 使用场景

- **制作可控的物理破坏动画**：你需要一个建筑在特定时间点、以特定方式坍塌，并在 Sequencer 中精确编辑坍塌的时间点和速度。
- **游戏中的预设物理表现**：在游戏过程中，需要触发一个复杂且结果确定的物理连锁反应（如多米诺骨牌、精密的机关）。
- **过场动画中的物理集成**：在电影级过场动画中，角色需要与环境进行物理交互，但你需要确保每次播放的结果都与预览时完全一致。
- **物理测试与迭代**：在编辑器中录制一次物理模拟，然后反复回放观察，而无需每次都重新运行昂贵的物理计算。

## 蓝图用法

此插件的核心蓝图 API 位于 `ChaosCaching` 运行时模块中，用于控制缓存的录制和回放。`ChaosCachingEditor` 模块主要提供编辑器内的资产创建和 Sequencer 集成功能。

### 核心节点

由于提供的源码主要为编辑器模块，典型的 Runtime 蓝图节点（如开始/停止录制）未直接列出。但基于编辑器集成，常见的操作包括：

| 操作 | 说明 |
|---|---|
| **创建缓存管理器** | 在内容浏览器中右键创建 `AChaosCacheManager` Actor。 |
| **分配缓存集合** | 在缓存管理器的细节面板中，设置 `ChaosCacheCollection` 资产来管理缓存数据。 |
| **使用 Sequencer 轨道** | 在 Sequencer 中为缓存管理器添加 `ChaosCache Track`，在轨道上添加关键帧来控制缓存的录制和播放时机。 |
| **使用 Take Recorder 源** | 在 Take Recorder 面板中添加 “Chaos Cache” 源，选择一个缓存管理器，录制其物理状态到 Sequencer 片段中。 |

## C++ 用法

### 头文件引入

要使用此插件的运行时功能，你需要依赖 `ChaosCaching` 模块。编辑器功能则依赖 `ChaosCachingEditor` 模块。

```cpp
// 包含核心运行时接口
#include "Chaos/ChaosCacheManager.h"
#include "Chaos/ChaosCacheCollection.h"

// 包含编辑器功能 (仅在编辑器模块中使用)
#include "Chaos/ChaosCachingEditorPlugin.h"
```

### 基本用法 (运行时)

```cpp
// 假设你已获得一个 AChaosCacheManager 指针
AChaosCacheManager* CacheManager = ...;

// 1. 确保缓存管理器指向一个有效的缓存集合
UChaosCacheCollection* CacheCollection = LoadObject<UChaosCacheCollection>(nullptr, TEXT("/Game/MyCacheCollection"));
CacheManager->SetCacheCollection(CacheCollection);

// 2. 控制录制 (通常通过 Sequencer 关键帧或蓝图)
// CacheManager->StartRecording(); // 具体函数名需参考运行时头文件
// CacheManager->StopRecording();

// 3. 控制回放
// CacheManager->StartPlayback();
```
*注意：以上为推断的伪代码，具体 API 需查阅 `AChaosCacheManager` 的公开方法。*

### 进阶用法 (编辑器扩展)

编辑器模块提供了自定义细节面板、资产工厂和 Sequencer 轨道编辑器。

```cpp
// 注册一个自定义的细节面板，用于展示 AChaosCacheManager
FPropertyEditorModule& PropertyModule = FModuleManager::LoadModuleChecked<FPropertyEditorModule>("PropertyEditor");
PropertyModule.RegisterCustomClassLayout(
    AChaosCacheManager::StaticClass()->GetFName(),
    FOnGetDetailCustomizationInstance::CreateStatic(&FCacheManagerDetails::MakeInstance)
);

// 在 Sequencer 中创建 Chaos Cache 轨道
TSharedRef<ISequencerTrackEditor> TrackEditor = FChaosCacheTrackEditor::CreateTrackEditor(MySequencer.ToSharedRef());
```

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何在编辑器中编程式地创建一个 `ChaosCacheManager` 并关联缓存集合。

```cpp
// MyChaosCacheDemo.h
#pragma once
#include "CoreMinimal.h"

class FMyChaosCacheDemo
{
public:
    static AChaosCacheManager* CreateDemoCacheManager(UWorld* World);
};
```

```cpp
// MyChaosCacheDemo.cpp
#include "MyChaosCacheDemo.h"
#include "Chaos/ChaosCacheManager.h"
#include "Chaos/ChaosCacheCollection.h"
#include "Engine/World.h"

AChaosCacheManager* FMyChaosCacheDemo::CreateDemoCacheManager(UWorld* World)
{
    if (!World) return nullptr;

    // 1. 加载或创建缓存集合资产
    UChaosCacheCollection* CacheCollection = LoadObject<UChaosCacheCollection>(
        nullptr,
        TEXT("/Game/DemoAssets/MyPhysicsCacheCollection")
    );
    if (!CacheCollection)
    {
        UE_LOG(LogTemp, Warning, TEXT("Failed to load ChaosCacheCollection asset."));
        return nullptr;
    }

    // 2. 在场景中生成缓存管理器
    FActorSpawnParameters SpawnParams;
    AChaosCacheManager* CacheManager = World->SpawnActor<AChaosCacheManager>(
        AChaosCacheManager::StaticClass(),
        FVector::ZeroVector,
        FRotator::ZeroRotator,
        SpawnParams
    );

    if (CacheManager)
    {
        // 3. 将缓存集合分配给管理器
        // 假设 AChaosCacheManager 有一个公开方法或属性来设置集合
        // CacheManager->SetCacheCollection(CacheCollection);
        UE_LOG(LogTemp, Log, TEXT("Successfully created ChaosCacheManager: %s"), *CacheManager->GetName());
    }

    return CacheManager;
}
```
*请注意：此示例中部分接口（如 `SetCacheCollection`）为推测性 API，实际使用时应参考 `AChaosCacheManager` 的具体公开接口。*

## 模块依赖

此插件依赖于 Unreal Engine 的 **Takes** 插件。

| 模块 | 用途 |
|---|---|
| `Takes` | 提供 Take Recorder 集成的底层框架，是录制功能的基础依赖。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量截断为浮点数的编译警告。 |
| 2026-05-12 | `d4c60147` | Geometry collection cache adapter : fix logic issue when dealing with root proxies | 修复几何体集合缓存适配器处理根代理时的逻辑问题。 |
| 2026-05-12 | `24eff459` | Chaos : Add trailing data to Chaos Event Relay | 为 Chaos 事件中继添加尾部数据。 |
| 2026-04-14 | `0d40a411` | [ContentBrowser] New Add Menu Physics Menu | 在内容浏览器的新建菜单中添加物理分类。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移到 UE_LOGF。 |

### 维护评价

ChaosCaching 插件创建于 2020 年，属于 Chaos 物理系统早期的重要配套工具。从 Git 记录看，截至 **2026 年 5 月**仍有持续的维护性更新和 Bug 修复，表明它**仍在活跃维护中**。更新内容主要包括编译兼容性修复、底层逻辑调整以及编辑器体验优化。

**综合评价**：
- **状态**：活跃维护中，但仍是实验性插件 (`IsExperimentalVersion=true`)，API 可能发生变化。
- **推荐**：**推荐使用**。对于需要确定性物理回放、通过 Sequencer 或 Take Recorder 集成复杂物理效果的项目，这是一个强大且必要的工具。虽然标记为实验性，但其功能成熟且有持续维护。使用者应做好在引擎版本升级时进行适配的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosCaching)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosCaching/Tests) *(如果存在，路径通常为 `/Tests`)*