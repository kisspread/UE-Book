# Chaos Cloth Asset Editor Core

> Core required functionalities for editing and creating Dataflow based Cloth Assets.

| 属性 | 值 |
|---|---|
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器工具、UI 组件、缩略图渲染器） |
| 模块 | `ChaosClothAssetEditor` (Runtime), `ChaosClothAssetEditorTools` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2026-04-07 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetEditorCore) | |

## 用途

ChaosClothAssetEditorCore 是 Chaos 布料系统的核心编辑器插件，提供基于 Dataflow（数据流图）的布料资产编辑环境。它解决的核心问题是：**如何让美术和技术美术以可视化、交互式的方式创建和编辑布料模拟资产**。

该插件构建了一个完整的布料资产编辑器，包含：

- **双视口架构**：一个 2D/3D 构造视口（Rest Space Viewport）用于编辑布料图案和缝合线，一个 3D 预览视口用于实时模拟预览
- **Dataflow 图编辑器集成**：布料资产的构建逻辑通过 Dataflow 节点图定义，支持可视化编程
- **交互式工具框架**：集成 UE 的 Interactive Tools Framework，提供重网格化、权重绘制、属性编辑、蒙皮权重传输、网格选择等工具
- **模拟可视化**：丰富的调试可视化选项，包括法线、空气动力学、风速、权重贴图、变形目标等
- **动画预览**：支持骨骼网格体动画驱动布料模拟的实时预览

该插件基于 `BaseCharacterFXEditor` 框架构建，与 UE 的角色特效编辑器架构保持一致。

## 使用场景

- 你在制作角色服装、旗帜、窗帘等布料模拟效果 → 使用此编辑器创建和调整布料资产
- 你需要通过可视化节点图定义布料的构建逻辑（裁片形状、缝合关系、物理属性） → 使用 Dataflow 图编辑器
- 你需要实时预览布料在动画驱动下的模拟效果 → 使用 3D 预览视口
- 你需要绘制布料的权重贴图来控制物理属性的空间分布 → 使用 Weight Map Paint 工具
- 你需要将蒙皮权重从一个网格传输到布料网格 → 使用 Transfer Skin Weights 工具

## 蓝图用法

该插件主要面向编辑器扩展，蓝图可直接使用的 API 较少。核心功能通过编辑器 UI 和 C++ API 暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `LaunchClothPanelAssetEditor` | 在 Cloth Panel 编辑器中打开布料资产 | `UAssetDefinition_ClothAsset` |
| `LaunchClothDataflowAssetEditor` | 在 Dataflow 编辑器中打开布料资产 | `UAssetDefinition_ClothAsset` |
| `UseClothPanelEditorByDefault` | 查询是否默认使用 Cloth Panel 编辑器 | `UAssetDefinition_ClothAsset` |

### 编辑器设置（项目设置）

通过 **Edit → Project Settings → Plugins → Chaos Cloth Editor** 可配置：

| 设置 | 说明 |
|---|---|
| `bClothAssetsOpenInDataflowEditor` | 布料资产是否默认在 Dataflow 编辑器中打开（而非 Cloth Panel 编辑器） |
| `ConstructionViewportMousePanButton` | 2D 视图模式下控制相机平移的鼠标按钮（右键/中键/两者皆可） |

## C++ 用法

### 头文件引入

```cpp
#include "ChaosClothAssetEditor/ChaosClothAssetEditorModule.h"
#include "ChaosClothAssetEditor/ClothEditor.h"
#include "ChaosClothAssetEditor/ClothEditorToolkit.h"
#include "ChaosClothAssetEditor/ClothEditorMode.h"
#include "ChaosClothAssetEditor/ClothEditorPreviewScene.h"
```

### 基本用法：打开布料资产编辑器

```cpp
// 通过 AssetDefinition 打开布料资产编辑器
// 来源: Private/ChaosClothAsset/AssetDefinition_ClothAsset.h

UChaosClothAsset* ClothAsset = /* 获取布料资产 */;

// 在 Cloth Panel 编辑器中打开
UAssetDefinition_ClothAsset::LaunchClothPanelAssetEditor(ClothAsset);

// 在 Dataflow 编辑器中打开
UAssetDefinition_ClothAsset::LaunchClothDataflowAssetEditor(ClothAsset);
```

### 进阶用法：模拟控制

```cpp
// 通过 3D 视口客户端控制布料模拟
// 来源: Private/ChaosClothAsset/ClothEditor3DViewportClient.h

// 获取 3D 视口客户端（通常从编辑器 Toolkit 获取）
TSharedPtr<FChaosClothAssetEditor3DViewportClient> ViewportClient = /* ... */;

// 软重置模拟（保留当前状态，重新开始）
ViewportClient->SoftResetSimulation();

// 硬重置模拟（完全重置到初始状态）
ViewportClient->HardResetSimulation();

// 暂停/恢复模拟
ViewportClient->SuspendSimulation();
bool bSuspended = ViewportClient->IsSimulationSuspended();
ViewportClient->ResumeSimulation();

// 启用/禁用模拟
ViewportClient->SetEnableSimulation(true);
bool bEnabled = ViewportClient->IsSimulationEnabled();

// 切换线框显示
ViewportClient->EnableSimMeshWireframe(true);
ViewportClient->EnableRenderMeshWireframe(true);

// LOD 控制
ViewportClient->SetLODLevel(0);      // LOD 0
ViewportClient->SetLODLevel(INDEX_NONE); // LOD Auto
int32 LODCount = ViewportClient->GetLODCount();
```

### 进阶用法：编辑器模式控制

```cpp
// 通过编辑器模式控制构造视口的显示选项
// 来源: Private/ChaosClothAsset/ClothEditorMode.h

UChaosClothAssetEditorMode* ClothMode = /* 获取编辑器模式 */;

// 切换构造视口的视图模式（2D/3D/渲染）
ClothMode->SetConstructionViewMode(EClothPatternVertexType::Sim2D);
ClothMode->SetConstructionViewMode(EClothPatternVertexType::Sim3D);

// 切换线框显示
ClothMode->ToggleConstructionViewWireframe();
bool bWireframe = ClothMode->IsConstructionViewWireframeActive();

// 切换缝合线显示
ClothMode->ToggleConstructionViewSeams();
bool bSeams = ClothMode->IsConstructionViewSeamsActive();

// 切换缝合线折叠
ClothMode->ToggleConstructionViewSeamsCollapse();

// 切换图案颜色
ClothMode->TogglePatternColor();

// 切换表面法线显示
ClothMode->ToggleConstructionViewSurfaceNormals();

// 获取边界框
FBox SelectionBox = ClothMode->SelectionBoundingBox();
FBox PreviewBox = ClothMode->PreviewBoundingBox();
```

### 进阶用法：预览场景配置

```cpp
// 配置布料预览场景
// 来源: Private/ChaosClothAsset/ClothEditorPreviewScene.h

UChaosClothPreviewSceneDescription* Description = /* 获取预览场景描述 */;

// 设置骨骼网格体
Description->SkeletalMeshAsset = MySkeletalMesh;

// 设置动画
Description->AnimationAsset = MyAnimation;

// 设置变换
Description->Translation = FVector3d(0, 0, 0);
Description->Rotation = FVector3d(0, 0, 0);
Description->Scale = FVector3d(1, 1, 1);

// 布料组件参数
Description->SolverGeometryScale = 1.0f;
Description->TeleportDistanceThreshold = 0.0f;
Description->TeleportRotationThreshold = 0.0f;

// PIE 期间是否暂停
Description->bPauseWhilePlayingInEditor = true;
```

## Demo 示例

### 最小编辑器扩展示例

```cpp
// MyClothEditorExtension.h
#pragma once

#include "CoreMinimal.h"
#include "ChaosClothAsset/ClothEditorMode.h"

class FMyClothEditorExtension
{
public:
    // 在布料编辑器中注册自定义工具
    static void RegisterCustomTool();
    
    // 获取当前编辑器模式的模拟可视化
    static TWeakPtr<UE::Chaos::ClothAsset::FClothEditorSimulationVisualization> 
        GetSimulationVisualization(UChaosClothAssetEditorMode* ClothMode);
};
```

```cpp
// MyClothEditorExtension.cpp
#include "MyClothEditorExtension.h"
#include "ChaosClothAsset/ClothEditor3DViewportClient.h"
#include "ChaosClothAsset/ClothEditorSimulationVisualization.h"

void FMyClothEditorExtension::RegisterCustomTool()
{
    // 注册自定义工具到布料编辑器的工具框架
    // 具体实现取决于 Interactive Tools Framework 的工具注册方式
}

TWeakPtr<UE::Chaos::ClothAsset::FClothEditorSimulationVisualization>
FMyClothEditorExtension::GetSimulationVisualization(UChaosClothAssetEditorMode* ClothMode)
{
    if (!ClothMode)
    {
        return nullptr;
    }
    
    // 通过编辑器模式获取模拟可视化对象
    // 用于自定义调试绘制或扩展可视化菜单
    return nullptr; // 实际实现需要访问模式内部状态
}
```

## 模块依赖

从 Build.cs 分析，该插件依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `ChaosClothAsset` | 布料资产核心数据结构和运行时逻辑 |
| `Dataflow` | Dataflow 节点图框架，用于布料资产的可视化编程构建 |
| `BaseCharacterFXEditor` | 角色特效编辑器基础框架，提供编辑器模式、工具包等基础设施 |
| `GeometryCollection` | 几何集合管理（ManagedArrayCollection），用于布料数据存储 |
| `GeometryFramework` | 几何框架，提供动态网格和预览几何体支持 |
| `InteractiveToolsFramework` | 交互式工具框架，用于构建编辑器中的交互工具 |
| `MeshModelingTools` | 网格建模工具（重网格化等） |
| `SkeletalMeshEditor` | 骨骼网格体编辑器基础设施 |

## 维护状态

### 近期更新

- 2026-04-21 `600f5cce` [Chaos Cloth Asset] Moved Cloth Asset modules out of beta.
- 2026-04-14 `0d40a411` [ContentBrowser] New Add Menu Physics Menu
- 2026-04-14 `35e60df1` Migrate UE_LOG to UE_LOGF.
- 2026-04-10 `0be5748b` Dataflow : Move all assets to use the new way to bind dataflow menu commends in the asset context me
- 2026-04-07 `30afa955` Cloth : Use the new template user experience

> 注：该插件创建时间较新（2026-04-07），git log 仅显示初始提交。多个类标记了 `UE_DEPRECATED(5.8, ...)`，表明部分功能正在从编辑器模块向运行时模块迁移。

### 维护评价

- **状态**：🆕 新创建的插件，处于活跃开发初期
- **架构**：基于成熟的 BaseCharacterFXEditor 框架，架构设计合理
- **迁移计划**：多个类（如 `UChaosClothAssetThumbnailRenderer`、`FThumbnailScene`、`AChaosClothPreviewActor`）已标记为 5.8 废弃，计划迁移到 `ChaosClothAsset` 模块的 internal 部分
- **模块类型注意**：Build.cs 中两个模块标记为 `Runtime` 类型，但 .uplugin 中 `ChaosClothAssetEditor` 模块标记为 `Editor` 类型，实际使用时应以 .uplugin 为准
- **推荐**：该插件是 Chaos 布料系统编辑器工作流的核心组件，如果你需要编辑布料资产，这是必需的依赖。由于是新插件，API 可能在后续版本中发生变化

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetEditorCore)
- 官方文档：暂无
- 相关插件：`ChaosClothAsset`（运行时核心）、`Dataflow`（数据流图框架）、`BaseCharacterFXEditor`（编辑器基础框架）