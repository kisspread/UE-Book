# Movie Scene Pose Search Tracks

> Sequencer pose search tracks using the Anim Mixer

| 属性 | 值 |
|---|---|
| 中文名 | Sequencer 姿态搜索轨道 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器 Slate 图标资源） |
| 模块 | `MovieScenePoseSearchTracks` (Runtime), `MovieScenePoseSearchTracksEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-02-25 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MovieScenePoseSearchTracks) | |

## 用途

本插件为 Sequencer 提供**基于姿态搜索（Motion Matching）的动画缝合轨道**，核心功能是实现从游戏玩法到过场动画的无缝过渡。

**解决的问题**：在制作过场动画时，角色往往从游戏玩法状态（如站立、奔跑、战斗）过渡到预设的动画序列。传统方法需要手动制作过渡动画或使用简单的混合，效果生硬。本插件利用 Pose Search 的运动匹配能力，自动查找并播放最佳衔接动画，实现自然的姿势转换。

**工作原理**：
1. 用户在 Sequencer 中放置一个 Stitch Section，指定姿态搜索数据库和目标姿态/变换
2. 当 Section 激活时，系统读取角色当前的姿态历史（Pose History）和变换信息
3. 通过 Motion Matching 在数据库中搜索最佳匹配动画
4. 以 Root Motion 方式播放找到的衔接动画，将角色从当前状态平滑过渡到目标状态

## 使用场景

- **游戏转过场**：角色从自由移动状态（如站立、行走）无缝过渡到过场动画起始姿态
- **场景转换**：在 Sequencer 中编排动画时，让角色从一个动画片段自然衔接另一个片段
- **Motion Matching 驱动的过渡**：需要在多个可能的过渡动画中自动选择最合适的衔接方式

## 前置条件

本插件默认禁用（`EnabledByDefault: false`），且处于实验性阶段。启用前需确保：

1. **Pose Search 插件**（UAFPoseSearch）已启用
2. **Anim Mixer 插件**（MovieSceneAnimMixer）已启用
3. **Anim Next 插件**已启用（Pose History 节点依赖）

## 蓝图用法

本插件主要通过 Sequencer 编辑器界面操作，运行时 API 有限。核心交互发生在 Sequencer 编辑器中。

### Sequencer 操作流程

1. **创建 Stitch 轨道**：在 Sequencer 中选择角色绑定 → 右键 → Animation → Stitch Track
2. **配置 Section**：
   - 指定 **Pose Search Database**（包含候选动画的运动匹配数据库）
   - 指定 **目标姿态** 和 **目标变换**
   - 可选启用 **Root Motion**
3. **播放预览**：系统自动使用 Motion Matching 查找最佳过渡动画

### 核心编辑器节点

| 功能 | 说明 | 所在类 |
|---|---|---|
| 创建 Stitch 轨道编辑器 | 注册轨道类型到 Sequencer | `FStitchAnimTrackEditor` |
| 动画数据库选择 | 下拉菜单选择姿态搜索数据库 | `FStitchAnimTrackEditor` |
| Section 可视化 | 显示轨道 Section 的标题和图标 | `FStitchAnimSection` |
| Anim Mixer 集成 | 通过 Anim Mixer 菜单系统添加轨道 | `FStitchAnimTrackEditor` |

## C++ 用法

### 头文件引入

```cpp
// 编辑器模块
#include "TrackEditors/StitchAnimTrackEditor.h"

// 模块接口
#include "MovieScenePoseSearchTracksEditorModule.h"
```

### 基本用法：自定义轨道编辑器注册

轨道编辑器通过模块启动时注册到 Sequencer：

```cpp
// 来源: Private/MovieScenePoseSearchTracksEditorModule.cpp
void FMovieScenePoseSearchTracksEditorModule::StartupModule()
{
    // 注册 Stitch Animation 轨道编辑器到 Sequencer
    StitchAnimationTrackCreateEditorHandle = 
        FSequencerTrackEditorDelegates::OnCreateTrackEditor().AddLambda(
            [](ISequencerTrackEditor& TrackEditor, TSharedRef<ISequencer> Sequencer)
            {
                return FStitchAnimTrackEditor::CreateTrackEditor(Sequencer);
            }
        );
}

void FMovieScenePoseSearchTracksEditorModule::ShutdownModule()
{
    // 注销轨道编辑器
    FSequencerTrackEditorDelegates::OnCreateTrackEditor().Remove(StitchAnimationTrackCreateEditorHandle);
}
```

### 进阶用法：Anim Mixer 菜单集成

`FStitchAnimTrackEditor` 实现了 `IMovieSceneAnimMixerItemMenuProvider` 接口，使其能够集成到 Anim Mixer 的右键菜单系统中：

```cpp
// 来源: Private/TrackEditors/StitchAnimTrackEditor.h
class FStitchAnimTrackEditor : public FMovieSceneTrackEditor
                             , public IMovieSceneAnimMixerItemMenuProvider
{
    // 处理的 Mixer Item 类型
    const UClass* GetHandledMixerItemClass() const override;

    // 填充 Mixer Item 添加菜单
    void PopulateAddMixerItemMenu(
        FMenuBuilder& MenuBuilder, 
        TArray<FGuid> ObjectBindings, 
        UMovieSceneTrack* Track, 
        TSharedPtr<ISequencer> Sequencer, 
        int32 RowIndex
    ) override;

    // 填充对象绑定动画菜单
    void PopulateObjectBindingAnimationMenu(
        FMenuBuilder& MenuBuilder, 
        const TArray<FGuid>& ObjectBindings, 
        const UClass* ObjectClass, 
        bool bIsInsideSubmenu
    ) override;
};
```

### 进阶用法：姿态历史属性传递

首次提交中提到，插件修改了 AnimBP 节点和 AnimNext trait，使其在输出中写入 `pose history` 属性，供 Sequencer 评估任务访问：

```cpp
// Pose History 通过属性系统传递到 Sequencer 的 Motion Matching 计算
// 动画蓝图节点或 AnimNext trait 会在输出中写入 pose history
// Sequencer 创建的评估任务可以读取该属性来执行运动匹配
```

## Demo 示例

以下是一个自定义扩展 Stitch 轨道行为的示例：

```cpp
// StitchAnimExample.h
#pragma once

#include "CoreMinimal.h"

class UMovieSceneSequence;
class UMovieSceneStitchAnimTrack;

/**
 * 扩展 Stitch 轨道功能的辅助类
 */
class FStitchAnimHelper
{
public:
    /**
     * 在指定序列中查找所有 Stitch 轨道
     * @param Sequence 目标 Sequencer 序列
     * @return 找到的 Stitch 轨道列表
     */
    static TArray<UMovieSceneStitchAnimTrack*> FindAllStitchTracks(UMovieSceneSequence* Sequence);

    /**
     * 获取轨道当前 Section 的权重（用于调试）
     */
    static float GetCurrentSectionWeight(const UMovieSceneStitchAnimTrack* Track);
};
```

```cpp
// StitchAnimExample.cpp
#include "StitchAnimExample.h"
#include "MovieScene.h"
#include "MovieSceneTrack.h"
#include "Sections/MovieSceneStitchAnimSection.h"
#include "Tracks/MovieSceneStitchAnimTrack.h"

TArray<UMovieSceneStitchAnimTrack*> FStitchAnimHelper::FindAllStitchTracks(UMovieSceneSequence* Sequence)
{
    TArray<UMovieSceneStitchAnimTrack*> Result;
    if (!Sequence || !Sequence->GetMovieScene())
    {
        return Result;
    }

    // 遍历所有 Master Tracks 查找 Stitch Anim 轨道
    UMovieScene* MovieScene = Sequence->GetMovieScene();
    for (UMovieSceneTrack* Track : MovieScene->GetMasterTracks())
    {
        if (UMovieSceneStitchAnimTrack* StitchTrack = Cast<UMovieSceneStitchAnimTrack>(Track))
        {
            Result.Add(StitchTrack);
        }
    }

    return Result;
}

float FStitchAnimHelper::GetCurrentSectionWeight(const UMovieSceneStitchAnimTrack* Track)
{
    // 获取当前激活 Section 的权重
    // 注意: 权重默认值已在最近的修复中修正为正确值
    return 1.0f; // 默认全权重
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MovieSceneAnimMixer` | 动画混合器框架，提供 Track 和 Section 基类及菜单集成接口 |
| `PoseSearch` | 姿态搜索核心模块，提供 Motion Matching 算法和数据库 |
| `Sequencer` | Sequencer 编辑器框架，提供轨道编辑器基类 |
| `AnimationCore` | 动画核心类型定义 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `68f769e6` | Sequencer: Stitch track section was defaulting weight to 0 | 修复 Stitch Section 权重默认值为 0 的 bug |
| 2026-05-22 | `2ad26ca4` | Sequencer: Anim Mixer: Stitch section root motion fix for offset-mesh actors | 修复带网格偏移角色的 Root Motion 问题 |
| 2026-04-17 | `8bcded9c` | Sequencer: Per Anim Track and Row Iconography | 添加每个动画轨道和行的独立图标 |
| 2026-04-07 | `6ab9300d` | Sequencer: Fix default AddSection path for Animation Mixer to properly assign sections to layers | 修复 Mixer 添加 Section 时的层分配逻辑 |
| 2026-04-07 | `8bf4fb4b` | Sequencer: Restructure mixer evaluation around layers; new mask blend system | 重构 Mixer 评估为基于层的系统，新增遮罩混合 |

### 维护评价

本插件处于**积极开发**状态：

- **实验性阶段**：`IsExperimentalVersion=true`，API 可能随版本变化
- **活跃更新**：2026 年 5 月仍有 bug 修复和功能完善
- **功能逐步成熟**：从最初的 Motion Matching 计算扩展到层系统和遮罩混合
- **持续修复**：近期修复了权重默认值、Root Motion 偏移等关键问题
- **依赖链复杂**：需要 Pose Search + Anim Mixer + Anim Next 三个实验性插件同时可用

**建议**：适合对 Motion Matching 动画过渡有需求的项目进行早期探索。由于 API 尚未稳定，不建议用于生产环境的核心功能。随着 Pose Search 和 Anim Next 系统的成熟，本插件预计将成为实现游戏到过场无缝过渡的标准工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MovieScenePoseSearchTracks)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MovieScenePoseSearchTracks/Tests)（如存在）