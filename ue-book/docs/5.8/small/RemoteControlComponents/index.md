# Remote Control Components

> 

| 属性 | 值 |
|---|---|
| 中文名 | 远程控制组件 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RemoteControlComponents` (Runtime), `RemoteControlComponentsEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-29 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/RemoteControlComponents) | |

## 用途

该插件是 UE5 远程控制（Remote Control）生态系统的一部分，为特定功能（例如 Motion Design）提供专用的组件。它扩展了远程控制的能力，可能包含用于在编辑器中设计阶段或运行时远程控制对象的特定组件实现。

## 使用场景

- 你在使用 **Motion Design** 工具链进行动态图形设计时，需要远程控制场景中的对象属性。
- 你需要为**远程控制面板（Remote Control Panel）** 提供特定的组件来暴露和控制对象。
- 你的工作流涉及在编辑器中通过网络远程控制和调试 Actor 或组件。

## 模块列表

- **`RemoteControlComponents` (Runtime)**
    运行时核心模块，提供用于远程控制的特定组件实现。
- **`RemoteControlComponentsEditor` (Runtime)**
    提供与编辑器集成相关的运行时功能，用于支持远程控制组件的编辑器交互。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2024-02-14 | `c579ba10` | Motion Design: | 与 Motion Design 功能相关的更新。 |
| 2024-02-13 | `723c2005` | [Remote Control Components] Remove “invalid” tracked properties from Tracker | 移除跟踪器中“无效”的已跟踪属性，优化属性管理。 |
| 2024-02-12 | `10de4dbc` | Remote Control: | 与 Remote Control 框架相关的更新。 |
| 2024-02-09 | `236f2d2f` | Remote Control Components: | 插件本体的功能或维护性更新。 |
| 2024-02-07 | `1f30386d` | Motion Design RC: | Motion Design 远程控制相关功能的更新。 |

### 维护评价

该插件创建于 2024 年 1 月底，最近一次实质性更新停留在 2024 年 2 月中旬。此后超过一年半没有新的提交记录。它被标记为 `ExperimentalVersion`，且未设置为默认启用，表明它仍处于实验性阶段，可能尚未达到稳定发布状态。**鉴于长期无更新，目前该插件可能处于不活跃维护或已被搁置的状态，不建议在生产项目中依赖。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/RemoteControlComponents)
- 官方文档：无
- 测试用例：未在插件目录内发现专用测试。