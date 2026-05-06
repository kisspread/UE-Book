# Water

> Full suite of water tools and rendering techniques to easily add oceans, river, lakes or custom water bodies that carve landscape and interacts with gameplay

| 属性 | 值 |
|---|---|
| 中文名 | 水体系统 |
| 分类 | Water |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质、网格体） |
| 模块 | `Water` (Runtime), `WaterEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-03 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Water) | |

## 总体用途

Water 插件为 Unreal Engine 提供了完整的水体创作与渲染工具集。它支持快速添加海洋、河流、湖泊以及自定义水体，这些水体能够自动雕刻景观地形，并且支持游戏逻辑交互（如游泳、漂浮、水流影响）。该插件基于 Niagra 粒子系统实现动态波浪与泡沫效果，同时利用自定义的物理材质与后处理体积实现水面的光学效果。它还包含编辑器扩展，用于可视化的水体绘制和自动景观改造。

## 模块列表

| 模块 | 类型 | 一句话描述 |
|---|---|---|
| [Water](Water.md) | Runtime | 提供水体核心运行时组件、渲染代理、物理交互接口以及水体参数管理。 |
| [WaterEditor](WaterEditor.md) | Editor | 提供水体编辑器工具，包括水体 Actor 放置、景观雕刻预览、波浪编辑器以及材质实例管理。 |

## 使用场景

- **开放世界海洋**：快速生成带有 LOD 和波浪模拟的大型海洋区域，并自动塑造海岸线地形。
- **河流系统**：沿样条路径创建可流动的河流，自动冲刷河床并生成河岸植被放置提示。
- **湖泊与水池**：放置静态或动态水位湖泊，支持浮力、游泳区域以及水下音效。
- **交互式水体**：利用 Niagara 系统实现角色入水涟漪、船只尾迹、物体漂浮等动态效果。
- **地图编辑器流程**：在编辑器中可视化调整水体形状、波浪强度、透明度等参数，并实时看到地形变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Water)
- [Runtime 模块文档](Water.md)
- [Editor 模块文档](WaterEditor.md)