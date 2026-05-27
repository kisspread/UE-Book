# N10X Source Code Access

> Allows access to source code in the 10X Editor .

| 属性 | 值 |
|---|---|
| 中文名 | 10X编辑器集成 |
| 分类 | Programming |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `N10XSourceCodeAccess` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2023-06-09 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/N10XSourceCodeAccess) | |

## 用途

此插件为 Unreal Engine 编辑器提供了与 **10X Editor** 代码编辑器的集成能力。它实现了一个 `ISourceCodeAccessor` 接口，使得在虚幻编辑器中进行代码导航（如“跳转到定义”、“打开文件”）时，可以直接在已安装的 10X 编辑器中打开相应的源代码文件和行号，而不是使用默认的 Visual Studio 或其他编辑器。它解决了使用 10X 作为主要 IDE 的开发者在虚幻工作流中的代码跳转体验问题。

## 使用场景

- 你在 Windows 平台上使用 10X Editor 作为你的主要 C++ IDE。
- 你希望从虚幻编辑器的蓝图节点、错误日志或调试器中双击源代码文件时，能在 10X 编辑器中直接打开并定位到对应行。

## 蓝图用法

此插件主要在编辑器和模块层面工作，不直接暴露蓝图节点。其功能通过虚幻编辑器的“源代码访问”设置自动激活。

### 核心节点

无公开的蓝图节点。

### 使用示例（蓝图描述）

无需蓝图设置。安装并启用插件后，通过编辑器菜单 `编辑 -> 编辑器偏好设置 -> 通用 -> 源代码 -> 源代码编辑器` 选择 “10X Editor” 即可。

## C++ 用法

此插件主要提供模块级服务，C++ 代码通常不需要直接引用它，除非你需要编写类似的源代码访问器或与之交互。

### 头文件引入

```cpp
#include "N10XSourceCodeAccessModule.h"
```

### 基本用法

获取源代码访问器实例并调用其方法。以下示例展示了如何检查访问器是否可用并尝试打开一个文件。

```cpp
// 包含模块头文件
#include "N10XSourceCodeAccessModule.h"

void ExampleOpenFile()
{
    // 获取模块实例
    FN10XSourceCodeAccessModule& Module = FModuleManager::LoadModuleChecked<FN10XSourceCodeAccessModule>(TEXT("N10XSourceCodeAccess"));
    
    // 获取具体的访问器
    F10XSourceCodeAccessor& Accessor = Module.GetAccessor();
    
    // 检查是否可以访问源代码（即 10X 编辑器是否就绪）
    if (Accessor.CanAccessSourceCode())
    {
        // 尝试在指定行打开文件
        FString FilePath = TEXT("/Game/Path/To/Your/File.cpp");
        int32 LineNumber = 42;
        Accessor.OpenFileAtLine(FilePath, LineNumber);
    }
}
```

### 进阶用法

通常，你不直接调用这些方法。虚幻引擎的源代码导航系统（如错误列表的双击事件、蓝图节点的“跳转到源代码”）会在内部通过 `ISourceCodeAccessor` 接口自动调用这些方法。插件的功能体现在对编辑器集成的无缝替换上。

## Demo 示例

以下是一个最小的、演示如何访问和使用此插件提供的 `F10XSourceCodeAccessor` 的 C++ 类。

**MySourceCodeUser.h**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"

class F10XSourceCodeAccessor;

class FMySourceCodeUser
{
public:
    void Initialize();
    void TryOpenFile(const FString& InFilePath, int32 InLineNumber);

private:
    F10XSourceCodeAccessor* AccessorPtr = nullptr;
};
```

**MySourceCodeUser.cpp**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.

#include "MySourceCodeUser.h"
#include "N10XSourceCodeAccessModule.h"
#include "N10XSourceCodeAccessor.h"

void FMySourceCodeUser::Initialize()
{
    if (FModuleManager::Get().IsModuleLoaded("N10XSourceCodeAccess"))
    {
        FN10XSourceCodeAccessModule& Module = FModuleManager::GetModuleChecked<FN10XSourceCodeAccessModule>("N10XSourceCodeAccess");
        AccessorPtr = &Module.GetAccessor();
    }
}

void FMySourceCodeUser::TryOpenFile(const FString& InFilePath, int32 InLineNumber)
{
    if (AccessorPtr && AccessorPtr->CanAccessSourceCode())
    {
        AccessorPtr->OpenFileAtLine(InFilePath, InLineNumber);
    }
}
```

## 模块依赖

此插件的 `Build.cs` 文件仅依赖 `HotReload` 模块。对于使用者而言，无需特殊依赖。要使用此插件的服务，你的模块只需要标准的引擎模块依赖即可。

| 模块 | 用途 |
|---|---|
| `HotReload` | 插件内部用于热重载支持 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-10-31 | `bbe97454` | Fix mismatched LOCTEXT_NAMESPACE and AllowWindowsPlatformTypes | 修复了本地化宏命名空间不匹配和Windows平台类型允许问题 |
| 2025-03-25 | `3395567a` | PR #13018: 10x Source Code Editor: Fix files not opening when file path contains spaces | 修复了当文件路径包含空格时无法在10X编辑器中打开文件的bug |
| 2024-10-07 | `d69a4c88` | [UE] Fix 10x source code accessor to pull the correct solution file name | 修复了获取错误解决方案文件名的问题 |
| 2024-07-18 | `9eaacc95` | [Backout] - CL34912307 - CIS Valk Error | 回滚了之前的更改 |
| 2024-07-18 | `413ba815` | [AutoRTFM] Migrate more critical sections to using the transactionally safe variants. | 将关键部分迁移到事务安全版本 |

### 维护评价

此插件创建于 2023 年中，是一个相对较新的集成插件。从 git 历史看，**仍在持续维护中**，最近一次更新在 2025 年 10 月，修复了本地化相关问题。维护频率不高，但修复都是针对具体问题的实质性改进（如路径空格处理）。鉴于其功能相对独立且专一，目前没有发现已知的重大问题或限制。**推荐使用 10X Editor 的 Windows 平台开发者启用此插件**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/N10XSourceCodeAccess)
- [官方文档]() （无）
- [测试用例]() （未在提供的信息中发现测试文件）