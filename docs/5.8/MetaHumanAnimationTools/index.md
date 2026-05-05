# MetaHuman Animation Tools

> Tooling for working with MetaHuman Animation data.

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画数据资产） |
| 模块 | `MetaHumanAnimationSerialization` (Runtime), `MetaHumanAnimationSerializationEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2026-02-02 |
| 年龄标签 | 🆕（未来） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimationTools) | |

## 用途

该插件为 MetaHuman 角色的动画数据提供了一套专用的序列化与反序列化工具。它解决的核心问题是将外部的 MetaHuman 动画数据（如面部捕捉数据）高效、准确地导入到 Unreal Engine 中，并使其能够在引擎内被正确读取、编辑和使用。插件通过分离运行时序列化逻辑与编辑器集成逻辑，确保了动画数据在打包后的游戏中也能被正确处理。

## 使用场景

- 你正在使用 MetaHuman 角色，并需要从专业的面部动捕设备（如 iPhone 的 ARKit 数据）导入动画数据。
- 你需要在编辑器中预览、编辑或混合来自不同来源的 MetaHuman 面部动画。
- 你的项目需要将 MetaHuman 动画数据打包到最终发行版本中，并确保其在运行时能被正确加载和播放。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| `MetaHumanAnimationSerialization` | Runtime | 提供 MetaHuman 动画数据的核心序列化与反序列化功能，是运行时数据处理的基础。 |
| `MetaHumanAnimationSerializationEditor` | Editor | 提供在 Unreal Editor 中导入、预览和编辑 MetaHuman 动画数据的工具与界面集成。 |

### 近期更新

- 2026-02-03 `f39fc2f9` 修正文件名拼写错误
- 2026-02-02 `b1aae96f` 新增插件，用于高效序列化面部动画曲线数据

### 维护评价

该插件近期有连续的提交记录，且内容包含错误修复与新功能开发，表明其处于**活跃维护**状态。从提交内容看，开发团队正在积极完善功能并优化代码质量，插件可能正处于功能扩展与稳定化阶段。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimationTools)