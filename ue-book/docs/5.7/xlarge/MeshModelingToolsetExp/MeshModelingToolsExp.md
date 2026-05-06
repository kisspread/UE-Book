# Experimental Mesh Modeling Toolset

> A set of experimental modules implementing 3D mesh creation and editing based on the Interactive Tools Framework

| 属性 | 值 |
|---|---|
| 中文名 | 实验性网格建模工具集 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（工具蓝图资产、编辑器按钮、属性集） |
| 模块 | `GeometryProcessingAdapters` (Runtime), `MeshModelingToolsEditorOnlyExp` (Runtime), `MeshModelingToolsExp` (Runtime), `ModelingEditorUI` (Runtime), `ModelingUI` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-29 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/MeshModelingToolsetExp) | |

---

## 用途

本插件基于 UE5 的 `Interactive Tools Framework` 实现了一系列实验性的 **3D 网格建模与编辑工具**。它扩展了基础的 `MeshModelingTools` 插件，提供了更丰富、用户友好的交互式工具，用于：
- 网格属性烘焙（法线贴图、AO、曲率、位移等）
- 网格对齐与变换（对齐物体、编辑枢轴、烘焙变换）
- 网格切割与布尔运算（平面切割、自交并集）
- 网格复制与转换（转换网格类型、转移网格数据）
- 网格分析与可视化（网格检查器、碰撞几何体分析）
- 基于笔刷的雕刻与选择（顶点刷、选择编辑）
- 基于样条线的建模（从样条生成网格、旋转边界）
- 碰撞几何体生成与编辑（设置、提取、简单碰撞编辑）

这些工具主要集中在 **建模模式 (Modeling Mode)** 的面板中，为美术和设计人员提供可视化、低代码的网格操作方式，同时允许通过属性集精细控制参数。

**为什么存在？** 核心 `MeshModelingTools` 插件提供了基础建模能力，但许多高级或常用的操作（如烘焙、对齐枢轴、碰撞生成）需要额外扩展。本插件将这些功能以独立工具形式提供，降低开发门槛，并支持通过脚本或蓝图自动执行（部分工具）。

---

## 使用场景

- 你需要将高模细节烘焙到低模贴图 → 使用 `BakeTexture` 工具（`UBakeMeshAttributeMapsTool`）
- 你需要将多个物体沿坐标轴对齐 → 使用 `AlignObjects` 工具
- 你需要将网格的变换（旋转/缩放）永久应用到顶点 → 使用 `BakeTransform` 工具
- 你需要从网格边界提取样条线或旋转生成回旋体 → 使用 `RevolveBoundary` / `RevolveSpline` 工具
- 你想要编辑静态网格或动态网格的碰撞几何体 → 使用 `SetCollisionGeometry` / `ExtractCollisionGeometry` 工具
- 在关卡设计时快速放置重复元素 → 使用 `PatternTool` 生成线形/网格/圆形阵列
- 检查网格拓扑错误、UV 接缝、法线方向 → 使用 `MeshInspector` 工具

---

## 蓝图用法

本插件工具在建模模式下通过编辑器 UI 使用，**不提供 BlueprintCallable 节点**（所有交互由编辑界面驱动）。但部分工具的**属性集**可以在蓝图中创建和操作，用于脚本化工作流。

### 可脚本化的属性集类

以下类继承自 `UInteractiveToolPropertySet`，可在蓝图中构造和读写：

| 类 | 说明 |
|---|---|
| `UAddPatchToolProperties` | 平面补丁的参数（宽度、细分、旋转） |
| `UAlignObjectsToolProperties` | 对齐选项（对齐类型、参考、轴） |
| `UBakeMeshAttributeMapsToolProperties` | 烘培贴图参数（输出类型、分辨率、采样数） |
| `UBakeMeshAttributeVertexToolProperties` | 顶点烘培参数（输出模式、通道像素） |
| `UCubeGridToolProperties` | 立方体网格生成参数（网格原点、方向、密度） |
| `UDrawPolyPathProperties` | 绘制路径参数（宽度模式、圆角半径、挤出高度） |
| `UExtractCollisionToolProperties` | 碰撞提取参数（输出类型、合并方式） |
| `USetCollisionGeometryToolProperties` | 碰撞几何体设置参数（几何体类型、精度） |
| `UMirrorToolProperties` | 镜像操作参数（操作模式、裁剪、焊接） |
| `UPatternToolProperties` | 阵列工具参数（形状、间距、旋转） |
| `UPlaneCutToolProperties` | 平面切割参数（保持两半、填充孔洞） |
| `USelfUnionMeshesToolProperties` | 自并集操作参数（修剪折翼、容差） |

### 典型蓝图脚本流程（以烘焙为例）

1. **获取工具管理器** → `Get Editor Interactive Tools Manager`
2. **激活 BakeTexture 工具**（需先选择目标网格）
3. **设置属性**：`BakeOutputTypes` → 勾选 `TangentSpaceNormal`
4. **触发接受** → 自动生成纹理并预览

> 注意：由于工具是编辑器模式下的 `UInteractiveTool`，无法在运行时直接通过蓝图调用。上述流程仅适用于 **Editor Utility Widget** 或 **Editor Scripting**。

---

## C++ 用法

本模块的 C++ API 主要面向需要自定义建模工具或集成到其他系统的高级用户。

### 头文件引入

```cpp
#include "AddPatchTool.h"          // 工具类
#include "AlignObjectsTool.h"      // 对齐工具
#include "BakeMeshAttributeMapsTool.h" // 烘培工具
#include "BakeMeshAttributeVertexTool.h"
#include "EditNormalsTool.h"
#include "MeshInspectorTool.h"
#include "PlaneCutTool.h"
#include "Physics/CollisionPropertySets.h"
#include "Physics/CollisionGeometryVisualization.h"
```

### 基本用法

#### 1. 创建并配置工具

```cpp
// 以 UAddPatchTool 为例
UAddPatchTool* PatchTool = NewObject<UAddPatchTool>();
PatchTool->SetWorld(GetWorld());
PatchTool->Setup();

// 设置平面补丁大小
UAddPatchToolProperties* Props = PatchTool->ShapeSettings;
Props->Width = 100.0f;
Props->Subdivisions = 10;
```

（来源：`Source/MeshModelingToolsExp/Public/AddPatchTool.h`）

#### 2. 通过 Builder 构造工具

```cpp
// 获取工具上下文
FToolBuilderState ToolState;
// ... 填充 SceneState

// 判断是否可以构建
UAddPatchToolBuilder* Builder = NewObject<UAddPatchToolBuilder>();
if (Builder->CanBuildTool(ToolState))
{
    UInteractiveTool* Tool = Builder->BuildTool(ToolState);
    // 使用工具
}
```

（来源：`AddPatchTool.h`）

#### 3. 使用烘培工具

```cpp
// 创建烘培工具
UBakeMeshAttributeMapsTool* BakeTool = NewObject<UBakeMeshAttributeMapsTool>();
BakeTool->Setup();

// 配置输出类型
UBakeMeshAttributeMapsToolProperties* Props = BakeTool->Settings;
Props->MapTypes = static_cast<int32>(EBakeMapType::TangentSpaceNormal | EBakeMapType::AmbientOcclusion);
Props->Resolution = EBakeTextureResolution::Resolution1024;

// 触发计算
BakeTool->OnTick(0.0f); // 实际需要等操作完成后获取结果
```

（来源：`BakeMeshAttributeMapsTool.h`, `BakeMeshAttributeMapsToolBase.h`）

#### 4. 碰撞几何体可视化

```cpp
#include "Physics/CollisionGeometryVisualization.h"
#include "Physics/CollisionPropertySets.h"

UPreviewGeometry* PreviewGeom = NewObject<UPreviewGeometry>();
UCollisionGeometryVisualizationProperties* VisProps = NewObject<UCollisionGeometryVisualizationProperties>();
FPhysicsDataCollection PhysicsData;
// ... 填充 PhysicsData

UE::PhysicsTools::InitializeCollisionGeometryVisualization(
    PreviewGeom,
    VisProps,
    PhysicsData,
    0.0f,  // DepthBias
    16     // 圆步进
);
```

（来源：`Physics/CollisionGeometryVisualization.h`）

#### 5. 编辑属性集

```cpp
// 修改工具属性并触发更新
UAlignObjectsToolProperties* AlignProps = NewObject<UAlignObjectsToolProperties>();
AlignProps->AlignType = EAlignObjectsAlignTypes::Pivots;
AlignProps->bAlignX = true;
AlignProps->bAlignY = true;
AlignProps->bAlignZ = false;
// 然后设置到工具
```

（来源：`AlignObjectsTool.h`）

### 进阶用法

#### 自定义工具继承

```cpp
// 派生自 UMultiSelectionMeshEditingTool
class UMyCustomTool : public UMultiSelectionMeshEditingTool
{
    GENERATED_BODY()
public:
    virtual void Setup() override
    {
        Super::Setup();
        // 添加自定义属性和行为
    }
};
```

#### 与 UGeometrySelection 交互

```cpp
#include "Selections/GeometrySelection.h"

UE::Geometry::FGeometrySelection Selection;
// 填充选择数据
// 然后传递给支持选择的工具，如 UEditNormalsTool
```

（来源：`EditNormalsTool.h`）

---

## Demo 示例

以下是一个完整的 C++ 工具示例，用于沿 X 轴对齐选中的多个网格对象。

### MyAlignTool.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "BaseTools/MultiSelectionMeshEditingTool.h"
#include "InteractiveToolBuilder.h"
#include "AlignObjectsTool.h"   // 复用现有属性集
#include "MyAlignTool.generated.h"

UCLASS()
class UMyAlignToolBuilder : public UMultiSelectionMeshEditingToolBuilder
{
    GENERATED_BODY()
public:
    virtual UMultiSelectionMeshEditingTool* CreateNewTool(const FToolBuilderState& SceneState) const override
    {
        return NewObject<UMyAlignTool>();
    }
protected:
    virtual const FToolTargetTypeRequirements& GetTargetRequirements() const override
    {
        static const FToolTargetTypeRequirements Reqs = {
            UStaticMeshBackedTarget::StaticClass(),
            USkeletalMeshBackedTarget::StaticClass()
        };
        return Reqs;
    }
};

UCLASS()
class UMyAlignTool : public UMultiSelectionMeshEditingTool
{
    GENERATED_BODY()
public:
    virtual void Setup() override
    {
        Super::Setup();
        // 添加对齐属性
        AlignProps = NewObject<UAlignObjectsToolProperties>(this);
        AddToolPropertySource(AlignProps);
        
        // 设置默认值
        AlignProps->bAlignX = true;
        AlignProps->bAlignY = false;
        AlignProps->bAlignZ = false;
    }
    
    virtual void OnPropertyModified(UObject* PropertySet, FProperty* Property) override
    {
        // 每次属性变化时执行对齐
        PerformAlign();
    }
    
    virtual void OnShutdown(EToolShutdownType ShutdownType) override
    {
        // 提交或撤销变换
    }

private:
    UPROPERTY()
    TObjectPtr<UAlignObjectsToolProperties> AlignProps;
    
    void PerformAlign()
    {
        // 遍历所有输入的 Target（见 UMultiSelectionMeshEditingTool）
        // 获取每个 Target 的 Transform，根据设置计算对齐目标位置
        // 应用 TransformChange
    }
};
```

### MyAlignTool.cpp

```cpp
#include "MyAlignTool.h"
#include "ToolTargets/ToolTargetManager.h"
#include "TargetInterfaces/PrimitiveComponentBackedTarget.h"
#include "Components/PrimitiveComponent.h"

void UMyAlignTool::PerformAlign()
{
    FVector AveragePos = FVector::ZeroVector;
    int32 Count = 0;
    for (int32 Idx = 0; Idx < Targets.Num(); ++Idx)
    {
        UPrimitiveComponent* Comp = UE::ToolTarget::GetPrimitiveComponent(Targets[Idx]);
        if (Comp)
        {
            AveragePos += Comp->GetComponentLocation();
            ++Count;
        }
    }
    if (Count == 0) return;
    AveragePos /= Count;
    
    // 对齐每个物体到平均 X 位置
    for (int32 Idx = 0; Idx < Targets.Num(); ++Idx)
    {
        UPrimitiveComponent* Comp = UE::ToolTarget::GetPrimitiveComponent(Targets[Idx]);
        if (Comp)
        {
            FTransform NewTransform = Comp->GetComponentTransform();
            if (AlignProps->bAlignX)
                NewTransform.SetLocation(FVector(AveragePos.X, NewTransform.GetLocation().Y, NewTransform.GetLocation().Z));
            // 类似处理 Y/Z...
        }
    }
}
```

> 注意：实际使用需结合 `UGizmoTransformChange` 或直接修改组件变换（不推荐，无撤销）。此处仅为演示架构。

---

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MeshModelingTools` | 基础建模工具框架（必须依赖） |
| `GeometryAlgos` | 网格算法（布尔运算、法线计算） |
| `DynamicMesh` | UE::Geometry 动态网格核心 |
| `InteractiveToolsFramework` | 交互工具框架基类 |
| `ModelingOperators` | 网格操作算子（背景计算） |
| `MeshDescription` | 编辑网格描述（与资产转换） |
| `PhysicsCore` | 碰撞几何体数据结构 |
| `Chaos` | 物理引擎对接 |

其他依赖（省略常见）：无特殊依赖（仅标准 Engine/Slate 等）

---

## 维护状态

### 近期更新

- 2025-12-18 `79bdb336` #jira UE-356302（修复/优化）
- 2025-11-18 `e352ab23` 修复将多个动态网格源转换为静态网格时的崩溃（建模模式转换工具）
- 2025-10-03 `fea318f1` PR #13360：为立方体网格工具添加分配和开始新命令的键盘快捷键
- 2025-10-03 `53d4840d` 建模工具：修复立方体网格的“接受并开始新”操作在编辑现有物体时无法正常工作的问题
- 2025-09-29 `300d2503` 合并 Actor - 近似：使用正确的合并材质，避免显示默认引擎纹理

### 维护评价

- **创建时间**：2025-09-29（约 3 个月前）
- **活跃度**：**活跃维护**。从 9 月至今每月均有功能性更新（修复、新特性、快捷键添加），且伴随有 PR 合并。
- **已知限制**：实验性插件，API 可能变化；部分工具（如 `BakeMultiMesh`）仍在完善中；依赖 `MeshModelingTools` 基础版本。
- **推荐度**：✅ **强烈推荐**。对于需要高级建模功能和自动化场景的美术/开发者，此插件是“建模模式”的核心扩展，功能丰富且持续更新。启用前请确保引擎版本为 UE5.5+。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/MeshModelingToolsetExp)
- [官方文档（基础建模模式）](https://docs.unrealengine.com/5.7/en-US/modeling-mode-overview/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/MeshModelingToolsetExp/Tests/)（若存在）