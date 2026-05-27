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

ChaosCaching 插件的核心功能是**记录和回放 Chaos 物理系统的模拟结果**。它通过将 Chaos 引擎（UE5 的物理模拟系统）在运行时产生的状态变化（如刚体位置、旋转、破碎状态等）捕获并存储到“混沌缓存”资产中，从而允许开发者在不重新进行复杂物理计算的情况下，在编辑器或运行时精确地重放这些物理动画。

它解决的主要问题包括：
1.  **预览与迭代**：在编辑器中提前录制并查看复杂的物理动画（如大规模破坏、布料、流体），避免每次都需要触发真实的物理模拟。
2.  **性能优化**：将昂贵的实时物理模拟结果缓存下来，在运行时播放缓存动画，节省计算资源。
3.  **确定性与复现**：确保物理动画的表现每次都完全一致，用于录制游戏内的过场动画或重现 bug。
4.  **与 Sequencer 和 Take Recorder 集成**：提供专门的轨道和录制源，以便在电影管线和实时录制工具中无缝使用物理动画。

## 使用场景

-   你正在制作一个包含复杂建筑破坏的关卡 → 使用 ChaosCaching 预先录制破坏序列，然后通过 Sequencer 编辑其播放时间、速度，并组合其他动画。
-   你的游戏需要播放一段固定的、由物理引擎生成的特效动画（如碎石滑落） → 将其录制为缓存资产，在运行时直接播放，避免实时计算。
-   你需要使用 Take Recorder 录制游戏实机演示，其中包含物理互动 → 将 `AChaosCacheManager` 作为录制源加入，精确记录物理状态变化。

## 蓝图用法

在运行时（Runtime）模块中，主要通过 `AChaosCacheManager` Actor 来管理和播放缓存。以下是核心功能节点：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Cache Mode` | 设置缓存管理器的模式（录制或播放） | `AChaosCacheManager` |
| `Get Cache Mode` | 获取当前的缓存模式 | `AChaosCacheManager` |
| `Start Recording` | 开始录制物理模拟到指定的缓存集合 | `AChaosCacheManager` |
| `Stop Recording` | 停止当前的录制 | `AChaosCacheManager` |
| `Start Playback` | 开始回放缓存中的物理动画 | `AChaosCacheManager` |
| `Stop Playback` | 停止当前的回放 | `AChaosCacheManager` |
| `Set Cache Collection` | 动态设置要使用的 `UChaosCacheCollection` 资产 | `AChaosCacheManager` |
| `Reset Cache System` | 重置缓存系统状态 | `AChaosCacheManager` |
| `Force Update` | 强制更新缓存管理器的状态（通常用于调试） | `AChaosCacheManager` |

### 使用示例（蓝图描述）

1.  **录制流程**：
    -   在场景中放置一个 `AChaosCacheManager` Actor。
    -   在其细节面板或通过蓝图，将其 `Cache Mode` 设置为 `Recording`。
    -   指定一个 `ChaosCacheCollection` 资产用于存储录制数据。
    -   在游戏开始时，调用 `Start Recording` 节点。
    -   触发你想要录制的物理事件（如爆炸）。
    -   在事件结束后调用 `Stop Recording`。
    -   保存关卡后，录制的数据将存在于指定的 `ChaosCacheCollection` 资产中。

2.  **播放流程**：
    -   将同一个 `AChaosCacheManager` Actor 的 `Cache Mode` 设置为 `Playback`。
    -   确保它引用了包含录制数据的 `ChaosCacheCollection`。
    -   调用 `Start Playback` 节点，物理对象将按照录制时的状态进行回放。

## C++ 用法

在 C++ 中，`ChaosCaching` Runtime 模块提供了核心的缓存管理类。`ChaosCachingEditor` Editor 模块则负责编辑器集成（如资产工厂、细节面板自定义、Sequencer 轨道等）。

### 头文件引入

```cpp
// 要使用 ChaosCacheManager 和相关缓存类
#include "Chaos/ChaosCacheManager.h"

// 要使用缓存集合资产
#include "Chaos/ChaosCacheCollection.h"

// 要在编辑器中创建或操作缓存集合资产
#include "Chaos/CacheCollectionFactory.h"
```

### 基本用法 (运行时录制与播放)

以下代码展示了如何以编程方式控制 `AChaosCacheManager`。

```cpp
// 假设你已经在场景中获取了 AChaosCacheManager* 的指针 CacheManager
// 以及一个已经加载的 UChaosCacheCollection* 缓存集合资产 CacheCollectionAsset

// 1. 设置缓存集合
CacheManager->SetCacheCollection(CacheCollectionAsset);

// 2. 切换到录制模式并开始录制
CacheManager->SetCacheMode(ECacheMode::Record);
CacheManager->StartRecording();

// ... 在此处触发物理模拟（例如，应用冲量、生成爆炸等）...
// 录制过程会自动进行

// 3. 停止录制
CacheManager->StopRecording();

// 4. （之后）切换到播放模式并开始回放
CacheManager->SetCacheMode(ECacheMode::Playback);
CacheManager->StartPlayback();

// 5. 停止回放
CacheManager->StopPlayback();
```

### 进阶用法 (编辑器集成与资产创建)

以下示例演示如何在编辑器工具中创建一个新的 `UChaosCacheCollection` 资产。这通常由编辑器模块（如 `ChaosCachingEditor`）中的命令或菜单触发。

```cpp
// 引入编辑器模块的头文件（如果你的模块依赖 ChaosCachingEditor）
#include "Chaos/CacheCollectionFactory.h"

// 在某个编辑器工具函数中
void CreateNewCacheCollectionAsset()
{
    UCacheCollectionFactory* Factory = NewObject<UCacheCollectionFactory>();
    if (Factory)
    {
        // 调用工厂方法，它会弹出“另存为”对话框
        // 并创建一个新的 UChaosCacheCollection 资产文件
        UObject* NewAsset = Factory->FactoryCreateNew(
            UChaosCacheCollection::StaticClass(),
            GetTransientPackage(), // 父包，实际会被对话框选择的路径覆盖
            NAME_None,             // 资产名，也会被对话框覆盖
            RF_NoFlags,            // 对象标志
            nullptr,               // 上下文
            GWarn                  // 反馈上下文
        );

        if (NewAsset)
        {
            // 新资产已创建并保存，可以在 Content Browser 中看到
            UE_LOG(LogTemp, Log, TEXT("Created new Chaos Cache Collection asset: %s"), *NewAsset->GetName());
        }
    }
}
```

## Demo 示例

一个最小的可编译示例，展示如何在一个自定义 Actor 中声明并使用 `AChaosCacheManager` 组件。

**MyCachingActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Chaos/ChaosCacheManager.h" // 包含核心类头文件
#include "MyCachingActor.generated.h"

UCLASS()
class MYPROJECT_API AMyCachingActor : public AActor
{
    GENERATED_BODY()

public:
    AMyCachingActor();

    // 蓝图可调用的函数，用于控制录制
    UFUNCTION(BlueprintCallable, Category = "Caching")
    void StartCachingSimulation();

    UFUNCTION(BlueprintCallable, Category = "Caching")
    void StopCachingSimulation();

    // 蓝图可调用的函数，用于控制回放
    UFUNCTION(BlueprintCallable, Category = "Caching")
    void PlayCachedSimulation();

    UFUNCTION(BlueprintCallable, Category = "Caching")
    void StopCachedPlayback();

protected:
    // Chaos Cache Manager 组件
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components", meta = (AllowPrivateAccess = "true"))
    TObjectPtr<AChaosCacheManager> CacheManager;

    // 要使用的缓存集合资产（可在蓝图编辑器中指定）
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Caching")
    TObjectPtr<UChaosCacheCollection> CacheCollectionAsset;
};
```

**MyCachingActor.cpp**
```cpp
#include "MyCachingActor.h"

AMyCachingActor::AMyCachingActor()
{
    // 创建并附加 Chaos Cache Manager 组件
    // 注意：在构造函数中创建组件需要使用 CreateDefaultSubobject
    CacheManager = CreateDefaultSubobject<AChaosCacheManager>(TEXT("ChaosCacheManager"));
    RootComponent = CacheManager; // 使其成为根组件，以便它存在于场景中
}

void AMyCachingActor::StartCachingSimulation()
{
    if (CacheManager && CacheCollectionAsset)
    {
        // 配置
        CacheManager->SetCacheCollection(CacheCollectionAsset);
        CacheManager->SetCacheMode(ECacheMode::Record);
        CacheManager->StartRecording();
    }
}

void AMyCachingActor::StopCachingSimulation()
{
    if (CacheManager)
    {
        CacheManager->StopRecording();
    }
}

void AMyCachingActor::PlayCachedSimulation()
{
    if (CacheManager && CacheCollectionAsset)
    {
        // 确保使用正确的资产并切换模式
        CacheManager->SetCacheCollection(CacheCollectionAsset);
        CacheManager->SetCacheMode(ECacheMode::Playback);
        CacheManager->StartPlayback();
    }
}

void AMyCachingActor::StopCachedPlayback()
{
    if (CacheManager)
    {
        CacheManager->StopPlayback();
    }
}
```

## 模块依赖

要使用此插件，你的模块需要依赖以下（非标准的）模块：

| 模块 | 用途 |
|---|---|
| `ChaosCaching` | 核心的运行时缓存录制与回放功能 |
| `ChaosCachingEditor` | （仅当需要编辑器集成时）提供资产工厂、细节面板自定义、Sequencer 轨道和录制源 |
| `Takes` | 由 `ChaosCachingEditor` 依赖，用于支持 Take Recorder 录制源 |
| `Chaos` | Chaos 物理系统的核心模块，提供 `Chaos Cache Manager` 等组件依赖的基础类型 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下双精度常量截断为浮点数的编译警告。 |
| 2026-05-12 | `d4c60147` | Geometry collection cache adapter : fix logic issue when dealing with root proxies | 修复了几何体集合缓存适配器在处理根代理时的逻辑问题。 |
| 2026-05-12 | `24eff459` | Chaos : Add trailing data to Chaos Event Relay | 向 Chaos 事件中继添加了尾部数据。 |
| 2026-04-14 | `0d40a411` | [ContentBrowser] New Add Menu Physics Menu | [内容浏览器] 新增物理菜单。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF。 |

### 维护评价

ChaosCaching 插件目前处于 **积极维护** 状态。
-   **创建时间**：约 6 年前（2020 年），是一个相对成熟的功能。
-   **更新频率**：最近一个月内有多次提交，表明仍在活跃开发。
-   **维护内容**：更新内容包括修复编译警告、逻辑错误以及适配底层 Chaos 引擎的改动，显示其与核心物理系统的同步维护。
-   **状态**：该插件被标记为 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`，说明它虽然功能完整且在维护中，但 Epic 可能尚未将其视为完全稳定的生产就绪特性，API 或行为在未来版本中可能发生变化。
-   **推荐度**：**推荐在实验性或内部项目中使用**，用于探索和实现物理动画录制回放功能。对于需要绝对稳定性的商业项目，需注意其实验性状态，并密切关注其 API 变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosCaching)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosCaching/Tests)