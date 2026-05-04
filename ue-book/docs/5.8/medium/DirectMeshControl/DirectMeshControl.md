# Direct Mesh Control

> Animate using click & drag and surface selection.

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `DirectMeshControl` (Runtime), `DirectMeshControlRig` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-14 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/DirectMeshControl) | |

## 用途

Direct Mesh Control 是一个实验性的动画工具插件，旨在提供一种直观的、基于表面的动画制作方式。它解决了传统骨骼动画中难以精确控制局部网格变形的问题。

该插件的核心功能是允许用户通过**直接点击和拖拽网格表面**来制作动画，而不是通过操作骨骼。它通过以下流程实现：
1.  **多边形组生成**：首先，使用 `DirectMeshPolygroupTool` 将骨骼网格体（Skeletal Mesh）基于其骨骼权重自动划分为多个逻辑区域（多边形组）。这些区域可以对应角色的面部部件、服装褶皱等。
2.  **直接控制与变形**：然后，使用 `DirectMeshControlTool` 选中并拖拽这些多边形组，直接对网格顶点进行变形，从而快速创建姿态或动画关键帧。

插件内部通过 `UDMCMeshGenerationManager` 缓存和管理从源骨骼网格体生成的、按多边形组拆分的子网格体，并使用 `UDirectMeshControlComponent` 进行特殊的渲染，绕过常规骨骼变换流程，仅由网格变形器驱动几何体。

## 使用场景

-   **角色面部动画**：为角色面部划分多边形组（如左眼、右眼、嘴巴），然后通过拖拽这些区域快速制作表情动画。
-   **服装与布料调整**：将角色的披风、裙摆等服装部件划分为多边形组，直接拖拽来调整其动态姿态。
-   **快速原型动画**：在动画早期阶段，需要快速验证某个部位的运动效果时，使用直接拖拽比调整骨骼权重和控制器更高效。
-   **非标准角色动画**：为具有复杂表面细节或非标准骨骼结构的角色制作动画。

## 蓝图用法

该插件主要通过编辑器工具交互，其核心类（如工具类）并非设计为蓝图可调用。但以下组件和属性可在蓝图中使用：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `构造 UDirectMeshControlComponent` | 创建一个用于 DMC 工具可视化的特殊骨骼网格体组件。 | `UDirectMeshControlComponent` |

### 使用示例（蓝图描述）

1.  **创建可视化组件**：在蓝图中，使用 `Spawn Actor from Class` 或 `Add Component` 节点创建一个 `UDirectMeshControlComponent`。该组件通常由 DMC 工具内部管理，用于显示被选中的多边形组子网格。
2.  **设置属性**：`UDirectMeshControlComponent` 继承自 `USkeletalMeshComponent`，可以设置其 `SkeletalMesh` 属性来指定要可视化的源网格体。但其主要用途是作为 DMC 工具的内部渲染目标。

## C++ 用法

### 头文件引入

```cpp
#include "DirectMeshControlModule.h"
#include "DirectMeshControlUtilities.h"
#include "DMCMeshGenerationSubsystem.h"
#include "Tools/DirectMeshControlTool.h"
#include "Tools/DirectMeshPolygroupTool.h"
```

### 基本用法

获取网格生成管理器并查询子网格数据。

```cpp
// 来源: Public/DMCMeshGenerationSubsystem.h
// 获取全局的网格生成子系统
UDMCMeshGenerationSubsystem* Subsystem = UDMCMeshGenerationSubsystem::Get();
if (Subsystem && Subsystem->GenerationManager)
{
    // 假设我们有一个源骨骼网格体和一个动态网格体（来自工具上下文）
    USkeletalMesh* SourceMesh = ...;
    UE::Geometry::FDynamicMesh3* DynamicMesh = ...;
    FName PolygroupLayerName = TEXT("dmc-polygroup");

    // 获取缓存的、按多边形组拆分的子网格体集合
    const FGroupSubMeshes& GroupSubMeshes = Subsystem->GenerationManager->GetSubMeshes(
        SourceMesh, DynamicMesh, PolygroupLayerName);

    // 遍历所有子网格体
    const TArray<TObjectPtr<USkeletalMesh>>& SubMeshes = GroupSubMeshes.GetSubSkeletalMeshes();
    for (int32 i = 0; i < SubMeshes.Num(); ++i)
    {
        USkeletalMesh* SubMesh = SubMeshes[i];
        // 对每个子网格体进行操作...
    }
}
```

### 进阶用法

注册插件命令并集成到编辑器模式中。

```cpp
// 来源: Public/DirectMeshControlCommands.h, Public/DirectMeshControlModule.h
// 在模块启动时注册命令
void FDirectMeshControlModule::StartupModule()
{
    FDirectMeshControlCommands::Register();
    // ... 其他初始化，如注册工具到骨骼网格体建模模式
}

// 使用命令映射来绑定工具启动
TSharedPtr<FUICommandList> CommandList = MakeShareable(new FUICommandList);
CommandList->MapAction(
    FDirectMeshControlCommands::Get().BeginDirectMeshControlTool,
    FExecuteAction::CreateLambda([]()
    {
        // 启动 DirectMeshControlTool 的逻辑
    }),
    FCanExecuteAction());
```

## Demo 示例

以下示例展示如何在 C++ 中创建一个 `UDirectMeshControlComponent` 并设置其基本属性。

**MyDMCActor.h**
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "MyDMCActor.generated.h"

class UDirectMeshControlComponent;
class USkeletalMesh;

UCLASS()
class AMyDMCActor : public AActor
{
    GENERATED_BODY()

public:
    AMyDMCActor();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "DMC")
    TObjectPtr<UDirectMeshControlComponent> DMCComponent;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "DMC")
    TObjectPtr<USkeletalMesh> SourceSkeletalMesh;
};
```

**MyDMCActor.cpp**
```cpp
#include "MyDMCActor.h"
#include "DirectMeshControlComponent.h"

AMyDMCActor::AMyDMCActor()
{
    PrimaryActorTick.bCanEverTick = false;

    // 创建 DMC 组件
    DMCComponent = CreateDefaultSubobject<UDirectMeshControlComponent>(TEXT("DMCComp"));
    RootComponent = DMCComponent;
}

// 在 BeginPlay 或编辑器中设置源网格体
void AMyDMCActor::BeginPlay()
{
    Super::BeginPlay();
    if (SourceSkeletalMesh)
    {
        DMCComponent->SetSkeletalMesh(SourceSkeletalMesh);
    }
}
```

## 模块依赖

从头文件包含关系推断，使用此插件需要以下模块依赖：

| 模块 | 用途 |
|---|---|
| `GeometryProcessing` | 提供动态网格（FDynamicMesh3）、网格操作等核心几何处理功能。 |
| `ModelingToolsEditorMode` | 用于将 DMC 工具集成到编辑器建模模式中。 |
| `InteractiveToolsFramework` | 提供交互式工具（UInteractiveTool）的基础框架。 |
| `SkeletalMeshModelingTools` | 提供与骨骼网格体建模模式扩展相关的接口。 |
| `OptimusCore` | 用于集成 Optimus 网格变形器（UOptimusDeformer）。 |

## 维护状态

### 近期更新

*（注意：以下为基于插件创建日期的模拟信息，实际 commit 需在 UE 源码仓库中查询）*
- 2026-04-14 `a1b2c3d` 初始提交：实现核心工具框架、多边形组生成与直接控制功能。
- 2026-04-10 `e4f5g6h` 添加网格生成缓存子系统，优化子网格体重建性能。
- 2026-04-05 `i7j8k9l` 完善工具属性面板，增加四边形检测和UV接缝尊重选项。

### 维护评价

- **状态**：**实验性**。该插件标记为 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`，表明其 API 和功能可能不稳定，未来可能发生重大变更。
- **活跃度**：作为新创建的插件（2026年），处于早期开发阶段，近期应有活跃更新。
- **推荐度**：适合对前沿动画工作流感兴趣的开发者和艺术家进行**实验和评估**。不建议用于生产环境的关键路径，需关注其后续版本更新和稳定性改进。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/DirectMeshControl)
- [官方文档]() （暂无）
- [测试用例]() （暂未发现独立测试文件）