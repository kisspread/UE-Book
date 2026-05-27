# Subsonic

> Subsonic is a high-level audio authoring and playback system. This plugin is experimental and as such there is no guarantee of backward compatibility.

| 属性 | 值 |
|---|---|
| 中文名 | 次声波音频系统 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `SubsonicCore` (Runtime), `SubsonicEditor` (Runtime), `SubsonicEngine` (Runtime), `SubsonicEngineTest` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-01-12 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic) | |

## 用途

Subsonic 是一个实验性的、高级的音频创作与播放系统。其核心目标是为开发者和音频设计师提供一套比传统 UE 音频系统更强大、更集成化、更面向内容创作（Authoring）的工作流。它不仅仅是一个音效播放器，而是一个统一的音频框架，旨在整合音效、音乐（尤其是交互式音乐）和对话等不同类型的音频内容管理。

它解决了传统音频系统可能存在的工具链分散、高级功能（如复杂的交互式音乐状态管理、精细的混音自动化）实现复杂、以及缺乏统一的可视化编辑工具等问题。通过创建统一的创作和运行时框架，Subsonic 试图简化高级音频项目的开发流程。

## 使用场景

- **电影级叙事游戏**：你需要管理复杂的、随着玩家选择和游戏进程无缝过渡的对话、音乐和环境音效。
- **音乐驱动的游戏**：例如节奏游戏或音乐可视化应用，需要将游戏逻辑与音频的节拍、小节和章节深度绑定。
- **程序化音频**：你希望游戏中的声音（如风声、水流、城市噪音）能根据程序化生成的世界参数（如风速、地形）实时变化。
- **大型开放世界**：你需要一个能高效管理成千上万个音频源、并根据距离、环境和优先级动态调整的系统。

## 蓝图用法

由于这是一个实验性插件，且用户提供的资料中没有详细的公开 API 信息，以下为基于“高级音频创作系统”这一定位推断的核心功能节点。实际节点请以插件内资产和源码为准。

### 核心节点（预期功能）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Subsonic Entity` | 从资产（如 Subsonic Sound Cue）创建一个可播放的音频实体 | `USubsonicSubsystem` 或类似 |
| `Play / Stop / Pause` | 控制音频实体的播放状态 | `USubsonicEntity` |
| `Set Parameter` | 设置音频实体的参数（如音量、音高、自定义RTPC） | `USubsonicEntity` |
| `Transition Music State` | 触发交互式音乐的状态过渡 | `UMusicControllerComponent` |

### 使用示例（蓝图描述）

在一个角色蓝图中：
1.  在 `BeginPlay` 事件中，通过 `Create Subsonic Entity` 节点，传入一个 `Subsonic Sound Cue` 资产（一个在编辑器中预设好的音乐结构），生成一个音乐实体引用。
2.  将这个引用存储为变量 `MusicEntity`。
3.  调用 `Play` 节点并连接到 `MusicEntity` 引用，开始播放。
4.  在玩家进入战斗区域时，使用 `Transition Music State` 节点，传入一个名为 “Combat” 的状态名，使音乐平滑过渡到战斗主题。

## C++ 用法

### 头文件引入

```cpp
#include “SubsonicCore/SubsonicSubsystem.h”
#include “SubsonicEngine/SubsonicEntity.h”
// 根据需要引入其他子模块头文件
```

### 基本用法

以下是一个概念性示例，展示如何在游戏逻辑中初始化和使用 Subsonic 系统。

```cpp
// 假设在某个 Actor 或 GameInstance 中
void AMyActor::BeginPlay()
{
	Super::BeginPlay();

	// 获取 Subsonic 子系统
	if (UGameInstance* GameInstance = GetGameInstance())
	{
		SubsonicSubsystem = GameInstance->GetSubsystem<USubsonicSubsystem>();
	}

	// 从资产创建音频实体
	if (SubsonicSubsystem)
	{
		USubsonicAsset* MyMusicAsset = LoadObject<USubsonicAsset>(nullptr, TEXT(“/Game/Audio/Subsonic/MainTheme”));
		if (MyMusicAsset)
		{
			MusicEntity = SubsonicSubsystem->CreateEntity(MyMusicAsset, this);
			MusicEntity->Play();
		}
	}
}
```

### 进阶用法

进阶用法涉及与实体和状态的深度交互，例如监听音频事件或动态修改参数。

```cpp
// 监听音频实体的状态变化（概念）
MusicEntity->OnStateChanged.AddDynamic(this, &AMyActor::HandleMusicStateChanged);

// 在游戏逻辑中动态调整参数
if (MusicEntity && MusicEntity->IsValid())
{
	MusicEntity->SetParameter(FName(“Intensity”), CurrentCombatIntensity);
}
```

## Demo 示例

一个最小的 C++ Actor 示例，展示基本初始化和播放。

```cpp
// SubsonicDemoActor.h
#pragma once
#include “GameFramework/Actor.h”
#include “SubsonicDemoActor.generated.h”

class USubsonicSubsystem;
class USubsonicEntity;

UCLASS()
class ASubsonicDemoActor : public AActor
{
	GENERATED_BODY()

public:
	ASubsonicDemoActor();

	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

	UPROPERTY(EditAnywhere, Category = “Subsonic”)
	TSoftObjectPtr<class USubsonicAsset> DemoSoundAsset;

private:
	UPROPERTY()
	TObjectPtr<USubsonicSubsystem> SubsonicSubsystem;

	UPROPERTY()
	TObjectPtr<USubsonicEntity> DemoEntity;
};
```

```cpp
// SubsonicDemoActor.cpp
#include “SubsonicDemoActor.h”
#include “SubsonicCore/SubsonicSubsystem.h”
#include “SubsonicEngine/SubsonicEntity.h”

ASubsonicDemoActor::ASubsonicDemoActor()
{
	PrimaryActorTick.bCanEverTick = false;
}

void ASubsonicDemoActor::BeginPlay()
{
	Super::BeginPlay();

	SubsonicSubsystem = GetGameInstance()->GetSubsystem<USubsonicSubsystem>();
	if (SubsonicSubsystem && !DemoSoundAsset.IsNull())
	{
		// 同步加载资产并创建实体
		USubsonicAsset* Asset = DemoSoundAsset.LoadSynchronous();
		if (Asset)
		{
			DemoEntity = SubsonicSubsystem->CreateEntity(Asset, this);
			if (DemoEntity)
			{
				DemoEntity->Play();
			}
		}
	}
}

void ASubsonicDemoActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	if (DemoEntity)
	{
		DemoEntity->Stop();
		DemoEntity->Destroy();
		DemoEntity = nullptr;
	}

	Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AudioMixer` | UE 底层音频混音器，Subsonic 很可能构建于其之上 |
| `MediaAssets` | 可能用于支持流式媒体或更复杂的音频资产格式 |
| `SignalProcessing` | 用于底层音频信号处理算法 |
| `AudioExtensions` | 用于扩展 UE 音频系统功能 |

*注：以上为根据插件性质推断的可能依赖。实际依赖关系需查看 `SubsonicCore.Build.cs` 等文件。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `0ad6a1ff` | [Audio, CIS] Fixup bad merge: Revert wholesale Subsonic Subscriber stomp; apply minimal non-deprecat | 修复了一次糟糕的合并冲突，撤销了对订阅者系统的大幅改动，采用了最小化的非废弃修复。 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决了与 FSoundWaveData API 废弃相关的合并冲突。 |
| 2026-04-23 | `129c3dc2` | Fix/silence PVS warnings | 修复或消除了 PVS 代码分析警告。 |
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | 在内容浏览器的“添加”菜单中新增了音频相关选项。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到了 UE_LOGF。 |

### 维护评价

Subsonic 插件**仍处于活跃的早期开发阶段**。它创建于 2026 年初，非常年轻。最近几个月的提交记录表明开发仍在继续，主要集中在**代码合并冲突修复、编译警告清理以及编辑器工具（如内容浏览器）的集成**上。这符合其“实验性”的定位，即功能和 API 可能正在快速迭代和变化。

**注意事项**：
1.  **实验性警告**：作为标记为 `IsExperimentalVersion: true` 的插件，其 API 和功能**没有向后兼容性保证**。在生产项目中使用存在风险。
2.  **默认未启用**：需要在插件管理器中手动启用。
3.  **文档缺失**：目前没有官方文档，理解和使用完全依赖于源码和示例资产。

**推荐**：适合对前沿音频技术感兴趣的开发者、以及可以在非关键项目中进行技术研究和原型验证的团队。不建议在需要稳定性的商业项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic)
- [官方文档]() (暂无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic/Source/SubsonicEngineTest)