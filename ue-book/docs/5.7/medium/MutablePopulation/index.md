# MutablePopulation

> Extend the Mutable plugin to support Population assets.

| 属性 | 值 |
|---|---|
| 中文名 | 人群生成 |
| 分类 | CustomizableObjects |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（人口资产蓝图） |
| 模块 | `CustomizableObjectPopulation` (Runtime), `CustomizableObjectPopulationEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-03-13 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MutablePopulation) | |

## 总体用途

MutablePopulation 是对 **Mutable（可定制对象）** 系统的扩展，专门用于**生成和管理具有随机变异的个体集合（Population）**。它允许开发者定义一套外观变体规则（如身体部件、颜色、材质、纹理等），然后在运行时批量生成大量外观各异的角色个体，且每个个体都是基于 Mutable 实时组合出的唯一实例。适用于需要大量随机 NPC 的场景（如开放世界人群、射击游戏敌人、过场路人），在节省内存和加载时间的同时保证外观多样性。

该插件提供核心运行时逻辑（`CustomizableObjectPopulation`）和编辑器工具（`CustomizableObjectPopulationEditor`），帮助设计师可视化配置人口资产。

## 模块概览

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| `CustomizableObjectPopulation` | Runtime | 定义人口数据资产、生成规则及运行时实例化逻辑，负责根据变体配置随机生产个体。 |
| `CustomizableObjectPopulationEditor` | Editor | 提供编辑器 UI 资产类型、自定义面板和操作命令，用于创建和预览人口资产。 |

更多详细信息请参阅各模块文档：
- [CustomizableObjectPopulation 模块](CustomizableObjectPopulation.md)
- [CustomizableObjectPopulationEditor 模块](CustomizableObjectPopulationEditor.md)

## 使用场景

- **开放世界人群**：在城镇、广场、集市等区域快速生成大量穿着服饰各异的路人，每个角色外观独一无二。
- **射击游戏敌人**：为不同敌人类型（士兵、暴徒、特种兵）生成随机外观，避免角色重复感。
- **过场动画路人**：在剧情场景中填充随机背景角色，无需手动摆放每个 NPC。
- **玩家自定义扩展**：内置 Mutable 的玩家捏人系统之外，为 NPC 提供一套独立的随机化逻辑。

## 维护状态

### 近期更新

- 2025-06-10 `bb3758b4` 修复 `SEditorViewport::MakeViewportToolbar()` 弃用告警。
- 2025-05-29 `f5ac91eb` 移除无效的 U 宏标记，修复编译警告。
- 2025-04-29 `13d19592` 修复使用 3 个或更多人群类时可能发生的随机崩溃。
- 2025-03-26 `634dfda6` 将所有可定制对象编辑器的标签统一为“资产名称”，提升 UX。
- 2025-03-13 `b059f7b4` 修复琐碎不可达代码警告。

### 维护评价

- **创建时间**：2025-03-13，距今不足半年。
- **近期更新频率**：每周都有功能性或修复性提交，尤其针对稳定性（随机崩溃修复）。
- **活跃度**：非常活跃，持续跟进引擎 API 变化并修复缺陷。
- **实验性状态**：插件标记为实验性（`IsExperimentalVersion: true`），但代码质量良好、有明确用途，适合愿意接受少量 API 变动的项目。
- **推荐度**：推荐用于需要自动化随机角色生成的 Mutable 项目，注意当前为实验版本，大规模生产前建议充分测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MutablePopulation)
- [Mutable 插件文档](https://docs.unrealengine.com/5.7/zh-CN/mutable-overview/)（插件依赖 Mutable，可参考其官方文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/MutablePopulation/Source/CustomizableObjectPopulation/Private/Tests/)（如果存在，此处为推测路径）