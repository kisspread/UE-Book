# Motion Design Data Link Integration

> 

| 属性 | 值 |
|---|---|
| 中文名 | 运动设计数据连接 |
| 分类 | Motion Design |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `AvalancheDataLink` (Runtime), `AvalancheDataLinkEditor` (Editor) |
| 实验性 | ⚦ 是 |
| 创建时间 | 2025-08-27 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/AvalancheDataLink) | |

## 用途

该插件是 **Motion Design（运动设计）** 和 **DataLink（数据链接）** 两个虚拟制作子系统之间的桥梁。它解决了在 Motion Design 环境中实时消费和驱动 DataLink 提供的数据流的问题。插件本身不定义新的数据源或动画系统，而是作为集成层，使得 Motion Design 的动画元素能够响应来自 DataLink 的实时数据更新。

## 使用场景

- 你需要将 Motion Design 中创建的动态图形或 UI 元素（如参数化的形状、文本）绑定到 DataLink 提供的实时数据源（如股票行情、传感器读数、数据库查询结果）上，实现数据驱动的动画。
- 在虚拟制片管线中，希望利用 DataLink 统一管理的数据来精确控制 Motion Design 模块生成的虚拟场景内容（例如 LED 墙内容、XR 环境）。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `AvalancheDataLink` | Runtime | 核心运行时模块，提供将 Motion Design 动画属性与 DataLink 数据源进行映射和同步的框架与基础类型。 |
| `AvalancheDataLinkEditor` | Editor | 编辑器工具模块，提供在 Motion Design 编辑器内方便地创建、查看和管理上述数据映射关系的用户界面和资产类型。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF，属于编译器或代码规范的维护性更新。 |
| 2025-08-27 | `f25e96ca` | Motion Design: set the scene state and data link plugins to beta | 将场景状态和数据链接插件标记为测试版，明确其不稳定状态。 |
| 2025-08-27 | `94f96138` | Motion Design: Moved scene state and data link plugins out of experimental into virtualproduction | 首次提交，将插件从实验性目录迁移至正式的虚拟制作插件目录。 |

### 维护评价

该插件于 **2025年8月底** 从实验状态迁出并正式发布（标记为 **Beta**）。自创建以来，仅有少量编译适配和状态设置类的更新，**没有新增实质性功能**。由于是 Beta 状态且创建时间极短，其 API 和功能范围尚未稳定。目前来看，它仍处于早期验证阶段，**不建议在生产项目中依赖使用**。需密切关注后续版本的更新公告，以了解其功能完善和正式发布的计划。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/AvalancheDataLink)