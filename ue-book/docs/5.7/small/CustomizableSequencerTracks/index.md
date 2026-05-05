# Customizable Sequencer Tracks (Experimental)

> Library that provides a blueprintable track type that can be added to sequencer

| 属性 | 值 |
|---|---|
| 分类 | Runtime |
| 默认启用 | ❌ `EnabledByDefault: false` |
| 包含内容 | ❌ `CanContainContent: false` |
| 模块 | `CustomizableSequencerTracks` (Runtime), `CustomizableSequencerTracksEditor` (Editor) |
| 创建时间 | 2020-08-11 |
| 年龄标签 | 👴 老古董（约 5.7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MovieScene/CustomizableSequencerTracks) | |

## 用途

这个 Plugin 提供了一套 **蓝图化 Sequencer 自定义轨道** 的基础框架。它让你无需编写 C++ 代码，就能通过继承蓝图类来创建自己的 Sequencer 轨道类型。

核心机制是三个蓝图可继承的基类，它们组合在一起定义了一条完整的 Sequencer 轨道：

1. **`USequencerTrackBP`** — 轨道定义：决定轨道类型（根轨道 vs 对象轨道）、支持的 Section 类型、是否支持多行/混合、轨道图标等
2. **`USequencerSectionBP`** — Section 定义：代表轨道上的一个时间段，负责向 Entity System 注册 Track Instance
3. **`USequencerTrackInstanceBP`** — 运行时实例：在 Sequencer 播放时执行实际逻辑，通过 BlueprintImplementableEvent 响应初始化、更新、销毁等生命周期事件

简单来说：`SequencerTrackBP` 定义"这是什么轨道"，`SequencerSectionBP` 定义"轨道上的片段"，`SequencerTrackInstanceBP` 定义"播放时做什么"。

### ⚠️ 实验性警告

这个 Plugin 标记为 **IsBetaVersion=true**、**EnabledByDefault=false**，需要手动启用。Epic 的态度很明确：这是一个实验性功能，API 可能在未来版本中发生变化。

## 使用场景

- 你需要在 Sequencer 中添加一个完全自定义的轨道类型，用来驱动你游戏中的特定系统（比如天气控制、镜头事件、对话触发等），但不想写 C++ Track Editor 代码
- 你想要一种简单的方式来创建 Sequencer 轨道，只通过蓝图配置属性，然后在蓝图中实现运行时逻辑
- 你的项目需要一个 Sequencer 轨道，能够绑定到特定的 Actor 类型，并在播放时触发蓝图事件

## 蓝图用法

### 核心类

#### USequencerTrackBP（蓝图名：`SequencerTrack`）

轨道的配置类。在蓝图中继承后，在 Class Defaults 中设置以下属性：

| 属性 | 类型 | 说明 |
|---|---|---|
| `bSupportsMultipleRows` | `bool` | 是否支持在同一轨道中叠加多个 Section |
| `bSupportsBlending` | `bool` | 是否支持 Easing/Blending 混合 |
| `TrackType` | `ECustomSequencerTrackType` | `RootTrack`（顶层轨道）或 `ObjectTrack`（绑定到对象的轨道） |
| `SupportedObjectType` | `UClass*` | 仅 ObjectTrack 有效，限定此轨道可绑定的对象类型 |
| `DefaultSectionType` | `TSubclassOf<USequencerSectionBP>` | 默认创建的 Section 类型 |
| `SupportedSections` | `TArray<TSubclassOf<USequencerSectionBP>>` | 支持的所有 Section 类型列表 |
| `TrackInstanceType` | `TSubclassOf<USequencerTrackInstanceBP>` | 运行时使用的 TrackInstance 蓝图类型 |
| `Icon` | `FSlateBrush` | 轨道在 Sequencer 中显示的图标 |

#### USequencerSectionBP（蓝图名：`SequencerSection`）

Section 蓝图基类。一般不需要添加额外逻辑——它的主要职责是通过 Entity System 注册 TrackInstance。如果需要自定义 Section 行为，可以在这里添加。

#### USequencerTrackInstanceBP（蓝图名：`SequencerTrackInstance`）

运行时逻辑的核心。继承此类后，在蓝图事件图表中实现以下 **可实现事件**：

| 事件 | 说明 |
|---|---|---|
| `OnInitialize` | TrackInstance 初始化时调用（一次） |
| `OnUpdate` | 每帧更新时调用，用于驱动实际动画逻辑 |
| `OnBeginUpdateInputs` | 开始更新输入列表前调用 |
| `OnInputAdded` | 当一个新的 Section 输入被添加时调用 |
| `OnInputRemoved` | 当一个 Section 输入被移除时调用 |
| `OnEndUpdateInputs` | 输入列表更新完成后调用 |
| `OnDestroyed` | TrackInstance 销毁前调用（会先对每个 Input 触发 OnInputRemoved） |

可用的 **蓝图调用函数**：

| 函数 | 说明 |
|---|---|
| `GetAnimatedObject()` | 获取被动画驱动的目标对象 |
| `GetInputs()` | 获取所有 Section 输入（返回 `TArray<FSequencerTrackInstanceInput>`） |
| `GetNumInputs()` | 获取输入数量 |
| `GetInput(int32 Index)` | 获取指定索引的输入 |

`FSequencerTrackInstanceInput` 是一个 BlueprintType 结构体，包含：
- `Section` — 对应的 `USequencerSectionBP` 引用
- `Context` — 当前评估上下文（非蓝图暴露，仅 C++ 可用）

### 使用示例（蓝图描述）

**创建一个自定义根轨道：**

1. 创建蓝图类，父类选 `SequencerTrackBP`，命名为 `MyCustomRootTrack`
2. 在 Class Defaults 中设置：
   - `TrackType` = `RootTrack`
   - `bSupportsMultipleRows` = `true`（如需要）
   - `DefaultSectionType` = 指向你创建的 Section 蓝图
   - `TrackInstanceType` = 指向你创建的 TrackInstance 蓝图
   - `Icon` = 设置一个图标

3. 创建蓝图类，父类选 `SequencerSectionBP`，命名为 `MyCustomSection`

4. 创建蓝图类，父类选 `SequencerTrackInstanceBP`，命名为 `MyCustomTrackInstance`
5. 在事件图表中实现 `OnUpdate` 事件——在这里编写每帧要执行的逻辑

6. 打开 Sequencer，在轨道列表中找到 `MyCustomRootTrack` 并添加

**创建一个绑定到 Actor 的对象轨道：**

1. 同上，但 `TrackType` 设为 `ObjectTrack`
2. 设置 `SupportedObjectType` 为你想要绑定的 Actor 类（如 `MyActor`）
3. 在 Sequencer 中，右键点击绑定了 `MyActor` 的对象 → Add Track → 选择你的自定义轨道

## C++ 用法

### 头文件引入

```cpp
// Runtime 模块
#include "SequencerTrackBP.h"
#include "SequencerSectionBP.h"
#include "SequencerTrackInstanceBP.h"
```

### 基本用法 — 通过 C++ 创建自定义轨道

虽然此 Plugin 主要面向蓝图，但你也可以直接用 C++ 继承这些基类：

```cpp
// MyCustomTrack.h
#pragma once

#include "SequencerTrackBP.h"
#include "MyCustomTrack.generated.h"

UCLASS(Blueprintable)
class UMyCustomTrack : public USequencerTrackBP
{
    GENERATED_BODY()

public:
    UMyCustomTrack()
    {
        TrackType = ECustomSequencerTrackType::RootTrack;
        bSupportsMultipleRows = false;
        bSupportsBlending = false;
        TrackInstanceType = UMyCustomTrackInstance::StaticClass();
        DefaultSectionType = USequencerSectionBP::StaticClass();
    }
};
```

### 进阶用法 — 自定义 TrackInstance

```cpp
// MyCustomTrackInstance.h
#pragma once

#include "SequencerTrackInstanceBP.h"
#include "MyCustomTrackInstance.generated.h"

UCLASS(Blueprintable)
class UMyCustomTrackInstance : public USequencerTrackInstanceBP
{
    GENERATED_BODY()

public:
    // C++ 版本的初始化逻辑
    virtual void OnInitialize() override
    {
        Super::OnInitialize();
        // 你的初始化代码
    }

    // C++ 版本的每帧更新逻辑
    virtual void OnAnimate() override
    {
        Super::OnAnimate();
        UObject* AnimObj = GetAnimatedObject();
        TArray<FSequencerTrackInstanceInput> Inputs = GetInputs();
        // 你的每帧逻辑
    }
};
```

> **来源**：`SequencerTrackBP.h`、`SequencerTrackInstanceBP.h`、`SequencerSectionBP.h`、`SequencerTrackBP.cpp`、`SequencerTrackInstanceBP.cpp`、`SequencerSectionBP.cpp`

## Demo 示例

此 Plugin 没有包含测试用例。以下是一个完整的最小示例，展示如何用 C++ 创建一个自定义 Sequencer 轨道。

### Build.cs 依赖

```csharp
// MyModule.Build.cs
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "MovieScene",
    "CustomizableSequencerTracks",  // Runtime 模块
});
```

### 完整示例

```cpp
// MyExampleTrack.h
#pragma once

#include "SequencerTrackBP.h"
#include "SequencerTrackInstanceBP.h"
#include "SequencerSectionBP.h"
#include "MyExampleTrack.generated.h"

// 运行时实例：在 OnUpdate 中打印日志
UCLASS(Blueprintable)
class UMyTrackInstance : public USequencerTrackInstanceBP
{
    GENERATED_BODY()

public:
    virtual void OnInitialize() override
    {
        Super::OnInitialize();
        UE_LOG(LogTemp, Log, TEXT("MyTrackInstance: Initialized"));
    }

    virtual void OnAnimate() override
    {
        Super::OnAnimate();
        UObject* Target = GetAnimatedObject();
        int32 NumInputs = GetNumInputs();
        UE_LOG(LogTemp, Verbose, TEXT("MyTrackInstance: Update, Target=%s, Inputs=%d"),
            *GetNameSafe(Target), NumInputs);
    }

    virtual void OnBeginUpdateInputs() override
    {
        Super::OnBeginUpdateInputs();
    }

    virtual void OnEndUpdateInputs() override
    {
        Super::OnEndUpdateInputs();
    }

    virtual void OnDestroyed() override
    {
        Super::OnDestroyed();
        UE_LOG(LogTemp, Log, TEXT("MyTrackInstance: Destroyed"));
    }
};

// 轨道定义：根轨道，不支持多行
UCLASS(Blueprintable)
class UMyExampleTrack : public USequencerTrackBP
{
    GENERATED_BODY()

public:
    UMyExampleTrack()
    {
        TrackType = ECustomSequencerTrackType::RootTrack;
        bSupportsMultipleRows = false;
        bSupportsBlending = false;
        DefaultSectionType = USequencerSectionBP::StaticClass();
        TrackInstanceType = UMyTrackInstance::StaticClass();
    }
};
```

使用时在 Sequencer 中通过 Add Track 菜单即可看到 `UMyExampleTrack`。由于它设置了 `TrackType = RootTrack`，会出现在顶层轨道列表中。

## 模块依赖

### CustomizableSequencerTracks（Runtime）

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心模块 |
| `CoreUObject` | UObject 系统 |
| `MovieScene` | Sequencer 的核心 Runtime 模块，提供 `UMovieSceneSection`、`UMovieSceneTrackInstance` 等基类 |
| `SlateCore` | UI 框架核心（用于 `FSlateBrush` 图标定义） |

### CustomizableSequencerTracksEditor（Editor）

| 模块 | 用途 |
|---|---|
| `AssetRegistry` | 资产注册表，用于发现蓝图自定义轨道类型 |
| `SequencerCore` | Sequencer 编辑器核心 |
| `Sequencer` | Sequencer 编辑器模块，提供 Track Editor 注册接口 |
| `EditorFramework` | 编辑器框架 |
| `UnrealEd` | Unreal 编辑器基础模块 |
| `Slate` / `SlateCore` | UI 框架 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2024-01-29 | `7ce78332` | Sequencer: Outliner UX improvements | Sequencer 大规模 UX 改进，可能涉及轨道显示方式的变化 |
| 2023-12-08 | `64658cf6` | GetAssetRegistryTags deprecation | 适配 5.4 的 `FAssetRegistryTagsContext` API 变更，`USequencerTrackBP` 加了新的 override |
| 2023-07-19 | `574e8e6e` | Add ShortName to modules | 给 Editor 模块加了 `ShortName = "CustomSeqTrEd"`，纯构建优化 |

### 维护评价

- **创建时间**：2020 年 8 月，已存在约 5.7 年
- **状态**：实验性（`IsBetaVersion=true`、`EnabledByDefault=false`）
- **更新频率**：最近 3 次提交跨越 2023-2024，均为被动维护（适配 API 变更），没有功能性更新
- **实质性更新**：自创建以来，核心功能未见重大变化，说明这套框架已经趋于稳定（或被 Epic 搁置）
- **建议**：适合用于原型验证和实验性项目。不建议在生产项目中大量依赖，因为 Epic 标记为 Beta 且不保证 API 稳定性。如果你的项目需要稳定的自定义 Sequencer 轨道，考虑直接用 C++ 继承 `UMovieSceneTrack` 体系，不依赖此 Plugin。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MovieScene/CustomizableSequencerTracks)
- 无官方文档（`.uplugin` 中 `DocsURL` 为空）
- 无测试用例
