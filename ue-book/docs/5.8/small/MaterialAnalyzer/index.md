# Material Analyzer

> Analyzer to discover possible memory savings in material shaders.

| 属性 | 值 |
|---|---|
| 中文名 | 材质分析器 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `MaterialAnalyzer` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2019-01-08 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/MaterialAnalyzer) | |

## 用途

Material Analyzer 是一个编辑器专用工具，旨在通过分析材质实例的参数继承和静态开关排列，发现项目中材质着色器（Material Shaders）潜在的重复和内存浪费，从而指导优化，减少打包后的着色器数量和内存占用。

它通过构建一个材质继承树，分析每个材质实例覆盖的基础属性、静态开关、静态组件蒙版和材质层参数，然后计算这些参数组合的排列，识别出具有相同最终排列（Permutation）的材质，这些材质理论上可以共享同一个着色器，从而节省内存。

## 使用场景

*   **项目中后期优化**：当项目材质实例数量庞大，打包后发现 Shader 内存占用过高时，使用此工具进行分析。
*   **美术资产优化**：技术美术（Tech Art）或程序员需要梳理材质参数设置，找出过度定制化或可合并的材质实例。
*   **着色器复杂度审计**：分析哪些静态参数组合导致了最多的着色器排列，从而简化材质图或参数设置。

## 蓝图用法

此插件主要提供编辑器工具界面，不暴露可直接在蓝图中调用的运行时函数。其功能通过编辑器菜单中的 `MaterialAnalyzer` 窗口访问。

### 核心交互

| 操作 | 说明 |
|---|---|
| **选择资产** | 在 Content Browser 中选择一个或多个材质/材质实例，或使用工具内的资产选择器。 |
| **构建材质树** | 工具会异步构建所选资产及其父材质的继承树。 |
| **分析排列** | 分析材质树中所有实例的参数组合，查找重复排列。 |
| **应用筛选** | 使用参数过滤器（Parameter Filter）缩小显示范围。 |
| **导出 CSV** | 将分析结果导出为 CSV 文件。 |
| **创建本地集合** | 根据分析出的建议，将相关材质资产添加到编辑器的本地集合（Collection）中，便于进一步操作。 |

## C++ 用法

此插件是纯编辑器工具，其核心逻辑（异步分析、数据结构）封装在 `Private` 头文件中，不提供公开的 C++ API。主要的交互方式是通过其 Slate UI (`SMaterialAnalyzer`)。

### 内部数据结构（供理解分析逻辑）

插件使用 `FAnalyzedMaterialNode` 结构体来表示材质继承树中的一个节点。

```cpp
// 源自: Source/Private/AnalyzedMaterialNode.h
struct FAnalyzedMaterialNode
{
    // 节点信息
    FString Path;
    FSoftObjectPath ObjectPath;
    FAssetData AssetData;

    // 存储被覆盖的参数信息
    TArray<FBasePropertyOverrideNodeRef> BasePropertyOverrides; // 基础属性覆盖
    TArray<FStaticSwitchParameterNodeRef> StaticSwitchParameters; // 静态开关参数
    TArray<FStaticComponentMaskParameterNodeRef> StaticComponentMaskParameters; // 静态组件蒙版
    TArray<FStaticMaterialLayerParameterNodeRef> MaterialLayerParameters; // 材质层参数

    // 子节点（继承自此材质的子材质实例）
    TArray<FAnalyzedMaterialNodeRef> ChildNodes;

    // ... 其他方法，如添加子节点、查找参数等
};
```

### 内部异步任务

分析过程是异步的，主要通过以下任务完成：

1.  **`FBuildBasicMaterialTreeAsyncTask`**：根据选择的资产数据，构建基础的材质继承树。
2.  **`FAnalyzeMaterialTreeAsyncTask`**：遍历材质树，为每个节点收集详细的参数覆盖信息。
3.  **`FAnalyzeForIdenticalPermutationsAsyncTask`**：遍历材质树，计算每个节点（叶子节点）的最终参数排列哈希，并找出哈希相同（即排列完全相同）的材质集合，作为优化建议。

## Demo 示例

此插件是编辑器工具，不适合编写独立的运行时示例。使用方法如下：

1.  **启用插件**：确保 `MaterialAnalyzer` 插件已启用（默认已启用）。
2.  **打开窗口**：在编辑器菜单栏选择 `Window > Developer Tools > Material Analyzer`。
3.  **选择资产**：在 Content Browser 中选择你想要分析的材质或材质实例资产。你可以在工具窗口的资产选择器（Asset Picker）中再次选择或确认。
4.  **分析**：工具会自动开始构建材质树和分析过程，进度条会显示在状态栏。
5.  **查看结果**：
    *   **材质树**：左侧树形视图显示材质继承关系，每个节点展开可看到其覆盖的参数（如静态开关、组件蒙版等）。
    *   **优化建议**：右侧 `Suggestions` 区域会列出检测到的“Identical Permutations”（完全相同的参数排列）。展开建议可以看到包含哪些材质。
6.  **交互**：
    *   **定位资源**：在材质树中右键某个节点，可以选择“Find in Content Browser”。
    *   **创建集合**：点击优化建议旁的按钮，可以将建议中的材质资产快速添加到一个新的编辑器本地集合，便于批量操作。
    *   **导出报告**：点击工具栏的“Export CSV”按钮，可将完整的材质分析树导出为CSV文件。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AssetManagerEditor` | 提供访问编辑器内资产注册表（Asset Registry）数据的能力，用于获取材质资产的依赖和数据。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-01-16 | `00864aac` | Don't consider Displacement overrides as triggering static material permutations since they only dri | 位移（Displacement）覆盖不再视为触发射列的静态参数，优化分析逻辑。 |
| 2025-10-30 | `0990a715` | Ran UnrealCodeFixup on Fortnite to change all ~Type() {} to instead be ~Type() = default | 代码规范调整，将析构函数改为使用 `= default`。 |
| 2025-05-08 | `1a49d758` | Moved "Public/MaterialTypes.h" header file to "Public/Materials/MaterialParameters.h". | 头文件位置迁移，属于框架重构的一部分。 |
| 2025-03-06 | `087acbaf` | [Lumen surface cache] Add support for sharing cards between primitive groups (r.LumenScene.SurfaceCa | 与 Lumen 表面缓存相关的改动，可能影响了底层材质数据结构。 |
| 2024-12-09 | `517f6573` | Updated the collections concept to allow for multiple top level folders. This is to enable support f | 更新了编辑器集合（Collection）功能，允许多个顶层文件夹，插件的“创建本地集合”功能可能受益于此。 |

### 维护评价

Material Analyzer 插件自2019年创建，已有7年历史，属于老古董级别。从Git记录看，**最近一年（2025-2026）仍有实质性更新**，包括优化其核心分析逻辑（如00864aac提交），表明它仍在被积极维护和使用。

该插件解决了一个特定的、持续存在的性能优化问题（Shader内存优化），功能明确，UI稳定。它作为编辑器工具，对运行时没有影响，风险较低。**推荐在需要进行材质和着色器优化的项目中使用此工具**。尽管它不是一个新功能，但仍然是Unreal Engine材质优化工具链中有用的一部分。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/MaterialAnalyzer)