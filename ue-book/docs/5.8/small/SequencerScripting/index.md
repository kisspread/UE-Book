# Sequencer Scripting

> Python and editor utility scripting extensions for sequencer and movie scenes

| 属性 | 值 |
|---|---|
| 中文名 | 序列器脚本 |
| 分类 | Scripting |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（脚本工具资产） |
| 模块 | `SequencerScripting` (Runtime), `SequencerScriptingEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-05-09 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/SequencerScripting) | |

## 用途

这个插件为 UE 的 Sequencer（序列器）和 Movie Scene 系统提供 Python 脚本接口。通过它，你可以用 Python 自动化控制序列器中的各种元素：

- 创建和管理 Level Sequence、Master Track
- 添加和编辑 Possessable/Spawnable 绑定
- 操作轨道（Track）和片段（Section）
- 读写关键帧、曲线数据
- 批量处理动画录制任务

此外还提供编辑器工具扩展（Editor Utility），让蓝图也能通过工具函数操作序列器，简化动画制作流程。

## 使用场景

- **自动化动画制作**：需要批量创建/修改 Level Sequence 中的关键帧数据
- **Python 批处理**：通过 Python 脚本批量处理多个序列资产
- **编辑器工具开发**：创建自定义编辑器工具来操作 Sequencer
- **动画录制工作流**：通过脚本控制动画录制的启停和配置

## 子模块列表

| 模块 | 类型 | 文档 | 说明 |
|---|---|---|---|
| `SequencerScripting` | Runtime | [SequencerScripting.md](SequencerScripting.md) | 运行时脚本核心，提供 Python/蓝图访问序列器的 API |
| `SequencerScriptingEditor` | Runtime | [SequencerScriptingEditor.md](SequencerScriptingEditor.md) | 编辑器专用扩展，提供更高层级的工具函数 |

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MovieScene` | Sequencer 核心运行时模块 |
| `LevelSequence` | Level Sequence 资产运行时支持 |
| `SequencerCore` | Sequencer 编辑器核心功能 |
| `LevelSequenceEditor` | Level Sequence 编辑器集成 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `b209798d` | Anim In Engine: Add bRemoveExcludedCurves option to animation recording so we can remove curves alre... | 为动画录制添加移除排除曲线的选项 |
| 2026-04-24 | `8b8110b4` | [EDA] Add Sequencer tool wrappers + fix sequencer toolset tests | 添加序列器工具包装器并修复工具集测试 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF |
| 2026-04-10 | `77af3950` | [EDA] Add SequencerTools toolset with Anim Mixer split into separate plugin | 添加 SequencerTools 工具集，Anim Mixer 拆分为独立插件 |
| 2026-04-10 | `8bd8f719` | [Backout] - CL52569948 | 回退某个提交 |

### 维护评价

- **状态**：活跃维护中
- 最近一次更新距今不到 3 个月（2026-05-12），更新频繁
- 持续有功能增强（SequencerTools 工具集、动画录制改进）
- 插件标记为 `IsBetaVersion=true`，API 可能会有变动
- **推荐使用**：✅ 适合需要通过 Python/蓝图自动化操作 Sequencer 的场景，但需注意 Beta 状态意味着接口可能随版本变化

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/SequencerScripting)
- 官方文档：无
- 子模块文档：[SequencerScripting.md](SequencerScripting.md) | [SequencerScriptingEditor.md](SequencerScriptingEditor.md)