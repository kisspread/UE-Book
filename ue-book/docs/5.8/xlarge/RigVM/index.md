# RigVM

> Provides frontend and backend for the RigVM visual programming language and runtime（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | RigVM运行时 |
| 分类 | Misc |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产和测试资源） |
| 模块 | `RigVM` (Runtime), `RigVMDeveloper` (Runtime), `RigVMEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2023-03-28 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/RigVM) | |

## 用途

RigVM 是 Unreal Engine 骨骼动画系统“Rig”的运行时核心。它实现了一套专为骨骼控制和程序化内容生成设计的可视化编程语言（Visual Scripting）。该插件并非通用蓝图编辑器，而是一个高性能、可解释执行的专用虚拟机，用于驱动角色的骨骼变形、网格生成以及复杂的程序化动画逻辑。

**为什么存在？** 它是 Control Rig、Live Link 等高级动画功能的基础依赖，为这些系统提供底层脚本执行能力。

## 使用场景

-   **你需要精确控制角色的骨骼或曲线动画** → 使用 Control Rig（其底层依赖 RigVM）。
-   **你需要创建程序化的内容生成规则**（如根据参数动态生成网格） → 使用 RigVM 脚本。
-   **你需要在运行时通过可视化编程定制复杂的游戏逻辑**（非通用游戏逻辑，而是涉及空间变换、动画通道的逻辑） → 可使用 RigVM 作为解决方案。

## 蓝图用法

RigVM 的蓝图接口主要由其宿主类 `URigVMHost` 提供。蓝图通常不直接操作 RigVM 实例，而是继承 `URigVMHost` 来创建自定义的、可执行 RigVM 脚本的资产或组件。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Execute` | 在指定的宿主（Host）上执行一次 RigVM 脚本。 | `URigVMHost` |
| `CanExecute` | 检查当前状态是否允许执行脚本。 | `URigVMHost` |

### 使用示例（蓝图描述）

1.  创建一个继承自 `URigVMHost` 的蓝图类。
2.  在该蓝图类的事件图表中，编写逻辑以触发 `Execute` 节点来运行关联的 RigVM 脚本。
3.  通过 `URigVMHost` 的属性（如变量、输入输出映射）与脚本进行数据交互。

## C++ 用法

### 头文件引入

```cpp
#include “RigVMCore/RigVM.h”
#include “RigVMHost.h”
```

### 基本用法

创建一个自定义的宿主类来管理和执行 RigVM 脚本。
```cpp
// MyRigVMHost.h
#pragma once
#include “RigVMHost.h”
#include “MyRigVMHost.generated.h”

UCLASS()
class UMyRigVMHost : public URigVMHost
{
    GENERATED_BODY()
public:
    // 可以重写此方法来定制执行逻辑
    // virtual bool Execute(URigVMMemoryStorage* InMemory, const FName& InEntryName = NAME_None) override;
};
```

### 进阶用法

RigVM 的核心在于其脚本对象 `URigVM` 和内存存储 `URigVMMemoryStorage`。高级用法涉及直接操控这些对象来实现更精细的控制或调试。
```cpp
// 获取宿主关联的 RigVM 脚本对象
URigVM* RigVM = MyHost->GetVM();

// 获取或创建内存存储实例
URigVMMemoryStorage* Memory = MyHost->GetMemoryStorage(true);

// 可以手动触发编译或执行流程
if (RigVM && RigVM->IsCompiled())
{
    // ... 进行更底层的虚拟机操作
}
```

## Demo 示例

一个最小的自定义 RigVM 宿主类示例。
```cpp
// MinimalRigVMHost.h
#pragma once
#include “RigVMHost.h”
#include “MinimalRigVMHost.generated.h”

UCLASS(BlueprintType)
class UMinimalRigVMHost : public URigVMHost
{
    GENERATED_BODY()

public:
    UMinimalRigVMHost();
    
    // 声明一个蓝图可调用的函数，用于触发执行
    UFUNCTION(BlueprintCallable, Category = “RigVM”)
    void RunMyScript();
};

// MinimalRigVMHost.cpp
#include “MinimalRigVMHost.h”

UMinimalRigVMHost::UMinimalRigVMHost()
{
    // 构造函数中可以配置一些默认属性
}

void UMinimalRigVMHost::RunMyScript()
{
    // 调用父类的 Execute 方法来运行脚本
    Execute();
}
```

## 模块依赖

从 Build.cs 的依赖关系分析，使用者主要需要关注以下独特依赖：

| 模块 | 用途 |
|---|---|
| `Kismet` | **RigVMDeveloper** 和 **RigVMEditor** 模块依赖此模块，表明其编辑器/开发功能与蓝图编辑器（Kismet）深度集成。 |

对于**运行时使用**（仅依赖 `RigVM` 模块），无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

从 git log 可以看出，该插件在最近一周内有非常频繁的提交，主要关联到其上游系统 Control Rig 的修复和改进。

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `dfee5052` | Control Rig: Fix missing dependency in ControlRigModules | 修复 Control Rig 模块的缺失依赖问题。 |
| 2026-05-22 | `e51b24ac` | Cherry-picking fix CL from Sara Schvartzman: | 从 Sara Schvartzman 那里摘取修复补丁。 |
| 2026-05-21 | `fee6a0dc` | Control Rig: Fix renaming a variable in some cases leaves a duplicate | 修复重命名变量时可能遗留副本的 Bug。 |
| 2026-05-18 | `5d1db13f` | Fix crash when debug pins are orphaned | 修复调试引脚孤立时导致的崩溃。 |
| 2026-05-15 | `0b718514` | Control RIg: Defensive fix when function of a unit struct is nullptr | 对单元结构体函数为空指针的情况进行防御性修复。 |

### 维护评价

**活跃维护**。
-   **创建时间**：约 2 年前，相对年轻。
-   **近期更新**：在过去一周内有多次实质性功能与 Bug 修复提交，表明正在被积极开发和维护。
-   **已知问题**：近期提交多为修复崩溃和逻辑错误，说明项目处于快速迭代和问题修复阶段。
-   **推荐使用**：是。作为 Control Rig 等核心动画功能的基石，它受到 Epic Games 团队的重点维护，是生产环境中可依赖的技术栈。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/RigVM)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/RigVM/Tests) （路径推断，通常位于插件下的 Tests 目录）