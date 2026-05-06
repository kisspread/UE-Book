# HairStrandsMutable 插件汇总文档

> Adds Mutable functionality to work with Grooms from the HairStrands plugin

| 属性 | 值 |
|---|---|
| 中文名 | Mutable 发型扩展 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `HairStrandsMutable` (Runtime), `HairStrandsMutableEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-01-29 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/HairStrandsMutable) | |

## 总体用途

该插件将 **Mutable**（自定义对象系统）与 **HairStrands**（毛发系统）桥接，允许在运行时动态创建、修改和组合发型（Groom）资产。

解决的核心问题：原生 HairStrands 中的 Groom 资产是静态的，无法根据游戏内参数（如发型选择、颜色变换、物理模拟等）实时变化。通过 Mutable，开发者可以定义参数化的发型模板，在运行时生成变体，实现类似“角色发型编辑器”或“动态毛发切换”的功能。

## 模块文档

| 模块 | 类型 | 一句话说明 |
|---|---|---|
| [`HairStrandsMutable`](HairStrandsMutable.md) | Runtime | 核心运行时逻辑，提供 Groom 组件与 Mutable 模型实例的数据桥接与参数化扩展 |
| [`HairStrandsMutableEditor`](HairStrandsMutableEditor.md) | UncookedOnly | 编辑器支持，为 Mutable 蓝图资产添加 Groom 引用（`FGroomReference`）的编辑与序列化能力 |

## 使用场景

- **多元化角色创建**：玩家在捏脸系统中可选择不同发型，发型本身可进一步调节颜色、长度、刘海形状等参数
- **动态换装系统**：角色装备不同帽子后，发型自动适应（隐藏部分头发）；或根据职业/阵营动态切换发型变体
- **游戏内发型商店**：提供参数化的发型包，玩家购买后可通过滑块调整属性，无需依赖独立模型资源
- **美术工作流优化**：艺术家只需创建单一基础发型，通过 Mutable 数据流在编辑器内快速预览几十种变体，减少手动输出 Assets 的数量

## 相关链接

- [源码目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/HairStrandsMutable)
- [HairStrandsMutable 模块文档](HairStrandsMutable.md)
- [HairStrandsMutableEditor 模块文档](HairStrandsMutableEditor.md)

## 维护状态

近期更新频繁（2025-01 至 2025-09），团队正在积极开发该功能，属于实验性插件，API 可能不稳定。适合在原型或非发布项目中试用，不建议直接用于正式上线产品。