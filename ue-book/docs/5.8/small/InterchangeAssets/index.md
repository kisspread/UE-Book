# Interchange Framework Assets

> The Interchange Framework Assets plugin exposes the assets used by the Interchange import framework.

| 属性 | 值 |
|---|---|
| 中文名 | 交换框架资产 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（材质、纹理等导入框架资源） |
| 模块 | `InterchangeAssets` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2023-03-01 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Assets) | |

## 用途

此插件是 UE5 **Interchange 导入框架**的内容资源提供者。它本身不包含导入逻辑代码，而是提供了 Interchange 导入器在处理外部文件（如 FBX、glTF、OBJ 等）时所需的基础材质、纹理等资产资源。

**为什么需要这个插件？** 当 Interchange 框架导入外部 3D 资源时，如果源文件中包含材质定义但没有对应的 Unreal 材质资产，导入器需要参考默认的材质模板来创建或映射材质。此插件正是为 Interchange 导入管线提供这些基础资源。

## 使用场景

- 你使用 **Interchange 导入管线** 导入 FBX/glTF/OBJ 文件 → 需要此插件提供的基础材质资产
- 你的项目启用了 Interchange（UE5 默认的现代导入框架）→ 此插件作为依赖自动启用
- 你自定义了 Interchange 导入器并需要参考默认材质资产 → 引用此插件中的资源

## 蓝图用法

此插件为纯内容插件（CanContainContent=true），仅包含资产文件，不暴露任何蓝图节点或 C++ API。

## C++ 用法

此插件无 C++ 源码头文件可供引用。如需在代码中访问此插件提供的资产，通过资产路径（Asset Path）引用即可。

### 资产引用示例

```cpp
// 通过路径引用 Interchange 提供的基础材质资产
// 路径格式: /InterchangeAssets/Materials/...
static ConstructorHelpers::FObjectFinder<UMaterialInterface> DefaultMaterialFinder(
    TEXT("/InterchangeAssets/Materials/MI_DefaultMaterial")
);
if (DefaultMaterialFinder.Succeeded())
{
    UMaterialInterface* DefaultMaterial = DefaultMaterialFinder.Object;
}
```

## Demo 示例

此插件为纯内容插件，无自定义代码。最简使用方式是直接启用插件：

1. 在 `.uproject` 中确保 `Interchange` 和 `InterchangeAssets` 插件已启用
2. 通过 FBX Import（使用 Interchange 管线）导入带材质的模型
3. 导入器将自动使用此插件提供的材质资产作为参考

## 模块依赖

无特殊依赖（仅标准 Core/Engine 等运行时模块）。

**插件依赖**：
| 插件 | 用途 |
|---|---|
| `BaseMaterial` | 提供基础材质模板，供此插件的资产引用 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-03-16 | `1f05dc85` | Adding includes before upcoming header cleanup. | 为即将进行的头文件清理预先添加必要的 include |
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 将配置文件从 Base*.ini 重命名为 Default*.ini |
| 2025-09-09 | `add9671d` | PR #13720: Fix Interchange PackageRedirects | 修复 Interchange 包重定向问题 |
| 2025-09-01 | `2d41229b` | InterchangeAssets: | InterchangeAssets 相关改动（提交信息不完整） |
| 2025-03-25 | `612836d4` | Interchange Shaders: | Interchange 着色器相关改动 |

### 维护评价

- **活跃维护**：最近 1 年内有多次更新，说明仍在持续维护中
- **更新内容**：主要为配置修正、头文件清理和 bug 修复，属于常规维护性质
- **插件角色**：作为 Interchange 框架的内容依赖组件，随 Interchange 主框架一起维护
- **推荐使用**：✅ 推荐。如果你的项目使用 Interchange 导入管线，此插件是必要的基础依赖，且默认启用无需额外配置

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Assets)
- [Interchange 主框架](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Interchange)
- [官方文档 - Interchange](https://dev.epicgames.com/documentation/en-us/unreal-engine/interchange-overview)