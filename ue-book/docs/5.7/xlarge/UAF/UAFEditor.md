# Unreal Animation Framework (UAF)

> Framework for defining functional data flow for animation systems

| 属性 | 值 |
|---|---|
| 中文名 | 动画框架 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑工作流资产） |
| 模块 | `UAF` (Runtime), `UAFEditor` (Runtime), `UAFTestSuite` (Runtime), `UAFUncookedOnly` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-25 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAF) | |

## 用途

UAF（Unreal Animation Framework）是 Epic Games 推出的下一代动画系统框架，旨在为动画系统定义**功能数据流**。它基于 RigVM 和 Workspace 架构，提供：

- **模块化动画逻辑**：通过“模块”（Module）组织动画行为，每个模块可包含变量、事件图、函数和特质（Trait）栈，形成可复用的动画片段。
- **声明式数据流**：使用可视化图表（Event Graph）与 RigVM 节点定义动画数据的驱动关系，替代传统蓝图/动画蓝图的部分功能。
- **编辑器工作流**：提供独立的 Workspace 编辑器用于管理模块、变量、函数和轨迹，支持查找/替换、编译结果查看、断点调试等高级编辑功能。
- **高性能运行时**：编译后的模块可在运行时高效执行，支持 LODPose、Locator 等机制实现跨对象引用。

**为什么存在？** UAF 是为了解决传统动画蓝图在复杂动画系统（如 AAA 游戏、交互式电影）中难以维护、扩展困难的问题，通过函数式数据流和模块化设计降低耦合、提升复用性，并提供更强大的编辑器工具链。

## 使用场景

- 你需要构建复杂的角色动画状态机（如混合、叠加、分层动画） → 使用 UAF Module 和 Trait 栈
- 你希望将动画逻辑拆分为独立、可复用的“模块” → 创建 UAF 系统（Module Asset）并编排变量与事件
- 你需要在动画运行时引用场景中的 Actor/Component → 使用 Locator（定位器）系统
- 你需要对动画变量进行全局查找/替换 → 使用 UAF 的 Find & Replace 工具
- 你正在开发新游戏的动画管线，并愿意使用实验性质的技术

## 蓝图用法

该编辑器模块（UAFEditor）主要提供编辑器扩展功能，不包含可直接在游戏运行时调用的蓝图节点。所有与 UAF 运行时交互的蓝图函数位于 `UAF` 运行时模块中（文档未提供）。但 UAF 编辑器资产（如 UAF 系统、变量、事件图）可以通过蓝图类进行创建和引用，例如使用 `UAnimNextModule` 及其子类。

如果你需要在蓝图中操作 UAF 模块，请参考运行时模块的 API。这里列出编辑器部分相关的蓝图类型：

| 蓝图类型 | 说明 | 所在类 |
|---|---|---|
| `UAnimNextWorkspaceFactory` | 在内容浏览器中创建 UAF 工作区资产的工厂，带 `BlueprintType` 标注 | `UAnimNextWorkspaceFactory` |

## C++ 用法

### 头文件引入

```cpp
#include "UAFEditor.h"          // 模块入口
#include "EditorUtils.h"        // 常用工具函数
#include "AnimNextEdGraphNodeCustomization.h" // 节点自定义
```

### 基本用法

**1. 获取并验证名称**
```cpp
#include "EditorUtils.h"

// Inside a UFactory::FactoryCreateNew or similar
UObject* Outermost = InParent; // your target package
FName ValidName = UE::UAF::Editor::FUtils::ValidateName(Outermost, Name.ToString());
// 如果名称无效，ValidateName 会返回修正后的名称
```
来源：`Source/UAFEditor/Private/EditorUtils.cpp`（推断）

**2. 注册自定义定位器片段编辑器**
```cpp
#include "IAnimNextEditorModule.h"
#include "Modules/ModuleManager.h"

void MyClass::RegisterLocator()
{
    IAnimNextEditorModule& EditorModule = FModuleManager::GetModuleChecked<IAnimNextEditorModule>("UAFEditor");
    EditorModule.RegisterLocatorFragmentEditorType("ActorLocator");
    // 注册后，UAF 资产中的定位器属性将显示 Actor 选择器
}
```
来源：`Source/UAFEditor/Private/AnimNextEditorModule.h`（`RegisterLocatorFragmentEditorType`）

**3. 实现自定义 Outliner Item 双击行为**
```cpp
#include "IWorkspaceOutlinerItemDetails.h"
#include "AnimNextAssetItemDetails.h"

// 继承 IWorkspaceOutlinerItemDetails 并实现 HandleDoubleClick
class FMyCustomItemDetails : public UE::Workspace::IWorkspaceOutlinerItemDetails
{
    virtual bool HandleDoubleClick(const FToolMenuContext& ToolMenuContext) const override
    {
        // 打开对应编辑器 tab
        return true;
    }
};
```
来源：`Source/UAFEditor/Internal/Common/AnimNextAssetItemDetails.h`

### 进阶用法

**在自定义资产工厂中创建 UAF Module**
```cpp
#include "Module/AnimNextModuleFactory.h"
#include "Module/AnimNextModule.h"

UAnimNextModule* CreateModule(UObject* InParent, FName InName, EObjectFlags Flags)
{
    UAnimNextModuleFactory* Factory = NewObject<UAnimNextModuleFactory>();
    Factory->ConfigureProperties(); // 打开资产类型选择对话框（可选）
    return Cast<UAnimNextModule>(Factory->FactoryCreateNew(
        UAnimNextModule::StaticClass(),
        InParent,
        InName,
        Flags,
        nullptr,
        GWarn
    ));
}
```
来源：`Source/UAFEditor/Internal/Module/AnimNextModuleFactory.h`

**使用 Find & Replace 替换变量引用**
```cpp
#include "AnimNextAssetFindReplaceVariables.h"

void ReplaceVariable(const FAssetData& InAssetData, const FAnimNextSoftVariableReference& OldRef, const FAnimNextSoftVariableReference& NewRef)
{
    UAnimNextAssetFindReplaceVariables* Processor = NewObject<UAnimNextAssetFindReplaceVariables>();
    Processor->SetFindReference(OldRef, SomeParamType);
    Processor->SetReplaceReference(NewRef);
    Processor->SetSearchScope(ESearchScope::Global);
    Processor->ReplaceInAsset(InAssetData);
}
```
来源：`Source/UAFEditor/Private/Common/AnimNextAssetFindReplaceVariables.h`

## Demo 示例

以下是一个最小 C++ 示例，演示如何在编辑器模块启动时注册一个自定义定位器编辑器，并创建一个 UAF Module 资产。

**MyUAFDemoModule.h**
```cpp
#pragma once
#include "Modules/ModuleInterface.h"
#include "Modules/ModuleManager.h"

class FMyUAFDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

**MyUAFDemoModule.cpp**
```cpp
#include "MyUAFDemoModule.h"
#include "IAnimNextEditorModule.h"
#include "Module/AnimNextModuleFactory.h"
#include "Module/AnimNextModule.h"
#include "AssetRegistry/AssetRegistryModule.h"

void FMyUAFDemoModule::StartupModule()
{
    // 注册自定义定位器片段
    if (IAnimNextEditorModule* EditorModule = FModuleManager::Get().GetModulePtr<IAnimNextEditorModule>("UAFEditor"))
    {
        EditorModule->RegisterLocatorFragmentEditorType("MyCustomLocator");
    }

    // 在 Content Browser 中创建一个 UAF Module 资产（示例）
    // 实际使用时你可能在 AssetFactory 中做此操作
    UPackage* Package = CreatePackage(nullptr, TEXT("/Game/MyAnimModule"));
    UAnimNextModule* Module = NewObject<UAnimNextModule>(
        Package,
        UAnimNextModule::StaticClass(),
        FName("MyAnimModule"),
        RF_Public | RF_Standalone
    );
    Package->MarkPackageDirty();
    FAssetRegistryModule::AssetCreated(Module);
}

void FMyUAFDemoModule::ShutdownModule()
{
    if (IAnimNextEditorModule* EditorModule = FModuleManager::Get().GetModulePtr<IAnimNextEditorModule>("UAFEditor"))
    {
        EditorModule->UnregisterLocatorFragmentEditorType("MyCustomLocator");
    }
}

IMPLEMENT_MODULE(FMyUAFDemoModule, MyUAFDemo);
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LiveCoding` | 支持 UAF 的热重载（UAF 和 UAFUncookedOnly 模块依赖） |
| `Workspace` | 提供 Workspace 编辑器框架（UAFEditor 间接依赖） |
| `RigVM` | 提供 RigVM 图表执行引擎（UAF 和 UAFEditor 依赖） |
| `UniversalObjectLocator` | 提供通用对象定位器系统（UAFEditor 用于 Locator 编辑） |

注：UAFEditor 模块还隐式依赖 `AnimNext`（UAF 运行时模块）、`AnimNextUncookedOnly`（未计入当前列表）、`Projects`、`DeveloperSettings` 等，此处仅列出独特依赖。

## 维护状态

### 近期更新

- 2025-10-02 `ef1c8b52` Fix double binding to IsEnabled（修复 IsEnabled 双击绑定）
- 2025-10-02 `f75459b5` Fix crash from selecting non-Actor derived blueprint to modify in UAF asset wizard（修复在 UAF 资产向导中选择非 Actor 派生蓝图时的崩溃）
- 2025-10-01 `6f23619b` Moved UEdGraphSchema asset reference filtering for drag and drop operations to their various implementations（将拖放操作的资产引用过滤移到各自的实现）
- 2025-09-30 `737f1f42` Crash fixes for LODPose（修复 LODPose 崩溃）
- 2025-09-25 `2f8943cd` Honor ShrinkByDefault in various existing array classes（尊重现有数组类中的 ShrinkByDefault）

### 维护评价

- **创建时间**：2025-09-25，不到一个月，属于新系统。
- **近期更新**：最近一周内有多次功能性修复（bug 修复、重构），更新频率高，说明团队活跃维护。
- **活跃状态**：非常活跃，几乎每天都有 commit，且内容涉及核心修复和重构。
- **已知问题**：存在崩溃和绑定问题，但正在快速修复。
- **推荐度**：由于是实验性插件且版本号为 0.1，仅适合在开发环境中尝试，不建议用于生产项目。但如果对新一代动画系统感兴趣，可以作为技术预览使用。

## 相关链接

- [源码（插件根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAF)
- [UAF 运行时模块头文件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAF/Source/UAF/Public)
- [UAF 编辑器模块头文件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAF/Source/UAFEditor/Public)（包含在 Internal 和 Private 下）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAF/Source/UAFTestSuite)