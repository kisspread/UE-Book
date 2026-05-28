# Property Access Node

> Blueprint node that allows access to properties via a property path（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 属性访问节点 |
| 分类 | Blueprints |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `PropertyAccessNode` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2020-09-01 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/PropertyAccessNode) | |

## 用途

本插件提供了一个强大的蓝图节点 `UK2Node_PropertyAccess`，它允许用户在蓝图编辑器中通过直观的“属性路径”（例如 `PlayerController.Character.Movement.MaxWalkSpeed`）来动态访问对象的属性值，而无需在蓝图中显式地拉取每一个中间对象的引用。其核心价值在于简化复杂属性链的访问，使蓝图更加清晰、易维护，并特别适用于需要在不同对象或上下文中重用相同属性访问逻辑的场景。它能解析路径，获取最终属性的类型和值，并能在编译时进行路径有效性检查和上下文绑定。

## 使用场景

- **动态属性访问**：当你在蓝图中需要根据名称字符串或逻辑路径（例如，从配置表读取的路径）来访问一个对象的属性时。
- **简化复杂属性获取**：避免在蓝图中连续拖拽多个 `Get` 节点来获取嵌套很深的属性（如 `Actor -> GetComponentByClass(SomeClass) -> GetSomeProperty`）。
- **动画蓝图与属性驱动**：特别适用于动画蓝图（AnimBP），可以方便地从动画图或状态机中访问角色蓝图的属性，作为动画变量或条件判断的来源。
- **数据驱动逻辑**：当你的游戏逻辑需要根据外部数据（如数据表、配置文件）中指定的属性路径来动态读取或设置值时。

## 蓝图用法

此插件主要提供了一个特殊的蓝图节点，其行为和外观类似于一个变量节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Property Access (Get)` | 通过路径访问对象属性并返回其值。节点会显示解析后的路径文本，并有一个输出引脚（名为 `Value`）输出属性值。 | `UK2Node_PropertyAccess` |
| `Property Access (Set)` | （理论上可通过路径设置属性，但核心节点主要设计为纯数据访问，`Set` 功能可能需要其他上下文支持） | `UK2Node_PropertyAccess` |
| `Get Text Path` | 获取当前属性访问节点配置的、用于显示的文本路径。 | `UK2Node_PropertyAccess` |
| `Get Resolved Pin Type` | 获取属性路径解析成功后，最终叶子属性对应的引脚类型（例如 `Float`, `Vector`, `Object Reference` 等）。 | `UK2Node_PropertyAccess` |

### 使用示例（蓝图描述）

1.  **基础访问**：
    *   在蓝图图表中右键，从菜单搜索 “Property Access” 或 “属性访问” 来放置该节点。
    *   节点初始状态可能有一个可编辑的路径字段。你可以直接输入如 `Self.ActorLocation.X` 或通过节点上下文菜单（右键节点）选择“绑定到属性…”来从对象树中选取。
    *   节点的 `Value` 输出引脚将提供该路径指向的最终属性的值（例如，一个 `Float` 值表示 X 坐标）。你可以将此引脚连接到其他节点（如 `Print String`）。

2.  **上下文指定**：
    *   该节点通常需要知道从哪个对象开始解析路径。在动画蓝图中，它可能默认关联到拥有该动画蓝图的角色。在普通蓝图中，你可能需要将上下文对象（如 `Self`）拖拽到节点上或通过其他方式指定。
    *   节点支持设置一个 `ContextId`，用于在编译时与特定上下文（如动画通知、状态机）关联，确保属性解析在正确的作用域内进行。

3.  **路径解析与错误提示**：
    *   如果输入的路径无效（如类名错误、属性不存在），节点会在编译时报告错误。
    *   成功解析后，节点通常会以更友好的方式显示路径文本（如分段显示），便于阅读。

## C++ 用法

此插件的 C++ API 主要围绕 `UK2Node_PropertyAccess` 类，用于程序化创建或操作该节点。

### 头文件引入

```cpp
#include "K2Node_PropertyAccess.h"
```

### 基本用法

**来源文件**: `Source/PropertyAccessNode/Private/K2Node_PropertyAccess.h`

```cpp
// 在某个蓝图编辑器扩展或节点工厂中
UK2Node_PropertyAccess* CreatePropertyAccessNode(UEdGraph* Graph, const FVector2D& NodePosition)
{
    // 1. 创建节点实例
    UK2Node_PropertyAccess* PropertyAccessNode = NewObject<UK2Node_PropertyAccess>(Graph);
    Graph->AddNode(PropertyAccessNode, true, false);
    PropertyAccessNode->CreateNewGuid();
    PropertyAccessNode->PostPlacedNewNode();
    PropertyAccessNode->SetFlags(RF_Transactional);
    
    // 2. 设置节点位置
    PropertyAccessNode->NodePosX = NodePosition.X;
    PropertyAccessNode->NodePosY = NodePosition.Y;
    
    // 3. 设置属性路径
    // 方法一：使用字符串数组
    TArray<FString> Path;
    Path.Add(TEXT("PlayerController"));
    Path.Add(TEXT("Character"));
    Path.Add(TEXT("HealthComponent"));
    Path.Add(TEXT("CurrentHealth"));
    PropertyAccessNode->SetPath(Path);
    
    // 4. 尝试解析属性（通常会在编译时自动进行，但可手动触发查看结果）
    // PropertyAccessNode->ResolvePropertyAccess(); // 这是一个 const 函数，内部修改 mutable 缓存
    
    // 5. 可选：设置上下文ID
    // PropertyAccessNode->SetContextId(FName(TEXT("MyAnimNotifyContext")));
    
    return PropertyAccessNode;
}
```

### 进阶用法

**来源文件**: `Source/PropertyAccessNode/Private/K2Node_PropertyAccess.h` (Combine with blueprint compiler context)

```cpp
// 在蓝图编译器上下文中（例如，在 ExpandNode 中），可以检查或操作属性访问节点
void HandlePropertyAccessNodeExpansion(FKismetCompilerContext& CompilerContext, UK2Node_PropertyAccess* Node)
{
    // 检查路径是否已解析
    const FProperty* ResolvedProp = Node->GetResolvedProperty();
    if (ResolvedProp)
    {
        int32 ArrayIndex = Node->GetResolvedArrayIndex();
        const FEdGraphPinType& PinType = Node->GetResolvedPinType();
        
        // 根据解析出的类型和属性，执行自定义的编译逻辑
        // 例如，生成一个中间变量来存储这个属性的值
        if (PinType.PinCategory == UEdGraphSchema_K2::PC_Float)
        {
            // 生成用于存储浮点属性值的变量
            CompilerContext.CreateLocalVariableForTransient(Node->GetOutputPin(), Node->GetOutputPin()->PinName);
        }
    }
    
    // 检查编译上下文
    const FText& CompiledContext = Node->GetCompiledContext();
    if (!CompiledContext.IsEmpty())
    {
        UE_LOG(LogTemp, Log, TEXT("PropertyAccessNode compiled in context: %s"), *CompiledContext.ToString());
    }
}
```

## Demo 示例

一个最小的 C++ 示例，展示如何在插件或编辑器模块中程序化地创建和配置一个 `UK2Node_PropertyAccess` 节点。

**PropertyAccessNodeDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class UEdGraph;

class FPropertyAccessNodeDemo
{
public:
    /** 在给定的蓝图图表中创建一个预设好的属性访问节点 */
    static UK2Node_PropertyAccess* DemoCreateNode(UEdGraph* InGraph);
};
```

**PropertyAccessNodeDemo.cpp**
```cpp
#include "PropertyAccessNodeDemo.h"
#include "K2Node_PropertyAccess.h"
#include "EdGraph/EdGraph.h"

UK2Node_PropertyAccess* FPropertyAccessNodeDemo::DemoCreateNode(UEdGraph* InGraph)
{
    if (!InGraph) return nullptr;

    // 1. 创建节点
    UK2Node_PropertyAccess* NewNode = NewObject<UK2Node_PropertyAccess>(InGraph);
    InGraph->AddNode(NewNode, true, false);
    NewNode->CreateNewGuid();
    NewNode->PostPlacedNewNode();

    // 2. 设置位置
    NewNode->NodePosX = 400;
    NewNode->NodePosY = 200;

    // 3. 配置路径 (例如：获取自身的位置X值)
    TArray<FString> PathToSet;
    PathToSet.Add(TEXT("ActorLocation")); // 假设这是 WorldContextObject 的一个属性
    PathToSet.Add(TEXT("X"));
    NewNode->SetPath(MoveTemp(PathToSet));

    // 4. 节点现在已存在于图表中。当蓝图编译时，它会尝试解析路径 "ActorLocation.X"。
    // 如果路径有效，节点的引脚类型将被设置为 Float，并输出该值。

    return NewNode;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PropertyAccessEditor` | 提供属性访问路径的选择、编辑 UI 以及编译时路径解析的核心支持。这是本插件功能所必需的。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2024-02-14 | `f543d807` | PropertyAccessEditor: Added BindingChain to OnCanBindProperty. | 增强属性访问的绑定检查，提供更详细的绑定链信息。 |
| 2024-02-13 | `5b88270d` | Fix Lyra PIE property access issues caused by CL 31251549 | 修复特定情况下（如Lyra项目）进行PIE测试时属性访问失效的问题。 |
| 2024-02-07 | `c6b6d713` | Fix function renames not applying to property access nodes and compilation crashes post-rename | 修复了重命名函数后，属性访问节点未正确更新引用以及可能引发的编译器崩溃问题。 |
| 2023-07-31 | `060d5c9b` | GitHub #10551: Fix `PropertyAccess` Crash when used in child AnimBP | 修复了在子动画蓝图中使用属性访问节点时发生的崩溃问题。 |
| 2023-01-12 | `2f78497e` | [Engine/Plugins] | （通用引擎插件提交，可能包含底层兼容性更新）。 |

### 维护评价

**PropertyAccessNode** 自2020年创建以来，持续接收来自Epic的更新，近期（2023-2024年）的提交主要集中在**修复关键bug**（如崩溃、PIE功能失效、重命名后引用丢失）和**增强核心功能**（绑定链检查）。这表明该插件是**动画蓝图、Lyra等现代项目工作流中的重要组成部分**，因此得到了持续维护。虽然作为“UncookedOnly”编辑器/开发工具插件，它不直接影响运行时，但其稳定性对蓝图开发体验至关重要。从维护频率和内容看，它仍处于**活跃维护中**，且没有废弃标记。**推荐在需要通过路径动态访问属性的蓝图开发场景中使用此插件**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/PropertyAccessNode)
- [官方文档]() (插件本身未提供官方文档链接)
- [测试用例]() (在提供的插件目录结构中未发现专门的测试文件)