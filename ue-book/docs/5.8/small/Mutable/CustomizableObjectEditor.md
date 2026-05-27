# Mutable

> Mutable adds the tools and runtime to create customizable objects for your games.

| 属性 | 值 |
|---|---|
| 中文名 | 可定制对象系统 |
| 分类 | CustomizableObjects |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `MutableRuntime` (Runtime), `CustomizableObject` (Runtime), `MutableTools` (Runtime), `MutableValidation` (Runtime), `CustomizableObjectEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-05 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable) | |

## 用途

Mutable 是一个**基于节点图的运行时资产合成系统**，用于在运行时动态组合、修改和生成游戏资产（网格体、材质、纹理、骨骼网格体等）。

传统做法中，如果一个角色有 5 种头盔 × 5 种铠甲 × 5 种武器，美术需要手动制作 125 个完整模型。Mutable 的核心思想是：将这些部件的"组合规则"定义为一张**节点图（Customizable Object Graph）**，运行时根据参数选择，由 Mutable 虚拟机动态合成最终的网格体、材质和纹理。

**核心概念**：
- **Customizable Object（CO）**：定义可变体的资产，内部是一张节点图
- **Customizable Object Instance（COI）**：CO 的一个具体实例，持有当前参数值
- **Parameters（参数）**：运行时可调整的值（Int 枚举、Float 滑条、Bool、Color、Projector 等）
- **Mutable Model**：编译后生成的虚拟机程序，实例化时执行
- **Layout（布局）**：UV 空间的分区策略，决定纹理如何打包

## 使用场景

- **角色自定义系统**：玩家在角色创建界面中选择发型、肤色、装备组合 → 使用 CO 参数 + COI 实例
- **武器/装备外观变化**：同一把剑可更换刃部、护手、握柄部件 → 使用 Multi-Component CO
- **NPC 变体生成**：同一种族的 NPC 有不同的面容、体型、服饰组合 → 使用 CO 随机参数
- **数据驱动内容**：通过 DataTable 行切换大量预定义变体（皮肤、表情等）→ 使用 Table Node
- **LOD 自动优化**：Mutable 可自动为不同 LOD 层级生成简化的纹理布局
- **运行时贴花/投影**：在角色身上投影 Logo 或涂鸦 → 使用 Projector 参数

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `NewCustomizableObject` | 在指定包路径中创建新的可定制对象资产 | `UCustomizableObjectEditorFunctionLibrary` |
| `CompileCustomizableObjectSynchronously` | 同步编译可定制对象（已弃用，改用 `UCustomizableObject::Compile`） | `UCustomizableObjectEditorFunctionLibrary` |

> **注意**：Mutable 的主要运行时 API（创建实例、修改参数、更新实例等）在 `UCustomizableObject` 和 `UCustomizableObjectInstance` 类中，这两个类属于 `CustomizableObject` 模块（非 Editor 模块）。由于提供的源码文件聚焦于 Editor 模块，以下主要展示编辑器侧的蓝图用法。

### 编辑器蓝图用法

在 Editor Utility Blueprint 中，可以通过以下方式创建可定制对象：

1. **创建新的 CO**：
   - 调用 `NewCustomizableObject`，指定包路径（如 `/Game/Characters`）、资产名和父对象
   - 返回 `UCustomizableObject*`，之后可以在其中添加节点图

2. **编译 CO**：
   - 调用 `CompileCustomizableObjectSynchronously`，指定优化等级和纹理压缩模式
   - 返回 `ECustomizableObjectCompilationState`（None / InProgress / Completed / Failed）

### 使用示例（蓝图描述）

创建一个子可定制对象并附加到父对象的组节点：

1. 创建 `NewCustomizableObjectParameters` 结构体
2. 设置 `PackagePath` 为 `/Game/CO`
3. 设置 `AssetName` 为 `ChildHelmet`
4. 设置 `ParentObject` 为已有的父 CO 资产引用
5. 设置 `ParentGroupNode` 为父 CO 中目标 Group 节点的名称
6. 调用 `NewCustomizableObject` 节点
7. 对返回的 CO 调用 `CompileCustomizableObjectSynchronously`

## C++ 用法

### 头文件引入

```cpp
// CustomizableObjectEditor 模块
#include "CustomizableObjectEditorFunctionLibrary.h"

// 图遍历工具
#include "MuCOE/GraphTraversal.h"

// 节点基类
#include "MuCOE/Nodes/CustomizableObjectNode.h"

// 扩展数据编译接口
#include "MuCOE/ExtensionDataCompilerInterface.h"

// 编辑器模块接口
#include "MuCOE/ICustomizableObjectEditorModulePrivate.h"
```

### 基本用法

**查询 CO 的根对象**（图遍历）：

```cpp
// 来源: GraphTraversal.h
#include "MuCOE/GraphTraversal.h"

// 获取指定 CO 的完整图根对象
UCustomizableObject* RootObject = GraphTraversal::GetRootObject(ChildObject);
if (RootObject)
{
    UE_LOG(LogTemp, Log, TEXT("Root CO: %s"), *RootObject->GetName());
}

// 检查 CO 是否是根对象
bool bIsRoot = GraphTraversal::IsRootObject(*SomeObject);
```

**获取 CO 图中所有相关对象**：

```cpp
// 来源: GraphTraversal.h
TSet<UCustomizableObject*> AllObjects;
GraphTraversal::GetAllObjectsInGraph(RootObject, AllObjects);

for (UCustomizableObject* Obj : AllObjects)
{
    UE_LOG(LogTemp, Log, TEXT("Related CO: %s"), *Obj->GetName());
}
```

**查找图中根 Object 节点**：

```cpp
// 来源: GraphTraversal.h
UCustomizableObjectNodeObject* RootNode = GetRootNode(MyCustomizableObject);
if (RootNode)
{
    // RootNode->States 包含所有状态定义
    // RootNode->GetObjectName() 返回对象名称
}
```

**沿引脚追踪连接**：

```cpp
// 来源: GraphTraversal.h
// 跟踪输入引脚，跳过孤立引脚和路由节点
UEdGraphPin* ConnectedPin = FollowInputPin(MyInputPin);
if (ConnectedPin)
{
    UE_LOG(LogTemp, Log, TEXT("Connected to: %s"), 
        *ConnectedPin->GetOwningNode()->GetNodeTitle(ENodeTitleType::FullTitle).ToString());
}
```

**注册自定义扩展数据**：

```cpp
// 来源: ExtensionDataCompilerInterface.h
#include "MuCOE/ExtensionDataCompilerInterface.h"

// 在节点的 GenerateMutableNode 中使用
void MyNode::GenerateMutableNode(FMutableGraphGenerationContext& Context)
{
    FExtensionDataCompilerInterface ExtInterface(Context);
    
    // 注册扩展数据，bDuplicate=true 表示打包时复制
    UE::Mutable::Private::PASSTHROUGH_ID Id = 
        ExtInterface.MakeExtensionData(*MyDataObject, true /*bDuplicate*/);
    
    // 注册生成的节点用于编译追踪
    ExtInterface.AddGeneratedNode(this);
}
```

### 进阶用法

**访问编辑器模块的私有接口**（排队编译请求）：

```cpp
// 来源: ICustomizableObjectEditorModulePrivate.h
#include "MuCOE/ICustomizableObjectEditorModulePrivate.h"

ICustomizableObjectEditorModulePrivate& EditorModule = 
    ICustomizableObjectEditorModulePrivate::GetChecked();

// 排队编译请求
TSharedRef<FCompilationRequest> Request = MakeShared<FCompilationRequest>(/* ... */);
EditorModule.EnqueueCompileRequest(Request, false /*bForceRequest*/);

// 查询当前编译中的请求数量
int32 NumRequests = EditorModule.GetNumCompileRequests();

// 取消所有编译请求
EditorModule.CancelCompileRequests();
```

**检查编译是否过期**：

```cpp
// 来源: ICustomizableObjectEditorModule.h (通过 EditorModule)
ICustomizableObjectEditorModulePrivate& EditorModule = 
    ICustomizableObjectEditorModulePrivate::GetChecked();

TArray<FName> OutOfDatePackages;
TArray<FName> AddedPackages;
TArray<FName> RemovedPackages;
bool bVersionDiff = false;

bool bOutOfDate = EditorModule.IsCompilationOutOfDate(
    *MyCustomizableObject,
    false /*bSkipIndirectReferences*/,
    OutOfDatePackages,
    AddedPackages,
    RemovedPackages,
    bVersionDiff
);

if (bOutOfDate)
{
    UE_LOG(LogTemp, Warning, TEXT("CO is out of date! %d packages changed."), 
        OutOfDatePackages.Num());
}
```

**Bake（烘焙）可定制对象实例**：

```cpp
// 来源: CustomizableObjectInstanceBakingUtils.h
#include "MuCOE/CustomizableObjectInstanceBakingUtils.h"

// 配置烘焙设置
FBakingConfiguration Config;
// ... 设置烘焙选项

// 同步烘焙实例的所有资源到磁盘
TMap<UPackage*, const FResourceBakingData> SavedPackages;
bool bSuccess = BakeCustomizableObjectInstance(
    *MyInstance,
    Config,
    false /*bIsUnattendedExecution*/,
    SavedPackages
);

// 异步方式：先编译 CO，再更新实例，最后烘焙
ScheduleCOCompilationForBaking(
    *MyInstance,
    FCompileNativeDelegate::CreateLambda([](const FCompileCallbackParams& Params)
    {
        // 编译完成后触发实例更新
    })
);
```

**注册自定义外部引脚类型**：

```cpp
// 来源: ICustomizableObjectEditorModulePrivate.h
// 注册外部操作类型到编辑器
EditorModule.RegisterExternalOperation(MyOperationStruct);

// 获取注册的外部引脚类型
const TMap<FName, TStrongObjectPtr<const UScriptStruct>>& Types = 
    EditorModule.GetExternalPinTypes();

// 获取引脚颜色
const TMap<FName, FLinearColor>& Colors = EditorModule.GetExternalPinTypeColors();
```

## Demo 示例

以下演示如何在编辑器工具中查询 CO 图结构并创建子对象：

```cpp
// MyCOEditorHelper.h
#pragma once

#include "CoreMinimal.h"

class UCustomizableObject;
class UCustomizableObjectNodeObject;

class FMyCOEditorHelper
{
public:
    /** 分析 CO 图结构并打印层级信息 */
    static void AnalyzeCOGraph(UCustomizableObject* RootCO);

    /** 创建一个新的子 CO 并附加到父对象 */
    static UCustomizableObject* CreateChildCO(
        const FString& PackagePath,
        const FString& AssetName,
        UCustomizableObject* Parent,
        const FString& GroupName);

    /** 获取 CO 的所有状态名称 */
    static TArray<FString> GetAllStateNames(UCustomizableObject* CO);
};
```

```cpp
// MyCOEditorHelper.cpp
#include "MyCOEditorHelper.h"

#include "MuCOE/GraphTraversal.h"
#include "MuCOE/Nodes/CustomizableObjectNode.h"
#include "MuCOE/Nodes/CustomizableObjectNodeObject.h"
#include "MuCO/CustomizableObject.h"
#include "MuCO/CustomizableObjectPrivate.h"
#include "MuCOE/CustomizableObjectEditorFunctionLibrary.h"

void FMyCOEditorHelper::AnalyzeCOGraph(UCustomizableObject* RootCO)
{
    if (!RootCO) return;

    // 获取完整图中的所有 CO
    TSet<UCustomizableObject*> AllObjects;
    GraphTraversal::GetAllObjectsInGraph(RootCO, AllObjects);

    UE_LOG(LogTemp, Log, TEXT("CO Graph '%s' contains %d objects:"), 
        *RootCO->GetName(), AllObjects.Num());

    for (UCustomizableObject* Obj : AllObjects)
    {
        bool bIsRoot = GraphTraversal::IsRootObject(*Obj);
        UCustomizableObject* Root = GraphTraversal::GetRootObject(Obj);

        UE_LOG(LogTemp, Log, TEXT("  %s (Root: %s, TreeRoot: %s)"),
            *Obj->GetName(),
            bIsRoot ? TEXT("Yes") : TEXT("No"),
            Root ? *Root->GetName() : TEXT("None"));
    }

    // 获取根节点
    UCustomizableObjectNodeObject* RootNode = GetRootNode(RootCO);
    if (RootNode)
    {
        UE_LOG(LogTemp, Log, TEXT("Root Object Node: %s"), 
            *RootNode->GetObjectName());

        // 打印状态信息
        for (const FCustomizableObjectState& State : RootNode->States)
        {
            UE_LOG(LogTemp, Log, TEXT("  State: %s (Params: %d)"),
                *State.Name, State.RuntimeParameters.Num());
        }
    }
}

UCustomizableObject* FMyCOEditorHelper::CreateChildCO(
    const FString& PackagePath,
    const FString& AssetName,
    UCustomizableObject* Parent,
    const FString& GroupName)
{
    FNewCustomizableObjectParameters Params;
    Params.PackagePath = PackagePath;
    Params.AssetName = AssetName;
    Params.ParentObject = Parent;
    Params.ParentGroupNode = GroupName;

    return UCustomizableObjectEditorFunctionLibrary::NewCustomizableObject(Params);
}

TArray<FString> FMyCOEditorHelper::GetAllStateNames(UCustomizableObject* CO)
{
    TArray<FString> Names;
    if (!CO) return Names;

    UCustomizableObjectNodeObject* RootNode = GetRootNode(CO);
    if (RootNode)
    {
        for (const FCustomizableObjectState& State : RootNode->States)
        {
            Names.Add(State.Name);
        }
    }
    return Names;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DerivedDataCache` | Mutable 编译结果存储到派生数据缓存 |
| `MessageLog` | 编译过程中的日志和错误消息显示 |
| `GameplayTags` | 参数选项过滤（Gameplay Tag 驱动的参数选项） |

> 注：`CustomizableObject` 模块还依赖 `MutableRuntime` 和 `MutableTools`；`CustomizableObjectEditor` 模块依赖 `CustomizableObject` 和 `MutableTools`。这些是插件内部依赖，使用者不需要直接引用。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `70229bdc` | [Mutable] Fix duplicated Skeletal Mesh geometry if there is multiple SKM with the same name. | 修复同名多个骨骼网格体时几何体重复的问题 |
| 2026-05-26 | `2b0ca8bd` | [mutable] Fixed "Clip mesh with UV Mask" op not loading the appropriate mask mip. | 修复 UV 蒙版裁剪网格操作未加载正确 mip 层级 |
| 2026-05-26 | `06ea27d3` | [Mutable] Fix texture parameters using the wrong method to compute the LODBias. | 修复纹理参数使用错误方法计算 LODBias |
| 2026-05-26 | `e9c39661` | [Mutable] Allow more clothing asset types by using the ClothingAssetBase interface. | 通过 ClothingAssetBase 接口支持更多服装资产类型 |
| 2026-05-25 | `c8ce9ff7` | [Mutable] Fix possible data race when comparing PassthroughObjects. | 修复比较 PassthroughObjects 时可能的数据竞争 |

### 维护评价

- **活跃维护**：最近的提交集中在 2026 年 5 月，修复频率高（单日多次提交），表明插件处于**活跃维护**状态
- **成熟度**：2024 年 9 月从 Experimental 迁移到 Beta，版本号已达 1.8.0，核心架构稳定
- **代码规模**：1206 个源文件，包含完整的编辑器节点图系统、运行时合成引擎、UV 布局编辑器、性能分析器等
- **迭代质量**：近期提交均为 bug 修复（几何体重复、mip 加载、LODBias 计算、线程安全等），说明核心功能已完成，当前处于稳定打磨阶段
- **实验性标记**：`.uplugin` 中从 Experimental 移出但标记为 Beta，`IsBetaVersion` 可能为 true
- **推荐使用**：✅ 推荐用于需要角色/装备自定义的项目。作为 Beta 插件，核心功能完善，但需注意可能存在的边缘情况 bug

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable)
- [官方文档](https://github.com/anticto/Mutable-Documentation/wiki)（社区维护）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable)（测试文件位于插件目录内）