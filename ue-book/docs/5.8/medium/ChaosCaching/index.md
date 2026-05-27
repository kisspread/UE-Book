# ChaosCaching

> Chaos Cache asset support for recording and playing back physics simulations

| 属性 | 值 |
|---|---|
| 中文名 | 混沌物理缓存 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产、蓝图） |
| 模块 | `ChaosCaching` (Runtime), `ChaosCachingEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-09-01 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosCaching) | |

## 用途

此插件的核心功能是记录和回放基于 Chaos 物理引擎的模拟结果。它允许开发者捕获物理对象（如刚体、布料、破碎体等）在一段时间内的运动状态，并将这些状态序列存储为“缓存资产”。然后，可以在编辑器或运行时精确地回放这些预计算的模拟动画，而无需实时运行复杂的物理计算。这解决了在编辑器中预览动态效果、保存昂贵的模拟结果以供重用，以及制作电影级物理动画的关键需求。

## 使用场景

- **编辑器预览**：在编辑器中精确预览和调整复杂的物理动画（如建筑倒塌、车辆碰撞），无需每次都重新运行耗时的模拟。
- **内容制作**：将精心调试的物理效果保存为资产，以便在游戏关卡中重复使用，保证效果一致。
- **流程化生产**：在动画制作管线中，将物理模拟作为预制动画进行缓存，然后与角色动画混合。
- **性能优化**：对于非常昂贵的物理模拟（如大规模破碎），预先计算并缓存结果，运行时直接播放以节省性能。
- **过场动画**：为需要精确物理表现的电影序列（如道具交互）预渲染动画。

## 蓝图用法

通过蓝图可以方便地控制缓存的录制与回放流程。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `StartRecording` | 开始为指定的物理对象录制模拟数据到缓存资产。 | `UChaosCacheManager` |
| `StopRecording` | 停止当前录制。 | `UChaosCacheManager` |
| `Play` | 从缓存中回放已录制的模拟动画。 | `UChaosCacheManager` |
| `PlayFromStart` | 从起始帧开始回放缓存动画。 | `UChaosCacheManager` |

### 使用示例（蓝图描述）

1.  **录制流程**：在场景中放置一个 `Chaos Cache Manager` Actor，并设置其引用的物理对象（如一个破碎的静态网格体）。在开始物理模拟前，调用 `StartRecording` 节点。模拟结束后，调用 `StopRecording` 节点。录制的数据会保存到指定的 `ChaosCache` 资产中。
2.  **回放流程**：要回放时，确保 `Chaos Cache Manager` 的缓存资产已正确设置。调用 `Play` 或 `PlayFromStart` 节点，物理对象将按照录制的轨迹运动。可以通过蓝图事件（如 `OnPlaybackComplete`）监听回放状态。

## C++ 用法

主要通过操作 `ChaosCacheManager` 和 `ChaosCache` 类来实现录制与回放。

### 头文件引入

```cpp
#include "ChaosCaching.h"
```

### 基本用法

以下代码展示了如何通过 C++ 控制缓存的录制与回放。
*（示例逻辑参考自引擎内部测试与模块公开接口）*

```cpp
// 假设已获取一个 AChaosCacheManager* CacheManager 和要录制的 UChaosCache* CacheAsset
// 开始录制
CacheManager->StartRecording(CacheAsset);

// ... 在此期间运行你的物理模拟 ...

// 停止录制
CacheManager->StopRecording();

// 稍后，回放缓存
CacheManager->Play(CacheAsset);
```

### 进阶用法

可以控制更细粒度的播放参数，例如起始时间或播放速率。

```cpp
// 从缓存的 1.5 秒处开始回放
CacheManager->Play(CacheAsset, 1.5f);

// 检查是否正在播放
if (CacheManager->IsPlaying())
{
    // 获取当前播放进度
    float Progress = CacheManager->GetPlaybackProgress();
}
```

## Demo 示例

一个最小的录制与回放示例类。
*（为简化，省略了 Actor/Component 设置细节，聚焦核心API调用）*

**MyCacheDemoActor.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyCacheDemoActor.generated.h"

class AChaosCacheManager;
class UChaosCache;

UCLASS()
class AMyCacheDemoActor : public AActor
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category="Cache")
    AChaosCacheManager* CacheManager;

    UPROPERTY(EditAnywhere, Category="Cache")
    UChaosCache* CacheAssetToUse;

    UFUNCTION(BlueprintCallable, Category="Cache")
    void StartDemoRecording();

    UFUNCTION(BlueprintCallable, Category="Cache")
    void StopDemoRecording();

    UFUNCTION(BlueprintCallable, Category="Cache")
    void PlayDemoCache();
};
```

**MyCacheDemoActor.cpp**
```cpp
#include "MyCacheDemoActor.h"
#include "ChaosCaching.h" // 引入Chaos缓存头文件

void AMyCacheDemoActor::StartDemoRecording()
{
    if (CacheManager && CacheAssetToUse)
    {
        CacheManager->StartRecording(CacheAssetToUse);
    }
}

void AMyCacheDemoActor::StopDemoRecording()
{
    if (CacheManager)
    {
        CacheManager->StopRecording();
    }
}

void AMyCacheDemoActor::PlayDemoCache()
{
    if (CacheManager && CacheAssetToUse)
    {
        CacheManager->Play(CacheAssetToUse);
    }
}
```

## 模块依赖

此插件依赖 Chaos 物理引擎的核心模块。

| 模块 | 用途 |
|---|---|
| `Chaos` | 提供 Chaos 物理求解器和核心类型定义。 |
| `ChaosSolverEngine` | 提供物理求解器引擎集成。 |
| `Sequencer` | 用于在 Sequencer 中集成缓存动画轨道。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了严格浮点模式下双精度常量截断为浮点数产生的编译警告。 |
| 2026-05-12 | `d4c60147` | Geometry collection cache adapter : fix logic issue when dealing with root proxies | 修复了处理根代理时几何体集合缓存适配器的逻辑错误。 |
| 2026-05-12 | `24eff459` | Chaos : Add trailing data to Chaos Event Relay | 为混沌事件中继器添加了尾部数据。 |
| 2026-04-14 | `0d40a411` | [ContentBrowser] New Add Menu Physics Menu | 在内容浏览器的添加菜单中整合了物理相关资产创建选项。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移至新的 UE_LOGF 宏。 |

### 维护评价

此插件仍处于 **实验性** 阶段（`IsExperimentalVersion=true`），但近期（2026年）有持续的维护和功能改进，包括错误修复和新特性。虽然创建已有约6年，但最近的活动表明它仍在**积极维护**中。主要限制是其**实验性**状态，意味着API和功能在稳定之前可能发生变化。鉴于其活跃的维护状态和明确的用途，**推荐在需要缓存物理模拟的项目中评估使用**，但需注意未来版本可能的兼容性变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosCaching)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosCaching/Tests)（可能存在）