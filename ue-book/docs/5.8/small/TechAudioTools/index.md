# Tech Audio Tools

> A collection of audio-related tools and utilities.

| 属性 | 值 |
|---|---|
| 中文名 | 音频技术工具集 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `TechAudioTools` (Runtime), `TechAudioToolsMetaSound` (Runtime), `TechAudioToolsMetaSoundEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TechAudioTools) | |

## 用途

TechAudioTools 是 Epic 为 MetaSound 系统提供的底层技术工具集，主要用于扩展 MetaSound 的数据类型支持和编辑器行为。插件围绕 **MetaSound Pin 类型注册**和 **Literal ViewModel（字面量视图模型）** 展开，解决以下问题：

- 自定义 MetaSound 节点的 Pin 类型注册与编辑器中的可视化行为
- 在 MetaSound 编辑器中支持 MVVM 模式管理节点属性的输入/输出
- 提供事务（Transaction）支持以实现 MetaSound 图的撤销/重做操作

该插件依赖 ModelViewViewModel（MVVM）插件，表明其采用了 MVVM 架构来解耦 MetaSound 编辑器的 UI 与数据逻辑。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| [`TechAudioTools`](TechAudioTools.md) | Runtime | 核心运行时模块，提供音频工具的基础功能和 Pin 类型注册 |
| [`TechAudioToolsMetaSound`](TechAudioToolsMetaSound.md) | Runtime | MetaSound 运行时扩展，处理 MetaSound Literal ViewModel 和数据模型 |
| [`TechAudioToolsMetaSoundEditor`](TechAudioToolsMetaSoundEditor.md) | Editor | MetaSound 编辑器扩展，管理 Pin 类型在编辑器中的注册与行为 |

## 使用场景

- 你在开发自定义 MetaSound 节点并需要注册新的 Pin 数据类型
- 你需要在 MetaSound 编辑器中为自定义数据类型提供 Literal（字面量）输入 UI
- 你需要通过 MVVM 模式管理 MetaSound 编辑器中的节点属性编辑
- 你需要在 MetaSound 图编辑中支持完整的撤销/重做（Transaction）功能

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MetaSound` | MetaSound 音频系统核心 |
| `ModelViewViewModel` | MVVM 框架，用于编辑器 UI 数据绑定 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-16 | `cb44584a` | MetaSound: Consolidate pin type registration and associated pin-related MetaSound Editor behavior in | 整合 Pin 类型注册及相关编辑器行为 |
| 2026-04-15 | `2010cdbb` | [Backout] - CL52717658 - CIS Compile Error | 回滚上一次提交以修复编译错误 |
| 2026-04-14 | `d9dda16b` | MetaSound: Consolidate pin type registration and associated pin-related MetaSound Editor behavior in | 整合 Pin 类型注册（后被回滚） |
| 2026-04-09 | `77ec5174` | [TechAudioTools] Added support for transactions in MetaSound Literal Viewmodels | 为 Literal ViewModel 添加事务支持 |
| 2026-03-16 | `e8ed118a` | DocumentConfiguration Rename to MetaSound(Document)Template | 重命名 DocumentConfiguration 为 MetaSound Template |

### 维护评价

- **状态**：活跃维护中
- **分析**：插件创建于 2025 年 4 月，距今不到 1 年，最近一个月内有多次功能性更新，表明处于积极开发阶段
- **注意**：标记为实验性和 Beta 版本（`IsBetaVersion=true`, `IsExperimentalVersion=true`），`Installed=false` 表示不会默认安装
- **推荐度**：适合在实验项目中尝试使用，但不建议在生产环境中依赖。API 可能发生 breaking changes

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TechAudioTools)
- [官方文档]()（暂无）
- [测试用例]()（暂未发现独立测试文件）