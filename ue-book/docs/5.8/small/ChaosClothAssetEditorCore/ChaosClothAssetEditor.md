# Chaos Cloth Asset Editor Core

> Core required functionalities for editing and creating Dataflow based Cloth Assets.

| 属性 | 值 |
|---|---|
| 中文名 | 布料资产编辑器核心 |
| 分类 | Physics |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ChaosClothAssetEditor` (Runtime), `ChaosClothAssetEditorTools` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2026-01-27 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetEditorCore) | |

## 用途

本插件是 Chaos Cloth Asset 的**编辑器侧核心**，提供基于 Dataflow 的布料资产编辑所需的全部 UI 和交互功能。它从原 `ChaosClothEditor` 插件拆分而来（将 USD 相关代码分离到独立插件），包含以下核心能力：

- **自定义编辑器模式**（`UChaosClothAssetEditorMode`）：管理布料编辑的所有交互状态，包括构建视图模式切换、模拟控制、LOD 管理、Dataflow 图节点联动
- **双视口系统**：2D Rest Space 视口（用于编辑布料网格拓扑/接缝）+ 3D 预览视口（用于实时模拟预览）
- **Dataflow 图编辑器集成**：节点选择自动联动工具启动，支持在图中创建/连接节点
- **交互工具集**：重新网格化（Remesh）、权重图绘制（Weight Map Paint）、属性编辑、蒙皮权重转移（Transfer Skin Weights）、网格选择（Mesh Selection）
- **模拟可视化**：法线、气动力、风速、权重图等调试绘制
- **旧版布料资产转换器**（实验性）：将 `UClothingAssetCommon` 转换为新的 `UChaosClothAsset`

## 使用场景

- 你在 UE5 中使用 Chaos 布料系统，需要一个专用编辑器来可视化编辑布料资产的拓扑、接缝和物理属性 → 本插件提供完整的编辑器环境
- 你需要将旧版 Skeletal Mesh 上的布料资产迁移到新的基于 Dataflow 的 Chaos Cloth Asset → 使用 `FLegacyClothingConverter`
- 你在开发布料相关的 Dataflow 节点，需要查看节点对布料集合的实际影响 → 编辑器的图编辑器 + 双视口提供实时反馈
- 你需要调试布料模拟（法线方向、权重图分布、气动力等） → 3D 视口的 Show 菜单提供丰富的可视化选项

## 蓝图用法

本插件不提供任何 Blueprint API。它是纯编辑器侧模块，所有功能通过编辑器 UI（工具栏、视口、面板）访问。

## C++ 用法

本插件的公开 C++ API 主要面向需要程序化操作布料资产的场景。编辑器模式、视口、工具等内部类均标记为 `MinimalAPI`，不建议直接使用。

### 头文件引入

```cpp
#include "ChaosClothAsset/LegacyClothingConverter.h"
```

### 基本用法 — 旧版布料资产转换

将旧版 `UClothingAssetCommon` 转换为新的 `UChaosClothAsset`。

**来源**: `Public/ChaosClothAsset/LegacyClothingConverter.h`

```cpp
#include "ChaosClothAsset/LegacyClothingConverter.h"
#include "ClothingAsset.h"

// 方式一：创建新资产
void ConvertLegacyClothAsset(const UClothingAssetCommon* LegacyAsset, 
                              const FString& OutputPath)
{
    using namespace UE::Chaos::ClothAsset;
    
    FLegacyClothingConverterResult Result = FLegacyClothingConverter::Convert(
        LegacyAsset,
        OutputPath,           // 输出包路径，如 "/Game/Cloth/"
        TEXT("MyClothAsset")  // 资产名称
    );
    
    if (Result.CreatedAsset)
    {
        // 转换成功，Result.CreatedAsset 是新创建的 UChaosClothAsset
        // Result.CreatedAssetPath 包含完整资产路径
    }
    else
    {
        // 转换失败，Result.ErrorText 包含错误信息
        UE_LOG(LogTemp, Error, TEXT("Conversion failed: %s"), *Result.ErrorText.ToString());
    }
}

// 方式二：转换到已有资产（就地覆盖）
void ConvertIntoExistingAsset(const UClothingAssetCommon* LegacyAsset,
                               UChaosClothAsset* ExistingAsset)
{
    using namespace UE::Chaos::ClothAsset;
    
    FLegacyClothingConverterResult Result = FLegacyClothingConverter::ConvertInto(
        LegacyAsset,
        ExistingAsset  // 会被重置为转换模板后重新烘焙数据
    );
    
    if (!Result.CreatedAsset)
    {
        // 失败处理
    }
}
```

### 进阶用法 — 通过资产编辑器 API 打开布料资产

通过 `UAssetDefinition_ClothAsset` 程序化打开布料编辑器：

```cpp
#include "AssetDefinition_ClothAsset.h"

void OpenClothAssetInEditor(UChaosClothAsset* ClothAsset)
{
    // 打开 Dataflow 编辑器（推荐方式）
    UAssetDefinition_ClothAsset::LaunchClothDataflowAssetEditor(ClothAsset);
}
```

> ⚠️ `LaunchClothPanelAssetEditor` 和 `UseClothPanelEditorByDefault` 在 5.8 中已废弃，请使用 Dataflow Editor。

## 模块依赖

从源码引用关系推断，使用本插件时你的模块需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `ChaosClothAsset` | 布料资产运行时模块（UChaosClothAsset、UChaosClothComponent） |
| `Dataflow` | Dataflow 图执行引擎与编辑器集成（FEngineContext、SDataflowGraphEditor） |
| `BaseCharacterFXEditor` | 角色特效编辑器基类（UEdMode、Toolkit、Viewport 基础设施） |
| `EditorInteractiveToolsFramework` | 编辑器交互工具框架（工具注册、输入行为、Gizmo） |
| `SkeletalMeshDescription` | 骨骼网格描述数据结构 |

> 注意：如果仅使用 `FLegacyClothingConverter` 的转换功能，只需依赖 `ChaosClothAsset` 模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `b9a938ae` | Cleanup Chaos Cloth Asset converter | 清理布料资产转换器代码 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 到 float 截断的编译警告 |
| 2026-05-12 | `a7e94182` | Interchange Cloth Asset: Add support for reimporting; | Interchange 布料资产添加重新导入支持 |
| 2026-05-12 | `f1d5a018` | Daaflow : add HUD selection information to both Cloth and dataflow selection tool viewports | Dataflow 选择工具视口添加 HUD 选择信息显示 |
| 2026-04-27 | `b6b093cd` | CIS - Fixed Issue 1323734: Compile warnings in Module.ChaosClothAssetEditor.cpp, ChaosClothAssetEdit | 修复编译警告问题 |

### 维护评价

- **创建时间**: 2026-01-27，仅约 4 个月前，属于全新插件
- **更新频率**: 非常活跃，最近一个月内有多次实质性更新（功能增强、bug 修复、代码清理）
- **维护状态**: 🟢 **活跃维护中** — 由 Epic Games 团队维护，与 UE5 主线同步更新
- **已知限制**:
  - 版本号仍为 0.1，表明 API 可能不稳定
  - `FLegacyClothingConverter` 标记为实验性（`UE_EXPERIMENTAL`），仅支持 LOD 0 转换
  - 旧版 Cloth Panel Editor 已废弃，正在向 Dataflow Editor 迁移
  - 部分缩略图渲染器类已标记废弃，将在后续版本移至 ChaosClothAsset 模块
- **推荐使用**: ✅ 推荐。作为 Chaos 布料系统的官方编辑器组件，是使用 Chaos Cloth 的必备插件。注意 `FLegacyClothingConverter` 的实验性标记。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetEditorCore)
- 官方文档（无，.uplugin 中 DocsURL 为空）