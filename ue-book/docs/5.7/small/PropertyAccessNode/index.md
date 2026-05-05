# Property Access Node

> Blueprint node that allows access to properties via a property path

| 属性 | 值 |
|---|---|
| 分类 | Blueprints |
| 默认启用 | true |
| 包含内容 | false |
| 模块 | PropertyAccessNode (UncookedOnly) |
| 创建时间 | 2020-09-01 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/PropertyAccessNode) | |

## 用途

Property Access Node 提供了一个蓝图节点 **Property Access**，让你通过 **属性路径（property path）** 来访问对象的属性值。它不是简单的 "Get Variable"，而是支持链式路径访问，例如 `Self > MeshComponent > RelativeRotation > Roll`。

这个 plugin 本质上是一个 **K2 自定义蓝图节点**（`UK2Node_PropertyAccess`），配合 Property Access Editor 提供的属性绑定 UI，让用户可以在蓝图中以可视化方式选择属性路径。它主要用于 **动画蓝图（Anim Blueprint）** 场景，在编译时通过 `UAnimBlueprintExtension_PropertyAccess` 将路径解析为高效的属性拷贝操作，并智能判断是否需要缓存变量（线程安全时直接内联访问，不安全时创建中间缓存变量）。

**为什么存在？** 传统蓝图要访问嵌套属性需要串联多个 "Get" 节点，而 Property Access Node 将整条路径封装成一个节点，简化了蓝图图谱的复杂度，同时在动画系统中可以利用 Property Access Library 进行批量编译优化。

## 使用场景

- 你在做动画蓝图，需要从角色的某个组件属性读取值来驱动动画参数 → 用 Property Access Node
- 你需要在蓝图中通过一条路径链式访问深层嵌套的属性（如 `Actor > CapsuleComponent > CapsuleHalfHeight`）→ 用 Property Access Node
- 你想在动画蓝图中以线程安全的方式高效读取属性，避免每帧都走蓝图 VM → Property Access Node 编译时会自动优化调用点

## 蓝图用法

这是一个 **纯节点（pure node）**，没有执行引脚，只有一个输出引脚 `Value`。它在蓝图编辑器中以变量样式显示（`DrawNodeAsVariable() == true`）。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Property Access` | 通过属性路径访问值，输出引脚类型随路径自动解析 | `UK2Node_PropertyAccess` |

### 使用方式

1. 在蓝图编辑器中右键搜索 **"Property Access"**（分类在 Variables 下）
2. 放置节点后，节点标题区域显示一个 **"Bind"** 按钮
3. 点击 Bind 按钮，弹出属性绑定下拉菜单，通过树形结构选择属性路径
4. 选择完成后，节点标题变为路径文本（如 `Self.RelativeRotation.Roll`），输出引脚自动变为对应类型
5. 右键节点可清除绑定（Remove Binding）

### 属性路径类型

- **属性路径**：如 `Self.ActorLocation` — 直接访问属性值
- **函数路径**：如 `Self.GetActorLocation()` — 调用纯函数（`BlueprintPure`，只有一个返回值）
- **数组元素**：支持指定数组索引访问特定元素

### 编译上下文显示

编译后，节点右下角会显示编译时分配的调用上下文（如 "Worker Thread Unbatched"），提示该属性访问在运行时的执行线程和方式。鼠标悬停可查看详细信息。

## C++ 用法

### 头文件引入

```cpp
#include "K2Node_PropertyAccess.h"
```

> 注意：这是一个 `UncookedOnly` 模块，仅在编辑器环境下可用，不可在打包后的运行时代码中使用。

### 基本用法

该 plugin 不暴露公共 C++ API 给外部模块使用。`UK2Node_PropertyAccess` 是一个蓝图图节点类，主要由蓝图编辑器内部使用。

核心操作是通过 `SetPath` / `ClearPath` / `GetPath` 管理属性路径：

```cpp
// 设置属性路径
TArray<FString> Path;
Path.Add(TEXT("Self"));
Path.Add(TEXT("MeshComponent"));
Path.Add(TEXT("RelativeRotation"));
Path.Add(TEXT("Roll"));
K2Node->SetPath(Path);

// 获取当前路径
const TArray<FString>& CurrentPath = K2Node->GetPath();

// 获取解析后的属性
const FProperty* ResolvedProp = K2Node->GetResolvedProperty();

// 清除路径
K2Node->ClearPath();
```

*来源：`K2Node_PropertyAccess.h`*

### 进阶用法

节点在编译时通过 `ExpandNode` 展开为两种模式：

1. **需要缓存变量**（非线程安全或上下文要求缓存）：编译器创建一个中间变量，插入 Property Access Library 的拷贝事件，然后将节点替换为 `UK2Node_VariableGet`
2. **直接内联**（线程安全且上下文允许）：直接展开属性路径，无需中间变量

```cpp
// 编译时判断是否需要缓存
const bool bRequiresCachedVariable = !bWasResolvedThreadSafe || 
    UAnimBlueprintExtension_PropertyAccess::ContextRequiresCachedVariable(ContextId);
```

*来源：`K2Node_PropertyAccess.cpp` L21-36, L38-113*

节点还实现了 `IClassVariableCreator` 接口，在动画蓝图编译期间参与变量创建流程。

## Demo 示例

由于 Property Access Node 是一个纯编辑器蓝图节点，没有运行时 API，完整示例需要在蓝图编辑器中操作。以下是等价的 C++ 模拟：

```cpp
// Build.cs - 如果你需要在自定义模块中引用该 plugin 的类型
PrivateDependencyModuleNames.Add("PropertyAccessNode");
// 注意：PropertyAccessNode 是 UncookedOnly，你的模块也需要是 Editor 或 UncookedOnly
```

实际上，绝大多数用法是通过蓝图编辑器 UI 完成，无需直接编写代码。

## 模块依赖

从 `PropertyAccessNode.Build.cs` 的 `PrivateDependencyModuleNames` 提取。该 plugin 没有公共依赖（全部为 Private），外部模块一般不需要直接依赖它。

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心库 |
| `CoreUObject` | UObject 系统 |
| `Slate` / `SlateCore` | UI 框架，用于节点自定义渲染 |
| `GraphEditor` | 蓝图图编辑器框架 |
| `BlueprintGraph` | 蓝图图节点基类（K2Node） |
| `Engine` | 引擎核心 |
| `UnrealEd` | 编辑器基础设施 |
| `InputCore` | 输入系统 |
| `KismetWidgets` | Kismet（蓝图编辑器）控件 |
| `KismetCompiler` | 蓝图编译器 |
| `PropertyAccessEditor` | 属性访问编辑器 UI 和解析逻辑 |
| `AnimGraph` | 动画图扩展，用于动画蓝图编译集成 |

Plugin 依赖：
- **PropertyAccessEditor** — 提供属性路径解析、绑定 UI 和编译支持

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2024-02-14 | `f543d8078ba3` | PropertyAccessEditor: Added BindingChain to OnCanBindProperty — 为属性绑定回调增加了 BindingChain 参数，增强了类型兼容性检查能力 |
| 2024-02-13 | `5b88270d06fd` | Fix Lyra PIE property access issues caused by CL 31251549 — 修复 Lyra 示例项目在 PIE 模式下属性访问的 bug |
| 2024-02-07 | `c6b6d713b984` | Fix function renames not applying to property access nodes and compilation crashes post-rename — 修复函数重命名后属性访问节点未同步更新导致的编译崩溃 |

### 维护评价

- **创建时间**：2020 年 9 月，约 5.7 年历史
- **最近更新**：2024 年 2 月，约 2 年前
- **维护状态**：**维护不活跃** — 最近一次更新在 2024 年初，之后没有新的提交。3 次更新都是 bug 修复性质，无新功能
- **代码规模**：非常小（9 个源文件，核心仅 K2Node_PropertyAccess + SPropertyAccessNode + Factory + Module 共 8 个文件），功能单一且稳定
- **是否推荐**：✅ 推荐使用。作为动画蓝图属性访问的基础设施，功能稳定成熟，不需要频繁更新。但需注意它是 UncookedOnly 类型，仅限编辑器/开发环境

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/PropertyAccessNode)
- [PropertyAccessEditor plugin](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/PropertyAccessEditor)（核心依赖，提供属性解析和 UI）
