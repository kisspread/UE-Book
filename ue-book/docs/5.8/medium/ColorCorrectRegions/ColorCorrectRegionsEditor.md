# Color Correction Regions (CCR)

> Color correction/shading constrained to regions/volumes

| 属性 | 值 |
|---|---|
| 中文名 | 颜色校正区域 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器扩展） |
| 模块 | `ColorCorrectRegions` (Runtime), `ColorCorrectRegionsEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 🏛️ 文物（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ColorCorrectRegions) | |

## 用途

Color Correct Regions 为 Unreal Engine 提供**基于空间区域（Volume）的颜色校正能力**。传统的颜色校正（Color Grading）是对整个画面全局生效的后处理效果，而此插件允许美术人员在场景中放置体积区域（Box、球形、自定义形状等），仅对区域内的像素施加颜色校正。

核心解决问题：
- **局部颜色校正**：在同一个场景中，不同区域需要不同的色调、饱和度、亮度调整（例如：室内暖光 vs 室外冷光区域）
- **虚拟制片场景**：结合 nDisplay 多屏幕输出时，不同屏幕区域可能需要独立的颜色校正
- **实拍与 CG 合成**：在虚拟制片流水线中，确保 CG 元素与实拍素材在特定区域内的色彩一致性

插件放置在 `Experimental` 目录，但 `.uplugin` 中 `IsExperimentalVersion` 和 `IsBetaVersion` 均为 `false`，表示功能已经相对稳定。

## 使用场景

- 你正在搭建虚拟制片场景，需要对 LED 墙幕的不同区域施加不同色彩调整 → 用 ColorCorrectRegions
- 你的关卡中有室内外场景切换，需要对特定区域独立调色 → 用 ColorCorrectRegions
- 你使用 nDisplay 多屏幕输出，需要对各屏幕的输出进行局部颜色校正 → 用 ColorCorrectRegions
- 你使用 Color Grading 插件的全局调色后，还需要对特定区域做局部修正 → 用 ColorCorrectRegions

## 蓝图用法

由于 Runtime 模块的 Public 头文件未在提供的信息中列出，以下内容基于 Editor 模块的类结构和插件架构推断。

### 核心 Actor

此插件的核心功能通过放置在关卡中的 Actor 实现：

| Actor | 说明 |
|---|---|
| `AColorCorrectionRegion` | 主要颜色校正区域 Actor，定义一个空间体积，对体积内的像素施加颜色校正 |
| `AColorCorrectWindow` | 颜色校正窗口 Actor，可能用于屏幕空间或更精细的区域控制 |

### 典型使用流程

1. 在关卡中放置一个 `ColorCorrectionRegion` Actor
2. 调整其体积形状（Box 大小、位置、旋转）覆盖需要校正的区域
3. 在 Details 面板中设置颜色校正参数（亮度、对比度、饱和度、色调等）
4. 根据需要添加多个区域，各区域独立生效

### 与 Color Grading Mixer 集成

插件通过 `FColorGradingHierarchyConfig_ColorCorrectRegion` 将区域 Actor 注册到 Color Grading Mixer 面板中，允许在统一的颜色校正面板中管理所有区域的颜色校正参数。

## C++ 用法

### 头文件引入

```cpp
#include "ColorCorrectRegionsEditorModule.h"
```

### 数据模型生成器

Editor 模块提供了 `IColorGradingEditorDataModelGenerator` 的实现，用于将 Color Correction Region Actor 的属性集成到 Color Grading Editor 的数据模型中。

```cpp
// 引自: ColorGradingDataModelGenerator_ColorCorrectRegion.h
// 获取颜色校正区域的数据模型生成器实例
TSharedRef<IColorGradingEditorDataModelGenerator> Generator =
    FColorGradingDataModelGenerator_ColorCorrectRegion::MakeInstance();

// 初始化数据模型（通常由 Color Grading Editor 框架调用）
Generator->Initialize(ColorGradingDataModel, PropertyRowGenerator);

// 生成数据模型
Generator->GenerateDataModel(PropertyRowGenerator, OutColorGradingDataModel);
```

### 层次结构配置

```cpp
// 引自: ColorGradingHierarchyConfig_ColorCorrectRegion.h
// 获取颜色校正区域的层次结构配置
TSharedRef<IColorGradingMixerObjectHierarchyConfig> HierarchyConfig =
    FColorGradingHierarchyConfig_ColorCorrectRegion::MakeInstance();

// 查找关联的 Actor
TArray<AActor*> AssociatedActors = HierarchyConfig->FindAssociatedActors(ParentObject);

// 验证拖放操作
FSceneOutlinerDragValidationInfo ValidationInfo =
    HierarchyConfig->ValidateDrop(DropTarget, Payload);
```

### 详情面板自定义

```cpp
// 引自: ColorCorrectRegionCustomization.h
// 注册自定义 Details 面板（通常在模块 StartupModule 中完成）
FPropertyEditorModule& PropertyModule = 
    FModuleManager::GetModuleChecked<FPropertyEditorModule>("PropertyEditor");

PropertyModule.RegisterCustomClassLayout(
    AColorCorrectWindow::StaticClass()->GetFName(),
    FOnGetDetailCustomizationInstance::CreateStatic(
        &FColorCorrectWindowDetails::MakeInstance)
);
```

### 上下文菜单扩展

```cpp
// 引自: ColorCorrectionActorContextMenu.h
// 创建并注册右键上下文菜单扩展
TSharedPtr<FColorCorrectionActorContextMenu> ContextMenu = 
    MakeShareable(new FColorCorrectionActorContextMenu());
ContextMenu->RegisterContextMenuExtender();

// 卸载时释放
ContextMenu->UnregisterContextMenuExtender();
```

## 模块依赖

### 本插件依赖的插件

| 插件 | 用途 | 是否必需 |
|---|---|---|
| `ColorGrading` | 提供颜色校正基础设施和 Color Grading Mixer 面板 | ✅ 是 |
| `nDisplayModularFeatures` | 提供 nDisplay 多屏幕输出支持 | ✅ 是 |
| `ObjectMixer` | 提供对象混音器集成 | ✅ 是 |
| `ConcertSyncClient` | 多用户编辑支持 | ❌ 可选 |

### 模块依赖

| 模块 | 用途 |
|---|---|
| `ColorGrading` | 颜色校正数据模型和编辑器集成 |

无特殊依赖（仅标准 Core/Engine/Slate 等），大部分功能通过插件依赖（Plugin Dependencies）实现。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-05-12 | `5c7314c3` | Fix Color Correct Regions render rect being truncated when dynamic resolution scales below 1.0. | 修复动态分辨率低于 1.0 时渲染区域矩形被截断的问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移为 UE_LOGF |
| 2026-04-06 | `a7ea00e7` | ColorCorrectActors: Promote CustomDepth/SceneDepth from half to float to preserve precision | 将自定义深度/场景深度从半精度提升为全精度以保留精度 |
| 2026-04-01 | `12ae598f` | Color Correction Actors Multi-User: fixed an issue where stencil id's assignment on some actors were | 修复多用户编辑中部分 Actor 模板 ID 分配的问题 |

### 维护评价

- **创建时间**：2020 年 9 月，至今约 6 年
- **维护状态**：**活跃维护中**。2026 年有多次实质性更新，包括精度修复、动态分辨率兼容修复、多用户编辑修复等
- **稳定性**：虽然仍位于 `Experimental` 目录，但 `.uplugin` 中 `IsExperimentalVersion` 和 `IsBetaVersion` 均为 `false`，功能已趋于稳定
- **已知关注点**：
  - 深度/精度相关问题曾需要修复（half → float 提升），说明在高精度场景下可能仍有数值敏感性
  - 动态分辨率场景曾存在渲染矩形截断问题，已修复
  - 位于 Experimental 目录但标记为非实验性，存在一定的命名不一致
- **推荐使用**：✅ 推荐。功能明确、维护活跃、bug 修复及时。适合需要局部颜色校正的虚拟制片和关卡设计项目。建议关注后续是否从 Experimental 目录迁移。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ColorCorrectRegions)
- [官方文档]()（暂无）