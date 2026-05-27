# Subsonic

> Subsonic is a high-level audio authoring and playback system. This plugin is experimental and as such there is no guarantee of backward compatibility.

| 属性 | 值 |
|---|---|
| 中文名 | 次声 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（音频资产） |
| 模块 | `SubsonicCore` (Runtime), `SubsonicEditor` (Runtime), `SubsonicEngine` (Runtime), `SubsonicEngineTest` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-01-12 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic) | |

## 用途

Subsonic 是一个**高层音频事件驱动系统**，用于音频的创作与回放。它解决的核心问题是：在复杂的游戏场景中，音频播放不再是简单的"播放一个 Sound Wave"，而是需要**事件驱动、参数化、数据导向**的音频管线。

具体来说，Subsonic 提供：

1. **事件集合（Event Collection）**：将多个音频事件组织为以 `FGameplayTag` 索引的集合，每个事件可包含一系列顺序执行的**动作（Action）**。
2. **参数化系统**：事件集合和事件都可以定义参数（`FInstancedPropertyBag`），动作属性可以**绑定**到这些参数上，实现参数驱动的音频行为。
3. **执行器（Executor）**：RAII 风格的执行上下文，自动向注册表注册/注销，支持触发时参数覆盖。
4. **订阅者模式**：通过 `ISubsonicEventSubscriberInterface` 接口，其他系统可以监听音频事件的生命周期（注册、执行前、执行后）。
5. **作用域数据存储**：提供全局作用域和执行器作用域的键值存储，供订阅者管理上下文相关数据。

与传统的 `UAudioComponent` 直接播放方式不同，Subsonic 的设计让音频行为可以完全在编辑器中**创作（author）**，无需编写播放代码，并支持运行时参数动态调整。

## 使用场景

- 你在做一个需要复杂音频反馈的游戏（如射击、爆炸、环境音），每种声音由多个子效果叠加 → 用 Subsonic 的事件集合 + 动作链
- 你需要根据游戏状态（距离、速度、生命值等）动态调整音量/音调 → 用 Subsonic 的参数绑定系统，运行时通过 `SetParameters` 覆盖
- 你有多个系统（UI、物理、AI）都需要监听音频事件的生命周期 → 用 `ISubsonicEventSubscriberInterface` 订阅事件
- 你需要音频行为与游戏逻辑解耦，由音频设计师在编辑器中配置 → 用 Subsonic 的事件编辑器和 PropertyBag 参数系统

## 蓝图用法

SubsonicCore 模块的公开 API 主要是 C++ 数据结构类型（`USTRUCT`/`BlueprintType`），而非传统的蓝图函数节点。核心类型可作为蓝图属性使用，但执行逻辑主要在 C++ 侧。

### 核心类型

| 类型 | 说明 | 可见性 |
|---|---|---|
| `FSubsonicEventCollectionDefinition` | 事件集合定义，包含以 GameplayTag 索引的事件映射 | BlueprintType |
| `FSubsonicEvent` | 单个事件，包含动作列表和公开标志 | BlueprintType |
| `FSubsonicEventActionDefinition` | 动作定义，包装一个具体的动作实例 | BlueprintType |
| `FSubsonicEventActionBase` | 动作基类（Abstract），所有具体动作继承此类 | BlueprintType |
| `FSubsonicParameterStore` | 参数存储，基于 FInstancedPropertyBag | BlueprintType |
| `FSubsonicExecutor` | 执行器（SharedRef，非 USTRUCT） | 仅 C++ |

### 枚举

| 枚举值 | 说明 |
|---|---|
| `ESubsonicExecutionScope::Global` | 全局作用域参数 |
| `ESubsonicExecutionScope::Executor` | 执行器作用域参数 |

### 使用示例（蓝图描述）

在蓝图中，`FSubsonicParameterStore` 可以作为变量使用，其内部的 `Bag` 属性（`FInstancedPropertyBag`）支持编辑器中定义键值对。执行器通过 C++ 创建后传入蓝图使用。

典型流程：
1. C++ 侧创建 `FSubsonicExecutor::Create()`，获取 `TSharedRef<FSubsonicExecutor>`
2. 在执行器上设置参数：`Executor->SetParameters(Params)`
3. 触发事件：`Executor->ExecuteEvent(EventName)`
4. 事件的每个动作依次执行，自动读取绑定的参数值

## C++ 用法

### 头文件引入

```cpp
#include "SubsonicEventCollection.h"
#include "SubsonicExecutor.h"
#include "SubsonicParameterStore.h"
#include "SubsonicHandles.h"
#include "SubsonicBuiltInParameters.h"
```

### 基本用法：创建事件集合和执行器

```cpp
#include "SubsonicEventCollection.h"
#include "SubsonicExecutor.h"
#include "SubsonicParameterStore.h"
#include "SubsonicBuiltInParameters.h"

using namespace UE::Subsonic::Core;

// 1. 构建事件集合
TMap<FGameplayTag, FSubsonicEvent> Events;

// 创建事件并添加到映射
FSubsonicEvent FireEvent;
// （假设已有具体 Action 子类 FSubsonicEventActionPlaySound）
Events.Add(FGameplayTag::RequestGameplayTag(TEXT("Audio.Fire")), MoveTemp(FireEvent));

// 2. 创建事件集合定义（自动生成唯一 ID 并注册）
FSubsonicEventCollectionDefinition CollectionDef = 
    FSubsonicEventCollectionDefinition::Create(
        TEXT("WeaponSounds"),
        MoveTemp(Events),
        Audio::DefaultDeviceId  // 音频设备 ID
    );

// 3. 创建执行器
TSharedRef<FSubsonicExecutor> Executor = FSubsonicExecutor::Create(
    Audio::DefaultDeviceId,
    nullptr  // CollectionAccessor，由引擎层提供
);

// 4. 设置触发时参数
FSubsonicParameterStore TriggerParams;
TriggerParams.Bag.SetValueFloat(FSubsonic::BuiltInParameters::Volume, 0.8f);
TriggerParams.Bag.SetValueFloat(FSubsonic::BuiltInParameters::PitchShift, 1.2f);
Executor->SetParameters(MoveTemp(TriggerParams));

// 5. 执行事件
Executor->ExecuteEvent(FName("Audio.Fire"));
```

### 进阶用法：实现事件订阅者

```cpp
// 继承 ISubsonicEventSubscriberInterface 来监听音频事件生命周期
class UMyAudioSubsystem : public UObject, public ISubsonicEventSubscriberInterface
{
    GENERATED_BODY()

public:
    virtual void BeginDestroy() override
    {
        Unregister();
        Super::BeginDestroy();
    }

    void Initialize()
    {
        Register();  // 自动向 ISubsonicEventRegistry 注册
    }

protected:
    // 当事件执行前调用
    virtual void OnEventPreExecute(
        const FSubsonicExecutor& InExecutor, 
        const FEventHandle& InHandle) override
    {
        UE_LOG(LogSubsonic, Log, TEXT("Event about to execute: %s"), *InHandle.ToString());
    }

    // 当事件执行后调用
    virtual void OnEventPostExecute(
        const FSubsonicExecutor& InExecutor, 
        const FEventHandle& InHandle) override
    {
        UE_LOG(LogSubsonic, Log, TEXT("Event finished: %s"), *InHandle.ToString());
    }

    // 当新的集合注册时
    virtual void OnCollectionRegistered(const FCollectionHandle& InCollection) override
    {
        UE_LOG(LogSubsonic, Log, TEXT("Collection registered: %s"), *InCollection.ToString());
    }

    // 当执行器注册时
    virtual void OnExecutorRegistered(const FSubsonicExecutor& InExecutor) override
    {
        UE_LOG(LogSubsonic, Log, TEXT("Executor created: %s"), *InExecutor.ToString());
    }
};
```

### 进阶用法：使用作用域数据存储

```cpp
#include "SubsonicSubscriberDataStore.h"

// TSubscriberDataStore 模板支持全局和执行器两级作用域存储
TSubscriberDataStore<float> VolumeStore;

// 全局作用域
VolumeStore.FindOrAdd(FName("MasterVolume")) = 1.0f;

// 执行器作用域（以 FExecutorScopeKey 为键）
FExecutorScopeKey Key(Executor);
VolumeStore.FindOrAdd(Key, FName("WeaponVolume")) = 0.7f;

// 查找
if (float* Volume = VolumeStore.Find(Key, FName("WeaponVolume")))
{
    *Volume *= 0.5f;  // 根据距离衰减
}

// 遍历某个执行器的所有数据
VolumeStore.ForEach(Key, [](FName Name, float& Value)
{
    // 应用最终音量到音频系统
});
```

## Demo 示例

一个完整的最小示例，展示如何创建自定义 Action 子类并注册事件集合。

```cpp
// MySubsonicAction.h
#pragma once

#include "SubsonicEventCollection.h"
#include "SubsonicEventActionBase.generated.h"

USTRUCT(BlueprintType)
struct FSubsonicEventActionLogMessage : public FSubsonicEventActionBase
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, Category = "Action")
    FName Name;

    UPROPERTY(EditAnywhere, Category = "Action")
    FText Message;

protected:
    virtual void Execute(const FSubsonicExecutor& InExecutor, const FActionHandle& InHandle) const override
    {
        UE_LOG(LogSubsonic, Log, TEXT("[%s] %s (Executor: %s)"),
            *Name.ToString(), *Message.ToString(), *InExecutor.ToString());
    }

#if WITH_EDITOR
    virtual FText GetDisplayInfo() const override
    {
        return FText::Format(NSLOCTEXT("Subsonic", "LogAction", "Log: {0}"), Message);
    }
#endif
};
```

```cpp
// MySubsonicSetup.cpp
#include "MySubsonicAction.h"
#include "SubsonicEventCollection.h"
#include "SubsonicExecutor.h"
#include "SubsonicHandles.h"

using namespace UE::Subsonic::Core;

void SetupSubsonicDemo(Audio::FDeviceId DeviceId)
{
    // 创建一个 Log Message 动作
    FSubsonicEventActionLogMessage LogAction;
    LogAction.Name = FName("GreetingAction");
    LogAction.Message = FText::FromString(TEXT("Hello from Subsonic!"));

    // 包装为 ActionDefinition
    FSubsonicEventActionDefinition ActionDef;
    // ActionDef 通过 TInstancedStruct 持有具体动作

    // 创建事件
    FSubsonicEvent GreetEvent;
    // 动作列表通过 AddAction 等编辑器接口管理

    // 构建事件映射
    TMap<FGameplayTag, FSubsonicEvent> Events;
    Events.Add(FGameplayTag::RequestGameplayTag(TEXT("Test.Greeting")), MoveTemp(GreetEvent));

    // 创建并注册集合
    FSubsonicEventCollectionDefinition Collection = 
        FSubsonicEventCollectionDefinition::Create(
            FName("DemoCollection"), 
            MoveTemp(Events), 
            DeviceId
        );

    if (Collection.IsValid())
    {
        UE_LOG(LogSubsonic, Log, TEXT("Collection created with ID: %u"), Collection.GetCollectionId());
    }
}
```

## 模块依赖

### SubsonicCore 模块

从 Build.cs 推断，SubsonicCore 作为核心运行时模块，依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `GameplayTags` | 事件以 `FGameplayTag` 为键索引 |
| `PropertyBag` / `StructUtils` | `FInstancedPropertyBag` 参数系统基础 |
| `AudioMixer` | 音频设备 ID（`Audio::FDeviceId`）等音频基础设施 |

无其他特殊依赖（仅标准 Core/Engine 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `0ad6a1ff` | [Audio, CIS] Fixup bad merge: Revert wholesale Subsonic Subscriber stomp; apply minimal non-deprecat | 修复合并冲突导致的订阅者代码被意外覆盖，恢复正确逻辑 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决与 FSoundWaveData API 废弃相关的合并冲突 |
| 2026-04-23 | `129c3dc2` | Fix/silence PVS warnings | 修复或抑制 PVS 静态分析工具的警告 |
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | 内容浏览器新增音频菜单项（编辑器集成） |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 宏（日志系统升级） |

### 维护评价

- **创建时间**：2026-01-12，非常新的插件
- **实验性状态**：`IsExperimentalVersion=true`，`EnabledByDefault=false`，需要手动启用
- **活跃度**：近期（2026-05）仍在积极开发，有合并修复和编辑器集成更新
- **代码质量**：完善的编辑器绑定系统、参数化设计、RAII 执行器模式，架构成熟
- **风险提示**：作为实验性插件，API 不保证向后兼容，随时可能重构
- **推荐程度**：⚠️ 适合研究和实验，不建议在生产项目中强依赖。关注 Epic 后续是否将其升级为正式插件

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic)
- [官方文档](https://docs.unrealengine.com)（暂无专属文档）