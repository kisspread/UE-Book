# Chaos Cloth Asset Editor Core

> Core required functionalities for editing and creating Dataflow based Cloth Assets.

| 属性 | 值 |
|---|---|
| 中文名 | 布料资产编辑器核心 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ChaosClothAssetEditor` (Runtime), `ChaosClothAssetEditorTools` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-01-27 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetEditorCore) | |

## 用途

这个插件是 Chaos Cloth 资产编辑器的核心模块，为基于 Dataflow 图的布料资产提供完整的编辑器环境。它从原有的 `ChaosClothEditor` 插件拆分而来，专注于编辑器功能，将 USD 相关代码移出编辑器模块。

插件解决的核心问题是：**如何在编辑器中可视化、编辑和调试 Dataflow 驱动的布料资产**。它提供了一套完整的布料编辑器 UI，包括：

- **双视口架构**：2D 构造视口（用于编辑布料面板的拓扑结构、缝合线）和 3D 预览视口（用于查看布料模拟效果）
- **Dataflow 图编辑器集成**：直接在编辑器中编辑布料的 Dataflow 节点图，选中节点即可查看和修改其属性
- **交互式工具框架集成**：基于 UE 的 Interactive Tools Framework，支持重网格化（Remesh）、权重绘制（Weight Map Paint）、属性编辑（Attribute Editor）、蒙皮权重传输（Transfer Skin Weights）、网格选择（Mesh Selection）等工具
- **模拟控制与可视化**：软/硬重置模拟、暂停/恢复、LOD 切换、线框/法线/接缝/权重图等调试可视化
- **旧版布料资产转换**：将旧版 `UClothingAssetCommon` 资产转换为新的基于 Dataflow 的 `UChaosClothAsset`

## 使用场景

- 你正在为角色制作布料服装，需要编辑布料物理参数和拓扑结构 → 使用此插件的布料资产编辑器
- 你需要将项目中旧版的布料资产迁移到新的 Dataflow 架构 → 使用 `FLegacyClothingConverter` 进行转换
- 你需要可视化调试布料的权重图、法线、空气动力学等模拟数据 → 使用编辑器的模拟可视化功能
- 你需要在 2D 构造视口中编辑布料面板的接缝和拓扑 → 使用构造视口的接缝编辑和面板颜色显示
- 你需要基于 Dataflow 节点图工作流创建和编辑布料资产 → 此插件提供完整的 Dataflow 图编辑器集成

## 蓝图用法

此插件主要面向编辑器扩展，不暴露常规的 `BlueprintCallable` API。但通过 `UChaosClothEditorOptions`（继承自 `UDeveloperSettings`）可以配置编辑器行为：

### 配置选项

| 属性 | 说明 | 所在类 |
|---|---|---|
| `bClothAssetsOpenInDataflowEditor` | 是否默认在 Dataflow 编辑器中打开布料资产（而非旧版布料编辑器） | `UChaosClothEditorOptions` |
| `ConstructionViewportMousePanButton` | 构造视口 2D 模式下的平移鼠标按键 | `UChaosClothEditorOptions` |

可通过 **Project Settings → Plugins → Chaos Cloth Editor** 进行配置。

## C++ 用法

此插件主要面向编辑器内部扩展，C++ API 集中在编辑器模式、工具和预览场景管理。

### 头文件引入

```cpp
#include "ChaosClothAsset/LegacyClothingConverter.h"
#include "ChaosClothAsset/ClothEditorOptions.h"
```

### 基本用法：旧版布料资产转换

将旧版布料资产转换为新的 Dataflow 驱动的 `UChaosClothAsset`：

```cpp
#include "ChaosClothAsset/LegacyClothingConverter.h"
#include "ChaosClothAsset/Public/ChaosClothAsset/UChaosClothAsset.h"

// 将旧版布料资产转换为新资产
UE::Chaos::ClothAsset::FLegacyClothingConverterResult Result =
    UE::Chaos::ClothAsset::FLegacyClothingConverter::Convert(
        SourceLegacyClothingAsset,
        TEXT("/Game/Characters/Cloth"),
        TEXT("ConvertedClothAsset")
    );

if (Result.CreatedAsset)
{
    // 转换成功，Result.CreatedAssetPath 包含新资产的路径
    UE_LOG(LogTemp, Log, TEXT("Cloth asset created at: %s"), *Result.CreatedAssetPath);
}
else
{
    // 转换失败，Result.ErrorText 包含错误信息
    UE_LOG(LogTemp, Error, TEXT("Conversion failed: %s"), *Result.ErrorText.ToString());
}
```

### 基本用法：转换到已有资产

如果需要将旧版数据覆盖到已存在的 `UChaosClothAsset` 上：

```cpp
// 转换到已有资产（就地修改）
UE::Chaos::ClothAsset::FLegacyClothingConverterResult Result =
    UE::Chaos::ClothAsset::FLegacyClothingConverter::ConvertInto(
        SourceLegacyClothingAsset,
        ExistingClothAsset  // 会被重置为转换模板的 Dataflow 图
    );
```

> **注意**：`FLegacyClothingConverter` 标记为 `UE_EXPERIMENTAL(5.8)`，属于实验性 API，使用需谨慎。当前仅支持导入 LOD 0，多 LOD 资产会丢失 LOD 0 以外的数据。

### 进阶用法：编辑器模式定制

如果你需要在自定义资产编辑器中嵌入布料编辑模式，可以通过继承或使用编辑器模式相关类：

```cpp
#include "ChaosClothAsset/ClothEditorMode.h"

// 获取布料编辑器模式 ID
const FEditorModeID& ClothModeId = UChaosClothAssetEditorMode::EM_ChaosClothAssetEditorModeId;

// 在模式中控制模拟
UChaosClothAssetEditorMode* ClothMode = /* 获取编辑器模式实例 */;
ClothMode->SetEnableSimulation(true);   // 启用模拟
ClothMode->HardResetSimulation();       // 硬重置模拟
ClothMode->SuspendSimulation();         // 暂停模拟

// 设置构造视口的显示模式
ClothMode->SetConstructionViewMode(EClothPatternVertexType::Sim2D);  // 2D 模式
ClothMode->ToggleConstructionViewWireframe();  // 切换线框显示
ClothMode->TogglePatternColor();              // 切换面板颜色
```

## Demo 示例

以下展示如何创建一个简单的布料预览场景来渲染布料资产：

```cpp
// ClothPreviewDemo.h
#pragma once

#include "CoreMinimal.h"
#include "ChaosClothAsset/ClothEditorPreviewScene.h"

class FClothPreviewDemo
{
public:
    void Initialize();
    void Tick(float DeltaTime);
    void SetClothAsset(UChaosClothAsset* InAsset);
    void SetSkeletalMesh(USkeletalMesh* InMesh);
    void SetAnimation(UAnimationAsset* InAnim);

private:
    TSharedPtr<UE::Chaos::ClothAsset::FChaosClothPreviewScene> PreviewScene;
};
```

```cpp
// ClothPreviewDemo.cpp
#include "ClothPreviewDemo.h"
#include "ChaosClothAsset/Public/ChaosClothAsset/UChaosClothAsset.h"
#include "ChaosClothComponent.h"
#include "Animation/AnimationAsset.h"

void FClothPreviewDemo::Initialize()
{
    // 创建预览场景
    FPreviewScene::ConstructionValues CV;
    CV.bAllowAudioPlayback = false;
    CV.bShouldSimulatePhysics = false;
    PreviewScene = MakeShared<UE::Chaos::ClothAsset::FChaosClothPreviewScene>(CV);
}

void FClothPreviewDemo::Tick(float DeltaTime)
{
    if (PreviewScene.IsValid())
    {
        PreviewScene->GetWorld()->Tick(LEVELTICK_All, DeltaTime);
    }
}

void FClothPreviewDemo::SetClothAsset(UChaosClothAsset* InAsset)
{
    if (PreviewScene.IsValid() && InAsset)
    {
        PreviewScene->SetClothAsset(InAsset);
    }
}

void FClothPreviewDemo::SetSkeletalMesh(USkeletalMesh* InMesh)
{
    if (PreviewScene.IsValid())
    {
        UChaosClothPreviewSceneDescription* Description =
            PreviewScene->GetPreviewSceneDescription();
        if (Description)
        {
            Description->SkeletalMeshAsset = InMesh;
            Description->SceneDescriptionPropertyChanged(
                GET_MEMBER_NAME_CHECKED(UChaosClothPreviewSceneDescription, SkeletalMeshAsset));
        }
    }
}

void FClothPreviewDemo::SetAnimation(UAnimationAsset* InAnim)
{
    if (PreviewScene.IsValid())
    {
        UChaosClothPreviewSceneDescription* Description =
            PreviewScene->GetPreviewSceneDescription();
        if (Description)
        {
            Description->AnimationAsset = InAnim;
            Description->SceneDescriptionPropertyChanged(
                GET_MEMBER_NAME_CHECKED(UChaosClothPreviewSceneDescription, AnimationAsset));
        }
    }
}
```

## 模块依赖

从源码分析中可推断以下特殊依赖：

| 模块 | 用途 |
|---|---|
| `ChaosClothAsset` | 布料资产运行时核心（`UChaosClothAsset`、`UChaosClothComponent`） |
| `Dataflow` | Dataflow 图编辑框架（`SDataflowGraphEditor`、`FEngineContext`、节点系统） |
| `CharacterFXEditor` | 角色特效编辑器基类（`FBaseCharacterFXEditorMode`、`FBaseCharacterFXEditorToolkit`） |
| `EditorInteractiveToolsFramework` | 交互式工具框架（工具注册、目标工厂、视口交互） |
| `InterchangeClothAsset` | 布料资产导入/重导入支持 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `b9a938ae` | Cleanup Chaos Cloth Asset converter | 清理布料资产转换器代码 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 转 float 的编译警告 |
| 2026-05-12 | `a7e94182` | Interchange Cloth Asset: Add support for reimporting; | 为 Interchange 布料资产添加重导入支持 |
| 2026-05-12 | `f1d5a018` | Dataflow : add HUD selection information to both Cloth and dataflow selection tool viewports | 在布料和 Dataflow 选择工具视口中添加 HUD 选中信息 |
| 2026-04-27 | `b6b093cd` | CIS - Fixed Issue 1323734: Compile warnings in Module.ChaosClothAssetEditor.cpp, ChaosClothAssetEdit | 修复编译警告问题 |

### 维护评价

**🟢 活跃维护中**

- **创建时间**：2026-01-27，非常新的插件（约 4 个月）
- **更新频率**：近 1 个月内有 5 次提交，更新频繁
- **更新内容**：涵盖功能增强（重导入支持、HUD 信息）、代码清理、bug 修复，属于正常迭代节奏
- **实验性标记**：版本号为 0.1，旧版转换器标记为 `UE_EXPERIMENTAL(5.8)`
- **已知限制**：
  - 旧版布料资产转换仅支持 LOD 0，多 LOD 资产会丢失其他 LOD 数据
  - 部分类（如缩略图渲染器）已标记为 `UE_DEPRECATED(5.8)`，计划迁移到 `ChaosClothAsset` 运行时模块
  - 旧版 Cloth Panel Editor 已废弃，推荐使用 Dataflow Editor

**推荐使用**：如果你正在使用 UE5.8+ 的 Chaos 布料系统，此插件是编辑布料资产的必备工具。注意它依赖于 `ChaosClothAsset` 运行时插件，两者需配合使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetEditorCore)
- 官方文档（暂无）