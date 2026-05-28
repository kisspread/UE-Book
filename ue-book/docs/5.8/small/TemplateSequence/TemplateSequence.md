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
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/TemplateSequence) | |

## 用途

TemplateSequence 是 Sequencer 系统的扩展，核心解决的是**序列复用**问题。

普通的 LevelSequence 绑定的是特定 Actor 实例，无法在多个地方共享。TemplateSequence 定义了一个**模板**——以一个 Spawnable 对象作为根对象，播放时才绑定到实际的目标对象上。这样同一个序列可以：

1. **在场景中多实例化**：一个相机动画序列可以被多个 `ATemplateSequenceActor` 同时使用，每个绑定不同的相机。
2. **驱动属性缩放**：模板序列中的属性可以被"缩放"（Scale），比如动画中定义的震动幅度可以按需放大或缩小。
3. **实现相机抖动（Camera Shake）**：通过 `USequenceCameraShakePattern`，Sequencer 动画可以直接用作相机抖动效果，这是该插件最典型的用途。

简单来说：**TemplateSequence = 可复用的 Sequencer 动画片段**。

## 使用场景

- 你需要制作一个通用的相机震动效果，希望在爆炸、撞击等多处复用 → 用 TemplateSequence 创建相机动画序列 + SequenceCameraShakePattern
- 你想在 Sequencer 中嵌入可复用的动画片段，而不是每次都重新制作 → 用 TemplateSequenceTrack 嵌入模板序列
- 你需要在场景中放置多个 Actor 各自播放同一个动画序列，但绑定不同对象 → 用 ATemplateSequenceActor
- 你需要对模板序列中的属性进行动态缩放（如根据距离调整震动强度）→ 使用 PropertyScale 机制

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Template Sequence Player` | 静态方法，创建模板序列播放器并返回 Actor | `UTemplateSequencePlayer` |
| `Get Sequence` | 获取当前绑定的模板序列 | `ATemplateSequenceActor` |
| `Load Sequence` | 加载并获取模板序列 | `ATemplateSequenceActor` |
| `Set Sequence` | 设置要播放的模板序列 | `ATemplateSequenceActor` |
| `Set Binding` | 设置模板序列绑定的目标 Actor | `ATemplateSequenceActor` |
| `Get Sequence Player` | 获取序列播放器实例 | `ATemplateSequenceActor` |

### 使用示例（蓝图描述）

**方式一：通过 Actor 在场景中播放模板序列**

1. 在场景中放置一个 `ATemplateSequenceActor`
2. 在 Details 面板中设置 `TemplateSequence` 属性指向你的 `UTemplateSequence` 资产
3. 设置 `PlaybackSettings` 配置播放参数（循环、播放速率等）
4. 调用 `Set Binding` 绑定目标 Actor
5. 游戏开始时自动播放，或通过 `SequencePlayer` 蓝图属性手动控制

**方式二：通过蓝图动态创建播放器**

1. 调用 `UTemplateSequencePlayer::CreateTemplateSequencePlayer`，传入世界上下文、模板序列资产和播放设置
2. 函数会自动生成 `ATemplateSequenceActor` 并通过 `OutActor` 输出参数返回
3. 通过返回的 Actor 进一步设置绑定和播放参数

**方式三：相机抖动**

1. 创建一个 `UCameraAnimationSequence`（模板序列的子类，专为相机设计）
2. 在相机抖动蓝图资产中，选择 `USequenceCameraShakePattern` 作为抖动模式
3. 将 `UCameraAnimationSequence` 赋给 `Sequence` 属性
4. 配置 `PlayRate`、`Scale`、`BlendInTime`、`BlendOutTime` 等参数
5. 通过 `PlayCameraShake` 等节点触发抖动

## C++ 用法

### 头文件引入

```cpp
#include "TemplateSequencePlayer.h"
#include "TemplateSequenceActor.h"
#include "TemplateSequence.h"
#include "CameraAnimationSequence.h"
#include "SequenceCameraShake.h"
```

### 基本用法：创建模板序列播放器

来源：`Public/TemplateSequencePlayer.h`

```cpp
// 在任意位置动态创建模板序列播放器
ATemplateSequenceActor* OutActor = nullptr;
UTemplateSequence* MyTemplateSeq = LoadObject<UTemplateSequence>(nullptr, TEXT("/Game/MyTemplateSeq"));

FMovieSceneSequencePlaybackSettings Settings;
Settings.bAutoPlay = true;
Settings.PlayRate = 1.0f;

UTemplateSequencePlayer* Player = UTemplateSequencePlayer::CreateTemplateSequencePlayer(
    GetWorld(),
    MyTemplateSeq,
    Settings,
    OutActor
);

// 绑定目标 Actor
if (OutActor)
{
    OutActor->SetBinding(MyTargetActor, true);
}
```

### 基本用法：相机动画序列播放器

来源：`Public/CameraAnimationSequencePlayer.h`

```cpp
// UCameraAnimationSequencePlayer 是轻量级播放器，专用于相机动画
UCameraAnimationSequencePlayer* Player = NewObject<UCameraAnimationSequencePlayer>();
Player->Initialize(CameraAnimSequence, /*StartOffset=*/0, /*DurationOverride=*/0.f);
Player->Play(/*bLoop=*/false, /*bRandomStartTime=*/true);

// 每帧更新
Player->Update(CurrentFrameTime);

// 获取当前位置
FFrameTime Pos = Player->GetCurrentPosition();

// 播放结束后停止
Player->Stop();
```

### 进阶用法：相机抖动模式

来源：`Public/SequenceCameraShake.h`

```cpp
// 创建基于 Sequencer 的相机抖动
USequenceCameraShakePattern* ShakePattern = NewObject<USequenceCameraShakePattern>();
ShakePattern->Sequence = CameraAnimationSeq;  // UCameraAnimationSequence*
ShakePattern->PlayRate = 1.0f;
ShakePattern->Scale = 1.0f;
ShakePattern->BlendInTime = 0.2f;
ShakePattern->BlendOutTime = 0.5f;
ShakePattern->bRandomSegment = false;

// 将此模式挂载到相机管理器上使用
// PlayCameraShake(ShakePattern->GetClass(), Scale);
```

### 进阶用法：属性缩放

来源：`Public/Sections/TemplateSequenceSection.h` + `Public/TemplateSequenceComponentTypes.h`

```cpp
// 模板序列支持对内部属性进行缩放控制
// 可以缩放 Float 属性、Transform 的位移部分、或 Transform 的旋转部分
ETemplateSectionPropertyScaleType ScaleType = ETemplateSectionPropertyScaleType::FloatProperty;

// 在 TemplateSequenceSection 中添加属性缩放
FTemplateSectionPropertyScale PropertyScale;
PropertyScale.ObjectBinding = SomeBindingGuid;
PropertyScale.PropertyBinding = SomePropertyBinding;
PropertyScale.PropertyScaleType = ETemplateSectionPropertyScaleType::TransformPropertyLocationOnly;
// FloatChannel 定义缩放曲线
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MovieScene` | Sequencer 核心运行时，提供 Entity System 框架 |
| `LevelSequence` | LevelSequence 运行时，模板序列的基础播放能力 |
| `LevelSequenceEditor` | 编辑器集成（插件依赖声明） |
| `CinematicCamera` | 相机镜头参数（Filmback、Lens、Focus 等） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点的编译警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移到 UE_LOGF 新宏 |
| 2026-04-10 | `c03b3afd` | PR #14610: Rep layout mismatch in level sequence player due to with editoronly data property | 修复 LevelSequencePlayer 因 editoronly 数据属性导致的复制布局不匹配 |
| 2026-02-20 | `49054c9f` | Sequencer: Add Bake Transform to object binding menu | 在对象绑定菜单中添加"烘焙变换"功能 |
| 2026-02-11 | `5919e4fa` | Remove 7 virtual functions in UObject (either deprecated or toolonly) | 清理 UObject 中 7 个已废弃的虚函数 |

### 维护评价

该插件创建于 2019 年，至今已有约 7 年历史。从最近的提交记录来看，2026 年仍有持续更新，但主要集中在**代码质量维护**（编译警告修复、宏迁移、虚函数清理）和**底层框架适配**（复制布局修复），而非功能扩展。

需要注意的几点：

1. **仍标记为实验性**（`IsBetaVersion=true`）且默认不启用（`EnabledByDefault=false`），说明 Epic 尚未将其视为稳定 API
2. 插件依赖 `LevelSequenceEditor`，这意味着它与编辑器工具链深度绑定
3. 最近没有新增功能的迹象，维护方向以稳定性和兼容性为主
4. 作为 Sequencer 子系统的一部分，只要 Sequencer 持续维护，该插件也会间接受益

**推荐程度**：如果你需要**基于 Sequencer 的相机抖动**或**可复用的序列动画**，这是官方推荐的实现路径（UE5 的相机抖动系统底层就是它）。但由于标记为实验性，生产环境中使用需注意 API 可能在未来版本发生变化。建议关注版本升级时的 Breaking Changes。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/TemplateSequence)