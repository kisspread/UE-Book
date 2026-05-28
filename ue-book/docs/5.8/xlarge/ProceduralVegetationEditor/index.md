# Procedural Vegetation Editor

> Node Graph based Editor that allows users to create Nanite Foliage ready vegetation directly in the engine. Users can load Procedural Vegetation Presets that contain prebuilt data for a species, and customize/create variations using the node graph.

| 属性 | 值 |
|---|---|
| 中文名 | 程序化植被编辑器 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（示例资产） |
| 模块 | `ProceduralVegetation` (Runtime), `ProceduralVegetationEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-29 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ProceduralVegetationEditor) | |

## 用途

这是一个基于节点图的程序化植被编辑器，解决在 UE5 中高效创建 Nanite Foliage 可用植被资产的问题。

核心流程：用户加载预制的植被物种预设（包含某物种的预构建数据），然后通过节点图界面自定义和创建变体。这种方式比手动建模或使用传统 Foliage Tool 更适合大量植被变体的批量生产。

## 使用场景

- 你需要为开放世界游戏批量生成不同树种的 Nanite 可用变体 → 使用此插件的节点图工作流
- 你有植被物种的预设数据，需要快速自定义尺寸、密度、枝叶分布等参数 → 加载预设后在节点图中调整
- 你希望植被资产导出后可直接用于 Nanite 渲染管线 → 该插件专为此场景设计

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `ProceduralVegetation` | Runtime | 核心数据模型与程序化生成逻辑 |
| `ProceduralVegetationEditor` | Runtime | 节点图编辑器 UI 与交互层 |

详见各模块文档：[ProceduralVegetation.md](ProceduralVegetation.md) · [ProceduralVegetationEditor.md](ProceduralVegetationEditor.md)

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `6587e553` | [PVE] Fix for Material look broken in the saved sample content. | 修复示例资产中材质显示异常 |
| 2026-05-22 | `ef6788f5` | Fix crash on platforms using HotReload where ProceduralVegetationEditor.plugin attempts to register | 修复 HotReload 平台上的注册崩溃 |
| 2026-05-21 | `5b49f4b9` | [PV] Fixed Incorrect/misleading and missing tooltips for the following nodes | 修正多个节点的工具提示文本 |
| 2026-05-21 | `461f91d8` | Re-write PV::Export::Internal::ReplaceAssetInPackage to resolve various crashes in the engine when o | 重写资产替换逻辑以修复引擎崩溃 |
| 2026-05-20 | `dc74565d` | [PVE] Major fixes | 大规模修复 |

### 维护评价

该插件处于**活跃维护**状态。创建于 2025 年 8 月，近一个月（2026 年 5 月）连续有多次实质性的 bug 修复和稳定性改进，包括材质修复、崩溃修复、节点提示修正等。

⚠️ 注意事项：
- 位于 `Experimental` 目录，API 和功能可能发生重大变更
- 首次提交已注明示例资产材质有问题，后续提交正在逐步修复
- 源码规模较大（347 文件），属于 **xlarge** 级别插件，文档已按模块拆分

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ProceduralVegetationEditor)
- 测试用例：未发现独立测试文件