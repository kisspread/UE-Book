# Movie Scene Pose Search Tracks

> Sequencer pose search tracks using the Anim Mixer

| 属性 | 值 |
|---|---|
| 中文名 | 动画混合姿势搜索轨道 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `MovieScenePoseSearchTracks` (Runtime), `MovieScenePoseSearchTracksEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-02-25 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MovieScenePoseSearchTracks) | |

## 用途
本插件为 Sequencer 提供了基于运动匹配（Motion Matching）技术的动画轨道。它允许动画师在 Sequencer 时间线中创建“缝合轨道”（Stitch Track），通过引用一个运动匹配数据库和一个目标姿势，当该片段激活时，系统会自动根据角色的历史姿态/运动轨迹，计算出最合适的动画片段来无缝连接当前状态与目标状态。这解决了从游戏玩法（Gameplay）无缝过渡到预设过场动画的难题，使得动画衔接更加自然流畅。

## 使用场景
- 你需要在过场动画中创建一个角色从游戏状态（如奔跑）自然过渡到某个特定表演姿势（如停在特定点转身说话）的平滑动画。
- 你希望基于角色的实时运动轨迹，动态计算并播放一段衔接动画，用于进入复杂的定格动画序列。
- 你需要利用运动匹配数据库中的动画，为 Sequencer 中的动画制作提供更智能、更符合物理逻辑的过渡。

## 蓝图用法
此插件主要提供 Sequencer 编辑器内的自定义轨道和片段。动画师或设计师直接在 Sequencer 中通过UI操作进行使用，而非通过蓝图节点调用。核心操作是在 Sequencer 轨道列表中添加 “Animation Stitch Track”，然后在其下方的 Section 中配置运动匹配数据库资产和目标姿势。

### 核心节点
此插件功能主要通过 Sequencer 编辑器UI暴露，无直接蓝图函数节点。

## C++ 用法
本插件主要为 Sequencer 编辑器和运行时提供自定义轨道类型和评估逻辑。开发者在扩展或调试时可能会接触以下接口。

### 头文件引入
```cpp
// Runtime 模块
#include "MovieScenePoseSearchTracks.h"
// Editor 模块
#include "MovieScenePoseSearchTracksEditor.h"
```

### 基本用法
插件的核心是实现了 `UMovieSceneStitchTrack` 和 `UMovieSceneStitchSection`，它们作为 Sequencer 的自定义轨道和片段运行。运行时评估逻辑由 `FMovieSceneStitchSectionTemplate` 处理，该模板在 Sequencer 播放时触发运动匹配计算并播放生成的动画。

### 进阶用法
此插件与 `MovieSceneAnimMixer` 和 `UAFPoseSearch` 插件深度集成。它修改了动画蓝图中的姿态历史（Pose History）节点，使其输出一个“姿态历史”属性，该属性在运行时被 Sequencer 评估任务访问，作为运动匹配计算的关键输入。开发者若要定制匹配逻辑，需深入理解 `PoseSearch` 模块的接口。

## Demo 示例
此插件的示例体现在 Sequencer 编辑器中。在启用插件后，可以：
1.  创建或打开一个关卡序列。
2.  在动画角色上添加轨道，选择 “Animation Stitch Track”。
3.  在新增的轨道片段上，设置一个运动匹配数据库资产和一个目标姿势。
4.  播放序列，观察角色如何根据其之前的运动轨迹，自动播放一段过渡动画，最终到达目标姿势。

## 模块依赖
此插件运行和编辑所依赖的独特模块（已省略 Core, Engine, Slate 等常见依赖）：

| 模块 | 用途 |
|---|---|
| `MovieSceneAnimMixer` | 提供 Sequencer 中的动画混合轨道框架和运行时评估基础设施 |
| `PoseSearch` | 提供运动匹配（Motion Matching）的核心算法和功能 |
| `UAFPoseSearch` | 提供统一动画框架（UAF）下的姿势搜索特性 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `68f769e6` | Sequencer: Stitch track section was defaulting weight to 0 | 修复缝合轨道片段权重默认值为0的问题。 |
| 2026-05-22 | `2ad26ca4` | Sequencer: Anim Mixer: Stitch section root motion fix for offset-mesh actors | 修复了网格体偏移角色在缝合片段中根运动的计算问题。 |
| 2026-04-17 | `8bcded9c` | Sequencer: Per Anim Track and Row Iconography | 为动画轨道和行增加了新的图标显示。 |
| 2026-04-07 | `6ab9300d` | Sequencer: Fix default AddSection path for Animation Mixer to properly assign sections to layers | 修复了动画混合器添加片段默认路径，确保片段正确分配到对应层。 |
| 2026-04-07 | `8bf4fb4b` | Sequencer: Restructure mixer evaluation around layers; new mask blend system | 重构了混合器的评估逻辑，围绕“层”进行组织，并引入了新的遮罩混合系统。 |

### 维护评价
- **创建时间**: 约2年前创建，属于较新的实验性插件。
- **近期活动**: 近半年有持续的更新（2026年4-5月），修复bug并改进功能（如根运动、权重、层系统），表明正在**积极维护**。
- **活跃度**: 非常活跃。作为实验性插件，仍在快速迭代和增加功能。
- **已知限制**: 作为实验性（`IsExperimentalVersion: true`）且默认未启用（`EnabledByDefault: false`）的插件，其API和功能在正式版中可能会有变动。目前主要功能是“缝合轨道”，未来可能会扩展。
- **推荐使用**: 如果你正在开发需要高级动画过渡（尤其是过场动画）的项目，并且愿意承担实验性API的风险，**推荐尝试**。它是连接 Gameplay 动画与 Sequencer 的强大工具。不建议用于追求长期稳定性的项目。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MovieScenePoseSearchTracks)
- [官方文档]() (暂无)
- [测试用例]() (在插件目录或 `Engine/Tests` 下，需具体查找)