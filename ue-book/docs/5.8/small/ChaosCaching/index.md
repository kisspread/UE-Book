# ChaosCaching

> Chaos Cache asset support for recording and playing back physics simulations

| 属性 | 值 |
|---|---|
| 中文名 | 混沌物理缓存 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（缓存资产、蓝图类） |
| 模块 | `ChaosCaching` (Runtime), `ChaosCachingEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-09-01 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosCaching) | |

## 用途

ChaosCaching 插件为 Chaos 物理引擎提供了**模拟录制与回放**能力。在游戏开发中，复杂的物理破碎、布料、刚体交互等效果在运行时计算开销大且结果不确定。该插件允许开发者：

1. **预录** Chaos 物理模拟过程（刚体、几何集合、布料、Niagara 粒子等），将模拟结果序列化到缓存资产中
2. **回放** 缓存数据，实现确定性的物理效果，无需运行时重复计算
3. **精确控制** 回放的时机、速度和位置

核心应用场景是将昂贵的离线物理模拟烘焙为资产，在运行时廉价播放，确保视觉效果一致且可控。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `ChaosCaching` | Runtime | 核心缓存运行时，提供缓存资产类型、录制/回放框架、各类物理对象的缓存适配器（刚体、几何集合、布料、Niagara） |
| `ChaosCachingEditor` | Editor | 编辑器工具，提供缓存资产的编辑器预览、Sequencer 集成、蓝图类资产创建菜单、内容浏览器集成 |

## 使用场景

- 你在做一个需要大规模物理破碎的场景，但不想运行时实时计算 → 使用 ChaosCaching 预录破碎过程
- 你需要精确控制破碎动画的时间线和触发时机 → 将物理模拟烘焙到 Sequencer 可控制的缓存中
- 你需要在网络同步中播放一致的物理效果 → 缓存回放提供确定性结果
- 你希望在过场动画中使用复杂的物理交互但性能有限 → 预录模拟回放替代实时计算

## 子模块文档

- [ChaosCaching（运行时核心）](ChaosCaching.md) — 缓存资产、录制/回放框架、物理对象适配器
- [ChaosCachingEditor（编辑器工具）](ChaosCachingEditor.md) — 编辑器预览、Sequencer 集成、蓝图类工厂

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ChaosSolverEngine` | Chaos 求解器引擎接口 |
| `Chaos` | Chaos 物理核心库 |
| `ChaosCore` | Chaos 基础数据类型 |
| `GeometryCollectionEngine` | 几何集合引擎（破碎体） |
| `Niagara` | Niagara 粒子系统集成 |
| `NiagaraCore` | Niagara 核心类型 |
| `SequencerScripting` | Sequencer 蓝图脚本接口 |

插件级依赖：`Takes`（Take 录制系统）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的警告 |
| 2026-05-12 | `d4c60147` | Geometry collection cache adapter : fix logic issue when dealing with root proxies | 修复几何集合缓存适配器处理根代理时的逻辑问题 |
| 2026-05-12 | `24eff459` | Chaos : Add trailing data to Chaos Event Relay | 为 Chaos 事件中继添加尾部数据 |
| 2026-04-14 | `0d40a411` | [ContentBrowser] New Add Menu Physics Menu | 内容浏览器新增物理菜单分类 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏从 UE_LOG 到 UE_LOGF |

### 维护评价

- **状态**：仍在活跃维护，近期有多次功能修复和改进
- **实验性**：插件标记为 `IsExperimentalVersion=true`，未默认启用，表明 Epic 认为 API 仍可能变动
- **稳定性**：从 commit 历史看，主要是 bug 修复和代码质量改进，非颠覆性重构
- **推荐度**：适合在需要物理模拟录制回放的项目中使用，但需注意实验性状态意味着未来 API 可能变化

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosCaching)