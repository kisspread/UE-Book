# Interchange Framework Assets

> The Interchange Framework Assets plugin exposes the assets used by the Interchange import framework.

| 属性 | 值 |
|---|---|
| 中文名 | 资产交换框架资源 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（材质模板等资产） |
| 模块 | `InterchangeAssets` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-03-25 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Assets) | |

## 用途

该插件为 **Interchange 资产导入框架**提供配套的**默认资产集合**。Interchange 本身是一个统一的资产导入导出框架，而此插件提供了该框架在运行时（如加载导入的资产时）需要使用的**基础材质、纹理和其他默认资源**。

简单来说：Interchange 插件负责导入逻辑，而 **InterchangeAssets 插件负责提供“默认值”**。例如，当导入一个不包含材质的 3D 模型时，Interchange 框架会使用此插件提供的默认材质进行渲染。

## 使用场景

- **使用 Interchange 框架导入资产**：当你在项目中启用了 `Interchange` 插件并使用其 API 导入 FBX、GLTF 等格式的 3D 模型或场景时，`InterchangeAssets` 插件自动提供所需的后备材质、纹理等资源，确保导入的模型在场景中能正确显示。
- **默认资产的自动替换**：在自动化资产处理管线中，当 Interchange 框架无法匹配到项目中的特定资产时，可能会回退到此插件提供的默认资产。

## 蓝图用法

此插件为**纯内容插件**，不暴露任何蓝图节点或函数。其资产（如 `M_DefaultGrid` 材质）通常由其他插件（如 `Interchange`）在内部引用。用户无需在蓝图中直接操作这些资产。

## C++ 用法

此插件为**纯内容插件**，不包含 C++ 源码。其资产（材质、纹理等）位于 `Content/` 目录下。要使用其提供的资产，你需要通过 `Interchange` 框架的 API，或使用 `FSoftObjectPath` 进行引用。

### 基本用法
```cpp
// 引用插件中的默认材质（路径来自插件的 Content 目录）
const FSoftObjectPath DefaultMaterialPath(TEXT("/InterchangeAssets/DefaultAssets/M_DefaultGrid.M_DefaultGrid"));

// 加载材质资产
UMaterial* DefaultMaterial = Cast<UMaterial>(DefaultMaterialPath.TryLoad());
```

## Demo 示例

此插件不包含可独立运行的示例。其资产通常作为 `Interchange` 插件导入流程的一部分被使用。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `BaseMaterial` | 提供基础的材质模板（已通过 .uplugin Plugins 字段声明依赖） |

**无其他特殊依赖**。此插件主要依赖于 Unreal Engine 的标准内容加载机制。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-03-16 | `1f05dc85` | Adding includes before upcoming header cleanup. | 在头文件清理前添加必要的包含语句，以保持编译兼容性 |
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 将配置文件从 Base<Plugin>.ini 重命名为 Default<Plugin>.ini，遵循UE5新规范 |
| 2025-09-09 | `add9671d` | PR #13720: Fix Interchange PackageRedirects | 修复 Interchange 包重定向问题，确保资产路径解析正确 |
| 2025-09-01 | `2d41229b` | InterchangeAssets: | 对 InterchangeAssets 插件的例行更新 |
| 2025-03-25 | `612836d4` | Interchange Shaders: | 更新了 Interchange 相关的着色器资产 |

### 维护评价

- **创建时间**：约 1 年前，属于较新的插件。
- **维护频率**：过去一年内有多次更新，主要围绕配置文件规范、路径修复和头文件兼容性等维护工作。
- **维护状态**：**维护中**。作为 `Interchange` 框架的核心配套资产，随着 Interchange 框架的更新，此插件也会持续维护。
- **推荐使用**：**是**。如果你在项目中使用了 `Interchange` 插件进行资产导入，那么此插件是**必须启用**的，它为框架提供了必要的默认资源。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Assets)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/) (无特定文档，参考 Interchange 框架文档)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange) (测试用例位于 Interchange 主插件目录下)