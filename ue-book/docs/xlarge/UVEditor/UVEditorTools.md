# UVEditor

> Asset editor for modifying the UV mapping of a mesh

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（材质、样式资源） |
| 模块 | `UVEditor` (Editor), `UVEditorTools` (Editor), `UVEditorToolsEditorOnly` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-04-21 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/UVEditor) | |

## 用途

UVEditor 是 UE5 内置的 **UV 编辑器**，为网格体提供完整的 UV 映射编辑能力。它解决的核心问题是：在引擎内直接编辑网格体的 UV 坐标，无需借助外部 DCC 工具（如 Blender、Maya）。

该插件提供了一个专用的资产编辑器界面，包含：
- **2D 展开视图**：显示 UV 展开后的平面布局，支持交互式编辑
- **3D 实时预览**：同步显示 UV 修改在原始网格体上的效果
- **完整的 UV 工具集**：包括选择、变换、接缝编辑、UV 重计算、布局优化、纹素密度控制等

插件依赖 `GeometryProcessing`、`MeshModelingToolset` 和 `MeshModelingToolsetExp`，底层使用 `FDynamicMesh3` 进行几何操作，支持多 UV 层、UDIM 瓦片、多资产同时编辑。

> ⚠️ **注意**：此插件标记为 `IsBetaVersion=true`，功能可能不完整或存在已知问题。

## 使用场景

- 你需要在引擎内快速调整模型的 UV 映射，不想切换到外部工具 → 用 UVEditor
- 你需要为游戏资产设置统一的纹素密度 → 用 UVEditor 的 Texel Density 工具
- 你需要将 UV 岛重新排列以优化纹理空间利用率 → 用 UVEditor 的 Layout 工具
- 你需要在网格体上切割或缝合 UV 接缝 → 用 UVEditor 的 Seam 工具
- 你需要对 UV 进行批量变换（移动、旋转、缩放、对齐、分布）→ 用 UVEditor 的 Transform 工具
- 你需要导出 UV 布局快照为纹理资产 → 用 UVEditor 的 UV Snapshot 工具

## 蓝图用法

UVEditor 是编辑器模式插件，主要通过编辑器 UI 交互使用，不直接暴露蓝图节点。其内部工具类通过 `UInteractiveToolBuilder` 模式构建，不提供 `BlueprintCallable` 接口。

### 核心交互方式

UVEditor 的使用方式是：
1. 在内容浏览器中选择一个 Static Mesh 或 Skeletal Mesh 资产
2. 右键选择"UV Editor"或通过工具栏打开
3. 在 UV Editor 窗口中使用各种工具进行编辑

### 工具列表

| 工具 | 说明 | 所在类 |
|---|---|---|
| Select | 基础选择工具，支持顶点/边/面选择及 Gizmo 变换 | `UUVSelectTool` |
| Brush Select | 笔刷选择工具，支持笔刷半径和岛扩展 | `UUVEditorBrushSelectTool` |
| Seam | 接缝编辑工具，支持切割和缝合模式 | `UUVEditorSeamTool` |
| Transform | UV 变换工具，支持移动/旋转/缩放/对齐/分布 | `UUVEditorTransformTool` |
| Layout | UV 布局优化工具，自动排列 UV 岛 | `UUVEditorLayoutTool` |
| Recompute UVs | 基于网格体分段重新计算 UV | `UUVEditorRecomputeUVsTool` |
| Texel Density | 纹素密度工具，采样和调整纹素密度 | `UUVEditorTexelDensityTool` |
| UV Snapshot | 导出 UV 布局为纹理资产 | `UUVEditorUVSnapshotTool` |
| Channel Edit | UV 通道管理工具，支持添加/复制/删除 UV 层 | `UUVEditorChannelEditTool` |

## C++ 用法

UVEditor 的 C++ API 主要面向插件内部扩展和自定义工具开发。

### 头文件引入

```cpp
#include "UVEditorToolsModule.h"
#include "ToolTargets/UVEditorToolMeshInput.h"
#include "Selection/UVToolSelectionAPI.h"
#include "ContextObjects/UVToolContextObjects.h"
#include "UVEditorToolBase.h"
```

### 基本用法：创建自定义 UV 工具

UVEditor 的工具系统基于 `UInteractiveTool` 框架。要创建自定义 UV 工具，需要实现 `IUVEditorGenericBuildableTool` 接口。

```cpp
// 来源: Engine/Plugins/Editor/UVEditor/Source/UVEditorTools/Public/UVEditorToolBase.h

#include "UVEditorToolBase.h"
#include "ToolTargets/UVEditorToolMeshInput.h"

// 自定义工具类，实现 IUVEditorGenericBuildableTool 接口
UCLASS()
class UMyCustomUVTool : public UInteractiveTool, public IUVEditorGenericBuildableTool
{
    GENERATED_BODY()

public:
    // IUVEditorGenericBuildableTool 接口实现 - 接收网格体输入
    virtual void SetTargets(const TArray<TObjectPtr<UUVEditorToolMeshInput>>& TargetsIn) override
    {
        Targets = TargetsIn;
    }

    virtual void Setup() override
    {
        Super::Setup();
        // 在这里初始化工具逻辑
        // Targets 中的每个 UUVEditorToolMeshInput 包含:
        //   - UnwrapCanonical: 展开的 UV 网格体
        //   - AppliedCanonical: 应用 UV 后的 3D 网格体
        //   - UnwrapPreview / AppliedPreview: 用于后台操作的预览
    }

    virtual void Shutdown(EToolShutdownType ShutdownType) override
    {
        Super::Shutdown(ShutdownType);
    }

protected:
    UPROPERTY()
    TArray<TObjectPtr<UUVEditorToolMeshInput>> Targets;
};
```

### 基本用法：使用选择 API

```cpp
// 来源: Engine/Plugins/Editor/UVEditor/Source/UVEditorTools/Public/Selection/UVToolSelectionAPI.h

#include "Selection/UVToolSelectionAPI.h"

// 在工具中访问选择 API
void UMyUVTool::HandleSelection()
{
    // SelectionAPI 通过上下文对象存储获取
    if (SelectionAPI && SelectionAPI->HaveSelections())
    {
        const TArray<FUVToolSelection>& Selections = SelectionAPI->GetSelections();
        FUVToolSelection::EType Type = SelectionAPI->GetSelectionsType();
        
        // 遍历每个资产的选择
        for (const FUVToolSelection& Selection : Selections)
        {
            UUVEditorToolMeshInput* Target = Selection.Target.Get();
            const TSet<int32>& SelectedIDs = Selection.SelectedIDs;
            
            // 根据选择类型处理
            switch (Selection.Type)
            {
            case FUVToolSelection::EType::Vertex:
                // 处理顶点选择
                break;
            case FUVToolSelection::EType::Edge:
                // 处理边选择
                break;
            case FUVToolSelection::EType::Triangle:
                // 处理三角形选择
                break;
            }
        }
    }
}
```

### 进阶用法：实现 UV 操作（Action）

UVEditor 使用 Action 模式执行 UV 拓扑操作（如分割、缝合、创建岛）。

```cpp
// 来源: Engine/Plugins/Editor/UVEditor/Source/UVEditorTools/Public/Actions/UVToolAction.h
// 来源: Engine/Plugins/Editor/UVEditor/Source/UVEditorTools/Public/Actions/UVSplitAction.h

#include "Actions/UVToolAction.h"

// 自定义 UV Action
UCLASS()
class UMyUVAction : public UUVToolAction
{
    GENERATED_BODY()

public:
    // 检查当前状态是否允许执行此操作
    virtual bool CanExecuteAction() const override
    {
        // SelectionAPI 和 EmitChangeAPI 在 Setup 时已注入
        return SelectionAPI && SelectionAPI->HaveSelections();
    }

    // 执行操作
    virtual bool ExecuteAction() override
    {
        if (!CanExecuteAction())
        {
            return false;
        }

        // 开始撤销事务
        EmitChangeAPI->BeginUndoTransaction(FText::FromString(TEXT("My UV Action")));

        // 执行 UV 操作...
        // 使用 SelectionAPI->GetSelections() 获取当前选择
        // 修改 UnwrapCanonical 网格体的 UV 数据

        EmitChangeAPI->EndUndoTransaction();
        return true;
    }
};
```

### 进阶用法：使用网格体输入对象

```cpp
// 来源: Engine/Plugins/Editor/UVEditor/Source/UVEditorTools/Public/ToolTargets/UVEditorToolMeshInput.h

#include "ToolTargets/UVEditorToolMeshInput.h"

void UMyUVTool::ProcessMeshInput(UUVEditorToolMeshInput* Input)
{
    // 获取展开的 UV 网格体（2D 平面表示）
    TSharedPtr<FDynamicMesh3> UnwrapMesh = Input->UnwrapCanonical;
    
    // 获取应用 UV 后的 3D 网格体
    TSharedPtr<FDynamicMesh3> AppliedMesh = Input->AppliedCanonical;
    
    // 获取 UV 层信息
    int32 NumUVLayers = UnwrapMesh->Attributes()->NumUVLayers();
    
    // 修改 UV 后，通知输入对象更新所有表示
    // Input 会自动同步 UnwrapCanonical、AppliedCanonical 及其预览
    Input->OnCanonicalModified.Broadcast({true, true});
}
```

### 进阶用法：使用 EmitChange API 进行撤销/重做

```cpp
// 来源: Engine/Plugins/Editor/UVEditor/Source/UVEditorTools/Public/ContextObjects/UVToolContextObjects.h

#include "ContextObjects/UVToolContextObjects.h"

void UMyUVTool::ApplyUVChange()
{
    // 工具无关的变更（在工具结束后仍可撤销）
    EmitChangeAPI->EmitToolIndependentUnwrapCanonicalChange(
        MeshInput,
        MoveTemp(MeshChange),  // TUniquePtr<FDynamicMeshChange>
        FText::FromString(TEXT("Modified UVs"))
    );
    
    // 工具相关的变更（仅在当前工具激活期间可撤销）
    EmitChangeAPI->EmitToolDependentChange(
        TargetObject,
        MoveTemp(Change),  // TUniquePtr<FToolCommandChange>
        FText::FromString(TEXT("Tool-specific change"))
    );
}
```

## Demo 示例

以下是一个最小的自定义 UV 工具实现，展示如何在 UVEditor 中注册和使用自定义工具。

### MyCustomUVTool.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "InteractiveTool.h"
#include "UVEditorToolBase.h"
#include "ToolTargets/UVEditorToolMeshInput.h"
#include "Selection/UVToolSelectionAPI.h"
#include "ContextObjects/UVToolContextObjects.h"

#include "MyCustomUVTool.generated.h"

UCLASS()
class UMyCustomUVToolSettings : public UInteractiveToolPropertySet
{
    GENERATED_BODY()
public:
    /** UV 缩放因子 */
    UPROPERTY(EditAnywhere, Category = Options, meta = (ClampMin = "0.01", ClampMax = "100"))
    float ScaleFactor = 1.0f;
};

UCLASS()
class UMyCustomUVTool : public UInteractiveTool, public IUVEditorGenericBuildableTool
{
    GENERATED_BODY()

public:
    // IUVEditorGenericBuildableTool
    virtual void SetTargets(const TArray<TObjectPtr<UUVEditorToolMeshInput>>& TargetsIn) override;

    // UInteractiveTool
    virtual void Setup() override;
    virtual void Shutdown(EToolShutdownType ShutdownType) override;
    virtual bool HasCancel() const override { return true; }
    virtual bool HasAccept() const override { return true; }
    virtual bool CanAccept() const override;

protected:
    UPROPERTY()
    TArray<TObjectPtr<UUVEditorToolMeshInput>> Targets;

    UPROPERTY()
    TObjectPtr<UMyCustomUVToolSettings> Settings;

    UPROPERTY()
    TObjectPtr<UUVToolSelectionAPI> SelectionAPI;

    UPROPERTY()
    TObjectPtr<UUVToolEmitChangeAPI> EmitChangeAPI;

    void ApplyScaleToSelection();
};
```

### MyCustomUVTool.cpp

```cpp
#include "MyCustomUVTool.h"
#include "DynamicMesh/DynamicMesh3.h"
#include "DynamicMesh/DynamicMeshAttributeSet.h"

void UMyCustomUVTool::SetTargets(const TArray<TObjectPtr<UUVEditorToolMeshInput>>& TargetsIn)
{
    Targets = TargetsIn;
}

void UMyCustomUVTool::Setup()
{
    Super::Setup();

    // 创建属性集
    Settings = NewObject<UMyCustomUVToolSettings>(this);
    AddToolPropertySource(Settings);

    // 从上下文获取 API 对象
    SelectionAPI = Cast<UUVToolSelectionAPI>(
        GetToolManager()->GetContextObjectStore()->FindContext<UUVToolSelectionAPI>());
    EmitChangeAPI = Cast<UUVToolEmitChangeAPI>(
        GetToolManager()->GetContextObjectStore()->FindContext<UUVToolEmitChangeAPI>());
}

void UMyCustomUVTool::Shutdown(EToolShutdownType ShutdownType)
{
    if (ShutdownType == EToolShutdownType::Accept)
    {
        ApplyScaleToSelection();
    }
    Super::Shutdown(ShutdownType);
}

bool UMyCustomUVTool::CanAccept() const
{
    return Targets.Num() > 0;
}

void UMyCustomUVTool::ApplyScaleToSelection()
{
    if (!SelectionAPI || !EmitChangeAPI)
    {
        return;
    }

    const TArray<FUVToolSelection>& Selections = SelectionAPI->GetSelections();
    if (Selections.Num() == 0)
    {
        return;
    }

    EmitChangeAPI->BeginUndoTransaction(FText::FromString(TEXT("Scale UV Selection")));

    for (const FUVToolSelection& Selection : Selections)
    {
        UUVEditorToolMeshInput* Input = Selection.Target.Get();
        if (!Input || !Input->UnwrapCanonical)
        {
            continue;
        }

        FDynamicMesh3& Mesh = *Input->UnwrapCanonical;
        FDynamicMeshUVOverlay* UVOverlay = Mesh.Attributes()->GetUVLayer(0);
        if (!UVOverlay)
        {
            continue;
        }

        // 对选中的三角形的 UV 坐标应用缩放
        for (int32 Tid : Selection.SelectedIDs)
        {
            for (int32 i = 0; i < 3; i++)
            {
                int32 ElementID = UVOverlay->GetElementID(Tid, i);
                if (UVOverlay->IsElement(ElementID))
                {
                    FVector2f UV = UVOverlay->GetElement(ElementID);
                    UV *= Settings->ScaleFactor;
                    UVOverlay->SetElement(ElementID, UV);
                }
            }
        }

        // 通知输入对象网格体已修改
        Input->OnCanonicalModified.Broadcast({true, true});
    }

    EmitChangeAPI->EndUndoTransaction();
}
```

## 模块依赖

从 Build.cs 和 .uplugin 的 Plugins 字段提取：

| 模块 | 用途 |
|---|---|
| `GeometryProcessing` | 几何处理算法（UV 展开、参数化等） |
| `MeshModelingToolset` | 网格建模工具集（交互式工具框架） |
| `MeshModelingToolsetExp` | 网格建模工具集实验性功能 |
| `ModelingOperators` | 建模操作符（TexelDensityOp 等已迁移至此） |
| `GeometryAlgorithms` | 几何算法（UVMetrics 已迁移至此） |

## 维护状态

### 近期更新

```
- febd61e82650 UVEditor: Fixed localization issue for the "Advanced Transform" category label.
- 1bb7cec8a513 Ran update script to removed null initializers when creating TSubclassOf<T> since it will use a code path that is the same as default initializer except that it checks so nullptr is a valid type (which it always is). And that check requires full knowledge of T (so type can't be forward declared) Same for function parameter default values but instead replaced = nullptr with = {} (which uses default initializer)
- 9803c443cfab Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applied using UnrealCodeFixup)
```

- `febd61e82650`：修复了"Advanced Transform"分类标签的本地化问题，属于小修。
- `1bb7cec8a513`：代码清理，移除 `TSubclassOf<T>` 的空初始化器，属于编译器适配。
- `9803c443cfab`：批量添加 `UE_INLINE_GENERATED_CPP_BY_NAME` 宏，属于编译优化。

### 维护评价

- **创建时间**：2021 年 4 月，约 4 年历史
- **代码规模**：211 个源文件，属于大型插件
- **维护状态**：活跃维护中。作为 UE5 核心编辑器功能，由 Epic Games 持续开发
- **实验性标记**：`IsBetaVersion=true`，表明功能仍在完善中，API 可能发生变化
- **已知限制**：
  - 部分头文件已标记为废弃（`UVMetrics.h`、`UVEditorTexelDensityOp.h`），相关功能已迁移至 `GeometryAlgorithms` 和 `ModelingOperators` 模块
  - 作为 Beta 版本，某些工具的 UI 和行为可能在后续版本中调整
- **推荐程度**：✅ 推荐使用。这是 UE5 官方的 UV 编辑解决方案，虽然标记为 Beta，但已具备完整的 UV 编辑能力，适合在引擎内进行 UV 调整工作。对于复杂的 UV 展开需求，仍建议结合外部 DCC 工具使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/UVEditor)
- 官方文档：无（.uplugin 中 DocsURL 为空）