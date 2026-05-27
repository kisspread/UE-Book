# Datasmith FBX Importer

> Adds support for importing content from DeltaGen and VRED into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | Datasmith FBX 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DatasmithVREDTranslator` (Editor), `DatasmithDeltaGenTranslator` (Editor), `DatasmithFBXTranslator` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 🏛️ 文物（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithFBXImporter) | |

## 用途

为 Unreal Engine 的 Datasmith 导入管线提供对汽车和工业设计行业常用 DCC 软件的 FBX 变体的支持。该插件针对 **DeltaGen** 和 **VRED** 两款专业可视化软件的 FBX 导出格式进行解析，将几何体、材质、场景层级、动画等数据正确翻译为 UE 内容资产。这些软件的 FBX 格式包含非标准的自定义属性和数据结构，普通 FBX 导入器无法正确处理，因此需要专门的翻译模块。

该插件默认不启用，需要手动在项目设置中激活。

## 模块列表

| 模块 | 说明 |
|---|---|
| [DatasmithFBXTranslator](DatasmithFBXTranslator.md) | 基础 FBX 翻译器，提供通用的 FBX 场景解析和数据转换逻辑 |
| [DatasmithDeltaGenTranslator](DatasmithDeltaGenTranslator.md) | DeltaGen 专用翻译器，处理 DeltaGen FBX 格式中的自定义属性和场景结构 |
| [DatasmithVREDTranslator](DatasmithVREDTranslator.md) | VRED 专用翻译器，处理 VRED FBX 变体格式并支持 VRED Python 导出器的最新 API 变更 |

## 使用场景

- 你从 **DeltaGen** 导出了汽车造型评审数据（含材质变体、场景状态等）→ 启用此插件后直接通过 Datasmith 管线导入 UE
- 你从 **VRED** 导出了产品可视化场景（含复杂材质层级和动画）→ 启用此插件后通过 Datasmith 导入 UE
- 你使用 **标准 FBX 格式**但属于上述软件的特定导出设置 → 基础 FBX 翻译器可处理兼容的 FBX 变体

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithFBXImporter)
- [DatasmithFBXTranslator](DatasmithFBXTranslator.md)
- [DatasmithDeltaGenTranslator](DatasmithDeltaGenTranslator.md)
- [DatasmithVREDTranslator](DatasmithVREDTranslator.md)

## 模块依赖

该插件依赖以下外部插件（已在 .uplugin 中声明）：

| 插件 | 用途 |
|---|---|
| `DatasmithImporter` | 提供 Datasmith 导入器核心框架 |
| `DatasmithContent` | 提供 Datasmith 资产类型定义 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode | 修复严格浮点模式下双精度常量截断为 float 的编译警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF | 将 UE_LOG 迁移到新的 UE_LOGF 宏 |
| 2026-02-03 | `88ba268b` | Fix unreachable code errors | 修复不可达代码导致的编译错误 |
| 2025-03-13 | `b059f7b4` | Fix trivial unreachable code warnings | 修复不可达代码的编译警告 |
| 2024-10-02 | `0a14cf0e` | Update VRED python exporter to support API changes in VRED | 更新 VRED Python 导出器以适配 VRED API 变更 |

### 维护评价

- 创建于 2019 年，属于 Enterprise（企业级）类别插件，已有约 7 年历史
- 近两年有持续的编译兼容性维护更新，保持与最新 UE 版本同步
- 2024 年有一次功能性更新（VRED API 适配），说明该插件仍在企业客户驱动下演进
- 所有更新均为维护性质（编译修复、API 迁移），无重大功能扩展
- **推荐使用**：如果你的企业工作流涉及 DeltaGen 或 VRED，这是唯一官方支持的导入路径。普通用户无需启用。