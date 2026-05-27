# Interchange Framework Assets

> The Interchange Framework Assets plugin exposes the assets used by the Interchange import framework.

| 属性 | 值 |
|---|---|
| 中文名 | Interchange 资产包 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（材质、纹理等导入框架资产） |
| 模块 | `InterchangeAssets` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Assets) | |

## 用途

InterchangeAssets 是 UE5 统一资产导入/导出框架（Interchange Framework）的**配套资产插件**，专门为 Interchange Pipeline 提供运行时所需的默认资源。

Interchange 框架在导入外部格式（如 glTF、FBX、USD 等）到 UE 资产时，需要引用一些内置的材质、纹理或其他资产来完成数据转换和映射。本插件就是这些资产的容器。

**为什么单独成插件？**
- 将资产与代码分离，便于独立更新
- 可以通过 `CanContainContent: true` 的标准方式打包 UAsset
- 依赖 `BaseMaterial` 插件获取基础材质系统支持

## 使用场景

- 你使用 glTF、FBX、USD 等格式导入资产时 → Interchange 管线自动引用本插件的资产
- 你编写自定义 Interchange Pipeline 时 → 可能需要引用本插件提供的默认材质
- 你在开发自定义资产导出器 → 可复用本插件中的默认映射资产

> **注意**：本插件由 Interchange 框架自动使用，通常无需手动引用。如果你禁用此插件，Interchange 导入功能可能无法正常工作。

## 蓝图用法

本插件为纯内容资产插件，不暴露蓝图可调用的函数。

## C++ 用法

本插件仅包含极少量代码（1 个源文件），主要用于注册模块。使用者无需直接引入此模块。

### 模块依赖

如需在其他模块中引用本插件的资产路径，可在 Build.cs 中添加：

```cpp
PublicDependencyModuleNames.Add("InterchangeAssets");
```

## 模块依赖

本插件依赖关系极为简单，无需特殊依赖。

| 模块 | 用途 |
|---|---|
| `BaseMaterial`（插件） | 提供基础材质系统支持 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-03-16 | `1f05dc85` | Adding includes before upcoming header cleanup. | 为即将到来的头文件清理预先添加必要的 include |
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 将 Base<Plugin>.ini 重命名为 Default<Plugin>.ini（标准化配置文件命名） |
| 2025-09-09 | `add9671d` | PR #13720: Fix Interchange PackageRedirects | 修复 Interchange 包重定向问题 |
| 2025-09-01 | `2d41229b` | InterchangeAssets: | InterchangeAssets 模块相关更新 |
| 2025-03-25 | `612836d4` | Interchange Shaders: | Interchange 着色器相关更新 |

### 维护评价

- **活跃程度**：活跃维护中，2025-2026 年持续有更新
- **更新性质**：主要是维护性更新（头文件清理、配置重命名、bug 修复）
- **稳定性**：作为纯内容插件，结构稳定，变动较小
- **推荐度**：✅ 推荐使用。这是 Interchange 框架的核心依赖，启用 Interchange 功能时自动加载，无需额外配置

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Assets)
- [Interchange 框架主插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Framework)