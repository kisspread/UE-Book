# Interchange Framework Assets

> The Interchange Framework Assets plugin exposes the assets used by the Interchange import framework.

| 属性 | 值 |
|---|---|
| 中文名 | 互换资产 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（Interchange框架使用的资产） |
| 模块 | `InterchangeAssets` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-03-25 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Assets) | |

## 用途

此插件是 Unreal Engine 5 “互换（Interchange）” 框架的配套资产包。其核心功能是为 Interchange 导入系统提供必要的内置资源，例如用于测试和验证不同文件格式（如 FBX、glTF、OBJ 等）导入流程的参考模型、材质和纹理。它解决了 Interchange 框架在默认状态下缺乏标准化测试和参考资产的问题，为框架的开发者和高级用户提供了基准。

## 使用场景

- 你正在开发或调试一个自定义的 Interchange 资产导入器 → 可以使用此插件中的资产作为标准的测试输入，验证你的导入器处理各种几何体、材质和 UV 是否正确。
- 你正在为 UE 创建新的资产导入格式支持插件 → 可以参考此插件中的资产结构和导入设置，作为构建新导入器的模板和测试基准。
- 你在学习 Interchange 框架的工作原理 → 可以检查此插件中的资产，观察它们在导入过程中如何被框架解析和处理。

## 蓝图用法

此插件主要作为资产内容提供者，未暴露直接的蓝图可调用函数或可读写属性。它主要通过被 `InterchangeImport` 或相关模块在内部引用的方式来发挥作用，无直接蓝图 API。

## C++ 用法

此插件主要作为资产内容提供者，未暴露面向用户或开发者的 C++ API 类。其模块 `InterchangeAssets` (Runtime) 主要负责资产的加载和注册，而非提供可直接在用户代码中调用的函数。

## Demo 示例

作为纯内容资产插件，其“示例”就是它自身包含的资产。在引擎中启用该插件后，你可以在 `Content/Interchange` 或类似的目录下找到测试用的网格体、材质等资产。你无需编写任何代码即可在编辑器中查看和使用这些资产。

## 模块依赖

从 `InterchangeAssets.Build.cs` 分析，该模块的依赖较为简洁。

| 模块 | 用途 |
|---|---|
| `InterchangeNodes` | 提供 Interchange 框架核心的节点数据结构，用于资产的结构化表示。 |

**注意**：该插件本身依赖 `BaseMaterial` 插件（已在 .uplugin 中声明），以确保基础材质资产可用。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-03-16 | `1f05dc85` | Adding includes before upcoming header cleanup. | 为即将到来的头文件清理工作预先添加必要的包含。 |
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 将插件配置文件从`Base`前缀重命名为`Default`前缀，跟随引擎规范更新。 |
| 2025-09-09 | `add9671d` | PR #13720: Fix Interchange PackageRedirects | 修复 Interchange 相关的包重定向问题，确保资产引用正确。 |
| 2025-09-01 | `2d41229b` | InterchangeAssets: | 对 `InterchangeAssets` 模块进行了代码修改（具体信息不足）。 |
| 2025-03-25 | `612836d4` | Interchange Shaders: | 与 Interchange 着色器相关的改动（可能影响资产材质）。 |

### 维护评价

`InterchangeAssets` 是一个相对较新的资产插件，其功能明确且独立。近期的 Git 提交记录显示，它主要在进行兼容性修复、规范适配以及作为 Interchange 整体框架一部分的同步更新，而非频繁的功能性变更。这符合其作为“资源库”的定位，其稳定性依赖于上层的 `Interchange` 模块。该插件仍在维护中，但更新节奏较慢。鉴于其核心作用是为框架提供基准资产，且由 Epic 官方维护，**推荐在使用或开发 Interchange 相关功能时启用和使用它**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Assets)
- [官方文档](https://docs.unrealengine.com/) (请查阅 Unreal Engine 官方文档中关于 Interchange 框架的章节)