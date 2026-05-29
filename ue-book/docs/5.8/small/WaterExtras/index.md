# Water Extras

> Samples, test maps, etc intended to help developers start using the water system. Not intended to be used directly in a shipping product.

| 属性 | 值 |
|---|---|
| 中文名 | 水体示例 |
| 分类 | Water |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（示例地图、测试资产） |
| 模块 | 无（纯内容插件） |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-11-18 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/WaterExtras) | |

## 用途

WaterExtras 是 **Water 插件的配套示例插件**，不包含任何 C++ 代码，纯粹提供示例地图和测试资产，帮助开发者快速上手 Epic 的 Water 水体系统。

它解决的问题是：Water 系统本身功能复杂（水面渲染、河流、湖泊、水位管理等），新开发者难以快速理解如何配置和使用。WaterExtras 提供开箱即用的示例场景，让开发者可以直接打开研究，比纯看文档高效得多。

**注意**：此插件明确标注"不建议直接用于发布产品"，仅作为学习参考用途。

## 使用场景

- 你刚开始接触 Water 系统，想快速了解水面、河流等组件的配置方式 → 启用此插件，打开示例地图研究
- 你在搭建项目原型，需要参考 Water 系统的标准用法 → 参考示例地图中的资产配置
- 你不需要参考示例，只是在开发正式项目 → **不需要启用此插件**

## 蓝图用法

不适用。本插件为纯内容插件，不包含任何 C++ 代码或蓝图函数库。

## C++ 用法

不适用。本插件为纯内容插件，没有头文件或源代码。

## Demo 示例

不适用。本插件本身就是示例合集——启用插件后，在 Content Browser 中浏览 `WaterExtras` 文件夹即可查看示例地图和资产。

## 模块依赖

无特殊依赖。本插件为纯内容插件，无 Build.cs 文件。

插件级别依赖：
| 依赖 | 用途 |
|---|---|
| `Water` | 核心水体系统，本插件提供的是其示例内容 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-10-06 | `26600db1` | Two more .ini files that need to be renamed after the recent change to plugin name requirements | 因插件命名规范变更，重命名了两个 ini 配置文件 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 将插件中的外部链接更新为 HTTPS 安全协议 |
| 2021-11-18 | `0c3be2b6` | Merge Release-Engine-Staging to Test @ CL# 18240298 | 插件首次创建，随引擎版本合并引入 |

### 维护评价

**⚠️ 维护不活跃**

- 自 2021 年创建以来，仅有 3 次提交，其中 2 次是合规性/协议层面的维护性改动
- **从未有过实质性功能更新**（没有新增示例地图或资产）
- 标记为 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`，说明 Epic 对此插件的定位是实验性的参考资源
- 仍然可以正常使用（依赖的 Water 系统在持续维护），但示例内容本身可能未跟上 Water 系统的最新改动

**建议**：可以作为学习 Water 系统的入门参考，但不要将其中的资产配置当作最新最佳实践。实际开发中请参考 Water 插件自身的文档和最新 API。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/WaterExtras)
- [Water 插件文档](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Water)