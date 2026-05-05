# Material Analyzer

> Analyzer to discover possible memory savings in material shaders.

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | 否 |
| 模块 | MaterialAnalyzer (Editor) |
| 创建时间 | 2019-01-08 |
| 年龄标签 | 👴 老古董 (>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/MaterialAnalyzer) | |

## 用途

Material Analyzer 是一个**编辑器内材质优化审计工具**。它解决的核心问题是：**项目中有大量材质实例（Material Instance），其中很多可能通过不同的 Static Switch / Static Component Mask / Base Property Override 产生了完全相同的 shader 排列（permutation），却各自占用了独立的 shader 编译产物，白白浪费内存和磁盘空间**。

这个工具会：
1. 从 Asset Registry 扫描项目中所有的 `UMaterial` 和 `UMaterialInstance`，构建材质继承树
2. 逐个加载材质，分析其参数覆盖情况（Static Switch、Static Component Mask、Base Property Override、Material Layer Parameter）
3. 对分析结果进行排列哈希比对，找出**生成了完全相同 shader 的材质实例群组**
4. 在底部 Suggestions 面板给出优化建议：建议将这些材质重新组织继承关系，使它们只通过动态参数（Dynamic Parameter）来区分

这是一个纯 Editor 工具，不包含运行时代码，不会影响打包产物。

## 使用场景

- 你的项目有几百甚至上千个材质实例，怀疑 shader 内存占用过高 → 用 Material Analyzer 扫描找出重复排列
- 你想了解某个材质在继承链中哪些属性被覆盖了 → 选中该材质查看参数详情
- 你需要将分析结果导出为 CSV 交给团队讨论优化方案 → 使用 Export to CSV 功能
- 你想对分析出的问题材质创建集合（Collection）方便后续批量操作 → 使用 Create Local Collection 功能

## 蓝图用法

此插件**不暴露任何蓝图接口**。它是一个纯编辑器 UI 工具，没有 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性。

## 使用方式（编辑器 UI）

### 打开工具

通过菜单栏：**Window → Developer Tools → Material Analyzer**

（位于 Developer Tools 审计类别下，使用材质编辑器图标）

### 界面布局

工具界面分为四个区域：

1. **顶部工具栏**
   - **Material To Analyze** — 材质选择器，选择要分析的材质
   - **Parameters to Filter** — 搜索框，按参数名过滤显示（按 Enter 确认）
   - **Export to CSV** — 将当前分析结果导出为 CSV 文件

2. **材质继承树（上半部分）** — 以树形结构展示选中材质的完整继承链，每行包含：
   - **Material Name** — 材质名称（可点击 Content Browser 图标定位资产）
   - **Number of Children (Direct/Total)** — 直接子材质数 / 总后代数
   - **Base Property Overrides** — 覆盖的基础属性（可展开）
   - **Material Layer Parameters** — 材质层参数
   - **Static Switch Parameters** — 静态开关参数（可展开）
   - **Static Component Mask Parameters** — 静态分量遮罩参数（可展开，显示 R/G/B/A 各通道）

3. **建议面板（下半部分）** — 分析完成后显示优化建议：
   - 按潜在优化收益排序（从大到小）
   - 展开建议可看到涉及的具体材质列表
   - 提供 **Create Local Collection** 按钮，一键将问题材质加入集合

4. **状态栏（底部）** — 显示当前分析进度和加载状态

### 分析流程

1. 打开 Material Analyzer 后，工具会自动从 Asset Registry 获取所有 `UMaterial` 和 `UMaterialInstance`，异步构建材质继承树
2. 在材质选择器中选择一个材质，工具会找到该材质的根节点并显示完整继承树
3. 工具异步逐个加载并分析继承链中每个材质的参数覆盖
4. 分析完成后，工具自动运行排列比对，检查是否有不同材质实例产生了相同的 shader 排列
5. 匹配结果以建议形式显示在 Suggestions 面板中

### CSV 导出

点击 **Export to CSV** 按钮后，弹出文件保存对话框，导出内容包含：
- MATERIAL — 材质名称
- BASE PROPERTY OVERRIDES — 覆盖的基础属性及值
- LAYER PARAMETERS — 材质层参数
- STATIC SWITCHES — 静态开关参数及值（True/False）
- STATIC COMPONENT MASKS — 静态分量遮罩（R/G/B/A）

默认保存路径：`{Project}/Saved/Logs/MaterialProperties.csv`

## C++ 用法

此插件完全是编辑器 UI，不提供可复用的 C++ API。如果你想在自己的工具中实现类似功能，可以参考其源码中以下核心模式：

### 核心类结构

| 类 | 文件 | 职责 |
|---|---|---|
| `FMaterialAnalyzerModule` | `MaterialAnalyzerModule.cpp` | 模块注册，注册 Nomad Tab Spawner |
| `SMaterialAnalyzer` | `SMaterialAnalyzer.h/cpp` | 主 Slate 控件，管理分析流程和 UI |
| `FAnalyzedMaterialNode` | `AnalyzedMaterialNode.h` | 材质节点数据结构，存储参数分析结果 |
| `SAnalyzedMaterialNodeWidgetItem` | `SAnalyzedMaterialNodeWidgetItem.h/cpp` | 树视图行控件 |
| `FBuildBasicMaterialTreeAsyncTask` | `SMaterialAnalyzer.h` | 异步任务：构建材质继承树 |
| `FAnalyzeMaterialTreeAsyncTask` | `SMaterialAnalyzer.h` | 异步任务：逐材质分析参数 |
| `FAnalyzeForIdenticalPermutationsAsyncTask` | `SMaterialAnalyzer.h` | 异步任务：查找相同排列 |

### 关键实现模式

**材质继承树构建**（来自 `SMaterialAnalyzer.cpp`）：

```cpp
// 从 Asset Registry 获取所有材质
FAssetRegistryModule& AssetRegistryModule = FModuleManager::LoadModuleChecked<FAssetRegistryModule>(AssetRegistryName);
IAssetRegistry& AssetRegistry = AssetRegistryModule.Get();
AssetRegistry.GetAssetsByClass(UMaterial::StaticClass()->GetClassPathName(), AssetDataArray, true);
AssetRegistry.GetAssetsByClass(UMaterialInstance::StaticClass()->GetClassPathName(), AssetDataArray, true);

// 通过 Parent 标签解析继承关系
FString ParentPathString = InAssetData->GetTagValueRef<FString>(NAME_Parent);
```

**异步分析流程**：工具使用三个 `FAsyncTask` 串行执行，避免阻塞编辑器 UI：
1. `FBuildBasicMaterialTreeAsyncTask` — 构建继承树（仅使用 AssetRegistry 数据，不加载资产）
2. `FAnalyzeMaterialTreeAsyncTask` — 逐材质加载并分析参数
3. `FAnalyzeForIdenticalPermutationsAsyncTask` — 哈希比对，找出相同排列

## Demo 示例

此插件是纯编辑器工具，无法通过代码创建 Demo。使用方法：

1. 在 UE5 编辑器中启用 Material Analyzer 插件（默认已启用）
2. 打开 **Window → Developer Tools → Material Analyzer**
3. 在材质选择器中选择任意材质或材质实例
4. 等待分析完成，查看材质继承树和优化建议

## 模块依赖

要在你的编辑器模块中引用 Material Analyzer 的源码模式，需要以下模块：

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、异步任务框架 |
| `CoreUObject` | UObject 资产系统 |
| `Engine` | 材质类型（UMaterial, UMaterialInstance） |
| `Slate` / `SlateCore` | UI 框架 |
| `UnrealEd` | 编辑器功能（Content Browser 同步） |
| `PropertyEditor` | 属性编辑器集成 |
| `AssetRegistry` | 资产注册表查询 |
| `AssetManagerEditor` | 集合（Collection）创建功能 |
| `DesktopPlatform` | 文件保存对话框 |
| `ToolWidgets` | 工具栏控件 |

## 维护状态

### 近期更新

| 日期 | Hash | 提交信息 | 解读 |
|---|---|---|---|
| 2025-05-08 | `1a49d758cda4` | Moved "Public/MaterialTypes.h" header file to "Public/Materials/MaterialParameters.h" | 引擎范围的头文件重组，非插件功能性更新 |
| 2025-03-06 | `087acbaf7f00` | [Lumen surface cache] Add support for sharing cards between primitive groups... | 引擎材质系统新增 Lumen Card Sharing 功能，插件仅被动适配 |
| 2024-12-09 | `517f6573f680` | Updated the collections concept to allow for multiple top level folders... | 集合系统重构，插件依赖的 Collection API 跟随更新 |

### 维护评价

- **创建时间**：2019 年 1 月，已超过 7 年
- **最近更新**：2025 年 5 月，但均为引擎级头文件/系统重构的被动适配，非插件自身功能更新
- **活跃度**：功能层面不活跃，最后一次实质性功能更新在很久以前
- **稳定性**：代码稳定，作为审计工具功能完备
- **已知限制**：
  - 分析大型项目时，材质加载可能耗时较长（虽为异步，但仍需逐个加载）
  - `FAnalyzeMaterialTreeAsyncTask` 标记为不可中止（`CanAbandon() = false`），无法在分析中途取消
  - 仅分析 Static Switch / Static Component Mask / Base Property Override，不覆盖所有可能影响 shader 排列的参数
- **推荐使用**：✅ 推荐。作为 Epic 官方材质优化工具，功能稳定，适合在项目优化阶段使用。如果项目材质数量较多且关注 shader 内存，值得定期运行。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/MaterialAnalyzer)
- 官方文档：无（.uplugin 中 DocsURL 为空）
