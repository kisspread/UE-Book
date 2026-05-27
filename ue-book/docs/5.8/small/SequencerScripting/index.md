# Sequencer Scripting

> Python and editor utility scripting extensions for sequencer and movie scenes

| 属性 | 值 |
|---|---|
| 中文名 | Sequencer 脚本扩展 |
| 分类 | Scripting |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `SequencerScripting` (Runtime), `SequencerScriptingEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-05-09 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/SequencerScripting) | |

## 用途

SequencerScripting 为 UE5 的 Sequencer（序列器）和 MovieScene 系统提供 Python 和蓝图脚本接口，解决批量操作动画序列、自动化影视流程管线的需求。

核心价值：
- **批量创建/修改序列**：通过 Python 脚本批量创建 Level Sequence、添加绑定（Bindings）、轨道（Tracks）、片段（Sections），适合影视制作中大量镜头的自动化
- **导出/导入能力**：支持导出 FBX 和 Alembic 格式的动画数据，便于与 Maya、Houdini 等 DCC 工具交换数据
- **编辑器工具开发**：提供 Sequencer Scripting Layer，可在 C++ 中实现自定义的 Sequencer 工具和工作流
- **动画混合与重定向**：包含动画重定向、混合、烘焙等高级功能，支持复杂的角色动画工作流

## 使用场景

- 你是影视制作 TD，需要批量创建数百个镜头的 Level Sequence → 用 Python + SequencerScripting 自动化
- 你需要把 Sequencer 中的关键帧动画导出到 FBX 交给动画师 → 用 FBX Export 功能
- 你要构建自定义的 Sequencer 工具面板（如动画混合器）→ 用 Sequencer Tools 扩展
- 你需要在运行时通过蓝图读取/控制序列播放 → 用蓝图 API 操作 UMovieSceneSequence

## 模块概览

| 模块 | 类型 | 职责 |
|---|---|---|
| `SequencerScripting` | Runtime | 核心运行时功能：Python 脚本绑定、蓝图函数、FBX/Alembic 导出、动画重定向 |
| `SequencerScriptingEditor` | Runtime | 编辑器扩展：Sequencer Scripting Layer、Sequencer 工具集、自定义轨道面板 |

详细 API 请参阅各子模块文档：
- [SequencerScripting](SequencerScripting.md) — 运行时核心 API
- [SequencerScriptingEditor](SequencerScriptingEditor.md) — 编辑器扩展 API

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/SequencerScripting)
- [SequencerScripting 子模块文档](SequencerScripting.md)
- [SequencerScriptingEditor 子模块文档](SequencerScriptingEditor.md)

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `b209798d` | Anim In Engine: Add bRemoveExcludedCurves option to animation recording so we can remove curves alre | 动画录制新增排除曲线选项 |
| 2026-04-24 | `8b8110b4` | [EDA] Add Sequencer tool wrappers + fix sequencer toolset tests | 新增 Sequencer 工具包装器并修复工具集测试 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移到 UE_LOGF 格式 |
| 2026-04-10 | `77af3950` | [EDA] Add SequencerTools toolset with Anim Mixer split into separate plugin | SequencerTools 工具集拆分为独立插件 |
| 2026-04-10 | `8bd8f719` | [Backout] - CL52569948 | 回退之前的变更 |

### 维护评价

**活跃维护** — 该插件近期（2026 年 4-5 月）仍有多次功能性更新，包括新增 Sequencer 工具包装器、动画混合器拆分、录制功能增强等。作为 Epic 官方维护的 Sequencer 脚本扩展，它处于持续开发状态。

⚠️ **注意**：该插件标记为 `IsBetaVersion = true`，且 `Installed = false`（不随引擎默认安装），需要手动启用。API 可能在版本间发生变化。

✅ **推荐使用**：对于需要 Python/蓝图自动化 Sequencer 工作流的项目，这是官方推荐的解决方案，处于活跃维护状态。