# Template Sequence

> Runtime for template sequences

| 属性 | 值 |
|---|---|
| 中文名 | 模板序列 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `TemplateSequence` (Runtime), `TemplateSequenceEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-10-02 |
| 年龄标签 | 🏛️ 文物（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/TemplateSequence) | |

## 用途

Template Sequence 插件提供了一种**可复用的序列模板**机制，允许你创建绑定到特定 Actor 类型的 Sequencer 序列，然后在多个地方复用。它的核心理念是：先定义一个"模板序列"并绑定到某类对象（如 Camera Actor），之后在 Sequencer 中可以直接引用该模板，实现动画的复用和参数化覆盖。

该插件最重要的实际用途是 **Camera Animation Sequence（摄像机动画序列）**——一种特殊的模板序列，专门用于创建可复用的摄像机动画。这些摄像机动画可以在 Sequencer 中被添加到任意摄像机 Actor 上，并支持叠加（additive）、属性缩放（property scaling）等高级功能。

插件解决的核心问题：在 Sequencer 中，Level Sequence 绑定的是具体 Actor 实例，无法直接复用。Template Sequence 通过抽象绑定到 Actor **类**而非实例，实现了序列资产的模板化复用。

## 使用场景

- 你在做一个需要大量摄像机动画的游戏（如过场动画、镜头震动、视角切换）→ 创建 Camera Animation Sequence 模板，重复引用到不同的摄像机上
- 你需要创建可复用的 Sequencer 动画模板，绑定到特定 Actor 类型 → 使用 Template Sequence
- 你需要在 Sequencer 中将同一段动画以叠加方式应用到摄像机上，并控制初始偏移 → 使用 Camera Animation Sequence 的 Additive 功能
- 你需要对模板序列中的动画属性进行缩放控制（如调整动画的速度、强度）→ 使用 Property Scaling 功能

## 蓝图用法

该插件主要是**编辑器工具**（Editor module），提供的可调用 API 主要集中在运行时模块中的实体系统。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `EnableNextFrame` | 启用下一帧的摄像机预览（将编辑器视口变换写入摄像机初始变换） | `UTemplateSequenceCameraPreviewSystem` |
| `DisableNextFrame` | 禁用摄像机预览（将摄像机初始变换恢复到原点） | `UTemplateSequenceCameraPreviewSystem` |

> **注意**：该插件的大部分功能通过 Sequencer 编辑器 UI 暴露（拖放资产、右键菜单、工具栏按钮），而非传统的蓝图节点。

### 使用示例（编辑器操作描述）

1. **创建模板序列**：在 Content Browser 中右键 → Cinematics → Template Sequence / Camera Animation Sequence，选择绑定的目标 Actor 类
2. **在 Sequencer 中使用**：在 Sequencer 中对 Actor 添加 Track → Template Sequence Track → 选择一个已创建的模板序列资产
3. **拖放操作**：支持直接将模板序列资产、Actor 或类拖放到 Sequencer 面板中自动创建绑定
4. **摄像机叠加设置**：编辑 Camera Animation Sequence 时，可通过视图菜单切换 "Camera Initially Additive to Viewport"，将当前视口位置作为叠加初始值

## C++ 用法

### 头文件引入

```cpp
// Runtime 模块（在你的项目中使用模板序列运行时功能）
#include "TemplateSequence.h"

// Editor 模块（仅在编辑器工具中使用）
#include "TemplateSequenceEditor.h"
```

### 基本用法 — 创建模板序列资产

通过工厂类在代码中创建新的 Template Sequence 资产。

```cpp
// 来源: Private/Factories/TemplateSequenceFactoryUtil.h
#include "TemplateSequenceFactoryUtil.h"
#include "TemplateSequence.h"

// 创建一个绑定到特定 Actor 类的模板序列
UTemplateSequence* NewSequence = FTemplateSequenceFactoryUtil::CreateTemplateSequence(
    InParent,                                    // 父包
    FName("MyTemplateSequence"),                 // 资产名
    RF_Transactional,                            // 对象标志
    UTemplateSequence::StaticClass(),            // 序列类
    ACameraActor::StaticClass()                  // 绑定的目标 Actor 类
);
```

### 基本用法 — 自定义编辑器工具包参数

```cpp
// 来源: Private/TemplateSequenceEditorToolkit.h
#include "TemplateSequenceEditorToolkit.h"

// 配置工具包参数
FTemplateSequenceToolkitParams ToolkitParams;
ToolkitParams.bCanChangeBinding = false;  // 禁止修改绑定类

// 初始化编辑器
TSharedRef<FTemplateSequenceEditorToolkit> Toolkit = MakeShared<FTemplateSequenceEditorToolkit>(Style);
Toolkit->Initialize(
    EToolkitMode::Standalone,
    nullptr,
    MyTemplateSequence,
    ToolkitParams
);
```

### 进阶用法 — 修改绑定 Actor

```cpp
// 来源: Private/Misc/TemplateSequenceEditorUtil.h
#include "TemplateSequenceEditorUtil.h"

// 在 Sequencer 编辑会话中动态修改模板序列绑定的目标 Actor
FTemplateSequenceEditorUtil Util(TemplateSequence, *Sequencer);
Util.ChangeActorBinding(
    NewActor,              // 新的绑定对象
    nullptr,               // ActorFactory（可选）
    true                   // 是否设置默认值
);
```

### 进阶用法 — 编辑器设置

```cpp
// 来源: Private/Misc/TemplateSequenceEditorSettings.h
#include "TemplateSequenceEditorSettings.h"

// 通过项目设置控制编辑器行为
UTemplateSequenceEditorSettings* Settings = GetMutableDefault<UTemplateSequenceEditorSettings>();

// 在 Camera Animation Track 的资产选择器中显示过时资产
Settings->bShowOutdatedAssetsInCameraAnimationTrackEditor = true;

// 设置视口位置作为叠加摄像机段的初始值
Settings->bCameraInitiallyAdditiveToViewport = true;
Settings->SaveConfig();
```

## Demo 示例

以下展示如何创建一个自定义的 Sequencer Track Editor，处理模板序列的 Track 编辑逻辑：

```cpp
// MyCustomTemplateSequenceHandler.h
#pragma once

#include "CoreMinimal.h"
#include "TemplateSequence/Sections/TemplateSequenceSection.h"

class FMyTemplateSequenceHandler
{
public:
    void HandleTemplateSequenceBinding(UObject* BoundObject, UTemplateSequence* Sequence);

    // 查询模板序列中可缩放的动画属性
    TArray<FScalablePropertyInfo> GetScalableProperties(const UTemplateSequenceSection* Section) const;
};
```

```cpp
// MyCustomTemplateSequenceHandler.cpp
#include "MyCustomTemplateSequenceHandler.h"
#include "TemplateSequence.h"
#include "TemplateSequence/Sections/TemplateSequenceSection.h"

void FMyTemplateSequenceHandler::HandleTemplateSequenceBinding(
    UObject* BoundObject,
    UTemplateSequence* Sequence)
{
    if (!BoundObject || !Sequence)
    {
        return;
    }

    // 获取序列的绑定信息
    FMovieSceneSequenceIDRef TemplateSequenceID = MovieSceneSequenceID::Root;
    UMovieScene* MovieScene = Sequence->GetMovieScene();

    if (MovieScene)
    {
        // 遍历所有 spawnable 并检查绑定类
        for (int32 i = 0; i < MovieScene->GetSpawnableCount(); ++i)
        {
            FMovieSceneSpawnable& Spawnable = MovieScene->GetSpawnable(i);
            UClass* SpawnableClass = Spawnable.GetClass();

            if (SpawnableClass && BoundObject->IsA(SpawnableClass))
            {
                // 找到匹配的绑定，执行后续逻辑
                UE_LOG(LogTemp, Log, TEXT("Matched binding: %s"), *Spawnable.GetName());
            }
        }
    }
}
```

## 模块依赖

### TemplateSequence（Runtime）

| 模块 | 用途 |
|---|---|
| `LevelSequence` | 基础的 Level Sequence 运行时支持 |
| `MovieScene` | Sequencer 核心运行时框架 |
| `MovieSceneTracks` | 标准 Sequencer Track 运行时 |

### TemplateSequenceEditor（Editor）

| 模块 | 用途 |
|---|---|
| `LevelSequenceEditor` | Level Sequence 编辑器基础设施 |
| `TemplateSequence` | 对应的 Runtime 模块 |
| `SequencerCore` | Sequencer 核心编辑器 API |
| `AssetDefinition` | 资产类型定义框架 |

> 插件还依赖 `LevelSequenceEditor` 插件（已在 .uplugin 中声明）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 转 float 的编译警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移为 UE_LOGF 格式 |
| 2026-04-10 | `c03b3afd` | PR #14610: Rep layout mismatch in level sequence player due to with editoronly data property | 修复因 editoronly 属性导致的序列播放器复制布局不匹配 |
| 2026-02-20 | `49054c9f` | Sequencer: Add Bake Transform to object binding menu | 在对象绑定右键菜单中添加"烘焙变换"功能 |
| 2026-02-11 | `5919e4fa` | Remove 7 virtual functions in UObject (either deprecated or toolonly) | 移除 UObject 中 7 个已废弃或仅工具使用的虚函数 |

### 维护评价

- **维护状态**：维护中但非活跃开发。近期更新均为编译修复、API 迁移和框架跟随性改动，无实质性新功能
- **创建时间**：2019 年创建，已存在约 7 年
- **实验性状态**：`.uplugin` 中 `IsBetaVersion=true` 且 `EnabledByDefault=false`，表明 Epic 官方仍将其视为实验性功能
- **代码质量**：架构清晰，模块化良好，Runtime/Editor 分离合理
- **已知限制**：默认不启用，需要在插件管理器中手动开启；Camera Animation Sequence 的叠加模式在某些复杂场景下可能需要手动调优

> ⚠️ **注意**：该插件标记为 Beta 且默认禁用，已在 UE5 中存在约 7 年仍未"毕业"。建议关注 Epic 官方更新，确认其是否会被正式纳入或被新方案替代。在生产项目中使用时需评估稳定性风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/TemplateSequence)
- [LevelSequenceEditor 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/LevelSequenceEditor)（前置依赖）