# Subsonic

> Subsonic is a high-level audio authoring and playback system. This plugin is experimental and as such is no guarantee of backward compatibility.

| 属性 | 值 |
|---|---|
| 中文名 | 次声波音频系统 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（音频内容资产） |
| 模块 | `SubsonicCore` (Runtime), `SubsonicEditor` (Runtime), `SubsonicEngine` (Runtime), `SubsonicEngineTest` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-01-12 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic) | |

## 用途

Subsonic 是一套**基于事件驱动的高级音频创作与播放系统**。它解决了传统 UE 音频系统中以下痛点：

1. **音频逻辑与蓝图/代码耦合过深**：传统方式需要手动管理 AudioComponent 的创建、播放、停止，逻辑分散在各处。Subsonic 引入了**事件集合（Event Collection）** 概念，将音频行为以数据驱动的方式组织在一起，通过 GameplayTag 触发。

2. **音频状态管理复杂**：Subsonic 提供了基于命名的音源管理（Named AudioComponent / GeneratorSource），支持 Executor 作用域和全局作用域，自动管理音源的创建、查找和释放。

3. **音频生成管线缺乏统一抽象**：Subsonic 将传统的 `UAudioComponent` 播放和底层 `GeneratorSource`（直接驱动音频渲染线程的波形/MetaSound 生成）统一到同一套事件系统中，并内置了 DSP 处理链（音量、音高偏移、高/低通滤波）。

4. **游戏线程与音频渲染线程的安全通信**：通过 `FSubsonicRelay` 实现批量命令队列，确保参数更新在音频线程安全执行。

简而言之：Subsonic 让你用**数据资产 + GameplayTag** 来定义和触发音频行为，而不是写大量蓝图节点或 C++ 代码来管理音频组件。

## 使用场景

- 你在做一个需要复杂音效交互的游戏（如音效随游戏状态变化、多层混合、事件触发链式音效）→ 用 Subsonic 将音频逻辑数据化
- 你需要在音频渲染线程直接生成/处理音频（低延迟、精确控制）→ 用 Subsonic 的 GeneratorSource 功能
- 你想用 MetaSound 但需要更高级的控制（参数注入、DSP 后处理）→ Subsonic 的 FSubsonicGenerator 包装了 MetaSound 生成器
- 你有大量音效需要按 GameplayTag 分类管理、按需触发 → 用 Subsonic 的 EventCollection 系统
- 你需要管理多个音频源的生命周期（创建、复用、停止、淡出）→ Subsonic 自动处理

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Executor` | 根据指定的事件集合创建一个执行器实例 | `USubsonicSubsystem` |
| `Execute Event` | 通过 GameplayTag 触发事件集合中的指定事件 | `USubsonicEventCollectionExecutor` |

### 使用示例（蓝图描述）

**基本流程：**

1. 创建一个 `USubsonicEventCollection` 资产（在编辑器中配置事件和动作）
2. 通过 `USubsonicSubsystem` 的 `Create Executor` 节点，传入事件集合资产，获得一个执行器（Executor）对象
3. 在需要触发音频的地方，调用执行器的 `Execute Event` 节点，传入对应的 GameplayTag
4. `Execute Event` 节点有两个执行输出引脚：`Succeeded` 和 `Failed`（通过 `ExpandEnumAsExecs` 实现）

**具体连接方式：**

```
[Event BeginPlay] → [SubsonicSubsystem: Create Executor]
                      - WorldContextObject: Self
                      - Name: "MyAudioExecutor"
                      - Collection: (事件集合资产引用)
                      → Executor

[某些游戏事件] → [Executor: Execute Event]
                   - EventTag: "Gameplay.Audio.Explosion"
                   → Succeeded → (后续逻辑)
                   → Failed → (降级处理)
```

事件集合内部可以配置多种事件动作（详见下方 C++ 部分），蓝图中通过编辑器 UI 配置数据，运行时只需触发对应的 GameplayTag。

## C++ 用法

### 头文件引入

```cpp
// 核心子系统和执行器
#include "SubsonicSubsystem.h"
#include "SubsonicEventCollectionObjects.h"

// GeneratorSource 播放功能
#include "SubsonicGeneratorSourceSubscriber.h"
```

### 基本用法

**创建执行器并触发事件：**

```cpp
// 来源: Public/SubsonicSubsystem.h, Public/SubsonicEventCollectionObjects.h

#include "SubsonicSubsystem.h"
#include "SubsonicEventCollectionObjects.h"

// 获取 Subsonic 子系统（引擎级单例）
USubsonicSubsystem* SubsonicSubsystem = GEngine->GetEngineSubsystem<USubsonicSubsystem>();

// 从事件集合创建执行器
const USubsonicEventCollection* Collection = /* 你的事件集合资产 */;
USubsonicEventCollectionExecutor* Executor = SubsonicSubsystem->CreateExecutorBP(
    GetWorld(), FName("MyExecutor"), Collection);

// 通过 GameplayTag 触发事件
ESubsonicExecutionResult Result;
Executor->ExecuteEvent(FGameplayTag::RequestGameplayTag(FName("Audio.Explosion")), Result);

if (Result == ESubsonicExecutionResult::Succeeded)
{
    UE_LOG(LogTemp, Log, TEXT("事件执行成功"));
}

// 用完后注销执行器，释放关联资源
Executor->Unregister();
```

### 进阶用法

**理解事件动作（Event Actions）：**

事件集合中的每个事件包含一组按顺序执行的动作。基于源码分析，Subsonic 提供以下标准动作：

**音频组件动作（AudioComponent 系列）：**

| 功能 | 动作结构体 | 说明 |
|---|---|---|
| 播放声音 | `FSubsonicEventAction_AudioComponentPlay` | 按名称管理 AudioComponent，播放指定 USoundBase |
| 停止声音 | `FSubsonicEventAction_AudioComponentStop` | 停止指定名称的音源 |
| 修改组件 | `FSubsonicEventAction_AudioComponentModify` | 对 AudioComponent 应用一组修改器 |

**音频组件修改器（Modifiers）：**

修改器通过 `FSubsonicEventAction_AudioComponentModify` 的 `Modifiers` 数组配置，支持：

| 修改器 | 说明 |
|---|---|
| `Play` | 设置开始时间偏移 |
| `Stop` | 停止播放 |
| `Set Sound` | 替换音源 |
| `Set Attenuation` | 设置衰减资产 |
| `Set Concurrency` | 设置并发策略 |
| `Set Modulation Routing` | 设置调制路由（音量/音高等目标） |
| `Execute On Finished` | 播放完成后触发父集合中的另一个事件 |

**GeneratorSource 动作（低延迟、渲染线程级）：**

| 功能 | 动作结构体 | 说明 |
|---|---|---|
| 播放波形 | `FSubsonicEventAction_GeneratorSourcePlay` | 直接在音频渲染线程播放 USoundWave，支持参数注入 |
| 停止波形 | `FSubsonicEventAction_GeneratorSourceStop` | 停止指定名称的 GeneratorSource |

**事件控制动作：**

| 功能 | 动作结构体 | 说明 |
|---|---|---|
| 延迟事件 | `FSubsonicEventAction_DelayEvent` | 延迟指定秒数后触发另一个事件，支持取消/替换 |

**作用域管理：**

```cpp
// 来源: SubsonicAction_AudioComponent.h 中的 ESubsonicExecutionScope 注释

// 所有命名音源都支持 Scope 参数：
// - ESubsonicExecutionScope::Executor  - 仅当前执行器实例可见
// - ESubsonicExecutionScope::Global    - 全局池，任何执行器都可访问

// 访问模式（AudioComponent 特有）：
// - Add        - 创建新组件，释放已有组件（非一次性声音会先停止）
// - FindOrAdd  - 查找已有组件，不存在则创建
// - Find       - 仅查找，不存在则忽略
```

## Demo 示例

以下是一个最小的 C++ 示例，展示如何创建执行器并触发事件：

```cpp
// MyAudioManager.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SubsonicEventCollectionObjects.h"
#include "MyAudioManager.generated.h"

UCLASS()
class AMyAudioManager : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;

    // 事件集合资产（在编辑器中设置）
    UPROPERTY(EditAnywhere, Category = "Audio")
    TObjectPtr<const USubsonicEventCollection> AudioEventCollection;

    // 触发音效
    UFUNCTION(BlueprintCallable, Category = "Audio")
    void TriggerSound(FGameplayTag EventTag);

private:
    UPROPERTY()
    TObjectPtr<USubsonicEventCollectionExecutor> Executor;
};
```

```cpp
// MyAudioManager.cpp
#include "MyAudioManager.h"
#include "SubsonicSubsystem.h"

void AMyAudioManager::BeginPlay()
{
    Super::BeginPlay();

    if (!AudioEventCollection)
    {
        UE_LOG(LogTemp, Warning, TEXT("未设置 AudioEventCollection"));
        return;
    }

    // 从子系统创建执行器
    USubsonicSubsystem* SubsonicSubsystem = GEngine->GetEngineSubsystem<USubsonicSubsystem>();
    if (SubsonicSubsystem)
    {
        Executor = SubsonicSubsystem->CreateExecutorBP(
            GetWorld(), FName("GameplayAudio"), AudioEventCollection);
    }
}

void AMyAudioManager::TriggerSound(FGameplayTag EventTag)
{
    if (!Executor)
    {
        UE_LOG(LogTemp, Warning, TEXT("执行器未初始化"));
        return;
    }

    ESubsonicExecutionResult Result;
    Executor->ExecuteEvent(EventTag, Result);

    if (Result == ESubsonicExecutionResult::Succeeded)
    {
        UE_LOG(LogTemp, Log, TEXT("Subsonic 事件 '%s' 执行成功"), *EventTag.ToString());
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Subsonic 事件 '%s' 未找到"), *EventTag.ToString());
    }
}
```

## 模块依赖

基于 SubsonicEngine 的源码分析，以下是该插件独特依赖的模块：

| 模块 | 用途 |
|---|---|
| `SubsonicCore` | Subsonic 核心抽象层（执行器、事件集合定义、Action 基类） |
| `GameplayTags` | 用于事件标识和查找 |
| `AudioMixer` | 底层音频混合器接口（GeneratorSource、MixerDevice） |
| `SignalProcessing` | DSP 处理（双二阶滤波器 FBiquadFilter） |
| `MetaSound` | MetaSound 生成器集成（可选，用于 MetaSound 路径） |
| `MetasoundFrontend` | MetaSound 前端 API（图构建回调等） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `0ad6a1ff` | [Audio, CIS] Fixup bad merge: Revert wholesale Subsonic Subscriber stomp; apply minimal non-deprecat | 修复合并错误：回退 Subscriber 被覆盖的变更，应用最小非废弃修改 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决与 FSoundWaveData API 废弃相关的合并冲突 |
| 2026-04-23 | `129c3dc2` | Fix/silence PVS warnings | 修复/消除 PVS 静态分析警告 |
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | 内容浏览器新增音频菜单入口 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 新日志宏 |

### 维护评价

**状态：活跃开发中**

- **创建时间**：2026-01-12，距今约 4 个月，属于全新插件
- **更新频率**：从 git 记录看，2026 年 4-5 月持续有更新，维护活跃
- **开发阶段**：`IsExperimentalVersion=true`，`EnabledByDefault=false`，明确标注为实验性插件
- **API 稳定性**：官方声明不保证向后兼容，API 可能在未来版本发生重大变化
- **近期改动性质**：合并冲突修复、编译警告修复、菜单集成，属于功能完善阶段

**⚠️ 注意事项：**
- 此插件为**实验性**插件，API 不稳定，不建议用于正式生产项目
- 创建时间极短，文档和社区资源几乎为零
- 模块划分清晰（Core/Engine/Editor/Test），架构设计成熟，预计未来会稳定发布
- 建议在原型开发阶段尝试，跟踪 Epic 的后续更新

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic)
- 官方文档：无（实验性插件，暂无官方文档）