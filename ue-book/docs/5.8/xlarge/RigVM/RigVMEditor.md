# RigVM

> Provides frontend and backend for the RigVM visual programming language and runtime（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 骨架虚拟机 |
| 分类 | Misc |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（Slate 样式资源） |
| 模块 | `RigVM` (Runtime), `RigVMDeveloper` (Runtime), `RigVMEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2023-03-28 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/RigVM) | |

## 用途

RigVM 是 Unreal Engine 的**骨架虚拟机（Rig Virtual Machine）**插件，为 Control Rig 等动画系统提供底层的**可视化编程语言前端和运行时后端**。

**核心问题**：Control Rig 需要一种高效、可序列化、可调试的图形化编程方式来驱动骨骼动画、物理模拟等 rig 操作。RigVM 就是这套基础设施——它定义了节点图的模型（Graph/Node/Pin）、编译器（将图形编译为字节码指令）、执行栈（Runtime VM）、以及完整的编辑器 UI。

**为什么独立存在**：RigVM 从 Engine 模块迁出为独立插件（2023-03-28），使得 Control Rig、Animation Blueprint 等系统可以共享同一套 VM 基础设施，同时允许独立迭代。它不仅仅是 Control Rig 的内部实现——它是 UE 的**通用 rig 可视化编程平台**。

## 使用场景

- 你在做角色骨骼动画（Control Rig）→ RigVM 是 Control Rig 的底层 VM 引擎
- 你需要自定义 rig 节点和函数库 → 用 RigVM 的节点图系统定义
- 你需要在编辑器中可视化调试 rig 执行 → 用 RigVMEditor 的 Execution Stack 视图
- 你需要跨蓝图搜索 rig 节点引用 → 用 Find-in-Blueprints 功能
- 你在开发基于 rig 的程序化动画工具 → RigVM 提供完整的前后端框架

## 蓝图用法

RigVMEditor 模块提供了 `URigVMEditorBlueprintLibrary` 工具类，包含以下可蓝图调用的函数：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RecompileVM` | 强制重新编译指定 RigVM 蓝图 | `URigVMEditorBlueprintLibrary` |
| `RecompileVMIfRequired` | 仅在需要时重新编译 | `URigVMEditorBlueprintLibrary` |
| `RequestAutoVMRecompilation` | 请求自动重新编译 | `URigVMEditorBlueprintLibrary` |
| `GetModel` | 获取蓝图的 RigVM 图模型对象 | `URigVMEditorBlueprintLibrary` |
| `GetController` | 获取蓝图的 RigVM 控制器对象 | `URigVMEditorBlueprintLibrary` |
| `LoadAssets` | 加载所有 RigVM 蓝图资产 | `URigVMEditorBlueprintLibrary` |
| `LoadAssetsByClass` | 按类加载 RigVM 蓝图资产 | `URigVMEditorBlueprintLibrary` |
| `LoadAssetsWithBlueprintFilter` | 使用蓝图过滤器加载资产 | `URigVMEditorBlueprintLibrary` |
| `LoadAssetsWithAssetDataFilter` | 使用资产数据过滤器加载资产 | `URigVMEditorBlueprintLibrary` |
| `LoadAssetsWithNodeFilter` | 使用节点过滤器加载资产 | `URigVMEditorBlueprintLibrary` |
| `RenderRigVMSubjectToPNG` | 将 rig VM 主体渲染为 PNG 图片 | `URigVMEditorBlueprintLibrary` |
| `RenderRigVMTemplateToPNG` | 将 rig VM 模板渲染为 PNG 图片 | `URigVMEditorBlueprintLibrary` |

### 资产过滤器委托

蓝图中可以绑定以下动态委托来自定义加载行为：

| 委托类型 | 用途 |
|---|---|
| `FRigVMAssetDataFilterDynamic` | 过滤 FAssetData |
| `FRigVMBlueprintFilterDynamic` | 过滤 URigVMBlueprint 和加载日志 |
| `FRigVMNodeFilterDynamic` | 过滤 URigVMBlueprint 中的节点 |

## C++ 用法

### 头文件引入

```cpp
#include "RigVMEditorModule.h"        // 编辑器模块
#include "RigVMEditorBlueprintLibrary.h" // 蓝图库工具
#include "RigVMEditor.h"              // 编辑器核心接口
```

### 基本用法

#### 获取编辑器模块

```cpp
// 来源: Public/RigVMEditorModule.h
// 获取 RigVM 编辑器模块实例
IRigVMEditorModule& EditorModule = IRigVMEditorModule::Get();

// 或获取完整实现
FRigVMEditorModule& Module = FRigVMEditorModule::Get();
```

#### 编译 RigVM 蓝图

```cpp
// 来源: Public/RigVMEditorBlueprintLibrary.h
// 强制重新编译
URigVMEditorBlueprintLibrary::RecompileVM(MyRigVMBlueprint);

// 仅在需要时编译（更高效）
URigVMEditorBlueprintLibrary::RecompileVMIfRequired(MyRigVMBlueprint);
```

#### 获取图模型和控制器

```cpp
// 来源: Public/RigVMEditorBlueprintLibrary.h
// 获取 RigVM 图模型
URigVMGraph* Model = URigVMEditorBlueprintLibrary::GetModel(MyRigVMBlueprint);

// 获取 RigVM 控制器（用于修改图）
URigVMController* Controller = URigVMEditorBlueprintLibrary::GetController(MyRigVMBlueprint);
```

#### 加载和过滤 RigVM 资产

```cpp
// 来源: Public/RigVMEditorBlueprintLibrary.h
// 加载所有 RigVM 蓝图
TArray<URigVMBlueprint*> AllAssets = URigVMEditorBlueprintLibrary::LoadAssets();

// 使用 C++ 过滤器加载
FRigVMNodeFilter NodeFilter;
NodeFilter.BindLambda([](const URigVMBlueprint* InBlueprint, const URigVMNode* InNode) -> bool
{
    // 自定义过滤逻辑
    return InNode->GetFName() == FName("MySpecialNode");
});
TArray<URigVMBlueprint*> FilteredAssets = 
    URigVMEditorBlueprintLibrary::LoadAssetsWithNodeFilter(
        URigVMBlueprint::StaticClass(), NodeFilter);
```

### 进阶用法

#### 使用编译管理器批量编译

```cpp
// 来源: Private/Editor/Kismet/RigVMBlueprintCompilationManager.h
// 初始化编译管理器
FRigVMBlueprintCompilationManager::Initialize();

// 将蓝图加入编译队列
FRigVMBlueprintCompilationManager::QueueForCompilation(MyBlueprint1);
FRigVMBlueprintCompilationManager::QueueForCompilation(MyBlueprint2);

// 批量刷新编译队列（比逐个编译更高效）
FRigVMBlueprintCompilationManager::FlushCompilationQueueAndReinstance();

// 或者同步编译单个蓝图
FRigVMBPCompileRequest Request(MyBlueprint, EBlueprintCompileOptions::None, nullptr);
FRigVMBlueprintCompilationManager::CompileSynchronously(Request);

// 注册自定义编译器扩展
FRigVMBlueprintCompilationManager::RegisterCompilerExtension(
    MyBlueprintType, MyCompilerExtension);
```

#### 使用节点注册表追踪编辑器节点

```cpp
// 来源: Internal/Editor/RigVMEdGraphNodeRegistry.h
// 创建或获取节点注册表（追踪特定类型的 EdGraph 节点）
using namespace UE::RigVMEditor;
TSharedRef<FRigVMEdGraphNodeRegistry> Registry = 
    FRigVMEdGraphNodeRegistry::GetOrCreateRegistry(
        MyRigVMAssetInterface, 
        URigVMFunctionReferenceNode::StaticClass());

// 监听注册表更新
Registry->OnPostRegistryUpdated.AddLambda([Registry]()
{
    // 获取已连接和未连接的节点
    const auto& Connected = Registry->GetConnectedEdGrapNodes();
    const auto& Disconnected = Registry->GetDisconnectedEdGrapNodes();
    
    // 处理节点变化...
});
```

#### 查找蓝图内引用

```cpp
// 来源: Public/Editor/RigVMFindReferences.h
// 构建搜索结果
FRigVMFindResultPtr Result = MakeShared<FRigVMFindReferencesGraphNode>(MyRigVMAsset);

// 在 C++ 中触发节点引用查找
UE::RigVMEditor::FRigVMEditorFindNodeReferencesParams Params(
    MyRigVMAsset, EdGraphNode, bSearchInAllBlueprints);
FRigVMEditorModule::GetOnRequestFindNodeReferences().Broadcast(Params);
```

#### 使用 Details View 包装对象

```cpp
// 来源: Public/Editor/RigVMDetailsViewWrapperObject.h
// 为自定义结构体创建属性编辑器包装
URigVMDetailsViewWrapperObject* Wrapper = 
    URigVMDetailsViewWrapperObject::MakeInstance(
        WrapperObjectClass, Outer, MyStruct, StructMemory, Subject);

// 读取包装对象内容
TMyStruct Value = Wrapper->GetContent<TMyStruct>();

// 修改后设置回
Wrapper->SetContent(NewValue);
```

## Demo 示例

### 最小 RigVM 编辑器交互示例

```cpp
// MyRigVMHelper.h
#pragma once
#include "CoreMinimal.h"

class URigVMBlueprint;
class URigVMGraph;
class URigVMController;

class FMyRigVMHelper
{
public:
    /** 编译指定的 RigVM 蓝图 */
    static void CompileBlueprint(URigVMBlueprint* InBlueprint);
    
    /** 向图中添加一个新节点 */
    static void AddNodeToGraph(URigVMBlueprint* InBlueprint, 
        const FName& InNodeTemplate, const FVector2D& InPosition);
    
    /** 获取图中所有节点名称 */
    static TArray<FString> GetAllNodeNames(URigVMBlueprint* InBlueprint);
};
```

```cpp
// MyRigVMHelper.cpp
#include "MyRigVMHelper.h"
#include "RigVMEditorBlueprintLibrary.h"
#include "RigVMBlueprint.h"
#include "RigVMGraph.h"
#include "RigVMController.h"
#include "RigVMNode.h"

void FMyRigVMHelper::CompileBlueprint(URigVMBlueprint* InBlueprint)
{
    if (!InBlueprint)
    {
        return;
    }
    URigVMEditorBlueprintLibrary::RecompileVM(InBlueprint);
}

void FMyRigVMHelper::AddNodeToGraph(URigVMBlueprint* InBlueprint,
    const FName& InNodeTemplate, const FVector2D& InPosition)
{
    if (!InBlueprint)
    {
        return;
    }
    
    URigVMGraph* Model = URigVMEditorBlueprintLibrary::GetModel(InBlueprint);
    URigVMController* Controller = URigVMEditorBlueprintLibrary::GetController(InBlueprint);
    
    if (!Model || !Controller)
    {
        return;
    }
    
    // 通过控制器在图中添加节点
    // 具体的节点模板名称取决于你的 rig 系统
    Controller->AddNode(InNodeTemplate, InPosition);
}

TArray<FString> FMyRigVMHelper::GetAllNodeNames(URigVMBlueprint* InBlueprint)
{
    TArray<FString> NodeNames;
    
    if (!InBlueprint)
    {
        return NodeNames;
    }
    
    URigVMGraph* Model = URigVMEditorBlueprintLibrary::GetModel(InBlueprint);
    if (!Model)
    {
        return NodeNames;
    }
    
    for (URigVMNode* Node : Model->GetNodes())
    {
        if (Node)
        {
            NodeNames.Add(Node->GetFName().ToString());
        }
    }
    
    return NodeNames;
}
```

## 模块依赖

RigVMEditor 模块依赖 Kismet，但作为使用者，你通常不需要直接依赖 Kismet。以下列出该插件**独特**的、对使用者有意义的依赖：

| 模块 | 用途 |
|---|---|
| `RigVM` | 核心 VM 运行时（图模型、编译器、执行栈） |
| `RigVMDeveloper` | 开发者工具（图控制器、节点工厂、蓝图扩展） |
| `RigVMEditor` | 编辑器 UI（图形编辑器、属性面板、搜索系统） |

> 注意：如果只需要运行时 rig 执行（如游戏中），只需依赖 `RigVM` 模块。编辑器功能需要 `RigVMEditor`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `dfee5052` | Control Rig: Fix missing dependency in ControlRigModules | 修复 ControlRig 模块缺失依赖 |
| 2026-05-22 | `e51b24ac` | Cherry-picking fix CL from Sara Schvartzman: | 从开发分支挑选修复提交 |
| 2026-05-21 | `fee6a0dc` | Control Rig: Fix renaming a variable in some cases leaves a duplicate | 修复变量重命名后残留重复项的问题 |
| 2026-05-18 | `5d1db13f` | Fix crash when debug pins are orphaned | 修复调试引脚孤立时的崩溃 |
| 2026-05-15 | `0b718514` | Control RIg: Defensive fix when function of a unit struct is nullptr | 防御性修复 unit struct 函数为空时的问题 |

### 维护评价

**活跃维护** — RigVM 作为 Control Rig 的核心基础设施，由 Epic Games 动画团队持续维护。近期更新集中在 bug 修复和稳定性改进，包括崩溃修复、重命名问题修复等。作为 UE5 动画系统的关键组件，该插件得到了长期且稳定的维护支持。

- ✅ 仍在活跃维护（最近一周有更新）
- ✅ 核心功能稳定，无已知重大限制
- ✅ **强烈推荐使用** — 如果你在使用 Control Rig 或任何 rig 相关功能，RigVM 是不可或缺的基础设施
- ⚠️ 这是一个大型底层框架插件（528 个源文件），通常由 Epic 内部团队和 Control Rig 插件使用，普通项目很少直接交互

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/RigVM)
- 官方文档（.uplugin 中未提供 DocsURL）
- [Control Rig 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Plugins/Animation/ControlRig)（RigVM 的主要使用者）