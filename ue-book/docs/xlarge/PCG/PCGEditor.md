# Procedural Content Generation Framework (PCG)

> Visual scripting framework for procedurally populating worlds with content in editor and/or at run-time.

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `PCG` (Runtime), `PCGCompute` (Runtime), `PCGEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-01-13 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/PCG) | |

## 用途

PCG (Procedural Content Generation Framework) 是一个功能强大的可视化脚本框架，用于在编辑器和/或运行时程序化地填充世界内容。它解决的核心问题是：如何让设计师和开发者能够通过直观的节点图（而非编写大量代码）来定义复杂的、可控的程序化内容生成规则。

该框架允许用户创建由各种节点组成的图（Graph），这些节点可以执行数据生成、过滤、变换、采样等操作。最终，这些图可以驱动静态网格体、植被、Actor 等内容的生成，实现大规模、多样且符合设计意图的程序化世界构建。它旨在提供比传统蓝图更高层次的抽象，专注于空间数据和内容生成逻辑。

## 使用场景

- **开放世界内容填充**：你需要在一个巨大的开放世界中程序化地放置树木、岩石、草地、建筑等，同时保持艺术控制和性能优化。
- **地牢/关卡生成**：你正在开发一个带有随机生成关卡的游戏（如 Roguelike），需要定义房间布局、敌人分布和物品放置的规则。
- **城市或环境布局**：你需要生成街道网络、建筑群、城市装饰物等复杂布局。
- **数据驱动的内容变体**：你希望根据不同的参数（如生物群系、难度）动态改变生成的内容。
- **运行时动态生成**：你需要在玩家探索时动态生成地形、植被或兴趣点。

## 蓝图用法

PCG 框架的核心逻辑和节点主要在 `PCG` 和 `PCGCompute` 运行时模块中定义。`PCGEditor` 模块主要提供编辑器内的图编辑、调试和可视化工具。以下是从 `PCGEditor` 模块头文件中提取的、可供蓝图或编辑器工具使用的部分 API。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateOrUpdatePCGAssets` | 根据一个或多个世界资产（UWorld）创建或更新对应的 PCG 数据资产。 | `UPCGLevelToAsset` |
| `BP_ExportWorld` | 蓝图可重写的事件，用于自定义从世界导出数据到 PCG 资产的过程。 | `UPCGLevelToAsset` |
| `SetWorld` / `GetWorld` | 设置或获取用于导出的世界对象。 | `UPCGLevelToAsset` |
| `DispatchEditorToast` | 在编辑器中显示一个临时通知消息。 | `FPCGEditorCommon::Helpers` |

### 使用示例（蓝图描述）

1.  **将关卡导出为 PCG 资产**：
    *   创建一个继承自 `UPCGLevelToAsset` 的蓝图类。
    *   重写 `BP_ExportWorld` 事件，在其中实现自定义的解析逻辑，将世界中的 Actor 数据提取并填充到传入的 `UPCGDataAsset` 中。
    *   在另一个蓝图（如编辑器工具）中，调用 `CreateOrUpdatePCGAssets` 静态函数，传入要导出的世界资产引用和你的自定义导出器类。

2.  **在编辑器工具中显示通知**：
    *   在你的编辑器工具蓝图中，调用 `FPCGEditorCommon::Helpers::DispatchEditorToast` 函数，传入要显示的文本和持续时间。

## C++ 用法

PCG 框架的 C++ 用法主要围绕创建自定义 PCG 节点（Settings）、扩展编辑器功能以及与 PCG 子系统交互。由于这是一个 xlarge 插件，其核心 API 非常庞大。以下示例基于提供的头文件，展示如何与 PCG 编辑器模块交互。

### 头文件引入

```cpp
#include "PCGEditorModule.h"
#include "PCGEditor.h"
#include "PCGLevelToAsset.h"
```

### 基本用法

**访问 PCG 编辑器模块并获取节点视觉日志**：
```cpp
// 来源: Engine/Plugins/PCG/Source/PCGEditor/Public/PCGEditorModule.h
// 获取 PCG 编辑器模块实例
FPCGEditorModule& PCGEditorModule = FModuleManager::GetModuleChecked<FPCGEditorModule>(TEXT("PCGEditor"));

// 获取节点视觉日志管理器，用于记录和显示节点执行时的调试信息
FPCGNodeVisualLogs& VisualLogs = PCGEditorModule.GetNodeVisualLogsMutable();
VisualLogs.LogToNode(MyPCGNode, TEXT("This is a debug message from my custom code."));
```

**使用 PCGLevelToAsset 导出世界**：
```cpp
// 来源: Engine/Plugins/PCG/Source/PCGEditor/Public/PCGLevelToAsset.h
// 假设你有一个 UWorld* WorldToExport
FPCGAssetExporterParameters ExportParams;
ExportParams.bSaveOnExport = true;
ExportParams.PackagePath = TEXT("/Game/PCG/ExportedAssets");

// 使用默认导出器
UPackage* ResultPackage = UPCGLevelToAsset::CreateOrUpdatePCGAsset(WorldToExport, ExportParams);

// 或者使用自定义的导出器子类
TSubclassOf<UPCGLevelToAsset> MyExporterClass = UMyCustomLevelToAsset::StaticClass();
UPackage* CustomResultPackage = UPCGLevelToAsset::CreateOrUpdatePCGAsset(WorldToExport, ExportParams, MyExporterClass);
```

### 进阶用法

**创建自定义的 PCG 数据可视化**：
PCG 编辑器允许为不同类型的数据注册自定义的可视化方式。你可以继承 `IPCGDataVisualization` 或其子类（如 `IPCGSpatialDataVisualization`）并实现相关接口。
```cpp
// 参考 Engine/Plugins/PCG/Source/PCGEditor/Public/DataVisualizations/PCGSpatialDataVisualization.h
class FMyCustomDataVisualization : public IPCGSpatialDataVisualization
{
public:
    // 重写此函数以提供自定义的调试显示逻辑
    virtual void ExecuteDebugDisplay(FPCGContext* Context, const UPCGSettingsInterface* SettingsInterface, const UPCGData* Data, AActor* TargetActor) const override
    {
        // 你的自定义可视化代码
    }

    // 重写此函数以提供自定义的表格列信息，用于属性列表视图
    virtual FPCGTableVisualizerInfo GetTableVisualizerInfoWithDomain(const UPCGData* Data, const FPCGMetadataDomainID& DomainID) const override
    {
        FPCGTableVisualizerInfo Info;
        // 添加自定义列...
        return Info;
    }
};

// 在模块启动时注册你的可视化
// (通常在 FPCGEditorModule::StartupModule 中调用)
void RegisterMyVisualization()
{
    // 假设你有一个获取模块的函数
    FPCGEditorModule* EditorModule = FModuleManager::GetModulePtr<FPCGEditorModule>(TEXT("PCGEditor"));
    if (EditorModule)
    {
        // 注册逻辑，具体方式取决于模块提供的接口
    }
}
```

## Demo 示例

以下是一个最小化的示例，展示如何创建一个简单的 PCG 编辑器扩展，该扩展在模块启动时记录一条消息。

**MyPCGEditorExtension.h**
```cpp
#pragma once
#include "Modules/ModuleManager.h"

class FMyPCGEditorExtensionModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

**MyPCGEditorExtension.cpp**
```cpp
#include "MyPCGEditorExtension.h"
#include "PCGEditorModule.h"

#define LOCTEXT_NAMESPACE "FMyPCGEditorExtensionModule"

void FMyPCGEditorExtensionModule::StartupModule()
{
    // 确保 PCGEditor 模块已加载
    FModuleManager::Get().LoadModule(TEXT("PCGEditor"));
    
    UE_LOG(LogTemp, Log, TEXT("MyPCGEditorExtension: Startup! PCG Editor features are available."));
    
    // 示例：尝试获取 PCG 编辑器模块
    FPCGEditorModule* PCGEditorModule = FModuleManager::GetModulePtr<FPCGEditorModule>(TEXT("PCGEditor"));
    if (PCGEditorModule)
    {
        UE_LOG(LogTemp, Log, TEXT("MyPCGEditorExtension: Successfully accessed PCGEditorModule."));
    }
}

void FMyPCGEditorExtensionModule::ShutdownModule()
{
    UE_LOG(LogTemp, Log, TEXT("MyPCGEditorExtension: Shutdown."));
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyPCGEditorExtensionModule, MyPCGEditorExtension)
```

**MyPCGEditorExtension.Build.cs**
```csharp
using UnrealBuildTool;

public class MyPCGEditorExtension : ModuleRules
{
    public MyPCGEditorExtension(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        
        PublicDependencyModuleNames.AddRange(new string[] { 
            "Core",
            "CoreUObject",
            "Engine",
            "PCGEditor" // 依赖 PCGEditor 模块
        });
        
        PrivateDependencyModuleNames.AddRange(new string[] { 
            "Slate",
            "SlateCore",
            "UnrealEd" // 编辑器模块通常需要
        });
    }
}
```

## 模块依赖

要使用 PCG 插件的功能，你的模块通常需要依赖 `PCG` 运行时模块。如果需要编辑器功能（如自定义节点可视化、扩展编辑器 UI），则需要依赖 `PCGEditor` 模块。

| 模块 | 用途 |
|---|---|
| `PCG` | PCG 框架的核心运行时模块，包含图执行、数据类型、节点设置等基础功能。 |
| `PCGCompute` | PCG 的计算模块，可能包含 GPU 计算或并行处理相关功能。 |
| `PCGEditor` | PCG 的编辑器模块，提供图编辑器、调试工具、资产类型操作和自定义细节面板等。 |

## 维护状态

### 近期更新

1.  **31a3298bbf96** (2024-07-26) - `[PCG] Fix crash on engine exit`
    *   **解读**：修复了一个在引擎退出时发生的崩溃问题。这是一个重要的稳定性修复。
2.  **4b6aeae4ea5e** (2024-07-25) - `[PCG] Disabled temporal AA & general viewport setup when entering PCG toolmode.`
    *   **解读**：改进了 PCG 工具模式下的视口体验，禁用了时域抗锯齿并调整了通用视口设置，可能是为了提升工具模式下的性能或视觉清晰度。
3.  **429aebd64400** (2024-07-25) - `[PCG] Fixed a crash/infinite loop when selecting actors that aren't valid with the tools. Fixed crash when selecting no actor class. Cleaned up more component pointers so BP actors can be edited while in the tool. Also reviewed pointer type so we don't resurrect components that would have been properly removed. Improved management of actor pivots, especially on newly created actors. Fixed minor UI problem in the attribute list view.`
    *   **解读**：这是一次综合性的质量改进更新。修复了多个与工具模式下 Actor 选择相关的崩溃和无限循环问题，改进了蓝图 Actor 在工具模式下的可编辑性，优化了组件指针管理和 Actor 轴心点处理，并修复了属性列表视图的一个 UI 问题。这表明团队正在积极打磨工具的稳定性和用户体验。

### 维护评价

PCG 插件由 Epic Games 官方维护，是 UE5 的核心功能之一。从创建时间（2022年）和最近的提交记录来看，该插件处于**活跃维护**状态。最近的提交集中在修复崩溃、改进编辑器工具稳定性和用户体验上，表明其仍在持续开发和完善中。作为官方插件，它拥有良好的支持和文档。**推荐使用**，尤其是在需要程序化内容生成的项目中。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/PCG)
- [官方文档](https://docs.unrealengine.com/latest/en-US/procedural-content-generation--framework-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/PCG/Tests) (如果存在)