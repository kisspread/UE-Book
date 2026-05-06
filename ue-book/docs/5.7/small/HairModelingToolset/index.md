# Hair Modeling Toolset

> Adds a set of tools for Groom/Hair Modeling to Modeling Tools Mode

| 属性 | 值 |
|---|---|
| 中文名 | 毛发建模工具集 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（UI 样式资源） |
| 模块 | `HairModelingToolset` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-11-15 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/HairModelingToolset) | |

---

## 用途

该插件为 **建模模式 (Modeling Mode)** 添加一组专门用于毛发（Groom / Hair）的中级建模工具。它并不直接编辑毛发本身体积或曲线，而是允许用户对毛发生成的几何体（如 Hair Cards、Hair Meshes）进行网格级别的操作，包括：

- 将 Groom 资产转换为静态网格（Mesh）；
- 为生成的网格生成多级 LOD；
- 编辑 Hair Cards（头发卡片）的拓扑和形状。

插件基于 UE 的 **建模模式框架** (Modeling Mode/Tools)，所有工具直接在编辑器视口内通过 `Modeling Mode` 的面板访问，无需编写代码。

---

## 使用场景

- **将毛发系统转换为可编辑网格**  
  当你需要把 Groom 生成的 Hair Cards 烘焙为静态网格，以便进行后续雕刻、材质调整或导出到其他 DCC 工具。

- **优化毛发几何复杂度**  
  通过简化工具为毛发网格生成不同的 LOD 级别，提高渲染性能，同时保持视觉质量。

- **手动修正 Hair Cards 布局**  
  当自动生成的 Hair Cards 位置不理想时，使用卡片编辑工具直接移动、旋转、删除或填充卡片。

---

## 蓝图用法

该插件的工具仅通过建模模式界面操作，**不暴露蓝图可调用的函数或事件**。所有属性以 `EditAnywhere` 形式在编辑器细节面板中修改，无需蓝图。

如果需要从蓝图启动建模工具，可参考建模模式框架的 API（如 `UModelingToolsManager`），但这不是本插件的直接接口。

---

## C++ 用法

### 头文件引入

```cpp
#include "HairModelingToolsetModule.h"
#include "GroomToMeshTool.h"
#include "GenerateLODMeshesTool.h"
#include "GroomCardsEditorTool.h"
#include "GroomQueryUtil.h"   // 用于工具内部的卡片提取辅助函数
```

### 基本用法

主要通过建模模式框架自动注册工具，无需手动实例化。若需要在 C++ 中调用该插件内部的功能（例如从 Groom 提取卡片网格），可使用 `UE::GroomQueries` 命名空间的辅助函数。

**示例：从 GroomActor 提取所有 Hair Cards 并转换为动态网格**

```cpp
// Source/HairModelingToolset/Private/GroomQueryUtil.h
// 函数：UE::GroomQueries::ExtractAllHairCards

AActor* SelectedActor = ...; // 需要转换为 AGroomActor
AGroomActor* GroomActor = Cast<AGroomActor>(SelectedActor);
if (GroomActor)
{
    int32 LODIndex = 0; // 使用 LOD0
    UE::Geometry::FDynamicMesh3 Mesh;
    UE::GroomQueries::FMeshCardStripSet CardInfo;
    UE::GroomQueries::ExtractAllHairCards(GroomActor, LODIndex, Mesh, &CardInfo);

    // 此后可将 Mesh 赋值给其他组件或进一步处理
}
```

**示例：注册自定义工具**（在模块启动时）

```cpp
// 在 StartupModule 中通过建模模式扩展接口注册工具
void FHairModelingToolsetModule::StartupModule()
{
    // 工具会自动通过 GetExtensionTools 注册
    // 无需手动调用注册函数
}
```

### 进阶用法

可通过 `UGeometryProcessingLibrary` 等通用 API 组合使用本插件的核心算法（如简化、网格生成），但这些算法并非本插件独有，而是依赖建模工具集底层。如需在代码中创建工具实例，可参考以下模式：

```cpp
// 工具由建模模式管理，通常不直接创建
// 若需要以编程方式触发工具，可使用 UIModelingModeSubsystem
UIModelingModeSubsystem* ModelingSubsystem = GEditor->GetEditorSubsystem<UIModelingModeSubsystem>();
ModelingSubsystem->ActivateTool(UGroomToMeshTool::StaticClass()->GetFName());
```

但请注意，`ActivateTool` 要求当前处于建模模式，且参数需与已注册的工具名匹配。

---

## Demo 示例

以下示例演示如何通过 C++ 从 `AGroomActor` 提取 Hair Cards 并生成静态网格资产。该代码可用于编辑器工具蓝图或自定义脚本。

**Header (`MyHairExporter.h`)**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GroomActor.h"
#include "DynamicMesh/DynamicMesh3.h"

class FMyHairExporter
{
public:
    static bool ExportGroomToMesh(AGroomActor* GroomActor, int32 LODIndex, UE::Geometry::FDynamicMesh3& OutMesh);
};
```

**Implementation (`MyHairExporter.cpp`)**

```cpp
#include "MyHairExporter.h"
#include "GroomQueryUtil.h"
#include "DynamicMesh/DynamicMeshAABBTree3.h"
#include "Async/Async.h"

bool FMyHairExporter::ExportGroomToMesh(AGroomActor* GroomActor, int32 LODIndex, UE::Geometry::FDynamicMesh3& OutMesh)
{
    if (!GroomActor || !GroomActor->GetGroomComponent())
    {
        return false;
    }

    // 使用插件内部的卡片提取函数
    UE::GroomQueries::ExtractAllHairCards(GroomActor, LODIndex, OutMesh, nullptr);
    return OutMesh.TriangleCount() > 0;
}
```

在编辑器蓝图或自定义工具中调用：

```cpp
AGroomActor* MyGroom = /* 获取场景中的 Groom Actor */;
UE::Geometry::FDynamicMesh3 Mesh;
if (FMyHairExporter::ExportGroomToMesh(MyGroom, 0, Mesh))
{
    // 可将 Mesh 保存为 StaticMesh 资产（此处省略具体保存逻辑）
}
```

---

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ModelingComponents` | 提供单选/表面点编辑工具基类、预览网格等 |
| `ModelingOperators` | 提供简化、重网格等操作算子（如 `FSimplifyMeshOp`） |
| `GeometryFramework` | 动态网格 (`FDynamicMesh3`, `FDynamicMeshAABBTree3`) |
| `Groom` | 毛发资产、组件、Actor 类型 |
| `MeshDescription` | 支持网格描述与转换 |

无特殊依赖（仅标准 Core/Engine/Slate 等）。

---

## 维护状态

### 近期更新

- 2025-06-03 `e5e94e83` Add support for custom/additional UV channels for hair cards/hair meshes.
- 2024-12-20 `d0cf4301` ModelingTools: Promote experimental modeling tools to beta. (后撤销)
- 2024-12-19 `0b7db795` [Backout] - CL38936187
- 2024-12-19 `4581f566` ModelingTools: Promote experimental modeling tools to beta.
- 2024-11-15 `a2c3875d` Cleanup of FSlateFontInfo constructor across the solution that uses font paths.

### 维护评价

- **创建时间**：2024-11-15，至今约 11 个月（仍在实验阶段）。
- **更新频率**：近 6 个月内有一次功能性更新（UV 通道支持），之前有 promote to beta 尝试但被回退，社区可见活跃开发。
- **活跃度**：维护活跃，团队持续迭代。
- **已知问题**：插件处于实验状态，API 和路径可能在未来版本发生变化；部分工具仍需从场景中选择特定 Actor 才能启用。
- **推荐程度**：✅ 推荐使用，尤其适合需要在建模管线中处理毛发的开发者。建议关注后续 beta/promote 状态。

---

## 相关链接

- [源码（主目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/HairModelingToolset)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/modeling-mode-in-unreal-engine/)（建模模式通用文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/HairModelingToolset/Tests)（可能不存在，此处仅为占位）