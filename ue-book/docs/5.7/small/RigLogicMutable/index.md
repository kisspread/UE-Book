# RigLogic Extensions For Mutable

> Adds Mutable functionality to work with RigLogic DNA

| 属性 | 值 |
|---|---|
| 中文名 | 可变绑定逻辑扩展 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RigLogicMutable` (Runtime), `RigLogicMutableEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-12-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RigLogicMutable) | |

## 总体用途

RigLogicMutable 是 RigLogic 与 Mutable 定制化系统的桥梁。它允许在 **Mutable 可自定义对象**（CustomizableObject）中直接引用和驱动 **RigLogic DNA** 数据，从而实现在运行时动态生成的骨骼网格体上应用面部绑定、肌肉模拟等基于 DNA 的动画逻辑。解决了两套系统单独使用时无法协同工作的问题：没有此插件，基于 Mutable 动态生成的网格体将无法与 RigLogic 的 DNA 数据进行绑定和实时变形。

## 模块列表

| 模块 | 一句话总结 | 文档 |
|---|---|---|
| `RigLogicMutable` (Runtime) | 运行时核心：提供 DNA 数据读取、与 Mutable 模型的集成逻辑，以及运行时更新骨骼网格体实例的接口 | [RigLogicMutable.md](RigLogicMutable.md) |
| `RigLogicMutableEditor` (UncookedOnly) | 编辑器支持：允许在 Mutable 定制化资产中导入/配置 DNA 文件，并提供编辑器内预览与调试功能 | [RigLogicMutableEditor.md](RigLogicMutableEditor.md) |

## 使用场景

- **面部绑定与实时定制**：你正在开发一款支持捏脸/换装的角色创建系统，使用 Mutable 动态生成头部网格，并需要同时保留 RigLogic 的面部动画（例如眨眼、口型同步）——此插件让两者在生成时自动对齐 DNA 数据。
- **基于 DNA 的角色变形**：在 Mutable 模型的不同变体中（如不同体型、不同种族角色），无需重复导出多个 DNA 文件，只需一份 DNA 并利用此插件的映射逻辑，动态适配不同拓扑或蒙皮权重。
- **游戏内动态换装保留表情**：当玩家更换服装/装备、并通过 Mutable 替换网格部件时，RigLogic 驱动的表情仍然能够正确作用于新生成的骨骼网格体。

## 使用前提

- 项目已启用 `RigLogic` 和 `Mutable` 插件（在 `.uproject` 或编辑器插件列表中勾选）。
- 需要在 `.Build.cs` 的 `PublicDependencyModuleNames` 中添加 `"RigLogicMutable"`（运行时模块）或 `"RigLogicMutableEditor"`（编辑器模块）。

## 维护状态

### 近期更新

| 日期 | 哈希 | Commit 内容 |
|---|---|---|
| 2025-09-01 | `75e4adbd` | [Mutable] 更改命名空间名称 |
| 2025-06-20 | `1ec52cfd` | [Mutable] 允许在游戏模式下加载和重新编译 CustomizableObject 模型 |
| 2025-02-06 | `41fd6b90` | [mutable] 修复移除 AddParticipatingObjects 方法后的编译问题 |
| 2025-01-29 | `ea8756da` | [Mutable] 将 ModelResources 转换为 UObject |
| 2024-12-09 | `17fd035f` | [RigLogicMutable] 修复生成带 DNA 的骨骼网格体时游戏崩溃的 Bug |

### 维护评价

属于实验性插件，创建至今约一年，持续有缺陷修复和适配 Mutable 底层变化（如命名空间、UObject 转换）的提交。最近一次实质性更新（2025-09）涉及命名空间变更，表明仍在主动维护，但改动以适配上游 Mutable 更新为主。稳定性尚可，但不推荐用于最终发布项目；若需要使用 RigLogic + Mutable 的组合，应优先考虑此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RigLogicMutable)
- [RigLogic 插件文档](https://docs.unrealengine.com/5.7/en-US/rig-logic-plugin-for-unreal-engine/)（*RigLogic 官方文档*）
- [Mutable 定制化系统文档](https://docs.unrealengine.com/5.7/en-US/mutable-customization-system/)（*Mutable 官方文档*）
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/RigLogicMutable/Tests/RigLogicMutableTest.cpp)（示例单元测试）