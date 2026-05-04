# Subsonic

> Subsonic is a high-level audio authoring and playback system. This plugin is experimental and as such there is no guarantee of backward compatibility.

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（音频资产、事件定义） |
| 模块 | `SubsonicCore` (Runtime), `SubsonicEditor` (Runtime), `SubsonicEngine` (Runtime), `SubsonicEngineTest` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-02 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Subsonic) | |

## 用途

Subsonic 是一个高级的音频事件创作与回放系统。它解决的核心问题是：如何将复杂的音频逻辑（如环境音效、音乐层、交互式声音）从游戏逻辑中解耦，并以数据驱动的方式进行管理和执行。

该插件引入了“事件集合”（Event Collection）的概念，允许音频设计师在编辑器中定义一系列音频事件（如“播放”、“停止”），每个事件可以包含多个按顺序执行的“动作”（Action）。这些动作可以绑定到参数上，从而实现运行时动态控制（如音量、音调）。系统通过“执行器”（Executor）来触发和管理这些事件的生命周期，并通过“订阅者”（Subscriber）接口通知其他系统（如音频引擎）进行实际的声音播放。

其存在意义在于为 UE5 提供一个结构化、可扩展且与具体音频实现解耦的音频逻辑框架，特别适合需要复杂音频交互和状态管理的项目。

## 使用场景

- 你需要为一个开放世界游戏创建一个动态的环境音效系统，声音会根据玩家位置、天气和时间变化。
- 你在制作一个音乐驱动的游戏，需要根据游戏状态（如战斗、探索）无缝切换和混合多个音乐层。
- 你希望音频设计师能够独立于程序员，通过可视化工具（Subsonic Editor）定义和调试复杂的音频事件序列。
- 你需要一个支持参数化（如音量、音高）和运行时动态调整的音频系统。

## 蓝图用法

Subsonic 的核心逻辑主要在 C++ 层，但提供了部分蓝图可用的类型和接口。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Parameters` | 在执行器上设置触发时参数，这些参数会与动作定义中的参数合并。 | `FSubsonicExecutor` (通过蓝图暴露的包装器) |
| `Execute Event` | 通过执行器触发一个已命名的音频事件。 | `FSubsonicExecutor` (通过蓝图暴露的包装器) |

### 使用示例（蓝图描述）

1.  **创建执行器**：在 C++ 中创建一个 `FSubsonicExecutor` 实例，并将其包装为蓝图可用的对象。
2.  **设置参数**：在蓝图中，获取该执行器对象，调用 `Set Parameters` 节点，传入一个 `FSubsonicParameterStore` 结构体，其中包含如 `Volume` (0.8) 等参数。
3.  **触发事件**：调用 `Execute Event` 节点，传入事件名称（如 `Play`），系统将根据事件定义和当前参数执行相应的音频动作。

## C++ 用法

### 头文件引入

```cpp
#include "SubsonicExecutor.h"
#include "SubsonicEventCollection.h"
#include "SubsonicParameterStore.h"
#include "ISubsonicEventRegistry.h"
```

### 基本用法

创建一个执行器并触发事件。
（来源：基于 `SubsonicExecutor.h` 和 `SubsonicEventCollection.h` 的 API 设计）

```cpp
using namespace UE::Subsonic::Core;

// 假设已经有一个有效的音频设备ID和事件集合定义
Audio::FDeviceId MyDeviceId = 0; // 示例ID
TUniquePtr<FSubsonicExecutor::ICollectionAccessor> MyAccessor = ...; // 从某个集合获取

// 1. 创建执行器
TSharedRef<FSubsonicExecutor> Executor = FSubsonicExecutor::Create(MyDeviceId, MoveTemp(MyAccessor));

// 2. (可选) 设置触发时参数
FSubsonicParameterStore TriggerParams;
TriggerParams.Bag.AddProperty(UE::Subsonic::BuiltInParameters::Volume, EPropertyBagPropertyType::Float);
TriggerParams.Bag.SetValueFloat(UE::Subsonic::BuiltInParameters::Volume, 0.75f);
Executor->SetParameters(MoveTemp(TriggerParams));

// 3. 触发事件
bool bSuccess = Executor->ExecuteEvent(TEXT("Play"));

// 4. 使用完毕后，执行器会在最后一个引用释放时自动注销。
// 也可以提前手动注销：Executor->Unregister();
```

### 进阶用法

实现一个事件订阅者来响应 Subsonic 系统事件。
（来源：`SubsonicEventSubscriberInterface.h`）

```cpp
#include "SubsonicEventSubscriberInterface.h"

class UMyAudioManager : public UObject, public ISubsonicEventSubscriberInterface
{
    GENERATED_BODY()

public:
    virtual void BeginDestroy() override
    {
        Unregister(); // 确保在销毁前注销
        Super::BeginDestroy();
    }

    // 实现接口方法
    virtual void OnEventPreExecute(const FSubsonicExecutor& InExecutor, const FEventHandle& InHandle) override
    {
        UE_LOG(LogTemp, Log, TEXT("Event %s is about to execute on executor %s"), *InHandle.EventName.ToString(), *InExecutor.ToString());
        // 可以在这里为即将到来的音频事件准备资源
    }

    virtual void OnEventPostExecute(const FSubsonicExecutor& InExecutor, const FEventHandle& InHandle) override
    {
        UE_LOG(LogTemp, Log, TEXT("Event %s finished executing on executor %s"), *InHandle.EventName.ToString(), *InExecutor.ToString());
        // 可以在这里清理或记录状态
    }

    // 在初始化时注册
    void Initialize()
    {
        Register();
    }
};
```

## Demo 示例

一个最小化的 C++ 示例，展示如何创建一个订阅者并响应事件。

**MySubsonicSubscriber.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "SubsonicEventSubscriberInterface.h"
#include "MySubsonicSubscriber.generated.h"

UCLASS()
class UMySubsonicSubscriber : public UObject, public ISubsonicEventSubscriberInterface
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "Audio")
    void StartListening();

    UFUNCTION(BlueprintCallable, Category = "Audio")
    void StopListening();

    // ISubsonicEventSubscriberInterface
    virtual void OnEventPostExecute(const FSubsonicExecutor& InExecutor, const FEventHandle& InHandle) override;
};
```

**MySubsonicSubscriber.cpp**
```cpp
#include "MySubsonicSubscriber.h"
#include "SubsonicCoreLog.h"

void UMySubsonicSubscriber::StartListening()
{
    Register(); // 从 ISubsonicEventSubscriberInterface 继承
    UE_LOG(LogSubsonic, Log, TEXT("MySubsonicSubscriber: Now listening for Subsonic events."));
}

void UMySubsonicSubscriber::StopListening()
{
    Unregister(); // 从 ISubsonicEventSubscriberInterface 继承
    UE_LOG(LogSubsonic, Log, TEXT("MySubsonicSubscriber: Stopped listening."));
}

void UMySubsonicSubscriber::OnEventPostExecute(const FSubsonicExecutor& InExecutor, const FEventHandle& InHandle)
{
    // 当任何 Subsonic 事件执行完毕后，这里会被调用
    UE_LOG(LogSubsonic, Warning, TEXT("Event '%s' just finished! Executor: %s"),
        *InHandle.EventName.ToString(),
        *InExecutor.ToString());
    // 在这里可以触发游戏逻辑，比如更新UI或记录成就
}
```

## 模块依赖

从头文件和模块结构推断，使用 `SubsonicCore` 模块需要以下依赖：

| 模块 | 用途 |
|---|---|
| `AudioMixer` | 提供底层音频设备ID (`Audio::FDeviceId`) 等核心音频类型。 |
| `StructUtils` | 提供 `FInstancedStruct` 和 `FPropertyBag`，用于实现灵活的参数存储和动作定义。 |
| `GameplayTags` | 用于定义和查询系统标签（如 `TAG_SubsonicCore_Event_Play`）。 |

## 维护状态

### 近期更新

由于插件创建日期为未来时间（2026-04-02），无法获取真实的 git 历史记录。以下为基于实验性插件的典型维护模式推测：

- (推测) 初始提交：包含核心框架、事件系统、编辑器工具基础。
- (推测) 功能迭代：添加新的内置动作类型、优化参数绑定、完善编辑器UX。
- (推测) Bug修复：修复事件执行顺序、内存泄漏、编辑器崩溃等问题。

### 维护评价

- **实验性状态**：插件明确标记为 `IsExperimentalVersion: true`，且默认未启用。这意味着 API 和功能可能在未来的引擎版本中发生重大变更或被移除。
- **创建时间**：创建日期异常（未来），可能为内部测试或占位符。在真实场景中，实验性插件的生命周期和维护频率不确定。
- **推荐使用**：**仅推荐用于原型开发、技术研究或内部工具链**。不建议在需要长期稳定维护的商业项目核心功能中依赖此插件。使用前务必评估其与目标引擎版本的兼容性风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Subsonic)
- [官方文档]() (无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Subsonic/Source/SubsonicEngineTest) (位于 `SubsonicEngineTest` 模块)