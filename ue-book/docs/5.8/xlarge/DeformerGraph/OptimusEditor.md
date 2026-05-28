# Deformer Graph

> Editor for creating GPU mesh deformation graphs

| 属性 | 值 |
|---|---|
| 中文名 | 变形器图 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `OptimusCore` (Runtime), `OptimusDeveloper` (Runtime), `OptimusEditor` (Runtime), `OptimusSettings` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-08-30 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/DeformerGraph) | |

## 子模块文档

由于本插件源码规模较大（282 个文件），按子模块拆分文档：

| 子模块 | 类型 | 文档 |
|---|---|---|
| OptimusCore | Runtime | 核心逻辑：图模型、节点系统、编译器、数据接口 |
| OptimusDeveloper | Runtime | 开发者工具与调试支持 |
| OptimusEditor | Runtime | 编辑器 UI：图编辑器、节点面板、属性面板、Shader 文本编辑器 |
| OptimusSettings | Runtime | 插件全局设置 |

> 本文档聚焦 **OptimusEditor** 子模块，其余模块将在各自文档中详细说明。

## 用途

DeformerGraph（前身为 Optimus）是一个基于 GPU 计算着色器的**可视化网格变形图编辑器**。它允许动画师和技术美术师通过拖拽节点的方式，在不编写任何 HLSL 代码的情况下，创建高性能的 GPU 蒙皮变形管线。

**解决的核心问题：**
- 传统 CPU 蒙皮在大规模角色或复杂变形场景下性能不足
- 手写 GPU Compute Shader 门槛高、迭代慢、调试困难
- 需要一个可视化工具让非程序员也能自定义变形逻辑

**为什么存在：**
该插件在 2022 年从 Experimental 状态的 "Optimus" 插件迁移并重命名为 "DeformerGraph"，是 Epic 为 UE5 推动 GPU 驱动动画管线的关键组件。它与 ComputeFramework 紧密集成，负责将用户创建的节点图编译为 GPU 可执行的计算调度。

## 使用场景

- **角色蒙皮加速**：你有一个高精度数字人角色，骨骼数超过 200 根 → 用 DeformerGraph 创建 GPU 蒙皮替代方案
- **程序化变形**：你需要风吹衣物、肌肉抖动等基于物理的实时变形效果 → 在 DeformerGraph 中组合噪声节点和数据接口
- **自定义变形管线**：你需要在标准蒙皮之后叠加额外的顶点偏移 → 创建多阶段计算内核，按执行域组织调度
- **多人物同屏优化**：场景中有大量 NPC 需要骨骼动画 → 用 GPU 驱动的变形图批量处理
- **非程序员自定义变形**：美术需要快速实验不同的变形效果而不想写代码 → 用图编辑器拖拽组合节点

## 蓝图用法

> ⚠️ 本插件以编辑器工具为主，运行时交互主要通过组件绑定和资源描述配置，而非直接的蓝图节点调用。核心 API 位于 `OptimusCore` 模块。

### 编辑器操作流程

1. **创建资产**：在内容浏览器中右键 → Animation → Deformer Graph
2. **编辑图**：双击资产打开可视化图编辑器
3. **配置绑定**：在图资源管理器中添加组件源绑定（Component Source Binding）
4. **添加资源**：定义数据资源（Resource）用于节点间数据传递
5. **添加变量**：定义可暴露给蓝图的变量（Variable）
6. **连接节点**：从节点面板拖入内核节点、数据接口节点，连接引脚
7. **编译**：点击编译按钮，检查编译输出面板的诊断信息
8. **应用**：在 Skeletal Mesh Component 上设置 Deformer Graph 资产

### 核心编辑器控件

| 控件 | 说明 |
|---|---|
| 节点面板（Node Palette） | 可用节点分类列表，支持搜索和分类筛选 |
| 图资源管理器（Graph Explorer） | 管理图层级、绑定、资源和变量 |
| 图标题栏（Title Bar） | 面包屑导航，支持图层级跳转 |
| Shader 文本编辑器 | 带 HLSL 语法高亮的着色器代码编辑器，支持搜索和编译错误标记 |
| 编译输出面板 | 显示编译诊断信息，支持点击错误定位到节点 |

## C++ 用法

### 头文件引入

```cpp
// 编辑器模块
#include "IOptimusEditorModule.h"

// 图编辑器核心
#include "OptimusEditor.h"
#include "OptimusEditorGraph.h"
#include "OptimusEditorGraphNode.h"
```

### 基本用法：创建编辑器实例

通过模块接口创建 DeformerGraph 编辑器实例：

```cpp
#include "IOptimusEditorModule.h"

// 获取编辑器模块
IOptimusEditorModule& EditorModule = IOptimusEditorModule::Get();

// 创建编辑器实例
UOptimusDeformer* DeformerAsset = LoadObject<UOptimusDeformer>(nullptr, TEXT("/Game/MyDeformerGraph"));
TSharedRef<IOptimusEditor> Editor = EditorModule.CreateEditor(
    EToolkitMode::Standalone,
    nullptr,  // InitToolkitHost
    DeformerAsset
);
```

来源：`Public/IOptimusEditorModule.h`

### 基本用法：使用剪贴板进行节点复制粘贴

```cpp
#include "OptimusEditorClipboard.h"

// 将选中的节点序列化到剪贴板
TArray<UOptimusNode*> SelectedNodes = GetSelectedNodes();
FOptimusEditorClipboard::SetClipboardFromNodes(SelectedNodes);

// 检查剪贴板是否有有效内容
if (FOptimusEditorClipboard::HasValidClipboardContent())
{
    // 从剪贴板创建图对象用于粘贴
    UOptimusNodeGraph* ClipboardGraph = FOptimusEditorClipboard::GetGraphFromClipboardContent(TargetPackage);
}
```

来源：`Public/OptimusEditorClipboard.h`

### 进阶用法：图编辑器事件订阅

```cpp
// 订阅图通知事件
FOptimusEditor::FOnGraphNotified OnGraphNotify;
OnGraphNotify.BindLambda([](EOptimusGraphNotifyType NotifyType, UOptimusNodeGraph* Graph, UObject* Subject)
{
    // 处理图变更通知
    switch (NotifyType)
    {
    case EOptimusGraphNotifyType::NodeAdded:
        UE_LOG(LogTemp, Log, TEXT("Node added: %s"), *Subject->GetName());
        break;
    case EOptimusGraphNotifyType::NodeRemoved:
        UE_LOG(LogTemp, Log, TEXT("Node removed"));
        break;
    }
});

FDelegateHandle Handle = Editor->SubscribeToGraphNotifies(Graph, OnGraphNotify);

// 取消订阅
Editor->UnsubscribeToGraphNotifies(Handle);
```

来源：`Private/OptimusEditor.h`

### 进阶用法：监听选中节点变更

```cpp
// 注册选中节点变更回调
Editor->OnSelectedNodesChanged().AddLambda([](const TArray<TWeakObjectPtr<UObject>>& NewSelection)
{
    for (const TWeakObjectPtr<UObject>& Obj : NewSelection)
    {
        if (UOptimusEditorGraphNode* GraphNode = Cast<UOptimusEditorGraphNode>(Obj.Get()))
        {
            UOptimusNode* ModelNode = GraphNode->ModelNode;
            // 对选中的模型节点进行操作
        }
    }
});

// 监听编译诊断更新
Editor->OnDiagnosticsUpdated().AddLambda([]()
{
    const TArray<FOptimusCompilerDiagnostic>& Diagnostics = Editor->GetCompilationDiagnostics();
    for (const auto& Diagnostic : Diagnostics)
    {
        // 处理编译错误/警告
    }
});
```

来源：`Private/OptimusEditor.h`

## Demo 示例

以下展示如何在 C++ 中以编程方式创建 DeformerGraph 并注册自定义属性自定义：

### .h 文件

```cpp
// MyDeformerGraphHelper.h
#pragma once

#include "CoreMinimal.h"

class UOptimusDeformer;
class UOptimusNodeGraph;

class FMyDeformerGraphHelper
{
public:
    /** 创建一个新的 DeformerGraph 资产 */
    static UOptimusDeformer* CreateDeformerGraph(
        const FString& InAssetPath,
        const FString& InAssetName);

    /** 在指定图中获取所有内核节点的名称 */
    static TArray<FName> GetKernelNodeNames(UOptimusNodeGraph* InGraph);

    /** 打开 DeformerGraph 编辑器 */
    static void OpenEditor(UOptimusDeformer* InDeformer);
};
```

### .cpp 文件

```cpp
// MyDeformerGraphHelper.cpp
#include "MyDeformerGraphHelper.h"
#include "IOptimusEditorModule.h"
#include "OptimusDeformer.h"
#include "OptimusNodeGraph.h"
#include "OptimusNode.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "Factories.h"

UOptimusDeformer* FMyDeformerGraphHelper::CreateDeformerGraph(
    const FString& InAssetPath,
    const FString& InAssetName)
{
    UPackage* Package = CreatePackage(*FString::Printf(TEXT("%s/%s"), *InAssetPath, *InAssetName));
    UOptimusDeformer* NewDeformer = NewObject<UOptimusDeformer>(
        Package, UOptimusDeformer::StaticClass(), FName(*InAssetName),
        RF_Public | RF_Standalone | RF_Transactional);

    if (NewDeformer)
    {
        FAssetRegistryModule::AssetCreated(NewDeformer);
        Package->MarkPackageDirty();
    }
    return NewDeformer;
}

TArray<FName> FMyDeformerGraphHelper::GetKernelNodeNames(UOptimusNodeGraph* InGraph)
{
    TArray<FName> NodeNames;
    if (!InGraph) return NodeNames;

    for (UOptimusNode* Node : InGraph->GetAllNodes())
    {
        if (Node)
        {
            NodeNames.Add(Node->GetFName());
        }
    }
    return NodeNames;
}

void FMyDeformerGraphHelper::OpenEditor(UOptimusDeformer* InDeformer)
{
    if (!InDeformer) return;

    IOptimusEditorModule& EditorModule = IOptimusEditorModule::Get();
    EditorModule.CreateEditor(
        EToolkitMode::Standalone,
        nullptr,
        InDeformer
    );
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `OptimusCore` | DeformerGraph 核心逻辑：图模型、节点系统、编译器、数据接口定义 |
| `OptimusDeveloper` | 开发者调试工具和运行时支持 |
| `Persona` | 骨骼网格编辑器集成（预览场景、骨骼操作） |
| `AssetTools` | 资产类型注册和编辑器操作 |
| `RenderCore` | GPU 计算着色器相关渲染基础设施 |
| `ShaderCore` | HLSL 语法高亮器（`FHLSLSyntaxHighlighterMarshaller`） |
| `KismetWidgets` | 图编辑器搜索功能（`SFindInGraph`） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `43a2c5ff` | Deformer Graph: programmatic component resolver | 新增编程式组件解析器，支持代码驱动的组件查找 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点数的编译警告 |
| 2026-04-24 | `59214322` | [ComputeFramework + Optimus] Added Per-kernel output mask for data interfaces as in certain cases (S | 为数据接口添加逐内核输出掩码，优化特定场景的调度 |
| 2026-04-16 | `004f9e11` | Deformer Graph: ability to look for secondary bindings in parent actors if not found in the component | 当组件中未找到绑定时，支持在父 Actor 中查找二级绑定 |
| 2026-04-14 | `909e5b5b` | [Deformer Graph] Move Mark Deformed to PostSubmit and GetReadableOutputBuffer to Gather dispatch dat | 将"标记已变形"移至 PostSubmit，将可读输出缓冲区移至调度数据收集阶段 |

### 维护评价

- **状态**: 🟢 **活跃维护**
- **创建时间**: 2022 年 8 月（从 Experimental 的 Optimus 迁移并重命名）
- **最近更新**: 2026 年 5 月仍有功能性更新，且更新频率稳定（约每 2 周一次）
- **成熟度**: 仍标记为 Beta（`IsBetaVersion=true`），但已广泛用于 Epic 自己的项目
- **趋势**: 持续有新功能添加（组件解析器、逐内核掩码、父 Actor 绑定查找），表明正在向正式版推进
- **已知限制**: 需要 GPU 支持 Compute Shader（SM5+），移动端兼容性有限；需要手动启用插件（`EnabledByDefault=false`）
- **推荐**: ✅ **推荐使用**。虽然是 Beta 状态，但 Epic 持续投入开发，是 UE5 GPU 动画管线的官方解决方案。适合需要 GPU 加速变形的专业项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/DeformerGraph)
- [OptimusCore 子模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/DeformerGraph/Source/OptimusCore)
- [OptimusEditor 子模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/DeformerGraph/Source/OptimusEditor)