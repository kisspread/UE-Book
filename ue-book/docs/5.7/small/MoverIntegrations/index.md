# Mover Integrations

> Mover Integrations is a Unreal Engine plugin acting as an umbrella to cover a variety of modules supporting Mover's integration with other plugins, such as animation, AI, and other gameplay systems.

| 属性 | 值 |
|---|---|
| 中文名 | 移动体集成 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（集成模块内容） |
| 模块 | `MoverIntegrations` (Runtime), `MoverMassIntegration` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-07 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MoverIntegrations) | |

## 总体用途

作为 Mover 运动系统的扩展插件，MoverIntegrations 提供了将 Mover 与其他 Engine 模块（如 Mass AI、动画系统、Gameplay 系统）集成的标准化桥梁。它通过独立的子模块（如 `MoverMassIntegration`）封装了针对特定系统的适配逻辑，降低了 Mover 与第三方系统之间的耦合，并简化了多系统协作场景下的配置工作。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| `MoverIntegrations` | Runtime | 基础集成模块，提供通用工具、接口和共享数据类型，为其他子模块提供底层支持。 |
| `MoverMassIntegration` | Runtime | 实现 Mover 与 Mass 实体框架的翻译器，使 Mass 的智能体能够使用 Mover 的运动能力。 |

详细 API 及用法请参阅对应模块文档：
- [MoverIntegrations 模块文档](MoverIntegrations.md)
- [MoverMassIntegration 模块文档](MoverMassIntegration.md)

## 使用场景

- 你正在使用 **Mover 运动系统**构建移动体逻辑，同时希望引入 **Mass AI 框架**管理大量智能体 → 启用 `MoverMassIntegration` 模块，让 Mass 实体直接驱动 Mover 的移动。
- 你需要将 Mover 与 **动画蓝图**、**Gameplay Abilities** 等系统无缝连接 → 通过 `MoverIntegrations` 提供的通用集成工具，减少手动桥接代码。
- 你希望在一个项目中使用多个 Mover 集成方案（如 Mass + AI + 动画），插件提供了模块化组织方式，方便按需启用、测试和扩展。

## 相关链接

- [源码（主目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MoverIntegrations)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MoverIntegrations/Tests)（可能位于 `Tests` 子目录下，若存在则可用）
- 官方文档：暂无（`DocsURL` 为空）