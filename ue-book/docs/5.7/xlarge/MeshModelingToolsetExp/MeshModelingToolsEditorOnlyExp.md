# Experimental Mesh Modeling Toolset

> A set of experimental modules implementing 3D mesh creation and editing based on the Interactive Tools Framework

| 属性 | 值 |
|---|---|
| 中文名 | 实验性网格建模工具集 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器工具） |
| 模块 | `MeshModelingToolsEditorOnlyExp` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-29 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MeshModelingToolsetExp) | |

## 用途

`MeshModelingToolsEditorOnlyExp` 是实验性网格建模工具集中的编辑器专用子模块。它提供了一系列用于在编辑器中操作、转换和优化网格几何体的工具，包括：

- **BSP 转换**：将 BSP 几何体转换为静态网格体，支持多种合并策略
- **渲染捕获烘焙**：从场景捕捉光照信息（如法线、粗糙度、金属度等）并烘焙为目标纹理
- **网格切线计算**：计算并可视化网格切线与法线，支持 MikkTSpace 等算法
- **网格转体积**：将静态网格体转换为虚幻引擎的 AVolume 轮廓，适用于碰撞或关卡边界
- **实例化管理**：合并重复静态网格体为 Instanced Static Mesh Component（HISM/ISM），减少绘制调用
- **子分曲面**：对多边形网格进行 Catmull-Clark、Loop 等子分算法
- **枢轴点编辑**：为选中 actors 创建/调整枢轴 actor
- **样条绘制**：通过点击/拖拽在场景中绘制样条并生成直接或蓝图的 spline component
- **材质编辑**：通过面选择快速分配材质
- **形状喷溅**：类似画笔工具，在表面随机放置小 mesh
- **体素布尔运算**：基于体素的差集、并集、交集操作

此模块显著扩展了内置“建模模式”（Modeling Mode）的能力，是完成复杂几何编辑任务的基础工具集。

## 使用场景

**适用对象**：关卡设计师、技术美术、环境美术师、游戏原型开发人员

- 将 BSP 关卡快速转换为静态网格体，以获得更好的性能与灵活性
- 从高模场景烘焙贴图到低模，用于游戏资产
- 为静态网格体校正切线，消除光照异常
- 将任意网格体转换为碰撞体积（如 BlockingVolume）
- 合并大量重复静态网格体实例，大幅降低 Draw Calls
- 对低多边形模型进行子分，获得光滑曲面
- 创建自定义枢轴点，便于动画或程序化放置
- 在关卡中临时绘制样条路径，用于放置或编辑

## 蓝图用法

该模块的所有工具均通过蓝图/C++ 的 `InteractiveToolsFramework` 激活，**不提供独立的蓝图函数节点**。不过，部分工具（如 `UBakeRenderCaptureTool`）的结果可通过蓝图访问（例如纹理属性）。以下列出可通过蓝图属性访问的关键数据：

### 核心属性（蓝图可读）

| 属性 | 说明 | 所在类 |
|---|---|---|
| `BaseColorMap` | 烘焙输出的基础颜色纹理 | `UBakeRenderCaptureResults` |
| `NormalMap` | 法线贴图纹理 | `UBakeRenderCaptureResults` |
| `PackedMRSMap` | 打包的金属度/粗糙度/高光贴图 | `UBakeRenderCaptureResults` |
| `EmissiveMap` | 自发光贴图 | `UBakeRenderCaptureResults` |
| `OpacityMap` | 不透明度贴图 | `UBakeRenderCaptureResults` |
| `SubsurfaceColorMap` | 次表面颜色贴图 | `UBakeRenderCaptureResults` |

### 使用示例（蓝图描述）

无需蓝图节点，工具操作在编辑器中通过“建模模式”（Modeling Mode）面板完成。如需在运行时访问烘焙结果，请使用 C++ 或通过蓝图直接引用生成的 UTexture2D 资产。

## C++ 用法

### 头文件引入

```cpp
#include "MeshModelingToolsEditorOnlyExp.h"          // 模块声明
#include "BakeRenderCaptureTool.h"                   // 烘焙工具
#include "BspConversionTool.h"                       // BSP转换工具
#include "MeshTangentsTool.h"                        // 切线工具
#include "MeshToVolumeTool.h"                        // 网格转体积工具
#include "HarvestInstancesTool.h"                    // 实例化工具
#include "SubdividePolyTool.h"                       // 子分工具
#include "AddPivotActorTool.h"                       // 枢轴工具
#include "DrawSplineTool.h"                          // 样条绘制工具
#include "EditMeshMaterialsTool.h"                   // 材质编辑工具
#include "ShapeSprayTool.h"                          // 形状喷溅
#include "VoxelCSGMeshesTool.h"                      // 体素布尔
```

### 基本用法

该模块的工具通过 `UInteractiveToolManager` 激活。以下示例展示如何在编辑器模式下启动一个网格切线工具：

```cpp
// 从场景选中一个静态网格体 actor 开始
void UMyTool::StartMeshTangents()
{
    // 获取工具管理器
    UInteractiveToolManager* ToolManager = GetToolManager();
    if (!ToolManager) return;

    // 构建工具
    const FToolBuilderState State = /* ... 获取当前状态 */;
    UMeshTangentsToolBuilder* Builder = NewObject<UMeshTangentsToolBuilder>();
    if (Builder->CanBuildTool(State))
    {
        UMeshTangentsTool* Tool = Cast<UMeshTangentsTool>(Builder->BuildTool(State));
        if (Tool)
        {
            ToolManager->ActivateTool(EToolSide::Left, Builder, &State);
        }
    }
}
```

> **注意**：实际使用中应遵循 InteractiveToolsFramework 的生命周期管理，在 `UEdMode`、`UInteractiveTool` 内部或自定义模式中调用。

### 进阶用法

以下示例组合多个工具完成“BSP 转静态网格体并烘焙”：

```cpp
// 1. 使用 BspConversionTool 将 BSP 转换为静态网格体
UBspConversionTool* ConvertTool = ...;
// 设置属性
ConvertTool->Properties->ConversionMode = EBspConversionMode::ConvertFirst;
ConvertTool->Properties->bIncludeVolumes = false;
// 执行转换（模拟 Accept）
ConvertTool->OnShutdown(EToolShutdownType::Accept);

// 2. 对新生成的静态网格体使用 BakeRenderCaptureTool 进行光照烘焙
UBakeRenderCaptureTool* BakeTool = ...;
BakeTool->SetTargetMesh(NewStaticMesh);
BakeTool->Setup();
// 运行烘焙操作
BakeTool->OnTick(0.0f);
BakeTool->OnShutdown(EToolShutdownType::Accept);
// 获取结果纹理
UTexture2D* NormalMap = BakeTool->BakeRenderCaptureResults->NormalMap;
```

> **注意**：以上代码仅为概念演示，实际运行时需要正确处理工具激活、输入输出以及撤销系统。

## Demo 示例

以下是一个最小化的编辑器模式示例，注册并启动 `UMeshTangentsTool`：

**MyTangentsMode.h**
```cpp
#pragma once
#include "EdMode.h"
#include "MeshTangentsTool.h"

class FMyTangentsMode : public FEdMode
{
public:
    virtual void Enter() override;
    virtual void Exit() override;
};
```

**MyTangentsMode.cpp**
```cpp
#include "MyTangentsMode.h"
#include "InteractiveToolManager.h"

void FMyTangentsMode::Enter()
{
    FEdMode::Enter();

    // 获取工具管理器并构建工具
    UInteractiveToolManager* ToolManager = GetToolManager();
    if (!ToolManager) return;

    // 这里假设已拥有有效的 FToolBuilderState
    FToolBuilderState BuilderState = GetToolManager()->GetCurrentToolBuilderState();
    UMeshTangentsToolBuilder* Builder = NewObject<UMeshTangentsToolBuilder>();
    if (Builder->CanBuildTool(BuilderState))
    {
        ToolManager->SelectActiveToolType(EToolSide::Left, Builder->GetClass());
        ToolManager->ActivateTool(EToolSide::Left);
    }
}

void FMyTangentsMode::Exit()
{
    FEdMode::Exit();
}
```

**编译配置**：在模块的 `Build.cs` 中添加依赖（见下一节），并确保模块类型为 `Editor` 或 `Runtime`（此模块为 Runtime，但实际仅在编辑器可用）。

## 模块依赖

以下为使用此模块（`MeshModelingToolsEditorOnlyExp`）时其他模块需要添加的依赖。**省略常见依赖**（Core, Engine, Slate等），仅列出非标准项：

| 模块 | 用途 |
|---|---|
| `InteractiveToolsFramework` | 工具框架基础，所有工具均依赖此模块 |
| `ModelingOperators` | 提供体素布尔、子分等几何操作算子 |
| `GeometryFramework` | 动态网格体（DynamicMesh）支持 |
| `MeshDescription` | 网格描述数据结构 |
| `ModelingComponents` | 建模模式通用组件与属性集 |
| `PropertyEditor` | 属性面板显示 |
| `UnrealEd` | 编辑器相关功能（BSP、体积等） |
| `BSPConversion` | BSP 转换内部模块（隐式依赖） |
| `RenderCapture` | 场景捕获与烘焙 |
| `SplineComponent` | 样条组件支持 |

**注意**：实际依赖可能因使用特定工具而异，建议在模块 `Build.cs` 的 `PrivateDependencyModuleNames` 中添加上述模块。

## 维护状态

### 近期更新

从插件根目录的 git 历史（截至 2025-12-18）：
- 2025-12-18 `79bdb336` — JIRA UE-356302（修复或功能更新）
- 2025-11-18 `e352ab23` — 修复将多个动态网格源转换为静态网格时的崩溃（建模模式转换工具）
- 2025-10-03 `53d4840d` — ModelingTools: 修复 CubeGrid “Accept and Start New” 在编辑现有物体时行为错误
- 2025-10-03 `fea318f1` — PR #13360: 为 CubeGrid 添加 “Assign and Start New” 键盘命令
- 2025-09-29 `300d2503` — Merge Actor - Approximate: 使用正确的合并材质，避免显示默认引擎纹理

### 维护评价

- **创建时间**：2025-09-29，约 3 个月前
- **更新频率**：月均 1-2 次实质性更新，包含功能新增、问题修复、性能优化
- **维护状态**：活跃维护，作者（Epic Games）持续投入
- **已知限制**：作为实验性插件，API 可能变动；部分工具（如 BspConversionTool）暂不支持运行时使用
- **推荐使用**：✅ 推荐用于编辑器下的建模工作流，但在正式项目中使用时需留意实验性标记的风险

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MeshModelingToolsetExp)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MeshModelingToolsetExp/Tests)（按需查看各工具的自动化测试）