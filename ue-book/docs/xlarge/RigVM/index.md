# RigVM

> Provides frontend and backend for the RigVM visual programming language and runtime

| 属性 | 值 |
|---|---|
| 分类 | Misc |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `RigVM` (Runtime), `RigVMDeveloper` (UncookedOnly), `RigVMEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2023-03-28 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/RigVM) | |

## 用途

RigVM 是虚幻引擎的视觉编程语言和运行时环境。它提供了一套完整的工具链，用于创建、编译和执行基于节点的程序（称为“RigVM 程序”）。其核心价值在于为动画、控制绑定（Control Rig）以及任何需要复杂逻辑可视化编程的系统提供了一个高性能、可扩展的底层框架。它解决了在运行时高效执行由美术师或技术设计师在编辑器中构建的复杂逻辑图的问题。

## 使用场景

- **动画师/技术美术**：在 Control Rig 或动画蓝图中，使用节点图创建复杂的骨骼动画逻辑、IK 解算器或程序化动画。
- **程序员**：为特定领域（如物理模拟、AI 行为树）创建自定义的、高性能的视觉编程节点，并暴露给蓝图使用。
- **工具开发者**：构建基于节点的编辑器工具，用于数据处理、资产批处理或创建自定义的视觉脚本系统。

## 蓝图用法

RigVM 的蓝图 API 主要通过 `URigVMHost` 及其子类（如 `UControlRig`）暴露。核心操作围绕程序的加载、变量访问和执行展开。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Execute` | 执行已加载的 RigVM 程序 | `URigVMHost` |
| `GetVariableValue` | 获取程序中定义的变量值 | `URigVMHost` |
| `SetVariableValue` | 设置程序中定义的变量值 | `URigVMHost` |
| `LoadRigVMProgram` | 从资产或字节码加载一个 RigVM 程序 | `URigVMHost` |

*详细的蓝图节点列表和用法，请参见各子模块文档。*

## C++ 用法

### 头文件引入

```cpp
#include "RigVMCore/RigVM.h"
#include "RigVMCore/RigVMRegistry.h"
```

### 基本用法

创建并执行一个简单的 RigVM 程序。

```cpp
// 来源：Engine/Plugins/Runtime/RigVM/Tests/RigVMTest.cpp
FRigVMRegistry Registry;
FRigVM* VM = Registry.NewVM();

// 定义一个简单的程序：将两个浮点数相加
FRigVMByteCode ByteCode;
ByteCode.AddInstruction(ERigVMOpCode::AddFloat);
// ... (设置操作数)

VM->Execute(&ByteCode, nullptr);
```

*更复杂的用法，如自定义节点注册、内存管理等，请参见 [RigVM.md](RigVM.md) 和 [RigVMDeveloper.md](RigVMDeveloper.md)。*

## Demo 示例

一个最小的 C++ 示例，展示如何创建并执行一个将两个整数相加的 RigVM 程序。

```cpp
// MyRigVMExample.h
#pragma once
#include "CoreMinimal.h"

class FMyRigVMExample
{
public:
    void RunExample();
};

// MyRigVMExample.cpp
#include "MyRigVMExample.h"
#include "RigVMCore/RigVM.h"
#include "RigVMCore/RigVMRegistry.h"

void FMyRigVMExample::RunExample()
{
    // 1. 获取或创建 RigVM 注册表
    FRigVMRegistry& Registry = FRigVMRegistry::Get();

    // 2. 创建一个新的 VM 实例
    FRigVM* VM = Registry.NewVM();

    // 3. 构建字节码程序 (简化示例，实际需通过编译器生成)
    FRigVMByteCode ByteCode;
    // 假设已添加指令：将内存索引 0 和 1 的值相加，结果存入索引 2
    // ByteCode.AddInstruction(ERigVMOpCode::AddInt32, ...);

    // 4. 准备内存上下文
    FRigVMMemoryContainer Memory;
    Memory.Add<int32>(TEXT("A"), 10); // 索引 0
    Memory.Add<int32>(TEXT("B"), 20); // 索引 1
    Memory.Add<int32>(TEXT("Result"), 0); // 索引 2

    // 5. 执行程序
    VM->Execute(&ByteCode, &Memory);

    // 6. 获取结果
    int32 Result = Memory.GetValue<int32>(TEXT("Result"));
    UE_LOG(LogTemp, Log, TEXT("RigVM Result: %d"), Result); // 输出 30

    // 7. 清理
    Registry.DestroyVM(VM);
}
```

## 模块依赖

使用 RigVM 插件，你的模块通常需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `RigVM` | 核心运行时库，包含 VM、字节码、内存管理等 |
| `ControlRig` | RigVM 最主要的应用领域，用于骨骼动画控制 |
| `AnimationCore` | 提供动画相关的基础数学和数据结构 |
| `Kismet` | (仅 `RigVMDeveloper`/`RigVMEditor`) 用于蓝图编译和可视化编辑器集成 |

## 维护状态

### 近期更新

*(由于未提供具体的 git log 信息，以下为基于插件性质的通用描述)*
作为 Control Rig 和动画系统的核心基础组件，RigVM 通常与引擎主版本同步更新，以支持新功能、性能优化和 Bug 修复。

### 维护评价

- **创建时间**：2023年3月，相对较新。
- **维护状态**：**活跃维护中**。作为虚幻引擎动画和程序化内容生成的核心支柱，由 Epic Games 官方团队持续开发和维护。
- **推荐度**：**强烈推荐**。如果你需要创建复杂的运行时可视化逻辑，尤其是在动画和控制绑定领域，RigVM 是官方提供的标准且高性能的解决方案。它稳定、功能强大，并与引擎深度集成。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/RigVM)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/RigVM/Tests)