# UAF Anim Graph

> Framework for defining animation graphs.

| 属性 | 值 |
|---|---|
| 中文名 | UAF 动画图 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、动画图模板） |
| 模块 | `UAFAnimGraph` (Runtime), `UAFAnimGraphEditor` (Runtime), `UAFAnimGraphTestSuite` (Runtime), `UAFAnimGraphUncookedOnly` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-29 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFAnimGraph) | |

## 用途

UAF Anim Graph 是一个用于定义、编辑和调试动画图的实验性框架。它基于 **特质（Trait）** 体系，允许用户通过组合和配置特质节点来构建动画逻辑，而非传统的蓝图节点连接。该插件提供了配套的编辑器工具（包括对象面板、特质编辑器、图形视图和回放调试器），旨在提供比标准动画蓝图更灵活、更模块化的动画定义方式。

## 使用场景

- 你需要创建高度可定制的动画图表，希望通过组件化的“特质”而非固定节点来组合行为。
- 你希望在编辑器中可视化管理动画图的执行流程，并能进行运行时调试（配合 Rewind Debugger 回放）。
- 你正在构建自定义动画系统，并希望利用 UAF 框架的图结构和评估机制。

## 蓝图用法

本插件（`UAFAnimGraphEditor`）主要提供编辑器扩展，不包含直接对蓝图公开的 `UFUNCTION` 蓝图可调用节点。运行时模块 `UAFAnimGraph` 可能包含可用于蓝图调用的函数，但未纳入此文档范围。

## C++ 用法

### 头文件引入

```cpp
#include "Graph/AnimNextAnimationGraphFactory.h" // 工厂类
#include "Graph/AnimNextAnimationGraphAssetDefinition.h" // 资产定义
#include "Graph/AnimNextGraphPanelNodeFactory.h" // 自定义节点工厂
#include "Graph/AnimNextGraphPanelPinFactory.h" // 自定义引脚工厂
#include "Graph/STraitEditorView.h" // 特质编辑器
#include "Graph/STraitHandlePin.h" // 特质柄引脚
```

### 基本用法

**1. 注册自定义资产工厂**

创建 `UAnimNextAnimationGraphFactory` 的派生类，并将其注册到编辑器模块的启动逻辑中。

```cpp
// 在模块 StartupModule 中注册
UFactory* Factory = NewObject<UAnimNextAnimationGraphFactory>();
FAssetToolsModule::GetModule().Get().RegisterAssetTypeActions(MakeShareable(new FAssetTypeActions_AnimNextAnimationGraph(Factory)));
```

*（源自：`AnimNextAnimationGraphFactory.h`）*

**2. 注册资产定义（Asset Definition）**

使用 `UAssetDefinition_AnimNextAnimationGraph`（或自己的子类）来定义资源的显示名称、图标、打开方式等：

```cpp
// 在模块 StartupModule 中
auto AssetDefinition = MakeShared<FAssetTypeActions_AnimNextAnimationGraph>();
FAssetToolsModule::GetModule().Get().RegisterAssetTypeActions(AssetDefinition);
```

*（源自：`AnimNextAnimationGraphAssetDefinition.h`）*

**3. 注入自定义节点/引脚外观**

通过 `FAnimNextGraphPanelNodeFactory` 和 `FAnimNextGraphPanelPinFactory` 替换特定节点的 Slate 图形：

```cpp
// 注册节点工厂
auto NodeFactory = MakeShared<FAnimNextGraphPanelNodeFactory>();
FEdGraphUtilities::RegisterVisualNodeFactory(NodeFactory);

// 注册引脚工厂
auto PinFactory = MakeShared<FAnimNextGraphPanelPinFactory>();
FEdGraphUtilities::RegisterVisualPinFactory(PinFactory);
```

*（源自：`AnimNextGraphPanelNodeFactory.h`, `AnimNextGraphPanelPinFactory.h`）*

**4. 集成特质编辑器**

为工作区编辑器添加特质编辑标签页，通过 `FTraitEditorTabSummoner` 创建 `STraitEditorView` 实例：

```cpp
// 在工作区编辑器初始化时
TSharedPtr<FTraitEditorTabSummoner> TabSummoner = MakeShared<FTraitEditorTabSummoner>(HostingApp);
HostingApp->RegisterTabSpawner(TabSummoner->GetIdentifier(), TabSummoner);
```

*（源自：`TraitEditorTabSummoner.h`, `STraitEditorView.h`）*

**5. 自定义细节面板**

为特定的结构体或对象定制属性面板，例如 `FAnimNextFactoryParamsDetails` 用于工厂参数，`FAnimNextGraphDetails` 用于图属性：

```cpp
// 注册结构体自定义
FPropertyEditorModule& PropertyModule = FModuleManager::LoadModuleChecked<FPropertyEditorModule>("PropertyEditor");
PropertyModule.RegisterCustomPropertyTypeLayout(
    "AnimNextFactoryParams",
    FOnGetPropertyTypeCustomizationInstance::CreateStatic(&FAnimNextFactoryParamsDetails::MakeInstance)
);
```

*（源自：`Factory/AnimNextFactoryParamsDetails.h`）*

### 进阶用法

结合 Rewind Debugger 为 UAF 动画图提供运行时调试支持。需要实现 `IRewindDebuggerTrackCreator` 并注册：

```cpp
// 实现 FEvaluationProgramTrackCreator，在编辑器模块初始化时注册
RewindDebugger::RegisterTrackCreator(MakeShared<FEvaluationProgramTrackCreator>());
```

通过 `FAnimNextAnimGraphAnalyzer` 解析追踪数据并提供给 `FAnimNextAnimGraphProvider`，在回放时显示评估程序信息。

*（源自：`RewindDebugger/AnimNextAnimGraphAnalyzer.h`, `RewindDebugger/EvaluationProgramTrack.h`）*

## Demo 示例

以下展示如何在插件模块中注册一个资产工厂和资产定义，使编辑器能够创建和打开 UAF 动画图资产。

```cpp
// MyAnimNextEditorModule.h
#pragma once
#include "Modules/ModuleInterface.h"

class FMyAnimNextEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};

// MyAnimNextEditorModule.cpp
#include "MyAnimNextEditorModule.h"
#include "AssetToolsModule.h"
#include "Graph/AnimNextAnimationGraphFactory.h"
#include "Graph/AnimNextAnimationGraphAssetDefinition.h"

#define LOCTEXT_NAMESPACE "MyAnimNextEditorModule"

void FMyAnimNextEditorModule::StartupModule()
{
    // 注册资产类型动作
    IAssetTools& AssetTools = FAssetToolsModule::GetModule().Get();
    EAssetTypeCategories::Type Category = AssetTools.RegisterAdvancedAssetCategory(FName(TEXT("Animation")), LOCTEXT("AnimationCategory", "Animation"));
    
    auto Factory = NewObject<UAnimNextAnimationGraphFactory>();
    TSharedPtr<FAssetTypeActions_AnimNextAnimationGraph> Actions = MakeShared<FAssetTypeActions_AnimNextAnimationGraph>();
    AssetTools.RegisterAssetTypeActions(Actions);
}

void FMyAnimNextEditorModule::ShutdownModule()
{
    // 取消注册（防止重复注册）
    if (FAssetToolsModule::IsModuleLoaded())
    {
        FAssetToolsModule::GetModule().Get().UnregisterAssetTypeActions(Actions.ToSharedRef());
    }
}

#undef LOCTEXT_NAMESPACE
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `UAFAnimGraph` | 核心运行时模块，提供图数据结构、节点基类和评估执行 |
| `Workspace` | 工作区编辑器框架，用于托管动画图编辑窗口 |
| `AssetDefinition` | 资产注册及右键菜单、属性面板集成 |
| `RigVM` | 节点执行逻辑的虚拟机支持 |
| `TraitCore` | 特质系统核心，定义特质、接口及组合规则 |
| `RewindDebugger` | 回放调试器框架，用于运行时查看图评估程序 |
| `PropertyEditor` | 细节面板定制化，属性布局自定义 |

## 维护状态

### 近期更新

- 2025-10-01 `6f23619b` — 将 UEdGraphSchema 资产引用过滤逻辑移动至各实现中
- 2025-09-03 `bb48edd8` — 修复编辑器退出时无效内存访问
- 2025-09-03 `bc59af4e` — 修复在旧版 UAF 内容上打开右键菜单时崩溃
- 2025-09-02 `78089693` — 为 UAF 姿势评估添加范围命名事件
- 2025-08-29 `3663a91d` — 修复 UAF RigVM 重写变量资产持久性问题

### 维护评价

该插件创建于 2025 年 8 月，至今约 2 个月，仍处于实验性阶段。最近的提交集中在 Bug 修复和功能改进上，社区维护活跃。由于插件较新，暂未发现稳定版本常见限制。但作为实验性插件，API 可能在未来发生较大变动，不建议在生产项目中仅依赖此框架，但可用于技术预览和原型设计。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFAnimGraph)
- [官方文档](https://docs.unrealengine.com/)（暂未提供专用文档）