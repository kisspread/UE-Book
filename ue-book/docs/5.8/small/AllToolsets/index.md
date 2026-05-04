# All Toolsets

> Aggregator plugin that depends on all Toolsets plugins.

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | 无（纯内容插件） |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-13 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/AllToolsets) | |

## 用途

`AllToolsets` 是一个**聚合器插件**，其本身不包含任何功能代码。它的唯一作用是**声明对 Epic 官方一系列“工具集”插件的依赖**，并确保它们被一起启用。

这个插件的存在解决了以下问题：
1.  **简化管理**：开发者无需手动逐个查找和启用所有相关的工具集插件，只需启用 `AllToolsets` 即可一键启用所有官方工具集。
2.  **确保一致性**：保证项目中使用了最新、最完整的官方工具集组合，避免遗漏。
3.  **实验性功能集合**：由于它本身是实验性的 (`IsExperimentalVersion: true`)，并且默认禁用 (`EnabledByDefault: false`)，它代表了 Epic 正在开发或测试中的一整套工具集。

## 使用场景

-   你正在开发一个大型项目，希望使用 Epic 提供的所有官方编辑器增强工具和自动化测试工具，但不想逐个查找和配置。
-   你正在评估 Epic 的实验性工具集功能，希望快速启用整个套件进行测试。
-   你希望确保团队所有成员的开发环境都启用了同一套标准工具集。

## 蓝图用法

此插件本身**不提供任何蓝图节点**。它的价值在于启用其依赖的子插件，这些子插件（如 `AIModuleToolset`, `AnimationAssistantToolset` 等）可能会提供各自的蓝图节点。

启用 `AllToolsets` 后，你可以在蓝图编辑器中查找由其依赖插件提供的功能。

## C++ 用法

此插件本身**不提供任何 C++ API**。它是一个纯配置插件。

### 头文件引入

无需引入任何头文件。

### 基本用法

在项目的 `.uproject` 文件或编辑器插件设置中启用 `AllToolsets` 插件即可。启用后，其所有依赖的工具集插件将自动被加载。

### 进阶用法

由于此插件是实验性的，你可能需要在代码中检查其依赖的某个特定工具集插件是否已加载，再使用其功能。但这通常不是 `AllToolsets` 本身的功能，而是其依赖插件的功能。

## Demo 示例

此插件没有可演示的代码。一个最小的“使用”示例就是在 `.uproject` 文件中启用它：

```json
{
    "Plugins": [
        {
            "Name": "AllToolsets",
            "Enabled": true
        }
    ]
}
```

## 模块依赖

此插件本身没有模块，但它声明了对以下插件的依赖（从 `.uplugin` 的 `Plugins` 数组提取）：

| 模块 | 用途 |
|---|---|
| `AIModuleToolset` | AI 模块相关的编辑器工具集 |
| `AnimationAssistantToolset` | 动画辅助工具集 |
| `AutomationTestToolset` | 自动化测试工具集 |
| *(其他未在提供的元数据中列出的工具集插件)* | |

**注意**：这些依赖插件本身可能还有各自的模块依赖。

## 维护状态

### 近期更新

-   2026-04-24 `0cd2b3ea` [Backout] - CL53139837
-   2026-04-24 `8dc8f3fd` Standardize Epic toolset plugin structure
-   2026-04-23 `c868841e` Rename NiagaraAIAssistantTools plugin to NiagaraToolsets

### 维护评价

-   **创建时间**：非常新（2026年4月创建）。
-   **更新频率**：近期（2026年4月）有活跃的提交，包括结构调整和依赖项重命名。
-   **维护状态**：**活跃维护中**。作为 Epic 官方实验性工具集的聚合器，它会随着子工具集插件的更新而更新。
-   **已知限制**：
    1.  **实验性**：插件本身标记为实验性，其包含的工具集功能可能不稳定或在未来版本中发生变化。
    2.  **默认禁用**：需要手动启用。
    3.  **无自身功能**：完全依赖于子插件。
-   **推荐使用**：如果你希望快速试用 Epic 的全套实验性编辑器工具，可以启用。但在生产项目中，建议根据具体需求，有选择地启用其依赖的子插件，而不是整个聚合器，以保持对项目依赖的精确控制。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/AllToolsets)
-   官方文档：无
-   测试用例：无（此插件无代码，因此无测试用例）