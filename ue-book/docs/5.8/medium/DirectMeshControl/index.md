# Direct Mesh Control

> Animate using click & drag and surface selection.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画资产） |
| 模块 | `DirectMeshControl` (Runtime), `DirectMeshControlRig` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-14 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Animation/DirectMeshControl) | |

## 用途

Direct Mesh Control 插件提供了一种直观的动画制作方式，允许用户通过直接点击、拖拽网格表面来创建和编辑动画。它解决了传统动画制作流程中需要预先设置骨骼、权重绘制等复杂步骤的问题，旨在让动画师能够像操作物理对象一样直接操纵模型表面，从而快速实现角色表情、物体变形等动画效果。

## 使用场景

- 你是一名动画师，需要快速为角色制作面部表情或口型动画 → 使用 Direct Mesh Control 直接拖拽面部网格点。
- 你正在开发一个需要实时物体变形的游戏（如软体物理、可破坏环境），希望提供直观的编辑工具 → 使用此插件在编辑器中直接“雕刻”动画状态。
- 你需要为过场动画中的道具或环境元素制作复杂的形变动画，但不想依赖复杂的骨骼系统 → 使用此插件进行基于表面的直接控制。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| `DirectMeshControl` | Runtime | 提供核心的网格表面选择、交互与动画数据管理功能。 |
| `DirectMeshControlRig` | Runtime | 将 Direct Mesh Control 的动画数据与 UE5 的动画系统（Control Rig）进行集成。 |

### 近期更新

- 2026-04-24 `7faab2ed` Direct Mesh Control: fixed library and proxies being GCd
- 2026-04-16 `090ee041` Animation Mode: support for hovered state and colors for gizmo libraries
- 2026-04-15 `f5734c77` Direct Mesh Control: documentation pass
- 2026-04-14 `da21a789` Direct Mesh Control: remove useless logs
- 2026-04-14 `331f0ab8` Direct Mesh Control: force DMC components animation updates in editor

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Animation/DirectMeshControl)