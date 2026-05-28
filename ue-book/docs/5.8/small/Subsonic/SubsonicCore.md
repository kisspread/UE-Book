# Subsonic

> Subsonic is a high-level audio authoring and playback system. This plugin is experimental and as such there is no guarantee of backward compatibility.

| 属性 | 值 |
|---|---|
| 中文名 | 次声波系统 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（代码资产） |
| 模块 | `SubsonicCore` (Runtime), `SubsonicEditor` (Runtime), `SubsonicEngine` (Runtime), `SubsonicEngineTest` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-01-12 |
| 年龄标签 | 🆕（约 0.5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic) | |

## 用途

Subsonic 是一个高层音频事件编辑和执行系统，而非底层音频引擎。它解决的核心问题是：如何在不编写大量硬编码逻辑的情况下，将复杂的音频播放逻辑（如音效组合、触发条件、参数变化、空间混音）可视化地设计出来，并能在运行时高效、灵活地触发和控制。

它存在是因为：
1.  **解耦设计与执行**：音频设计师可以在编辑器中可视化地组合“事件”（Event）和“动作”（Action），而无需程序员在 C++ 中编写播放逻辑。
2.  **参数化与动态控制**：事件和动作可以绑定到外部参数，允许音频行为根据游戏状态（如角色速度、环境类型、任务进度）动态变化。
3.  **作用域管理**：通过“执行器”（Executor）概念，管理音频播放的上下文和生命周期，方便进行数据追踪（如为不同 UI 界面或角色维护独立的音频状态）。

## 使用场景

-   **复杂技能音效**：在一个 RPG 游戏中，设计师可以创建一个“释放火球”事件，其动作序列是：先播放施法吟唱音效 -> 短暂静音 -> 播放爆炸音效 -> 播放余烬燃烧循环音效，所有音效的音量、音调都可以通过施法者等级或环境湿度等参数动态调整。
-   **动态环境音景**：在一个开放世界游戏中，根据玩家的位置（森林/沙漠）和天气（雨天/晴天）等参数，自动混合不同的背景音效层，并实现平滑过渡。
-   **交互式音乐系统**：为音游或节奏游戏设计，根据玩家输入的“完美”、“良好”、“失误”等状态，触发不同的音乐片段或音效，并可能改变主音乐的节奏或音高。
-   **UI 反馈**：为复杂的 UI 交互（如组合按钮、拖拽进度条）设计连贯、有层次的音效序列。

## 蓝图用法

Subsonic 的核心数据结构（如 `FSubsonicEventCollectionDefinition`）主要通过 C++ 创建和管理，但其执行和参数设置可以通过蓝图完成。以下关键节点基于其公开的 API 和结构体推断。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Executor` | 为一个事件集合创建一个执行器实例，这是触发事件的入口。 | `FSubsonicExecutor` |
| `Execute Event` | 通过执行器触发一个已命名的事件。 | `FSubsonicExecutor` |
| `Set Parameters` | 在执行器上设置触发时参数，这些参数将与事件动作中的参数合并。 | `FSubsonicExecutor` |
| `Get Is Valid` | 检查执行器是否有效。 | `FSubsonicExecutor` |

### 使用示例（蓝图描述）

1.  **创建执行器**：在 C++ 中创建一个 `FSubsonicEventCollectionDefinition` 并注册事件。然后，在蓝图中（例如在一个 Actor 的 `BeginPlay`），调用 `FSubsonicExecutor::Create` 函数，传入音频设备 ID 和事件集合的访问器，获得一个 `TSharedRef<FSubsonicExecutor>`，将其存储为变量。
2.  **设置参数**：在需要播放音效前（例如当玩家按下攻击键），创建一个 `FSubsonicParameterStore` 结构体变量。使用“Set Property Value (by Name)”节点，在其中设置如 `Volume`、`PitchShift` 等预定义参数，或自定义参数。然后，调用存储的执行器变量的 `Set Parameters` 节点，传入这个参数存储结构。
3.  **触发事件**：紧接着，调用执行器的 `Execute Event` 节点，传入要播放的事件名称（例如 `“Player.Attack”`）。Subsonic 系统将根据事件定义中配置的动作序列和当前设置的参数进行播放。

## C++ 用法

### 头文件引入

```cpp
// 核心类型和执行器
#include "SubsonicExecutor.h"
#include "SubsonicHandles.h"
// 事件定义结构
#include "SubsonicEventCollection.h"
// 参数存储
#include "SubsonicParameterStore.h"
// 内置参数名
#include "SubsonicBuiltInParameters.h"
```

### 基本用法

创建并注册一个事件集合定义。

```cpp
// 假设在某个 Manager 类中
void UMyAudioManager::InitializeAudioSystem()
{
    using namespace UE::Subsonic;

    // 1. 创建事件集合定义
    // 注意：实际中通常从资产（如DataAsset）反序列化，这里为演示手动创建。
    Core::FSubsonicEventCollectionDefinition CollectionDef = Core::FSubsonicEventCollectionDefinition::Create(
        TEXT("PlayerAudio"), // 集合名称
        {}, // 事件映射（稍后添加）
        Audio::DefaultDeviceId // 音频设备 ID
    );

    // 2. 创建并配置一个事件
    Core::FSubsonicEvent FootstepEvent;
    // 为事件添加一个动作（例如播放一个音效），这里简化，实际动作需要具体类型。
    // FootstepEvent.GetMutableActionCollection().Add(...); 

    // 3. 将事件添加到集合
    CollectionDef.AddEvent(FGameplayTag::RequestGameplayTag(TEXT("Player.Movement.Footstep")), MoveTemp(FootstepEvent));

    // 4. 注册集合到系统
    // CollectionDef.Register(...); // 需要获取有效的 CollectionHandle 和 DeviceId
}
```

### 进阶用法

创建执行器，设置参数并触发事件。

```cpp
// 在游戏对象中，例如 ACharacter 子类
void AMyCharacter::PlayFootstep()
{
    // 假设 CollectionAccessor 是一个实现了 ICollectionAccessor 接口的对象，
    // 它持有我们之前注册的音频集合定义。
    if (CollectionAccessor && AudioDeviceId != INDEX_NONE)
    {
        // 1. 创建执行器
        TSharedRef<UE::Subsonic::Core::FSubsonicExecutor> Executor = 
            UE::Subsonic::Core::FSubsonicExecutor::Create(AudioDeviceId, MoveTemp(CollectionAccessor));

        // 2. 准备参数
        UE::Subsonic::FSubsonicParameterStore Params;
        // 使用 PropertyBag 设置具体值
        FProperty* VolProp = Params.Bag.AddProperty(UE::Subsonic::BuiltInParameters::Volume, EPropertyBagPropertyType::Float);
        if (VolProp) { Params.Bag.SetValueFloat(UE::Subsonic::BuiltInParameters::Volume, 0.5f); }

        // 3. 将参数应用到执行器
        Executor->SetParameters(MoveTemp(Params));

        // 4. 触发事件
        Executor->ExecuteEvent(FName(TEXT("Player.Movement.Footstep")));
    }
}
```

## Demo 示例

### AudioDemoManager.h
```cpp
#pragma once
#include "SubsonicExecutor.h"
#include "SubsonicEventCollection.h"
#include "SubsonicParameterStore.h"
#include "GameFramework/Actor.h"
#include "AudioDemoManager.generated.h"

UCLASS()
class AAudioDemoManager : public AActor
{
	GENERATED_BODY()

public:
	AAudioDemoManager();
	virtual void BeginPlay() override;

	// 蓝图可调用，演示播放音效
	UFUNCTION(BlueprintCallable, Category = "Subsonic Demo")
	void PlayDemoSound(float InVolume);

private:
	// 事件集合定义
	UE::Subsonic::Core::FSubsonicEventCollectionDefinition CollectionDefinition;

	// 执行器
	TSharedPtr<UE::Subsonic::Core::FSubsonicExecutor> Executor;

	// 音频设备ID
	Audio::FDeviceId DeviceId = INDEX_NONE;

	// 标记是否初始化成功
	bool bIsInitialized = false;
};
```

### AudioDemoManager.cpp
```cpp
#include "AudioDemoManager.h"
#include "SubsonicBuiltInParameters.h"
#include "SubsonicEventRegistry.h"
#include "SubsonicSubsystem.h" // 假设使用一个子系统获取设备ID

AAudioDemoManager::AAudioDemoManager()
{
	PrimaryActorTick.bCanEverTick = false;
}

void AAudioDemoManager::BeginPlay()
{
	Super::BeginPlay();

	// 1. 获取音频设备ID (示例方式，实际可能不同)
	if (const USubsonicSubsystem* SubSys = GetGameInstance()->GetSubsystem<USubsonicSubsystem>())
	{
		DeviceId = SubSys->GetAudioDeviceId();
	}

	if (DeviceId == INDEX_NONE)
	{
		UE_LOG(LogSubsonic, Error, TEXT("AAudioDemoManager: Failed to get Audio Device ID."));
		return;
	}

	// 2. 创建一个简单的事件集合定义
	// 这里演示创建一个只有一个“PlaySound”事件的集合，该事件会触发一个播放音效的动作。
	// 由于动作类型是实验性的且未在核心模块完全公开，此示例会简化。
	// 实际使用中，你需要导入或引用具体的动作结构，如 FSubsonicEventActionPlaySound。
	TMap<FGameplayTag, UE::Subsonic::Core::FSubsonicEvent> Events;
	UE::Subsonic::Core::FSubsonicEvent DemoEvent;
	// 伪代码：向事件的动作集合中添加一个“播放音效”的动作定义
	// DemoEvent.GetMutableActionCollection().Add(FSubsonicEventActionDefinition{ /* 配置播放 SoundWave */ });
	Events.Add(FGameplayTag::RequestGameplayTag(TEXT("Demo.PlaySound")), MoveTemp(DemoEvent));

	// 3. 创建集合并注册
	CollectionDefinition = UE::Subsonic::Core::FSubsonicEventCollectionDefinition::Create(
		TEXT("DemoAudioCollection"),
		MoveTemp(Events),
		DeviceId
	);
	// 注意：Create 内部已处理注册。我们还需保存一个访问器。
	// 在实际系统中，集合通常由资产管理器管理，这里我们直接在内存中创建并保留。

	// 4. 创建执行器
	// 我们需要一个 ICollectionAccessor 的实现来包装我们的集合定义。
	struct FDemoCollectionAccessor : public UE::Subsonic::Core::FSubsonicExecutor::ICollectionAccessor
	{
		UE::Subsonic::Core::FSubsonicEventCollectionDefinition& Def;
		FDemoCollectionAccessor(UE::Subsonic::Core::FSubsonicEventCollectionDefinition& InDef) : Def(InDef) {}
		const UE::Subsonic::Core::FSubsonicEventCollectionDefinition* GetDefinition() const override { return &Def; }
		UE::Subsonic::Core::FCollectionHandle GetHandle() const override { return UE::Subsonic::Core::FCollectionHandle(); /* 简化 */ }
	};

	auto Accessor = MakeUnique<FDemoCollectionAccessor>(CollectionDefinition);
	Executor = UE::Subsonic::Core::FSubsonicExecutor::Create(DeviceId, MoveTemp(Accessor));

	bIsInitialized = Executor.IsValid();
}

void AAudioDemoManager::PlayDemoSound(float InVolume)
{
	if (!bIsInitialized || !Executor.IsValid())
	{
		UE_LOG(LogSubsonic, Warning, TEXT("AAudioDemoManager::PlayDemoSound: System not initialized."));
		return;
	}

	// 设置参数
	UE::Subsonic::FSubsonicParameterStore ParamStore;
	FProperty* VolProp = ParamStore.Bag.AddProperty(UE::Subsonic::BuiltInParameters::Volume, EPropertyBagPropertyType::Float);
	if (VolProp)
	{
		ParamStore.Bag.SetValueFloat(UE::Subsonic::BuiltInParameters::Volume, FMath::Clamp(InVolume, 0.0f, 1.0f));
	}

	// 应用参数并执行事件
	Executor->SetParameters(MoveTemp(ParamStore));
	Executor->ExecuteEvent(FName(TEXT("Demo.PlaySound")));
}
```

## 模块依赖

Subsonic 插件主要依赖于 UE 的音频和核心子系统。使用者需要在自己的模块 `Build.cs` 中添加对 `SubsonicCore` 的依赖。

| 模块 | 用途 |
|---|---|
| `SubsonicCore` | 插件的核心运行时模块，包含事件、执行器、参数等核心数据结构和逻辑。 |
| `AudioMixer` | UE 底层音频混合器，Subsonic 的事件最终会转化为底层的音频播放命令。 |
| `GameplayTags` | 用于标识和管理事件名称，提供层次化和可查询的标签系统。 |
| `PropertyBag` (或 `DataValidation`) | 用于实现灵活的、基于 `FInstancedPropertyBag` 的参数系统。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `0ad6a1ff` | [Audio, CIS] Fixup bad merge: Revert wholesale Subsonic Subscriber stomp; apply minimal non-deprecat | 修复合并错误：回退对订阅者系统的全面破坏性改动，并应用最小的非废弃性修复。 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决了与 `FSoundWaveData` API 废弃修复相关的合并冲突。 |
| 2026-04-23 | `129c3dc2` | Fix/silence PVS warnings | 修复/静音静态代码分析（PVS）警告。 |
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | [内容浏览器] 新增“添加”菜单中的“音频”子菜单。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 `UE_LOG` 迁移到 `UE_LOGF`。 |

### 维护评价

Subsonic 是一个非常新的、实验性的插件，自 2026 年 1 月创建以来，一直保持着**活跃的开发节奏**。从近期的 Git 历史来看，它正在经历 API 的调整（如修复合并、处理废弃警告）和编辑器集成的完善（如新的内容浏览器菜单）。

**需要注意的是**：
1.  **实验性**：其 `.uplugin` 文件明确标注为实验性 (`IsExperimentalVersion: true`)，这意味着其 API 和功能**没有向后兼容性保证**，可能在未来版本中发生重大变化。
2.  **不推荐用于生产环境**：由于其实验性状态和不保证的兼容性，不建议在需要长期稳定维护的项目中直接使用。
3.  **适合早期探索和原型开发**：非常适合用于音频系统原型设计、学习高层音频事件编辑概念，或在独立项目、Game Jam 中尝试。

**总体来说，这是一个充满潜力但需要谨慎对待的前沿功能。建议密切关注其后续版本的更新说明。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic)
- 官方文档：无（实验性插件，暂无官方文档）
- 测试用例：插件目录下包含 `SubsonicEngineTest` 模块。