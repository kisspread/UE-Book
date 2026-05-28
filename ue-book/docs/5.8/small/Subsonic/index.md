# Subsonic

> Subsonic is a high-level audio authoring and playback system. This plugin is experimental and as such there is no guarantee of backward compatibility.

| 属性 | 值 |
|---|---|
| 中文名 | 音频编排系统 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（音频资产、测试资源） |
| 模块 | `SubsonicCore` (Runtime), `SubsonicEditor` (Runtime), `SubsonicEngine` (Runtime), `SubsonicEngineTest` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-01-12 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic) | |

## 用途

Subsonic 是 UE5 的高层音频编排与播放系统，用于替代或增强传统的 Sound Cue 工作流。它提供了面向创作的音频播放接口，支持更灵活的音频事件编排和运行时控制。与底层 AudioMixer 不同，Subsonic 关注的是"音频创作"层面——如何组织、触发和混合多个音频源，适合需要复杂音频逻辑的项目。

## 使用场景

- 你需要一个比 Sound Cue 更灵活的音频编排系统 → 用 Subsonic
- 你要构建复杂的音频事件链（如动态环境音、交互式音乐）→ 用 Subsonic
- 你需要在编辑器中可视化编辑音频播放流程 → 用 SubsonicEditor 模块
- 你正在搭建项目音频架构，希望使用 Epic 推荐的新一代音频系统 → 评估 Subsonic

## 模块一览

| 模块 | 类型 | 说明 |
|---|---|---|
| [`SubsonicCore`](SubsonicCore.md) | Runtime | 核心数据类型和基础结构定义 |
| [`SubsonicEngine`](SubsonicEngine.md) | Runtime | 音频引擎运行时，处理播放、混合和更新逻辑 |
| [`SubsonicEditor`](SubsonicEditor.md) | Runtime | 编辑器集成，提供音频资产的编辑器工具和 UI |
| [`SubsonicEngineTest`](SubsonicEngineTest.md) | Runtime | 自动化测试套件，验证引擎核心功能 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic)
- 官方文档：暂无
- [SubsonicCore 文档](SubsonicCore.md)
- [SubsonicEngine 文档](SubsonicEngine.md)
- [SubsonicEditor 文档](SubsonicEditor.md)
- [SubsonicEngineTest 文档](SubsonicEngineTest.md)

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `0ad6a1ff` | [Audio, CIS] Fixup bad merge: Revert wholesale Subsonic Subscriber stomp; apply minimal non-deprecat | 修复合并冲突，回滚错误的 Subscriber 覆盖 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决 FSoundWaveData API 废弃相关的合并冲突 |
| 2026-04-23 | `129c3dc2` | Fix/silence PVS warnings | 修复静态分析警告 |
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | ContentBrowser 中新增音频菜单入口 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移至新格式 |

### 维护评价

- **状态**：活跃开发中（2026-01 创建，最近更新 2026-05）
- **实验性**：标记为 `IsExperimentalVersion=true`，API 不保证向后兼容
- **建议**：可关注和试用，但不建议用于需要稳定 API 的生产环境。该系统正在快速迭代中，近期有多次合并修复和功能新增。