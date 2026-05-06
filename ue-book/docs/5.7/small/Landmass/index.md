# Landmass

> （原描述为空，基于源码分析）

| 属性 | 值 |
|---|---|
| 中文名 | 地体画笔 |
| 分类 | Other |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `Landmass` (Runtime), `LandmassEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-02-13 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Landmass) | |

## 用途说明

Landmass 是景观（Landscape）编辑系统的扩展插件，提供一套蓝图可编程的地表画笔（Brush）基座。它允许开发者通过蓝图创建自定义的地形编辑画笔，如侵蚀、平滑、雕刻等工具，而无需编写 C++ 代码。核心组件 `BPBrushBase` 封装了与 Landscape 交互的标准接口，使蓝图画笔能够无缝集成到 Landscape 编辑面板中，支持实时预览与撤销/重做。该插件旨在降低地形工具的开发门槛，加速原型设计与迭代。

## 使用场景

- 你在开发一个大型开放世界项目，需要定制独特的地形雕刻算法 → 使用 Landmass 创建蓝图画笔，快速实现原型并测试。
- 你想要为团队成员提供非编程人员也可调用的地形编辑工具 → 通过蓝图画笔基座封装常见地形操作，暴露参数供设计师调节。
- 你在研究程序化地形生成，需要将外部算法集成到 Unreal 的 Landscape 编辑流程中 → 利用 Landmass 的蓝图接口快速整合。

## 模块列表

| 模块 | 类型 | 一句话描述 | 文档 |
|---|---|---|---|
| `Landmass` | Runtime | 提供地体画笔的核心数据类型、画笔基类及运行时接口。 | [Landmass](Landmass.md) |
| `LandmassEditor` | Editor | 处理画笔在 Landscape 编辑器中的注册、面板集成、交互与可视化。 | [LandmassEditor](LandmassEditor.md) |

## 使用场景

详细使用方式请参考各模块文档。典型工作流：
1. 在内容浏览器中创建一个继承自 `BPBrushBase` 的蓝图类。
2. 在蓝图图表中重写 `OnBrushTick` 或 `ApplyBrush` 等事件，实现自定义地形修改逻辑。
3. 将蓝图画笔放置到关卡中，通过 Landscape 编辑面板选择该画笔进行交互。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Landmass)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Landmass/Tests)（如存在）