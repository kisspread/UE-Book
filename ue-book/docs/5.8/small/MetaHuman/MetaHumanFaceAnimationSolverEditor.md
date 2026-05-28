# MetaHuman Face Animation Solver Editor

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | 面部动画求解器编辑器 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（编辑器资产定义与自定义界面） |
| 模块 | `MetaHumanFaceAnimationSolverEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕（约 <1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanFaceAnimationSolverEditor) | |

## 用途

本模块是 MetaHuman Animator 插件中“面部动画求解器”（`MetaHumanFaceAnimationSolver`）资产的**编辑器扩展模块**。其核心职责是为 `UMetaHumanFaceAnimationSolver` 类型的资产在 Unreal Editor 中提供完整的编辑体验，包括：
1.  **资产创建**：提供标准的“新建资产”（Factory）流程。
2.  **资产定义**：在内容浏览器中定义该资产的显示名称、图标颜色和所属类别。
3.  **细节面板定制**：自定义选中该资产后，在“细节”面板中显示的属性布局和可编辑内容。

它解决了在编辑器中管理、配置和直观地操作面部动画求解器资产的问题，是 MetaHuman 动画工作流的重要组成部分。

## 使用场景

-   你从 MetaHuman 的面部性能捕捉（Performance）或面部轮廓追踪（Contour Tracking）数据中，需要创建一个**面部动画求解器**资产来驱动 MetaHuman 角色的面部动画。
-   你需要**自定义**面部动画求解器资产的属性，例如调整求解参数、映射权重或查看其内部状态。
-   你正在开发涉及 MetaHuman 面部动画的流程工具，需要以编程方式或通过编辑器 UI 与求解器资产进行交互。

## 蓝图用法

该模块主要为编辑器提供扩展，**没有公开可直接在蓝图运行时调用的节点**。其提供的功能（如资产工厂）主要由编辑器框架在内部调用。

## C++ 用法

### 核心类

该模块提供的 C++ 类主要用于编辑器扩展，而非运行时动画逻辑。

1.  **资产工厂 (`UMetaHumanFaceAnimationSolverFactoryNew`)**
    *   **用途**：当用户在内容浏览器中右键选择“创建基础资产 -> MetaHuman -> 面部动画求解器”时，由编辑器调用以实例化新的资产对象。
    *   **关键重写**：
        *   `FactoryCreateNew`: 实际创建 `UMetaHumanFaceAnimationSolver` 对象。
        *   `GetToolTip`: 返回资产创建菜单中的工具提示文本。

2.  **资产定义 (`UAssetDefinition_MetaHumanFaceAnimationSolver`)**
    *   **用途**：定义 `UMetaHumanFaceAnimationSolver` 资产在编辑器中的表现形式。
    *   **关键重写**：
        *   `GetAssetDisplayName`: 返回“MetaHuman Face Animation Solver”。
        *   `GetAssetColor`: 定义资产图标颜色。
        *   `GetAssetClass`: 返回 `UMetaHumanFaceAnimationSolver` 类的软引用。
        *   `GetAssetCategories`: 将资产归类到“MetaHuman”类别下。

3.  **细节面板自定义 (`FMetaHumanFaceAnimationSolverCustomization`)**
    *   **用途**：当用户在细节面板中选中一个“面部动画求解器”资产时，用于定制其显示的属性和布局。

### 基本用法（C++ 编辑器扩展）

```cpp
// 此代码展示了编辑器模块通常如何注册资产类型和细节面板自定义。
// 这些操作通常在模块的 StartupModule() 中完成。

#include "AssetToolsModule.h"
#include "PropertyEditorModule.h"
#include "MetaHumanFaceAnimationSolverFactoryNew.h" // 包含资产工厂头文件
#include "MetaHumanFaceAnimationSolverCustomizations.h" // 包含自定义类头文件

void FYourEditorModule::StartupModule()
{
    // 注册资产类型
    IAssetTools& AssetTools = FModuleManager::LoadModuleChecked<FAssetToolsModule>("AssetTools").Get();
    AssetTools.RegisterAssetTypeActions(MakeShareable(new FAssetTypeActions_MetaHumanFaceAnimationSolver));

    // 注册细节面板自定义
    FPropertyEditorModule& PropertyModule = FModuleManager::LoadModuleChecked<FPropertyEditorModule>("PropertyEditor");
    PropertyModule.RegisterCustomClassLayout(
        UMetaHumanFaceAnimationSolver::StaticClass()->GetFName(),
        FOnGetDetailCustomizationInstance::CreateStatic(&FMetaHumanFaceAnimationSolverCustomization::MakeInstance)
    );
}
```

## Demo 示例

此模块为编辑器扩展，**不包含**独立的运行时或可编译的最小 C++ 示例。其功能通过编辑器 UI 触发，或由其他更底层的模块（如 `MetaHumanFaceAnimationSolver`）提供运行时逻辑。

## 模块依赖

由于没有提供此模块的 `Build.cs` 文件，无法列出其确切的编译时依赖。但根据其文件结构和功能推断，它很可能依赖于：
*   `MetaHumanFaceAnimationSolver`：提供核心的运行时求解器资产类。
*   `MetaHumanCoreEditor` / `MetaHumanToolkit`：可能提供通用的 MetaHuman 编辑器工具函数或基类。
*   `UnrealEd`, `Slate`, `PropertyEditor`：标准的编辑器和 UI 框架。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时，禁用关卡序列导出功能 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 上的渲染伪影 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 为现有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复定序器缓存问题 |

### 维护评价

**活跃维护**。该模块作为 MetaHuman Animator 这个大型、核心插件的一部分，近期（2026年5月）有非常频繁的提交记录。更新内容集中于功能修复（渲染、缓存）、新功能集成（序列导出）以及与其他子系统（如身体追踪）的协同工作优化。这表明 Epic Games 的开发团队正在持续积极地开发和维护整个 MetaHuman 工具链。**强烈推荐使用**，它是官方 MetaHuman 动画流程的标准组成部分。

## 相关链接

-   [源码 (MetaHumanFaceAnimationSolverEditor 目录)](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanFaceAnimationSolverEditor)
-   [父插件 MetaHumanAnimator 源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
-   (官方文档链接：根据 .uplugin 信息，DocsURL 字段为空，暂无特定模块文档。MetaHuman 的官方文档应参考 Epic Games 的 MetaHuman 门户或文档站。)