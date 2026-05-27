# Subsonic

> Subsonic is a high-level audio authoring and playback system. This plugin is experimental and as such there is no guarantee of backward compatibility.

| 属性 | 值 |
|---|---|
| 中文名 | 次声波音频系统 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（音频资产） |
| 模块 | `SubsonicCore` (Runtime), `SubsonicEditor` (Runtime), `SubsonicEngine` (Runtime), `SubsonicEngineTest` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-01-12 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic) | |

## 用途

Subsonic 是一套**基于事件的高层音频创作与播放系统**。它解决的核心问题是：如何将复杂的音频播放逻辑抽象为可编辑、可参数化、可复用的事件-动作（Event-Action）体系，并支持运行时动态触发。

具体来说：

- **事件集合（Event Collection）**：将一组音频事件组织为一个集合，每个事件通过 `FGameplayTag` 标识，集合支持在编辑器中可视化编辑。
- **动作（Action）**：事件触发时执行的具体操作，如播放音效、设置音量、应用滤波器等。动作用 `TInstancedStruct<FSubsonicEventActionBase>` 表示，支持多态扩展。
- **执行器（Executor）**：RAII 设计的执行上下文，自动注册/注销到全局事件注册表，使订阅者能够按执行器维度追踪和管理数据。
- **参数系统**：支持在编辑器中将属性绑定到参数，运行时通过 `FSubsonicParameterStore` 动态覆盖参数值（音量、音高、滤波器截止频率、淡出时间等）。
- **订阅者接口**：任何实现了 `ISubsonicEventSubscriberInterface` 的对象都可以监听事件的注册、执行、注销等生命周期事件。

与 UE 原生的 MetaSound 和 SoundCue 系统不同，Subsonic 更偏向于**程序化音频创作流程**——它将音频播放逻辑封装为可在编辑器中编辑的数据结构，同时保留了 C++ 层面的高度可编程性。

## 使用场景

- 你需要构建一个参数化的音频事件系统，例如根据游戏状态动态触发不同的环境音组合 → 用 Subsonic 的 Event Collection + Parameter Store
- 你需要按执行器维度隔离音频数据，例如多个 NPC 同时播放各自的对话音频且互不干扰 → 用 FSubsonicExecutor + TSubscriberDataStore
- 你需要在编辑器中可视化编辑音频事件和参数绑定，运行时动态覆盖参数（音量、音高、滤波器等） → 用 Subsonic 的参数绑定系统
- 你需要监听音频事件的生命周期来做可视化反馈或调试 → 实现 ISubsonicEventSubscriberInterface

## 蓝图用法

Subsonic 的核心数据结构（`FSubsonicEventCollectionDefinition`、`FSubsonicEvent`、`FSubsonicParameterStore` 等）均标记为 `BlueprintType`，但大部分编辑器操作函数标记为 `UE_INTERNAL`，对外暴露的 Blueprint API 集中在执行器和参数存储上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ExecuteEvent` | 通过名称触发事件 | `FSubsonicExecutor` |
| `SetParameters` | 设置执行器的触发时参数 | `FSubsonicExecutor` |
| `GetParameters` | 获取当前参数存储 | `FSubsonicExecutor` |
| `HasParameter` | 检查参数是否存在 | `FSubsonicParameterStore` |
| `RemoveParameter` | 移除指定参数 | `FSubsonicParameterStore` |
| `Reset` | 重置所有参数 | `FSubsonicParameterStore` |
| `MergeFrom` | 用另一个参数存储覆盖合并 | `FSubsonicParameterStore` |

### 内置参数常量

| 常量名 | 说明 |
|---|---|
| `Volume` | 音量 |
| `PitchShift` | 音高偏移 |
| `HighpassCutoff` | 高通滤波器截止频率 |
| `LowpassCutoff` | 低通滤波器截止频率 |
| `FadeOutTime` | 淡出时间 |

### 使用示例（蓝图描述）

1. **创建执行器并触发事件**：使用 `FSubsonicExecutor::Create` 创建执行器实例，传入音频设备 ID 和集合访问器。然后在蓝图中调用 `ExecuteEvent`，传入事件的 `FGameplayTag` 对应的名称。
2. **动态参数覆盖**：在调用 `ExecuteEvent` 之前，先调用 `SetParameters` 设置一个 `FSubsonicParameterStore`，其中包含 `Volume`、`PitchShift` 等参数的运行时值。这些值会在执行时与编辑器中创作的参数合并。

## C++ 用法

### 头文件引入

```cpp
#include "SubsonicEventCollection.h"
#include "SubsonicExecutor.h"
#include "SubsonicParameterStore.h"
#include "SubsonicBuiltInParameters.h"
#include "SubsonicEventSubscriberInterface.h"
#include "SubsonicHandles.h"
```

### 基本用法：创建事件集合定义

```cpp
using namespace UE::Subsonic::Core;

// 创建一个事件集合定义，包含两个事件
TMap<FGameplayTag, FSubsonicEvent> Events;
FSubsonicEvent AmbientEvent;
FSubsonicEvent ImpactEvent;
Events.Add(FGameplayTag::RequestGameplayTag(TEXT("Audio.Ambient")), MoveTemp(AmbientEvent));
Events.Add(FGameplayTag::RequestGameplayTag(TEXT("Audio.Impact")), MoveTemp(ImpactEvent));

// 创建集合定义（需传入音频设备 ID）
FSubsonicEventCollectionDefinition CollectionDef = FSubsonicEventCollectionDefinition::Create(
    TEXT("MyAudioCollection"),
    MoveTemp(Events),
    Audio::FDefaultDeviceId
);

// 验证集合是否有效
ensure(CollectionDef.IsValid());
```

### 基本用法：创建执行器并触发事件

```cpp
using namespace UE::Subsonic::Core;

// 创建执行器（需要实现 ICollectionAccessor）
auto CollectionAccessor = MakeUnique<FMyCollectionAccessor>();
TSharedRef<FSubsonicExecutor> Executor = FSubsonicExecutor::Create(
    Audio::FDefaultDeviceId,
    MoveTemp(CollectionAccessor)
);

// 设置触发时参数
FSubsonicParameterStore Params;
Params.Bag.AddProperty(UE::Subsonic::BuiltInParameters::Volume, EPropertyBagPropertyType::Float);
Params.Bag.SetValueFloat(UE::Subsonic::BuiltInParameters::Volume, 0.8f);
Executor->SetParameters(MoveTemp(Params));

// 触发事件
Executor->ExecuteEvent(FGameplayTag::RequestGameplayTag(TEXT("Audio.Impact")).GetTagName());
```

### 进阶用法：实现自定义事件订阅者

```cpp
#include "SubsonicEventSubscriberInterface.h"
#include "SubsonicSubscriberDataStore.h"

class UMyAudioSubscriber : public UObject, public ISubsonicEventSubscriberInterface
{
    GENERATED_BODY()

public:
    // 当事件执行前调用
    virtual void OnEventPreExecute(const FSubsonicExecutor& InExecutor, const FEventHandle& InHandle) override
    {
        UE_LOG(LogSubsonic, Log, TEXT("Event %s about to execute from executor %s"),
            *InHandle.EventName.ToString(), *InExecutor.ToString());
    }

    // 当事件执行后调用
    virtual void OnEventPostExecute(const FSubsonicExecutor& InExecutor, const FEventHandle& InHandle) override
    {
        UE_LOG(LogSubsonic, Log, TEXT("Event %s finished executing"), *InHandle.EventName.ToString());
    }

    // 当执行器注册时调用——可用于初始化执行器级别的数据
    virtual void OnExecutorRegistered(const FSubsonicExecutor& InExecutor) override
    {
        FExecutorScopeKey Key(InExecutor);
        DataStore.FindOrAdd(Key, TEXT("PlayCount")) = 0;
    }

    // 当执行器注销时调用——清理执行器级别的数据
    virtual void OnExecutorUnregistered(const FSubsonicExecutor& InExecutor) override
    {
        FExecutorScopeKey Key(InExecutor);
        DataStore.Remove(Key);
    }

private:
    // 使用 TSubscriberDataStore 管理全局和执行器级别的数据
    TSubscriberDataStore<int32> DataStore;
};
```

## Demo 示例

### .h 文件

```cpp
// MySubsonicExample.h
#pragma once

#include "CoreMinimal.h"
#include "SubsonicExecutor.h"
#include "SubsonicEventCollection.h"
#include "SubsonicEventSubscriberInterface.h"
#include "SubsonicSubscriberDataStore.h"

namespace UE::Subsonic::Core
{
    // 最简的 ICollectionAccessor 实现
    class FSimpleCollectionAccessor : public FSubsonicExecutor::ICollectionAccessor
    {
    public:
        FSimpleCollectionAccessor(FSubsonicEventCollectionDefinition* InDef, FCollectionHandle InHandle)
            : Definition(InDef), Handle(InHandle) {}

        virtual const FSubsonicEventCollectionDefinition* GetDefinition() const override { return Definition; }
        virtual FCollectionHandle GetHandle() const override { return Handle; }

    private:
        FSubsonicEventCollectionDefinition* Definition;
        FCollectionHandle Handle;
    };
}

// 简单的事件订阅者
class FSimpleAudioSubscriber : public ISubsonicEventSubscriberInterface
{
public:
    FSimpleAudioSubscriber();
    virtual ~FSimpleAudioSubscriber();

    virtual void OnEventPreExecute(const FSubsonicExecutor& InExecutor, const FEventHandle& InHandle) override;
    virtual void OnEventPostExecute(const FSubsonicExecutor& InExecutor, const FEventHandle& InHandle) override;

private:
    UE::Subsonic::Core::TSubscriberDataStore<int32> ExecutionCounts;
};
```

### .cpp 文件

```cpp
// MySubsonicExample.cpp
#include "MySubsonicExample.h"
#include "SubsonicBuiltInParameters.h"
#include "SubsonicParameterStore.h"

using namespace UE::Subsonic::Core;

FSimpleAudioSubscriber::FSimpleAudioSubscriber()
{
    Register(); // 注册到 SubsonicEventRegistry
}

FSimpleAudioSubscriber::~FSimpleAudioSubscriber()
{
    Unregister(); // 从 SubsonicEventRegistry 注销
}

void FSimpleAudioSubscriber::OnEventPreExecute(const FSubsonicExecutor& InExecutor, const FEventHandle& InHandle)
{
    FExecutorScopeKey Key(InExecutor);
    int32& Count = ExecutionCounts.FindOrAdd(Key, InHandle.EventName);
    Count++;

    UE_LOG(LogSubsonic, Log, TEXT("'%s' pre-execute (count: %d) [executor: %s]"),
        *InHandle.EventName.ToString(), Count, *InExecutor.ToString());
}

void FSimpleAudioSubscriber::OnEventPostExecute(const FSubsonicExecutor& InExecutor, const FEventHandle& InHandle)
{
    UE_LOG(LogSubsonic, Log, TEXT("'%s' post-execute [executor: %s]"),
        *InHandle.EventName.ToString(), *InExecutor.ToString());
}

// 演示完整流程
void ExampleSubsonicUsage()
{
    // 1. 创建事件集合
    TMap<FGameplayTag, FSubsonicEvent> Events;
    Events.Add(FGameplayTag::RequestGameplayTag(TEXT("FX.Explosion")), FSubsonicEvent());

    FSubsonicEventCollectionDefinition Collection = FSubsonicEventCollectionDefinition::Create(
        TEXT("GameplayAudio"), MoveTemp(Events), Audio::FDefaultDeviceId);

    // 2. 创建订阅者
    FSimpleAudioSubscriber Subscriber;

    // 3. 创建执行器
    auto Accessor = MakeUnique<FSimpleCollectionAccessor>(&Collection, FCollectionHandle{});
    TSharedRef<FSubsonicExecutor> Executor = FSubsonicExecutor::Create(
        Audio::FDefaultDeviceId, MoveTemp(Accessor));

    // 4. 设置参数并触发事件
    FSubsonicParameterStore Params;
    Params.Bag.AddProperty(BuiltInParameters::Volume, EPropertyBagPropertyType::Float);
    Params.Bag.SetValueFloat(BuiltInParameters::Volume, 0.5f);
    Executor->SetParameters(MoveTemp(Params));

    Executor->ExecuteEvent(TEXT("FX.Explosion"));

    // 5. 清理（Executor 析构时自动注销）
    Executor->Unregister();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GameplayTags` | 用于事件标识的 FGameplayTag |
| `PropertyBag` | 用于参数存储的 FInstancedPropertyBag |
| `AudioMixer` | 音频设备 ID 和音频系统集成 |

> 注：以上为从源码头文件推断的核心依赖。完整依赖列表请参考各模块的 `.Build.cs` 文件。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `0ad6a1ff` | [Audio, CIS] Fixup bad merge: Revert wholesale Subsonic Subscriber stomp; apply minimal non-deprecat | 修复合并冲突：回退对 Subscriber 的大面积改动，应用最小非废弃修复 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决与 FSoundWaveData API 废弃相关的合并冲突 |
| 2026-04-23 | `129c3dc2` | Fix/silence PVS warnings | 修复/静默 PVS 静态分析警告 |
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | 内容浏览器新增音频菜单分类 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移到 UE_LOGF 新日志宏 |

### 维护评价

- **状态**：🆕 全新实验性插件，创建于 2026 年 1 月，距今约 4 个月
- **活跃度**：**活跃开发中**。最近 1 个月内有更新（5 月合并冲突修复），2-3 个月内有功能迭代（编辑器菜单集成、PVS 修复、日志宏迁移）
- **实验性**：标记为 `IsExperimentalVersion=true`，`EnabledByDefault=false`，**无向后兼容保证**
- **已知限制**：
  - 所有 `UE_INTERNAL` 标记的函数均为模块内部 API，外部使用者不应直接调用
  - `FSubsonicEventCollectionDefinition` 禁用了拷贝构造（`WithCopy = false`），只能移动
  - 参数绑定（Property Binding）系统仅在编辑器构建中可用（`WITH_EDITOR`）
- **推荐**：该插件处于早期实验阶段，API 可能发生重大变化。适合在实验性项目中探索使用，不建议在生产环境中依赖。关注 Epic 的后续更新以追踪 API 稳定性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic)
- [官方文档]()（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic/Source/SubsonicEngineTest)