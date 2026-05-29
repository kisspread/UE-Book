# UVEditor

> Asset editor for modifying the UV mapping of a mesh

| 属性 | 值 |
|---|---|
| 中文名 | UV编辑器 |
| 分类 | Other |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、UI控件） |
| 模块 | `UVEditor` (Editor), `UVEditorTools` (Editor), `UVEditorToolsEditorOnly` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-06-15 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/UVEditor) | |

## 用途

UVEditor 是 Unreal Engine 5 内置的 UV 贴图编辑器，用于在引擎内直接修改网格的 UV 映射，无需导出到外部 DCC 工具。它解决的核心问题是：**在不离开引擎工作流的前提下完成 UV 展开、切割、对齐、排布和烘焙等操作**。

该插件从 Experimental 目录迁移而来（2023年6月），目前标记为 Beta 版本。它提供了一个完整的 2D 展开视图 + 3D 实时预览的双视口编辑环境，内置了十余种 UV 操作工具，支持 UDIM 工作流、多 UV 通道管理，以及与 MeshModelingToolset 深度集成的几何处理后端。

**核心能力包括**：
- 多资产同时编辑，每个资产独立的展开网格（UnwrapCanonical）和应用网格（AppliedCanonical）表示
- 顶点/边/三角形/岛屿/网格级选择机制，支持框选和笔刷选择
- UV 变换（缩放/旋转/平移）、对齐、分布操作
- 缝合线切割/连接工具，带路径搜索算法
- 自动 UV 展开（RecomputeUVs）、UV 布局打包（Layout）
- Texel Density 管理与采样
- UV 通道编辑（添加/复制/删除）
- UV 快照导出为纹理资产
- 完整的撤销/重做支持，包括选择状态的事务化

## 使用场景

- 你有一个静态网格需要调整 UV 映射但不想离开引擎 → 用 UVEditor 直接编辑
- 你需要在多个资产之间保持一致的 Texel Density → 用 Texel Density 工具采样和调整
- 你需要快速将 UV 岛屿自动排布到 UDIM 瓦片中 → 用 Layout 工具配合 UDIM 支持
- 你需要对 UV 进行精确的对齐和分布操作 → 用 Transform 工具的对齐/分布模式
- 你需要在模型上绘制切割线来创建新接缝 → 用 Seam 工具的 Cut 模式
- 你需要将 UV 布局导出为纹理用于参考 → 用 UV Snapshot 工具
- 你需要管理网格的多个 UV 通道 → 用 Channel Edit 工具添加/复制/删除通道

## 蓝图用法

UVEditor 是编辑器插件，主要通过编辑器 UI 交互，但其核心 API 可通过 C++ 扩展。

### 核心 API 类

| API 类 | 说明 | 所在头文件 |
|---|---|---|
| `UUVToolSelectionAPI` | 管理选择状态、高亮、选择模式切换 | `Selection/UVToolSelectionAPI.h` |
| `UUVToolEmitChangeAPI` | 发出撤销/重做事务 | `ContextObjects/UVToolContextObjects.h` |
| `UUVToolLivePreviewAPI` | 与 3D 实时预览视口交互 | `ContextObjects/UVToolContextObjects.h` |
| `UUVTool2DViewportAPI` | 与 2D 展开视口交互（UDIM、网格、标尺） | `ContextObjects/UVToolContextObjects.h` |
| `UUVToolViewportButtonsAPI` | 控制视口按钮状态（Gizmo模式、选择模式、吸附） | `ContextObjects/UVToolViewportButtonsAPI.h` |
| `UUVToolAssetAndChannelAPI` | 管理资产和 UV 通道可见性 | `ContextObjects/UVToolContextObjects.h` |
| `UUVToolAABBTreeStorage` | 存储和管理 AABB 加速结构 | `ContextObjects/UVToolContextObjects.h` |
| `UUVEditorToolPropertiesAPI` | 存储当前工具的显示属性集 | `ContextObjects/UVToolContextObjects.h` |

### 选择操作

| 节点/方法 | 说明 | 所在类 |
|---|---|---|
| `HaveSelections()` | 检查是否有选中元素 | `UUVToolSelectionAPI` |
| `GetSelections()` | 获取当前选中对象数组 | `UUVToolSelectionAPI` |
| `GetSelectionsType()` | 获取选择类型（顶点/边/三角形） | `UUVToolSelectionAPI` |
| `SetSelections()` | 设置选择状态并可选广播事件 | `UUVToolSelectionAPI` |
| `ClearSelections()` | 清除选择状态 | `UUVToolSelectionAPI` |
| `SetSelectionMechanicMode()` | 切换选择模式（None/Vertex/Edge/Triangle/Island/Mesh） | `UUVToolSelectionAPI` |
| `SetHighlightVisible()` | 控制高亮显示的可见性 | `UUVToolSelectionAPI` |
| `GetUnwrapSelectionBoundingBoxCenter()` | 获取选择的边界框中心 | `UUVToolSelectionAPI` |

### 工具列表

| 工具类 | 说明 |
|---|---|
| `UUVSelectTool` | 默认选择工具，带变换 Gizmo |
| `UUVEditorTransformTool` | UV 变换/对齐/分布工具 |
| `UUVEditorSeamTool` | 接缝切割/连接工具 |
| `UUVEditorLayoutTool` | UV 自动布局打包工具 |
| `UUVEditorRecomputeUVsTool` | 基于多边形组自动重新计算 UV |
| `UUVEditorTexelDensityTool` | Texel Density 采样与调整 |
| `UUVEditorChannelEditTool` | UV 通道添加/复制/删除 |
| `UUVEditorBrushSelectTool` | 笔刷选择工具 |
| `UUVEditorUVSnapshotTool` | UV 布局导出为纹理 |

## C++ 用法

### 头文件引入

```cpp
#include "Selection/UVToolSelectionAPI.h"
#include "ContextObjects/UVToolContextObjects.h"
#include "ToolTargets/UVEditorToolMeshInput.h"
#include "Operators/UVEditorUVTransformOp.h"
#include "UVEditorTransformTool.h"
#include "UVEditorSeamTool.h"
```

### 基本用法：选择 API

来自 `Public/Selection/UVToolSelectionAPI.h`：

```cpp
// 检查是否有选中元素
if (SelectionAPI->HaveSelections())
{
    // 获取所有选择对象（每个资产一个）
    const TArray<FUVToolSelection>& Selections = SelectionAPI->GetSelections();
    
    // 获取选择类型
    FUVToolSelection::EType Type = SelectionAPI->GetSelectionsType();
    
    // 获取选择边界框中心（用于 Gizmo 定位）
    FVector3d Center = SelectionAPI->GetUnwrapSelectionBoundingBoxCenter(true);
}

// 设置选择模式（顶点/边/三角形/岛屿/网格）
UUVToolSelectionAPI::FSelectionMechanicModeChangeOptions ModeOptions;
ModeOptions.bConvertExisting = true;   // 将现有选择转换为新模式
ModeOptions.bBroadcastIfConverted = true;
ModeOptions.bEmitChanges = true;
SelectionAPI->SetSelectionMechanicMode(
    UUVToolSelectionAPI::EUVEditorSelectionMode::Island, ModeOptions);

// 监听选择变化
SelectionAPI->OnSelectionChanged.AddLambda(
    [](bool bEmitChangeAllowed, uint32 SelectionChangeType)
    {
        // 选择已改变，更新工具状态
    });
```

### 基本用法：撤销/重做事务

来自 `Public/ContextObjects/UVToolContextObjects.h`：

```cpp
// 发出工具无关的变更（工具关闭后仍可撤销）
EmitChangeAPI->EmitToolIndependentChange(
    TargetObject,
    MakeUnique<FMyCustomChange>(),
    NSLOCTEXT("MyTool", "ChangeDesc", "Modified UV coordinates"));

// 发出基于 UnwrapCanonical 网格变更的事务（推荐方式）
EmitChangeAPI->EmitToolIndependentUnwrapCanonicalChange(
    InputObject,
    MakeUnique<FDynamicMeshChange>(/* ... */),
    NSLOCTEXT("MyTool", "ChangeDesc", "Modified unwrap mesh"));

// 发出工具依赖的变更（工具切换后失效）
EmitChangeAPI->EmitToolDependentChange(
    TargetObject,
    MakeUnique<FMyTransientChange>(),
    NSLOCTEXT("MyTool", "TransientDesc", "Preview adjustment"));
```

### 基本用法：UV 输入对象（多网格同步）

来自 `Public/ToolTargets/UVEditorToolMeshInput.h`：

```cpp
// 从 UnwrapPreview 更新应用预览（拖拽时常用，只更新可见项）
InputObject->UpdateAppliedPreviewFromUnwrapPreview(&ChangedVids, &ChangedTids);

// 从预览更新规范网格（拖拽结束后，固化变更）
InputObject->UpdateCanonicalFromPreviews(&ChangedVids, &ChangedTids, true);

// 从 UnwrapCanonical 更新所有表示
InputObject->UpdateAllFromUnwrapCanonical(&ChangedVids, &ChangedTids);

// UV 坐标与展开世界坐标转换
int32 AppliedVid = InputObject->UnwrapVidToAppliedVid(UnwrapVid);

TArray<int32> UnwrapVids;
InputObject->AppliedVidToUnwrapVids(AppliedVid, UnwrapVids);
```

### 进阶用法：UV 变换操作

来自 `Public/Operators/UVEditorUVTransformOp.h`：

```cpp
// 创建 UV 变换操作工厂
auto Factory = NewObject<UUVEditorUVTransformOperatorFactory>();
Factory->TransformType = EUVEditorUVTransformType::Transform;
Factory->OriginalMesh = MeshData;
Factory->Settings = TransformSettings;
Factory->EdgeSelection = EdgeSelectionSet;
Factory->VertexSelection = VertexSelectionSet;

// 获取操作符（用于 MeshOpPreviewWithBackgroundCompute）
TUniquePtr<FDynamicMeshOperator> Op = Factory->MakeNewOperator();

// 配置变换参数
auto TransformOp = static_cast<FUVEditorUVTransformOp*>(Op.Get());
TransformOp->Scale = FVector2D(2.0, 2.0);      // 非均匀缩放
TransformOp->Rotation = 45.0f;                   // 旋转角度
TransformOp->Translation = FVector2D(0.5, 0.0); // 平移偏移
TransformOp->TranslationMode = EUVEditorTranslationModeBackend::Relative;
TransformOp->PivotMode = EUVEditorPivotTypeBackend::BoundingBoxCenter;
```

### 进阶用法：自定义 UV 工具

来自 `Public/UVEditorToolBase.h`：

```cpp
// 实现 IUVEditorGenericBuildableTool 接口以创建自定义 UV 工具
UCLASS()
class UMyCustomUVTool : public UInteractiveTool, public IUVEditorGenericBuildableTool
{
    GENERATED_BODY()
public:
    // IUVEditorGenericBuildableTool 接口
    virtual void SetTargets(const TArray<TObjectPtr<UUVEditorToolMeshInput>>& TargetsIn) override
    {
        Targets = TargetsIn;
    }

    virtual void Setup() override
    {
        UInteractiveTool::Setup();
        // 初始化工具逻辑
    }

    virtual void Shutdown(EToolShutdownType ShutdownType) override
    {
        // 清理资源
        UInteractiveTool::Shutdown(ShutdownType);
    }

protected:
    TArray<TObjectPtr<UUVEditorToolMeshInput>> Targets;
};

// 使用通用构建器注册工具
auto Builder = NewObject<UGenericUVEditorToolBuilder>();
Builder->Initialize(Targets, UMyCustomUVTool::StaticClass());
```

### 进阶用法：选择高亮机制

来自 `Public/Selection/UVToolSelectionHighlightMechanic.h`：

```cpp
// 初始化高亮机制
HighlightMechanic->Initialize(UnwrapWorld, LivePreviewWorld);

// 设置可见性
HighlightMechanic->SetIsVisible(true, true);

// 重建展开视口高亮（使用选择的起始变换）
HighlightMechanic->RebuildUnwrapHighlight(Selections, StartTransform, false);

// 仅移动高亮（不重建，用于跟随 Gizmo 平移）
HighlightMechanic->SetUnwrapHighlightTransform(NewTransform, true, false);

// 在应用预览中高亮选中元素
HighlightMechanic->RebuildAppliedHighlightFromUnwrapSelection(Selections, false);

// 启用配对边高亮（显示可焊接的边对）
HighlightMechanic->SetEnablePairedEdgeHighlights(true);

// 自定义高亮外观
HighlightMechanic->SetColor(FColor::Green);
HighlightMechanic->SetLineThickness(3.0f);
HighlightMechanic->SetPointSize(8.0f);
```

### 进阶用法：UDIM 工作流

来自 `Public/ContextObjects/UVToolContextObjects.h`：

```cpp
// 配置 UDIM 瓦片
TArray<FUDIMBlock> Blocks;
FUDIMBlock Block1;
Block1.UDIM = 1001;
Block1.TextureResolution = 512;
Blocks.Add(Block1);

FUDIMBlock Block2;
Block2.UDIM = 1002;
Block2.TextureResolution = 1024;
Blocks.Add(Block2);

UVTool2DViewportAPI->SetUDIMBlocks(Blocks, true);

// 控制 2D 视口显示
UVTool2DViewportAPI->SetDrawGrid(true, true);
UVTool2DViewportAPI->SetDrawRulers(true, true);
```

## Demo 示例

以下展示一个自定义 UV 操作工具的最小实现：

### MyUVScaleTool.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "InteractiveTool.h"
#include "UVEditorToolBase.h"
#include "ToolTargets/UVEditorToolMeshInput.h"
#include "UVEditorToolAnalyticsUtils.h"

UCLASS()
class UMyUVScaleToolProperties : public UInteractiveToolPropertySet
{
    GENERATED_BODY()
public:
    /** UV 缩放因子 */
    UPROPERTY(EditAnywhere, Category = "Scale", meta = (ClampMin = "0.01", ClampMax = "100.0"))
    float ScaleFactor = 2.0f;
};

UCLASS()
class UMyUVScaleTool : public UInteractiveTool, 
    public IUVToolSupportsSelection,
    public IUVEditorGenericBuildableTool
{
    GENERATED_BODY()

public:
    // IUVEditorGenericBuildableTool
    virtual void SetTargets(const TArray<TObjectPtr<UUVEditorToolMeshInput>>& TargetsIn) override;

    // IUVToolSupportsSelection
    virtual bool SupportsUnsetElementAppliedMeshSelections() const { return false; }

    // UInteractiveTool
    virtual void Setup() override;
    virtual void Shutdown(EToolShutdownType ShutdownType) override;
    virtual void OnTick(float DeltaTime) override;
    virtual bool HasCancel() const override { return true; }
    virtual bool HasAccept() const override { return true; }
    virtual bool CanAccept() const override;
    virtual void OnPropertyModified(UObject* PropertySet, FProperty* Property) override;

protected:
    UPROPERTY()
    TArray<TObjectPtr<UUVEditorToolMeshInput>> Targets;

    UPROPERTY()
    TObjectPtr<UMyUVScaleToolProperties> Settings = nullptr;

    UPROPERTY()
    TObjectPtr<UUVToolSelectionAPI> SelectionAPI = nullptr;

    UPROPERTY()
    TObjectPtr<UUVToolEmitChangeAPI> EmitChangeAPI = nullptr;

    UPROPERTY()
    TArray<TObjectPtr<UUVEditorUVTransformOperatorFactory>> Factories;

    void UpdateFactories();
};
```

### MyUVScaleTool.cpp

```cpp
#include "MyUVScaleTool.h"
#include "Operators/UVEditorUVTransformOp.h"
#include "ContextObjects/UVToolContextObjects.h"
#include "MeshOpPreviewWithBackgroundCompute.h"
#include "ToolContextInterfaces.h"
#include "Selection/UVToolSelectionAPI.h"
#include "UVEditorToolMeshInput.h"

void UMyUVScaleTool::SetTargets(
    const TArray<TObjectPtr<UUVEditorToolMeshInput>>& TargetsIn)
{
    Targets = TargetsIn;
}

void UMyUVScaleTool::Setup()
{
    UInteractiveTool::Setup();

    // 获取上下文对象
    SelectionAPI = Cast<UUVToolSelectionAPI>(
        GetToolManager()->GetContextObjectStore()->FindContext<UUVToolSelectionAPI>());
    EmitChangeAPI = Cast<UUVToolEmitChangeAPI>(
        GetToolManager()->GetContextObjectStore()->FindContext<UUVToolEmitChangeAPI>());

    // 创建属性集
    Settings = NewObject<UMyUVScaleToolProperties>(this);
    AddPropertySet(Settings);

    // 为每个目标创建操作工厂
    for (auto& Target : Targets)
    {
        auto Factory = NewObject<UUVEditorUVTransformOperatorFactory>(this);
        Factory->TransformType = EUVEditorUVTransformType::Transform;
        Factory->OriginalMesh = Target->UnwrapCanonical;
        Factory->Settings = Settings;

        // 传递当前选择
        if (SelectionAPI && SelectionAPI->HaveSelections())
        {
            // 提取边和顶点选择
            for (const auto& Sel : SelectionAPI->GetSelections())
            {
                if (Sel.Type == FUVToolSelection::EType::Edge)
                {
                    Factory->EdgeSelection = Sel.SelectedIDs;
                }
                else if (Sel.Type == FUVToolSelection::EType::Vertex)
                {
                    Factory->VertexSelection = Sel.SelectedIDs;
                }
            }
        }

        Factories.Add(Factory);
    }

    UpdateFactories();
}

void UMyUVScaleTool::Shutdown(EToolShutdownType ShutdownType)
{
    Factories.Empty();
    UInteractiveTool::Shutdown(ShutdownType);
}

void UMyUVScaleTool::OnTick(float DeltaTime)
{
    // 持续更新预览
}

bool UMyUVScaleTool::CanAccept() const
{
    return true;
}

void UMyUVScaleTool::OnPropertyModified(UObject* PropertySet, FProperty* Property)
{
    UpdateFactories();
}

void UMyUVScaleTool::UpdateFactories()
{
    for (auto& Factory : Factories)
    {
        if (Factory && Factory->Settings)
        {
            // 重置预览以反映新的缩放参数
            Factory->OriginalMesh = Targets[Factories.IndexOfByKey(Factory)]->UnwrapCanonical;
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GeometryProcessing` | 几何处理算法（UV 展开、网格操作等） |
| `MeshModelingToolset` | 网格建模工具集（编辑器工具框架） |
| `MeshModelingToolsetExp` | 实验性网格建模工具 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 截断为 float 的编译警告 |
| 2026-04-24 | `0213bc37` | [ITF] Call `UInputRouter::ForceTerminateSource()` from within `UInputRouter::DeregisterSource()` pri | 输入框架改进：在注销输入源时强制终止 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 日志宏迁移到新的 UE_LOGF 格式 |
| 2026-03-10 | `0b781d0c` | Add/RemoveOverlayWidget: | 视口覆盖控件的添加/移除功能调整 |
| 2026-03-05 | `1adb9f68` | New material translator work: | 材质翻译器的更新工作 |

### 维护评价

UVEditor 作为 Epic Games 官方维护的核心编辑器工具，处于**活跃维护**状态。虽然标记为 Beta（IsBetaVersion=true），但自 2023 年从 Experimental 迁移以来持续获得更新，最近的提交集中在 2026 年 5 月，涵盖编译警告修复、输入系统改进和日志系统迁移等。

**优势**：
- Epic Games 直接维护，代码质量有保障
- 持续的活跃开发，bug 修复及时
- 深度集成 UE5 工具框架（Interactive Tools Framework），架构设计成熟
- 完整的撤销/重做、选择、高亮机制
- 支持 UDIM 工作流和多 UV 通道

**限制与注意事项**：
- 仍标记为 Beta，API 可能在未来版本中发生变化
- 部分功能标记为实验性（如 UDIM 原型支持，通过 CVar 控制）
- 作为编辑器插件，不支持运行时使用
- 依赖 GeometryProcessing 和 MeshModelingToolset，需确保这些插件已启用

**推荐使用**：✅ 推荐。虽然 Beta 标记需要留意潜在的 API 变化，但对于需要在引擎内编辑 UV 的工作流来说，这是官方推荐且持续维护的解决方案。外部 DCC 工具（Blender、Maya 等）在复杂的 UV 工作中仍然更成熟，但对于快速调整和简单的 UV 操作，UVEditor 已经足够实用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/UVEditor)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/UVEditor/Tests)（如存在）