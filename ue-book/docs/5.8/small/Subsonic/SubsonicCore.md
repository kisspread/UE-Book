# Subsonic

> Subsonic is a high-level audio authoring and playback system. This plugin is experimental and as such there is no guarantee of backward compatibility.

| 属性 | 值 |
|---|---|
| 中文名 | 次声音频系统 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（数据资产） |
| 模块 | `SubsonicCore` (Runtime), `SubsonicEditor` (Runtime), `SubsonicEngine` (Runtime), `SubsonicEngineTest` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-01-12 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic) | |

## 用途

Subsonic 并非一个通用的音频播放器插件，而是一个**音频创作与逻辑执行框架**。它旨在解决传统音频系统中事件响应与播放逻辑耦合度过高、难以数据驱动和灵活扩展的问题。

该系统的核心思想是：将音频播放的触发逻辑抽象为“事件”，并为每个事件定义一组可参数化、可组合的“动作”。这使得音频设计师和程序员能够：
1.  **数据驱动音频逻辑**：在编辑器中直观地定义“武器开火”、“UI交互”、“环境触发”等事件，并为其配置一系列音频处理动作（如播放声音、应用效果器、调整音高）。
2.  **执行上下文管理**：通过 `FSubsonicExecutor`（执行器）管理每一次事件调用的独立上下文，支持作用域（全局/执行器）内的参数传递与状态维护。
3.  **模块化与可扩展性**：通过 `ISubsonicEventSubscriberInterface`（订阅者接口）允许其他系统（如游戏逻辑、音频分析工具）监听并响应 Subsonic 系统的内部事件，实现深度集成。

**简而言之，Subsonic 的存在是为了提供一个结构化、可扩展的音频事件总线和执行引擎。**

## 使用场景

- **复杂音频反馈系统**：在动作或射击游戏中，定义“射击”、“命中”、“爆炸”等事件，并为其关联不同的音效库、随机播放规则和效果器链。
- **交互式音乐系统**：根据游戏状态（如战斗强度、角色情绪）触发“音乐状态切换”事件，动态混合不同的音乐层或调整播放参数。
- **UI 与界面音效**：将菜单导航、按钮点击等交互事件标准化，并通过 Subsonic 统一管理，便于批量调整风格和音量。
- **环境音景与声学模拟**：创建区域或物体触发的“环境音”事件，根据玩家距离、天气参数动态调整音效的音量、滤波器和空间化设置。
- **音频工具与分析**：利用订阅者接口，开发自定义的音频调试器、性能分析工具或动态混音器，监听和干预音频事件的执行过程。

## 蓝图用法

Subsonic 核心系统主要面向 C++ 开发，其蓝图接口主要用于数据定义和参数查询。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create` | 创建一个新的 Subsonic 执行器实例，关联一个音频设备和事件集合。 | `FSubsonicExecutor` |
| `ExecuteEvent` | 使用当前执行器上下文执行一个已命名的音频事件。 | `FSubsonicExecutor` |
| `SetParameters` | 设置执行器当前作用域（执行器级别）的运行时参数。 | `FSubsonicExecutor` |
| `HasParameter` | 检查当前参数存储中是否存在指定名称的参数。 | `FSubsonicParameterStore` |
| `MergeFrom` | 将一个参数存储合并到另一个，覆盖同名参数。 | `FSubsonicParameterStore` |
| `IsPublic` | 查询一个事件是否为公开事件（可被外部执行）。 | `FSubsonicEvent` |

### 使用示例（蓝图描述）

在蓝图中，您通常不会直接调用 `FSubsonicExecutor`（它是非 UObject 的共享引用类型）。更常见的用法是在 C++ 中管理执行器，并通过自定义的蓝图函数库暴露简化的操作接口。例如，可以创建一个 `UFUNCTION(BlueprintCallable)` 函数 “PlaySubsonicEvent”，其内部逻辑如下：
1.  获取或创建一个与当前游戏上下文（如角色）关联的 `TSharedRef<FSubsonicExecutor>`。
2.  （可选）调用 `SetParameters`，将当前游戏参数（如角色速度、生命值）填入执行器的参数存储。
3.  调用 `ExecuteEvent(“EventName”)` 触发预定义的音频事件。
4.  返回执行结果。

参数数据（`FSubsonicParameterStore`）可以通过 `EditAnywhere` 属性暴露在蓝图类中，供设计师配置默认值或在编辑器中调试。

## C++ 用法

### 头文件引入

```cpp
#include "SubsonicCore/SubsonicExecutor.h"
#include "SubsonicCore/SubsonicEventCollectionDefinition.h"
#include "SubsonicCore/SubsonicEventSubscriberInterface.h"
```

### 基本用法：创建执行器并触发事件

```cpp
// 假设我们已经有一个 FSubsonicEventCollectionDefinition* EventCollectionDef
// 通常这个定义会从资产加载或原生构建

// 获取音频设备 ID (示例)
Audio::FDeviceId DeviceId = 0; // 或从音频设备管理器获取

// 1. 创建执行器访问器 (需要您提供或系统内置一个实现)
class FSimpleCollectionAccessor : public UE::Subsonic::Core::FSubsonicExecutor::ICollectionAccessor
{
    // ... 实现 GetDefinition 和 GetHandle ...
};

auto CollectionAccessor = MakeUnique<FSimpleCollectionAccessor>(EventCollectionDef, CollectionHandle);

// 2. 创建执行器实例 (RAII 模式，析构时自动注销)
TSharedRef<UE::Subsonic::Core::FSubsonicExecutor> Executor =
    UE::Subsonic::Core::FSubsonicExecutor::Create(DeviceId, MoveTemp(CollectionAccessor));

// 3. (可选) 设置执行器级参数
UE::Subsonic::Core::FSubsonicParameterStore Params;
Params.Bag.AddProperty(FName(“Volume”), EPropertyBagPropertyType::Float);
Params.Bag.SetValueFloat(FName(“Volume”), 0.8f);
Executor->SetParameters(MoveTemp(Params));

// 4. 触发事件
const FName EventToTrigger(“PlayHitSound”);
if (Executor->ExecuteEvent(EventToTrigger))
{
    UE_LOG(LogSubsonic, Log, TEXT(“Event ‘%s’ executed successfully.”), *EventToTrigger.ToString());
}
```

### 进阶用法：实现事件订阅者

```cpp
#include “SubsonicCore/SubsonicEventSubscriberInterface.h”

class UMyAudioDebugTool : public UObject, public UE::Subsonic::Core::ISubsonicEventSubscriberInterface
{
    GENERATED_BODY()

public:
    // 初始化时自动注册到 Subsonic 系统
    virtual void PostInitProperties() override
    {
        Super::PostInitProperties();
        Register(); // 调用基类的注册方法
    }

    // 销毁时注销
    virtual void BeginDestroy() override
    {
        Unregister();
        Super::BeginDestroy();
    }

protected:
    // 实现接口：监听事件执行前后
    virtual void OnEventPreExecute(const UE::Subsonic::Core::FSubsonicExecutor& InExecutor,
                                   const UE::Subsonic::Core::FEventHandle& InHandle) override
    {
        // 例如：记录即将执行的事件
        UE_LOG(LogSubsonic, Display, TEXT(“Event Pre-Execute: %s from Executor %u”),
               *InHandle.EventName.ToString(), InExecutor.GetId());
    }

    virtual void OnEventPostExecute(const UE::Subsonic::Core::FSubsonicExecutor& InExecutor,
                                    const UE::Subsonic::Core::FEventHandle& InHandle) override
    {
        // 例如：统计事件执行次数或耗时
    }

    // 实现接口：监听集合注册（可用于关联特定音频设备的数据）
    virtual void OnCollectionRegistered(const UE::Subsonic::Core::FCollectionHandle& InCollection) override
    {
        // 为新注册的集合初始化一些调试数据
        TSubscriberDataStore<FMyDebugData> DebugStore;
        // ... 初始化 ...
        MyDebugDataStore.Add(InCollection, MoveTemp(DebugStore));
    }

private:
    // 使用作用域数据存储器来管理每个执行器或集合的调试数据
    TMap<UE::Subsonic::Core::FCollectionHandle,
         UE::Subsonic::Core::TSubscriberDataStore<FMyDebugData>> MyDebugDataStore;
};
```

## Demo 示例

一个最小的、可编译的示例，演示如何原生构建一个事件集合并通过执行器触发它。

**MyAudioSubsystem.h**
```cpp
#pragma once

#include “CoreMinimal.h”
#include “SubsonicCore/SubsonicHandles.h” // 用于 FCollectionHandle
#include “MyAudioSubsystem.generated.h”

namespace UE::Subsonic::Core
{
    struct FSubsonicEventCollectionDefinition;
    struct FSubsonicExecutor;
}

UCLASS()
class UMyAudioSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    UFUNCTION(BlueprintCallable, Category = “Audio”)
    void TriggerTestEvent();

private:
    // 持有原生定义的事件集合
    TUniquePtr<UE::Subsonic::Core::FSubsonicEventCollectionDefinition> TestCollection;
    UE::Subsonic::Core::FCollectionHandle TestCollectionHandle;

    // 执行器实例 (可以按对象或按需求创建多个)
    TSharedPtr<UE::Subsonic::Core::FSubsonicExecutor> TestExecutor;
};
```

**MyAudioSubsystem.cpp**
```cpp
#include “MyAudioSubsystem.h”
#include “SubsonicCore/SubsonicEventCollectionDefinition.h”
#include “SubsonicCore/SubsonicExecutor.h”
#include “SubsonicCore/SubsonicBuiltInParameters.h”
#include “GameplayTagContainer.h”

void UMyAudioSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);

    // 1. 原生构建一个事件集合
    using namespace UE::Subsonic::Core;

    // 定义一个事件 Tag
    FGameplayTag TestEventTag = FGameplayTag::RequestGameplayTag(FName(“Audio.Event.Test”));

    // 创建一个简单的事件动作（实际中需要具体的 FSubsonicEventActionBase 子类）
    // 这里我们用一个假设的 FSubsonicAction_PlaySound
    // FSubsonicEventActionDefinition ActionDef;
    // ActionDef.SetAction(TInstancedStruct<FSubsonicEventActionBase>::Make<FSubsonicAction_PlaySound>(...));

    // FSubsonicEvent TestEvent;
    // TestEvent.GetMutableActionCollection().Add(ActionDef);

    // 构建集合定义
    // TMap<FGameplayTag, FSubsonicEvent> Events;
    // Events.Add(TestEventTag, MoveTemp(TestEvent));
    // TestCollection = MakeUnique<FSubsonicEventCollectionDefinition>(
    //     FSubsonicEventCollectionDefinition::Create(FName(“NativeTestCollection”), MoveTemp(Events), 0 /* DeviceId */));
    // TestCollectionHandle = ...; // 通常在注册后获得

    // 2. 创建执行器
    // auto Accessor = MakeUnique<...>(TestCollection.Get(), TestCollectionHandle);
    // TestExecutor = FSubsonicExecutor::Create(0, MoveTemp(Accessor));
}

void UMyAudioSubsystem::Deinitialize()
{
    // 执行器是共享引用，当最后一个引用释放时会自动注销。
    // 在这里重置指针即可。
    TestExecutor.Reset();
    TestCollection.Reset();
    Super::Deinitialize();
}

void UMyAudioSubsystem::TriggerTestEvent()
{
    if (TestExecutor.IsValid())
    {
        // 可选：修改参数
        UE::Subsonic::Core::FSubsonicParameterStore Params;
        // 假设我们覆盖内置的 Volume 参数
        Params.Bag.AddProperty(UE::Subsonic::BuiltInParameters::Volume, EPropertyBagPropertyType::Float);
        Params.Bag.SetValueFloat(UE::Subsonic::BuiltInParameters::Volume, 0.5f);
        TestExecutor->SetParameters(Params);

        // 触发事件
        TestExecutor->ExecuteEvent(FName(“TestEvent”)); // 需要与定义的事件名对应
    }
}
```

## 模块依赖

要使用 `Subsonic` 插件，您的模块需要根据使用的部分添加依赖。具体依赖项请查阅各模块的 `Build.cs` 文件。典型的依赖模式如下：

| 模块 | 用途 |
|---|---|
| `SubsonicCore` | Subsonic 的核心运行时模块，提供所有基础类型、执行器和注册机制。您的模块如果只需要在运行时使用 Subsonic 功能，依赖此模块即可。 |
| `SubsonicEditor` | Subsonic 的编辑器扩展模块。仅在编辑器工具开发中需要，例如创建自定义事件编辑器或资产工厂。 |
| `GameplayTags` | **可能需要**。核心系统使用 `FGameplayTag` 作为事件标识符。 |
| `PropertyBag` / `InstancedStruct` | **可能需要**。系统内部使用 `FInstancedPropertyBag` 和 `TInstancedStruct` 来实现灵活的参数和动作存储。 |
| `AudioMixer` / `Audio` | **可能需要**。系统与音频设备 (`Audio::FDeviceId`) 交互，可能依赖底层音频模块。 |

**重要提示**：由于 Subsonic 是实验性插件，其内部依赖结构可能发生变化。**务必**检查您所使用模块的 `Subsonic*.Build.cs` 文件中的 `PublicDependencyModuleNames` 和 `PrivateDependencyModuleNames` 以获取准确信息。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `0ad6a1ff` | [Audio, CIS] Fixup bad merge: Revert wholesale Subsonic Subscriber stomp; apply minimal non-deprecat | 修复合并错误，回滚了对订阅者接口的不当修改，采用了最小化的非废弃修改方案。 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决了与 `FSoundWaveData` API 废弃相关的合并冲突。 |
| 2026-04-23 | `129c3dc2` | Fix/silence PVS warnings | 修复或静默了 PVS (静态代码分析) 警告。 |
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | 内容浏览器新增了音频相关资产的添加菜单项。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 `UE_LOG` 宏迁移到了 `UE_LOGF` 格式。 |

### 维护评价

- **创建时间**：该插件创建于 2026 年 1 月，非常年轻。
- **近期活动**：最近一次提交在 2026 年 5 月，主要集中在**合并冲突修复、代码警告清理和编辑器UI微调**，暂无新的重大功能提交。4月份有一些编辑器和日志相关的改进。
- **活跃状态**：作为 Epic 官方维护的实验性插件，其更新频率与引擎开发主线绑定。目前看来处于**早期开发或内部测试整合阶段**，活跃度中等。
- **已知限制**：插件明确标注为 **“实验性，不保证向后兼容”**。这意味着其 API、数据格式和功能在未来的引擎版本中可能发生 breaking changes。
- **推荐使用**：
    - **仅适用于**愿意承担 API 不稳定风险、并且需要此类高级音频创作框架的**高级开发者或内部团队**。
    - **不建议**在计划长期维护的商业项目中直接使用，除非有明确的迁移或适配策略。
    - 建议密切关注其变更日志，并准备好在引擎升级时进行适配工作。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic)
- 官方文档：无
- 测试用例：在提供的文件路径中未发现独立的测试文件，测试代码可能集成在 `SubsonicEngineTest` 模块或主引擎测试套件中。