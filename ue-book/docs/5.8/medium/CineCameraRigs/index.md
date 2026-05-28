# CineCameraRigs

> Extended camera rigs for cinematic workflow

| 属性 | 值 |
|---|---|
| 中文名 | 电影摄影机支架 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资源） |
| 模块 | `CineCameraRigs` (Runtime), `CineCameraRigsEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-01-31 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/CineCameraRigs) | |

## 用途

该插件为虚幻引擎的虚拟制作（Virtual Production）工作流提供了扩展的摄影机支架系统。其核心目标是解决电影级别摄影机运动控制的痛点，特别是复杂的沿轨道运动（Rail）。它通过一个自定义的样条线组件来存储摄影机数据和运动参数，实现了对摄影机运动曲线（如速度）的精确控制和可视化。此外，还引入了元数据插值选项，允许将自定义属性与摄影机运动同步，从而实现更丰富、可控的电影镜头效果。

## 使用场景

- **虚拟拍摄/电影制作**：你需要在虚拟场景中创建并控制一个摄影机沿预设的复杂轨道（Rail）进行平滑运动，以模拟摇臂、轨道车等专业设备的效果。
- **精确运动控制**：你需要不仅控制摄影机的路径，还希望精细调整其沿路径的速度曲线，并直观地在编辑器中看到速度变化（速度可视化）。
- **元数据同步**：你需要将特定的事件、参数或信号（如焦点变化、特效触发）与摄影机的运动进度绑定。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `CineCameraRigs` | Runtime | 核心运行时模块，包含 `CineCameraRigRail`、自定义样条线组件等基础类，负责摄影机支架的逻辑、运动计算和数据管理。 |
| `CineCameraRigsEditor` | Editor | 编辑器扩展模块，提供用于配置、可视化（如速度曲线）和控制摄影机支架的编辑器工具与 UI。 |

## 蓝图用法

### 核心节点

以下为核心蓝图节点（基于插件结构推断）：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Attach to Rig Rail` | 将一个 Actor（通常是虚拟摄影机）附加到指定的 `CineCameraRigRail` 上，使其跟随轨道运动。 | `CineCameraRigRail` |
| `Set Speed Visualization` | 启用或禁用沿轨道运动的速度可视化显示。 | `CineCameraRigRail` |
| `Set Rail Progress` | 设置附加在轨道上的 Actor 的运动进度（0.0 到 1.0）。 | `CineCameraRigRail` |

### 使用示例（蓝图描述）

1.  在场景中放置一个 `CineCameraRigRail` Actor。
2.  在蓝图中，获取该 `CineCameraRigRail` 的引用。
3.  使用 `Attach to Rig Rail` 节点，将你的虚拟摄影机 Actor 附加到该轨道上。
4.  通过 `Set Rail Progress` 节点，在时间轴（Timeline）或 Sequencer 中驱动进度参数，使摄影机沿轨道运动。
5.  启用 `Set Speed Visualization` 以在编辑器视口中直观查看运动速度曲线。

## C++ 用法

### 头文件引入

```cpp
#include "CineCameraRigRail.h"
#include "CineSplineComponent.h"
```

### 基本用法

创建并使用 `CineCameraRigRail` 来控制摄影机运动。
```cpp
// 假设在某个 Actor 或 Component 中
ACineCameraRigRail* Rail = GetWorld()->SpawnActor<ACineCameraRigRail>(ACineCameraRigRail::StaticClass());

// 获取其内部的 CineSplineComponent
UCineSplineComponent* SplineComp = Rail->GetCineSplineComponent();

// 配置样条点或通过编辑器编辑路径

// 将一个摄影机 Actor 附加到轨道
AVirtualCameraActor* MyCamera = GetMyVirtualCamera();
Rail->AttachCameraToRail(MyCamera);

// 在 Tick 或 Sequencer 轨道中更新进度
float Progress = 0.5f; // 可以随时间变化
Rail->SetProgress(Progress);
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。该插件依赖于 `.uplugin` 中声明的 `EditorScriptingUtilities`、`ConcertSyncCore`、`SequencerScripting` 和 `LevelSequenceEditor` 等插件，但这些是插件级依赖，不是使用者模块需要在 `Build.cs` 中直接引用的。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `ddded373` | Fix CineSpline parallel-curve desync when metadata properties are written directly by self-healing v | 修复 CineSpline 并行曲线在直接写入元数据属性时出现的同步问题，通过自愈机制修复。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF。 |
| 2026-02-03 | `4fc77002` | [Sequencer] Few small API export tweaks to allow to use these classes outside of sequencer. | 对 Sequencer 相关 API 进行小的导出调整，使其能在 Sequencer 之外使用。 |
| 2025-12-19 | `a01aeeaa` | check for UObjectInitialized  && !IsEngineExitRequested() before running clean-up code that involves | 在运行涉及 UObject 的清理代码前，增加对 UObject 已初始化且引擎未请求退出的检查。 |
| 2025-12-18 | `d951ccc8` | Adding metadata interpolation option for CineCameraRigRail | 为 CineCameraRigRail 添加元数据插值选项。 |

### 维护评价

**活跃维护**。该插件创建于 2023 年，虽然在 `Experimental` 文件夹下且默认未启用（`IsBetaVersion=true`），但近期有持续的功能性更新和 bug 修复，表明 Epic 团队仍在积极开发和维护。最近的更新集中在修复核心的样条线同步问题、增强 API 的灵活性以及完善元数据功能，这些都属于实质性改进。**推荐**在虚拟制作项目中关注和使用此插件，但需注意其“实验性”状态可能意味着 API 未来仍有变动的可能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/CineCameraRigs)
- [官方文档](https://epicgames.com)（暂无专门文档链接）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/CineCameraRigs)（路径为推测，实际测试用例可能位于其他位置）