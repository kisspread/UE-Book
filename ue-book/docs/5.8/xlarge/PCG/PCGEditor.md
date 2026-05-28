# Procedural Content Generation Framework (PCG)

> Visual scripting framework for procedurally populating worlds with content in editor and/or at run-time.

| 属性 | 值 |
|---|---|
| 中文名 | 程序化内容生成框架 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `PCG` (Runtime), `PCGCompute` (Runtime), `PCGEditor` (Runtime), `PCGTests` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-01-30 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/PCG) | |

## 用途

PCG 是 UE5 的核心程序化内容生成系统，提供了一个基于节点图的可视化脚本框架，用于在编辑器和/或运行时程序化地填充世界内容。

**核心解决的问题**：传统关卡设计中，手动放置大量重复或有规律的场景元素（植被、岩石、建筑装饰、拾取物等）极其耗时且难以维护。PCG 通过数据流图（Data Flow Graph）将生成逻辑模块化，每个节点负责一个特定的数据操作（采样、过滤、变换、生成等），最终驱动静态网格体实例化（ISM/HISM）或其他输出。

**为什么存在**：
- 取代传统的 Foliage 工具和手动摆放，提供更灵活、可复用、可版本控制的程序化工作流
- 支持分层生成（Hierarchical Generation），可根据不同网格大小（HiGen Grid）在不同 LOD 层级生成内容
- 支持 GPU 加速执行（Compute Shader 后端），大幅提升大数据量场景的生成性能
- 提供"手动编辑"（Manual Edit）模式，允许艺术家在程序化结果基础上进行局部微调
- 与 World Partition 深度集成，支持分区世界的流式生成和烘焙（PCGWorldPartitionBuilder）

## 使用场景

- **开放世界场景填充**：你需要在大面积地形上程序化放置石头、树木、草丛 → 使用 Surface Sampler + Static Mesh Spawner 节点组合
- **建筑内部装饰**：你需要在房间内自动放置家具和装饰物 → 使用 Volume Sampler 或已有的网格体表面采样
- **地牢/关卡生成**：你需要运行时生成房间布局和内容 → 使用 Loop 节点 + Subgraph 组合，配合运行时 PCG Component 触发生成
- **GPU 加速大量实例生成**：你有数十万实例需要快速生成 → 使用 GPU 兼容节点（带 GPU 标签的节点）在 Compute Shader 上执行
- **烘焙世界分区内容**：你需要将 PCG 生成结果烘焙为静态内容 → 使用 PCGWorldPartitionBuilder（命令行工具）
- **程序化内容的手动微调**：设计师想在自动生成的结果上手动删除/移动部分实例 → 使用 Manual Edit 面板和 Delta 编辑系统
- **交互式工具编辑 PCG 节点**：你想在视口中通过画刷、样条线、体积等交互方式直接编辑 PCG 节点参数 → 使用 PCG Editor Mode 中的交互工具（Draw Spline、Paint、Volume、Query 等）

## 蓝图用法

PCG 模块的核心 API 主要集中在运行时模块中。以下是从 PCGEditor 模块提取的可在蓝图中使用的功能：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddAssetToSubmitAllowList` | 将资产添加到 PCG Builder 的允许提交列表中 | `UPCGWorldPartitionBuilderHelper` |
| `HasSpawnedActor` | 返回当前工具是否已生成 Actor | `UPCGInteractiveToolSettings` |
| `HasGeneratedPCGComponent` | 返回当前工具是否已生成 PCG Component | `UPCGInteractiveToolSettings` |
| `GetWorkingPCGComponent` | 获取当前正在操作的 PCG Component | `UPCGInteractiveToolSettings` |
| `GraphAssetFilter` | 过滤 Details 面板中的图表资产选择器 | `UPCGInteractiveToolSettings` |
| `GetDataInstanceNamesForGraph` | 获取当前图表的所有数据实例名称 | `UPCGInteractiveToolSettings` |

### PCG 编辑器设置

PCG 提供了丰富的编辑器设置（`UPCGEditorSettings`），可控制：

- **节点颜色**：为不同类型的 PCG 节点（输入/输出、采样、过滤、生成、蓝图、子图等）配置不同的颜色
- **引脚颜色**：为空间数据、点数据、样条线、地形、纹理等不同类型引脚配置颜色
- **工作流配置**：双击节点行为、是否显示模板选择器、是否允许选择分区 Actor 等
- **编辑器性能**：视口是否作为生成源、是否禁用 CPU 限流、暂停按钮配置等
- **属性列表视图**：列名溢出策略、字符串溢出策略等

## C++ 用法

### 头文件引入

```cpp
// PCG 编辑器模块
#include "PCGEditorModule.h"
#include "PCGEditor.h"
#include "PCGEditorGraphNodeBase.h"
#include "PCGEditorSettings.h"

// PCG 数据可视化
#include "PCGDataVisualizationHelpers.h"
#include "PCGDeltaVisualizationRegistry.h"
#include "PCGDeltaViewportExtension.h"

// PCG 交互工具
#include "PCGInteractiveToolSettings.h"
#include "PCGAssetEditorInteractiveTool.h"
```

### 基本用法 — 自定义节点图编辑器扩展

```cpp
// 获取 PCG 编辑器模块
FPCGEditorModule& PCGEditorModule = FModuleManager::GetModuleChecked<FPCGEditorModule>("PCGEditor");

// 创建进度通知
TWeakPtr<IPCGEditorProgressNotification> Notification = 
    PCGEditorModule.CreateProgressNotification(
        FTextFormat::FromString(TEXT("Processing {0}...")), true);

// 设置编辑器权限模式
PCGEditorModule.SetPermissionMode(EPCGEditorPermissionMode::All);
```

来源：`Source/PCGEditor/Public/PCGEditorModule.h`

### 基本用法 — 数据可视化辅助

```cpp
#include "PCGDataVisualizationHelpers.h"

// 为 PCG 数据创建表可视化信息
FPCGTableVisualizerInfo Info;
UPCGData* MyData = /* ... */;

// 创建默认的元数据列信息
Info = PCGDataVisualizationHelpers::CreateDefaultMetadataColumnInfos(MyData);

// 添加自定义列
FPCGAttributePropertySelector Selector = FPCGAttributePropertySelector::CreateAttributeSelector(TEXT("MyAttribute"));
PCGDataVisualizationHelpers::AddColumnInfo(Info, MyData, Selector);

// 使用模板版本添加带类型的列
PCGDataVisualizationHelpers::AddTypedColumnInfo<FVector>(Info, MyData, Selector);
```

来源：`Source/PCGEditor/Public/DataVisualizations/PCGDataVisualizationHelpers.h`

### 进阶用法 — 自定义 Delta 可视化扩展

```cpp
#include "PCGDeltaViewportExtension.h"

// 实现自定义 Delta 视口扩展
class FMyCustomViewportExtension : public IPCGDeltaViewportExtension
{
public:
    virtual FText GetDisplayName() const override 
    { 
        return NSLOCTEXT("MyPCG", "CustomDelta", "Custom Delta"); 
    }
    
    virtual TSharedRef<SWidget> CreateWidget(FPCGDeltaViewportCallbacks Callbacks) override
    {
        return SNew(STextBlock).Text(FText::FromString("Custom Delta Widget"));
    }
    
    virtual void UpdateContext(const FPCGDeltaViewportContext& Context) override { /* ... */ }
    virtual void RefreshLists(const FPCGDeltaViewportContext& Context) override { /* ... */ }
    
    virtual FLinearColor GetDisplayColor(bool bIsSelected) const override
    {
        return bIsSelected ? FLinearColor::Yellow : FLinearColor::Green;
    }
    
    virtual bool MatchesSourceElement(const FTransform& SourceElementTransform, 
                                       const FConstStructView DeltaStruct, 
                                       const double SpatialTolerance) const override
    {
        return false;
    }
};

// 注册到 Delta 视口扩展注册表
FPCGDeltaViewportExtensionRegistry& Registry = FPCGEditorModule::GetMutableDeltaViewportExtensionRegistry();
Registry.RegisterExtension(
    FMyCustomDelta::StaticStruct(), 
    MakeUnique<FMyCustomViewportExtension>());
```

来源：`Source/PCGEditor/Public/DeltaViewportExtensions/PCGDeltaViewportExtension.h`

### 进阶用法 — 注册自定义资产编辑器交互工具

```cpp
#include "PCGAssetEditorInteractiveTool.h"

// 声明自定义工具
UCLASS()
class UPCGMyCustomTool : public UPCGAssetEditorInteractiveTool
{
    GENERATED_BODY()
public:
    // 声明支持的节点类型
    PCG_DECLARE_SUPPORTED_NODES(
        UPCGMySettingsA,
        UPCGMySettingsB
    );
    
    virtual void Setup() override
    {
        Super::Setup();
        // 初始化工具
    }
    
    virtual void OnAccept() override
    {
        // 应用工具结果
    }
    
protected:
    virtual TArray<UClass*> GetSupportedSettingsClasses() const override
    {
        return { UPCGMySettingsA::StaticClass(), UPCGMySettingsB::StaticClass() };
    }
};

// 在模块启动时注册
void FMyModule::StartupModule()
{
    FPCGAssetEditorToolRegistry::Get().RegisterTool(
        UPCGMySettingsA::StaticClass(), 
        UPCGMyCustomTool::StaticClass());
}
```

来源：`Source/PCGEditor/Public/AssetEditorMode/Tools/PCGAssetEditorInteractiveTool.h`

## Demo 示例

### 自定义 PCG 数据可视化

```cpp
// MyPCGDataVisualization.h
#pragma once

#include "DataVisualizations/PCGBaseTextureDataVisualization.h"

class FMyCustomDataVisualization : public FPCGBaseTextureDataVisualization
{
public:
    virtual TArray<TSharedPtr<FStreamableHandle>> LoadRequiredResources(const UPCGData* Data) const override;
    virtual FPCGSetupSceneFunc GetViewportSetupFunc(
        const UPCGSettingsInterface* SettingsInterface, 
        const UPCGData* Data) const override;
};
```

```cpp
// MyPCGDataVisualization.cpp
#include "MyPCGDataVisualization.h"
#include "PCGDataVisualizationHelpers.h"

TArray<TSharedPtr<FStreamableHandle>> FMyCustomDataVisualization::LoadRequiredResources(
    const UPCGData* Data) const
{
    TArray<TSharedPtr<FStreamableHandle>> Handles;
    // 加载所需的纹理/材质资源
    return Handles;
}

FPCGSetupSceneFunc FMyCustomDataVisualization::GetViewportSetupFunc(
    const UPCGSettingsInterface* SettingsInterface, 
    const UPCGData* Data) const
{
    return [WeakData = TWeakObjectPtr<const UPCGData>(Data)](FPCGSceneSetupContext& Context)
    {
        if (const UPCGData* PinnedData = WeakData.Get())
        {
            // 设置视口中的可视化场景
            // 添加网格体、材质等
        }
    };
}
```

### 自定义 Delta 可视化注册

```cpp
// MyDeltaVisualization.h
#pragma once

#include "DeltaVisualizations/PCGDeltaVisualizationRegistry.h"
#include "PCGDeltaVisualization.h"

class FMyDeltaVisualization : public IPCGDeltaVisualization
{
public:
    virtual TArray<FPCGDeltaVisualizerColumnInfo> GetColumnInfos() const override
    {
        return { { FName("Status"), FText::FromString("Status"), EPCGMetadataTypes::String } };
    }
    
    virtual FText GetCellText(FName ColumnId, const FPCGDeltaKey& DeltaKey, 
                               FConstStructView Delta) const override
    {
        return FText::FromString("Modified");
    }
};
```

```cpp
// 注册 Delta 可视化（在模块启动时）
FPCGDeltaVisualizationRegistry& Registry = FPCGEditorModule::GetMutableDeltaVisualizationRegistry();
Registry.RegisterDeltaVisualization(
    FMyCustomDelta::StaticStruct(), 
    MakeUnique<FMyDeltaVisualization>());
```

来源：`Source/PCGEditor/Public/DeltaVisualizations/PCGDeltaVisualizationRegistry.h`

## 模块依赖

PCGEditor 模块的特殊依赖（摘自 Build.cs）：

| 模块 | 用途 |
|---|---|
| `PCG` | PCG 运行时核心模块，提供 PCG 图、节点、设置、数据等基础类型 |
| `PCGCompute` | PCG 计算模块，支持 GPU 执行后端 |
| `ContentBrowser` | 内容浏览器集成，用于资产选择器和浏览器同步 |
| `ClassViewer` | 类查看器，用于 SoftClassPath 引脚的类选择 |
| `InteractiveToolsFramework` | 交互工具框架，用于编辑器模式中的视口交互工具 |
| `ToolWidgets` | 工具 UI 控件，用于 Manual Edit 面板等工具界面 |
| `WorkspaceMenuStructure` | 工作区菜单结构，用于编辑器标签页的组织 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `1cd8cea5` | [PCG] Fixed potential crash when building the landscape cache, when some entries can't be resolved. | 修复地形缓存构建时某些条目无法解析导致的崩溃 |
| 2026-05-26 | `788faf05` | [PCG] Optimize FPCGComponentVisualizer | 优化 PCG 组件可视化器性能 |
| 2026-05-26 | `0532b644` | [PCG] Fix crash with null objects with accessors | 修复访问器中空对象导致的崩溃 |
| 2026-05-26 | `82ca98ed` | [PCG] Optimized & cached metadata size computation, but gated on a flag w/ TLS backing so the normal | 优化并缓存元数据大小计算，使用 TLS 支持的标志进行控制 |
| 2026-05-26 | `585bbecb` | [PCG] Fixed editor update performance issue related to manual edit (+ a double update) and inspectio | 修复与手动编辑和检查相关的编辑器更新性能问题 |

### 维护评价

**积极维护中** ✅

- **创建时间**：2024-01-30（从实验性功能移出正式发布）
- **更新频率**：非常活跃，最近提交集中在 2026-05-26，且同一日期有多次提交
- **维护内容**：涵盖 bug 修复（崩溃修复）、性能优化（组件可视化器、元数据计算、编辑器更新）、功能改进
- **代码规模**：1472 个源文件，属于超大型插件，包含完整的编辑器工具链、交互工具、调试工具、数据可视化系统
- **模块化设计**：分为 PCG（运行时核心）、PCGCompute（GPU 计算）、PCGEditor（编辑器）、PCGTests（测试）四个模块

**注意**：虽然插件较新（约 2 年），但 Epic 对其投入了大量开发资源，是 UE5 程序化内容生成的核心基础设施。代码中有大量 `@todo_pcg` 标记，表明仍在持续迭代中。强烈推荐在需要程序化内容生成的项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/PCG)
- [官方文档](https://docs.unrealengine.com/latest/en-US/procedural-content-generation--framework-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/PCG/Tests)