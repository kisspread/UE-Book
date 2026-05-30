# Harmonix

> A package of Harmonix music related audio functionality.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 音乐音频工具包 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（音频资产、MetaSound 节点、MIDI 资产） |
| 模块 | `Harmonix` (Runtime), `HarmonixDsp` (Runtime), `HarmonixDspEditor` (Runtime), `HarmonixDspTests` (Runtime), `HarmonixEditor` (Runtime), `HarmonixMetasound` (Runtime), `HarmonixMetasoundEditor` (Runtime), `HarmonixMetasoundTests` (Runtime), `HarmonixMidi` (Runtime), `HarmonixMidiEditor` (Runtime), `HarmonixMidiTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-17 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix) | |

## 用途

Harmonix 是 Epic Games 旗下 Harmonix GenTech 团队（Rock Band、Guitar Hero 的创造者）开发的**音乐感知型音频处理框架**，于 UE 5.4 随引擎一起对授权用户开放。

该插件解决的核心问题是：**在游戏中实现与音乐节拍、速度、时间轴深度绑定的音频处理和交互系统**。它不是一个简单的音频播放器，而是一套完整的音乐技术栈，包含：

- **HarmonixDsp**：底层数字信号处理（DSP）引擎，提供 Fusion 采样器/合成器架构（FusionPatch、FusionVoice、KeyZone 映射等），用于实时音频合成与采样回放
- **HarmonixMidi**：MIDI 文件解析与回放引擎，支持标准 MIDI 文件的读取、解析和实时播放
- **HarmonixMetasound**：与 UE5 的 MetaSound 系统深度集成，将 Harmonix 的音乐功能（节拍追踪、MIDI 回放、DSP 处理）封装为 MetaSound 节点，可在 MetaSound 图中直接使用
- **Harmonix**（核心模块）：提供跨模块共享的基础类型、同步时钟（音乐时钟、小节/拍子计数）、音频-游戏同步机制

简而言之，Harmonix 让游戏能够"理解音乐"——精确知道当前在第几拍、第几小节、BPM 是多少，并以此驱动游戏玩法和视觉效果。

## 使用场景

- **节奏游戏**：需要精确的节拍检测和拍点判定（如 Beat Saber 类游戏）→ 用 Harmonix 的音乐时钟和节拍同步
- **动态音乐系统**：游戏音乐需要根据玩法状态无缝切换段落、层叠混音 → 用 HarmonixDsp 的 Fusion 采样器配合 MetaSound
- **音乐可视化**：需要提取音频的频谱、节拍信息驱动粒子特效或后处理 → 用 HarmonixDsp 的 DSP 分析
- **MIDI 驱动的游戏玩法**：需要解析 MIDI 文件来生成音符流、驱动打击判定 → 用 HarmonixMidi
- **程序化音乐生成**：需要根据游戏状态实时生成/变形音乐 → 用 MetaSound 节点组合 Harmonix 功能
- **音频反应式灯光/环境**：需要音频信号驱动场景灯光、环境变化 → 用 DSP 输出和音乐时钟

## 蓝图用法

> ⚠️ 该插件默认未启用（`EnabledByDefault: false`），且处于实验阶段（`IsExperimentalVersion: true`）。使用前需在项目设置中手动启用 "Harmonix" 插件。

Harmonix 的主要蓝图接口通过 **MetaSound 节点**暴露。启用插件后，在 MetaSound 编辑器中可找到 Harmonix 提供的自定义节点。

### 核心 MetaSound 节点

| 节点类别 | 说明 | 所在模块 |
|---|---|---|
| 音乐时钟节点 | 提供 BPM、节拍位置、小节计数等音乐时间信息 | `HarmonixMetasound` |
| MIDI 回放节点 | 在 MetaSound 中加载和回放 MIDI 文件 | `HarmonixMetasound` |
| Fusion 采样器节点 | 基于 FusionPatch 的采样回放和合成 | `HarmonixMetasound` |
| DSP 处理节点 | 音频信号的数字信号处理操作 | `HarmonixMetasound` |

### 使用示例

**场景：创建一个节拍同步的 MetaSound**

1. 新建一个 MetaSound 资产
2. 在节点搜索中找到 Harmonix 分类下的 **音乐时钟节点**，添加到图中
3. 将时钟节点的 **Beat Out** 输出连接到一个触发音效的节点，实现每拍触发一次声音
4. 将时钟节点的 **BPM** 输出连接到需要速率同步的参数
5. 游戏中播放该 MetaSound 时，所有连接的节点会自动与音乐节拍同步

**场景：使用 Fusion 采样器回放音频**

1. 创建或导入一个 FusionPatch 资产（定义采样映射和 KeyZone）
2. 在 MetaSound 图中添加 **Fusion Player** 节点
3. 将 FusionPatch 资产赋给播放器节点
4. 连接触发信号（如来自 MIDI 回放节点或游戏事件）
5. 通过 KeyZone 映射实现不同音高/力度触发不同采样

## C++ 用法

### 头文件引入

```cpp
// 核心模块
#include "Harmonix.h"

// DSP 模块
#include "HarmonixDsp.h"

// MIDI 模块
#include "HarmonixMidi.h"

// MetaSound 集成
#include "HarmonixMetasound.h"
```

### 基本用法

**加载和解析 MIDI 文件**

```cpp
// 来源: Source/HarmonixMidi/ 相关测试用例
#include "HarmonixMidi.h"

// 通过资产系统加载 MIDI 资产
// 在编辑器中导入 .mid 文件会自动创建 UAsset

// 代码中使用 MIDI 数据进行解析和读取
// 具体 API 需参考 HarmonixMidi 模块的 Public 头文件
```

**使用 Fusion 音频系统**

```cpp
// 来源: Source/HarmonixDsp/ 相关测试用例
#include "HarmonixDsp.h"

// FusionPatch: 定义采样库和 KeyZone 映射
// FusionVoice: 管理单个音频回放实例
// KeyZone: 定义音高/力度到采样的映射关系

// 从近期 commit 可知，KeyZone 有严格的排序要求：
// KeyZone 必须正确排序以确保正确的采样选择
```

**集成 MetaSound 节点**

```cpp
// 来源: Source/HarmonixMetasound/ 相关实现
#include "HarmonixMetasound.h"

// Harmonix 通过自定义 MetaSound 节点暴露功能
// 节点在模块启动时自动注册到 MetaSound 系统
// 运行时通过 MetaSound 图的执行流驱动
```

### 进阶用法

**FusionVoice 生命周期管理与 UserObject 跟踪**

从近期 commit（`0ae74ea8`）可知，FusionPatch 的 proxy 现在支持附加 UserObject 用于活动追踪：

```cpp
// FusionVoice 管理音频回放实例的 ID 分配
// 从 commit 8513e7f4 可知：
// - AssignIDs 时必须保证 KeyZone 的正确排序
// - 需要对结构性 null 进行防御检查

// UserObject 机制允许关联游戏对象与音频实例
// 用于追踪某个 FusionPatch 正在被哪些游戏对象使用
```

**音频精度注意事项**

从 commit `852b276c` 可知，在 strict floating point 模式下需要注意 double/float 精度转换问题。使用 Harmonix 的 DSP 功能时，确保浮点类型一致性。

## Demo 示例

> ⚠️ 由于 Harmonix 是一个实验性插件且主要通过 MetaSound 图进行配置，以下为最简集成示例。

### 启用插件

在 `DefaultEngine.ini` 中添加：

```ini
[/Script/Plugins.PluginManager]
Harmonix=true
```

### C++ 集成示例

```cpp
// MyMusicManager.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyMusicManager.generated.h"

UCLASS()
class AMyMusicManager : public AActor
{
	GENERATED_BODY()

public:
	AMyMusicManager();

	virtual void BeginPlay() override;
	virtual void Tick(float DeltaTime) override;

	// MetaSound 组件用于播放包含 Harmonix 节点的 MetaSound
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	class UMetaSoundSource* MusicMetaSound;

	UPROPERTY(VisibleAnywhere)
	class UAudioComponent* AudioComponent;
};
```

```cpp
// MyMusicManager.cpp
#include "MyMusicManager.h"
#include "Components/AudioComponent.h"
// Harmonix 功能通过 MetaSound 节点间接使用
// 在 MetaSound 编辑器中配置 Harmonix 节点后，
// 代码中只需播放对应的 MetaSound 资产即可

AMyMusicManager::AMyMusicManager()
{
	PrimaryActorTick.bCanEverTick = true;

	AudioComponent = CreateDefaultSubobject<UAudioComponent>(TEXT("AudioComponent"));
	RootComponent = AudioComponent;
}

void AMyMusicManager::BeginPlay()
{
	Super::BeginPlay();

	// 播放包含 Harmonix 音乐时钟节点的 MetaSound
	if (MusicMetaSound && AudioComponent)
	{
		AudioComponent->SetSound(MusicMetaSound);
		AudioComponent->Play();
	}
}

void AMyMusicManager::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	// 在此可以查询音乐时钟状态
	// Harmonix 的节拍信息通过 MetaSound 的数据输出暴露
	// 游戏逻辑可通过 Data Interface 读取这些输出
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AssetRegistry` | 资产注册与发现，用于 FusionPatch、MIDI 等自定义资产类型 |
| `MetaSound` (隐含) | MetaSound 集成的基础，HarmonixMetasound 依赖 MetaSound 框架 |

> 注：UnrealEd 依赖存在于多个子模块中，属于标准编辑器集成依赖，此处省略。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `8513e7f4` | [Audio] Fix FFusionVoice::AssignIDs KeyZone ordering + add structural null defense. | 修复 FusionVoice 的 KeyZone 排序问题并增加空值防御 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决 FSoundWaveData API 废弃修复的合并冲突 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 截断为 float 的编译警告 |
| 2026-05-12 | `0ae74ea8` | [Harmonix] Add user object to the FusionPatch proxy that can be used for tracking activity in association | 为 FusionPatch 代理添加 UserObject 用于关联活动追踪 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符不匹配问题 |

### 维护评价

**🟢 活跃维护**

- **创建时间**：2024-01-17，约 2 年前，随 UE 5.4 发布
- **更新频率**：非常活跃，近一个月内有多次功能性更新和 bug 修复
- **维护团队**：Epic Games - Harmonix GenTech（专业音乐技术团队）
- **当前状态**：实验性插件（`IsExperimentalVersion: true`），默认未启用
- **已知限制**：
  - 实验性阶段，API 可能在未来版本中发生变化
  - 默认未启用，需要手动在项目设置中开启
  - 文档和示例较少，学习曲线较陡
- **推荐度**：如果你的项目需要节拍同步、MIDI 驱动玩法或高级音频合成，强烈建议关注此插件。虽然处于实验阶段，但由 Harmonix 专业团队维护，且持续有实质性更新。建议在非生产环境中先行试验。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix)
- [官方文档](https://docs.unrealengine.com/)（暂无独立文档页面）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix/Source/HarmonixDspTests)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix/Source/HarmonixMetasoundTests)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix/Source/HarmonixMidiTests)

---

> **子模块索引**（本插件包含 521 个源文件，属于大型插件，建议按子模块阅读）：
>
> | 子模块 | 类型 | 说明 |
> |---|---|---|
> | Harmonix | Runtime | 核心模块，共享基础类型和音乐时钟 |
> | HarmonixDsp | Runtime | 数字信号处理与 Fusion 采样器引擎 |
> | HarmonixMidi | Runtime | MIDI 文件解析与回放 |
> | HarmonixMetasound | Runtime | MetaSound 节点集成 |
> | HarmonixEditor | Runtime | 编辑器扩展与设置自定义 |
> | HarmonixDspEditor | Runtime | DSP 模块的编辑器支持 |
> | HarmonixMidiEditor | Runtime | MIDI 模块的编辑器支持 |
> | HarmonixMetasoundEditor | Runtime | MetaSound 模块的编辑器支持 |
> | HarmonixDspTests | Runtime | DSP 模块自动化测试 |
> | HarmonixMidiTests | Runtime | MIDI 模块自动化测试 |
> | HarmonixMetasoundTests | Runtime | MetaSound 模块自动化测试 |