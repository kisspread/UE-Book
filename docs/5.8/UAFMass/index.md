# UAF Mass

> Mass integration for UAF.

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UAFMass` (Runtime), `UAFMassTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-02-17 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFMass) | |

## 用途

该插件为 Unreal Animation Framework (UAF) 提供了与 Mass 框架的集成。其核心目的是将 UAF 的动画能力（如动画图、动画实例）适配到 Mass 实体框架中，从而支持对海量实体（例如成千上万的 NPC 或单位）进行高效、可扩展的动画驱动和更新。它解决了在大型开放世界或 RTS 游戏中，传统基于 Actor 的动画系统无法高效处理大量角色动画的问题。

## 使用场景

- 你正在开发一个拥有大量 NPC 或生物的开放世界游戏，需要为它们提供流畅且性能可控的动画。
- 你正在制作一个即时战略（RTS）游戏，需要同时驱动屏幕上成百上千个单位的动画状态。
- 你希望利用 Mass 框架的数据导向设计来优化动画系统的内存布局和缓存命中率。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| **UAFMass** | Runtime | 核心运行时模块，提供将 UAF 动画系统集成到 Mass 框架所需的处理器、片段和模板。 |
| **UAFMassTests** | Runtime | 自动化测试模块，用于验证 UAFMass 核心功能的正确性。 |

*详细的 API 和用法请参考各模块的独立文档：[UAFMass.md](UAFMass.md) 和 [UAFMassTests.md](UAFMassTests.md)。*

### 近期更新

- 2026-04-23 `746b6abb` 将UAF-Mass轨迹桥接功能移入引擎UAFMass插件
- 2026-04-01 `58888966` [MassCore] 将头文件移至Public/Mass/子目录，并移除文件名中的Mass前缀
- 2026-03-30 `161605b0` [Mass] 从MassEntity模块中提取出MassCore模块
- 2026-03-11 `1d291fa1` [Mass] 为UMassObserverProcessor添加多片段观察者支持
- 2026-02-17 `baf983b4` [提交工具 - UAF] 为UAF插件添加验证器，以构建和运行低级测试

### 维护评价

该插件近期维护状态活跃。在约两个月的时间内进行了五次提交，频率较高。提交内容涵盖了核心模块重构、功能增强和测试基础设施建设，表明插件正在经历积极的架构优化和功能完善。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFMass)
- [官方文档]() (暂无)
- [测试用例]() (暂无)