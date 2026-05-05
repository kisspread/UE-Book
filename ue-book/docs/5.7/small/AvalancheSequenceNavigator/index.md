# Motion Design Sequence Navigator

> Sequence Navigator Bridge for embedded Motion Design Sequences

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | AvalancheSequenceNavigator (Editor, PostDefault) |
| 创建时间 | 2025-05-21 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/AvalancheSequenceNavigator) | |

## 用途

AvalancheSequenceNavigator 是 **Sequence Navigator** 插件与 **Motion Design (Avalanche)** 系统之间的桥接插件。

Motion Design 系统（原 Avalanche）在 Sequencer 中使用嵌入式的 `UAvaSequence` 来管理运动设计动画序列。然而，标准的 Sequence Navigator 工具（即 Sequencer 左侧面板中的导航树）并不知道如何展示这些特殊的嵌入式序列。

本插件充当 **Provider（数据提供者）** 的角色，向 Sequence Navigator 注册一个 `FAvaNavigationToolProvider`，使得 Motion Design 的 `UAvaSequence` 能够正确地显示在 Sequence Navigator 的树形结构中，并提供完整的管理功能（播放、添加、删除、导出等）。

**简而言之**：如果你使用 Motion Design 编辑器并需要在 Sequence Navigator 面板中管理你的序列，就需要这个插件。

## 使用场景

- 你在 Motion Design（原 Avalanche）系统中创建了嵌入式动画序列（UAvaSequence），需要在 Sequence Navigator 的树形视图中查看和管理它们
- 你需要通过 Sequence Navigator 的工具栏直接播放、停止、继续 Motion Design 序列
- 你需要将 Motion Design 序列导出为独立的 Sequencer Asset
- 你需要拖放方式重新组织序列的层级关系

## 蓝图用法

本插件不暴露任何 BlueprintCallable 函数。它是一个纯编辑器模块，所有功能通过编辑器 UI（Sequence Navigator 面板的工具栏和右键菜单）提供。

## C++ 用法

本插件的核心功能通过 Sequence Navigator 的 Provider 扩展点实现，不提供公共 API。以下信息仅供二次开发者参考。

### 头文件引入

```cpp
// 本插件的所有类都在 Private 目录下，不对外暴露公共头文件
// 如需扩展类似功能，应引用 SequenceNavigator 和 AvalancheSequencer 的公共头文件
#include "Providers/NavigationToolProvider.h"
#include "NavigationToolExtender.h"
```

### 内部架构

插件由以下核心类组成：

| 类 | 职责 |
|---|---|
| `FAvalancheSequenceNavigatorModule` | 模块入口，监听 Sequencer 创建事件，注册 Provider |
| `FAvaNavigationToolProvider` | 核心 Provider，向 Sequence Navigator 提供 Motion Design 序列数据 |
| `FNavigationToolAvaSequence` | 导航树中的序列项节点，对应一个 `UAvaSequence` |
| `FAvaSequenceNavigatorCommands` | UI 命令定义（Add、Play、Stop、Continue、Export、SpawnPlayer） |
| `FAvaNavigationToolStatusColumn` | Motion Design 专有的状态列 |
| `FAvaNavigationToolSequenceDropHandler` | 处理序列项的拖放操作 |

### 模块启动流程

```
StartupModule()
  ├─ Register FAvaSequenceNavigatorCommands
  └─ Register OnSequencerCreated callback
       └─ OnSequencerCreated()
            ├─ Listen to OnSequencerClosed
            └─ Listen to AvaSequencerSubsystem::OnSequencerCreated
                 └─ OnAvaSequencerCreated()
                      └─ Create FAvaNavigationToolProvider
                           └─ FNavigationToolExtender::RegisterToolProvider()
```

### Provider 扩展的 Sequence Navigator 功能

`FAvaNavigationToolProvider` 扩展了以下 Sequence Navigator 功能：

**列（Columns）**：

| 列 | 来源 |
|---|---|
| Playhead, DeactiveState, MarkerVisibility, Lock, Color, Label, Items, InTime, OutTime, Length, HBias, StartFrameOffset, Take, Comment | SequenceNavigator 内置列 |
| RevisionControl | 仅在 Source Control 启用时显示 |
| Status | **Motion Design 专有列**（`FAvaNavigationToolStatusColumn`） |

**默认列视图**：名为 "Motion Design"，默认显示 Color、Label、Items、Status 四列。

**内置过滤器**：Sequence、Track、Binding、Marker 四种过滤器。

**工具栏按钮**：
- ➕ Add New — 新增嵌入式序列
- ▶️ Play — 播放选中序列
- ⏭️ Continue — 继续播放选中序列
- ⏹️ Stop — 停止播放选中序列

**右键菜单**：
- Apply Preset — 将预设应用到选中序列（支持默认预设和自定义预设）
- Spawn Sequence Player — 为选中序列生成 Sequence Player Actor
- Export — 将序列导出为独立 Asset
- Duplicate / Delete / Rename — 通用操作

### Demo 示例

本插件无公共 API，无需编写代码。启用插件后，当 Motion Design 编辑器打开 Sequencer 时，Sequence Navigator 面板会自动显示 Motion Design 序列树。

## 模块依赖

本插件的 Build.cs 依赖关系如下：

### 公共依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |

### 私有依赖

| 模块 | 用途 |
|---|---|
| `Avalanche` | Motion Design（Avalanche）核心运行时 |
| `AvalancheEditorCore` | Motion Design 编辑器核心（样式、图标等） |
| `AvalancheSequence` | Motion Design 序列类型（UAvaSequence） |
| `AvalancheSequencer` | Motion Design 与 Sequencer 的集成 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `MovieScene` | Sequencer 底层序列框架 |
| `SequenceNavigator` | **Sequence Navigator** 导航工具框架 |
| `Sequencer` | UE Sequencer 编辑器 |
| `SequencerCore` | Sequencer 核心库 |
| `Slate` | Slate UI 框架 |
| `SlateCore` | Slate 核心 |
| `ToolMenus` | UE 工具菜单扩展框架 |
| `UnrealEd` | 编辑器功能 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-09-10 | `bdd5a9cb6d2e` | Motion Design: fix issue where having an operator stack, or material designer details opened would cause sequencer to not be closeable | 修复 Sequencer 无法关闭的 bug（与 operator stack / material designer 详情面板冲突） |
| 2025-08-18 | `2d3d7c8dfb5c` | [SequenceNavigator] Fix Motion Design sequence children not showing, hide unsupported column widgets, add missing includes, refresh default column view on active provider changed, fix crash on editor close, remove commented out code | 较大的修复合集：修复子序列不显示、隐藏不支持的列、修复编辑器关闭时崩溃 |
| 2025-07-28 | `fda9994cc6b8` | [SequenceNavigator] Fix Horde loop variable error | 修复编译错误（Horde CI 循环变量问题） |

### 维护评价

- **创建时间**：2025-05-21，非常新的插件（不到 1 年）
- **更新频率**：最近 3 个月内有 3 次更新，活跃维护中
- **状态**：实验性（`IsExperimentalVersion: true`，`EnabledByDefault: false`）
- **已知限制**：
  - 重命名功能（`RelabelSelection`）的 `BeginRename` 调用被注释掉，标注为 `@Todo`
  - 插件完全依赖 Motion Design（Avalanche）系统，不能独立使用
- **推荐程度**：如果你使用 Motion Design 系统，这是必需插件；否则无需启用。由于仍为实验性，可能在后续版本中有所变动。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/AvalancheSequenceNavigator)
- [SequenceNavigator 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/SequenceNavigator)（被桥接的目标插件）
- [Avalanche 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Avalanche)（Motion Design 核心插件）
