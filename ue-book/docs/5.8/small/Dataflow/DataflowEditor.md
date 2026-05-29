# Editor DataflowGraph

> Editor Dataflow Graph

| 属性 | 值 |
|---|---|
| 中文名 | 数据流图编辑器 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（编辑器资产、材质模板、图标资源） |
| 模块 | `DataflowEditor` (Editor), `DataflowEnginePlugin` (Runtime), `DataflowNodes` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2026-04-23 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Dataflow) | |

## 用途

**Editor DataflowGraph** 是一个基于节点图的编辑器框架，用于创建、编辑和评估**数据流图**（Dataflow Graph）。它提供了一个可视化的编程环境，允许用户通过连接节点来定义数据处理管线，支持几何运算、物理模拟、属性转换等任务。该插件是 UE 内部数据处理工具（如 Chaos 物理、几何集合编辑器、布料编辑器等）的核心基础设施。

该插件解决以下问题：
- 将复杂的数据处理逻辑（如几何体变换、碰撞生成、网格细分）抽象为可组合的节点图，避免编写大量 C++ 代码。
- 提供实时反馈的编辑器面板（构建视图、模拟视图、选择视图、集合电子表格等），帮助用户调试和可视化数据流。
- 支持通过蓝图或 C++ 扩展新节点，实现自定义数据处理逻辑。

## 使用场景

- **程序化几何建模**：用节点图定义几何体生成流程（例如从基本形状叠加编码生成复杂网格）。
- **物理模拟控制**：在布料或毛发模拟中，用数据流图定义模拟参数、碰撞行为、骨骼蒙皮等。
- **工具集成**：自定义编辑器工具（如网格变形、自动 UV 生成、材质分配），通过数据流图提供可配置的管线。
- **数据可视化与调试**：借助集合电子表格、选择视图等面板，实时查看节点输出数据（如顶点位置、面法线、骨骼权重）。

## 蓝图用法

数据流图编辑器暴露了一组蓝图函数，用于在运行时或编辑器脚本中动态构建和修改数据流图。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddDataflowNode` | 在数据流图中添加指定类型的节点，返回节点名称 | `UDataflowEditorBlueprintLibrary` |
| `ConnectDataflowNodes` | 连接两个节点的引脚（输出 → 输入） | `UDataflowEditorBlueprintLibrary` |
| `AddDataflowFromClipboardContent` | 从剪贴板字符串（JSON 格式的节点图）导入数据流图 | `UDataflowEditorBlueprintLibrary` |
| `SetDataflowNodeProperty` | 设置数据流节点上的属性值（属性名为 FName，值为字符串） | `UDataflowEditorBlueprintLibrary` |

### 使用示例（蓝图）

1. **创建并连接两个节点**
   - 调用 `AddDataflowNode` 添加 "MyNodeType" 节点，基名 "NewNode"，位置 (0,0) → 得到节点名。
   - 调用 `AddDataflowNode` 添加另一个节点 → 得到第二个节点名。
   - 调用 `ConnectDataflowNodes`，填入第一个节点名、输出引脚名、第二个节点名、输入引脚名。若成功返回 true。

2. **从外部 JSON 加载数据流**
   - 调用 `AddDataflowFromClipboardContent`，传入 UDataflow 对象和包含节点图定义的字符串（JSON 格式），以及放置位置。返回 true 表示成功。

## C++ 用法

### 头文件引入

```cpp
#include "Dataflow/DataflowToolTarget.h"
#include "Dataflow/DataflowComponentToolTarget.h"
#include "Dataflow/DataflowObject.h"
#include "Dataflow/DataflowNodeFactory.h"   // 注册自定义节点
```

### 基本用法：通过工具目标获取数据流网格

以下示例演示如何从 `UDataflowToolTarget` 获取动态网格，此代码常用于编辑器工具（如建模工具）中。

```cpp
// 文件来源：Engine/Plugins/Dataflow/Source/DataflowEditor/Private/Dataflow/DataflowToolTarget.cpp

// 假设已有一个 UDataflow* Dataflow 和关联的 UObject* Asset
TUniquePtr<FMeshDescription> MeshDesc = MakeUnique<FMeshDescription>();

// 创建工具目标
UDataflowReadOnlyToolTarget* ToolTarget = NewObject<UDataflowReadOnlyToolTarget>();
ToolTarget->Dataflow = Dataflow;
ToolTarget->Asset = Asset;
// 初始化上下文（通常由编辑器模式管理）
ToolTarget->Context = UE::Dataflow::FEngineContext::Create(Dataflow, Asset);

// 获取网格描述
const FMeshDescription* OutMeshDesc = ToolTarget->GetMeshDescription();
if (OutMeshDesc)
{
    // 处理网格数据 ...
}
```

### 进阶用法：创建自定义数据流节点

通过继承 `FDataflowNode` 和注册到 `FDataflowNodeFactory` 来扩展数据流节点。

```cpp
// 文件来源：Engine/Plugins/Dataflow/Source/DataflowNodes/Private/DataflowMyCustomNode.cpp

#include "Dataflow/DataflowNode.h"
#include "Dataflow/DataflowNodeFactory.h"

struct FMyCustomNode : public FDataflowNode
{
    // 输入
    int32 InputValue;
    // 输出
    int32 OutputValue;

    FMyCustomNode(const Dataflow::FNodeParameters& Param)
        : FDataflowNode(Param)
    {
        RegisterInputConnection(&InputValue, GET_MEMBER_NAME_CHECKED(FMyCustomNode, InputValue));
        RegisterOutputConnection(&OutputValue, GET_MEMBER_NAME_CHECKED(FMyCustomNode, OutputValue));
    }

    virtual void Evaluate(UE::Dataflow::FContext& Context) const override
    {
        // 执行逻辑
        const int32 In = Context.EvaluateValue(InputValue);
        Context.SetValue(OutputValue, In * 2);
    }
};

// 在模块启动时注册
void FMyModule::StartupModule()
{
    FDataflowNodeFactory::Get().RegisterNodeType(TEXT("MyCustomNode"), [](const Dataflow::FNodeParameters& Param)
    {
        return MakeShared<FMyCustomNode>(Param);
    });
}
```

## Demo 示例

以下是一个最小化的编辑器工具，它通过 `UDataflowToolTarget` 获取 Dataflow 中的网格并在场景中显示。

### MyDataflowTool.h
```cpp
#pragma once

#include "CoreMinimal.h"
#include "InteractiveTool.h"
#include "InteractiveToolBuilder.h"
#include "MyDataflowTool.generated.h"

UCLASS()
class UMyDataflowToolBuilder : public UInteractiveToolBuilder
{
    GENERATED_BODY()
public:
    virtual bool CanBuildTool(const FToolBuilderState& SceneState) const override;
    virtual UInteractiveTool* BuildTool(const FToolBuilderState& SceneState) const override;
};

UCLASS()
class UMyDataflowTool : public UInteractiveTool
{
    GENERATED_BODY()
public:
    virtual void Setup() override;
    virtual void Shutdown(EToolShutdownType ShutdownType) override;
    virtual void Render(IToolsContextRenderAPI* RenderAPI) override;
    
    // 输入数据流
    UPROPERTY()
    TObjectPtr<UDataflow> Dataflow;
};
```

### MyDataflowTool.cpp
```cpp
#include "MyDataflowTool.h"
#include "Dataflow/DataflowToolTarget.h"
#include "InteractiveToolManager.h"
#include "ToolTargets/ToolTarget.h"

bool UMyDataflowToolBuilder::CanBuildTool(const FToolBuilderState& SceneState) const
{
    return true;
}

UInteractiveTool* UMyDataflowToolBuilder::BuildTool(const FToolBuilderState& SceneState) const
{
    UMyDataflowTool* Tool = NewObject<UMyDataflowTool>();
    Tool->Dataflow = Cast<UDataflow>(SceneState.SelectedObjects[0]); // 选中一个 Dataflow 资产
    return Tool;
}

void UMyDataflowTool::Setup()
{
    // 创建工具目标
    UDataflowReadOnlyToolTarget* ToolTarget = NewObject<UDataflowReadOnlyToolTarget>();
    ToolTarget->Dataflow = Dataflow;
    ToolTarget->Asset = Dataflow; // 假设 Dataflow 本身就是资产
    ToolTarget->Context = UE::Dataflow::FEngineContext::Create(Dataflow, nullptr);
    
    const FMeshDescription* Mesh = ToolTarget->GetMeshDescription();
    if (Mesh)
    {
        // 使用 Mesh 数据生成动态网格组件等...
        UE_LOG(LogTemp, Log, TEXT("Got mesh with %d vertices"), Mesh->Vertices().Num());
    }
}

void UMyDataflowTool::Shutdown(EToolShutdownType ShutdownType)
{
    // 清理
}

void UMyDataflowTool::Render(IToolsContextRenderAPI* RenderAPI)
{
    // 渲染调试信息
}
```

**提示**：此工具需要依赖 `InteractiveToolsFramework` 和 `DataflowEditor` 模块。在 `Build.cs` 中添加 `PublicDependencyModuleNames.AddRange(new string[] { "InteractiveToolsFramework", "DataflowEditor" });`。

## 模块依赖

DataflowEditor 模块依赖于以下独特模块（省略标准 Core/Engine/Slate 等）：

| 模块 | 用途 |
|---|---|
| `DataflowEnginePlugin` | 提供核心数据流执行引擎、节点注册、上下文评估 |
| `DataflowNodes` | 提供预定义的通用数据流节点（如数学运算、几何操作） |
| `GeometryCollection` | 几何集合核心库，用于处理 ManagedArrayCollection，是数据流输出类型之一 |
| `Chaos` | 物理引擎核心，用于模拟场景（碰撞、缓存） |
| `DynamicMesh` | 动态网格表示，用于工具目标输出 |
| `InteractiveToolsFramework` | 编辑器交互工具框架 |
| `AdvancedPreviewScene` | 高级预览场景，用于视图设置 |
| `EditorWidgets` | 编辑器控件（如组合框、列表视图） |
| `PropertyEditor` | 属性编辑器定制 |
| `WorkspaceMenuStructure` | 工作区菜单结构 |
| `InputCore` | 输入处理 |
| `SlateCore` / `Slate` | UI 框架 |
| `UnrealEd` | 编辑器基础设施 |

## 维护状态

### 近期更新

- 2026-04-25 `8450647` Dataflow : make proximity renderable type use the exploded settings  
- 2026-04-24 `ddbdf42` Dataflow : add exploded view and hierarchical component to geometry collection rendering type  
- 2026-04-24 `ca3cc90` Dataflow : fix time line issues  
- 2026-04-23 `3bbaa3b` Dataflow Editor : fix issue with reloading assets with embedded dataflow graph  
- 2026-04-23 `23602a9` Dataflow: (初始创建或主要重构)

### 维护评价

- **创建时间**：2026-04-23（极新）
- **最近更新**：更新频繁，最近几天有功能新增（爆裂视图、时间线修复）和 bug 修复。
- **活跃度**：非常活跃，Epic 团队持续投入开发。
- **推荐使用**：✅ 推荐。该插件是 UE5 未来数据处理和程序化工作流的基石，正处于积极开发阶段，新功能不断加入。但因为是早期版本，API 可能发生变化，建议关注更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Dataflow)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Dataflow/Source/DataflowEditor/Private/Tests)（假设存在）