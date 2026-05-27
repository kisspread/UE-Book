# Subsonic

> Subsonic is a high-level audio authoring and playback system. This plugin is experimental and as such there is no guarantee of backward compatibility.

| 属性 | 值 |
|---|---|
| 中文名 | 次声波音频系统 |
| 分类 | Audio |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（音频资产） |
| 模块 | `SubsonicCore` (Runtime), `SubsonicEditor` (Runtime), `SubsonicEngine` (Runtime), `SubsonicEngineTest` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-01-12 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic) | |

## 用途

Subsonic 是一个基于事件驱动的音频创作与播放框架。它旨在为复杂音频场景提供一种结构化、可配置且可维护的解决方案。与传统的直接播放音源不同，Subsonic 通过“事件集合”、“事件”和“动作”的层次结构来组织音频逻辑，允许开发者（特别是设计师）在编辑器中参数化地定义音频行为，而无需编写大量代码。它解决了在大型项目中，音频触发逻辑分散、参数管理混乱、难以调试和复用的问题，通过数据驱动的方式提高了音频设计的迭代效率。

## 使用场景

- 你正在开发一个需要精细控制音频参数（如音高、滤波、淡出）的恐怖游戏，希望在编辑器中为不同的环境或事件（如“玩家靠近怪物”、“开门声”）配置不同的音频效果混合。
- 你需要为游戏中的技能、武器或 UI 交互创建丰富的音效变体，这些音效的行为依赖于游戏状态参数（如玩家距离、武器等级）。
- 你的项目需要音频逻辑能够被设计师在编辑器中独立创建、测试和调整，而无需程序员每次修改后都重新编译代码。
- 你需要一个音频系统能够支持“试听”功能，以便在编辑器中快速预览复杂音频事件的效果。

## 蓝图用法

根据提供的 SubsonicCore 模块源码分析，其核心的蓝图暴露主要集中在数据结构（`USTRUCT`）上，而具体的执行和注册逻辑更多由 C++ 模块（如 SubsonicEngine）驱动。蓝图用户通常会与 `FSubsonicParameterStore` 和定义好的事件资源交互。

### 核心结构体

| 结构体 | 说明 | 所在类/文件 |
|---|---|---|
| `FSubsonicParameterStore` | 用于存储和传递音频参数的包。可包含音量、音高等内置或自定义参数。 | `SubsonicParameterStore.h` |
| `FSubsonicEvent` | 代表一个可触发的音频事件，包含一组要执行的动作。 | `SubsonicEventCollection.h` |
| `FSubsonicEventCollectionDefinition` | 事件的集合定义，是组织和注册事件的核心容器。 | `SubsonicEventCollection.h` |

### 内置参数名称

在蓝图中设置参数时，可以使用以下预定义的参数名（`FName`）：
- `Volume`
- `PitchShift`
- `HighpassCutoff`
- `LowpassCutoff`
- `FadeOutTime`
（来自 `SubsonicBuiltInParameters.h`）

### 使用示例（蓝图描述）

虽然无法直接展示蓝图节点图，但典型的蓝图使用流程如下：
1.  在 C++ 或通过资产创建一个 `FSubsonicEventCollectionDefinition`。
2.  在该定义中，使用 `GameplayTag` 定义不同的事件（如 `Gameplay.Impact.Heavy`）。
3.  在每个事件下，添加多个动作（`FSubsonicEventActionDefinition`）。动作类型可能包括播放声音、设置参数等。
4.  为动作配置参数，这些参数可以绑定到事件或集合级别的 `FInstancedPropertyBag`（在编辑器中可视化为参数列表）。
5.  在游戏中，创建 `FSubsonicExecutor`（执行器）来触发事件。执行器可以携带触发时的参数（`FSubsonicParameterStore`）。
6.  调用执行器的 `ExecuteEvent(FName EventName)` 或 `ExecuteEvent(FGameplayTag EventTag)` 来触发事件，系统将自动合并参数并执行所有绑定的动作。

## C++ 用法

### 头文件引入

```cpp
// 使用事件系统核心
#include "SubsonicEventCollection.h"
#include "SubsonicExecutor.h"
#include "SubsonicParameterStore.h"
#include "ISubsonicEventRegistry.h"
```

### 基本用法：创建并触发一个事件

此示例展示了如何用代码定义一个简单的事件集合，并通过执行器触发它。
（灵感来源于 `SubsonicEventCollection.h` 和 `SubsonicExecutor.h` 中的结构）

```cpp
// 假设我们有一个音频设备ID，通常在运行时获取
Audio::FDeviceId MyAudioDeviceId = 0;

// 1. 创建一个事件集合定义
UE::Subsonic::Core::FSubsonicEventCollectionDefinition MyCollection =
    UE::Subsonic::Core::FSubsonicEventCollectionDefinition::Create(
        FName("MyGameSounds"),
        {}， // 初始为空的事件映射
        MyAudioDeviceId
    );

// 2. 向集合中添加一个事件（通常在编辑器中完成，代码演示原理）
FGameplayTag ImpactTag = FGameplayTag::RequestGameplayTag(FName("Gameplay.Impact"));
MyCollection.AddEvent(ImpactTag);

// 3. 为事件添加动作（简化，实际动作类型需要继承自 FSubsonicEventActionBase）
// UE::Subsonic::Core::FEventHandle EventHandle = ...; // 通过事件标签获取句柄
// MyCollection.AddAction(EventHandle);

// 4. 创建执行器来触发事件
TSharedRef<UE::Subsonic::Core::FSubsonicExecutor> Executor =
    UE::Subsonic::Core::FSubsonicExecutor::Create(MyAudioDeviceId, /* ... Collection Accessor ... */);

// 5. （可选）设置触发时的参数
UE::Subsonic::FSubsonicParameterStore TriggerParams;
TriggerParams.Bag.AddProperty(FName("Volume"), EPropertyBagPropertyType::Float);
TriggerParams.Bag.SetValueFloat(FName("Volume"), 0.7f);
Executor->SetParameters(TriggerParams);

// 6. 触发事件
bool bSuccess = Executor->ExecuteEvent(FName("Gameplay.Impact"));

// 7. 执行器在其生命周期结束后会自动注销。也可以手动调用 Executor->Unregister();
```

### 进阶用法：实现事件订阅者接口

通过实现 `ISubsonicEventSubscriberInterface`，你的类可以在音频事件的生命周期中收到回调，用于实现自定义逻辑（如UI反馈、游戏状态检查）。
（来源：`SubsonicEventSubscriberInterface.h`）

```cpp
// MyAudioSubscriber.h
#pragma once
#include "SubsonicEventSubscriberInterface.h"
#include "MyAudioSubscriber.generated.h"

UCLASS()
class UMyAudioSubscriber : public UObject, public ISubsonicEventSubscriberInterface
{
    GENERATED_BODY()

public:
    // 在对象初始化时注册
    virtual void BeginDestroy() override
    {
        Unregister(); // 确保反注册
        Super::BeginDestroy();
    }

    // 重写接口方法
    virtual void OnEventPreExecute(const UE::Subsonic::Core::FSubsonicExecutor& InExecutor, const UE::Subsonic::Core::FEventHandle& InHandle) override
    {
        // 在事件触发前执行逻辑，例如检查游戏状态
        UE_LOG(LogTemp, Log, TEXT("事件 %s 即将执行，来自执行器 %s"), *InHandle.EventName.ToString(), *InExecutor.ToString());
    }

    virtual void OnEventPostExecute(const UE::Subsonic::Core::FSubsonicExecutor& InExecutor, const UE::Subsonic::Core::FEventHandle& InHandle) override
    {
        // 在事件触发后执行逻辑，例如更新UI
        UE_LOG(LogTemp, Log, TEXT("事件 %s 执行完成"), *InHandle.EventName.ToString());
    }

    // 构造时或合适时机调用
    void Activate()
    {
        Register(); // 调用基类的 Register 向注册中心订阅
    }

    void Deactivate()
    {
        Unregister();
    }
};
```

## Demo 示例

一个最小化、可编译的示例，展示如何创建一个简单的事件订阅者。
（注意：实际创建和执行事件通常需要 SubsonicEngine 模块的支持，此处仅展示订阅者结构）

**MyMinimalSubscriber.h**
```cpp
#pragma once
#include "SubsonicEventSubscriberInterface.h"
#include "MyMinimalSubscriber.generated.h"

UCLASS()
class UMyMinimalSubscriber : public UObject, public ISubsonicEventSubscriberInterface
{
    GENERATED_BODY()

public:
    UMyMinimalSubscriber();
    virtual ~UMyMinimalSubscriber();

    virtual void OnCollectionRegistered(const UE::Subsonic::Core::FCollectionHandle& InCollection) override;
    virtual void OnEventPreExecute(const UE::Subsonic::Core::FSubsonicExecutor& InExecutor, const UE::Subsonic::Core::FEventHandle& InHandle) override;
};
```

**MyMinimalSubscriber.cpp**
```cpp
#include "MyMinimalSubscriber.h"
#include "SubsonicCoreLog.h" // 用于 LogSubsonic

UMyMinimalSubscriber::UMyMinimalSubscriber()
{
    // 在构造函数中注册自己
    Register();
}

UMyMinimalSubscriber::~UMyMinimalSubscriber()
{
    Unregister();
}

void UMyMinimalSubscriber::OnCollectionRegistered(const UE::Subsonic::Core::FCollectionHandle& InCollection)
{
    UE_LOG(LogSubsonic, Log, TEXT("集合 '%s' 已注册。"), *InCollection.ToString());
}

void UMyMinimalSubscriber::OnEventPreExecute(const UE::Subsonic::Core::FSubsonicExecutor& InExecutor, const UE::Subsonic::Core::FEventHandle& InHandle)
{
    UE_LOG(LogSubsonic, Log, TEXT("准备执行事件: %s (来自: %s)"), *InHandle.EventName.ToString(), *InExecutor.ToString());
    // 在这里可以添加你的自定义逻辑
}
```

## 模块依赖

从 SubsonicCore 的 `Build.cs` 文件分析，其除了标准依赖外，还依赖于以下音频相关模块。

| 模块 | 用途 |
|---|---|
| `MetasoundFrontend` | 集成 MetaSound 节点图系统，可能用于将 Subsonic 事件映射为 MetaSound 图的输入。 |
| `AudioExtensions` | 提供音频扩展功能，是 Unreal 音频系统的基础组件。 |
| `AudioMixer` | 底层的音频混音器实现。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `0ad6a1ff` | [Audio, CIS] Fixup bad merge: Revert wholesale Subsonic Subscriber stomp; apply minimal non-deprecating fixup. | 修复一次错误的合并，回退了对订阅者逻辑的大范围覆盖，只应用了最小必要的、非废弃性的修正。 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决了与 `FSoundWaveData` API 废弃修复相关的合并冲突。 |
| 2026-04-23 | `129c3dc2` | Fix/silence PVS warnings | 修复或静音了来自 PVS 静态代码分析工具的警告。 |
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | 为内容浏览器的“新增资产”菜单添加了音频相关的子菜单。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移到新的 `UE_LOGF` 格式。 |

### 维护评价

Subsonic 是一个相对较新的插件（创建于 2026 年初），目前处于**实验性**阶段（`IsExperimentalVersion = true`）。从 git 记录看，它仍在进行活跃的开发和维护，近期的提交主要包括合并冲突修复、代码清理和工具链适配。

**需要注意的限制**：
1.  **实验性**：官方明确表示不保证向后兼容性，API 和行为可能在后续版本中发生变化。
2.  **功能不完整**：根据有限的源码分析，核心的“动作”类型和具体的播放实现可能分散在其他模块（如 SubsonicEngine）中，当前提供的核心模块更偏向于数据结构和框架定义。
3.  **学习曲线**：它引入了一套新的音频创作范式（事件-动作-参数），需要团队学习和适应。

**推荐建议**：如果你的项目需要高度参数化、事件驱动的音频系统，并且愿意接受实验性 API 可能带来的风险，Subsonic 值得尝试和关注。它特别适合大型团队中希望分离游戏逻辑和音频设计的场景。对于独立开发者或简单项目，传统的 `Play Sound at Location` 等方法可能更直接。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic)
- [官方文档]（无，.uplugin 中 DocsURL 为空）