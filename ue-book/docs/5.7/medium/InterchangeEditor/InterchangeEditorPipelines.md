# Interchange Editor Pipelines

> The Interchange Editor plugin exposes the Interchange import framework and pipelines to Unreal Editor.

| 属性 | 值 |
|---|---|
| 中文名 | 交换编辑器管道 UI |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产类型、编辑器界面样式） |
| 模块 | `InterchangeEditorPipelines` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-09-23 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Editor/Source/Pipelines) | |

## 用途

Interchange Editor Pipelines 模块为 Interchange 导入框架提供了一整套编辑器级用户界面组件。它实现了导入过程中用于配置管道（Pipeline）的对话框、图形检查器、资源卡片列表、翻译器设置窗口以及各种细节定制（如 GLTF、MaterialX 管道的属性面板）。该模块的核心作用是让用户能够通过友好的交互界面——而非手动编写 Python 或 C++ 代码——来管理导入流程中的管道设置、冲突解决和预览。

它解决了以下问题：
- 为**非技术艺术家**提供可视化的导入管道配置对话框（`SInterchangePipelineConfigurationDialog`）
- 在导入前预览资源结构并选择性地启用/禁用导入的节点（`SInterchangeGraphInspectorWindow`）
- 显示导入过程中每种资产类型的摘要卡片，并高亮冲突警告（`SInterchangeAssetCard`）
- 提供翻译器设置修改对话框（`SInterchangeTranslatorSettingsDialog`）
- 为管道基类（`UInterchangePipelineBase`）和特定管道（GLTF、MaterialX）自定义细节面板样式

## 使用场景

- **你在使用 Interchange 导入 3D 场景（FBX/glTF）** → 本模块负责显示管道路由选择、每步管道的属性面板、以及最终资源的预览卡片。
- **你需要为美术团队提供简化导入流程** → 利用 `SInterchangePipelineConfigurationDialog` 和预设系统，可以保存/加载管道配置，降低操作门槛。
- **你在开发自定义导入管道** → 你的管道类（继承 `UInterchangePipelineBase`）的属性会自动被 `FInterchangePipelineBaseDetailsCustomization` 渲染成可交互的 UI 面板。
- **你需要调试导入过程** → 使用 `SInterchangeGraphInspectorWindow` 图形检查器，可以以树状视图浏览导入场景的完整节点图，并手动切换每个节点的导入状态。

## 蓝图用法

本模块绝大部分是编辑器 UI 组件，不暴露直接的 BlueprintCallable 函数。不过，`UInterchangePipelineConfigurationGeneric` 可用于 C++ 中启动管道配置对话框，该对话框本身展示了所有可用的 UI 组件。

### 核心节点（C++ 调用入口，蓝图不可直接调用）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ShowPipelineDialog`（继承自 `UInterchangePipelineConfigurationBase`） | 显示管道配置模态对话框，返回用户选择结果 | `UInterchangePipelineConfigurationGeneric` |
| `ExecutePipeline`（Overridden，公开但通常不直接调用） | 执行图形检查器管道的逻辑（打开图形检查器窗口） | `UInterchangeGraphInspectorPipeline` |
| `ExecutePipeline`（Overridden，公开但通常不直接调用） | 执行资源卡片管道的逻辑（根据 UI 选择禁用/启用工厂节点） | `UInterchangeCardsPipeline` |

**使用示例（蓝图伪代码）**：

> 注意：在蓝图中无法直接实例化 `UInterchangePipelineConfigurationGeneric` 并调用 `ShowPipelineDialog`，因为该函数是 `Protected` 且需要传递复杂参数。正确的用法是通过 C++ 或 Python 调用 Interchange 导入命令（如 `InterchangeTools.ImportAsset`），该命令内部会自动调用此 UI。

## C++ 用法

### 头文件引入

```cpp
#include "InterchangePipelineConfigurationGeneric.h"
#include "SInterchangePipelineConfigurationDialog.h"
#include "InterchangeCardsPipeline.h"
#include "InterchangeGraphInspectorPipeline.h"
```

### 基本用法

以下示例展示了如何在 C++ 中获取当前 Interchange 的管道配置 UI 并显示对话框（通常由 Interchange 导入框架内部调用）。

```cpp
// 文件来源: Engine/Plugins/Interchange/Editor/Source/Pipelines/Private/InterchangePipelineConfigurationGeneric.cpp

void UInterchangePipelineConfigurationGeneric::ShowPipelineDialog_Internal(FPipelineConfigurationDialogParams& InParams)
{
    // 创建管道配置对话框
    TSharedRef<SInterchangePipelineConfigurationDialog> Dialog = SNew(SInterchangePipelineConfigurationDialog)
        .SourceData(InParams.SourceData)
        .bSceneImport(InParams.bSceneImport)
        .bReimport(InParams.bReimport)
        .PipelineStacks(InParams.PipelineStacks)
        .OutPipelines(InParams.OutPipelines)
        .BaseNodeContainer(InParams.BaseNodeContainer)
        .ReimportObject(InParams.ReimportObject);

    // 打开模态窗口（内部会阻塞直到用户确认或取消）
    Dialog->ShowModal();
}
```

### 进阶用法

#### 1. 使用图形检查器管道预览导入场景

`UInterchangeGraphInspectorPipeline` 是一个特殊的管道，它会在导入前打开一个图形检查器窗口，让用户预览并调整导入节点。

```cpp
// 文件来源: Engine/Plugins/Interchange/Editor/Source/Pipelines/Private/InterchangeGraphInspectorPipeline.cpp

UInterchangeGraphInspectorPipeline* InspectorPipeline = NewObject<UInterchangeGraphInspectorPipeline>();

// 设置管道要执行的节点容器
TArray<UInterchangeSourceData*> SourceDatas;
SourceDatas.Add(SourceData);

InspectorPipeline->ExecutePipeline(BaseNodeContainer, SourceDatas, TEXT("/Game/Imports"));
// 执行时内部会创建 SInterchangeGraphInspectorWindow 并显示
```

#### 2. 以编程方式禁用某些工厂节点（对应资源卡片 UI）

`UInterchangeCardsPipeline` 允许您根据 UI 选择设置哪些类型的资产不被导入。

```cpp
// 文件来源: Engine/Plugins/Interchange/Editor/Source/Pipelines/Public/InterchangeCardsPipeline.h

UInterchangeCardsPipeline* CardsPipeline = NewObject<UInterchangeCardsPipeline>();
TArray<UClass*> FactoryNodeClassesToDisable;
FactoryNodeClassesToDisable.Add(UInterchangeStaticMeshFactoryNode::StaticClass());
CardsPipeline->SetDisabledFactoryNodes(FactoryNodeClassesToDisable);

// 执行管道后，静态网格体工厂节点将被禁用，不会被导入
CardsPipeline->ExecutePipeline(BaseNodeContainer, SourceDatas, TEXT("/Game/Imports"));
```

#### 3. 自定义管道属性面板（使用细节定制类）

`FInterchangePipelineBaseDetailsCustomization` 会自动关联到任何 `UInterchangePipelineBase` 实例的细节面板，提供渲染支持（如冲突信息区域、额外信息区域、只读属性锁定）。

```cpp
// 文件来源: Engine/Plugins/Interchange/Editor/Source/Pipelines/Private/InterchangeEditorPipelineDetails.cpp

// 注册自定义细节（通常由模块启动时自动注册）
FPropertyEditorModule& PropertyModule = FModuleManager::LoadModuleChecked<FPropertyEditorModule>("PropertyEditor");
PropertyModule.RegisterCustomClassLayout(
    UInterchangePipelineBase::StaticClass()->GetFName(),
    FOnGetDetailCustomizationInstance::CreateStatic(&FInterchangePipelineBaseDetailsCustomization::MakeInstance)
);
```

## Demo 示例

以下是一个最小、可独立编译的 C++ 模块，演示如何通过代码启动 Interchange 管道配置对话框（假设已配置好源数据和节点容器）。此示例不展示完整的导入流程，仅展示 UI 的触发方式。

```cpp
// InterchangeUISample.h
#pragma once
#include "CoreMinimal.h"
#include "Modules/ModuleInterface.h"
#include "Modules/ModuleManager.h"

class FInterchangeUISampleModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
};

// InterchangeUISample.cpp
#include "InterchangeUISample.h"
#include "InterchangePipelineConfigurationGeneric.h"
#include "InterchangeSourceData.h"
#include "InterchangeBaseNodeContainer.h"
#include "InterchangeManager.h" // 需要 Interchange 核心模块

void FInterchangeUISampleModule::StartupModule()
{
    // 模拟导入触发
    UInterchangeSourceData* SourceData = UInterchangeSourceData::CreateSourceData(TEXT("D:/test.fbx"));
    if (!SourceData) return;

    UInterchangeBaseNodeContainer* NodeContainer = NewObject<UInterchangeBaseNodeContainer>();

    // 创建管道配置对话框参数
    TArray<FInterchangeStackInfo> Stacks;
    // ... 填充栈信息（通常由 InterchangeImportHandler 提供）
    TArray<UInterchangePipelineBase*> OutPipelines;

    UInterchangePipelineConfigurationGeneric* Config = NewObject<UInterchangePipelineConfigurationGeneric>();
    FPipelineConfigurationDialogParams Params;
    Params.SourceData = SourceData;
    Params.bSceneImport = false;
    Params.bReimport = false;
    Params.PipelineStacks = Stacks;
    Params.OutPipelines = &OutPipelines;
    Params.BaseNodeContainer = NodeContainer;

    // 显示对话框（模态）
    EInterchangePipelineConfigurationDialogResult Result = Config->ShowPipelineDialog_Internal(Params);
    if (Result == EInterchangePipelineConfigurationDialogResult::Import)
    {
        // 使用 OutPipelines 执行实际导入
    }
}

IMPLEMENT_MODULE(FInterchangeUISampleModule, InterchangeUISample);
```

**编译要求**：该模块的 `Build.cs` 必须依赖 `InterchangeCore`、`InterchangeEngine`、`InterchangePipelines`，以及编辑器模块 `PropertyEditor`、`EditorStyle`。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `InterchangeCore` | Interchange 核心节点容器和数据模型 |
| `InterchangePipelines` | 管道基类及其执行逻辑 |
| `InterchangeEngine` | 高层导入管理器和源数据处理 |
| `InterchangeDispatcher` | 翻译器及工厂后端调度 |
| `GLTFCore` | glTF 管道自定义细节（`FInterchangeGLTFPipelineSettingsCustomization`） |
| `MaterialX` | MaterialX 管道自定义细节（`FInterchangeMaterialXPipelineSettingsCustomization`） |
| `ToolWidgets` | 高级 Slate 控件（如底部面板、筛选框） |
| `ApplicationCore` | 窗口和输入事件支持 |
| `AssetTools` | 注册资产类型操作 (FAssetTypeActions) |
| `BlueprintGraph` | 蓝图管道工厂（`UInterchangeBlueprintPipelineBaseFactory`） |

**注意**：以上依赖中，`InterchangeCore`、`InterchangePipelines`、`InterchangeEngine`、`InterchangeDispatcher` 是 Interchange 生态特有的模块；`ToolWidgets`、`ApplicationCore`、`AssetTools`、`BlueprintGraph` 属于编辑器不常见依赖，故列出。常见核心模块（Core, CoreUObject, Engine, Slate, SlateCore, UMG, InputCore, UnrealEd, PropertyEditor）不再重复。

## 维护状态

### 近期更新

- 2025-10-02 `35b266d6` — [Interchange UI] - Add separator section headings in the Import Dialog details view panel settings dialog
- 2025-09-24 `d2b213b6` — Interchange - Import performance improvement attempt
- 2025-09-24 `c5a21eff` — [BUGFIX][Interchange] FBX Python Level Import Test Failing
- 2025-09-23 `dcd0cb0d` — Tentatively fixed crash reported by users when closing import dialog
- 2025-09-23 `24638fbb` — [Interchange] Temp fix for Interchange Logging

### 维护评价

该模块创建于 2025 年 9 月，属于非常新的功能。近期更新频繁（几乎每天都有提交），内容涵盖 UI 增强、性能优化和 Bug 修复。当前处于**活跃维护**状态。

- **优点**：与 Interchange 框架同步迭代，修复及时，UI 细节不断改进。
- **注意事项**：由于模块极新，API 可能仍会变化，使用前建议锁定引擎版本。
- **推荐使用**：✅ 强烈推荐，特别适合需要可视化导入管道管理的项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Editor/Source/Pipelines)
- [官方文档（Interchange 概述）](https://docs.unrealengine.com/5.4/en-US/interchange-framework-in-unreal-engine/)
- [测试用例（模块内测试）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Editor/Tests)